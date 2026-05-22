#!/usr/bin/env python3
"""Round-trip fidelity benchmark.

Measures semantic preservation when converting JSON → format → JSON.

For each format, the benchmark:
1. Converts the canonical equivalent.json to the format.
2. Parses the format back to a Python dict.
3. Compares the original dict to the round-tripped dict.

Scores (0-100%) per document per format:

- value_fidelity:     % of leaf values that survive as the same value (possibly after type cast).
- type_fidelity:      % of leaf values whose Python type is preserved exactly.
- structure_fidelity: % of key paths that exist in both original and round-tripped.
- overall_fidelity:   harmonic mean of the three above.

SDIF AI and TOON are marked N/A (they are projections or have no standard parser).

Each run writes persistent evidence to:

- benchmarks/tmp/roundtrip_fidelity  while running
- benchmarks/results/roundtrip_fidelity  on success

Environment variables:

- SDIF_BENCHMARK_OUTPUT_DIR=<path>     Redirect evidence. Default: benchmarks/.
- SDIF_BENCHMARK_GOLDEN_DIR=<path>     Corpus directory. Default: examples/golden.
- SDIF_BENCHMARK_TOON=0               Disable TOON (it cannot round-trip anyway).
- SDIF_BENCHMARK_VERBOSE=1            Print diagnostic warnings.
- SDIF_ENV_OVERRIDE=0                 Keep existing env vars instead of .env overrides.
"""

from __future__ import annotations

import contextlib
import json
import os
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any

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

import yaml  # type: ignore[import-untyped]

from sdif.json.converter import document_to_json_data  # noqa: E402
from sdif import parse_text  # noqa: E402
from sdif.core.policy import Policy  # noqa: E402

_BENCHMARK_POLICY = Policy(
    max_document_size=10_000_000,
    max_table_row_count=100_000,
    max_string_length=1_000_000,
)

BENCHMARK_TRACK_NAME = "roundtrip_fidelity"

NA_FORMATS = {"SDIF AI", "TOON"}


# ====================
# Parsers
# ====================


def parse_json_compact(text: str) -> dict[str, Any] | None:
    try:
        return json.loads(text)
    except Exception as exc:
        verbose_warning(f"JSON parse failed: {exc}")
        return None


def parse_yaml(text: str) -> dict[str, Any] | None:
    try:
        result = yaml.safe_load(text)
        return result if isinstance(result, dict) else None
    except Exception as exc:
        verbose_warning(f"YAML parse failed: {exc}")
        return None


def parse_xml(text: str) -> dict[str, Any] | None:
    try:
        root = ET.fromstring(text.split("\n", 1)[1] if text.startswith("<?xml") else text)
        return _xml_element_to_dict(root)
    except Exception as exc:
        verbose_warning(f"XML parse failed: {exc}")
        return None


def _xml_element_to_dict(elem: ET.Element) -> dict[str, Any]:
    children = list(elem)
    if not children:
        return {elem.tag: elem.text or ""}

    result: dict[str, Any] = {}
    child_tags: list[str] = [c.tag for c in children]

    if all(tag == "item" for tag in child_tags):
        items = [_xml_element_to_dict(c).get("item", c.text or "") for c in children]
        return {elem.tag: items}

    for child in children:
        tag = child.tag
        child_children = list(child)
        if not child_children:
            result[tag] = child.text or ""
        elif all(c.tag == "item" for c in child_children):
            result[tag] = [
                _xml_element_to_dict(c).get("item", c.text or "") for c in child_children
            ]
        else:
            result[tag] = _xml_element_to_dict(child).get(tag, {})

    return {elem.tag: result}


def parse_csv_bundle(text: str) -> dict[str, Any] | None:
    import csv
    import io

    try:
        result: dict[str, Any] = {}
        current_section: str | None = None
        current_rows: list[str] = []
        is_fields = False

        def flush_section() -> None:
            nonlocal current_rows, is_fields
            if not current_rows:
                return
            reader = csv.reader(current_rows)
            headers = next(reader, None)
            if headers is None:
                return
            if is_fields:
                for row in reader:
                    if len(row) >= 2:
                        result[row[0]] = _infer_scalar(row[1])
            else:
                rows_list = []
                for row in reader:
                    if headers:
                        rows_list.append(
                            {headers[i]: _infer_scalar(row[i]) for i in range(min(len(headers), len(row)))}
                        )
                if current_section:
                    result[current_section] = rows_list
            current_rows = []

        for line in text.splitlines():
            if line.startswith("# fields"):
                flush_section()
                current_section = None
                is_fields = True
            elif line.startswith("# table:"):
                flush_section()
                current_section = line[len("# table:"):].strip()
                is_fields = False
            else:
                current_rows.append(line)

        flush_section()
        return result
    except Exception as exc:
        verbose_warning(f"CSV bundle parse failed: {exc}")
        return None


