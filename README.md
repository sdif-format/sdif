# SDIF — Semantic Data Interchange Format

[![Status](https://img.shields.io/badge/status-0.2.8--draft-orange)](docs/spec.md)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

SDIF is a compact, semantic, canonicalizable data interchange format for AI agents and deterministic machine workflows, with human-auditable source files.

It targets documents that need more meaning and auditability than CSV, less ambiguity than YAML, more token efficiency than JSON in repeated records, and deterministic bytes for hashing/signing.

```text
SDIF = structured data + compact tables + semantic relations + declarative rules + canonical form
```

## Why SDIF?

JSON repeats field names in arrays:

```json
[
  { "id": "R1", "status": "done", "gate": "verify", "evidence": "reports/syntax.md" },
  { "id": "R2", "status": "pending", "gate": "verify", "evidence": "reports/schema.md" }
]
```

SDIF declares the shape once and uses literal tabs (`HTAB`) between table cells. This is a deliberate agent/tooling tradeoff: it keeps table cells compact and unquoted, but editors must preserve tabs:

```sdif
milestones[id,status,gate,evidence]:
  R1	done	verify	reports/syntax.md
  R2	pending	verify	reports/schema.md
```

It also represents semantic relationships directly:

```sdif
rel:
  R2 depends_on R1
  release.v2.validation_plan validated_by validation.report.v2
```

## Current repository status

This repository is implementing the 0.1 MVP:

```text
source.sdif -> AST -> canonical bytes -> sha256 hash
```

The initial Python package includes a parser, schema validation, schema-aware canonicalization, JSON conversion, `.sdif.ai` projection helpers, CLI tooling, and golden fixtures. Tree-sitter now has an MVP grammar package, corpus fixture, highlight query, and shared conformance fixtures for editor/agent tooling; the specification plus conformance fixtures are the portable authority, with the Python parser acting as the current reference implementation.

The `.sdif.ai` projection is the token-dense agent surface. It may omit the
canonical two-space indentation on table rows and mark string-preserved table
columns with a `$` suffix, such as `value$`, so scalar-like strings (`null`,
`42`, `true`) do not need repeated quotes in every row.

## Quick start

```bash
python -m pip install -e '.[dev]'
sdif parse examples/plan.sdif
sdif canon examples/plan.sdif
sdif canon examples/plan.sdif --schema examples/schema.sdif
sdif hash examples/plan.sdif
sdif hash examples/plan.sdif --schema examples/schema.sdif
sdif validate examples/plan.sdif --schema examples/schema.sdif
sdif tokens examples/plan.sdif
sdif to-json examples/plan.sdif
sdif from-json document.json
sdif ai examples/plan.sdif --alias kind=k --alias status=st
```

`sdif tokens` reports byte size, tokenizer identity, and token count. It uses
`tiktoken/cl100k_base` when `tiktoken` is installed and otherwise falls back to
a deterministic 4-bytes-per-token estimate. `benchmarks/token_comparison.py`
compares JSON, YAML, XML, CSV Bundle, canonical SDIF, and the compact SDIF AI
projection surface from the same golden JSON fixtures.

You can also run the development CLI script:

```bash
python tools/sdif-cli.py canon examples/registry.sdif
```

## Tree-sitter tooling

`tree-sitter-sdif/` contains the MVP grammar package for editor and incremental
parse tooling. It includes `grammar.js`, `tree-sitter.json`, `test/corpus/core.txt`, and
`queries/highlights.scm`. This layer is tooling-focused, but it must stay aligned with the shared
`conformance/manifest.sdif` fixture suite. SDIF and `.sdif.ai` remain the
agent-facing formats; JSON is not required as an agent working surface.

```bash
cd tree-sitter-sdif
npm install
npm run generate
npm test
```

## Documentation

- [Specification draft](docs/spec.md)
- [Canonicalization contract](docs/canonicalization.md)
- [Format comparison](docs/comparison.md)
- [Semantic quality comparison](docs/semantic-quality.md)
- [Examples](examples/)

## License

MIT. See [LICENSE](LICENSE).
