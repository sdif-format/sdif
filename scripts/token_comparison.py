#!/usr/bin/env python3
"""SDIF benchmark generated from canonical JSON golden files.

The benchmark derives all compared formats from the same canonical JSON source:

- JSON Compact
- JSON Pretty
- YAML
- XML
- CSV Bundle
- SDIF
- SDIF AI projection
- TOON, when the official CLI is available

It can count tokens with multiple tokenizers:

- Estimate, deterministic 4 UTF-8 bytes per token fallback
- tiktoken / cl100k_base
- Llama 3 tokenizer through transformers
- Claude token counting API through anthropic, opt-in only

Each benchmark execution writes persistent evidence to:

- benchmarks/<timestamp>/comparison.log
- benchmarks/<timestamp>/comparison.md
- benchmarks/latest -> <timestamp>

Environment variables:

- SDIF_BENCHMARK_TOON=0
    Disable TOON comparison.

- SDIF_BENCHMARK_CLAUDE=1
    Enable Claude token counting. Requires ANTHROPIC_API_KEY.

- SDIF_CLAUDE_MODEL=<model>
    Claude model used for token counting.
    Default: claude-sonnet-4-5

- SDIF_LLAMA_TOKENIZER=<hf-model-or-local-path>
    Hugging Face tokenizer name or local path.
    Default: meta-llama/Meta-Llama-3-8B

- HF_TOKEN=<token>
    Optional Hugging Face token for gated tokenizers.

- SDIF_LLAMA_LOCAL_ONLY=1
    Only load Llama tokenizer from local Hugging Face cache.

- SDIF_BENCHMARK_VERBOSE=1
    Print tokenizer/TOON diagnostic warnings.

- SDIF_TIKTOKEN_ENCODING=<encoding>
    tiktoken encoding name.
    Default: cl100k_base
"""

from __future__ import annotations

import contextlib
import csv
import functools
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, TextIO
from xml.sax.saxutils import escape as xml_escape

import yaml  # type: ignore[import-untyped]

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from sdif.ai import ai_view  # noqa: E402
from sdif.json import json_data_to_sdif  # noqa: E402


# ====================
# Optional dependencies
# ====================

try:
    import tiktoken  # type: ignore[import-not-found]
except ImportError:
    tiktoken = None  # type: ignore[assignment]


try:
    from transformers import AutoTokenizer  # type: ignore[import-not-found]
except ImportError:
    AutoTokenizer = None  # type: ignore[assignment,misc]


try:
    from anthropic import Anthropic  # type: ignore[import-not-found]
except ImportError:
    Anthropic = None  # type: ignore[assignment,misc]


# ====================
# Types
# ====================

TokenCounter = Callable[[str], int | None]

AI_ALIASES = {
    "authority": "auth",
    "description": "desc",
    "evidence": "ev",
    "lifecycle": "life",
    "priority": "pri",
    "schema": "sch",
    "status": "st",
    "version": "v",
}


@dataclass(frozen=True)
class FormatResult:
    name: str
    text: str
    bytes_size: int
    tokens: dict[str, int | None]
    primary_ratio: float | None


@dataclass(frozen=True)
class TokenizerSpec:
    name: str
    counter: TokenCounter


@dataclass(frozen=True)
class BenchmarkEvidence:
    generated_at: str
    run_dir: Path
    golden_dir: Path
    primary_name: str
    tokenizers: list[TokenizerSpec]
    results_by_document: dict[str, list[FormatResult]]
    env_file_loaded: bool


# ====================
# Evidence helpers
# ====================


class Tee:
    """Write text to multiple streams at once."""

    def __init__(self, *streams: TextIO) -> None:
        self.streams = streams

    def write(self, data: str) -> int:
        for stream in self.streams:
            stream.write(data)
        return len(data)

    def flush(self) -> None:
        for stream in self.streams:
            stream.flush()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def benchmark_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def create_benchmark_run_dir() -> Path:
    base_dir = REPO_ROOT / "benchmarks"
    base_dir.mkdir(parents=True, exist_ok=True)

    timestamp = benchmark_timestamp()
    run_dir = base_dir / timestamp
    counter = 1

    while run_dir.exists():
        run_dir = base_dir / f"{timestamp}-{counter:02d}"
        counter += 1

    run_dir.mkdir(parents=True)
    return run_dir


