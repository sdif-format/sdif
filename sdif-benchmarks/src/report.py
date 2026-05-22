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


_SDIF_AI_VIEWER_CSS = """
body{margin:0;padding:32px;background:#0f172a;color:#e2e8f0;font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.page{max-width:1100px;margin:0 auto}
.toolbar{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-bottom:20px}
.toolbar a{color:#60a5fa;text-decoration:none;font-weight:600}
.toolbar a:hover{text-decoration:underline}
.meta{font-size:.8em;color:#64748b;margin-bottom:8px}
pre.sdif{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:24px 28px;overflow-x:auto;line-height:1.6;font-size:.88em;white-space:pre}
.d{color:#818cf8}
.h{color:#f472b6;font-weight:700}
.bh{color:#a78bfa}
.k{color:#38bdf8}
.v{color:#a3e635}
.r{color:#fb923c}
.c{color:#475569;font-style:italic}
.row{color:#cbd5e1}
"""

# Identifier pattern that allows dots (matches sdif.ai, some.namespace)
_IDENT = r"[A-Za-z_][A-Za-z0-9_.-]*"


def _highlight_sdif_ai(text: str) -> str:
    import re

    lines = []
    for line in text.splitlines():
        esc = html.escape(line)
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        if stripped.startswith("#"):
            # comment
            lines.append(f'<span class="c">{esc}</span>')
        elif stripped.startswith("@"):
            # directive: @sdif.ai 1.0
            lines.append(f'<span class="d">{esc}</span>')
        elif re.match(rf"^{_IDENT}\[", stripped) or re.match(rf"^{_IDENT}\]:$", stripped):
            # table_header: name[col1,col2]: or grouped_relation closer name]:
            lines.append(f'<span class="h">{esc}</span>')
        elif re.match(r"^rel[\[:]", stripped):
            # relation_block: rel: or grouped_relation_block: rel[subject]:
            lines.append(f'<span class="r">{esc}</span>')
        elif re.match(r"^rules:", stripped):
            # rules_block
            lines.append(f'<span class="r">{esc}</span>')
        elif indent == 0 and re.match(rf"^{_IDENT}:$", stripped):
            # block_header: corpus: scorecard: notes:
            lines.append(f'<span class="bh">{esc}</span>')
        elif indent == 0 and re.match(rf"^{_IDENT}\s", stripped):
            # zero-indent field or table row: key value
            m = re.match(rf"^({_IDENT})\s+(.*)", stripped)
            if m:
                k = html.escape(m.group(1))
                v = html.escape(m.group(2))
                lines.append(f'<span class="k">{k}</span> <span class="v">{v}</span>')
            else:
                lines.append(esc)
        elif indent > 0:
            lines.append(f'<span class="row">{esc}</span>')
        else:
            lines.append(esc)
    return "\n".join(lines)


def render_sdif_ai_viewer(sdif_ai_text: str, title: str, *, back_href: str = "dashboard.html") -> str:
    """Render a .sdif.ai file as a self-contained syntax-highlighted HTML viewer."""
    body = _highlight_sdif_ai(sdif_ai_text)
    size_kb = len(sdif_ai_text.encode()) / 1024
    lines = sdif_ai_text.count("\n") + 1
    escaped_title = html.escape(title)
    escaped_back = html.escape(back_href)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>{escaped_title}</title>
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style>{_SDIF_AI_VIEWER_CSS}</style>
</head>
<body>
<main class="page">
<div class="toolbar">
<a href="{escaped_back}">← Back</a>
<span>{escaped_title}</span>
</div>
<div class="meta">{lines} lines · {size_kb:.1f} KB · SDIF AI projection</div>
<pre class="sdif">{body}</pre>
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
