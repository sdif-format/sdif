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
- TokenX through Node.js / npm / npx, heuristic estimator
- tiktoken / cl100k_base
- Llama 3 tokenizer through transformers
- Claude token counting API through anthropic, opt-in only

Each benchmark execution writes persistent evidence to:

- benchmarks/<timestamp>/comparison.log
- benchmarks/<timestamp>/comparison.md
- benchmarks/<timestamp>/summary.md
- benchmarks/<timestamp>/summary.json
- benchmarks/<timestamp>/summary.sdif
- benchmarks/<timestamp>/summary.sdif.ai
- benchmarks/<timestamp>/comparison.json
- benchmarks/<timestamp>/comparison.sdif
- benchmarks/<timestamp>/comparison.sdif.ai
- benchmarks/latest -> <timestamp>

By default, benchmark evidence is written under the repository `benchmarks/` directory.
Set `SDIF_BENCHMARK_OUTPUT_DIR` to redirect generated evidence to an external directory.
This is useful for tests, CI probes, and dry runs that must not mutate repository artifacts.

Environment variables:

- SDIF_BENCHMARK_OUTPUT_DIR=<path>
    Optional benchmark output directory.
    Default: benchmarks/ under the repository root.

- SDIF_BENCHMARK_TOON=0
    Disable TOON comparison.

- SDIF_BENCHMARK_TOKENX=0
    Disable TokenX token estimation.

- SDIF_TOKENX_DEFAULT_CHARS_PER_TOKEN=<number>
    Optional TokenX default characters-per-token heuristic.

- SDIF_TOKENX_RESOLVE_DIRS=<path-separated-dirs>
    Optional extra node_modules resolution roots for TokenX.

- SDIF_BENCHMARK_CLAUDE=1
    Enable Claude token counting. Requires ANTHROPIC_API_KEY.

- SDIF_CLAUDE_MODEL=<model>
    Claude model used for token counting.
    Default: claude-sonnet-4-5

- SDIF_BENCHMARK_LLAMA=0
    Disable Llama tokenizer counting.
    Default: enabled.

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

- SDIF_ENV_OVERRIDE=0
    Keep existing exported environment variables instead of overriding them from .env.
    Default: 1
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
from dataclasses import dataclass, field
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


@dataclass(frozen=True)
class RankedObservation:
    document_name: str
    tokenizer_name: str
    rank: int
    format_name: str
    tokens: int
    baseline_tokens: int
    saved_tokens: int
    ratio_value: float


@dataclass
class AggregateStats:
    ranks: list[float] = field(default_factory=list)
    ratios: list[float] = field(default_factory=list)
    saved_tokens: list[float] = field(default_factory=list)
    coverage: int = 0


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


def benchmark_output_dir() -> Path:
    configured = os.environ.get("SDIF_BENCHMARK_OUTPUT_DIR")

    if configured:
        return Path(configured).expanduser().resolve()

    return REPO_ROOT / "benchmarks"


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path.absolute())


def create_benchmark_run_dir(base_dir: Path | None = None) -> Path:
    target_dir = base_dir or benchmark_output_dir()
    target_dir.mkdir(parents=True, exist_ok=True)

    timestamp = benchmark_timestamp()
    run_dir = target_dir / timestamp
    counter = 1

    while run_dir.exists():
        run_dir = target_dir / f"{timestamp}-{counter:02d}"
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

        override_env = os.environ.get("SDIF_ENV_OVERRIDE", "1") != "0"

        if key in os.environ and not override_env:
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
    if os.environ.get("SDIF_BENCHMARK_LLAMA") == "0":
        return None

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


TOKENX_NODE_SCRIPT = r"""
import { createRequire } from 'node:module'
import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { pathToFileURL } from 'node:url'

const text = readFileSync(0, 'utf8')

const pathSeparator = process.platform === 'win32' ? ';' : ':'
const resolveDirs = (process.env.SDIF_TOKENX_RESOLVE_DIRS || '')
  .split(pathSeparator)
  .map((value) => value.trim())
  .filter(Boolean)

async function loadTokenx() {
  try {
    return await import('tokenx')
  } catch {
    // Continue with explicit resolution paths.
  }

  for (const dir of resolveDirs) {
    try {
      const require = createRequire(join(dir, 'package.json'))
      const resolved = require.resolve('tokenx')
      return await import(pathToFileURL(resolved).href)
    } catch {
      // Try the next directory.
    }
  }

  throw new Error(
    'Unable to resolve tokenx. Install it locally, globally, or allow npx fallback.'
  )
}

const { estimateTokenCount } = await loadTokenx()

const rawDefaultCharsPerToken = process.env.SDIF_TOKENX_DEFAULT_CHARS_PER_TOKEN
const defaultCharsPerToken = rawDefaultCharsPerToken
  ? Number(rawDefaultCharsPerToken)
  : undefined

const options = Number.isFinite(defaultCharsPerToken) && defaultCharsPerToken > 0
  ? { defaultCharsPerToken }
  : undefined

const count = estimateTokenCount(text, options)

if (!Number.isFinite(count)) {
  throw new Error(`TokenX returned a non-finite count: ${count}`)
}

process.stdout.write(String(Math.round(count)))
"""


