# Changelog

## [Unreleased]

### Fixed

- Fixed canonicalization of list literals so `canonicalize → parse` preserves lists as
  lists instead of converting them into quoted strings. Previously, `_quote_if_needed`
  re-quoted any list literal containing a comma or double-quote — a semantic change, not
  normalization. Both bare-token lists (`[a,b,c]`, `[1,2,3]`) and quoted-string lists
  (`["alpha","beta"]`) now survive the round-trip unchanged.
- Regenerated the `plan` canonical fixture and SHA-256 hash: the canonical representation
  of `scope.in` was semantically incorrect (a quoted string instead of a list literal).
  The new hash reflects the corrected canonical output.
- Fixed SDIF AI expansion of `$`-suffixed table columns so numeric-looking strings such
  as HTTP status codes (`"200"`, `"404"`) remain strings during round-trip conversion.
  Previously, `expand_ai_doc()` recorded column indices in `Table.quoted_columns` but
  `_parse_table_cell` ignored that set and coerced the values to integers.
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
  - `test_canonicalize_preserves_list_literals` — guards against `canonicalize` converting
    list literals to quoted strings; covers bare-token, numeric, and quoted-string variants.
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
