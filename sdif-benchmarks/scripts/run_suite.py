#!/usr/bin/env python3
"""SDIF Benchmark Suite Runner.

Runs all benchmark tracks and produces a unified evidence index:

    benchmarks/results/
      index.json
      index.sdif
      index.sdif.ai
      README.md
      dashboard.html
      token_efficiency/
      context_packing/
      roundtrip_fidelity/
      delta_compactness/
      retrieval_accuracy/  (opt-in)

Usage:
    python benchmarks/scripts/run_suite.py [--skip TOKEN] [--skip CONTEXT] ...
    SDIF_BENCHMARK_RETRIEVAL=1 ANTHROPIC_API_KEY=<key> python benchmarks/scripts/run_suite.py

Environment:
    SDIF_BENCHMARK_SKIP=token,context,roundtrip,delta,retrieval
        Comma-separated list of track short names to skip.
    SDIF_BENCHMARK_RETRIEVAL=1
        Opt-in to the retrieval accuracy track (requires ANTHROPIC_API_KEY).
    SDIF_BENCHMARK_OUTPUT_DIR=<path>
        Redirect all output. Default: benchmarks/ under the repository root.
    SDIF_BENCHMARK_VERBOSE=1
        Print extra diagnostics.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

_BENCHMARK_DIR = Path(__file__).resolve().parent.parent
if str(_BENCHMARK_DIR / "src") not in sys.path:
    sys.path.insert(0, str(_BENCHMARK_DIR / "src"))

import infra  # noqa: E402
import report  # noqa: E402
from infra import (  # noqa: E402
    BENCHMARK_DIR,
    REPO_ROOT,
    benchmark_output_dir,
    benchmark_result_dir,
    display_path,
    load_env_file,
    markdown_escape,
    utc_now_iso,
)

SUITE_VERSION = "1.0"

TRACKS = [
    {
        "id": "token_efficiency",
        "short": "token",
        "label": "Token Efficiency",
        "script": "token_efficiency.py",
        "optional": False,
        "claim": "SDIF AI reduces token usage vs JSON Compact",
    },
    {
        "id": "context_packing",
        "short": "context",
        "label": "Context Packing",
        "script": "context_packing.py",
        "optional": False,
        "claim": "SDIF AI fits more documents into fixed context windows",
    },
    {
        "id": "roundtrip_fidelity",
        "short": "roundtrip",
        "label": "Round-trip Fidelity",
        "script": "roundtrip_fidelity.py",
        "optional": False,
        "claim": "SDIF preserves structure, value, and type across the corpus",
    },
    {
        "id": "delta_compactness",
        "short": "delta",
        "label": "Mutation Sensitivity",
        "script": "delta_compactness.py",
        "optional": False,
        "claim": "SDIF produces less noise on full-document re-send after mutation",
    },
    {
        "id": "retrieval_accuracy",
        "short": "retrieval",
        "label": "Retrieval Accuracy",
        "script": "retrieval_accuracy.py",
        "optional": True,
        "claim": "LLMs answer structured questions more accurately from SDIF",
    },
]

SCRIPTS_DIR = BENCHMARK_DIR / "scripts"


# ====================
# Scorecard extraction
# ====================


def _extract_token_scorecard(result_dir: Path) -> dict[str, Any]:
    summary = json.loads((result_dir / "summary.json").read_text())
    ranking = summary.get("consensusRanking", [])
    sdif_ai = next((r for r in ranking if r.get("format") == "SDIF AI"), None)
    json_compact = next((r for r in ranking if r.get("format") == "JSON Compact"), None)
    if sdif_ai:
        return {
            "metric": "medianRatioVsJsonCompact",
            "value": round(sdif_ai["medianRatio"], 1),
            "unit": "%",
            "description": f"SDIF AI median token ratio vs JSON Compact: {sdif_ai['medianRatio']:.1f}%",
            "bestRatio": round(sdif_ai.get("bestRatio", 0), 1),
            "worstRatio": round(sdif_ai.get("worstRatio", 0), 1),
        }
    return {"metric": "unavailable", "value": None}


def _extract_context_scorecard(result_dir: Path) -> dict[str, Any]:
    summary = json.loads((result_dir / "summary.json").read_text())
    pfs = summary.get("perFormatSummary", {})
    sdif_ai = pfs.get("SDIF_AI") or pfs.get("SDIF AI")
    json_compact = pfs.get("JSON_Compact") or pfs.get("JSON Compact")
    if sdif_ai and json_compact:
        fit_32k_sdif = sdif_ai.get("fitRate", {}).get("b32768", 0)
        fit_32k_json = json_compact.get("fitRate", {}).get("b32768", 0)
        fit_128k_sdif = sdif_ai.get("fitRate", {}).get("b131072", 0)
        return {
            "metric": "fitRateAt32K",
            "value": round(fit_32k_sdif, 1),
            "unit": "%",
            "description": f"SDIF AI 32K fit rate: {fit_32k_sdif:.0f}% vs JSON Compact {fit_32k_json:.0f}%",
            "fitRateAt32K_jsonCompact": round(fit_32k_json, 1),
            "fitRateAt128K_sdifAI": round(fit_128k_sdif, 1),
        }
    return {"metric": "unavailable", "value": None}


def _extract_roundtrip_scorecard(result_dir: Path) -> dict[str, Any]:
    summary = json.loads((result_dir / "summary.json").read_text())
    docs = summary.get("documents", [])
    sdif_fidelities: list[float] = []
    sdif_successes = 0
    sdif_total = 0
    for doc in docs:
        for fmt in doc.get("formats", []):
            if fmt.get("format") == "SDIF":
                sdif_total += 1
                if fmt.get("parseSuccess"):
                    sdif_successes += 1
                    fid = fmt.get("overallFidelity")
                    if fid is not None:
                        sdif_fidelities.append(fid)
    avg_fidelity = sum(sdif_fidelities) / len(sdif_fidelities) if sdif_fidelities else None
    return {
        "metric": "sdifOverallFidelity",
        "value": round(avg_fidelity, 2) if avg_fidelity is not None else None,
        "unit": "%",
        "description": f"SDIF round-trip: {sdif_successes}/{sdif_total} documents, avg fidelity {avg_fidelity:.1f}%" if avg_fidelity else "n/a",
        "successfulRoundTrips": f"{sdif_successes}/{sdif_total}",
    }


def _extract_delta_scorecard(result_dir: Path) -> dict[str, Any]:
    summary = json.loads((result_dir / "summary.json").read_text())
    docs = summary.get("documents", [])
    sdif_deltas: list[float] = []
    json_deltas: list[float] = []
    for doc in docs:
        for fmt in doc.get("formats", []):
            if fmt.get("format") == "SDIF":
                sdif_deltas.append(fmt.get("tokenDeltaPct", 0))
            elif fmt.get("format") == "JSON Compact":
                json_deltas.append(fmt.get("tokenDeltaPct", 0))
    avg_sdif = sum(sdif_deltas) / len(sdif_deltas) if sdif_deltas else None
    avg_json = sum(json_deltas) / len(json_deltas) if json_deltas else None
    return {
        "metric": "avgTokenDeltaPct",
        "value": round(avg_sdif, 2) if avg_sdif is not None else None,
        "unit": "%",
        "description": f"SDIF avg token delta on full-resend: {avg_sdif:.1f}% vs JSON Compact {avg_json:.1f}%" if avg_sdif and avg_json else "n/a",
        "jsonCompactAvgDelta": round(avg_json, 2) if avg_json is not None else None,
        "note": "full-resend model — not true SDIF delta encoding",
    }


def _extract_retrieval_scorecard(result_dir: Path) -> dict[str, Any]:
    summary_path = result_dir / "summary.json"
    if not summary_path.exists():
        return {"metric": "unavailable", "value": None}
    summary = json.loads(summary_path.read_text())
    formats = summary.get("perFormatSummary", {})
    sdif_ai = formats.get("SDIF_AI") or formats.get("SDIF AI")
    json_compact = formats.get("JSON_Compact") or formats.get("JSON Compact")
    if sdif_ai:
        acc = sdif_ai.get("accuracy", sdif_ai.get("overallAccuracy"))
        return {
            "metric": "overallAccuracy",
            "value": round(acc, 1) if acc is not None else None,
            "unit": "%",
            "description": f"SDIF AI retrieval accuracy: {acc:.1f}%" if acc else "n/a",
        }
    return {"metric": "unavailable", "value": None}


_SCORECARD_EXTRACTORS = {
    "token_efficiency": _extract_token_scorecard,
    "context_packing": _extract_context_scorecard,
    "roundtrip_fidelity": _extract_roundtrip_scorecard,
    "delta_compactness": _extract_delta_scorecard,
    "retrieval_accuracy": _extract_retrieval_scorecard,
}


# ====================
# Suite runner
# ====================


def _run_track(track: dict[str, Any], *, retrieval_enabled: bool, env: dict[str, str]) -> bool:
    script = SCRIPTS_DIR / track["script"]
    cmd = [sys.executable, str(script)]
    track_env = {**os.environ, **env}
    if track["id"] == "retrieval_accuracy":
        if not retrieval_enabled:
            print(f"  ⏭  Skipping retrieval_accuracy (set SDIF_BENCHMARK_RETRIEVAL=1 to enable)")
            return False
        track_env["SDIF_BENCHMARK_RETRIEVAL"] = "1"

    print(f"\n{'='*60}")
    print(f"  Running: {track['label']} ({track['script']})")
    print(f"{'='*60}")
    t0 = time.monotonic()
    result = subprocess.run(cmd, env=track_env)
    elapsed = time.monotonic() - t0
    if result.returncode == 0:
        print(f"  ✅ {track['label']} completed in {elapsed:.1f}s")
        return True
    else:
        print(f"  ❌ {track['label']} failed (exit {result.returncode}) after {elapsed:.1f}s")
        return False


def _build_index(
    run_results: list[dict[str, Any]],
    generated_at: str,
    *,
    corpus_documents: int,
) -> dict[str, Any]:
    scorecard = []
    artifacts = []
    for entry in run_results:
        track = entry["track"]
        if not entry["ran"] or not entry["success"]:
            continue
        result_dir = benchmark_result_dir(track["id"])
        scorecard_data = _SCORECARD_EXTRACTORS[track["id"]](result_dir)
        scorecard.append({
            "track": track["id"],
            "label": track["label"],
            "claim": track["claim"],
            **scorecard_data,
            "evidence": f"{track['id']}/summary.md",
        })
        artifacts.append({
            "track": track["id"],
            "label": track["label"],
            "summaryMd": f"{track['id']}/summary.md",
            "summaryJson": f"{track['id']}/summary.json",
            "summarySdif": f"{track['id']}/summary.sdif",
            "summarySdifAi": f"{track['id']}/summary.sdif.ai",
            "dashboard": f"{track['id']}/dashboard.html",
        })

    return {
        "kind": "BenchmarkSuiteReport",
        "version": SUITE_VERSION,
        "generatedAt": generated_at,
        "corpus": {
            "source": "examples/golden",
            "documents": corpus_documents,
        },
        "tracks": [e["track"]["id"] for e in run_results if e["ran"] and e["success"]],
        "scorecard": scorecard,
        "artifacts": artifacts,
    }


def _index_readme(index: dict[str, Any], generated_at: str) -> str:
    scorecard = index.get("scorecard", [])
    lines = [
        "# SDIF Benchmark Suite — Results",
        "",
        "> Generated by `benchmarks/scripts/run_suite.py`.",
        f"> Last run: `{generated_at}`",
        "",
        "SDIF is evaluated across five dimensions:",
        "",
        "| Dimension | Claim | Result |",
        "| --- | --- | ---: |",
    ]
    for entry in scorecard:
        val = entry.get("value")
        unit = entry.get("unit", "")
        result_str = f"{val}{unit}" if val is not None else "—"
        lines.append(
            f"| {markdown_escape(entry['label'])} "
            f"| {markdown_escape(entry['claim'])} "
            f"| {result_str} |"
        )

    lines.extend([
        "",
        "## Explore",
        "",
        "- [Open suite dashboard](dashboard.html)",
        "- [Raw index](index.json) / [SDIF](index.sdif) / [SDIF AI](index.sdif.ai)",
        "",
        "## Tracks",
        "",
    ])
    for entry in index.get("artifacts", []):
        lines.extend([
            f"### {markdown_escape(entry['label'])}",
            "",
            f"- [Summary]({entry['summaryMd']})",
            f"- [Dashboard]({entry['dashboard']})",
            f"- SDIF AI: [{entry['summarySdifAi']}]({entry['summarySdifAi']})",
            "",
        ])

    lines.extend([
        "## Reproduce",
        "",
        "```bash",
        "make benchmark-token",
        "make benchmark-packing",
        "make benchmark-roundtrip",
        "make benchmark-delta",
        "# opt-in:",
        "SDIF_BENCHMARK_RETRIEVAL=1 ANTHROPIC_API_KEY=<key> make benchmark-retrieval",
        "# or run the full suite:",
        "python benchmarks/scripts/run_suite.py",
        "```",
        "",
        "## Meta",
        "",
        "> The benchmark evidence for SDIF is itself published in SDIF format.",
        "> `index.sdif.ai` is a compact AI-optimized overview of this entire suite.",
        "",
    ])
    return "\n".join(lines)


def _suite_dashboard_html(index: dict[str, Any], readme_md: str) -> str:
    template_path = BENCHMARK_DIR / "src" / "suite_dashboard.html"
    if template_path.exists():
        template = template_path.read_text(encoding="utf-8")
        index_json = json.dumps(index, ensure_ascii=False)
        # Escape </script> sequences to prevent early tag close in <script> block
        safe_json = index_json.replace("</", "<\\/")
        template = template.replace("__SUITE_INDEX_JSON__", safe_json)
        return template
    # Minimal fallback if template missing
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>SDIF Benchmark Suite</title>
<style>body{{font-family:sans-serif;max-width:900px;margin:2rem auto;padding:0 1rem}}</style>
</head>
<body>
<h1>SDIF Benchmark Suite</h1>
<p>Generated: {index['generatedAt']}</p>
<h2>Scorecard</h2>
<table border="1" cellpadding="6">
<tr><th>Dimension</th><th>Claim</th><th>Result</th></tr>
{''.join(
    f"<tr><td>{e['label']}</td><td>{e['claim']}</td><td>{e.get('value','—')}{e.get('unit','')}</td></tr>"
    for e in index.get('scorecard', [])
)}
</table>
<h2>Artifacts</h2>
<ul>
{''.join(
    f'<li><a href="{e["dashboard"]}">{e["label"]} Dashboard</a></li>'
    for e in index.get('artifacts', [])
)}
</ul>
</body>
</html>"""


