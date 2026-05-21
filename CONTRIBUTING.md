# Contributing to SDIF

Thanks for helping build SDIF: a compact, semantic, canonicalizable data interchange format.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest
```

## Contribution rules

- Keep the specification and implementation aligned.
- Prefer deterministic behavior over permissive magic.
- Add or update fixtures for parser/canonicalization behavior.
- Use literal horizontal tabs (`HTAB`, U+0009) in table rows; ordinary spaces are data.
- Do not add executable semantics to `rules:`; rules are declarative validation input.
- Keep canonical output stable, comment-free, LF-normalized, and suitable for hashing.

## Pull request checklist

- [ ] Tests cover new behavior.
- [ ] `python -m pytest` passes.
- [ ] Documentation or examples changed when syntax/behavior changed.
- [ ] Canonicalization and hashing implications were considered.
