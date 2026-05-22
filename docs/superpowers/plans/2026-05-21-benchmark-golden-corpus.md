# Benchmark Golden Corpus Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand SDIF benchmark golden fixtures with deterministic small, medium, large, wide, deep, text-heavy, relational, and OpenAPI-derived documents.

**Architecture:** Keep `equivalent.json` as semantic source and derive `source.sdif`, `canonical.sdif`, and `canonical.sha256` with existing fixture generation. Use generated, SDIF-representable JSON to keep corpus repeatable and benchmark cost bounded.

**Tech Stack:** Python 3.12, SDIF JSON converter/canonicalizer, pytest, ruff, mypy.

---

### Task 1: Corpus policy test

**Files:**
- Modify: `tests/test_repo_artifacts.py`

- [ ] Write a failing pytest that checks benchmark golden corpus has at least 18 fixture documents, at least 4 small `<20 KiB`, 4 medium `20-200 KiB`, and 4 large `>200 KiB`, and includes `github.openapi/equivalent.json`.
- [ ] Run the focused test and confirm it fails against the current corpus.

### Task 2: Deterministic fixture generator

**Files:**
- Create or modify: `sdif-benchmarks/scripts/generate_benchmark_golden.py`
- Generated under: `examples/golden/*/{equivalent.json,source.sdif,canonical.sdif,canonical.sha256}`

- [ ] Generate SDIF-representable JSON fixture families for small, medium, large, wide, deep, text-heavy, relational, and mixed profiles.
- [ ] Derive all SDIF canonical artifacts with `scripts/generate_golden_fixtures.py`.
- [ ] Convert the provided `github.openapi/github.openapi.json` into a bounded `github.openapi/equivalent.json` fixture if the full 70 MB document is impractical.

### Task 3: Benchmark evidence

**Files:**
- Modify: `sdif-benchmarks/results/token_efficiency` result directory

- [ ] Run deterministic benchmark with optional integrations disabled.
- [ ] Inspect `sdif-benchmarks/results/token_efficiency/summary.md` and `summary.json` for corpus count and ranking consistency.

### Task 4: Closure

**Files:**
- All changed/generated files

- [ ] Run `make format`, `make lint`, `make typecheck`, `make test-cov`.
- [ ] Commit the scoped changes and leave the git tree clean.
