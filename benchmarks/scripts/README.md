# Benchmark Scripts

This directory contains executable benchmark runners.

- `token_efficiency.py` derives every compared representation from `examples/golden/<fixture>/equivalent.json` and writes token-efficiency evidence.

New benchmark runners should live here so the benchmark suite stays organized as a first-class subsystem, similar to TOON's benchmark layout.