def _infer_scalar(value: str) -> Any:
    if value == "null":
        return None
    if value == "true":
        return True
    if value == "false":
        return False
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


def parse_sdif(text: str) -> dict[str, Any] | None:
    try:
        doc = parse_text(text, policy=_BENCHMARK_POLICY)
        return document_to_json_data(doc)
    except Exception as exc:
        verbose_warning(f"SDIF parse failed: {exc}")
        return None


FORMAT_PARSERS = {
    "JSON Compact": parse_json_compact,
    "JSON Pretty": parse_json_compact,
    "YAML": parse_yaml,
    "XML": parse_xml,
    "CSV Bundle": parse_csv_bundle,
    "SDIF": parse_sdif,
}


# ====================
# Fidelity scoring
# ====================


def collect_leaves(obj: Any, path: str = "") -> list[tuple[str, Any]]:
    if isinstance(obj, dict):
        items = []
        for k, v in obj.items():
            items.extend(collect_leaves(v, f"{path}.{k}" if path else k))
        return items
    if isinstance(obj, list):
        items = []
        for i, v in enumerate(obj):
            items.extend(collect_leaves(v, f"{path}[{i}]"))
        return items
    return [(path, obj)]


def score_fidelity(original: dict[str, Any], roundtripped: dict[str, Any]) -> dict[str, float]:
    orig_leaves = dict(collect_leaves(original))
    rt_leaves = dict(collect_leaves(roundtripped))

    all_paths = set(orig_leaves.keys()) | set(rt_leaves.keys())
    if not all_paths:
        return {"value_fidelity": 100.0, "type_fidelity": 100.0, "structure_fidelity": 100.0, "overall_fidelity": 100.0}

    # Structure fidelity: paths in original that exist in round-trip
    orig_paths = set(orig_leaves.keys())
    common_paths = orig_paths & set(rt_leaves.keys())
    structure_fidelity = len(common_paths) / len(orig_paths) * 100 if orig_paths else 100.0

    if not common_paths:
        return {"value_fidelity": 0.0, "type_fidelity": 0.0, "structure_fidelity": structure_fidelity, "overall_fidelity": 0.0}

    value_matches = 0
    type_matches = 0

    for path in common_paths:
        orig_val = orig_leaves[path]
        rt_val = rt_leaves[path]

        # Value: compare via str representation for lossless, allow numeric cast
        if orig_val == rt_val:
            value_matches += 1
        elif orig_val is not None and rt_val is not None:
            if str(orig_val) == str(rt_val):
                value_matches += 1
            else:
                try:
                    if float(str(orig_val)) == float(str(rt_val)):
                        value_matches += 1
                except (ValueError, TypeError):
                    pass

        # Type: exact Python type match
        if type(orig_val) is type(rt_val):
            type_matches += 1

    value_fidelity = value_matches / len(common_paths) * 100
    type_fidelity = type_matches / len(common_paths) * 100

    # Overall: harmonic mean
    scores = [value_fidelity, type_fidelity, structure_fidelity]
    if all(s > 0 for s in scores):
        overall = len(scores) / sum(1 / s for s in scores)
    else:
        overall = 0.0

    return {
        "value_fidelity": round(value_fidelity, 1),
        "type_fidelity": round(type_fidelity, 1),
        "structure_fidelity": round(structure_fidelity, 1),
        "overall_fidelity": round(overall, 1),
    }


# ====================
# Data model
# ====================


@dataclass(frozen=True)
class FidelityResult:
    format_name: str
    text: str
    bytes_size: int
    parse_success: bool
    value_fidelity: float | None
    type_fidelity: float | None
    structure_fidelity: float | None
    overall_fidelity: float | None
    note: str


@dataclass(frozen=True)
class DocumentResult:
    document_name: str
    rows: list[FidelityResult]


@dataclass(frozen=True)
class FidelityEvidence:
    generated_at: str
    run_dir: Path
    golden_dir: Path
    documents: list[DocumentResult]
    env_file_loaded: bool


# ====================
# Core benchmark
# ====================


