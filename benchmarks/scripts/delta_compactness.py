#!/usr/bin/env python3
"""Mutation sensitivity benchmark.

Measures how much a deterministic 10% leaf mutation affects each format when
the whole document is re-sent. This is NOT a true delta/patch benchmark — it
measures full-document resend overhead, not incremental encoding.

Two complementary metrics:

1. Token delta: tokens(mutated) - tokens(original) — how many tokens the
   mutation adds to a full-resend payload.

2. Diff lines: added + removed lines in a unified diff — format-level noise
   from the mutation, independent of absolute document size.

Mutation strategy (deterministic):
- Collect all leaf values in sorted key-path order.
- Mutate the first ⌈10%⌉ of leaves:
    - strings: append "-v2"
    - ints/floats: multiply by 1.1, round to 2 decimal places
    - bools: flip
    - null: leave as null (already minimal)

Framing note: a format with low token delta on full-resend is agentic-loop
friendly today. A true SDIF semantic delta (base + patch) would be even smaller,
but that is a separate benchmark (semantic_delta.py, not yet implemented).

All compared formats are derived from the same canonical JSON source.

Each run writes persistent evidence to:

- benchmarks/tmp/delta_compactness  while running
- benchmarks/results/delta_compactness  on success

Environment variables:

- SDIF_BENCHMARK_OUTPUT_DIR=<path>     Redirect evidence. Default: benchmarks/.
- SDIF_BENCHMARK_GOLDEN_DIR=<path>     Corpus directory. Default: examples/golden.
- SDIF_BENCHMARK_TOON=0               Disable TOON.
- SDIF_BENCHMARK_VERBOSE=1            Print diagnostic warnings.
- SDIF_TIKTOKEN_ENCODING=<encoding>   tiktoken encoding. Default: cl100k_base.
- SDIF_ENV_OVERRIDE=0                 Keep existing env vars.
"""

from __future__ import annotations

import contextlib
import difflib
import json
import math
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_BENCHMARK_DIR = Path(__file__).resolve().parent.parent
if str(_BENCHMARK_DIR / "src") not in sys.path:
    sys.path.insert(0, str(_BENCHMARK_DIR / "src"))

import infra  # noqa: E402
import formats as fmt  # noqa: E402
import report  # noqa: E402
from infra import (  # noqa: E402
    CORPUS_DIR_NAME,
    DASHBOARD_FILE_NAME,
    REPO_ROOT,
    Tee,
    benchmark_golden_dir,
    benchmark_result_dir,
    create_benchmark_run_dir,
    discover_documents,
    display_path,
    load_env_file,
    markdown_escape,
    publish_benchmark_result,
    utc_now_iso,
    verbose_warning,
)

BENCHMARK_TRACK_NAME = "delta_compactness"

try:
    import tiktoken  # type: ignore[import-not-found]
except ImportError:
    tiktoken = None  # type: ignore[assignment]


# ====================
# Token counting
# ====================


