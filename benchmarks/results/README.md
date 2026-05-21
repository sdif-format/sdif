# Benchmark Results

This directory is reserved for curated or published benchmark evidence.

The token-efficiency runner writes in-progress evidence under `benchmarks/tmp/token_efficiency/` and moves successful runs to `benchmarks/results/token_efficiency/`.
Successful runs include `dashboard.html`, a self-contained HTML dashboard generated from the same run data as the JSON, SDIF, and Markdown reports. They also include `corpus/`, the exact per-document JSON, YAML, XML, CSV Bundle, SDIF, SDIF AI, and optional TOON files measured by the run. Keep large exploratory runs out of source control unless they are intentionally promoted as release evidence.
