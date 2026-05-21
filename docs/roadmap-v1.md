# SDIF v1.0 Roadmap

This roadmap translates the `0.2.9-draft` specification into a bounded path toward a mature `v1.0.0` format release.

## Release principle

SDIF v1.0.0 must stabilize the core contract before expanding the ecosystem. The v1 release should freeze syntax, the normative AST, canonical bytes, schema-driven validation, safe defaults, `.sdif.ai` reversibility, and conformance evidence.

Remote includes, remote schemas, complex namespaces, deep graph validation, complete digital-signature workflows, advanced type unions, and non-declarative rule execution are important, but they should be treated as versioned extensions unless a release gate explicitly promotes them into the core. The remote includes policy must remain disabled by default unless explicitly enabled.

## Scope classes

### Core v1 blockers

These items affect compatibility, parser behavior, canonical hashes, validation semantics, or default safety:

- `@sdif 1.0` version semantics and migration notes from the draft line.
- Closed grammar for core documents, tables, relations, rules, narratives, directives, and `.sdif.ai` projection input.
- Normative AST and trivia model for source, canonical, and projection workflows.
- `canonical-syntax-v1` byte contract.
- Minimal schema language and schema-aware table ordering contract.
- Error taxonomy: parse error, validation error, and policy denial.
- Include and remote-resource safety defaults.
- Shared conformance fixtures for valid, invalid, canonical, policy-denied, and projection cases.

### Versioned extensions

These can ship after v1.0.0 without weakening the core release if the spec marks them as extensions:

- Remote includes with allowlists, digest pinning, cache rules, and network-disabled defaults.
- Remote schemas with the same remote-resource policy model.
- Complex namespaces beyond simple `@namespace prefix iri` declarations.
- Deep graph validation across relation closure and external vocabularies.
- Digital signatures as a complete embedded or detached verification workflow.
- Advanced type unions beyond the minimal schema language.
- Rule execution beyond declarative validation.
- Semantic canonicalization policies such as alias expansion, numeric normalization, date-time equivalence, and semantic merging.

## Milestones

### M1 — Spec freeze candidate

Goal: turn draft recommendations into normative release decisions.

Acceptance criteria:

- `docs/spec.md` defines `@sdif 1.0` separately from package versioning.
- The spec distinguishes core v1 requirements from extensions.
- Inline comments inside table rows are prohibited in strict mode.
- Table cell typing is defined as raw string capture followed by schema-driven typing.
- The `$` suffix in `.sdif.ai` table headers is defined as a string-preservation hint, not part of the semantic field name.
- `@include` is disabled by default and enabled only by explicit policy.
- `@namespace prefix iri` is the v1 namespace form; complex namespace behavior remains extension-only.
- Rule expressions have a normative AST shape for declarative validation.

### M2 — Canonicalization contract

Goal: freeze reproducible bytes for hashing and future signing.

Acceptance criteria:

- `canonical-syntax-v1` covers UTF-8, LF line endings, final newline, comment removal, directive ordering, metadata ordering, relation ordering, rule ordering, indentation, and literal `HTAB` table cells.
- Without a schema, table row order is preserved.
- With a schema and `ordered=true`, table row order is preserved.
- With a schema, `ordered=false`, and a declared `primary_key`, rows are sorted by primary-key value.
- With a schema and `ordered=false` but no declared `primary_key`, strict canonicalization reports a canonicalization error rather than guessing semantic order.
- Alias expansion, numeric normalization, date-time equivalence, equivalent list spelling, duplicate-field merging, and semantic merging remain future versioned policies unless separately promoted with golden fixtures.

### M3 — Schema and validation contract

Goal: make validation predictable without adding a large type system prematurely.

Acceptance criteria:

- The schema document shape is normative for v1.
- Required fields, table declarations, table ordering, primary keys, relations, and declarative rule functions are specified.
- Raw table cells remain strings until schema-driven typing is applied.
- Diagnostics are stable in both text and JSON output.
- Advanced type unions are documented as extension work unless the minimal v1 schema needs a tightly bounded union form.

### M4 — Security model

Goal: keep SDIF safe by default in local and agentic workflows.

Acceptance criteria:

- Parsers never execute code.
- Includes are Disabled by default.
- Local includes require an explicit allowlist.
- Remote includes and Remote schemas are disabled by default even when local includes are enabled.
- Include resolution rejects cycles.
- Policy limits cover document size, nesting depth, string length, table row count, include depth, total expanded bytes, and alias expansion.
- Policy denials are reported separately from parse and validation errors.

### M5 — `.sdif.ai` profile

Goal: promote `.sdif.ai` from preliminary projection helper to a formal derived profile.

Acceptance criteria:

- `.sdif.ai` is a derived agent projection, not the canonical signing surface by default.
- Reversibility means `canonicalize(sdif_from_ai(ai_view(source))) == canonicalize(source)` for supported constructs.
- Alias header syntax, ordering, scope, collision handling, and expansion limits are specified.
- Compact table rows may omit canonical indentation only when unambiguous and separated by literal `HTAB` cells.
- The `$` column suffix decodes scalar-like values as strings and is stripped from the semantic field name.
- Conformance includes `.sdif.ai` projection and reverse-projection fixtures.

### M6 — Conformance and release gate

Goal: make v1.0.0 evidence-backed rather than aspirational.

Acceptance criteria:

- Conformance fixtures cover valid documents, invalid documents, canonical equivalence, schema validation, policy denials, and `.sdif.ai` projection behavior.
- The reference Python implementation passes the v1 conformance suite.
- Tree-sitter fixtures stay aligned with shared conformance cases where syntax overlaps.
- Release notes list all extension work deferred beyond v1.0.0.
- The repository publishes the exact commands used to validate the release candidate.

## First implementation slice

Start with documentation and conformance guardrails:

1. Publish this roadmap and link it from the README.
2. Add repository tests that keep the roadmap discoverable.
3. Convert the most important open design recommendations into normative spec language in small pull-sized increments.
4. For each normative change, add or update focused conformance fixtures before changing parser or canonicalizer behavior.

This keeps the v1 path executable while avoiding a broad, risky redesign of parser, schema, canonicalization, includes, namespaces, and `.sdif.ai` in one pass.
