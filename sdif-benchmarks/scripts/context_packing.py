#!/usr/bin/env python3
"""Context-window packing benchmark.

For a fixed token budget (4K, 8K, 32K, 128K), how many document copies of each
format fit before the context window is exhausted?

Formats compared: JSON Compact, JSON Pretty, YAML, XML, CSV Bundle, SDIF, SDIF AI,
and optionally TOON.

Primary tokenizer: tiktoken (cl100k_base) when available, byte-estimate fallback.

Each run writes persistent evidence to:

- benchmarks/tmp/context_packing  while running
- benchmarks/results/context_packing  on success

Environment variables:

- SDIF_BENCHMARK_OUTPUT_DIR=<path>
    Redirect evidence output. Default: benchmarks/ under the repository root.

- SDIF_BENCHMARK_GOLDEN_DIR=<path>
    Corpus directory. Default: examples/golden under the repository root.

- SDIF_BENCHMARK_TOON=0
    Disable TOON comparison.

- SDIF_BENCHMARK_VERBOSE=1
    Print diagnostic warnings.

- SDIF_TIKTOKEN_ENCODING=<encoding>
    tiktoken encoding. Default: cl100k_base.

- SDIF_ENV_OVERRIDE=0
    Keep existing exported environment variables instead of overriding from .env.
"""

from __future__ import annotations

import contextlib
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

_BENCHMARK_DIR = Path(__file__).resolve().parent.parent
if str(_BENCHMARK_DIR / "src") not in sys.path:
    sys.path.insert(0, str(_BENCHMARK_DIR / "src"))

import infra  # noqa: E402 — sets up REPO_ROOT/src on sys.path
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

BENCHMARK_TRACK_NAME = "context_packing"

