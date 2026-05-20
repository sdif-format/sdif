# SDIF canonicalization contract

SDIF canonicalization turns source text into deterministic UTF-8 bytes suitable for hashing, fixture comparison, and future signing workflows.

The current implementation is an MVP canonical serializer, not a full semantic normalizer. It intentionally makes stable syntax-level choices while leaving deeper semantic equivalence rules for a later versioned contract.

## Pipeline

```text
source.sdif -> parser -> source-independent AST -> canonical SDIF bytes -> sha256
```

Comments, blank lines, and source-only trivia are not part of the canonical AST.

## Implemented rules

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
12. Computes SHA-256 over the canonical UTF-8 bytes.

## Schema-aware policies

Canonicalization can run without a schema. In that mode, table row order is preserved because the tool cannot know whether order is semantically meaningful.

When a schema is provided, table policies from `tables[name,ordered,primary_key]` are used:

```sdif
@sdif 0.1
kind Schema
tables[name,ordered,primary_key]:
  milestones	false	id
```

For tables where `ordered` is `false` and `primary_key` names an existing column, rows are sorted by the primary-key column.

CLI usage:

```bash
sdif canon examples/plan.sdif --schema examples/schema.sdif
sdif hash examples/plan.sdif --schema examples/schema.sdif
```

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
