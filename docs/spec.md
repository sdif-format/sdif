# SDIF — Semantic Data Interchange Format

## Document status

**Version:** 0.2.3-draft
**Name:** Semantic Data Interchange Format
**Short name:** SDIF
**Recommended source extension:** `.sdif`
**Recommended canonical extension:** `.sdif.canon`
**Recommended AI-optimized extension:** `.sdif.ai`
**Proposed MIME type:** `application/sdif`
**Encoding:** UTF-8
**Design mode:** schema-first, semantic-first, token-aware, canonicalization-ready

This document defines an initial public technical specification for SDIF, a compact semantic data interchange format designed for humans, machines, and AI agents.

SDIF is not intended to universally replace JSON, YAML, TOML, CSV, Markdown, RDF, or other data formats. Its purpose is narrower: to represent structured, semantic, verifiable, and token-efficient documents in a way that remains readable by humans and deterministic for machines.

---

## 1. Executive summary

SDIF is a textual format for representing structured data, semantic relationships, declarative rules, validation evidence, and bounded narrative context.

It combines several ideas:

* The strict structural model of JSON.
* The readability of YAML and TOML.
* The tabular compactness of CSV and token-efficient formats.
* The graph-like expressiveness of semantic triples.
* The bounded narrative capability of Markdown-style text blocks.
* The determinism required for canonicalization, hashing, signing, and reproducible validation.

The primary goal of SDIF is to maximize **semantic density per token** without sacrificing clarity, validation, or safety.

A compact summary:

```text
SDIF = structured data + compact tables + semantic relations + declarative rules + canonical form
```

---

## 2. Goals

SDIF should:

1. Be readable by humans.
2. Be efficient for AI models to process.
3. Be deterministic to parse.
4. Be validatable through schemas.
5. Be canonicalizable.
6. Support stable hashing and signing.
7. Represent scalar data, objects, lists, tables, relations, rules, and narrative blocks.
8. Avoid unnecessary repetition, especially in uniform arrays of objects.
9. Support both human-authored source files and machine-normalized canonical files.
10. Remain implementation-friendly and portable.

---

## 3. Non-goals

SDIF does not aim to:

1. Become a general-purpose programming language.
2. Execute arbitrary code.
3. Replace SQL.
4. Replace full RDF or OWL.
5. Replace Markdown for long-form prose.
6. Replace JSON for existing public APIs where JSON is already the expected contract.
7. Allow highly flexible syntax at the cost of ambiguity.
8. Optimize aesthetics over deterministic processing.
9. Be tied to a specific product, operating system, vendor, or project.
10. Be exclusively an AI-only format.

---

## 4. Design principles

### 4.1 Semantic density per token

SDIF should avoid verbose patterns when a more compact representation preserves the same meaning.

Verbose representation:

```json
[
  { "id": "R1", "status": "done", "gate": "verify" },
  { "id": "R2", "status": "pending", "gate": "verify" }
]
```

SDIF representation:

```sdif
milestones[id,status,gate]:
  R1	done	verify
  R2	pending	verify
```

The table header defines the shape once. Each row then carries only values. Table columns are separated by the horizontal tab character (`HTAB`, U+0009), not by comma or ordinary space.

This avoids conflicts with natural-language text, localized decimal notation, quoted phrases, and comma-rich content.

### 4.2 Schema-first

Every serious SDIF document should declare a schema.

```sdif
schema example.plan.v1
```

A parser may read SDIF without a schema, but a validator should not treat an unschematized document as fully reliable.

### 4.3 Semantics over shape

SDIF does not only describe data shape. It can also describe meaning.

```sdif
rel:
  release.v2 depends_on release.v1
  release.v2 validated_by validation.report.v2
```

Relationships are first-class citizens of the format.

### 4.4 Canonicalizable by design

Every valid SDIF document should be convertible into a unique canonical representation.

The canonical form removes comments, stylistic variation, non-essential whitespace, ambiguous ordering, and syntactic sugar.

### 4.5 Human source, machine truth

The `.sdif` profile is intended for human authorship. The `.sdif.canon` profile is intended for reproducible validation, hashing, signing, and machine comparison.

### 4.6 AI views are projections, not authority

The `.sdif.ai` profile may use stronger compaction and aliases to reduce token cost, but it should be treated as a derived view unless explicitly signed as an artifact in its own right.

### 4.7 No hidden magic

Aliases, relation predicates, rule functions, required fields, lifecycle states, and validation behavior must be defined by a schema, vocabulary, or local declaration.

### 4.8 Safe by default

SDIF must not execute code. Declarative rules describe validation conditions or policies, not arbitrary procedures.

---

## 5. Main use cases

SDIF is suitable for:

1. Semantic registries.
2. Structured technical plans.
3. Policy documents.
4. Interface contracts.
5. Validation reports.
6. Evidence manifests.
7. Decision records.
8. Capability manifests.
9. Knowledge indexes.
10. Agent-to-agent data exchange.
11. Compact representation of repeated structured data.
12. Auditable metadata catalogs.
13. Governance-ready configuration.
14. Documentation indexes.
15. Hybrid data/prose technical documents.

SDIF is not ideal for:

1. Large binary blobs.
2. Very large numerical datasets.
3. High-frequency telemetry streams.
4. Long literary documents.
5. Extremely simple configuration where TOML or JSON is enough.
6. Public API contracts that already require JSON compatibility.

---

## 6. Format profiles

SDIF defines three primary profiles.

### 6.1 SDIF Source

Recommended extension:

```text
.sdif
```

The source profile is optimized for human authorship.

It may include:

* Comments.
* Blank lines.
* Reasonable ordering flexibility.
* Narrative blocks.
* Declared aliases.
* Tables.
* Relations.
* Declarative rules.

Example:

```sdif
@sdif 0.1
kind Plan
id release.v2.plan
schema example.plan.v1

# Human-readable title.
title "Release v2 validation plan"
status open
priority P0
```

### 6.2 SDIF Canonical

Recommended extension:

```text
.sdif.canon
```

The canonical profile is optimized for machines.

It must be:

* Comment-free.
* Deterministically ordered.
* Normalized for whitespace and line endings.
* Normalized for scalar representation.
* Suitable for hashing.
* Suitable for signing.
* Suitable for byte-for-byte comparison.

### 6.3 SDIF AI View

Recommended extension:

```text
.sdif.ai
```

The AI view is optimized for compact model input.

