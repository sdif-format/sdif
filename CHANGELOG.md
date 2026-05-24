# Changelog

## [Unreleased]

## [1.1.0] - 2026-05-24

### Added

- `sdif validate` is now schema-optional. Without `--schema`, the command checks syntactic
  validity only and exits `0` (valid) or `1` (invalid SDIF). With `--schema`, schema
  validation is layered on top. A new `--quiet` flag suppresses stdout and communicates the
  result through the exit code alone, taking precedence over `--json`. Operational failures
  (file not found, policy denial) now exit `2` consistently.
- `expand_ai_doc()` in `sdif.ai`: expands `.sdif.ai` aliases into a `Document` without
  calling `canonicalize()`, preserving statement order for callers that need semantic
  equivalence over canonical form. `sdif_from_ai()` now delegates to it before canonicalizing.
  Exported from the public `sdif.ai` API.
- Dependabot configuration for Python dependencies and GitHub Actions.

### Fixed

- Alias projection: `ai_view()` now filters aliases to keys actually present in the document
  and drops any alias whose target collides with an existing literal key, preventing spurious
  expansions in documents that share names with common aliases.
- List literals: `canonicalize → parse` round-trips now preserve list type. `_quote_if_needed`
  previously re-quoted lists containing commas or double-quotes (a semantic change, not
  normalization). Both bare-token lists (`[a,b,c]`, `[1,2,3]`) and quoted-string lists
  (`["alpha","beta"]`) now survive unchanged.
- Canonical fixture: regenerated the `plan` fixture and its SHA-256 hash after `scope.in`
  was found to be stored as a quoted string instead of a list literal.
- SDIF AI table expansion: `$`-suffixed column values (e.g. HTTP status codes `"200"`,
  `"404"`) now remain strings through `expand_ai_doc()`. Previously `_parse_table_cell`
  coerced them to integers.
- CI: development tooling now runs through declared dev extras.
- Type checking: fixed Python 3.10 compatibility for the `tomllib` fallback import.

### Maintenance

- Cleaned up test imports to satisfy CodeQL maintainability rules.
- Refreshed `uv.lock` after development dependency updates.

## [1.0.0] - 2026-05-22

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
