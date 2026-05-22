"""Shared rendering helpers: JSON, SDIF, and HTML dashboard output."""

from __future__ import annotations

import html
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


_MD_VIEWER_CSS = """
body{margin:0;padding:32px;background:#f6f7f9;color:#1f2937;font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.page{max-width:960px;margin:0 auto}
.toolbar{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-bottom:20px}
.toolbar a{color:#2563eb;text-decoration:none;font-weight:600}
.toolbar a:hover{text-decoration:underline}
.md{background:#fff;padding:40px;border-radius:16px;box-shadow:0 10px 30px rgba(15,23,42,.08);line-height:1.65}
.md h1,.md h2,.md h3{line-height:1.25;margin-top:1.6em}
.md h1:first-child,.md h2:first-child,.md h3:first-child{margin-top:0}
.md h1{padding-bottom:.35em;border-bottom:1px solid #e5e7eb}
.md code{background:#f1f5f9;padding:.15em .35em;border-radius:6px;font-size:.95em}
.md pre{background:#0f172a;color:#e5e7eb;padding:16px;border-radius:12px;overflow-x:auto}
.md pre code{background:transparent;color:inherit;padding:0}
.md table{width:100%;border-collapse:collapse;margin:1.5em 0}
.md th,.md td{border:1px solid #e5e7eb;padding:8px 12px;text-align:left}
.md th{background:#f8fafc}
.md blockquote{margin-left:0;padding-left:16px;border-left:4px solid #cbd5e1;color:#475569}
.md img{max-width:100%;border-radius:8px}
"""


def render_md_viewer(md_text: str, title: str, *, back_href: str = "dashboard.html") -> str:
    """Render markdown to a self-contained HTML file (no JS, no external deps)."""
    try:
        import markdown as _md

        body = _md.markdown(
            md_text,
            extensions=["tables", "fenced_code"],
        )
    except ImportError:
        body = f"<pre>{html.escape(md_text)}</pre>"

    escaped_title = html.escape(title)
    escaped_back = html.escape(back_href)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>{escaped_title}</title>
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style>{_MD_VIEWER_CSS}</style>
</head>
<body>
<main class="page">
<div class="toolbar">
<a href="{escaped_back}">← Back</a>
<span></span>
</div>
<article class="md">
{body}
</article>
</main>
</body>
</html>
"""


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