It may include:

* Declared aliases.
* More compact field names.
* Omitted fields when schema defaults are known.
* Table-first representation.
* Ordering optimized for incremental understanding.

Example:

```sdif
@sdif.ai 0.1
alias[k=kind,a=authority,l=lifecycle,st=status,vby=validated_by]

k Plan
id release.v2
a Canonical
l Active
st open

m[id,st,g,e]:
  R1	done	validate-schema	reports/schema.md
  R2	pending	validate-semantics	reports/semantics.md
```

The AI view should normally be generated from source or canonical SDIF, not manually treated as the authoritative source.

---

## 7. Core data model

An SDIF document is composed of:

1. Directives.
2. Scalar fields.
3. Objects.
4. Lists.
5. Tables.
6. Relations.
7. Declarative rules.
8. Narrative blocks.
9. Comments.

### 7.1 Document

An SDIF document is an ordered sequence of statements.

A statement may be:

* A directive.
* A scalar field.
* An object block.
* A table block.
* A relation block.
* A rule block.
* A narrative block.
* A comment.

### 7.2 Directives

Directives begin with `@`.

```sdif
@sdif 0.1
@profile source
@vocab example.core.v1
```

Initial reserved directives:

| Directive    | Meaning                                                     |
| ------------ | ----------------------------------------------------------- |
| `@sdif`      | Declares the SDIF format version.                           |
| `@profile`   | Declares the document profile.                              |
| `@vocab`     | Declares a vocabulary.                                      |
| `@base`      | Declares a base URI or semantic namespace.                  |
| `@namespace` | Declares a namespace prefix.                                |
| `@include`   | Includes another local document or vocabulary if permitted. |

The `@include` directive must be disabled by default in secure validators or restricted through an explicit allowlist.

### 7.3 Scalar fields

A scalar field has the form:

```sdif
key value
```

Examples:

```sdif
status open
priority P0
created_at 2026-05-20T18:00:00Z
active true
```

### 7.4 Objects

Objects use indentation.

```sdif
owner:
  id team.platform
  role maintainer
  authority Canonical
```

### 7.5 Lists

Inline list:

```sdif
tags [registry,validation,release]
```

Block list:

```sdif
tags:
  - registry
  - validation
  - release
```

The canonical form must choose one deterministic representation.

### 7.6 Tables

Tables represent uniform arrays of objects.

```sdif
items[id,name,status]:
  item.1	First item	open
  item.2	Second item	closed
```

This is semantically equivalent to:

```json
{
  "items": [
    { "id": "item.1", "name": "First item", "status": "open" },
    { "id": "item.2", "name": "Second item", "status": "closed" }
  ]
}
```

Tables are central to SDIF's token efficiency.

Table rows use `HTAB` as the column separator. Spaces, commas, quote marks, and localized decimal separators are data, not delimiters.

```sdif
budget[id,item,cost,tax_rate]:
  IT01	server load	450,25	21,0
  IT02	api calls	120,00	10,5
  IT03	storage fees	85,50	21,0
```

In strict mode, a tab inside a cell must be escaped as `\t` or represented through a narrative block or external reference.

### 7.7 Relations

Relations are expressed as triples:

```sdif
rel:
  subject predicate object
```

Example:

```sdif
rel:
  release.v2 depends_on release.v1
  release.v2 validated_by validation.report.v2
  validation.report.v2 emits reports/validation.md
```

A predicate must be allowed by the declared schema or vocabulary.

### 7.8 Declarative rules

Rules use compact parenthesized expressions.

```sdif
rules:
  (deny missing(evidence))
  (deny dangling(rel))
  (warn eq(authority,Unknown))
```

Rules are not executable code. They are declarative expressions interpreted by a validator with an explicit allowlist of rule functions.

### 7.9 Narrative blocks

Narrative blocks use triple quotes.

```sdif
intent """
Define the validation requirements for the next release.
The document should remain auditable and reproducible.
"""
```

Narrative blocks are useful for intent, rationale, notes, acceptance criteria, and other bounded human context.

### 7.10 Comments

Comments begin with `#`.

```sdif
# Source-only comment.
status open
```

Comments are allowed in SDIF Source but must be removed from SDIF Canonical.

---

## 8. Type system

SDIF should support these base types:

| Type       | Example                    |
| ---------- | -------------------------- |
| Null       | `null`                     |
| Boolean    | `true`, `false`            |
| Integer    | `42`                       |
| Decimal    | `10.75`                    |
| String     | `"hello world"`            |
| Identifier | `release.v2`               |
| Path       | `reports/validation.md`    |
| Date       | `2026-05-20`               |
| DateTime   | `2026-05-20T18:30:00Z`     |
| Duration   | `PT15M`                    |
| List       | `[a,b,c]`                  |
| Object     | indented block             |
| Table      | `items[id,name]:`          |
| Relation   | `subject predicate object` |
| Expression | `(deny missing(evidence))` |

### 8.1 Boolean

Only the following boolean literals are allowed:

```sdif
true
false
```

Values such as `yes`, `no`, `on`, `off`, `1`, and `0` must not be treated as booleans in the core format.

### 8.2 Numbers

Integers:

```sdif
count 42
```

Decimals:

```sdif
amount 10.75
```

Scientific notation:

```sdif
ratio 1.2e-5
```

Canonicalization must normalize numeric representation.

### 8.3 Strings

Outside tables, a value may be unquoted only if it is a safe identifier, reserved literal, number, date, datetime, duration, or list.

Strings with spaces or special characters must be quoted in scalar fields.

```sdif
status open
title "Release v2 validation plan"
label "Revenue, monthly"
```

Inside table cells, spaces, commas, quote marks, and localized decimal commas are part of the cell value because columns are separated by `HTAB`.

```sdif
items[id,label,amount]:
  item.1	Revenue, monthly	450,25
  item.2	"quoted label"	120,00
```

A table cell only requires escaping when it must contain the actual tab character, a line break, or another control character reserved by the table grammar.

Multiline strings use triple quotes outside tables.

```sdif
summary """
This is a multiline narrative block.
Line breaks are preserved.
"""
```

### 8.4 Identifiers

A safe identifier may contain:

* ASCII letters.
* Digits.
* `_`.
* `-`.
* `.`.
* `/` for controlled paths.
* `:` only when permitted by schema or namespace policy.

Examples:

```sdif
id release.v2.plan
schema example.plan.v1
path reports/validation/latest.md
```