def run_benchmark(run_dir: Path, *, env_file_loaded: bool) -> FidelityEvidence:
    golden_dir = benchmark_golden_dir()
    doc_names = discover_documents(golden_dir)
    if not doc_names:
        raise SystemExit("No golden files found under examples/golden/*/equivalent.json")

    print("🔄 SDIF ROUND-TRIP FIDELITY BENCHMARK")
    print("Measures: JSON → format → JSON semantic preservation\n")
    print(f"{'Document':<28} {'Format':<14} {'Overall':>9} {'Value':>7} {'Type':>7} {'Struct':>8}  Note")
    print("=" * 100)

    all_results: list[DocumentResult] = []

    for doc_name in doc_names:
        source = golden_dir / doc_name / "equivalent.json"
        original: dict[str, Any] = json.loads(source.read_text(encoding="utf-8"))
        format_pairs = fmt.build_formats(original)
        rows: list[FidelityResult] = []
        first = True

        for format_name, text in format_pairs:
            if format_name in NA_FORMATS:
                result = FidelityResult(
                    format_name=format_name,
                    text=text,
                    bytes_size=len(text.encode("utf-8")),
                    parse_success=False,
                    value_fidelity=None,
                    type_fidelity=None,
                    structure_fidelity=None,
                    overall_fidelity=None,
                    note="N/A (projection/no parser)",
                )
            else:
                parser = FORMAT_PARSERS.get(format_name)
                if parser is None:
                    note = "no parser"
                    result = FidelityResult(
                        format_name=format_name,
                        text=text,
                        bytes_size=len(text.encode("utf-8")),
                        parse_success=False,
                        value_fidelity=None,
                        type_fidelity=None,
                        structure_fidelity=None,
                        overall_fidelity=None,
                        note=note,
                    )
                else:
                    roundtripped = parser(text)
                    if roundtripped is None:
                        result = FidelityResult(
                            format_name=format_name,
                            text=text,
                            bytes_size=len(text.encode("utf-8")),
                            parse_success=False,
                            value_fidelity=None,
                            type_fidelity=None,
                            structure_fidelity=None,
                            overall_fidelity=None,
                            note="parse error",
                        )
                    else:
                        # Unwrap XML top-level wrapper
                        if format_name == "XML" and isinstance(roundtripped, dict):
                            unwrapped = roundtripped.get("document", roundtripped)
                            if isinstance(unwrapped, dict):
                                roundtripped = unwrapped

                        scores = score_fidelity(original, roundtripped)
                        result = FidelityResult(
                            format_name=format_name,
                            text=text,
                            bytes_size=len(text.encode("utf-8")),
                            parse_success=True,
                            value_fidelity=scores["value_fidelity"],
                            type_fidelity=scores["type_fidelity"],
                            structure_fidelity=scores["structure_fidelity"],
                            overall_fidelity=scores["overall_fidelity"],
                            note="",
                        )

            rows.append(result)

        rows.sort(key=lambda r: (-(r.overall_fidelity or -1)))
        fmt.write_document_corpus(run_dir, doc_name, {r.format_name: r.text for r in rows})

        for row in rows:
            prefix = doc_name if first else ""
            overall = f"{row.overall_fidelity:.1f}%" if row.overall_fidelity is not None else "  N/A"
            value = f"{row.value_fidelity:.1f}%" if row.value_fidelity is not None else "  N/A"
            type_ = f"{row.type_fidelity:.1f}%" if row.type_fidelity is not None else "  N/A"
            struct = f"{row.structure_fidelity:.1f}%" if row.structure_fidelity is not None else "  N/A"
            print(
                f"{prefix:<28} {row.format_name:<14} "
                f"{overall:>9} {value:>7} {type_:>7} {struct:>8}  {row.note}"
            )
            first = False

        print("-" * 100)
        all_results.append(DocumentResult(document_name=doc_name, rows=rows))

    _print_summary(all_results)
    return FidelityEvidence(
        generated_at=utc_now_iso(),
        run_dir=benchmark_result_dir(BENCHMARK_TRACK_NAME),
        golden_dir=golden_dir,
        documents=all_results,
        env_file_loaded=env_file_loaded,
    )


def _print_summary(results: list[DocumentResult]) -> None:
    format_scores: dict[str, list[float]] = {}
    for doc in results:
        for row in doc.rows:
            if row.overall_fidelity is not None:
                format_scores.setdefault(row.format_name, []).append(row.overall_fidelity)

    print("\n📈 Average overall fidelity by format")
    print("=" * 60)
    for format_name, scores in sorted(format_scores.items(), key=lambda x: -_avg(x[1])):
        avg = _avg(scores)
        print(f"  {format_name:<14} {avg:>6.1f}%  ({len(scores)} docs)")
    print()