def update_latest_symlink(run_dir: Path) -> Path:
    latest = run_dir.parent / "latest"

    if latest.is_symlink() or latest.is_file():
        latest.unlink()
    elif latest.exists():
        raise RuntimeError(
            f"Cannot update latest symlink because {latest} exists and is not a symlink."
        )

    latest.symlink_to(run_dir.name, target_is_directory=True)
    return latest


def markdown_escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def env_value(name: str, *, secret: bool = False) -> str:
    value = os.environ.get(name)

    if not value:
        return "_unset_"

    if secret:
        return "_set_"

    return f"`{markdown_escape(value)}`"


def parse_env_value(raw_value: str) -> str:
    """Parse a simple .env value.

    Supports:
    - KEY=value
    - KEY="value"
    - KEY='value'
    - inline comments only when value is not quoted
    """

    value = raw_value.strip()

    if not value:
        return ""

    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]

    if "#" in value:
        value = value.split("#", 1)[0].rstrip()

    return value


def load_env_file(path: Path) -> bool:
    """Load a local .env file without overriding existing environment variables."""

    if not path.exists():
        return False

    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        if line.startswith("export "):
            line = line[len("export ") :].strip()

        if "=" not in line:
            verbose_warning(f"Ignoring invalid .env line {line_number}: missing '='")
            continue

        key, raw_value = line.split("=", 1)
        key = key.strip()

        if not key:
            verbose_warning(f"Ignoring invalid .env line {line_number}: empty key")
            continue

        if key in os.environ:
            continue

        os.environ[key] = parse_env_value(raw_value)

    return True


# ====================
# Format generators
# ====================