### 8.5 Dates and times

Dates use ISO-style format:

```sdif
date 2026-05-20
```

Date-time values use ISO 8601 style:

```sdif
created_at 2026-05-20T18:30:00Z
```

Durations should use ISO 8601 duration notation:

```sdif
timeout PT30S
retention P90D
```

---

## 9. Lexical rules

### 9.1 Encoding

All SDIF documents must be UTF-8 encoded.

A UTF-8 BOM may be accepted in tolerant mode, but it must be removed in canonical form.

### 9.2 Line endings

Parsers may accept LF or CRLF.

Canonical SDIF must use LF.

### 9.3 Whitespace

The recommended indentation is two spaces.

Tabs must not be used for indentation in strict mode.

The horizontal tab character (`HTAB`, U+0009) is reserved as the column separator inside table rows.

This produces a simple rule:

1. Spaces define indentation and may appear inside table cell values.
2. Tabs separate table columns.
3. Tabs do not indent SDIF blocks.

### 9.4 Comments

A comment begins with `#` outside strings and multiline blocks.

```sdif
# comment
status open # inline comment
```

Inline comments are allowed in source, but they may be prohibited inside tables for parser simplicity and canonical stability.

### 9.5 Reserved literals

Initial reserved literals:

```text
null
true
false
rel
rules
alias
schema
kind
id
```

Reserved words may be used as values when unambiguous, but their use as keys may be restricted by schema.

---

## 10. Normative MVP decisions

This section closes several design questions for the 0.1 MVP.

### 10.1 Table separator

The MVP uses the horizontal tab character (`HTAB`, U+0009) as the table column separator.

```sdif
items[id,status,owner]:
  item.1	open	team.platform
  item.2	closed	team.platform
```

Reasons:

1. It avoids conflicts with natural-language spaces.
2. It avoids conflicts with comma-rich text.
3. It avoids conflicts with localized decimal commas such as `10,75`.
4. It makes parsing table rows simple and deterministic.
5. It preserves unquoted human-readable text inside cells.
6. It keeps the table model close to TSV, a proven interchange pattern.

A table cell may contain spaces, commas, quotes, slashes, colons, and localized decimal notation without quoting.

```sdif
budget[id,item,cost,tax_rate]:
  IT01	server load	450,25	21,0
  IT02	api calls	120,00	10,5
  IT03	storage fees	85,50	21,0
```

A literal tab inside a cell must be escaped as `\t` in strict mode.

Tabs are reserved for table separation only. They must not be used for indentation.

### 10.2 Rule syntax

The MVP uses parenthesized expressions.

```sdif
rules:
  (deny missing(evidence))
  (warn eq(authority,Unknown))
```

Reasons:

1. Deterministic parsing.
2. Explicit arity.
3. Clear nesting.
4. Direct AST conversion.
5. Lower ambiguity than whitespace-only rule syntax.

### 10.3 Unquoted strings

The MVP follows two related policies.

Outside tables:

```text
safe identifier or quoted string
```

A scalar value must be quoted if it contains:

1. Spaces.
2. Commas that are intended as text.
3. Parentheses.
4. Brackets.
5. Quotes.
6. Comment markers.
7. Characters outside the safe identifier rule.

Valid scalar examples:

```sdif
status open
path reports/validation/latest.md
title "Release v2 validation plan"
label "Revenue, monthly"
```

Inside tables, cells are separated by `HTAB`, so ordinary spaces and commas are allowed as raw cell content.

Valid table example:

```sdif
items[id,label,amount]:
  item.1	Release v2 validation plan	450,25
  item.2	Revenue, monthly	120,00
```

A table cell must only escape a literal tab, a line break, or a reserved control character.

### 10.4 Normative parser before editor tooling

A Tree-sitter grammar is valuable for editor support, syntax highlighting, and incremental parsing, but it should not be the normative parser for the initial specification.

The MVP should define first:

1. Normative lexer.
2. Normative parser.
3. Normative AST.
4. Canonical serializer.
5. Round-trip fixtures.

Tree-sitter support may follow and should be validated against the official fixtures.

### 10.5 Canonicalizer from the first implementation slice

The canonicalizer is not a later enhancement. It is part of the first useful SDIF implementation.

Minimum pipeline:

```text
source.sdif -> AST -> canonical AST -> source.sdif.canon -> hash
```

The first milestone is not full semantic validation. The first milestone is stable canonical bytes.

---

## 11. Core grammar — EBNF draft

This section defines a practical draft grammar for the SDIF core. It is intended to support the MVP parser, AST, canonicalizer, and basic validator.

### 11.1 Notation

```text
*  zero or more
+  one or more
?  optional
|  alternative
```

Lexical tokens such as `IDENT`, `STRING`, `NUMBER`, and `DATETIME` are defined below.

### 11.2 Document

```ebnf
document        = spacing, statement*, EOF ;

statement       = blank_line
                | comment_line
                | directive_line
                | field_line
                | object_block
                | table_block
                | relation_block
                | rule_block
                | narrative_block
                ;
```

### 11.3 Base lines

```ebnf
blank_line       = horizontal_space*, newline ;
comment_line     = horizontal_space*, comment, newline ;
comment          = "#", not_newline* ;

newline          = "\n" | "\r\n" ;
horizontal_space = " " | "\t" ;
spacing          = (blank_line | comment_line)* ;
```

In strict mode, tabs must not be accepted as indentation.

### 11.4 Directives

```ebnf
directive_line  = "@", directive_name, directive_args?, inline_comment?, newline ;

directive_name  = IDENT ;
directive_args  = horizontal_space+, value, (horizontal_space+, value)* ;
```

Examples:

```sdif
@sdif 0.1
@profile source
@vocab example.core.v1
```

### 11.5 Scalar fields

```ebnf
field_line      = key, horizontal_space+, value, inline_comment?, newline ;
key             = IDENT ;
```

Examples:

```sdif
kind Plan
id release.v2.plan
schema example.plan.v1
status open
priority P0
```

### 11.6 Objects

```ebnf
object_block       = key, ":", inline_comment?, newline,
                     indented_statement+ ;

indented_statement = INDENT, statement_body, DEDENT? ;
statement_body     = field_line
                   | object_block
                   | table_block
                   | relation_block
                   | rule_block
                   | narrative_block
                   | comment_line
                   | blank_line
                   ;
```

