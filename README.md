# SDIF — Semantic Data Interchange Format

[![Status](https://img.shields.io/badge/status-1.0.0--stable-green)](docs/spec.md)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

SDIF is a compact, semantic, canonicalizable data interchange format for AI agents and deterministic machine workflows, with human-auditable source files.

It targets documents that need more meaning and auditability than CSV, less ambiguity than YAML, more token efficiency than JSON in repeated records, and deterministic bytes for hashing/signing.

```text
SDIF = structured data + compact tables + semantic relations + declarative rules + canonical form
```

SDIF also includes an AI projection surface, `.sdif.ai`, designed for token-dense agent exchange while remaining reversible back into canonical SDIF when the projection contract is respected.

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

## Token efficiency evidence

SDIF is designed for structured semantic data that may be read, written, transformed, hashed, signed, and passed through AI agent contexts.

The current benchmark derives every compared format from the same canonical JSON semantic source:

```text
examples/golden/<document>/equivalent.json
```

The benchmark compares:

* JSON Compact
* JSON Pretty
* YAML
* XML
* CSV Bundle
* canonical SDIF
* compact SDIF AI projection

Latest benchmark summary:

| Metric                                       |                     Result |
| -------------------------------------------- | -------------------------: |
| Documents compared                           |                         21 |
| Tokenizer/document comparisons               |                         63 |
| Available tokenizers                         | Estimate, TokenX, tiktoken |
| Best consensus format                        |                    SDIF AI |
| SDIF AI consensus average rank               |                       1.06 |
| SDIF AI median ratio vs JSON Compact         |                      56.3% |
| SDIF AI wins across tokenizer/document pairs |                         59 |
| SDIF canonical median ratio vs JSON Compact  |                      59.5% |
| TOON median ratio vs JSON Compact            |                      63.2% |
| JSON Compact baseline                        |                     100.0% |

In this corpus, SDIF AI preserves structured semantics while reducing median token usage to about **56% of compact JSON**.

Tokenizer-specific winners:

| Tokenizer | Winning format |  Wins |
| --------- | -------------- | ----: |
| Estimate  | SDIF AI        | 20/21 |
| TokenX    | SDIF AI        | 20/21 |
| tiktoken  | SDIF AI        | 19/21 |

This is not a universal claim that SDIF is always smaller than every alternative. It is current benchmark evidence for this repository corpus, generated from shared canonical fixtures. Claude and Llama3 token counting were disabled in the latest run, so those results are not claimed yet.

Benchmark artifacts are written under:

```text
benchmarks/results/token_efficiency
```

For the full benchmark methodology, tracks, corpus model, and environment switches, see [`benchmarks/README.md`](benchmarks/README.md).

## Current repository status

This repository implements the stable SDIF `1.0.0` specification.

The current Python package includes:

* parser
* schema validation
* schema-aware canonicalization
* JSON conversion
* `.sdif.ai` projection helpers
* CLI tooling
* token counting utilities
* benchmark generation
* golden fixtures
* shared conformance fixtures

Tree-sitter now has a v1 grammar package, corpus fixture, highlight query, and shared conformance fixtures for editor/agent tooling.

The specification plus conformance fixtures are the portable authority, with the Python parser acting as the current reference implementation.

The `.sdif.ai` projection is the token-dense agent surface. It may omit the canonical two-space indentation on table rows and mark string-preserved table columns with a `$` suffix, such as `value$`, so scalar-like strings (`null`, `42`, `true`) do not need repeated quotes in every row.

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

`sdif tokens` reports byte size, tokenizer identity, and token count. It uses `tiktoken/cl100k_base` when `tiktoken` is installed and otherwise falls back to a deterministic 4-bytes-per-token estimate.

You can also run the development CLI script:

```bash
python tools/sdif-cli.py canon examples/registry.sdif
```

## Benchmarking

Run the benchmark script to compare JSON, YAML, XML, CSV Bundle, canonical SDIF, and the compact SDIF AI projection surface from the same golden JSON fixtures:

```bash
python benchmarks/scripts/token_efficiency.py
```

The benchmark loads `.env` when present and can optionally enable additional tokenizers.

Useful environment flags:

```bash
SDIF_BENCHMARK_LLAMA=1
SDIF_BENCHMARK_CLAUDE=1
```

Claude token counting requires API access. Llama token counting requires the corresponding local tokenizer dependencies.

A typical benchmark run produces:

```text
comparison.log
comparison.md
comparison.json
comparison.sdif
comparison.sdif.ai
summary.md
summary.json
summary.sdif
summary.sdif.ai
```

The `benchmarks/results/token_efficiency` directory contains the most recent successful token-efficiency run.

## Tree-sitter tooling

`tree-sitter-sdif/` contains the v1 grammar package for editor and incremental parse tooling.

It includes:

* `grammar.js`
* `tree-sitter.json`
* `test/corpus/core.txt`
* `queries/highlights.scm`

This layer is tooling-focused, but it must stay aligned with the shared `conformance/manifest.sdif` fixture suite.

SDIF and `.sdif.ai` remain the agent-facing formats; JSON is not required as an agent working surface.

```bash
cd tree-sitter-sdif
npm install
npm run generate
npm test
```

## Documentation

* [Specification](docs/spec.md)
* [Canonicalization contract](docs/canonicalization.md)
* [Format comparison](docs/comparison.md)
* [Semantic quality comparison](docs/semantic-quality.md)
* [Examples](examples/)

## Limitations

SDIF `1.0` is the stable core contract. Current benchmark results are promising, but they should be read with these boundaries:

* results are corpus-dependent;
* not every data shape benefits equally from tabular projection;
* editors and tools must preserve literal tabs in table rows;
* `.sdif.ai` is an agent projection surface, not the canonical signing surface;
* Claude and Llama3 token counting must be enabled separately before claiming results for those tokenizers.

## License

MIT. See [LICENSE](LICENSE).
