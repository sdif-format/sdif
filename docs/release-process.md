# SDIF release process

This document records the minimal release process for SDIF `1.0.x` packages.

## Preconditions

- The working tree is clean except for intentional release changes.
- `docs/spec.md` records the stable format version, specification document version, and current Python package version.
- Tree-sitter and benchmark release gates run in the sibling `tree-sitter-sdif` and `sdif-benchmarks` repositories.
- Public docs describe the stable v1 contract without contradicting package metadata.
- `sdif-benchmarks/results/token_efficiency/` contains real benchmark artifacts from a completed run when publishing benchmark claims.

## Required gates

Run from the repository root:

```bash
make release-check

# sibling repository gates
(cd sdif-benchmarks && make test)
(cd tree-sitter-sdif && python3 scripts/check_tree_sitter_scaffold.py && npm test)
```

`make release-check` runs:

```bash
PYTHONPATH=src python3 scripts/check_conformance_fixtures.py
PYTHONPATH=src python3 -m compileall -q src scripts tests tools
uv run ruff check .
uv run mypy
uv run python -c "import sdif; print('sdif import OK')"
PYTHONPATH=src python3 -m pytest -q
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
