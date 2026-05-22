#!/usr/bin/env python3
"""Retrieval accuracy benchmark.

Measures whether format affects LLM answer quality on structured data questions.

For each document, deterministic questions are generated from the JSON structure:

1. Scalar lookup:   "What is the value of <field>?"
2. Count:           "How many <array_field> are there?"
3. Max/min value:   "What is the maximum <numeric_field> across all <array_field>?"
4. Filtered count:  "How many <array_field> have <field> equal to <value>?"

Each question is posed to Claude with the document rendered in each format.
Answers are validated deterministically against ground truth computed from the
original JSON — no LLM judge.

Opt-in: requires SDIF_BENCHMARK_RETRIEVAL=1 and ANTHROPIC_API_KEY.

Without these, the script prints instructions and exits with a non-zero status.

Each run writes persistent evidence to:

- benchmarks/tmp/retrieval_accuracy  while running
- benchmarks/results/retrieval_accuracy  on success

Environment variables:

- SDIF_BENCHMARK_RETRIEVAL=1
    Required. Enable this benchmark. Requires ANTHROPIC_API_KEY.

- ANTHROPIC_API_KEY=<key>
    Required when SDIF_BENCHMARK_RETRIEVAL=1.

- SDIF_CLAUDE_MODEL=<model-id>
    Claude model for retrieval queries.
    Default: claude-haiku-4-5-20251001

- SDIF_BENCHMARK_OUTPUT_DIR=<path>
    Redirect evidence output. Default: benchmarks/.

- SDIF_BENCHMARK_GOLDEN_DIR=<path>
    Corpus directory. Default: examples/golden.

- SDIF_BENCHMARK_TOON=0
    Disable TOON.

- SDIF_BENCHMARK_VERBOSE=1
    Print diagnostic warnings.

- SDIF_RETRIEVAL_MAX_QUESTIONS=<n>
    Max questions per document. Default: 8.

- SDIF_ENV_OVERRIDE=0
    Keep existing env vars instead of .env overrides.
"""

from __future__ import annotations

import contextlib
import json
import os
import sys
from dataclasses import dataclass, field
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

BENCHMARK_TRACK_NAME = "retrieval_accuracy"
DEFAULT_MODEL = "claude-haiku-4-5-20251001"
DEFAULT_MAX_QUESTIONS = 8

try:
    from anthropic import Anthropic  # type: ignore[import-not-found]
except ImportError:
    Anthropic = None  # type: ignore[assignment,misc]


# ====================
# Question generation
# ====================


@dataclass(frozen=True)
class Question:
    question_id: str
    question_type: str
    text: str
    ground_truth: str
    hint: str


def generate_questions(data: dict[str, Any], max_questions: int = DEFAULT_MAX_QUESTIONS) -> list[Question]:
    questions: list[Question] = []

    # Scalar lookups
    for key, value in data.items():
        if isinstance(value, str | int | float | bool) and value is not None:
            questions.append(
                Question(
                    question_id=f"lookup_{key}",
                    question_type="scalar_lookup",
                    text=f'What is the value of "{key}"?',
                    ground_truth=str(value),
                    hint=f"Look for the field named '{key}'.",
                )
            )
        if len(questions) >= max_questions // 3:
            break

    # Array counts and numeric aggregation
    for key, value in data.items():
        if isinstance(value, list) and value:
            questions.append(
                Question(
                    question_id=f"count_{key}",
                    question_type="count",
                    text=f'How many "{key}" entries are there?',
                    ground_truth=str(len(value)),
                    hint=f"Count the number of items in the '{key}' list.",
                )
            )

            if isinstance(value[0], dict):
                # Find a numeric field for max/min
                for field_key in list(value[0].keys())[:5]:
                    vals = [
                        item[field_key]
                        for item in value
                        if isinstance(item, dict) and isinstance(item.get(field_key), int | float)
                    ]
                    if len(vals) >= 2:
                        max_val = max(vals)
                        questions.append(
                            Question(
                                question_id=f"max_{key}_{field_key}",
                                question_type="aggregation",
                                text=f'What is the maximum "{field_key}" value across all "{key}" entries?',
                                ground_truth=str(max_val),
                                hint=f"Find the largest value of '{field_key}' in the '{key}' list.",
                            )
                        )
                        break

                # Filtered count: find a categorical field with a specific value
                for field_key in list(value[0].keys())[:5]:
                    cat_vals = [
                        item[field_key]
                        for item in value
                        if isinstance(item, dict) and isinstance(item.get(field_key), str)
                    ]
                    if cat_vals:
                        target = cat_vals[0]
                        count = sum(1 for v in cat_vals if v == target)
                        questions.append(
                            Question(
                                question_id=f"filter_{key}_{field_key}",
                                question_type="filtered_count",
                                text=f'How many "{key}" entries have "{field_key}" equal to "{target}"?',
                                ground_truth=str(count),
                                hint=f"Count items in '{key}' where '{field_key}' is '{target}'.",
                            )
                        )
                        break

        if len(questions) >= max_questions:
            break

    return questions[:max_questions]


