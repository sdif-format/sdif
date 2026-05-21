#!/usr/bin/env python3
"""SDIF benchmark generated from canonical JSON golden files.

The benchmark derives all compared formats from the same canonical JSON source:

- JSON Compact
- JSON Pretty
- YAML
- SDIF
- TOON, when the official CLI is available

It can count tokens with multiple tokenizers:

- tiktoken / cl100k_base
- Llama 3 tokenizer through transformers
- Claude token counting API through anthropic, opt-in only

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
"""

from __future__ import annotations

import functools
import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import yaml

from sdif.json import json_data_to_sdif

REPO_ROOT = Path(__file__).resolve().parents[1]


# ====================
# Optional dependencies
# ====================

try:
    import tiktoken
except ImportError:
    tiktoken = None


try:
    from transformers import AutoTokenizer
except ImportError:
    AutoTokenizer = None


try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None


# ====================
# Types
# ====================

TokenCounter = Callable[[str], int | None]


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


# ====================
# Format generators
# ====================

def json_compact(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def json_pretty(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def yaml_generated(data: dict[str, Any]) -> str:
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)


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
        TokenizerSpec("tiktoken", count_tiktoken),
        TokenizerSpec("Llama3", count_llama3),
        TokenizerSpec("Claude", count_claude),
    ]


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
    formats: list[tuple[str, str]] = [
        ("JSON Compact", json_compact(data)),
        ("JSON Pretty", json_pretty(data)),
        ("YAML", yaml_generated(data)),
        ("SDIF", json_data_to_sdif(data, include_header=True)),
    ]

    toon_text = toon_from_cli(data)
    if toon_text is not None:
        formats.append(("TOON", toon_text))

    return formats


def count_format(
    name: str,
    text: str,
    tokenizers: list[TokenizerSpec],
    primary_baseline: int | None,
) -> FormatResult:
    tokens = {
        tokenizer.name: tokenizer.counter(text)
        for tokenizer in tokenizers
    }

    primary_tokens = tokens.get("tiktoken")
    primary_ratio = ratio(primary_tokens, primary_baseline)

    return FormatResult(
        name=name,
        text=text,
        bytes_size=len(text.encode("utf-8")),
        tokens=tokens,
        primary_ratio=primary_ratio,
    )


def sort_key(row: FormatResult) -> tuple[int, int, int, str]:
    primary = row.tokens.get("tiktoken")

    if primary is None:
        return (1, 10**12, row.bytes_size, row.name)

    return (0, primary, row.bytes_size, row.name)


def discover_documents(golden_dir: Path) -> list[str]:
    return [
        path.parent.name
        for path in sorted(golden_dir.glob("*/equivalent.json"))
    ]


# ====================
# Rendering
# ====================

def print_header(tokenizers: list[TokenizerSpec]) -> None:
    tokenizer_columns = "".join(f" {tokenizer.name:>9}" for tokenizer in tokenizers)

    print("📊 SDIF BENCHMARK - Multi-Tokenizer")
    print("Semantic source: examples/golden/<document>/equivalent.json")
    print("Primary ordering and ratio: tiktoken vs JSON Compact\n")
    print(
        f"{'Document':<24} "
        f"{'Format':<12}"
        f"{tokenizer_columns}"
        f" {'Bytes':>8}"
        f" {'vs JSON/tik':>12}"
    )
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
            f" {format_count(row.tokens.get(tokenizer.name)):>9}"
            for tokenizer in tokenizers
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

    print("\n🏁 Wins by tiktoken")
    print("=" * 112)

    wins: dict[str, int] = {}

    for rows in results_by_document.values():
        comparable = [
            row
            for row in rows
            if row.tokens.get("tiktoken") is not None
        ]

        if not comparable:
            continue

        winner = sorted(comparable, key=sort_key)[0]
        wins[winner.name] = wins.get(winner.name, 0) + 1

    for format_name, count in sorted(wins.items(), key=lambda item: (-item[1], item[0])):
        print(f"{format_name:<15} wins: {count}/{documents_count} documents")


def print_footer(results_by_document: dict[str, list[FormatResult]]) -> None:
    print("\n✅ Benchmark completed by deriving all formats from canonical JSON.")

    all_formats = {
        row.name
        for rows in results_by_document.values()
        for row in rows
    }

    if os.environ.get("SDIF_BENCHMARK_TOON") == "0":
        print("ℹ️  TOON skipped: SDIF_BENCHMARK_TOON=0.")
    elif "TOON" not in all_formats:
        print(
            "ℹ️  TOON skipped: neither global `toon` nor `npx @toon-format/cli` "
            "could produce output."
        )

    if os.environ.get("SDIF_BENCHMARK_CLAUDE") != "1":
        print("ℹ️  Claude skipped: set SDIF_BENCHMARK_CLAUDE=1 to enable API token counting.")


# ====================
# Main
# ====================

def main() -> None:
    golden_dir = REPO_ROOT / "examples/golden"
    documents = discover_documents(golden_dir)

    if not documents:
        raise SystemExit("No golden files found under examples/golden/*/equivalent.json")

    tokenizers = available_tokenizers()
    results_by_document: dict[str, list[FormatResult]] = {}

    print_header(tokenizers)

    for document_name in documents:
        source = golden_dir / document_name / "equivalent.json"
        data: dict[str, Any] = json.loads(source.read_text(encoding="utf-8"))

        compact_json = json_compact(data)
        primary_baseline = count_tiktoken(compact_json)

        rows = [
            count_format(
                name=format_name,
                text=text,
                tokenizers=tokenizers,
                primary_baseline=primary_baseline,
            )
            for format_name, text in build_formats(data)
        ]

        rows.sort(key=sort_key)
        results_by_document[document_name] = rows

        print_document_rows(document_name, rows, tokenizers)

    print_summary(
        documents_count=len(documents),
        results_by_document=results_by_document,
        tokenizers=tokenizers,
    )
    print_footer(results_by_document)


if __name__ == "__main__":
    main()
