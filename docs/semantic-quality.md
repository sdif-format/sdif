# Semantic quality comparison

`sdif-benchmarks/scripts/token_efficiency.py` measures transport density: bytes, estimated
tokens, and tokenizer-specific token counts. Semantic quality is a separate
question: how much intent, relationship structure, typing, validation policy,
and auditability survive when the same document is represented in another
format.

This page defines the repo-local methodology for comparing SDIF and SDIF AI
against JSON, YAML, and CSV without changing the token benchmark.

Executable guard:

```bash
cd sdif-benchmarks && python3 scripts/check_semantic_quality.py
```

The guard checks the SDIF example set against the axes below using parser,
conversion, validation, SDIF AI projection, and canonicalization behavior.

## Evaluation axes

| Axis | What it measures | SDIF signal | JSON/YAML/CSV comparison |
| --- | --- | --- | --- |
| relational expressivity | Whether relationships are first-class instead of an invented convention | Native `rel:` rows such as `R2 depends_on R1` | JSON/YAML need a convention such as `{subject,predicate,object}`; CSV needs a bridge table |
| round-trip fidelity | Whether conversion preserves the same semantic data | `sdif to-json` plus `sdif from-json` and golden fixture tests | JSON can preserve the data but repeats table keys; CSV cannot preserve hierarchy without a bundle convention |
| schema validation | Whether the format can carry enforceable business semantics | `sdif validate` checks fields, enums, table columns, and relation typing | JSON needs external JSON Schema; YAML inherits the same issue; CSV needs external tooling |
| SDIF AI semantic retention | Whether compact aliases and projection rules keep functional meaning | `.sdif.ai` keeps tables, relations, and explicit alias headers when useful | The compact surface is less human-readable but remains parseable and reversible for supported constructs |
| canonicalization | Whether equal semantics produce deterministic bytes for hashing/signing | `sdif canon` and `sdif hash` are core commands | JSON/YAML need separate canonicalization profiles; CSV bundles need extra ordering and escaping policy |

## 1. Relational expressivity

Use `examples/plan.sdif` and inspect the relation block:

```bash
sed -n '/^rel:/,/^rules:/p' examples/plan.sdif
```

SDIF carries graph edges as a native primitive:

```sdif
rel:
  R2 depends_on R1
```

In JSON or YAML, the same edge is not a primitive of the format. A producer must
choose an application convention, usually an array of edge objects. In CSV, the
edge normally becomes a separate relation table. Those encodings can work, but
the semantic quality is lower because the graph meaning lives in an external
agreement rather than the base syntax.

## 2. Round-trip fidelity

Run the supported conversion path:

```bash
sdif to-json examples/plan.sdif > /tmp/plan.json
sdif from-json /tmp/plan.json > /tmp/plan_recreated.sdif
sdif canon /tmp/plan_recreated.sdif
```

The golden fixture guard is `tests/test_json_golden_equivalence.py`. It proves
that checked-in SDIF fixtures can map to JSON-compatible data and back without
changing the supported semantic data. The comparison result is intentionally not
"JSON loses everything"; rather, JSON preserves the tree data but needs more
ceremony for repeated records and relation conventions.

## 3. Schema validation

Run the validator:

```bash
sdif validate examples/plan.sdif --schema examples/schema.sdif
```

The validation tests in `tests/test_validation.py` cover required fields, enum
membership, table shape, and relation typing. This is a core semantic-quality
advantage over plain CSV and ad hoc YAML/JSON because the SDIF document model is
built to be checked by an SDIF schema instead of relying on unrelated application
code.

## 4. SDIF AI semantic retention

Generate the compact agent projection:

```bash
sdif ai examples/plan.sdif --alias kind=k --alias status=st
```

SDIF AI intentionally trades some human readability for lower context cost. The
quality question is not whether `k` is nicer than `kind`; it is whether the
projection still exposes the same functional structure to an agent: tables,
relation blocks, rule blocks, and any alias header required to decode compact
names. For supported constructs, SDIF AI should remain parseable and should not
require JSON as the agent-facing surface.

## 5. Canonicalization and auditability

Run:

```bash
sdif canon examples/plan.sdif
sdif hash examples/plan.sdif
```

Canonicalization is part of SDIF's machine semantics. Two source files that are
accepted as the same SDIF document should normalize to stable bytes before
hashing or signing. JSON, YAML, and CSV can be canonicalized, but their base
formats do not make this repo-local canonicalization contract the default.

## Suggested scoring

Use a simple 0-2 rubric for each axis when comparing formats:

- `0`: not representable without external application convention.
- `1`: representable, but semantics are convention-heavy or not directly
  validated by the format/tooling.
- `2`: represented as a first-class or repo-validated construct.

This keeps semantic quality separate from token density. A format can be compact
but semantically weak, or verbose but semantically faithful.