def count_tokens(text: str) -> int:
    if tiktoken is not None:
        try:
            enc = tiktoken.get_encoding(os.environ.get("SDIF_TIKTOKEN_ENCODING", "cl100k_base"))
            return len(enc.encode(text))
        except Exception as exc:
            verbose_warning(f"tiktoken failed, using estimate: {exc}")
    return max(1, (len(text.encode("utf-8")) + 3) // 4)


def tokenizer_name() -> str:
    if tiktoken is not None:
        return f"tiktoken/{os.environ.get('SDIF_TIKTOKEN_ENCODING', 'cl100k_base')}"
    return "estimate (4 bytes/token)"


# ====================
# Mutation
# ====================


def _collect_leaf_paths(obj: Any, path: str = "") -> list[tuple[str, Any]]:
    if isinstance(obj, dict):
        result = []
        for k in sorted(obj.keys()):
            result.extend(_collect_leaf_paths(obj[k], f"{path}.{k}" if path else k))
        return result
    if isinstance(obj, list):
        result = []
        for i, v in enumerate(obj):
            result.extend(_collect_leaf_paths(v, f"{path}[{i}]"))
        return result
    return [(path, obj)]


def _set_leaf(obj: Any, path_parts: list[str], value: Any) -> None:
    if len(path_parts) == 1:
        key = path_parts[0]
        if isinstance(obj, dict):
            obj[key] = value
        elif isinstance(obj, list):
            idx = int(key.strip("[]"))
            obj[idx] = value
        return
    key = path_parts[0]
    if isinstance(obj, dict):
        _set_leaf(obj[key], path_parts[1:], value)
    elif isinstance(obj, list):
        idx = int(key.strip("[]"))
        _set_leaf(obj[idx], path_parts[1:], value)


def _mutate_value(value: Any) -> Any:
    if isinstance(value, str):
        return value + "-v2"
    if isinstance(value, bool):
        return not value
    if isinstance(value, int):
        return round(value * 1.1, 2)
    if isinstance(value, float):
        return round(value * 1.1, 2)
    return value


def mutate(data: dict[str, Any], mutation_fraction: float = 0.10) -> dict[str, Any]:
    import copy

    mutated = copy.deepcopy(data)
    leaves = _collect_leaf_paths(mutated)
    n = max(1, math.ceil(len(leaves) * mutation_fraction))

    for path, value in leaves[:n]:
        parts = _split_path(path)
        _set_leaf(mutated, parts, _mutate_value(value))

    return mutated


def _split_path(path: str) -> list[str]:
    import re

    return re.split(r"\.|(?=\[)", path)


# ====================
# Data model
# ====================


@dataclass(frozen=True)
class DeltaResult:
    format_name: str
    original_text: str
    mutated_text: str
    original_tokens: int
    mutated_tokens: int
    token_delta: int
    token_delta_pct: float
    diff_lines_added: int
    diff_lines_removed: int
    diff_lines_changed: int


@dataclass(frozen=True)
class DocumentResult:
    document_name: str
    rows: list[DeltaResult]
    leaves_total: int
    leaves_mutated: int


@dataclass(frozen=True)
class DeltaEvidence:
    generated_at: str
    run_dir: Path
    golden_dir: Path
    documents: list[DocumentResult]
    tokenizer: str
    mutation_fraction: float
    env_file_loaded: bool


# ====================
# Core benchmark
# ====================


def run_benchmark(run_dir: Path, *, env_file_loaded: bool) -> DeltaEvidence:
    golden_dir = benchmark_golden_dir()
    doc_names = discover_documents(golden_dir)
    if not doc_names:
        raise SystemExit("No golden files found under examples/golden/*/equivalent.json")

    fraction = 0.10
    tok = tokenizer_name()

    print("📊 SDIF DELTA COMPACTNESS BENCHMARK")
    print(f"Tokenizer: {tok}")
    print(f"Mutation: {fraction*100:.0f}% of leaf values changed\n")
    print(
        f"{'Document':<28} {'Format':<14} {'Orig tokens':>12} {'Δ tokens':>10} "
        f"{'Δ%':>7} {'Diff+':>7} {'Diff-':>7}"
    )
    print("=" * 100)

    all_results: list[DocumentResult] = []

    for doc_name in doc_names:
        source = golden_dir / doc_name / "equivalent.json"
        original: dict[str, Any] = json.loads(source.read_text(encoding="utf-8"))
        mutated = mutate(original, fraction)

        leaves = _collect_leaf_paths(original)
        leaves_mutated = max(1, math.ceil(len(leaves) * fraction))

        original_formats = dict(fmt.build_formats(original))
        mutated_formats = dict(fmt.build_formats(mutated))

        rows: list[DeltaResult] = []
        first = True

        for format_name in original_formats:
            orig_text = original_formats[format_name]
            mut_text = mutated_formats.get(format_name, orig_text)

            orig_tokens = count_tokens(orig_text)
            mut_tokens = count_tokens(mut_text)
            token_delta = mut_tokens - orig_tokens
            token_delta_pct = (token_delta / orig_tokens * 100) if orig_tokens > 0 else 0.0

            orig_lines = orig_text.splitlines(keepends=True)
            mut_lines = mut_text.splitlines(keepends=True)
            diff = list(difflib.unified_diff(orig_lines, mut_lines, lineterm=""))
            added = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
            removed = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))
            changed = added + removed

            rows.append(
                DeltaResult(
                    format_name=format_name,
                    original_text=orig_text,
                    mutated_text=mut_text,
                    original_tokens=orig_tokens,
                    mutated_tokens=mut_tokens,
                    token_delta=token_delta,
                    token_delta_pct=token_delta_pct,
                    diff_lines_added=added,
                    diff_lines_removed=removed,
                    diff_lines_changed=changed,
                )
            )

        rows.sort(key=lambda r: abs(r.token_delta))

        # Corpus: save both original and mutated
        fmt.write_document_corpus(run_dir, doc_name, {r.format_name: r.original_text for r in rows})
        mutated_corpus_dir = run_dir / CORPUS_DIR_NAME / f"{doc_name}_mutated"
        mutated_corpus_dir.mkdir(parents=True, exist_ok=True)
        for row in rows:
            file_name = fmt.FORMAT_FILE_NAMES.get(row.format_name)
            if file_name:
                (mutated_corpus_dir / file_name).write_text(row.mutated_text, encoding="utf-8")

        for row in rows:
            prefix = doc_name if first else ""
            sign = "+" if row.token_delta >= 0 else ""
            print(
                f"{prefix:<28} {row.format_name:<14} "
                f"{row.original_tokens:>12} "
                f"{sign}{row.token_delta:>9} "
                f"{sign}{row.token_delta_pct:>6.1f}% "
                f"{row.diff_lines_added:>7} "
                f"{row.diff_lines_removed:>7}"
            )
            first = False

        print("-" * 100)
        all_results.append(
            DocumentResult(
                document_name=doc_name,
                rows=rows,
                leaves_total=len(leaves),
                leaves_mutated=leaves_mutated,
            )
        )

    _print_summary(all_results)

    return DeltaEvidence(
        generated_at=utc_now_iso(),
        run_dir=benchmark_result_dir(BENCHMARK_TRACK_NAME),
        golden_dir=golden_dir,
        documents=all_results,
        tokenizer=tok,
        mutation_fraction=fraction,
        env_file_loaded=env_file_loaded,
    )


