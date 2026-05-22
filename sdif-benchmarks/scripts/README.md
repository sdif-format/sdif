# Benchmark Scripts

Executable benchmark runners. Each script reads from `examples/golden/` (or `SDIF_BENCHMARK_GOLDEN_DIR`), writes in-progress evidence to `benchmarks/tmp/<track>/`, and moves the result to `benchmarks/results/<track>/` on success.

| Script | Track | What it measures |
| --- | --- | --- |
| `run_suite.py` | *(all)* | Orchestrates all tracks and produces `benchmarks/results/index.*` + `dashboard.html` |
| `token_efficiency.py` | `token_efficiency` | Byte and token reduction across all formats vs JSON Compact |
| `context_packing.py` | `context_packing` | How many documents of each format fit in 4K/8K/32K/128K context budgets |
| `roundtrip_fidelity.py` | `roundtrip_fidelity` | JSON→format→JSON value, type, and structure preservation |
| `delta_compactness.py` | `delta_compactness` | Token overhead of re-sending a mutated document (mutation sensitivity; full-resend, not true delta) |
| `retrieval_accuracy.py` | `retrieval_accuracy` | LLM answer quality by format — opt-in, requires `SDIF_BENCHMARK_RETRIEVAL=1` and `ANTHROPIC_API_KEY` |

Run the full suite: `make benchmark-suite` or `python benchmarks/scripts/run_suite.py`.

Run individual tracks: `make benchmark-<track>` or `python benchmarks/scripts/<script>.py`.

`run_suite.py` supports `--skip TRACK` and `--only TRACK` flags (short names: `token`, `context`, `roundtrip`, `delta`, `retrieval`).
