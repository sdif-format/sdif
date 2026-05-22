"""Shared rendering helpers: JSON, SDIF, and HTML dashboard output."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import infra  # noqa: F401 — ensures REPO_ROOT/src is on sys.path

BENCHMARK_DIR = Path(__file__).resolve().parents[1]
DASHBOARD_TEMPLATE_PATH = BENCHMARK_DIR / "src" / "dashboard_template.html"
GENERIC_DASHBOARD_TEMPLATE_PATH = BENCHMARK_DIR / "src" / "generic_dashboard.html"


def render_json_report(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def render_sdif_report(data: dict[str, Any]) -> str:
    from sdif.json import json_data_to_sdif

    return json_data_to_sdif(data, include_header=True)


def render_sdif_ai_report(sdif_text: str) -> str:
    from formats import compact_ai_projection

    return compact_ai_projection(sdif_text)


def json_script_payload(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def render_dashboard_report(
    structured_data: dict[str, Any],
    summary_markdown: str,
    detail_markdown: str,
    *,
    template_path: Path | None = None,
) -> str:
    path = template_path or GENERIC_DASHBOARD_TEMPLATE_PATH
    template = path.read_text(encoding="utf-8")
    replacements = {
        "__SDIF_REPORT_DATA_JSON__": json_script_payload(structured_data),
        "__SDIF_SUMMARY_MD_JSON__": json_script_payload(summary_markdown),
        "__SDIF_COMPARISON_MD_JSON__": json_script_payload(detail_markdown),
    }
    for marker, payload in replacements.items():
        if marker not in template:
            raise RuntimeError(f"Dashboard template missing marker: {marker}")
        template = template.replace(marker, payload, 1)
    return template