# ====================
# LLM querying
# ====================


SYSTEM_PROMPT = (
    "You are a precise data extraction assistant. Answer questions about structured data documents. "
    "Respond with ONLY the answer — no explanation, no units, no extra words. "
    "For numbers: give the numeric value only (e.g., '42' not '42 items'). "
    "For strings: give the exact string value. "
    "If the answer cannot be determined from the document, respond with 'unknown'."
)


def query_claude(
    client: Any,
    model: str,
    document_text: str,
    format_name: str,
    question: Question,
) -> str | None:
    try:
        response = client.messages.create(
            model=model,
            max_tokens=64,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Document ({format_name} format):\n\n"
                        f"```\n{document_text[:8000]}\n```\n\n"
                        f"Question: {question.text}\n"
                        f"Hint: {question.hint}"
                    ),
                }
            ],
        )
        return response.content[0].text.strip() if response.content else None
    except Exception as exc:
        verbose_warning(f"Claude API error for {format_name}/{question.question_id}: {exc}")
        return None


def normalize_answer(answer: str) -> str:
    a = answer.strip().lower()
    try:
        return str(float(a))
    except ValueError:
        pass
    return a


def answers_match(predicted: str | None, ground_truth: str) -> bool:
    if predicted is None:
        return False
    return normalize_answer(predicted) == normalize_answer(ground_truth)


# ====================
# Data model
# ====================


@dataclass(frozen=True)
class QuestionResult:
    question_id: str
    question_type: str
    question_text: str
    ground_truth: str
    predicted: str | None
    correct: bool


@dataclass(frozen=True)
class FormatResult:
    format_name: str
    text: str
    bytes_size: int
    question_results: list[QuestionResult]
    accuracy: float


@dataclass(frozen=True)
class DocumentResult:
    document_name: str
    questions: list[Question]
    format_results: list[FormatResult]


@dataclass(frozen=True)
class RetrievalEvidence:
    generated_at: str
    run_dir: Path
    golden_dir: Path
    model: str
    documents: list[DocumentResult]
    env_file_loaded: bool


# ====================
# Core benchmark
# ====================


def run_benchmark(
    run_dir: Path, *, env_file_loaded: bool, client: Any, model: str
) -> RetrievalEvidence:
    golden_dir = benchmark_golden_dir()
    doc_names = discover_documents(golden_dir)
    if not doc_names:
        raise SystemExit("No golden files found under examples/golden/*/equivalent.json")

    max_q = int(os.environ.get("SDIF_RETRIEVAL_MAX_QUESTIONS", DEFAULT_MAX_QUESTIONS))

    print(f"🔍 SDIF RETRIEVAL ACCURACY BENCHMARK")
    print(f"Model: {model}")
    print(f"Max questions per document: {max_q}\n")

    all_results: list[DocumentResult] = []

    for doc_name in doc_names:
        source = golden_dir / doc_name / "equivalent.json"
        data: dict[str, Any] = json.loads(source.read_text(encoding="utf-8"))
        questions = generate_questions(data, max_q)

        if not questions:
            verbose_warning(f"No questions generated for {doc_name}, skipping.")
            continue

        print(f"\n📄 {doc_name} ({len(questions)} questions)")
        print(f"{'Format':<14} {'Accuracy':>10}  Results")
        print("-" * 70)

        format_pairs = dict(fmt.build_formats(data))
        fmt.write_document_corpus(run_dir, doc_name, format_pairs)

        format_results: list[FormatResult] = []

        for format_name, text in format_pairs.items():
            q_results: list[QuestionResult] = []

            for q in questions:
                predicted = query_claude(client, model, text, format_name, q)
                correct = answers_match(predicted, q.ground_truth)
                q_results.append(
                    QuestionResult(
                        question_id=q.question_id,
                        question_type=q.question_type,
                        question_text=q.text,
                        ground_truth=q.ground_truth,
                        predicted=predicted,
                        correct=correct,
                    )
                )

            correct_count = sum(1 for r in q_results if r.correct)
            accuracy = correct_count / len(q_results) * 100 if q_results else 0.0

            format_results.append(
                FormatResult(
                    format_name=format_name,
                    text=text,
                    bytes_size=len(text.encode("utf-8")),
                    question_results=q_results,
                    accuracy=accuracy,
                )
            )

            result_icons = "".join("✓" if r.correct else "✗" for r in q_results)
            print(f"{format_name:<14} {accuracy:>9.1f}%  {result_icons}")

        all_results.append(
            DocumentResult(
                document_name=doc_name,
                questions=questions,
                format_results=sorted(format_results, key=lambda r: -r.accuracy),
            )
        )

    _print_summary(all_results)

    return RetrievalEvidence(
        generated_at=utc_now_iso(),
        run_dir=benchmark_result_dir(BENCHMARK_TRACK_NAME),
        golden_dir=golden_dir,
        model=model,
        documents=all_results,
        env_file_loaded=env_file_loaded,
    )


