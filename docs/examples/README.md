# SDIF examples

Authoritative runnable examples live in the repository-level [`examples/`](../../examples/) directory:

- [`plan.sdif`](../../examples/plan.sdif): planning document with fields, table rows, relations, and rules.
- [`validation-report.sdif`](../../examples/validation-report.sdif): validation output with diagnostics as compact rows.
- [`registry.sdif`](../../examples/registry.sdif): semantic registry of modules and capabilities.
- [`schema.sdif`](../../examples/schema.sdif): MVP schema used by validation and schema-aware canonicalization tests.

## Golden fixtures

Canonicalization and conversion fixtures live under [`examples/golden/`](../../examples/golden/).
Each fixture directory treats JSON as the semantic source of truth and contains:

- `equivalent.json`: JSON is the semantic source for the fixture.
- `source.sdif`: SDIF generated from `equivalent.json`.
- `canonical.sdif`: expected canonical bytes for `source.sdif`.
- `canonical.sha256`: SHA-256 over `canonical.sdif`.

Generated comparison formats that are not part of the current compatibility contract should not be checked in under golden fixture directories.
Run this before committing fixture changes:

```bash
python3 scripts/generate_golden_fixtures.py --check
python3 -m pytest tests/test_json_golden_equivalence.py tests/test_canonical_fixtures.py -q
```