# ====================
# Main
# ====================


def main() -> None:
    parser = argparse.ArgumentParser(description="SDIF Benchmark Suite Runner")
    parser.add_argument(
        "--skip",
        action="append",
        default=[],
        metavar="TRACK",
        help="Skip a track by short name (token, context, roundtrip, delta, retrieval). Repeatable.",
    )
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        metavar="TRACK",
        help="Run only these tracks. Repeatable.",
    )
    args = parser.parse_args()

    env_file_loaded = load_env_file(REPO_ROOT / ".env")
    retrieval_enabled = os.environ.get("SDIF_BENCHMARK_RETRIEVAL") == "1"
    skip_set = {s.lower() for s in args.skip}
    only_set = {s.lower() for s in args.only}

    skip_env = os.environ.get("SDIF_BENCHMARK_SKIP", "")
    if skip_env:
        skip_set.update(s.strip().lower() for s in skip_env.split(",") if s.strip())

    generated_at = utc_now_iso()
    print(f"\n🧪 SDIF Benchmark Suite")
    print(f"   Generated at: {generated_at}")
    print(f"   Env file loaded: {env_file_loaded}")

    run_results: list[dict[str, Any]] = []
    for track in TRACKS:
        short = track["short"]
        if only_set and short not in only_set:
            run_results.append({"track": track, "ran": False, "success": False, "reason": "not in --only"})
            continue
        if short in skip_set:
            print(f"\n  ⏭  Skipping {track['label']} (--skip {short})")
            run_results.append({"track": track, "ran": False, "success": False, "reason": "skipped"})
            continue
        if track["optional"] and not retrieval_enabled:
            run_results.append({"track": track, "ran": False, "success": False, "reason": "opt-in required"})
            _run_track(track, retrieval_enabled=False, env={})
            continue

        success = _run_track(track, retrieval_enabled=retrieval_enabled, env={})
        run_results.append({"track": track, "ran": True, "success": success})

    # Count corpus documents from golden dir
    from infra import benchmark_golden_dir, discover_documents
    corpus_docs = len(discover_documents(benchmark_golden_dir()))

    index = _build_index(run_results, generated_at, corpus_documents=corpus_docs)
    readme_md = _index_readme(index, generated_at)

    results_dir = benchmark_output_dir() / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    index_json = report.render_json_report(index)
    (results_dir / "index.json").write_text(index_json, encoding="utf-8")

    # index.sdif — keys must be valid SDIF identifiers (no digit-start)
    # the index dict is already clean, but scorecard list needs care
    # Use render_json_report for index.sdif fallback when SDIF converter chokes on complex nested data
    try:
        index_sdif = report.render_sdif_report(index)
    except Exception:
        index_sdif = f"# BenchmarkSuiteReport (SDIF rendering skipped — see index.json)\n"
    (results_dir / "index.sdif").write_text(index_sdif, encoding="utf-8")

    try:
        index_sdif_ai = report.render_sdif_ai_report(index_sdif)
    except Exception:
        index_sdif_ai = index_sdif
    (results_dir / "index.sdif.ai").write_text(index_sdif_ai, encoding="utf-8")
    import report as _report
    (results_dir / "index-sdif-ai-viewer.html").write_text(
        _report.render_sdif_ai_viewer(index_sdif_ai, "SDIF Benchmark Suite — Index SDIF AI", back_href="dashboard.html"),
        encoding="utf-8",
    )

    (results_dir / "README.md").write_text(readme_md, encoding="utf-8")
    (results_dir / "README-viewer.html").write_text(
        _report.render_md_viewer(readme_md, "SDIF Benchmark Suite — README", back_href="dashboard.html"),
        encoding="utf-8",
    )

    dashboard_html = _suite_dashboard_html(index, readme_md)
    (results_dir / "dashboard.html").write_text(dashboard_html, encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"  📋 Suite complete: {len([r for r in run_results if r['ran'] and r['success']])} tracks ran")
    print(f"{'='*60}")
    for entry in run_results:
        t = entry["track"]
        if entry["ran"] and entry["success"]:
            print(f"  ✅ {t['label']}")
        elif entry["ran"] and not entry["success"]:
            print(f"  ❌ {t['label']} (failed)")
        else:
            reason = entry.get("reason", "skipped")
            print(f"  ⏭  {t['label']} ({reason})")

    print(f"\n🗂️  Suite index written to:")
    print(f"  {display_path(results_dir / 'index.json')}")
    print(f"  {display_path(results_dir / 'index.sdif')}")
    print(f"  {display_path(results_dir / 'index.sdif.ai')}")
    print(f"  {display_path(results_dir / 'README.md')}")
    print(f"  {display_path(results_dir / 'dashboard.html')}")


if __name__ == "__main__":
    main()
