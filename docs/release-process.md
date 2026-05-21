# SDIF release process

This document records the minimal release process for SDIF `1.0.x` packages.

## Preconditions

- The working tree is clean except for intentional release changes.
- `pyproject.toml`, `docs/spec.md`, `tree-sitter-sdif/package.json`, and `tree-sitter-sdif/tree-sitter.json` agree on the package version where applicable.
- Public docs describe the stable v1 contract without contradicting package metadata.
- `benchmarks/latest/` contains real benchmark artifacts, not a broken symlink.

## Required gates

Run from the repository root:

```bash
PYTHONPATH=src python3 scripts/check_conformance_fixtures.py
PYTHONPATH=src python3 scripts/check_semantic_quality.py
PYTHONPATH=src python3 scripts/check_tree_sitter_scaffold.py
PYTHONPATH=src python3 -m compileall -q src scripts tests tools
uv run ruff check .
uv run mypy
uv run python -c "import sdif; print('sdif import OK')"
SDIF_ENV_OVERRIDE=0 SDIF_BENCHMARK_TOON=0 SDIF_BENCHMARK_TOKENX=0 SDIF_BENCHMARK_LLAMA=0 SDIF_BENCHMARK_CLAUDE=0 PYTHONPATH=src python3 -m pytest -q
SDIF_ENV_OVERRIDE=0 SDIF_BENCHMARK_TOON=0 SDIF_BENCHMARK_TOKENX=0 SDIF_BENCHMARK_LLAMA=0 SDIF_BENCHMARK_CLAUDE=0 PYTHONPATH=src python3 scripts/token_comparison.py
```

## Artifact hygiene

Release tarballs are produced from Git, not from the mutable working directory:

```bash
make archive
```

`make archive` creates `dist/sdif.tar.gz` with `git archive`, so ignored local files such as `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, and `.venv/` are excluded.

Before publishing, inspect the archive:

```bash
tar -tzf dist/sdif.tar.gz | grep -E '(^|/)(__pycache__|\.pytest_cache|\.mypy_cache|\.ruff_cache|\.venv)(/|$)' && exit 1 || true
```

## Publication rule

Do not publish a final `1.0.0` artifact unless every required gate above exits successfully in a clean checkout.
