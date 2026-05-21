# SDIF canonicalization contract

SDIF canonicalization turns source text into deterministic UTF-8 bytes suitable for hashing, fixture comparison, and future signing workflows.

The current implementation is an MVP canonical serializer, not a full semantic normalizer. It intentionally makes stable syntax-level choices while leaving deeper semantic equivalence rules for a later versioned contract.

## Pipeline

```text
source.sdif -> parser -> source-independent AST -> canonical SDIF bytes -> sha256
```

Comments, blank lines, and source-only trivia are not part of the canonical AST.

## Implemented rules

The `canonical-syntax-v1` contract is the syntax-level canonical byte contract for the v1 stabilization track. It does not claim semantic equivalence beyond the rules listed here.

The MVP canonicalizer currently:

1. Normalizes input line endings to LF through the parser.
2. Emits UTF-8 text with LF line endings.
3. Emits a final trailing newline.
4. Removes source comments and blank source-only trivia.
5. Emits directives in deterministic reserved-directive order.
6. Emits common metadata fields before other top-level statements.
7. Emits two-space indentation for child blocks.
8. Emits table rows with literal `HTAB` separators.
9. Sorts relations by `(subject, predicate, object)`.
10. Sorts rules by source expression.
11. Sorts schema-declared unordered table rows by `primary_key` when a schema is provided.
12. Normalizes nested narrative indentation by stripping the opening line's indentation prefix from body lines.
13. Computes SHA-256 over the canonical UTF-8 bytes.

## Format Version Contract

The `@sdif 0.1` format version header represents the syntax and semantic contract of the format. This contract is independent of the library implementation version (e.g. Python package version `1.0.0`).

## Schema-aware policies

Canonicalization can run without a schema. In that mode, table row order is preserved because the tool cannot know whether order is semantically meaningful.

Without a schema, table row order is preserved.

With a schema and `ordered=true`, table row order is preserved.

When a schema is provided, table policies from `tables[name,ordered,primary_key]` are used:

```sdif
@sdif 0.1
kind Schema
tables[name,ordered,primary_key]:
  milestones	false	id
```

With a schema, `ordered=false`, and a declared `primary_key`, rows are sorted by primary-key value.

With a schema and `ordered=false` but no declared `primary_key`, strict canonicalization reports a canonicalization error rather than guessing semantic order.

CLI usage:

```bash
sdif canon examples/plan.sdif --schema examples/schema.sdif
sdif hash examples/plan.sdif --schema examples/schema.sdif
```

The `--schema` option must point to a schema document whose top-level kind is `Schema`. The same guard is enforced by `Schema.from_document()`, so CLI validation and programmatic schema loading reject non-schema documents consistently.
Do not pass `canonical.sdif` as schema; golden canonical files are expected outputs, not schema inputs.

## Golden fixtures

Repository golden fixtures live under `examples/golden/<fixture>/`:

```text
source.sdif         source fixture
canonical.sdif      expected canonical bytes
canonical.sha256    SHA-256 of canonical.sdif
equivalent.json     comparison projection, not a canonical source
equivalent.yaml     comparison projection, not a canonical source
equivalent.toon     comparison projection, not a canonical source
```

Tests assert that each `source.sdif` canonicalizes to `canonical.sdif`, and that `canonical.sha256` matches SHA-256 over those exact bytes.

## Explicit non-goals for v0.1 MVP

The MVP canonicalizer does not yet perform full semantic normalization. In particular, it does not yet normalize:

- numeric representations such as `1.0` versus `1.00`;
- date-time zones such as `Z` versus `+00:00`;
- aliases or vocabulary expansion;
- equivalent list spellings;
- duplicate fields or duplicate tables as canonical merge operations;
- JSON/YAML/TOON projections as canonical inputs.

Those rules should be added only with explicit versioning, fixtures, and migration notes.
