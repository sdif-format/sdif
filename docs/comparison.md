# JSON vs YAML vs TOON vs SDIF

## Summary

| Format | Strength | Weakness | SDIF position |
| --- | --- | --- | --- |
| JSON | Universal API interchange and simple data model | Verbose repeated keys; comments absent; canonicalization is external policy | SDIF keeps JSON-like structure but reduces repetition and adds semantic blocks |
| YAML | Human-friendly configuration | Large grammar, implicit typing surprises, many equivalent spellings | SDIF intentionally narrows syntax for deterministic parsing and canonicalization |
| TOON | Token-efficient object/table notation for LLM contexts | Primarily optimized for compact transfer, not semantic validation or canonical hashes | SDIF adopts table compactness but adds relations, rules, profiles, schemas, canonical bytes |
| SDIF | Semantic density, tabular compaction, relationships, declarative rules, canonicalization | New ecosystem; narrower MVP; requires SDIF-aware tooling | Best fit for auditable semantic documents and AI-agent exchange |

## Repeated records

JSON repeats keys for every row:

```json
[
  {"id":"R1","status":"done","gate":"syntax"},
  {"id":"R2","status":"pending","gate":"schema"}
]
```

YAML is easier to read but still repeats keys:

```yaml
- id: R1
  status: done
  gate: syntax
- id: R2
  status: pending
  gate: schema
```

TOON compacts repeated object keys by declaring a tabular shape for LLM transfer:

```toon
[2]{id,status,gate}:
  R1,done,syntax
  R2,pending,schema
```

SDIF uses a table shape once, then literal `HTAB` separated cells, and the same document can also include relations, rules, schemas, and canonical hashes:

```sdif
milestones[id,status,gate]:
  R1	done	syntax
  R2	pending	schema
```

## Semantic relationships

JSON/YAML can encode relationships, but they do not reserve a compact semantic relation block. SDIF does:

```sdif
rel:
  R2 depends_on R1
  validation.report.v2 validates release.v2.validation_plan
```

## Canonicalization

SDIF treats canonicalization as core behavior rather than an afterthought:

1. Remove comments and redundant blank lines.
2. Normalize line endings to LF.
3. Emit deterministic directives and statements.
4. Hash the canonical bytes with SHA-256.

## When not to use SDIF

Use JSON for public APIs that already require JSON. Use YAML/TOML for simple local configuration where canonical hashes, semantic relations, and compact repeated records do not matter. Use CSV/TSV for plain flat tables.