@functools.lru_cache(maxsize=1)
def npm_global_root() -> str | None:
    npm = shutil.which("npm")
    if npm is None:
        return None

    try:
        completed = subprocess.run(
            [npm, "root", "-g"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        verbose_warning(f"Unable to detect npm global root: {exc}")
        return None

    if completed.returncode != 0:
        verbose_warning(f"Unable to detect npm global root: {completed.stderr.strip()}")
        return None

    root = completed.stdout.strip()
    return root or None


def tokenx_resolve_dirs() -> list[str]:
    dirs: list[str] = []

    local_node_modules = REPO_ROOT / "node_modules"
    if local_node_modules.exists():
        dirs.append(str(local_node_modules))

    global_root = npm_global_root()
    if global_root is not None:
        dirs.append(global_root)

    extra_dirs = os.environ.get("SDIF_TOKENX_RESOLVE_DIRS")
    if extra_dirs:
        dirs.extend(value.strip() for value in extra_dirs.split(os.pathsep) if value.strip())

    return dirs


def tokenx_environment() -> dict[str, str]:
    env = os.environ.copy()
    dirs = tokenx_resolve_dirs()

    if dirs:
        env["SDIF_TOKENX_RESOLVE_DIRS"] = os.pathsep.join(dirs)

    return env


def tokenx_candidate_commands() -> list[list[str]]:
    commands: list[list[str]] = []

    node = shutil.which("node")
    if node is not None:
        commands.append([node, "--input-type=module", "-e", TOKENX_NODE_SCRIPT])

    npx = shutil.which("npx")
    if npx is not None:
        commands.append(
            [
                npx,
                "-y",
                "-p",
                "tokenx",
                "node",
                "--input-type=module",
                "-e",
                TOKENX_NODE_SCRIPT,
            ]
        )

    return commands


@functools.lru_cache(maxsize=1)
def get_tokenx_command() -> tuple[list[str], dict[str, str]] | None:
    if os.environ.get("SDIF_BENCHMARK_TOKENX") == "0":
        return None

    commands = tokenx_candidate_commands()
    if not commands:
        verbose_warning("TokenX unavailable: neither `node` nor `npx` was found.")
        return None

    env = tokenx_environment()

    for command in commands:
        try:
            completed = subprocess.run(
                command,
                input="",
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                cwd=REPO_ROOT,
                env=env,
                timeout=30,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            verbose_warning(f"TokenX command failed to start: {' '.join(command[:3])} | {exc}")
            continue

        if completed.returncode == 0:
            return (command, env)

        verbose_warning(
            "TokenX command unavailable: "
            f"{' '.join(command[:4])} | stderr={completed.stderr.strip()}"
        )

    return None


def count_tokenx(text: str) -> int | None:
    """Estimate tokens with TokenX through Node.js, global npm, or npx fallback."""

    command_and_env = get_tokenx_command()
    if command_and_env is None:
        return None

    command, env = command_and_env

    try:
        completed = subprocess.run(
            command,
            input=text,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            cwd=REPO_ROOT,
            env=env,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        verbose_warning(f"TokenX failed: {exc}")
        return None

    if completed.returncode != 0:
        verbose_warning(f"TokenX failed: {completed.stderr.strip()}")
        return None

    output = completed.stdout.strip()

    try:
        return int(float(output))
    except ValueError:
        verbose_warning(f"TokenX returned invalid output: {output!r}")
        return None


def available_tokenizers() -> list[TokenizerSpec]:
    return [
        TokenizerSpec("Estimate", count_estimate),
        TokenizerSpec("TokenX", count_tokenx),
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


def format_integer(value: float | int | None) -> str:
    if value is None:
        return "-"
    return str(round(value))


def format_ratio(value: float | None) -> str:
    return "-" if value is None else f"{value:>6.1f}%"


def format_decimal(value: float | None, digits: int = 2) -> str:
    return "-" if value is None else f"{value:.{digits}f}"


def ratio(tokens: int | None, baseline: int | None) -> float | None:
    if tokens is None or baseline is None or baseline == 0:
        return None
    return (tokens / baseline) * 100


def average(values: list[float]) -> float:
    return sum(values) / len(values)


def median(values: list[float]) -> float:
    ordered = sorted(values)
    size = len(ordered)

    if size == 0:
        raise ValueError("Cannot calculate median of an empty list")

    midpoint = size // 2

    if size % 2 == 1:
        return ordered[midpoint]

    return (ordered[midpoint - 1] + ordered[midpoint]) / 2


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


def find_row(rows: list[FormatResult], format_name: str) -> FormatResult | None:
    return next((row for row in rows if row.name == format_name), None)


def tokenizer_baseline(rows: list[FormatResult], tokenizer_name: str) -> int | None:
    baseline = find_row(rows, "JSON Compact")
    if baseline is None:
        return None
    return baseline.tokens.get(tokenizer_name)


def ranked_rows_for_tokenizer(
    rows: list[FormatResult],
    tokenizer_name: str,
) -> list[FormatResult]:
    comparable = [row for row in rows if row.tokens.get(tokenizer_name) is not None]
    return sorted(
        comparable,
        key=lambda row: (
            row.tokens.get(tokenizer_name)
            if row.tokens.get(tokenizer_name) is not None
            else 10**12,
            row.bytes_size,
            row.name,
        ),
    )


def tokenizer_has_data(evidence: BenchmarkEvidence, tokenizer_name: str) -> bool:
    for rows in evidence.results_by_document.values():
        baseline = tokenizer_baseline(rows, tokenizer_name)
        if baseline is not None:
            return True
    return False


def available_tokenizer_names(evidence: BenchmarkEvidence) -> list[str]:
    return [
        tokenizer.name
        for tokenizer in evidence.tokenizers
        if tokenizer_has_data(evidence, tokenizer.name)
    ]


def iter_ranked_observations(
    evidence: BenchmarkEvidence,
    tokenizer_name: str,
) -> list[RankedObservation]:
    observations: list[RankedObservation] = []

    for document_name, rows in evidence.results_by_document.items():
        baseline = tokenizer_baseline(rows, tokenizer_name)
        if baseline is None:
            continue

        for index, row in enumerate(ranked_rows_for_tokenizer(rows, tokenizer_name), start=1):
            tokens = row.tokens.get(tokenizer_name)
            ratio_value = ratio(tokens, baseline)

            if tokens is None or ratio_value is None:
                continue

            observations.append(
                RankedObservation(
                    document_name=document_name,
                    tokenizer_name=tokenizer_name,
                    rank=index,
                    format_name=row.name,
                    tokens=tokens,
                    baseline_tokens=baseline,
                    saved_tokens=baseline - tokens,
                    ratio_value=ratio_value,
                )
            )

    return observations


def wins_by_tokenizer(evidence: BenchmarkEvidence, tokenizer_name: str) -> dict[str, int]:
    wins: dict[str, int] = {}

    for rows in evidence.results_by_document.values():
        ranked = ranked_rows_for_tokenizer(rows, tokenizer_name)
        baseline = tokenizer_baseline(rows, tokenizer_name)

        if not ranked or baseline is None:
            continue

        winner = ranked[0]
        wins[winner.name] = wins.get(winner.name, 0) + 1

    return wins


def tokenizer_kind(tokenizer_name: str) -> str:
    kinds = {
        "Estimate": "heuristic",
        "TokenX": "heuristic",
        "tiktoken": "model tokenizer",
        "Llama3": "model tokenizer",
        "Claude": "API tokenizer",
    }
    return kinds.get(tokenizer_name, "unknown")


def tokenizer_note(tokenizer_name: str) -> str:
    if tokenizer_name == "Estimate":
        return "Deterministic fallback: 4 UTF-8 bytes per token."

    if tokenizer_name == "TokenX":
        if os.environ.get("SDIF_BENCHMARK_TOKENX") == "0":
            return "Disabled through SDIF_BENCHMARK_TOKENX=0."
        return "Resolved through Node.js, local/global npm, or npx fallback."

    if tokenizer_name == "tiktoken":
        if tiktoken is None:
            return "Unavailable because Python package `tiktoken` is not installed."
        return f"Encoding: {os.environ.get('SDIF_TIKTOKEN_ENCODING', 'cl100k_base')}."

    if tokenizer_name == "Llama3":
        if os.environ.get("SDIF_BENCHMARK_LLAMA") == "0":
            return "Disabled through SDIF_BENCHMARK_LLAMA=0."
        if AutoTokenizer is None:
            return "Unavailable because Python package `transformers` is not installed."
        tokenizer = os.environ.get("SDIF_LLAMA_TOKENIZER", "meta-llama/Meta-Llama-3-8B")
        if os.environ.get("SDIF_LLAMA_LOCAL_ONLY") == "1":
            return (
                f"Tokenizer `{tokenizer}` could not be loaded from the local Hugging Face cache. "
                "Set SDIF_LLAMA_LOCAL_ONLY=0 to allow download, or pre-cache the tokenizer."
            )
        return f"Tokenizer: {tokenizer}."

    if tokenizer_name == "Claude":
        if os.environ.get("SDIF_BENCHMARK_CLAUDE") != "1":
            return "Disabled. Set SDIF_BENCHMARK_CLAUDE=1 to enable API token counting."
        if Anthropic is None:
            return "Unavailable because Python package `anthropic` is not installed."
        if not os.environ.get("ANTHROPIC_API_KEY"):
            return "Unavailable because ANTHROPIC_API_KEY is unset."
        return f"Model: {os.environ.get('SDIF_CLAUDE_MODEL', 'claude-sonnet-4-5')}."

    return ""


def tokenizer_status(evidence: BenchmarkEvidence, tokenizer_name: str) -> str:
    if tokenizer_has_data(evidence, tokenizer_name):
        return "available"

    if tokenizer_name == "TokenX" and os.environ.get("SDIF_BENCHMARK_TOKENX") == "0":
        return "disabled"

    if tokenizer_name == "Llama3" and os.environ.get("SDIF_BENCHMARK_LLAMA") == "0":
        return "disabled"

    if tokenizer_name == "Claude" and os.environ.get("SDIF_BENCHMARK_CLAUDE") != "1":
        return "disabled"

    return "unavailable"


def format_coverage(value: int, total: int) -> str:
    return f"{value}/{total}"


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
    print(f"Console ordering and ratio: {primary_name} vs JSON Compact\n")
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
    print("\n📈 Average ratio vs JSON Compact by tokenizer")
    print("=" * 112)

    for tokenizer in tokenizers:
        tokenizer_name = tokenizer.name
        ratios_by_format: dict[str, list[float]] = {}

        for rows in results_by_document.values():
            baseline = tokenizer_baseline(rows, tokenizer_name)

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

    print(f"\n🏁 Console wins by {primary_name}")
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


def print_evidence_footer(
    run_dir: Path,
    log_path: Path,
    markdown_path: Path,
    summary_path: Path,
    summary_json_path: Path,
    summary_sdif_path: Path,
    summary_sdif_ai_path: Path,
    json_path: Path,
    sdif_path: Path,
    sdif_ai_path: Path,
    latest: Path,
) -> None:
    print()
    print("🧾 Benchmark evidence written")
    print(f"  log:      {display_path(log_path)}")
    print(f"  markdown: {display_path(markdown_path)}")
    print(f"  summary:  {display_path(summary_path)}")
    print(f"  summary json:    {display_path(summary_json_path)}")
    print(f"  summary sdif:    {display_path(summary_sdif_path)}")
    print(f"  summary sdif.ai: {display_path(summary_sdif_ai_path)}")
    print(f"  json:     {display_path(json_path)}")
    print(f"  sdif:     {display_path(sdif_path)}")
    print(f"  sdif.ai:  {display_path(sdif_ai_path)}")
    print(f"  latest:   {display_path(latest)} -> {run_dir.name}")


# ====================
# Markdown report rendering
# ====================


def render_markdown_report(evidence: BenchmarkEvidence) -> str:
    lines: list[str] = [
        "# SDIF Benchmark Evidence Report",
        "",
        f"- Generated at: `{evidence.generated_at}`",
        f"- Run directory: `{display_path(evidence.run_dir)}`",
        f"- Semantic source: `{display_path(evidence.golden_dir)}/<document>/equivalent.json`",
        "- Ratios are computed independently per tokenizer against `JSON Compact`.",
        "- All formats are derived from the same canonical JSON semantic source.",
        f"- Console ordering tokenizer: `{evidence.primary_name}`",
        f"- `.env` loaded: `{'yes' if evidence.env_file_loaded else 'no'}`",
        "",
    ]

    lines.extend(render_executive_summary(evidence))
    lines.extend(render_tokenizer_results(evidence))
    lines.extend(render_document_analysis(evidence))
    lines.extend(render_raw_count_matrix(evidence))
    lines.extend(render_environment(evidence))
    lines.extend(render_notes(evidence))
    lines.extend(render_artifacts(evidence))

    return "\n".join(lines)


def consensus_rows(
    evidence: BenchmarkEvidence,
) -> list[tuple[str, float, float, float, float, float, int, int]]:
    """Return consensus rows ordered by average rank and median ratio."""

    documents_count = len(evidence.results_by_document)
    available_names = available_tokenizer_names(evidence)
    total_observations = documents_count * len(available_names)
    aggregates: dict[str, AggregateStats] = {}

    if total_observations == 0:
        return []

    for tokenizer_name in available_names:
        for observation in iter_ranked_observations(evidence, tokenizer_name):
            entry = aggregates.setdefault(observation.format_name, AggregateStats())
            entry.ranks.append(float(observation.rank))
            entry.ratios.append(observation.ratio_value)
            entry.coverage += 1

    rows: list[tuple[str, float, float, float, float, float, int, int]] = []

    for format_name, stats in aggregates.items():
        rows.append(
            (
                format_name,
                average(stats.ranks),
                median(stats.ratios),
                min(stats.ratios),
                max(stats.ratios),
                max(stats.ranks) - min(stats.ranks),
                stats.coverage,
                total_observations,
            )
        )

    return sorted(rows, key=lambda row: (row[1], row[2], row[0]))


def average_ratio_for_format(
    evidence: BenchmarkEvidence,
    tokenizer_name: str,
    format_name: str,
) -> float | None:
    values: list[float] = []

    for rows in evidence.results_by_document.values():
        baseline = tokenizer_baseline(rows, tokenizer_name)
        row = find_row(rows, format_name)

        if row is None:
            continue

        value = ratio(row.tokens.get(tokenizer_name), baseline)
        if value is not None:
            values.append(value)

    if not values:
        return None

    return average(values)


def total_wins_for_format(evidence: BenchmarkEvidence, format_name: str) -> int:
    total = 0

    for tokenizer_name in available_tokenizer_names(evidence):
        total += wins_by_tokenizer(evidence, tokenizer_name).get(format_name, 0)

    return total


def render_summary_report(evidence: BenchmarkEvidence) -> str:
    available_names = available_tokenizer_names(evidence)
    documents_count = len(evidence.results_by_document)
    consensus = consensus_rows(evidence)

    lines: list[str] = [
        "# SDIF Benchmark Summary",
        "",
        f"- Generated at: `{evidence.generated_at}`",
        f"- Run directory: `{display_path(evidence.run_dir)}`",
        f"- Full report: `{display_path(evidence.run_dir / 'comparison.md')}`",
        f"- Structured JSON: `{display_path(evidence.run_dir / 'comparison.json')}`",
        f"- Structured SDIF: `{display_path(evidence.run_dir / 'comparison.sdif')}`",
        f"- SDIF AI projection: `{display_path(evidence.run_dir / 'comparison.sdif.ai')}`",
        f"- Raw log: `{display_path(evidence.run_dir / 'comparison.log')}`",
        f"- Documents compared: `{documents_count}`",
        f"- Available tokenizers: `{', '.join(available_names) if available_names else 'none'}`",
        "",
        "## Key Findings",
        "",
    ]

    if consensus:
        (
            best_format,
            avg_rank,
            median_ratio,
            _best_ratio,
            _worst_ratio,
            _rank_spread,
            coverage,
            total,
        ) = consensus[0]
        lines.extend(
            [
                f"- Best consensus format: **{markdown_escape(best_format)}** "
                f"(avg rank `{avg_rank:.2f}`, median ratio `{median_ratio:.1f}%`, coverage `{coverage}/{total}`).",
                "- Ratios are computed independently per tokenizer against `JSON Compact`.",
            ]
        )
    else:
        lines.append("- No tokenizer produced comparable results.")

    for tokenizer_name in available_names:
        wins = wins_by_tokenizer(evidence, tokenizer_name)
        if not wins:
            continue

        winners = ", ".join(
            f"{format_name} {count}/{documents_count}"
            for format_name, count in sorted(wins.items(), key=lambda item: (-item[1], item[0]))
        )
        lines.append(f"- `{markdown_escape(tokenizer_name)}` winners: {markdown_escape(winners)}.")

    lines.extend(
        [
            "",
            "## Tokenizer Availability",
            "",
            "| Tokenizer | Status | Type | Notes |",
            "| --- | --- | --- | --- |",
        ]
    )

    for tokenizer in evidence.tokenizers:
        lines.append(
            f"| `{markdown_escape(tokenizer.name)}` "
            f"| {tokenizer_status(evidence, tokenizer.name)} "
            f"| {tokenizer_kind(tokenizer.name)} "
            f"| {markdown_escape(tokenizer_note(tokenizer.name))} |"
        )

    lines.extend(
        [
            "",
            "## Consensus Ranking",
            "",
            "| Format | Avg Rank | Median Ratio | Best Ratio | Worst Ratio | Rank Spread | Coverage |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )

    for (
        format_name,
        avg_rank,
        median_ratio,
        best_ratio,
        worst_ratio,
        rank_spread,
        coverage,
        total,
    ) in consensus:
        lines.append(
            f"| {markdown_escape(format_name)} "
            f"| {avg_rank:.2f} "
            f"| {median_ratio:.1f}% "
            f"| {best_ratio:.1f}% "
            f"| {worst_ratio:.1f}% "
            f"| {rank_spread:.0f} "
            f"| {coverage}/{total} |"
        )

    selected_formats = [
        "SDIF AI",
        "SDIF",
        "TOON",
        "CSV Bundle",
        "JSON Compact",
    ]

    lines.extend(
        [
            "",
            "## Direct Comparison",
            "",
            "Focused comparison of the main formats a reader is most likely to care about.",
            "",
            "| Format | Consensus Avg Rank | Consensus Median Ratio | Wins Across Tokenizer/Document Pairs | "
            + " | ".join(f"`{markdown_escape(name)}` Avg Ratio" for name in available_names)
            + " |",
            "| --- | ---: |---:|---:|" + "|".join("---:" for _ in available_names) + "|",
        ]
    )

    consensus_by_format = {row[0]: row for row in consensus}

    for format_name in selected_formats:
        if format_name not in consensus_by_format:
            continue

        _, avg_rank, median_ratio, *_rest = consensus_by_format[format_name]
        ratio_columns = [
            format_ratio(average_ratio_for_format(evidence, tokenizer_name, format_name)).strip()
            for tokenizer_name in available_names
        ]

        lines.append(
            f"| {markdown_escape(format_name)} "
            f"| {avg_rank:.2f} "
            f"| {median_ratio:.1f}% "
            f"| {total_wins_for_format(evidence, format_name)} "
            f"| {' | '.join(ratio_columns)} |"
        )

    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- Full benchmark report: `{display_path(evidence.run_dir / 'comparison.md')}`",
            f"- Structured JSON report: `{display_path(evidence.run_dir / 'comparison.json')}`",
            f"- Structured SDIF report: `{display_path(evidence.run_dir / 'comparison.sdif')}`",
            f"- SDIF AI projection: `{display_path(evidence.run_dir / 'comparison.sdif.ai')}`",
            f"- Raw benchmark log: `{display_path(evidence.run_dir / 'comparison.log')}`",
            f"- Latest symlink: `{display_path(evidence.run_dir.parent / 'latest')}`",
            "",
        ]
    )

    return "\n".join(lines)


def structured_report_data(evidence: BenchmarkEvidence) -> dict[str, Any]:
    available_names = available_tokenizer_names(evidence)
    documents_count = len(evidence.results_by_document)

    data: dict[str, Any] = {
        "kind": "BenchmarkReport",
        "version": "1.0",
        "generatedAt": evidence.generated_at,
        "runDirectory": display_path(evidence.run_dir),
        "semanticSource": f"{display_path(evidence.golden_dir)}/<document>/equivalent.json",
        "ratiosBaseline": "JSON Compact",
        "consoleOrderingTokenizer": evidence.primary_name,
        "envFileLoaded": evidence.env_file_loaded,
        "documentsCompared": documents_count,
        "availableTokenizers": available_names,
        "tokenizers": [],
        "consensusRanking": [],
        "winnersByTokenizer": [],
        "directComparison": [],
        "documents": [],
        "environment": {
            "SDIF_BENCHMARK_TOON": os.environ.get("SDIF_BENCHMARK_TOON"),
            "SDIF_BENCHMARK_TOKENX": os.environ.get("SDIF_BENCHMARK_TOKENX"),
            "SDIF_TOKENX_DEFAULT_CHARS_PER_TOKEN": os.environ.get(
                "SDIF_TOKENX_DEFAULT_CHARS_PER_TOKEN"
            ),
            "SDIF_TOKENX_RESOLVE_DIRS": os.environ.get("SDIF_TOKENX_RESOLVE_DIRS"),
            "SDIF_BENCHMARK_CLAUDE": os.environ.get("SDIF_BENCHMARK_CLAUDE"),
            "SDIF_CLAUDE_MODEL": os.environ.get("SDIF_CLAUDE_MODEL"),
            "SDIF_BENCHMARK_LLAMA": os.environ.get("SDIF_BENCHMARK_LLAMA"),
            "SDIF_LLAMA_TOKENIZER": os.environ.get("SDIF_LLAMA_TOKENIZER"),
            "SDIF_LLAMA_LOCAL_ONLY": os.environ.get("SDIF_LLAMA_LOCAL_ONLY"),
            "SDIF_TIKTOKEN_ENCODING": os.environ.get("SDIF_TIKTOKEN_ENCODING"),
            "HF_TOKEN": "set" if os.environ.get("HF_TOKEN") else "unset",
            "ANTHROPIC_API_KEY": "set" if os.environ.get("ANTHROPIC_API_KEY") else "unset",
        },
        "artifacts": {
            "log": display_path(evidence.run_dir / "comparison.log"),
            "markdown": display_path(evidence.run_dir / "comparison.md"),
            "summary": display_path(evidence.run_dir / "summary.md"),
            "summaryJson": display_path(evidence.run_dir / "summary.json"),
            "summarySdif": display_path(evidence.run_dir / "summary.sdif"),
            "summarySdifAi": display_path(evidence.run_dir / "summary.sdif.ai"),
            "json": display_path(evidence.run_dir / "comparison.json"),
            "sdif": display_path(evidence.run_dir / "comparison.sdif"),
            "sdifAi": display_path(evidence.run_dir / "comparison.sdif.ai"),
            "latest": display_path(evidence.run_dir.parent / "latest"),
        },
    }

    for tokenizer in evidence.tokenizers:
        data["tokenizers"].append(
            {
                "name": tokenizer.name,
                "status": tokenizer_status(evidence, tokenizer.name),
                "type": tokenizer_kind(tokenizer.name),
                "notes": tokenizer_note(tokenizer.name),
            }
        )

    for (
        format_name,
        avg_rank,
        median_ratio,
        best_ratio,
        worst_ratio,
        rank_spread,
        coverage,
        total,
    ) in consensus_rows(evidence):
        data["consensusRanking"].append(
            {
                "format": format_name,
                "avgRank": avg_rank,
                "medianRatio": median_ratio,
                "bestRatio": best_ratio,
                "worstRatio": worst_ratio,
                "rankSpread": rank_spread,
                "coverage": coverage,
                "coverageTotal": total,
            }
        )

    for tokenizer_name in available_names:
        wins = wins_by_tokenizer(evidence, tokenizer_name)
        for format_name, count in sorted(wins.items(), key=lambda item: (-item[1], item[0])):
            data["winnersByTokenizer"].append(
                {
                    "tokenizer": tokenizer_name,
                    "format": format_name,
                    "wins": count,
                    "documents": documents_count,
                }
            )

    selected_formats = ["SDIF AI", "SDIF", "TOON", "CSV Bundle", "JSON Compact"]
    consensus_by_format = {row[0]: row for row in consensus_rows(evidence)}

    for format_name in selected_formats:
        if format_name not in consensus_by_format:
            continue

        _, avg_rank, median_ratio, best_ratio, worst_ratio, rank_spread, coverage, total = (
            consensus_by_format[format_name]
        )
        data["directComparison"].append(
            {
                "format": format_name,
                "consensusAvgRank": avg_rank,
                "consensusMedianRatio": median_ratio,
                "consensusBestRatio": best_ratio,
                "consensusWorstRatio": worst_ratio,
                "consensusRankSpread": rank_spread,
                "coverage": coverage,
                "coverageTotal": total,
                "totalWins": total_wins_for_format(evidence, format_name),
                "avgRatioByTokenizer": {
                    tokenizer_name: average_ratio_for_format(evidence, tokenizer_name, format_name)
                    for tokenizer_name in available_names
                },
            }
        )

    for document_name, rows in evidence.results_by_document.items():
        document_data: dict[str, Any] = {
            "name": document_name,
            "winnersByTokenizer": [],
            "formats": [],
        }

        for tokenizer_name in available_names:
            baseline = tokenizer_baseline(rows, tokenizer_name)
            ranked = ranked_rows_for_tokenizer(rows, tokenizer_name)

            if baseline is None or not ranked:
                continue

            winner = ranked[0]
            winner_tokens = winner.tokens.get(tokenizer_name)
            document_data["winnersByTokenizer"].append(
                {
                    "tokenizer": tokenizer_name,
                    "format": winner.name,
                    "tokens": winner_tokens,
                    "jsonCompactTokens": baseline,
                    "savedTokens": baseline - winner_tokens if winner_tokens is not None else None,
                    "ratio": ratio(winner_tokens, baseline),
                }
            )

        for row in rows:
            format_data: dict[str, Any] = {
                "format": row.name,
                "bytes": row.bytes_size,
                "tokens": row.tokens,
                "ratios": {},
                "ranks": {},
            }

            for tokenizer_name in available_names:
                baseline = tokenizer_baseline(rows, tokenizer_name)
                format_data["ratios"][tokenizer_name] = ratio(
                    row.tokens.get(tokenizer_name), baseline
                )

                for rank_index, ranked_row in enumerate(
                    ranked_rows_for_tokenizer(rows, tokenizer_name), start=1
                ):
                    if ranked_row.name == row.name:
                        format_data["ranks"][tokenizer_name] = rank_index
                        break

            document_data["formats"].append(format_data)

        data["documents"].append(document_data)

    return data


def render_json_report(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def render_sdif_report(data: dict[str, Any]) -> str:
    return json_data_to_sdif(data, include_header=True)


def render_sdif_ai_report(sdif_text: str) -> str:
    return compact_ai_projection(sdif_text)


def render_executive_summary(evidence: BenchmarkEvidence) -> list[str]:
    documents_count = len(evidence.results_by_document)
    available_names = available_tokenizer_names(evidence)
    total_observations = documents_count * len(available_names)

    lines: list[str] = [
        "## Executive Summary",
        "",
        "### Tokenizer Availability",
        "",
        "| Tokenizer | Status | Type | Notes |",
        "| --- | --- | --- | --- |",
    ]

    for tokenizer in evidence.tokenizers:
        lines.append(
            f"| `{markdown_escape(tokenizer.name)}` "
            f"| {tokenizer_status(evidence, tokenizer.name)} "
            f"| {tokenizer_kind(tokenizer.name)} "
            f"| {markdown_escape(tokenizer_note(tokenizer.name))} |"
        )

    lines.extend(
        [
            "",
            "### Consensus Ranking",
            "",
        ]
    )

    if not available_names:
        lines.extend(
            [
                "No tokenizer produced comparable results.",
                "",
            ]
        )
        return lines

    aggregates: dict[str, AggregateStats] = {}

    for tokenizer_name in available_names:
        for observation in iter_ranked_observations(evidence, tokenizer_name):
            entry = aggregates.setdefault(observation.format_name, AggregateStats())
            entry.ranks.append(float(observation.rank))
            entry.ratios.append(observation.ratio_value)
            entry.saved_tokens.append(float(observation.saved_tokens))
            entry.coverage += 1

    lines.extend(
        [
            "| Format | Avg Rank | Median Ratio | Best Ratio | Worst Ratio | Rank Spread | Coverage |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )

    def consensus_sort_key(item: tuple[str, AggregateStats]) -> tuple[float, float, str]:
        format_name, stats = item
        return (average(stats.ranks), median(stats.ratios), format_name)

    for format_name, stats in sorted(aggregates.items(), key=consensus_sort_key):
        rank_spread = max(stats.ranks) - min(stats.ranks)

        lines.append(
            f"| {markdown_escape(format_name)} "
            f"| {average(stats.ranks):.2f} "
            f"| {median(stats.ratios):.1f}% "
            f"| {min(stats.ratios):.1f}% "
            f"| {max(stats.ratios):.1f}% "
            f"| {rank_spread:.0f} "
            f"| {format_coverage(stats.coverage, total_observations)} |"
        )

    lines.extend(
        [
            "",
            "### Winners by Tokenizer",
            "",
            "| Tokenizer | Winner Format | Wins | Documents |",
            "| --- | --- | ---: | ---: |",
        ]
    )

    for tokenizer_name in available_names:
        wins = wins_by_tokenizer(evidence, tokenizer_name)

        if not wins:
            lines.append(f"| `{markdown_escape(tokenizer_name)}` | - | 0 | {documents_count} |")
            continue

        for format_name, count in sorted(wins.items(), key=lambda item: (-item[1], item[0])):
            lines.append(
                f"| `{markdown_escape(tokenizer_name)}` "
                f"| {markdown_escape(format_name)} "
                f"| {count} "
                f"| {documents_count} |"
            )

    lines.append("")
    return lines


def render_tokenizer_results(evidence: BenchmarkEvidence) -> list[str]:
    documents_count = len(evidence.results_by_document)

    lines: list[str] = [
        "## Tokenizer Results",
        "",
    ]

    for tokenizer in evidence.tokenizers:
        tokenizer_name = tokenizer.name
        observations = iter_ranked_observations(evidence, tokenizer_name)

        lines.extend(
            [
                f"### `{markdown_escape(tokenizer_name)}`",
                "",
            ]
        )

        if not observations:
            status = tokenizer_status(evidence, tokenizer_name)
            label = "Disabled" if status == "disabled" else "Unavailable"
            lines.extend(
                [
                    f"{label}. {markdown_escape(tokenizer_note(tokenizer_name))}",
                    "",
                ]
            )
            continue

        by_format: dict[str, AggregateStats] = {}

        for observation in observations:
            entry = by_format.setdefault(observation.format_name, AggregateStats())
            entry.ranks.append(float(observation.rank))
            entry.ratios.append(observation.ratio_value)
            entry.saved_tokens.append(float(observation.saved_tokens))
            entry.coverage += 1

        wins = wins_by_tokenizer(evidence, tokenizer_name)

        lines.extend(
            [
                "#### Summary",
                "",
                "| Format | Avg Rank | Avg Ratio | Median Ratio | Avg Saved Tokens | Wins | Coverage |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )

        def sort_tokenizer_summary(item: tuple[str, AggregateStats]) -> tuple[float, float, str]:
            format_name, stats = item
            return (average(stats.ranks), average(stats.ratios), format_name)

        for format_name, stats in sorted(by_format.items(), key=sort_tokenizer_summary):
            lines.append(
                f"| {markdown_escape(format_name)} "
                f"| {average(stats.ranks):.2f} "
                f"| {average(stats.ratios):.1f}% "
                f"| {median(stats.ratios):.1f}% "
                f"| {round(average(stats.saved_tokens))} "
                f"| {wins.get(format_name, 0)} "
                f"| {format_coverage(stats.coverage, documents_count)} |"
            )

        lines.extend(
            [
                "",
                "#### Per-document Ranking",
                "",
                "| Document | Rank | Format | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |",
                "| --- | ---: | --- | ---: | ---: | ---: | ---: |",
            ]
        )

        for observation in observations:
            lines.append(
                f"| `{markdown_escape(observation.document_name)}` "
                f"| {observation.rank} "
                f"| {markdown_escape(observation.format_name)} "
                f"| {observation.tokens} "
                f"| {observation.baseline_tokens} "
                f"| {observation.saved_tokens} "
                f"| {observation.ratio_value:.1f}% |"
            )

        lines.append("")

    return lines


def render_document_analysis(evidence: BenchmarkEvidence) -> list[str]:
    available_names = available_tokenizer_names(evidence)

    lines: list[str] = [
        "## Document Analysis",
        "",
    ]

    if not available_names:
        lines.extend(["No tokenizer produced comparable document-level results.", ""])
        return lines

    for document_name, rows in evidence.results_by_document.items():
        lines.extend(
            [
                f"### `{markdown_escape(document_name)}`",
                "",
                "#### Winners by Tokenizer",
                "",
                "| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |",
                "| --- | --- | ---: | ---: | ---: | ---: |",
            ]
        )

        for tokenizer_name in available_names:
            baseline = tokenizer_baseline(rows, tokenizer_name)
            ranked = ranked_rows_for_tokenizer(rows, tokenizer_name)

            if baseline is None or not ranked:
                lines.append(f"| `{markdown_escape(tokenizer_name)}` | - | - | - | - | - |")
                continue

            winner = ranked[0]
            winner_tokens = winner.tokens.get(tokenizer_name)
            winner_ratio = ratio(winner_tokens, baseline)

            lines.append(
                f"| `{markdown_escape(tokenizer_name)}` "
                f"| {markdown_escape(winner.name)} "
                f"| {format_count(winner_tokens)} "
                f"| {baseline} "
                f"| {baseline - winner_tokens if winner_tokens is not None else '-'} "
                f"| {format_ratio(winner_ratio).strip()} |"
            )

        lines.extend(
            [
                "",
                "#### Ratio Matrix",
                "",
                "| Format | "
                + " | ".join(f"`{markdown_escape(name)}`" for name in available_names)
                + " |",
                "|---|" + "|".join("---:" for _ in available_names) + "|",
            ]
        )

        for row in sorted(
            rows, key=lambda item: document_format_sort_key(item, rows, available_names)
        ):
            ratio_columns: list[str] = []

            for tokenizer_name in available_names:
                baseline = tokenizer_baseline(rows, tokenizer_name)
                value = ratio(row.tokens.get(tokenizer_name), baseline)
                ratio_columns.append(format_ratio(value).strip())

            lines.append(f"| {markdown_escape(row.name)} | {' | '.join(ratio_columns)} |")

        lines.append("")

    return lines


def document_format_sort_key(
    row: FormatResult,
    rows: list[FormatResult],
    tokenizer_names: list[str],
) -> tuple[float, float, int, str]:
    ranks: list[float] = []
    ratios: list[float] = []

    for tokenizer_name in tokenizer_names:
        ranked = ranked_rows_for_tokenizer(rows, tokenizer_name)
        baseline = tokenizer_baseline(rows, tokenizer_name)

        if baseline is None:
            continue

        for index, ranked_row in enumerate(ranked, start=1):
            if ranked_row.name != row.name:
                continue

            value = ratio(row.tokens.get(tokenizer_name), baseline)
            if value is not None:
                ranks.append(float(index))
                ratios.append(value)

    if not ranks or not ratios:
        return (10**12, 10**12, row.bytes_size, row.name)

    return (average(ranks), average(ratios), row.bytes_size, row.name)


def render_raw_count_matrix(evidence: BenchmarkEvidence) -> list[str]:
    token_headers = [tokenizer.name for tokenizer in evidence.tokenizers]

    lines: list[str] = [
        "## Raw Count Matrix",
        "",
        "This section contains raw counts only. Ratios are intentionally excluded here because they are tokenizer-specific.",
        "",
    ]

    for document_name, rows in evidence.results_by_document.items():
        lines.extend(
            [
                f"### `{markdown_escape(document_name)}`",
                "",
                "| Format | Bytes | "
                + " | ".join(f"`{markdown_escape(name)}`" for name in token_headers)
                + " |",
                "| --- | ---: |" + "|".join("---:" for _ in token_headers) + "|",
            ]
        )

        for row in rows:
            token_columns = " | ".join(
                format_count(row.tokens.get(tokenizer.name)) for tokenizer in evidence.tokenizers
            )

            lines.append(f"| {markdown_escape(row.name)} | {row.bytes_size} | {token_columns} |")

        lines.append("")

    return lines


def render_environment(evidence: BenchmarkEvidence) -> list[str]:
    return [
        "## Environment",
        "",
        "| Variable | Value |",
        "| --- | --- |",
        f"| `.env loaded` | `{'yes' if evidence.env_file_loaded else 'no'}` |",
        f"| `SDIF_BENCHMARK_TOON` | {env_value('SDIF_BENCHMARK_TOON')} |",
        f"| `SDIF_BENCHMARK_TOKENX` | {env_value('SDIF_BENCHMARK_TOKENX')} |",
        f"| `SDIF_TOKENX_DEFAULT_CHARS_PER_TOKEN` | {env_value('SDIF_TOKENX_DEFAULT_CHARS_PER_TOKEN')} |",
        f"| `SDIF_TOKENX_RESOLVE_DIRS` | {env_value('SDIF_TOKENX_RESOLVE_DIRS')} |",
        f"| `SDIF_BENCHMARK_CLAUDE` | {env_value('SDIF_BENCHMARK_CLAUDE')} |",
        f"| `SDIF_CLAUDE_MODEL` | {env_value('SDIF_CLAUDE_MODEL')} |",
        f"| `SDIF_BENCHMARK_LLAMA` | {env_value('SDIF_BENCHMARK_LLAMA')} |",
        f"| `SDIF_LLAMA_TOKENIZER` | {env_value('SDIF_LLAMA_TOKENIZER')} |",
        f"| `SDIF_LLAMA_LOCAL_ONLY` | {env_value('SDIF_LLAMA_LOCAL_ONLY')} |",
        f"| `SDIF_TIKTOKEN_ENCODING` | {env_value('SDIF_TIKTOKEN_ENCODING')} |",
        f"| `HF_TOKEN` | {env_value('HF_TOKEN', secret=True)} |",
        f"| `ANTHROPIC_API_KEY` | {env_value('ANTHROPIC_API_KEY', secret=True)} |",
        "",
    ]


def render_notes(evidence: BenchmarkEvidence) -> list[str]:
    all_formats = {row.name for rows in evidence.results_by_document.values() for row in rows}

    lines: list[str] = [
        "## Notes",
        "",
    ]

    if os.environ.get("SDIF_BENCHMARK_TOON") == "0":
        lines.append("- TOON skipped because `SDIF_BENCHMARK_TOON=0`.")
    elif "TOON" not in all_formats:
        lines.append(
            "- TOON skipped because neither global `toon` nor `npx @toon-format/cli` produced output."
        )

    for tokenizer in evidence.tokenizers:
        status = tokenizer_status(evidence, tokenizer.name)
        if status != "available":
            lines.append(
                f"- `{markdown_escape(tokenizer.name)}` is {status}: "
                f"{markdown_escape(tokenizer_note(tokenizer.name))}"
            )

    if len(lines) == 2:
        lines.append("- No additional notes.")

    lines.append("")
    return lines


def render_artifacts(evidence: BenchmarkEvidence) -> list[str]:
    return [
        "## Artifacts",
        "",
        f"- Raw log: `{display_path(evidence.run_dir / 'comparison.log')}`",
        f"- Markdown report: `{display_path(evidence.run_dir / 'comparison.md')}`",
        f"- Summary report: `{display_path(evidence.run_dir / 'summary.md')}`",
        f"- Structured JSON report: `{display_path(evidence.run_dir / 'comparison.json')}`",
        f"- Structured SDIF report: `{display_path(evidence.run_dir / 'comparison.sdif')}`",
        f"- SDIF AI projection: `{display_path(evidence.run_dir / 'comparison.sdif.ai')}`",
        f"- Latest symlink: `{display_path(evidence.run_dir.parent / 'latest')}`",
        "",
    ]


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
    summary_path = run_dir / "summary.md"
    summary_json_path = run_dir / "summary.json"
    summary_sdif_path = run_dir / "summary.sdif"
    summary_sdif_ai_path = run_dir / "summary.sdif.ai"
    json_path = run_dir / "comparison.json"
    sdif_path = run_dir / "comparison.sdif"
    sdif_ai_path = run_dir / "comparison.sdif.ai"

    with log_path.open("w", encoding="utf-8") as log_file:
        with contextlib.redirect_stdout(Tee(sys.stdout, log_file)):
            evidence = run_benchmark(run_dir, env_file_loaded=env_file_loaded)
            structured_data = structured_report_data(evidence)
            sdif_text = render_sdif_report(structured_data)

            markdown_path.write_text(
                render_markdown_report(evidence),
                encoding="utf-8",
            )
            summary_path.write_text(
                render_summary_report(evidence),
                encoding="utf-8",
            )
            json_path.write_text(
                render_json_report(structured_data),
                encoding="utf-8",
            )
            summary_json_path.write_text(
                render_json_report(structured_data),
                encoding="utf-8",
            )
            sdif_path.write_text(
                sdif_text,
                encoding="utf-8",
            )
            summary_sdif_path.write_text(
                sdif_text,
                encoding="utf-8",
            )
            sdif_ai_path.write_text(
                render_sdif_ai_report(sdif_text),
                encoding="utf-8",
            )
            summary_sdif_ai_path.write_text(
                render_sdif_ai_report(sdif_text),
                encoding="utf-8",
            )

            latest = update_latest_symlink(run_dir)
            print_evidence_footer(
                run_dir,
                log_path,
                markdown_path,
                summary_path,
                summary_json_path,
                summary_sdif_path,
                summary_sdif_ai_path,
                json_path,
                sdif_path,
                sdif_ai_path,
                latest,
            )


if __name__ == "__main__":
    main()