def _print_summary(results: list[DocumentResult]) -> None:
    format_deltas: dict[str, list[float]] = {}
    format_diff_lines: dict[str, list[int]] = {}
    for doc in results:
        for row in doc.rows:
            format_deltas.setdefault(row.format_name, []).append(row.token_delta_pct)
            format_diff_lines.setdefault(row.format_name, []).append(row.diff_lines_changed)

    print("\n📈 Mutation sensitivity: full-resend token delta and diff lines per format")
    print("   (measures full-document resend overhead, not true delta encoding)")
    print("=" * 70)
    print(f"{'Format':<14} {'Avg Δ tokens%':>15} {'Avg diff lines':>16}")
    print("-" * 70)

    rows = []
    for format_name, deltas in format_deltas.items():
        avg_delta = sum(deltas) / len(deltas)
        avg_diff = sum(format_diff_lines.get(format_name, [0])) / max(
            len(format_diff_lines.get(format_name, [1])), 1
        )
        rows.append((format_name, avg_delta, avg_diff))

    rows.sort(key=lambda x: abs(x[1]))

    for format_name, avg_delta, avg_diff in rows:
        sign = "+" if avg_delta >= 0 else ""
        print(f"{format_name:<14} {sign}{avg_delta:>14.1f}% {avg_diff:>16.1f}")
    print()