`INDENT` and `DEDENT` may be synthetic tokens generated by the lexer.

### 11.7 Inline lists

```ebnf
list            = "[", list_items?, "]" ;
list_items      = value, (",", value)* ;
```

Example:

```sdif
tags [registry,validation,release]
```

### 11.8 Tables

```ebnf
table_block     = table_header, table_row+ ;

table_header    = key, "[", column_list, "]", ":", inline_comment?, newline ;
column_list     = IDENT, (",", IDENT)* ;

table_row       = INDENT, table_cell, (HTAB, table_cell)*, inline_comment?, newline ;
table_cell      = table_cell_char* ;
table_cell_char = any_char_except_htab_or_newline ;
HTAB            = ? U+0009 horizontal tab ? ;
```

Required semantic rules:

1. Each row must contain exactly the same number of cells as the table header declares.
2. `HTAB` is the only column separator in table rows.
3. Ordinary spaces inside cells are preserved as data.
4. Commas inside cells are preserved as data.
5. Quote marks inside cells are preserved as data unless an implementation chooses to support optional quoted-cell decoding.
6. A literal tab inside a cell must be escaped as `\t` in strict mode.
7. Empty cells must be rejected in strict mode unless the schema explicitly allows them.
8. Multiline blocks are not valid inside tables in the MVP.
9. Inline comments inside tables may be prohibited in strict mode.

Example:

```sdif
milestones[id,status,gate,evidence]:
  R1	done	validate-syntax	reports/syntax.md
  R2	pending	validate-schema	reports/schema.md
```

### 11.9 Relations

```ebnf
relation_block  = "rel", ":", inline_comment?, newline, relation_row+ ;
relation_row    = INDENT, relation_subject, horizontal_space+, relation_predicate,
                  horizontal_space+, relation_object, inline_comment?, newline ;

relation_subject   = IDENTIFIER_VALUE ;
relation_predicate = IDENTIFIER_VALUE ;
relation_object    = IDENTIFIER_VALUE | STRING ;
```

Example:

```sdif
rel:
  release.v2 depends_on release.v1
  release.v2 validated_by validation.report.v2
```

In the MVP, a relation has exactly three parts: subject, predicate, and object.

### 11.10 Rules

```ebnf
rule_block      = "rules", ":", inline_comment?, newline, rule_row+ ;
rule_row        = INDENT, expression, inline_comment?, newline ;

expression      = "(", function_name, expression_arg*, ")" ;
function_name   = IDENT ;
expression_arg  = horizontal_space+, (value | expression) ;
```

Examples:

```sdif
rules:
  (deny missing(evidence))
  (warn eq(authority,Unknown))
  (deny all(missing(schema) missing(kind)))
```

`missing(evidence)` may be treated as compact call syntax and normalized in the AST.

Recommended internal representation:

```text
Call(name="deny", args=[Call(name="missing", args=[Identifier("evidence")])])
```

### 11.11 Narrative blocks

```ebnf
narrative_block   = key, horizontal_space+, multiline_string, inline_comment?, newline? ;
multiline_string  = "\"\"\"", multiline_content, "\"\"\"" ;
multiline_content = any_char_until_triple_quote* ;
```

Example:

```sdif
intent """
Define validation requirements for the next release.
Preserve reproducibility and auditability.
"""
```

### 11.12 Values

```ebnf
value           = null
                | boolean
                | datetime
                | date
                | duration
                | number
                | string
                | list
                | identifier_value
                ;

scalar_value    = null
                | boolean
                | datetime
                | date
                | duration
                | number
                | string
                | identifier_value
                ;

null            = "null" ;
boolean         = "true" | "false" ;
```

### 11.13 Lexical tokens

```ebnf
IDENT           = IDENT_START, IDENT_CONT* ;
IDENT_START     = "A".."Z" | "a".."z" | "_" ;
IDENT_CONT      = IDENT_START | "0".."9" | "-" ;

identifier_value = IDENTIFIER_CHAR+ ;
IDENTIFIER_CHAR  = "A".."Z"
                 | "a".."z"
                 | "0".."9"
                 | "_"
                 | "-"
                 | "."
                 | "/"
                 | ":"
                 ;

number          = integer | decimal | scientific ;
integer         = sign?, digit+ ;
decimal         = sign?, digit+, ".", digit+ ;
scientific      = sign?, digit+, ("." digit+)?, ("e" | "E"), sign?, digit+ ;
sign            = "+" | "-" ;
digit           = "0".."9" ;

string          = quoted_string ;
quoted_string   = "\"", quoted_char*, "\"" ;
quoted_char     = escaped_char | normal_string_char ;
escaped_char    = "\\", ("\\" | "\"" | "n" | "r" | "t" | "u", hex, hex, hex, hex) ;

normal_string_char = any_char_except_quote_backslash_newline ;

inline_comment  = horizontal_space+, "#", not_newline* ;
```

### 11.14 Dates, times, and durations

```ebnf
date            = digit, digit, digit, digit, "-", digit, digit, "-", digit, digit ;

datetime        = date, "T", digit, digit, ":", digit, digit, ":", digit, digit,
                  fractional_seconds?, timezone ;

fractional_seconds = ".", digit+ ;
timezone        = "Z" | sign, digit, digit, ":", digit, digit ;

duration        = "P", duration_body ;
duration_body   = IDENTIFIER_CHAR+ ;
```

The grammar recognizes shape. Semantic validation should verify actual calendar validity.

### 11.15 Type precedence

When an unquoted token could match multiple types, the following precedence applies:

1. `null`
2. boolean
3. datetime
4. date
5. duration
6. number
7. identifier value

Example:

```sdif
value 2026-05-20
```

This is a date.

```sdif
value "2026-05-20"
```

This is a string.

---

## 12. Minimum normative AST

The MVP implementation should produce an AST independent from the original text.

### 12.1 Document

```text
Document
  format_version: Version
  directives: Directive[]
  statements: Statement[]
  diagnostics: Diagnostic[]
```

### 12.2 Statements

```text
Statement
  Field(Field)
  Object(Object)
  Table(Table)
  RelationBlock(Relation[])
  RuleBlock(Expression[])
  Narrative(Narrative)
```

Comments may exist in a source-preserving AST, but they must not be part of the canonical AST.

### 12.3 Values

