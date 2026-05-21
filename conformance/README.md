# SDIF conformance fixtures

This directory contains portable SDIF conformance cases for parser, canonicalizer,
and tooling implementations. The fixtures are intentionally SDIF-first: the
manifest is `manifest.sdif`, and each case includes source bytes, canonical
bytes, a canonical SHA-256 digest, and an expected Tree-sitter-style syntax
shape.

These fixtures reduce reliance on one implementation as the only authority.
The specification and this fixture suite define the portable behavior; the
Python parser is the current reference implementation used by the checker until
independent parser backends are wired into CI.

## Layout

```text
manifest.sdif
cases/<case-id>/source.sdif
cases/<case-id>/canonical.sdif
cases/<case-id>/expected.tree
```

Run:

```bash
python3 scripts/check_conformance_fixtures.py
```