def _avg(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


# ====================
# Reporting
# ====================


def _structured_data(evidence: DeltaEvidence) -> dict[str, Any]:
    return {
        "kind": "MutationSensitivityReport",
        "version": "1.0",
        "note": "Full-resend overhead benchmark. Not a true SDIF delta encoding benchmark.",
        "generatedAt": evidence.generated_at,
        "runDirectory": display_path(evidence.run_dir),
        "semanticSource": f"{display_path(evidence.golden_dir)}/<document>/equivalent.json",
        "tokenizer": evidence.tokenizer,
        "mutationFraction": evidence.mutation_fraction,
        "envFileLoaded": evidence.env_file_loaded,
        "environment": {
            "SDIF_BENCHMARK_GOLDEN_DIR": os.environ.get("SDIF_BENCHMARK_GOLDEN_DIR"),
            "SDIF_BENCHMARK_TOON": os.environ.get("SDIF_BENCHMARK_TOON"),
            "SDIF_TIKTOKEN_ENCODING": os.environ.get("SDIF_TIKTOKEN_ENCODING"),
        },
        "documents": [
            {
                "name": doc.document_name,
                "leavesTotal": doc.leaves_total,
                "leavesMutated": doc.leaves_mutated,
                "formats": [
                    {
                        "format": row.format_name,
                        "originalTokens": row.original_tokens,
                        "mutatedTokens": row.mutated_tokens,
                        "tokenDelta": row.token_delta,
                        "tokenDeltaPct": row.token_delta_pct,
                        "diffLinesAdded": row.diff_lines_added,
                        "diffLinesRemoved": row.diff_lines_removed,
                        "diffLinesChanged": row.diff_lines_changed,
                    }
                    for row in doc.rows
                ],
            }
            for doc in evidence.documents
        ],
    }


def _summary_md(evidence: DeltaEvidence) -> str:
    format_deltas: dict[str, list[float]] = {}
    format_diff_lines: dict[str, list[int]] = {}
    for doc in evidence.documents:
        for row in doc.rows:
            format_deltas.setdefault(row.format_name, []).append(row.token_delta_pct)
            format_diff_lines.setdefault(row.format_name, []).append(row.diff_lines_changed)

    rows = []
    for format_name, deltas in format_deltas.items():
        avg_delta = _avg(deltas)
        avg_diff = _avg([float(v) for v in format_diff_lines.get(format_name, [0])])
        rows.append((format_name, avg_delta, avg_diff))
    rows.sort(key=lambda x: abs(x[1]))

    lines: list[str] = [
        "# SDIF Mutation Sensitivity Benchmark — Summary",
        "",
        "> **Framing**: this benchmark measures full-document resend overhead after a 10% leaf mutation.",
        "> It is NOT a true SDIF delta benchmark. A semantic delta (base + patch) would be even smaller.",
        "",
        f"- Generated at: `{evidence.generated_at}`",
        f"- Tokenizer: `{markdown_escape(evidence.tokenizer)}`",
        f"- Mutation: `{evidence.mutation_fraction*100:.0f}%` of leaf values changed",
        f"- Documents: `{len(evidence.documents)}`",
        "",
        "## Key Findings",
        "",
        "A 10% leaf mutation simulates a typical incremental document update.",
        "Formats with smaller token delta and fewer diff lines produce less noise on full-resend.",
        "",
        "| Format | Avg Δ tokens % | Avg diff lines |",
        "| --- | ---: | ---: |",
    ]

    for format_name, avg_delta, avg_diff in rows:
        sign = "+" if avg_delta >= 0 else ""
        lines.append(
            f"| {markdown_escape(format_name)} | {sign}{avg_delta:.1f}% | {avg_diff:.1f} |"
        )

    lines.extend([
        "",
        "## Methodology",
        "",
        f"- Mutation: first `{evidence.mutation_fraction*100:.0f}%` of leaves (sorted by key path) are changed.",
        "  - Strings: append `-v2`.",
        "  - Numbers: multiply by `1.1`.",
        "  - Booleans: flip.",
        "- **Token delta**: `tokens(mutated) - tokens(original)` — full-document resend model.",
        "- **Diff lines**: unified diff added + removed lines — format-level verbosity in patches.",
        "- This benchmark does **not** measure SDIF semantic delta encoding (`kind Delta`), which",
        "  would transmit only changed fields as a patch. That is a separate benchmark.",
        "",
    ])

    return "\n".join(lines)


def _detail_md(evidence: DeltaEvidence) -> str:
    lines: list[str] = [
        "# SDIF Mutation Sensitivity Benchmark — Document Detail",
        "",
        f"- Generated at: `{evidence.generated_at}`",
        f"- Mutation: `{evidence.mutation_fraction*100:.0f}%` of leaf values changed",
        "",
    ]

    for doc in evidence.documents:
        lines.extend([
            f"## {markdown_escape(doc.document_name)}",
            "",
            f"Leaves total: `{doc.leaves_total}`, mutated: `{doc.leaves_mutated}`",
            "",
            "| Format | Orig tokens | Mutated tokens | Δ tokens | Δ% | Diff lines |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ])
        for row in sorted(doc.rows, key=lambda r: abs(r.token_delta)):
            sign = "+" if row.token_delta >= 0 else ""
            lines.append(
                f"| {markdown_escape(row.format_name)} "
                f"| {row.original_tokens} "
                f"| {row.mutated_tokens} "
                f"| {sign}{row.token_delta} "
                f"| {sign}{row.token_delta_pct:.1f}% "
                f"| {row.diff_lines_changed} |"
            )
        lines.append("")

    return "\n".join(lines)


# ====================
# Main
# ====================


def main() -> None:
    env_file_loaded = load_env_file(REPO_ROOT / ".env")
    run_dir = create_benchmark_run_dir(BENCHMARK_TRACK_NAME)
    final_dir = benchmark_result_dir(BENCHMARK_TRACK_NAME)
    log_path = run_dir / "comparison.log"

    with log_path.open("w", encoding="utf-8") as log_file:
        with contextlib.redirect_stdout(Tee(sys.stdout, log_file)):
            evidence = run_benchmark(run_dir, env_file_loaded=env_file_loaded)
            structured = _structured_data(evidence)
            summary = _summary_md(evidence)
            detail = _detail_md(evidence)
            sdif_text = report.render_sdif_report(structured)

            (run_dir / "summary.md").write_text(summary, encoding="utf-8")
            (run_dir / "summary-viewer.html").write_text(
                report.render_md_viewer(summary, "Delta Compactness — Summary"), encoding="utf-8"
            )
            (run_dir / "summary.json").write_text(report.render_json_report(structured), encoding="utf-8")
            (run_dir / "summary.sdif").write_text(sdif_text, encoding="utf-8")
            (run_dir / "summary.sdif.ai").write_text(report.render_sdif_ai_report(sdif_text), encoding="utf-8")
            (run_dir / "comparison.md").write_text(detail, encoding="utf-8")
            (run_dir / "comparison-viewer.html").write_text(
                report.render_md_viewer(detail, "Delta Compactness — Detail"), encoding="utf-8"
            )
            (run_dir / DASHBOARD_FILE_NAME).write_text(
                report.render_dashboard_report(structured, summary, detail), encoding="utf-8"
            )

            published = publish_benchmark_result(run_dir, BENCHMARK_TRACK_NAME)
            print(f"\n🧾 Evidence written to {display_path(published)}")
            print(f"  summary.md:   {display_path(published / 'summary.md')}")
            print(f"  summary.json: {display_path(published / 'summary.json')}")
            print(f"  summary.sdif: {display_path(published / 'summary.sdif')}")
            print(f"  dashboard:    {display_path(published / DASHBOARD_FILE_NAME)}")
            print(f"  corpus:       {display_path(published / CORPUS_DIR_NAME)}")


if __name__ == "__main__":
    main()
