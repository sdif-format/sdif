# Changelog

## 1.0.0 - 2026-05-21

### Stable v1 contract

- Freezes `@sdif 1.0` and `@sdif.ai 1.0` as the supported v1 document directives.
- Defines canonical-syntax-v1 as the reproducible source of canonical hashes.
- Treats `.sdif.ai` as a derived, reversible projection of canonical SDIF.
- Ships the Python parser, canonicalizer, validator, CLI, conformance fixtures, and Tree-sitter scaffold together at package version `1.0.0`.

### Release gates

- Full pytest suite.
- Conformance fixture checker.
- Semantic-quality documentation checker.
- Tree-sitter scaffold checker.
- `compileall` smoke check for `src`, `scripts`, `tests`, and `tools`.
- Direct benchmark smoke with optional external tokenizer integrations disabled for deterministic local release evidence.