```text
Value
  Null
  Boolean(bool)
  Integer(i64)
  Decimal(string)
  String(string)
  Identifier(string)
  Date(string)
  DateTime(string)
  Duration(string)
  List(Vec<Value>)
```

Decimals should be represented as normalized strings or exact decimal values, not binary floating-point values.

### 12.4 Tables

```text
Table
  name: Identifier
  columns: Vec<Identifier>
  rows: Vec<TableRow>

TableRow
  cells: Vec<Value>
```

### 12.5 Relations

```text
Relation
  subject: Identifier
  predicate: Identifier
  object: RelationObject

RelationObject
  Identifier(string)
  String(string)
```

### 12.6 Expressions

```text
Expression
  Call { name: Identifier, args: Vec<ExpressionArg> }

ExpressionArg
  Value(Value)
  Call(Expression)
```

---

## 13. Schemas

An SDIF schema defines the expected shape and semantics of a document.

### 13.1 Schema responsibilities

A schema should define:

1. Allowed kinds.
2. Required fields.
3. Optional fields.
4. Field types.
5. Defaults.
6. Enumerations.
7. Allowed tables.
8. Required columns.
9. Allowed relation predicates.
10. Allowed rule functions.
11. Allowed aliases.
12. Whether order is semantically significant.
13. Canonicalization policy.

### 13.2 Minimal schema example

A schema may itself be written in SDIF.

```sdif
@sdif 0.1
kind Schema
id example.plan.v1
schema sdif.schema.v1
authority Canonical
lifecycle Active

for_kind Plan

fields[name,type,required,default]:
  kind	Enum(Plan)	true	null
  id	Identifier	true	null
  schema	Identifier	true	null
  authority	Enum(Canonical,Reference,Working,Derived,External,Unknown)	false	Unknown
  lifecycle	Enum(Draft,Active,Deprecated,Superseded,Archived,Quarantined)	false	Draft
  title	String	true	null
  status	Enum(open,closed,blocked)	true	open
  priority	Enum(P0,P1,P2,P3)	false	P2

tables[name,ordered,primary_key]:
  milestones	true	id
  scope	false	in

columns[table,name,type,required]:
  milestones	id	Identifier	true
  milestones	status	Enum(done,pending,blocked)	true
  milestones	gate	Identifier	false
  milestones	evidence	Path	false
  scope	in	Identifier	true
  scope	out	Identifier	true

relations[predicate,subject_type,object_type,required]:
  depends_on	Identifier	Identifier	false
  validated_by	Identifier	Identifier	false
  governed_by	Identifier	Identifier	false
  emits	Identifier	Path	false

rule_functions[name,min_args,max_args]:
  deny	1	1
  warn	1	1
  missing	1	1
  dangling	1	1
  invalid	1	1
  unknown	1	1
  eq	2	2
```

### 13.3 MVP schema types

Minimum recommended schema types:

```text
Null
Boolean
Integer
Decimal
String
Identifier
Path
Date
DateTime
Duration
Enum(...)
List<T>
```

Types outside the MVP:

```text
Union
Map
Regex
Object<T>
ExternalRef
RemoteSchema
```

### 13.4 Duplicate handling

Recommended MVP rules:

1. A root-level scalar field must not repeat unless the schema declares it as accumulative.
2. A table must not repeat unless explicitly allowed by schema.
3. A `rel:` block may repeat and concatenate.
4. A `rules:` block may repeat and concatenate.
5. Object blocks must not repeat unless explicitly allowed.

---

## 14. Validation pipeline

SDIF validation should happen in phases.

### 14.1 Lexing

Checks:

* Valid UTF-8.
* Valid tokens.
* Closed strings.
* Valid comment placement.
* Normalizable line endings.

### 14.2 Parsing

Builds an AST.

Checks:

* Valid indentation.
* Closed blocks.
* Well-formed tables.
* Correct table cell count.
* Relations with exactly three parts.
* Balanced expressions.

### 14.3 Normalization

Resolves:

* Aliases.
* Defaults.
* Type recognition.
* Namespaces.
* Includes, if enabled.
* Base URIs, if enabled.

### 14.4 Schema validation

Checks:

* Required fields.
* Types.
* Enumerations.
* Allowed tables.
* Required columns.
* Allowed relation predicates.
* Allowed rule functions.

### 14.5 Semantic validation

Checks may include:

* Dangling relations.
* Missing evidence.
* Forbidden cycles.
* Invalid lifecycle transitions.
* Duplicate semantic identifiers.
* Inconsistency between fields and relations.

### 14.6 Rule evaluation

Declarative rules may produce:

* `pass`
* `warn`
* `deny`
* `error`

A validator must distinguish:

* `deny`: the document was understood, but a policy rejected it.
* `error`: the document could not be processed correctly.

---

## 15. Canonicalization

Canonicalization converts SDIF Source into SDIF Canonical.

### 15.1 Goals

Canonical SDIF must be:

1. Deterministic.
2. Stable.
3. Comment-free.
4. Unambiguous.
5. Suitable for hashing.
6. Suitable for signing.
7. Suitable for byte-for-byte comparison.

### 15.2 Recommended rules

The canonicalizer should:

1. Use UTF-8 without BOM.
2. Use LF line endings.
3. Use two-space indentation.
4. Remove comments.
5. Remove redundant blank lines.
6. Order directives deterministically.
7. Order fields according to schema policy.
8. Escape strings consistently.
9. Sort relations when order is not significant.
10. Sort table rows when order is not significant.
11. Preserve order when the schema declares order significant.

The v0.1 MVP intentionally does not yet normalize aliases, booleans beyond parser-preserved literals, null spellings, dates, date-times, or numeric representation as semantic equivalence classes. Those policies require explicit versioning and golden fixtures.

### 15.3 Hashing

The hash should be calculated over canonical bytes.

```text
sha256(sdif_canonical_bytes)
```

### 15.4 Signing

Signatures should be applied to canonical bytes, not to source text, unless the source text is itself canonical.

---

## 16. JSON mapping

SDIF should map conceptually to JSON.

### 16.1 Scalar field

SDIF:

```sdif
status open
```

JSON:

```json
{
  "status": "open"
}
```

### 16.2 Object

SDIF:

```sdif
owner:
  id team.platform
  role maintainer
```

JSON:

```json
{
  "owner": {
    "id": "team.platform",
    "role": "maintainer"
  }
}
```

### 16.3 Table

SDIF:

```sdif
items[id,status]:
  item.1	open
  item.2	closed
```