def json_compact(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def json_pretty(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def yaml_generated(data: dict[str, Any]) -> str:
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)


def xml_generated(data: dict[str, Any]) -> str:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    _emit_xml_value("document", data, lines, indent=0)
    return "\n".join(lines) + "\n"


def csv_bundle_generated(data: dict[str, Any]) -> str:
    """Render a deterministic CSV bundle from the canonical JSON source.

    CSV alone is a flat-table format, so nested/list values are encoded as
    compact JSON cells and repeated top-level object arrays get their own CSV
    section. This keeps the comparison honest: it measures a practical CSV
    interchange bundle rather than pretending one CSV table can represent the
    whole semantic document.
    """

    sections: list[str] = []
    scalar_rows: list[tuple[str, object]] = []

    for key, value in data.items():
        if _is_uniform_object_array(value):
            sections.append(_csv_section(key, value))  # type: ignore[arg-type]
        else:
            scalar_rows.append((key, value))

    if scalar_rows:
        output = io.StringIO()
        writer = csv.writer(output, lineterminator="\n")
        writer.writerow(["key", "value"])

        for key, value in scalar_rows:
            writer.writerow([key, _csv_cell(value)])

        sections.insert(0, "# fields\n" + output.getvalue().rstrip("\n"))

    return "\n\n".join(sections).rstrip() + "\n"


def compact_ai_projection(sdif_text: str) -> str:
    candidates = [
        ai_view(sdif_text, {}, include_header=False),
        ai_view(sdif_text, AI_ALIASES, include_header=True),
    ]
    return min(candidates, key=lambda candidate: len(candidate.encode("utf-8")))


def run_command(command: list[str], output: Path, timeout_seconds: int = 30) -> str | None:
    try:
        completed = subprocess.run(
            command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=timeout_seconds,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        verbose_warning(f"Command failed to start: {' '.join(command)} | {exc}")
        return None

    if completed.returncode != 0:
        verbose_warning(
            "Command returned non-zero exit status: "
            f"{' '.join(command)} | stderr={completed.stderr.strip()}"
        )
        return None

    if output.exists():
        return output.read_text(encoding="utf-8")

    if completed.stdout.strip():
        return completed.stdout

    return None


def toon_from_cli(data: dict[str, Any]) -> str | None:
    """Render TOON using the official @toon-format/cli command.

    TOON is derived from the canonical JSON source, never from hand-written
    benchmark fixtures.
    """

    if os.environ.get("SDIF_BENCHMARK_TOON") == "0":
        return None

    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "source.json"
        output = Path(tmp) / "source.toon"
        source.write_text(json_compact(data), encoding="utf-8")

        toon = shutil.which("toon")
        if toon is not None:
            rendered = run_command([toon, str(source), "-o", str(output)], output)
            if rendered is not None:
                return rendered

        npx = shutil.which("npx")
        if npx is None:
            verbose_warning("TOON skipped: neither `toon` nor `npx` was found.")
            return None

        return run_command(
            [npx, "-y", "@toon-format/cli", str(source), "-o", str(output)],
            output,
            timeout_seconds=60,
        )


# ====================
# Token counters
# ====================


@functools.lru_cache(maxsize=1)
def get_tiktoken_encoder() -> Any:
    if tiktoken is None:
        raise RuntimeError("tiktoken is not installed")

    encoding_name = os.environ.get("SDIF_TIKTOKEN_ENCODING", "cl100k_base")
    return tiktoken.get_encoding(encoding_name)


def count_tiktoken(text: str) -> int | None:
    if tiktoken is None:
        return None

    try:
        encoder = get_tiktoken_encoder()
        return len(encoder.encode(text))
    except Exception as exc:
        verbose_warning(f"tiktoken unavailable: {exc}")
        return None


@functools.lru_cache(maxsize=1)
def get_llama_tokenizer() -> Any:
    if AutoTokenizer is None:
        raise RuntimeError("transformers is not installed")

    model_name = os.environ.get(
        "SDIF_LLAMA_TOKENIZER",
        "meta-llama/Meta-Llama-3-8B",
    )

    local_files_only = os.environ.get("SDIF_LLAMA_LOCAL_ONLY") == "1"

    return AutoTokenizer.from_pretrained(
        model_name,
        token=os.environ.get("HF_TOKEN"),
        trust_remote_code=True,
        local_files_only=local_files_only,
    )


def count_llama3(text: str) -> int | None:
    if AutoTokenizer is None:
        return None

    try:
        tokenizer = get_llama_tokenizer()
        return len(tokenizer.encode(text, add_special_tokens=False))
    except Exception as exc:
        verbose_warning(f"Llama tokenizer unavailable: {exc}")
        return None


@functools.lru_cache(maxsize=1)
def get_anthropic_client() -> Any:
    if Anthropic is None:
        raise RuntimeError("anthropic is not installed")

    return Anthropic()


def count_estimate(text: str) -> int:
    byte_count = len(text.encode("utf-8"))
    return max(1, (byte_count + 3) // 4)


def count_claude(text: str) -> int | None:
    """Count tokens with Anthropic's message token counting endpoint.

    This is intentionally opt-in because it requires network access, an API key,
    and may be slower than local tokenizers.
    """

    if os.environ.get("SDIF_BENCHMARK_CLAUDE") != "1":
        return None

    if Anthropic is None:
        return None

    try:
        client = get_anthropic_client()
        response = client.messages.count_tokens(
            model=os.environ.get("SDIF_CLAUDE_MODEL", "claude-sonnet-4-5"),
            messages=[
                {
                    "role": "user",
                    "content": text,
                }
            ],
        )
        return int(response.input_tokens)
    except Exception as exc:
        verbose_warning(f"Claude tokenizer unavailable: {exc}")
        return None


def available_tokenizers() -> list[TokenizerSpec]:
    return [
        TokenizerSpec("Estimate", count_estimate),
        TokenizerSpec("tiktoken", count_tiktoken),
        TokenizerSpec("Llama3", count_llama3),
        TokenizerSpec("Claude", count_claude),
    ]


def select_primary_tokenizer(tokenizers: list[TokenizerSpec], sample_text: str) -> TokenizerSpec:
    for preferred_name in ("tiktoken", "Estimate"):
        for tokenizer in tokenizers:
            if tokenizer.name == preferred_name and tokenizer.counter(sample_text) is not None:
                return tokenizer

    return tokenizers[0]


# ====================
# Benchmark helpers
# ====================


def verbose_warning(message: str) -> None:
    if os.environ.get("SDIF_BENCHMARK_VERBOSE") == "1":
        print(f"⚠️  {message}")


def format_count(value: int | None) -> str:
    return "-" if value is None else str(value)


def format_ratio(value: float | None) -> str:
    return "-" if value is None else f"{value:>6.1f}%"


def ratio(tokens: int | None, baseline: int | None) -> float | None:
    if tokens is None or baseline is None or baseline == 0:
        return None
    return (tokens / baseline) * 100


def average(values: list[float]) -> float:
    return sum(values) / len(values)


def build_formats(data: dict[str, Any]) -> list[tuple[str, str]]:
    sdif_text = json_data_to_sdif(data, include_header=True)
    formats: list[tuple[str, str]] = [
        ("JSON Compact", json_compact(data)),
        ("JSON Pretty", json_pretty(data)),
        ("YAML", yaml_generated(data)),
        ("XML", xml_generated(data)),
        ("CSV Bundle", csv_bundle_generated(data)),
        ("SDIF", sdif_text),
        ("SDIF AI", compact_ai_projection(sdif_text)),
    ]

    toon_text = toon_from_cli(data)
    if toon_text is not None:
        formats.append(("TOON", toon_text))

    return formats


def count_format(
    name: str,
    text: str,
    tokenizers: list[TokenizerSpec],
    primary_name: str,
    primary_baseline: int | None,
) -> FormatResult:
    tokens = {tokenizer.name: tokenizer.counter(text) for tokenizer in tokenizers}

    primary_tokens = tokens.get(primary_name)
    primary_ratio = ratio(primary_tokens, primary_baseline)

    return FormatResult(
        name=name,
        text=text,
        bytes_size=len(text.encode("utf-8")),
        tokens=tokens,
        primary_ratio=primary_ratio,
    )


def sort_key(row: FormatResult, primary_name: str) -> tuple[int, int, int, str]:
    primary = row.tokens.get(primary_name)

    if primary is None:
        return (1, 10**12, row.bytes_size, row.name)

    return (0, primary, row.bytes_size, row.name)


def discover_documents(golden_dir: Path) -> list[str]:
    return [path.parent.name for path in sorted(golden_dir.glob("*/equivalent.json"))]


def _emit_xml_value(name: str, value: object, lines: list[str], indent: int) -> None:
    prefix = " " * indent
    tag = _xml_tag(name)

    if isinstance(value, dict):
        lines.append(f"{prefix}<{tag}>")
        for key, child in value.items():
            _emit_xml_value(str(key), child, lines, indent + 2)
        lines.append(f"{prefix}</{tag}>")
    elif isinstance(value, list):
        lines.append(f"{prefix}<{tag}>")
        for item in value:
            _emit_xml_value("item", item, lines, indent + 2)
        lines.append(f"{prefix}</{tag}>")
    else:
        lines.append(f"{prefix}<{tag}>{xml_escape(_scalar_text(value))}</{tag}>")


def _xml_tag(name: str) -> str:
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.-]*", name):
        return name
    return "item"


def _scalar_text(value: object) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    return str(value)


def _is_uniform_object_array(value: object) -> bool:
    if not isinstance(value, list) or not value:
        return False
    if not all(isinstance(item, dict) for item in value):
        return False

    columns = list(value[0].keys())
    if not columns:
        return False

    expected = set(columns)
    return all(set(item.keys()) == expected for item in value)


def _csv_section(name: str, rows: list[dict[str, object]]) -> str:
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    columns = list(rows[0].keys())

    writer.writerow(columns)

    for row in rows:
        writer.writerow([_csv_cell(row[column]) for column in columns])

    return f"# table:{name}\n{output.getvalue().rstrip(chr(10))}"


def _csv_cell(value: object) -> str:
    if isinstance(value, str | int | float) or value is None or isinstance(value, bool):
        return _scalar_text(value)

    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


# ====================
# Console rendering
# ====================


def print_header(tokenizers: list[TokenizerSpec], primary_name: str) -> None:
    tokenizer_columns = "".join(f" {tokenizer.name:>9}" for tokenizer in tokenizers)

    print("📊 SDIF BENCHMARK - Multi-Tokenizer")
    print("Semantic source: examples/golden/<document>/equivalent.json")
    print(f"Primary ordering and ratio: {primary_name} vs JSON Compact\n")
    print(f"{'Document':<24} {'Format':<12}{tokenizer_columns} {'Bytes':>8} {'vs JSON':>12}")
    print("=" * 112)


def print_document_rows(
    document_name: str,
    rows: list[FormatResult],
    tokenizers: list[TokenizerSpec],
) -> None:
    first = True

    for row in rows:
        prefix = document_name if first else ""
        token_columns = "".join(
            f" {format_count(row.tokens.get(tokenizer.name)):>9}" for tokenizer in tokenizers
        )

        print(
            f"{prefix:<24} "
            f"{row.name:<12}"
            f"{token_columns}"
            f" {row.bytes_size:>8}"
            f" {format_ratio(row.primary_ratio):>12}"
        )

        first = False

    print("-" * 112)


def print_summary(
    documents_count: int,
    results_by_document: dict[str, list[FormatResult]],
    tokenizers: list[TokenizerSpec],
    primary_name: str,
) -> None:
    print("\n📈 Average ratio vs JSON Compact")
    print("=" * 112)

    for tokenizer in tokenizers:
        tokenizer_name = tokenizer.name
        ratios_by_format: dict[str, list[float]] = {}

        for rows in results_by_document.values():
            baseline = next(
                (row.tokens.get(tokenizer_name) for row in rows if row.name == "JSON Compact"),
                None,
            )

            for row in rows:
                value = ratio(row.tokens.get(tokenizer_name), baseline)
                if value is not None:
                    ratios_by_format.setdefault(row.name, []).append(value)

        if not ratios_by_format:
            print(f"\n{tokenizer_name}: unavailable")
            continue

        print(f"\n{tokenizer_name}:")
        for format_name, values in sorted(
            ratios_by_format.items(),
            key=lambda item: average(item[1]),
        ):
            print(
                f"  {format_name:<15} "
                f"average: {average(values):>6.1f}% "
                f"coverage: {len(values)}/{documents_count}"
            )

    print(f"\n🏁 Wins by {primary_name}")
    print("=" * 112)

    wins: dict[str, int] = {}

    for rows in results_by_document.values():
        comparable = [row for row in rows if row.tokens.get(primary_name) is not None]

        if not comparable:
            continue

        winner = sorted(comparable, key=lambda row: sort_key(row, primary_name))[0]
        wins[winner.name] = wins.get(winner.name, 0) + 1

    for format_name, count in sorted(wins.items(), key=lambda item: (-item[1], item[0])):
        print(f"{format_name:<15} wins: {count}/{documents_count} documents")


def print_footer(results_by_document: dict[str, list[FormatResult]]) -> None:
    print("\n✅ Benchmark completed by deriving all formats from canonical JSON.")

    all_formats = {row.name for rows in results_by_document.values() for row in rows}

    if os.environ.get("SDIF_BENCHMARK_TOON") == "0":
        print("ℹ️  TOON skipped: SDIF_BENCHMARK_TOON=0.")
    elif "TOON" not in all_formats:
        print(
            "ℹ️  TOON skipped: neither global `toon` nor `npx @toon-format/cli` "
            "could produce output."
        )

    if os.environ.get("SDIF_BENCHMARK_CLAUDE") != "1":
        print("ℹ️  Claude skipped: set SDIF_BENCHMARK_CLAUDE=1 to enable API token counting.")


def print_evidence_footer(run_dir: Path, log_path: Path, markdown_path: Path, latest: Path) -> None:
    print()
    print("🧾 Benchmark evidence written")
    print(f"  log:      {log_path.relative_to(REPO_ROOT)}")
    print(f"  markdown: {markdown_path.relative_to(REPO_ROOT)}")
    print(f"  latest:   {latest.relative_to(REPO_ROOT)} -> {run_dir.name}")


# ====================
# Markdown report rendering
# ====================


def render_markdown_report(evidence: BenchmarkEvidence) -> str:
    documents_count = len(evidence.results_by_document)

    lines: list[str] = [
        "# SDIF Benchmark Evidence Report",
        "",
        f"- Generated at: `{evidence.generated_at}`",
        f"- Run directory: `{evidence.run_dir.relative_to(REPO_ROOT)}`",
        f"- Semantic source: `{evidence.golden_dir.relative_to(REPO_ROOT)}/<document>/equivalent.json`",
        f"- Primary ordering and ratio: `{evidence.primary_name}` vs `JSON Compact`",
        "",
        "## Environment",
        "",
        "| Variable | Value |",
        "|---|---|",
        f"| `SDIF_BENCHMARK_TOON` | {env_value('SDIF_BENCHMARK_TOON')} |",
        f"| `SDIF_BENCHMARK_CLAUDE` | {env_value('SDIF_BENCHMARK_CLAUDE')} |",
        f"| `SDIF_CLAUDE_MODEL` | {env_value('SDIF_CLAUDE_MODEL')} |",
        f"| `SDIF_LLAMA_TOKENIZER` | {env_value('SDIF_LLAMA_TOKENIZER')} |",
        f"| `SDIF_LLAMA_LOCAL_ONLY` | {env_value('SDIF_LLAMA_LOCAL_ONLY')} |",
        f"| `SDIF_TIKTOKEN_ENCODING` | {env_value('SDIF_TIKTOKEN_ENCODING')} |",
        f"| `HF_TOKEN` | {env_value('HF_TOKEN', secret=True)} |",
        f"| `ANTHROPIC_API_KEY` | {env_value('ANTHROPIC_API_KEY', secret=True)} |",
        "",
        "## Documents",
        "",
    ]

    token_headers = [tokenizer.name for tokenizer in evidence.tokenizers]

    for document_name, rows in evidence.results_by_document.items():
        lines.extend(
            [
                f"### `{markdown_escape(document_name)}`",
                "",
                "| Format | Bytes | "
                + " | ".join(markdown_escape(name) for name in token_headers)
                + " | vs JSON Compact |",
                "|---|---:|" + "|".join("---:" for _ in token_headers) + "|---:|",
            ]
        )

        for row in rows:
            token_columns = " | ".join(
                format_count(row.tokens.get(tokenizer.name)) for tokenizer in evidence.tokenizers
            )

            lines.append(
                f"| {markdown_escape(row.name)} "
                f"| {row.bytes_size} "
                f"| {token_columns} "
                f"| {format_ratio(row.primary_ratio).strip()} |"
            )

        lines.append("")

    lines.extend(
        [
            "## Average ratio vs JSON Compact",
            "",
        ]
    )

    for tokenizer in evidence.tokenizers:
        tokenizer_name = tokenizer.name
        ratios_by_format: dict[str, list[float]] = {}

        for rows in evidence.results_by_document.values():
            baseline = next(
                (row.tokens.get(tokenizer_name) for row in rows if row.name == "JSON Compact"),
                None,
            )

            for row in rows:
                value = ratio(row.tokens.get(tokenizer_name), baseline)
                if value is not None:
                    ratios_by_format.setdefault(row.name, []).append(value)

        lines.extend(
            [
                f"### `{markdown_escape(tokenizer_name)}`",
                "",
            ]
        )

        if not ratios_by_format:
            lines.extend(["Unavailable.", ""])
            continue

        lines.extend(
            [
                "| Format | Average | Coverage |",
                "|---|---:|---:|",
            ]
        )

        for format_name, values in sorted(
            ratios_by_format.items(),
            key=lambda item: average(item[1]),
        ):
            lines.append(
                f"| {markdown_escape(format_name)} "
                f"| {average(values):.1f}% "
                f"| {len(values)}/{documents_count} |"
            )

        lines.append("")

    lines.extend(
        [
            f"## Wins by `{markdown_escape(evidence.primary_name)}`",
            "",
            "| Format | Wins |",
            "|---|---:|",
        ]
    )

    wins: dict[str, int] = {}

    for rows in evidence.results_by_document.values():
        comparable = [row for row in rows if row.tokens.get(evidence.primary_name) is not None]

        if not comparable:
            continue

        winner = sorted(comparable, key=lambda row: sort_key(row, evidence.primary_name))[0]
        wins[winner.name] = wins.get(winner.name, 0) + 1

    for format_name, count in sorted(wins.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| {markdown_escape(format_name)} | {count}/{documents_count} |")

    all_formats = {row.name for rows in evidence.results_by_document.values() for row in rows}

    lines.extend(
        [
            "",
            "## Notes",
            "",
        ]
    )

    if os.environ.get("SDIF_BENCHMARK_TOON") == "0":
        lines.append("- TOON skipped because `SDIF_BENCHMARK_TOON=0`.")
    elif "TOON" not in all_formats:
        lines.append(
            "- TOON skipped because neither global `toon` nor `npx @toon-format/cli` produced output."
        )

    if os.environ.get("SDIF_BENCHMARK_CLAUDE") != "1":
        lines.append("- Claude skipped because `SDIF_BENCHMARK_CLAUDE=1` was not set.")

    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- Raw log: `{evidence.run_dir.relative_to(REPO_ROOT) / 'comparison.log'}`",
            f"- Markdown report: `{evidence.run_dir.relative_to(REPO_ROOT) / 'comparison.md'}`",
            f"- Latest symlink: `{evidence.run_dir.parent.relative_to(REPO_ROOT) / 'latest'}`",
            "",
        ]
    )

    return "\n".join(lines)


# ====================
# Main
# ====================


def run_benchmark(run_dir: Path, *, env_file_loaded: bool) -> BenchmarkEvidence:
    golden_dir = REPO_ROOT / "examples/golden"
    documents = discover_documents(golden_dir)

    if not documents:
        raise SystemExit("No golden files found under examples/golden/*/equivalent.json")

    tokenizers = available_tokenizers()
    sample_data = json.loads(
        (golden_dir / documents[0] / "equivalent.json").read_text(encoding="utf-8")
    )
    primary_tokenizer = select_primary_tokenizer(tokenizers, json_compact(sample_data))
    results_by_document: dict[str, list[FormatResult]] = {}

    print_header(tokenizers, primary_tokenizer.name)

    for document_name in documents:
        source = golden_dir / document_name / "equivalent.json"
        data: dict[str, Any] = json.loads(source.read_text(encoding="utf-8"))

        compact_json = json_compact(data)
        primary_baseline = primary_tokenizer.counter(compact_json)

        rows = [
            count_format(
                name=format_name,
                text=text,
                tokenizers=tokenizers,
                primary_name=primary_tokenizer.name,
                primary_baseline=primary_baseline,
            )
            for format_name, text in build_formats(data)
        ]

        rows.sort(key=lambda row: sort_key(row, primary_tokenizer.name))
        results_by_document[document_name] = rows

        print_document_rows(document_name, rows, tokenizers)

    print_summary(
        documents_count=len(documents),
        results_by_document=results_by_document,
        tokenizers=tokenizers,
        primary_name=primary_tokenizer.name,
    )
    print_footer(results_by_document)

    return BenchmarkEvidence(
        generated_at=utc_now_iso(),
        run_dir=run_dir,
        golden_dir=golden_dir,
        primary_name=primary_tokenizer.name,
        tokenizers=tokenizers,
        results_by_document=results_by_document,
        env_file_loaded=env_file_loaded,
    )


def main() -> None:
    env_file_loaded = load_env_file(REPO_ROOT / ".env")

    run_dir = create_benchmark_run_dir()
    log_path = run_dir / "comparison.log"
    markdown_path = run_dir / "comparison.md"

    with log_path.open("w", encoding="utf-8") as log_file:
        with contextlib.redirect_stdout(Tee(sys.stdout, log_file)):
            evidence = run_benchmark(run_dir, env_file_loaded=env_file_loaded)

            markdown_path.write_text(
                render_markdown_report(evidence),
                encoding="utf-8",
            )

            latest = update_latest_symlink(run_dir)
            print_evidence_footer(run_dir, log_path, markdown_path, latest)


if __name__ == "__main__":
    main()
