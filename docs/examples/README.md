# SDIF examples

Authoritative runnable examples live in the repository-level [`examples/`](../../examples/) directory.


## Golden fixtures

Canonicalization fixtures live under [`examples/golden/`](../../examples/golden/). Each fixture directory contains:

- `source.sdif`: source input used by tests.
- `canonical.sdif`: expected canonical bytes.
- `canonical.sha256`: SHA-256 over `canonical.sdif`.
- `equivalent.json`, `equivalent.yaml`, `equivalent.toon`: comparison projections, not canonical inputs.

The golden fixtures are part of the compatibility contract for the MVP canonicalizer.