JSON:

```json
{
  "items": [
    { "id": "item.1", "status": "open" },
    { "id": "item.2", "status": "closed" }
  ]
}
```

### 16.4 Relations

SDIF:

```sdif
rel:
  a depends_on b
```

Recommended JSON:

```json
{
  "rel": [
    { "subject": "a", "predicate": "depends_on", "object": "b" }
  ]
}
```

### 16.5 Rules

SDIF:

```sdif
rules:
  (deny missing(evidence))
```

Possible JSON:

```json
{
  "rules": [
    {
      "action": "deny",
      "condition": {
        "function": "missing",
        "args": ["evidence"]
      }
    }
  ]
}
```

---

## 17. Comparison with other formats

### 17.1 JSON

JSON is universal and excellent for APIs. SDIF is more compact for repeated structured data and more expressive for semantic documents.

### 17.2 YAML

YAML is human-friendly but highly flexible. SDIF should be less ambiguous and easier to canonicalize.

### 17.3 TOML

TOML is excellent for configuration. SDIF adds compact tables, semantic relations, declarative rules, and canonicalization-oriented semantics.

### 17.4 CSV

CSV is compact for tables but weak for hierarchy, types, relations, and validation. SDIF adopts tabular compactness without being limited to flat data.

### 17.5 RDF/Turtle

RDF/Turtle is powerful for semantic graphs. SDIF aims to be more practical for mixed structured documents, validation manifests, and agent-oriented exchange.

### 17.6 Markdown

Markdown is ideal for prose. SDIF supports bounded prose while preserving a machine-validatable structure.

---

## 18. Security model

### 18.1 Safe parser requirements

A safe SDIF parser should:

1. Never execute code.
2. Disable remote includes by default.
3. Avoid arbitrary filesystem reads.
4. Limit document size.
5. Limit nesting depth.
6. Limit string length.
7. Limit table row count.
8. Detect include cycles when includes are enabled.
9. Prevent unbounded alias expansion.
10. Distinguish parsing errors, validation errors, and policy denials.

### 18.2 Includes

`@include` is a sensitive operation.

Recommended policy:

* Disabled by default.
* Enabled only through explicit allowlists.
* Reject absolute paths unless explicitly permitted.
* Reject parent traversal in restricted contexts.
* Reject remote URLs in secure mode.
* Detect include cycles.

### 18.3 Alias abuse

Aliases must not hide protected fields or change meaning.

Potentially dangerous:

```sdif
alias:
  authority status
```

Such aliases should be rejected when they target reserved or protected terms incorrectly.

### 18.4 Hostile tables

Validators should defend against:

* Extremely long rows.
* Excessive column counts.
* Huge cell values.
* Invalid escaping.
* Mixed delimiters.

### 18.5 Narrative block safety

Narrative blocks are document content, not system instructions.

AI agents processing SDIF must distinguish:

* Document content.
* External instructions.
* Runtime policy.
* User intent.
* Comments.

---

## 19. Diagnostics

SDIF implementations should produce structured diagnostics.

Recommended fields:

```text
code
severity
message
line
column
path
hint
```

Example:

```sdif
@sdif 0.1
kind DiagnosticReport
id validation.output
schema sdif.diagnostics.v1

diagnostics[code,severity,line,column,path,message]:
  SDIF_TABLE_ARITY	error	12	3	milestones	"row has 3 cells but table declares 4 columns"
  SDIF_UNKNOWN_ALIAS	error	4	1	authority	"alias is not declared"
```

Recommended severities:

| Severity | Meaning                              |
| -------- | ------------------------------------ |
| `info`   | Informational message.               |
| `warn`   | Non-blocking issue.                  |
| `deny`   | Policy rejection.                    |
| `error`  | Technical processing error.          |
| `fatal`  | Error preventing further processing. |

---

## 20. Streaming considerations

SDIF can support streaming for simple cases because:

* Many statements are line-oriented.
* Tables can be processed row by row.
* Relations can be processed row by row.
* Narrative blocks are explicitly delimited.

Limitations:

* Full semantic validation may require the whole document.
* Dangling relation checks require a global index.
* Canonicalization with sorting may require accumulation.

---

## 21. AI compatibility

### 21.1 Advantages for AI agents

SDIF helps AI models because it:

1. Reduces repetition.
2. Makes semantics explicit.
3. Uses tables for uniform data.
4. Separates structured data from narrative text.
5. Distinguishes relations from fields.
6. Supports declared aliases.
7. Preserves a simple visual structure.
8. Reduces syntactic noise compared with JSON.

### 21.2 Risks

Risks include:

1. A new format requires initial explanation.
2. Excessively compact aliases can reduce comprehension.
3. Very wide tables can be error-prone.
4. Rule expressions require a known vocabulary.
5. Narrative blocks may be confused with instructions if not handled carefully.

### 21.3 Mitigations

1. Use clear aliases.
2. Keep table headers descriptive.
3. Avoid very wide tables.
4. Put `kind`, `id`, and `schema` near the top.
5. Prefer simple relation predicates.
6. Use a small set of rule functions in the MVP.
7. Treat `.sdif.ai` as a generated view.

---

## 22. Complete example: technical plan

```sdif
@sdif 0.1
kind Plan
id release.v2.validation_plan
schema example.plan.v1
authority Canonical
lifecycle Active

created_at 2026-05-20T18:00:00Z
status open
priority P0
owner team.platform

title "Release v2 validation plan"

intent """
Define the minimum validation requirements for release v2.
The plan must remain auditable, reproducible, and easy to review.
"""

scope[in,out]:
  schema validation	ui redesign
  canonicalization	feature expansion
  semantic relations	remote includes
  validation reports	release automation

milestones[id,status,gate,evidence]:
  R1	done	validate-syntax	reports/syntax.md
  R2	done	validate-canonical	reports/canonical.md
  R3	pending	validate-schema	reports/schema.md
  R4	pending	validate-semantics	reports/semantics.md

rel:
  R3 depends_on R2
  R4 depends_on R3
  release.v2.validation_plan validated_by validation.report.v2

rules:
  (deny missing(evidence))
  (deny dangling(rel))
  (deny invalid(lifecycle))
  (warn eq(authority,Unknown))
```

---

## 23. Complete example: validation report

