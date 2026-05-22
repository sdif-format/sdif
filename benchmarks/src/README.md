# Benchmark Library

Reusable helpers shared across all benchmark tracks.

| Module | Purpose |
| --- | --- |
| `infra.py` | Path setup, directory lifecycle (`create_benchmark_run_dir`, `publish_benchmark_result`), env loading, `Tee`, `discover_documents` |
| `formats.py` | Format generators: builds JSON Compact, JSON Pretty, YAML, XML, CSV Bundle, SDIF, SDIF AI, and optionally TOON from a Python dict; `write_document_corpus` |
| `report.py` | Rendering helpers: `render_json_report`, `render_sdif_report`, `render_sdif_ai_report`, `render_dashboard_report` |
| `generic_dashboard.html` | Self-contained HTML template for per-track evidence dashboards (Summary + Detail panels) |
| `suite_dashboard.html` | Landing-page HTML template for the suite runner (`run_suite.py`) — hero claim, scorecard cards, track links |
| `dashboard_template.html` | Full token-efficiency dashboard template |

`infra.py` adds `REPO_ROOT/src` to `sys.path` at import time so all scripts can `import sdif` without extra setup. Scripts that import `formats.py` get this automatically.

Keep executable entrypoints in `benchmarks/scripts/`. Add shared code here only when two or more tracks need it.