CONTEXT_BUDGETS = [4_096, 8_192, 32_768, 131_072]
BUDGET_LABELS = {4_096: "4K", 8_192: "8K", 32_768: "32K", 131_072: "128K"}

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
            encoding_name = os.environ.get("SDIF_TIKTOKEN_ENCODING", "cl100k_base")
            enc = tiktoken.get_encoding(encoding_name)
            return len(enc.encode(text))
        except Exception as exc:
            verbose_warning(f"tiktoken failed, using estimate: {exc}")
    return max(1, (len(text.encode("utf-8")) + 3) // 4)


def tokenizer_name() -> str:
    if tiktoken is not None:
        return f"tiktoken/{os.environ.get('SDIF_TIKTOKEN_ENCODING', 'cl100k_base')}"
    return "estimate (4 bytes/token)"


# ====================
# Data model
# ====================


@dataclass(frozen=True)
class FormatPacking:
    format_name: str
    text: str
    bytes_size: int
    tokens: int
    records_by_budget: dict[int, int]


@dataclass(frozen=True)
class DocumentResult:
    document_name: str
    rows: list[FormatPacking]


@dataclass(frozen=True)
class PackingEvidence:
    generated_at: str
    run_dir: Path
    golden_dir: Path
    documents: list[DocumentResult]
    tokenizer: str
    env_file_loaded: bool


# ====================
# Core benchmark
# ====================


def run_benchmark(run_dir: Path, *, env_file_loaded: bool) -> PackingEvidence:
    golden_dir = benchmark_golden_dir()
    doc_names = discover_documents(golden_dir)
    if not doc_names:
        raise SystemExit("No golden files found under examples/golden/*/equivalent.json")

    tok = tokenizer_name()
    print(f"📦 SDIF CONTEXT PACKING BENCHMARK")
    print(f"Tokenizer: {tok}")
    print(f"Budgets: {', '.join(BUDGET_LABELS[b] for b in CONTEXT_BUDGETS)} tokens\n")

    budget_headers = "".join(f" {BUDGET_LABELS[b]:>8}" for b in CONTEXT_BUDGETS)
    print(f"{'Document':<28} {'Format':<14} {'Tokens':>7}{budget_headers}")
    print("=" * 100)

    all_results: list[DocumentResult] = []

    for doc_name in doc_names:
        source = golden_dir / doc_name / "equivalent.json"
        data: dict[str, Any] = json.loads(source.read_text(encoding="utf-8"))
        format_pairs = fmt.build_formats(data)
        rows: list[FormatPacking] = []
        first = True

        for format_name, text in format_pairs:
            tokens = count_tokens(text)
            records_by_budget = {b: b // max(tokens, 1) for b in CONTEXT_BUDGETS}
            rows.append(
                FormatPacking(
                    format_name=format_name,
                    text=text,
                    bytes_size=len(text.encode("utf-8")),
                    tokens=tokens,
                    records_by_budget=records_by_budget,
                )
            )

        rows.sort(key=lambda r: r.tokens)
        fmt.write_document_corpus(run_dir, doc_name, {r.format_name: r.text for r in rows})

        for row in rows:
            prefix = doc_name if first else ""
            budget_cols = "".join(f" {row.records_by_budget[b]:>8}" for b in CONTEXT_BUDGETS)
            print(f"{prefix:<28} {row.format_name:<14} {row.tokens:>7}{budget_cols}")
            first = False

        print("-" * 100)
        all_results.append(DocumentResult(document_name=doc_name, rows=rows))

    _print_summary(all_results)

    return PackingEvidence(
        generated_at=utc_now_iso(),
        run_dir=benchmark_result_dir(BENCHMARK_TRACK_NAME),
        golden_dir=golden_dir,
        documents=all_results,
        tokenizer=tok,
        env_file_loaded=env_file_loaded,
    )


def _per_format_aggregates(
    results: list[DocumentResult],
) -> list[tuple[str, float, float | None, dict[int, float], dict[int, float], dict[int, float]]]:
    """Return per-format aggregate rows: (name, avg_tokens, ratio_vs_json, fit_rate, avg_docs, median_docs)."""
    format_tokens: dict[str, list[int]] = {}
    format_records: dict[str, dict[int, list[int]]] = {}

    for doc in results:
        for row in doc.rows:
            format_tokens.setdefault(row.format_name, []).append(row.tokens)
            per_budget = format_records.setdefault(row.format_name, {})
            for budget, n in row.records_by_budget.items():
                per_budget.setdefault(budget, []).append(n)

    baseline_avg = _avg(format_tokens.get("JSON Compact", []))

    rows = []
    for format_name, token_list in format_tokens.items():
        avg = _avg(token_list)
        ratio = (avg / baseline_avg * 100) if baseline_avg else None
        per_budget = format_records.get(format_name, {})
        fit_rate = {b: _fit_rate(per_budget.get(b, [])) for b in CONTEXT_BUDGETS}
        avg_docs = {b: _avg(per_budget.get(b, [])) for b in CONTEXT_BUDGETS}
        med_docs = {b: _median(per_budget.get(b, [])) for b in CONTEXT_BUDGETS}
        rows.append((format_name, avg, ratio, fit_rate, avg_docs, med_docs))

    rows.sort(key=lambda x: x[1])
    return rows


def _print_summary(results: list[DocumentResult]) -> None:
    rows = _per_format_aggregates(results)
    n_docs = len(results)

    print(f"\n📈 Fit rate: % of {n_docs} documents that fit at least once per budget")
    print("=" * 90)
    budget_hdrs = "".join(f" {BUDGET_LABELS[b]:>8}" for b in CONTEXT_BUDGETS)
    print(f"{'Format':<14} {'Avg tokens':>12} {'vs JSON':>9}{budget_hdrs}")
    print("-" * 90)

    for format_name, avg, ratio, fit_rate, _avg_docs, _med_docs in rows:
        ratio_str = f"{ratio:.1f}%" if ratio is not None else "-"
        rate_cols = "".join(f" {fit_rate[b]:>7.0f}%" for b in CONTEXT_BUDGETS)
        print(f"{format_name:<14} {avg:>12.1f} {ratio_str:>9}{rate_cols}")

    print()


def _avg(values: Sequence[int | float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _median(values: Sequence[int | float]) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    n = len(s)
    mid = n // 2
    return float(s[mid]) if n % 2 == 1 else (s[mid - 1] + s[mid]) / 2.0


def _fit_rate(counts: Sequence[int]) -> float:
    if not counts:
        return 0.0
    return sum(1 for c in counts if c >= 1) / len(counts) * 100


# ====================
# Reporting
# ====================


def _sdif_key(format_name: str) -> str:
    """Convert a format display name to a valid SDIF identifier."""
    return format_name.replace(" ", "_").replace("-", "_")


def _base_meta(evidence: PackingEvidence) -> dict[str, Any]:
    return {
        "kind": "ContextPackingReport",
        "version": "1.1",
        "generatedAt": evidence.generated_at,
        "tokenizer": evidence.tokenizer,
        "documentCount": len(evidence.documents),
        "budgets": CONTEXT_BUDGETS,
        "budgetLabels": {f"b{k}": v for k, v in BUDGET_LABELS.items()},
    }


def _summary_data(evidence: PackingEvidence) -> dict[str, Any]:
    """Compact summary — used for summary.sdif.ai (LLM-friendly overview)."""
    agg_rows = _per_format_aggregates(evidence.documents)
    per_format_summary = {
        _sdif_key(fmt_name): {
            "avgTokens": round(avg, 1),
            "vsJsonCompactPct": round(ratio, 1) if ratio is not None else None,
            "fitRate": {f"b{b}": round(fit_rate[b], 1) for b in CONTEXT_BUDGETS},
            "avgDocs": {f"b{b}": round(avg_docs[b], 1) for b in CONTEXT_BUDGETS},
            "medianDocs": {f"b{b}": round(med_docs[b], 1) for b in CONTEXT_BUDGETS},
        }
        for fmt_name, avg, ratio, fit_rate, avg_docs, med_docs in agg_rows
    }
    return {**_base_meta(evidence), "perFormatSummary": per_format_summary}


def _detail_data(evidence: PackingEvidence) -> dict[str, Any]:
    """Full detail — used for comparison.sdif.ai (per-document breakdown)."""
    return {
        **_summary_data(evidence),
        "runDirectory": display_path(evidence.run_dir),
        "semanticSource": f"{display_path(evidence.golden_dir)}/<document>/equivalent.json",
        "envFileLoaded": evidence.env_file_loaded,
        "environment": {
            "SDIF_BENCHMARK_GOLDEN_DIR": os.environ.get("SDIF_BENCHMARK_GOLDEN_DIR"),
            "SDIF_BENCHMARK_TOON": os.environ.get("SDIF_BENCHMARK_TOON"),
            "SDIF_TIKTOKEN_ENCODING": os.environ.get("SDIF_TIKTOKEN_ENCODING"),
        },
        "documents": [
            {
                "name": doc.document_name,
                "formats": [
                    {
                        "format": row.format_name,
                        "bytes": row.bytes_size,
                        "tokens": row.tokens,
                        "recordsByBudget": {f"b{k}": v for k, v in row.records_by_budget.items()},
                    }
                    for row in doc.rows
                ],
            }
            for doc in evidence.documents
        ],
    }


def _summary_md(evidence: PackingEvidence) -> str:
    agg_rows = _per_format_aggregates(evidence.documents)
    n_docs = len(evidence.documents)

    lines: list[str] = [
        "# SDIF Context Packing Benchmark — Summary",
        "",
        f"- Generated at: `{evidence.generated_at}`",
        f"- Tokenizer: `{markdown_escape(evidence.tokenizer)}`",
        f"- Documents: `{n_docs}`",
        f"- Budgets: {', '.join(f'`{BUDGET_LABELS[b]}`' for b in CONTEXT_BUDGETS)} tokens",
        "",
        "## Key Finding",
        "",
    ]

    if agg_rows:
        best_name, best_avg, best_ratio, best_fit, _, _ = agg_rows[0]
        json_row = next((r for r in agg_rows if r[0] == "JSON Compact"), None)
        ratio_str = f"{best_ratio:.1f}%" if best_ratio is not None else "-"
        lines.append(
            f"- **{markdown_escape(best_name)}** is the most compact format: "
            f"avg {best_avg:.0f} tokens ({ratio_str} of JSON Compact)."
        )
        if json_row and len(CONTEXT_BUDGETS) > 1:
            b8k = CONTEXT_BUDGETS[1]
            best_fit_8k = best_fit[b8k]
            json_fit_8k = json_row[3][b8k]
            if best_fit_8k > json_fit_8k:
                lines.append(
                    f"- In an 8K context, {markdown_escape(best_name)} fits "
                    f"{best_fit_8k:.0f}% of documents vs {json_fit_8k:.0f}% for JSON Compact."
                )

    budget_hdrs = " | ".join(f"`{BUDGET_LABELS[b]}`" for b in CONTEXT_BUDGETS)
    lines.extend([
        "",
        f"## Fit Rate: % of {n_docs} documents that fit at least once",
        "",
        f"| Format | Avg tokens | vs JSON | {budget_hdrs} |",
        "| --- | ---: | ---: |" + " ---: |" * len(CONTEXT_BUDGETS),
    ])

    for fmt_name, avg, ratio, fit_rate, _avg_d, _med_d in agg_rows:
        ratio_str = f"{ratio:.1f}%" if ratio is not None else "-"
        rate_cols = " | ".join(f"{fit_rate[b]:.0f}%" for b in CONTEXT_BUDGETS)
        lines.append(
            f"| {markdown_escape(fmt_name)} | {avg:.0f} | {ratio_str} | {rate_cols} |"
        )

    lines.extend([
        "",
        "## Avg documents per context budget",
        "",
        f"| Format | {budget_hdrs} |",
        "| --- |" + " ---: |" * len(CONTEXT_BUDGETS),
    ])

    for fmt_name, _avg_t, _ratio, _fit, avg_docs, _med_d in agg_rows:
        avg_cols = " | ".join(f"{avg_docs[b]:.1f}" for b in CONTEXT_BUDGETS)
        lines.append(f"| {markdown_escape(fmt_name)} | {avg_cols} |")

    lines.extend([
        "",
        "## Methodology",
        "",
        "- All formats are derived from the same canonical `equivalent.json` source.",
        f"- **Fit rate**: % of corpus documents where `floor(budget / tokens) >= 1`.",
        "- **Avg docs**: mean number of copies that fit per document across the corpus.",
        f"- Tokenizer: `{markdown_escape(evidence.tokenizer)}`.",
        "- Ratios computed against JSON Compact as the stable baseline.",
        "",
    ])

    return "\n".join(lines)


def _detail_md(evidence: PackingEvidence) -> str:
    lines: list[str] = [
        "# SDIF Context Packing Benchmark — Document Detail",
        "",
        f"- Generated at: `{evidence.generated_at}`",
        f"- Tokenizer: `{markdown_escape(evidence.tokenizer)}`",
        "",
    ]

    budget_hdrs = " | ".join(f"`{BUDGET_LABELS[b]}`" for b in CONTEXT_BUDGETS)

    for doc in evidence.documents:
        lines.extend([
            f"## {markdown_escape(doc.document_name)}",
            "",
            f"| Format | Tokens | Bytes | {budget_hdrs} |",
            "| --- | ---: | ---: |" + " ---: |" * len(CONTEXT_BUDGETS),
        ])
        for row in sorted(doc.rows, key=lambda r: r.tokens):
            rec_cols = " | ".join(str(row.records_by_budget[b]) for b in CONTEXT_BUDGETS)
            lines.append(
                f"| {markdown_escape(row.format_name)} | {row.tokens} | {row.bytes_size} | {rec_cols} |"
            )
        lines.append("")

    return "\n".join(lines)


# ====================
# Main
# ====================


def main() -> None:
    env_file_loaded = load_env_file(REPO_ROOT / ".env")
    run_dir = create_benchmark_run_dir(BENCHMARK_TRACK_NAME)
    log_path = run_dir / "comparison.log"

    with log_path.open("w", encoding="utf-8") as log_file:
        with contextlib.redirect_stdout(Tee(sys.stdout, log_file)):
            evidence = run_benchmark(run_dir, env_file_loaded=env_file_loaded)
            summary_data = _summary_data(evidence)
            detail_data = _detail_data(evidence)
            summary_md = _summary_md(evidence)
            detail_md = _detail_md(evidence)

            summary_sdif = report.render_sdif_report(summary_data)
            detail_sdif = report.render_sdif_report(detail_data)

            (run_dir / "summary.md").write_text(summary_md, encoding="utf-8")
            (run_dir / "summary-viewer.html").write_text(
                report.render_md_viewer(summary_md, "Context Packing — Summary"), encoding="utf-8"
            )
            (run_dir / "summary.json").write_text(report.render_json_report(summary_data), encoding="utf-8")
            (run_dir / "summary.sdif").write_text(summary_sdif, encoding="utf-8")
            _sum_ai = report.render_sdif_ai_report(summary_sdif)
            (run_dir / "summary.sdif.ai").write_text(_sum_ai, encoding="utf-8")
            (run_dir / "summary-sdif-ai-viewer.html").write_text(
                report.render_sdif_ai_viewer(_sum_ai, "Context Packing — SDIF AI"), encoding="utf-8"
            )
            (run_dir / "comparison.md").write_text(detail_md, encoding="utf-8")
            (run_dir / "comparison-viewer.html").write_text(
                report.render_md_viewer(detail_md, "Context Packing — Detail"), encoding="utf-8"
            )
            (run_dir / "comparison.json").write_text(report.render_json_report(detail_data), encoding="utf-8")
            (run_dir / "comparison.sdif").write_text(detail_sdif, encoding="utf-8")
            _det_ai = report.render_sdif_ai_report(detail_sdif)
            (run_dir / "comparison.sdif.ai").write_text(_det_ai, encoding="utf-8")
            (run_dir / "comparison-sdif-ai-viewer.html").write_text(
                report.render_sdif_ai_viewer(_det_ai, "Context Packing — Comparison SDIF AI"), encoding="utf-8"
            )
            (run_dir / DASHBOARD_FILE_NAME).write_text(
                report.render_dashboard_report(detail_data, summary_md, detail_md), encoding="utf-8"
            )

            published = publish_benchmark_result(run_dir, BENCHMARK_TRACK_NAME)
            print(f"\n🧾 Evidence written to {display_path(published)}")
            print(f"  summary.md:      {display_path(published / 'summary.md')}")
            print(f"  summary.json:    {display_path(published / 'summary.json')}")
            print(f"  summary.sdif:    {display_path(published / 'summary.sdif')}")
            print(f"  summary.sdif.ai: {display_path(published / 'summary.sdif.ai')}")
            print(f"  comparison.sdif.ai: {display_path(published / 'comparison.sdif.ai')}")
            print(f"  dashboard:       {display_path(published / DASHBOARD_FILE_NAME)}")
            print(f"  corpus:          {display_path(published / CORPUS_DIR_NAME)}")


if __name__ == "__main__":
    main()
