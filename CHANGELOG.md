# Changelog

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