def _print_summary(results: list[DocumentResult]) -> None:
    format_accuracies: dict[str, list[float]] = {}
    for doc in results:
        for fr in doc.format_results:
            format_accuracies.setdefault(fr.format_name, []).append(fr.accuracy)

    print("\n📈 Average retrieval accuracy by format")
    print("=" * 50)
    for format_name, accs in sorted(format_accuracies.items(), key=lambda x: -_avg(x[1])):
        print(f"  {format_name:<14} {_avg(accs):>6.1f}%  ({len(accs)} docs)")
    print()


def _avg(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


# ====================
# Reporting
# ====================


def _structured_data(evidence: RetrievalEvidence) -> dict[str, Any]:
    return {
        "kind": "RetrievalAccuracyReport",
        "version": "1.0",
        "generatedAt": evidence.generated_at,
        "runDirectory": display_path(evidence.run_dir),
        "semanticSource": f"{display_path(evidence.golden_dir)}/<document>/equivalent.json",
        "model": evidence.model,
        "envFileLoaded": evidence.env_file_loaded,
        "environment": {
            "SDIF_BENCHMARK_GOLDEN_DIR": os.environ.get("SDIF_BENCHMARK_GOLDEN_DIR"),
            "SDIF_CLAUDE_MODEL": os.environ.get("SDIF_CLAUDE_MODEL"),
            "SDIF_RETRIEVAL_MAX_QUESTIONS": os.environ.get("SDIF_RETRIEVAL_MAX_QUESTIONS"),
            "ANTHROPIC_API_KEY": "set" if os.environ.get("ANTHROPIC_API_KEY") else "unset",
        },
        "documents": [
            {
                "name": doc.document_name,
                "questions": [
                    {
                        "id": q.question_id,
                        "type": q.question_type,
                        "text": q.text,
                        "groundTruth": q.ground_truth,
                    }
                    for q in doc.questions
                ],
                "formats": [
                    {
                        "format": fr.format_name,
                        "bytes": fr.bytes_size,
                        "accuracy": fr.accuracy,
                        "results": [
                            {
                                "questionId": r.question_id,
                                "correct": r.correct,
                                "groundTruth": r.ground_truth,
                                "predicted": r.predicted,
                            }
                            for r in fr.question_results
                        ],
                    }
                    for fr in doc.format_results
                ],
            }
            for doc in evidence.documents
        ],
    }


def _summary_md(evidence: RetrievalEvidence) -> str:
    format_accuracies: dict[str, list[float]] = {}
    format_by_type: dict[str, dict[str, list[bool]]] = {}

    for doc in evidence.documents:
        for fr in doc.format_results:
            format_accuracies.setdefault(fr.format_name, []).append(fr.accuracy)
            for r in fr.question_results:
                format_by_type.setdefault(fr.format_name, {}).setdefault(
                    r.question_type, []
                ).append(r.correct)

    sorted_formats = sorted(format_accuracies.items(), key=lambda x: -_avg(x[1]))

    q_types = sorted({
        r.question_type
        for doc in evidence.documents
        for fr in doc.format_results
        for r in fr.question_results
    })

    lines: list[str] = [
        "# SDIF Retrieval Accuracy Benchmark — Summary",
        "",
        f"- Generated at: `{evidence.generated_at}`",
        f"- Model: `{markdown_escape(evidence.model)}`",
        f"- Documents: `{len(evidence.documents)}`",
        "",
        "## Key Findings",
        "",
        "Higher accuracy = the format helps the LLM answer structured data questions correctly.",
        "",
        "| Format | Avg Accuracy | " + " | ".join(markdown_escape(t) for t in q_types) + " |",
        "| --- | ---: |" + " ---: |" * len(q_types),
    ]

    for format_name, accs in sorted_formats:
        type_cols = []
        for qt in q_types:
            type_results = format_by_type.get(format_name, {}).get(qt, [])
            if type_results:
                acc = sum(type_results) / len(type_results) * 100
                type_cols.append(f"{acc:.0f}%")
            else:
                type_cols.append("-")
        lines.append(
            f"| {markdown_escape(format_name)} | {_avg(accs):.1f}% | " + " | ".join(type_cols) + " |"
        )

    lines.extend([
        "",
        "## Methodology",
        "",
        "- Questions are generated deterministically from the document structure (no hand-crafting).",
        "- Ground truth is computed from the original JSON — no LLM judge.",
        f"- Model: `{markdown_escape(evidence.model)}`.",
        "- Question types: scalar_lookup, count, aggregation, filtered_count.",
        "",
    ])

    return "\n".join(lines)


def _detail_md(evidence: RetrievalEvidence) -> str:
    lines: list[str] = [
        "# SDIF Retrieval Accuracy Benchmark — Document Detail",
        "",
        f"- Generated at: `{evidence.generated_at}`",
        f"- Model: `{markdown_escape(evidence.model)}`",
        "",
    ]

    for doc in evidence.documents:
        lines.extend([
            f"## {markdown_escape(doc.document_name)}",
            "",
            "### Questions",
            "",
            "| # | Type | Question | Ground Truth |",
            "| --- | --- | --- | --- |",
        ])
        for i, q in enumerate(doc.questions, 1):
            lines.append(
                f"| {i} | {markdown_escape(q.question_type)} "
                f"| {markdown_escape(q.text)} "
                f"| `{markdown_escape(q.ground_truth)}` |"
            )

        lines.extend([
            "",
            "### Results by Format",
            "",
            "| Format | Accuracy | " + " | ".join(f"Q{i}" for i in range(1, len(doc.questions) + 1)) + " |",
            "| --- | ---: |" + " :---: |" * len(doc.questions),
        ])
        for fr in doc.format_results:
            q_cells = " | ".join("✓" if r.correct else "✗" for r in fr.question_results)
            lines.append(
                f"| {markdown_escape(fr.format_name)} | {fr.accuracy:.1f}% | {q_cells} |"
            )
        lines.append("")

    return "\n".join(lines)


# ====================
# Main
# ====================


def _print_usage_and_exit() -> None:
    print("⚠️  Retrieval accuracy benchmark requires opt-in.")
    print()
    print("Set the following environment variables:")
    print("  SDIF_BENCHMARK_RETRIEVAL=1   — enable the benchmark")
    print("  ANTHROPIC_API_KEY=<key>      — Anthropic API key")
    print()
    print("Optional:")
    print(f"  SDIF_CLAUDE_MODEL=<model>    — model to use (default: {DEFAULT_MODEL})")
    print(f"  SDIF_RETRIEVAL_MAX_QUESTIONS=<n> — questions per document (default: {DEFAULT_MAX_QUESTIONS})")
    sys.exit(1)


def main() -> None:
    env_file_loaded = load_env_file(REPO_ROOT / ".env")

    if os.environ.get("SDIF_BENCHMARK_RETRIEVAL") != "1":
        _print_usage_and_exit()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY is not set.")
        _print_usage_and_exit()

    if Anthropic is None:
        print("❌ The 'anthropic' Python package is not installed.")
        print("   Run: uv pip install anthropic")
        sys.exit(1)

    model = os.environ.get("SDIF_CLAUDE_MODEL", DEFAULT_MODEL)
    client = Anthropic()

    run_dir = create_benchmark_run_dir(BENCHMARK_TRACK_NAME)
    final_dir = benchmark_result_dir(BENCHMARK_TRACK_NAME)
    log_path = run_dir / "comparison.log"

    with log_path.open("w", encoding="utf-8") as log_file:
        with contextlib.redirect_stdout(Tee(sys.stdout, log_file)):
            evidence = run_benchmark(
                run_dir, env_file_loaded=env_file_loaded, client=client, model=model
            )
            structured = _structured_data(evidence)
            summary = _summary_md(evidence)
            detail = _detail_md(evidence)
            sdif_text = report.render_sdif_report(structured)

            (run_dir / "summary.md").write_text(summary, encoding="utf-8")
            (run_dir / "summary.json").write_text(report.render_json_report(structured), encoding="utf-8")
            (run_dir / "summary.sdif").write_text(sdif_text, encoding="utf-8")
            (run_dir / "summary.sdif.ai").write_text(report.render_sdif_ai_report(sdif_text), encoding="utf-8")
            (run_dir / "comparison.md").write_text(detail, encoding="utf-8")
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