```sdif
@sdif 0.1
kind EvidenceReport
id validation.report.v2
schema example.evidence_report.v1
authority Derived
lifecycle Active

subject release.v2.validation_plan
verified_at 2026-05-20T18:15:00Z
verifier validator.core
result pass

checks[id,result,message]:
  syntax	pass	source document parsed successfully
  canonical	pass	canonical output is stable
  schema	pass	required fields are present
  relations	pass	no dangling relations found
  evidence	pass	required evidence references are present

artifacts[id,path,sha256]:
  summary	reports/validation-summary.md	sha256:TODO
  details	reports/validation-details.sdif	sha256:TODO

rel:
  validation.report.v2 validates release.v2.validation_plan
  validation.report.v2 emits reports/validation-summary.md
```

---

## 24. Complete example: semantic registry

```sdif
@sdif 0.1
kind Registry
id example.registry
schema example.semantic_registry.v1
authority Canonical
lifecycle Active

entries[id,kind,lifecycle,authority,path,evidence]:
  example.schema	Schema	Active	Canonical	schemas/example.schema.sdif	reports/schema.md
  example.registry	Registry	Active	Canonical	registry/example.registry.sdif	reports/registry.md
  validator.core	Tool	Active	Canonical	tools/validator.md	reports/validator.md

rel:
  example.registry governed_by example.schema
  example.registry validated_by validator.core
  validator.core emits reports/validator.md

rules:
  (deny missing(entries.evidence))
  (deny dangling(rel))
  (deny invalid(entries.lifecycle))
```

---

## 25. Implementation components

A complete SDIF implementation should include:

1. Lexer.
2. Parser.
3. AST.
4. Normalizer.
5. Schema validator.
6. Declarative rule evaluator.
7. Canonicalizer.
8. Serializer.
9. JSON converter.
10. Diagnostic generator.

### 25.1 Conceptual AST

```text
Document
  directives: Directive[]
  statements: Statement[]

Statement
  Field(key, value)
  Object(key, statements)
  Table(name, columns, rows)
  Relation(subject, predicate, object)
  Rule(expression)
  Narrative(key, text)
```

### 25.2 Conceptual value model

```text
Value
  Null
  Boolean(bool)
  Integer(i64)
  Decimal(decimal)
  String(string)
  Identifier(string)
  Date(date)
  DateTime(datetime)
  Duration(duration)
  List(Value[])
```

---

## 26. MVP scope

The first useful SDIF implementation should support:

1. `@sdif` directive.
2. Scalar fields.
3. Indented objects.
4. Inline lists.
5. Tables.
6. `rel:` blocks.
7. `rules:` blocks with parenthesized expressions.
8. Narrative blocks.
9. Source comments.
10. Table arity validation.
11. Basic schema validation.
12. JSON conversion.
13. Basic canonicalization.

Out of scope for the MVP:

1. Remote includes.
2. Complex namespaces.
3. Deep graph validation.
4. Digital signatures.
5. Remote schemas.
6. Advanced type unions.
7. Rule execution beyond declarative validation.
8. Formal `.sdif.ai` profile beyond simple generation.

### 26.1 MVP acceptance criteria

The MVP should prove this pipeline:

```text
source.sdif -> AST -> canonical bytes -> stable hash
```

Minimum acceptance criteria:

1. Valid syntax fixtures parse deterministically.
2. Invalid syntax fixtures fail with stable diagnostics.
3. Equivalent source fixtures produce identical canonical bytes.
4. Equivalent source fixtures produce identical SHA-256 hashes.
5. Table arity errors are detected.
6. Required fields are detected through a minimal schema.
7. Relations with invalid arity are rejected.
8. Rule expressions must be balanced and parseable.

---

## 27. Technical roadmap

### 27.1 Phase A — Syntax core

Deliverables:

1. Lexer.
2. Parser.
3. AST.
4. Valid and invalid fixtures.
5. Line and column diagnostics.

Closure criterion:

```text
All MVP syntax fixtures parse deterministically or fail with stable diagnostics.
```

### 27.2 Phase B — Minimal canonicalization

Deliverables:

1. Canonical AST.
2. `.sdif.canon` serializer.
3. Line ending normalization.
4. Comment removal.
5. Deterministic header ordering.
6. Stable hash generation.

Closure criterion:

```text
Equivalent source fixtures produce identical canonical bytes and identical SHA-256 hashes.
```

### 27.3 Phase C — MVP schema validation

Deliverables:

1. SDIF schema parser.
2. Required field validation.
3. Basic type validation.
4. Table validation.
5. Relation predicate validation.
6. Rule function validation.

Closure criterion:

```text
Schema-valid fixtures pass and schema-invalid fixtures fail with structured diagnostics.
```

### 27.4 Phase D — Editor tooling

Deliverables:

1. Tree-sitter grammar.
2. Syntax highlighting.
3. Optional minimal language server.
4. Fixture alignment with the normative parser.

Closure criterion:

```text
Editor parse trees align with normative parser fixtures for the MVP grammar.
```

---

## 28. Versioning policy

### 28.1 Format version

The `@sdif` directive declares the format version.

```sdif
@sdif 0.1
```

Compatible changes may include:

* New optional directives.
* New optional profiles.
* New opt-in rule functions.
* New schema-level capabilities.

Incompatible changes include:

* Changing the meaning of existing syntax.
* Changing canonicalization rules without versioning.
* Changing scalar type precedence.
* Changing base rule semantics.

### 28.2 Schema version

Schemas are versioned independently.

```sdif
schema example.plan.v1
```

A new schema version may impose stricter validation while the SDIF format version remains unchanged.

---

## 29. Style recommendations

### 29.1 Recommended document order

Suggested source order:

1. `@sdif` directive.
2. Profile and vocabulary directives.
3. `kind`.
4. `id`.
5. `schema`.
6. `authority`.
7. `lifecycle`.
8. Timestamps.
9. Title and summary.
10. Main fields.
11. Tables.
12. Relations.
13. Rules.
14. Long narrative blocks when not critical at the top.

### 29.2 Naming

Use `snake_case` for keys:

```sdif
created_at 2026-05-20T18:00:00Z
```

Use dot notation for hierarchical identifiers:

```sdif
id release.v2.validation_plan
```

Use kebab-case for human-readable slugs when appropriate:

```sdif
tag schema-validation
```

### 29.3 Tables

Keep tables reasonably narrow.

If a table exceeds 8 to 10 columns, consider splitting it.

### 29.4 Relations

Prefer clear predicates over excessively short aliases.

