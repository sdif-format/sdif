# Changelog

## [Unreleased]

### Fixed

- Fixed `_parse_table_cell` in `sdif.json.converter` to honour `Table.quoted_columns`
  when decoding. Previously, after `expand_ai_doc()` strips the `$` suffix from column
  names and records their indices in `quoted_columns`, the decoder ignored that set and
  coerced numeric-looking strings (e.g. HTTP status codes `"200"`, `"404"`) to integers.
  Now the column index is checked against `quoted_columns` and such cells are returned
  as strings.
- Fixed `_quote_if_needed` in `sdif.canonical.canonicalizer` to not re-quote bare list
  literals (e.g. `[a,b,c]`, `[1,2,3]`). Previously, the presence of a comma caused the
  safe-identifier check to fall through and wrap the literal in quotes, converting a list
  into a string after a canonicalize → parse round-trip.
- Fixed release checks so CI runs development tooling through declared dev extras.
- Fixed Python 3.10 type-checking compatibility for the `tomllib` fallback.
- Added `expand_ai_doc()` to `sdif.ai` — expands `.sdif.ai` aliases and returns a `Document`
  without calling `canonicalize()`. This preserves statement order (fields, rules, relations)
  for callers that need semantic equivalence rather than canonical form.
  `sdif_from_ai()` now delegates to `expand_ai_doc()` before canonicalizing.

### Added

- Regression tests in `tests/test_json_conversion.py`:
  - `test_scalar_ambiguous_strings_survive_json_sdif_json_field_round_trip` — verifies
    strings matching typed SDIF literals (`"200"`, `"true"`, `"null"`, `"[1,2]"`, `""`,
    etc.) round-trip through JSON→SDIF→JSON as strings.
  - `test_scalar_ambiguous_strings_survive_json_sdif_json_table_round_trip` — same for
    table cells.
  - `test_scalar_ambiguous_strings_survive_sdif_ai_expand_table_round_trip` — same
    through the SDIF AI → `expand_ai_doc` → `document_to_json_data` path.
  - `test_canonicalize_preserves_list_literals_without_inner_quotes` — guards against
    `canonicalize` converting bare list literals to quoted strings.
- Configured Dependabot updates for Python dependencies and GitHub Actions.
- Exported `expand_ai_doc` from the `sdif.ai` public API.

### Maintenance

- Cleaned up test imports to satisfy CodeQL maintainability checks.
- Refreshed the `uv.lock` lockfile after development dependency updates.

## 1.0.0 - 2026-05-22

### Stable v1 contract

- Freezes `@sdif 1.0` and `@sdif.ai 1.0` as the supported v1 document directives.
- Defines canonical-syntax-v1 as the reproducible source of canonical hashes.
- Treats `.sdif.ai` as a derived, reversible projection of canonical SDIF.
- Ships the Python parser, canonicalizer, validator, CLI, conformance fixtures, and shared specification at package version `1.0.0`.

### Repository split

- Moves benchmark ownership to the sibling `sdif-benchmarks` repository.
- Moves Tree-sitter grammar ownership to the sibling `tree-sitter-sdif` repository.
- Keeps the core repository focused on the SDIF specification, reference implementation, conformance fixtures, examples, and documentation.

### Reference implementation

- Provides parser, canonicalizer, schema validation, JSON conversion, `.sdif.ai` projection helpers, CLI tooling, and token counting utilities.
- Preserves literal HTAB table-cell semantics across parser, canonicalizer, examples, and conformance coverage.
- Documents the stable v1 format, canonicalization contract, semantic-quality boundaries, and ecosystem repositories.

### Release gates

- Full pytest suite.
- Conformance fixture checker.
- Semantic-quality documentation checker.
- Core release checks with benchmark and Tree-sitter checks removed from the core CI boundary.
- Deterministic local benchmark smoke coverage delegated to `sdif-benchmarks`.
- Tree-sitter scaffold and grammar checks delegated to `tree-sitter-sdif`.