def _avg(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


# ====================
# Reporting
# ====================


def _structured_data(evidence: FidelityEvidence) -> dict[str, Any]:
    return {
        "kind": "RoundTripFidelityReport",
        "version": "1.0",
        "generatedAt": evidence.generated_at,
        "runDirectory": display_path(evidence.run_dir),
        "semanticSource": f"{display_path(evidence.golden_dir)}/<document>/equivalent.json",
        "envFileLoaded": evidence.env_file_loaded,
        "environment": {
            "SDIF_BENCHMARK_GOLDEN_DIR": os.environ.get("SDIF_BENCHMARK_GOLDEN_DIR"),
        },
        "documents": [
            {
                "name": doc.document_name,
                "formats": [
                    {
                        "format": row.format_name,
                        "bytes": row.bytes_size,
                        "parseSuccess": row.parse_success,
                        "valueFidelity": row.value_fidelity,
                        "typeFidelity": row.type_fidelity,
                        "structureFidelity": row.structure_fidelity,
                        "overallFidelity": row.overall_fidelity,
                        "note": row.note,
                    }
                    for row in doc.rows
                ],
            }
            for doc in evidence.documents
        ],
    }


def _fmt_score(v: float | None) -> str:
    return f"{v:.1f}%" if v is not None else "N/A"


def _summary_md(evidence: FidelityEvidence) -> str:
    format_scores: dict[str, list[float]] = {}
    for doc in evidence.documents:
        for row in doc.rows:
            if row.overall_fidelity is not None:
                format_scores.setdefault(row.format_name, []).append(row.overall_fidelity)

    sorted_formats = sorted(format_scores.items(), key=lambda x: -_avg(x[1]))

    lines: list[str] = [
        "# SDIF Round-Trip Fidelity Benchmark — Summary",
        "",
        f"- Generated at: `{evidence.generated_at}`",
        f"- Documents: `{len(evidence.documents)}`",
        "",
        "## Key Findings",
        "",
        "Fidelity measures semantic preservation when converting `JSON → format → JSON`.",
        "100% = lossless. Lower = semantic loss (type coercion, nesting collapse, etc.).",
        "",
        "| Format | Avg Overall | Coverage |",
        "| --- | ---: | ---: |",
    ]

    for format_name, scores in sorted_formats:
        lines.append(
            f"| {markdown_escape(format_name)} | {_avg(scores):.1f}% | {len(scores)}/{len(evidence.documents)} |"
        )

    lines.extend([
        "",
        "## Score Definitions",
        "",
        "| Score | Definition |",
        "| --- | --- |",
        "| **Value fidelity** | % of leaf values that round-trip to the same value (string comparison). |",
        "| **Type fidelity** | % of leaf values whose Python type is preserved exactly. |",
        "| **Structure fidelity** | % of key paths from the original that exist in the round-tripped document. |",
        "| **Overall fidelity** | Harmonic mean of the three scores above. |",
        "",
    ])

    return "\n".join(lines)


def _detail_md(evidence: FidelityEvidence) -> str:
    lines: list[str] = [
        "# SDIF Round-Trip Fidelity Benchmark — Document Detail",
        "",
        f"- Generated at: `{evidence.generated_at}`",
        "",
    ]

    for doc in evidence.documents:
        lines.extend([
            f"## {markdown_escape(doc.document_name)}",
            "",
            "| Format | Overall | Value | Type | Structure | Note |",
            "| --- | ---: | ---: | ---: | ---: | --- |",
        ])
        for row in sorted(doc.rows, key=lambda r: -(r.overall_fidelity or -1)):
            lines.append(
                f"| {markdown_escape(row.format_name)} "
                f"| {_fmt_score(row.overall_fidelity)} "
                f"| {_fmt_score(row.value_fidelity)} "
                f"| {_fmt_score(row.type_fidelity)} "
                f"| {_fmt_score(row.structure_fidelity)} "
                f"| {markdown_escape(row.note)} |"
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
                report.render_md_viewer(summary, "Round-Trip Fidelity — Summary"), encoding="utf-8"
            )
            (run_dir / "summary.json").write_text(report.render_json_report(structured), encoding="utf-8")
            (run_dir / "summary.sdif").write_text(sdif_text, encoding="utf-8")
            (run_dir / "summary.sdif.ai").write_text(report.render_sdif_ai_report(sdif_text), encoding="utf-8")
            (run_dir / "comparison.md").write_text(detail, encoding="utf-8")
            (run_dir / "comparison-viewer.html").write_text(
                report.render_md_viewer(detail, "Round-Trip Fidelity — Detail"), encoding="utf-8"
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