Good:

```sdif
release.v2 depends_on release.v1
```

Too cryptic for source documents:

```sdif
v2 dep v1
```

Compact aliases may be appropriate in `.sdif.ai`, but source documents should favor clarity.

---

## 30. Open questions

The 0.1 draft intentionally leaves several topics open.

### 30.1 Inline comments in tables

Allowing inline comments inside table rows improves human authoring but complicates parsing and canonicalization, especially when table cells may contain ordinary spaces and punctuation.

Recommendation: disallow inline comments inside table rows in strict MVP mode.

### 30.2 Table cell typing

Because table cells are separated by `HTAB`, a raw cell may contain spaces, commas, quotes, and localized decimal notation.

Open decision: should the parser infer scalar types inside table cells before schema validation, or should table cells remain raw strings until the schema assigns column types?

Recommendation: keep table cells as raw strings in the initial table AST, then apply schema-driven typing during normalization. This avoids premature misclassification of localized numbers such as `450,25`.

### 30.3 Namespace design

A future version should define namespace syntax precisely.

Possible form:

```sdif
@namespace ex https://example.org/ns#
```

### 30.4 Includes

Includes are useful but security-sensitive.

Recommendation: exclude them from the MVP or allow only local, allowlisted includes.

### 30.5 Rule expression syntax

The MVP uses compact parenthesized expressions, but the exact internal normalization should be specified more formally.

For example:

```sdif
(deny missing(evidence))
```

could normalize to:

```text
Call("deny", [Call("missing", [Identifier("evidence")])])
```

### 30.6 Canonical table ordering

Schemas should explicitly declare whether table row order is significant.

Open decision: should order be significant by default, or should primary-key sorting be the default when a primary key exists?

---

## 31. Conclusion

SDIF is a compact, schema-governed semantic data interchange format for humans, machines, and AI agents.

Its value is not that it is merely shorter than JSON or cleaner than YAML. Its value is the combination of four properties that rarely appear together:

1. Human readability.
2. Token efficiency.
3. Explicit semantics.
4. Strong validation and canonicalization.

The core idea:

```text
SDIF = JSON-like data + compact tables + semantic triples + declarative rules + canonical form
```

The first implementation should avoid trying to support every possible feature. It should prove the essential technical spine:

```text
source.sdif -> AST -> canonical bytes -> stable hash
```

Once that pipeline is stable, schema validation, semantic validation, editor tooling, AI-optimized views, signing, and advanced vocabularies can evolve on top of a solid foundation.

---

## Appendix A. MVP Python implementation notes

The repository implementation follows the normative spine defined above:

```text
source.sdif -> AST -> canonical bytes -> sha256 hash
```

### CLI

The current CLI entry point is `sdif` after installation, or `python tools/sdif-cli.py` from a checkout.

```bash
sdif parse examples/plan.sdif
sdif canon examples/plan.sdif
sdif hash examples/plan.sdif
sdif validate examples/plan.sdif --schema examples/schema.sdif
sdif tokens examples/plan.sdif
sdif to-json examples/plan.sdif
sdif from-json document.json
sdif ai examples/plan.sdif --alias kind=k --alias status=st
```

`sdif tokens` emits `bytes=<n> tokenizer=<name> tokens=<n>`. The MVP CLI uses
`tiktoken/cl100k_base` when the optional `tiktoken` dependency is available and
falls back to `estimate/4bytes` otherwise. The benchmark script remains the
authoritative multi-format comparison surface.

The repository benchmark derives JSON compact, JSON pretty, YAML, XML, CSV
Bundle, SDIF, SDIF AI, and optionally TOON from the same canonical JSON fixture
source. `SDIF AI` is produced from the generated SDIF document with the
`.sdif.ai` projection so the benchmark tracks the AI-context surface separately
from canonical SDIF. For benchmark fairness, that projection chooses the smaller
of a headerless context-window view and an explicit alias-header view; aliases
are only useful when their decoding header pays for itself. It always reports an
`Estimate` column using the same deterministic 4-UTF-8-bytes-per-token fallback
as `sdif tokens`, and uses `tiktoken` as the primary ordering and ratio metric
when that optional dependency is installed. `CSV Bundle` is intentionally named
as a bundle because a full semantic SDIF document may contain metadata, nested
values, relations, and rules that cannot fit in a single honest flat CSV table.

### AST model

The MVP AST is intentionally small and source-independent:

- `Document(directives, statements)`
- `Directive(name, args)`
- `Field(key, value)`
- `ObjectBlock(key, statements)`
- `Table(name, columns, rows)`
- `Relation(subject, predicate, object)`
- `Rule(source)`
- `Narrative(key, text)`

Comments are accepted in source but excluded from the canonical AST and canonical output.

### Canonicalization rules implemented in the MVP

The current canonical serializer:

1. Normalizes line endings to LF through parser input normalization.
2. Removes comments and blank source-only trivia.
3. Emits directives in deterministic reserved-directive order.
4. Emits common metadata fields in deterministic order before other statements.
5. Preserves table rows with literal `HTAB` separators.
6. Emits a final trailing newline.
7. Hashes SHA-256 over canonical UTF-8 bytes.

Schema-aware canonicalization now supports table row ordering through `tables[name,ordered,primary_key]`: unordered tables with a declared primary key are sorted by that key when a schema is provided. Relations and rules are sorted deterministically. Alias expansion, numeric normalization, date-time equivalence, and semantic merging remain future versioned policies.

### Validation CLI and diagnostics

The MVP validator can load an SDIF schema document and emit either text output or structured JSON diagnostics.

```bash
sdif validate examples/plan.sdif --schema examples/schema.sdif
sdif validate examples/plan.sdif --schema examples/schema.sdif --json
```

The `--schema` argument must parse as an SDIF document with `kind Schema`.
Malformed schema tables fail before validation with an `invalid --schema`
message instead of a Python traceback.

Structured diagnostics use this shape:

```json
{
  "valid": false,
  "diagnostics": [
    {
      "code": "SDIF_REQUIRED_FIELD",
      "severity": "error",
      "message": "missing required field: id",
      "path": "id",
      "hint": "add `id` to the document"
    }
  ]
}
```

### JSON conversion scope

The MVP JSON converter supports scalar fields, nested objects, uniform arrays as SDIF tables, `rel` arrays as relation blocks, `rules` arrays as rule blocks, and scalar lists as inline SDIF lists.
