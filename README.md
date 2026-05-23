<p align="center">
  <img src="https://raw.githubusercontent.com/sdif-format/.github/d5ec91398d67baccbb1bf28f2dcf2781f1316545/profile/assets/sdif-logo-t.png" alt="SDIF Format" width="520">
</p>

<p align="center">
  <strong>Semantic Data Interchange Format</strong>
</p>

<p align="center">
  Compact, semantic and canonicalizable structured data<br>
  for AI agents, deterministic workflows and human-auditable records.
</p>

<p align="center">
  <a href="#what-is-sdif">What is SDIF?</a>
  ·
  <a href="#quick-start">Quick start</a>
  ·
  <a href="#format-at-a-glance">Format at a glance</a>
  ·
  <a href="#token-efficiency">Token efficiency</a>
  ·
  <a href="#ecosystem">Ecosystem</a>
  ·
  <a href="#documentation">Documentation</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/spec-v1.0.0%20stable-16a34a?style=flat-square" alt="Spec v1.0.0 stable">
  <img src="https://img.shields.io/badge/python-3.10%2B-2563eb?style=flat-square" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/license-MIT-374151?style=flat-square" alt="MIT">
  <img src="https://img.shields.io/badge/focus-AI%20native%20data-111827?style=flat-square" alt="AI native data">
</p>

<br>

<div align="center">

<table>
  <tr>
    <td align="center" width="25%">
      <strong>Compact</strong>
      <br><br>
      Shape declared once.<br>
      No repeated field names.
    </td>
    <td align="center" width="25%">
      <strong>Semantic</strong>
      <br><br>
      Tables, relations,<br>
      metadata and intent.
    </td>
    <td align="center" width="25%">
      <strong>Canonical</strong>
      <br><br>
      Stable output for hashing,<br>
      signing and comparison.
    </td>
    <td align="center" width="25%">
      <strong>Auditable</strong>
      <br><br>
      Designed to be read,<br>
      reviewed and trusted.
    </td>
  </tr>
</table>

</div>

<br>

---

## What is SDIF?

**SDIF — Semantic Data Interchange Format** is a compact, canonicalizable and AI-friendly data format for structured information that needs to move cleanly between humans, tools, agents and deterministic workflows.

It is designed for cases where data should be:

- small enough to be efficient in AI context windows;
- structured enough for machines to parse and validate;
- readable enough for humans to review;
- deterministic enough for hashing, signing and reproducible workflows;
- semantic enough to express tables, relations, metadata and intent.

SDIF also includes an AI projection surface, `.sdif.ai`, designed for token-dense agent exchange while remaining reversible back into canonical SDIF when the projection contract is respected.

<br>

---

## Quick start

```bash
pip install -e '.[dev]'
```

```bash
sdif parse    examples/plan.sdif
sdif canon    examples/plan.sdif
sdif canon    examples/plan.sdif --schema examples/schema.sdif
sdif hash     examples/plan.sdif
sdif validate examples/plan.sdif --schema examples/schema.sdif
sdif tokens   examples/plan.sdif
sdif to-json  examples/plan.sdif
sdif from-json document.json
sdif ai       examples/plan.sdif --alias kind=k --alias status=st
```

`sdif tokens` reports byte size, tokenizer identity and token count. It uses `tiktoken/cl100k_base` when available and falls back to a deterministic 4-bytes-per-token estimate.

<br>

---

## Format at a glance

JSON repeats field names across every record:

```json
[
  { "id": "R1", "status": "done",    "owner": "build",    "evidence": "reports/build.md"  },
  { "id": "R2", "status": "open",    "owner": "qa",       "evidence": "reports/tests.md"  },
  { "id": "R3", "status": "done",    "owner": "security", "evidence": "reports/audit.md"  }
]
```

SDIF declares the shape once and uses literal tabs between cells. Editors must preserve tabs — this is a deliberate tradeoff for compactness:

```sdif
@sdif 1.0

kind Plan
id   release.v1
title "Release readiness plan"

items[id,status,owner,evidence]:
  R1	done	build	reports/build.md
  R2	open	qa	reports/tests.md
  R3	done	security	reports/audit.md

rel:
  release.v1  validated_by  R1
  release.v1  blocked_by    R2
  release.v1  governed_by   R3
```

Semantic relationships are first-class, not embedded strings.

<br>

<p align="center">
  <strong>
    Structured information closer to a document,<br>
    while still behaving like a contract.
  </strong>
</p>

<br>

---

## Token efficiency

The benchmark derives every compared format from the same canonical JSON source in `examples/golden/`. Results below are from the most recent run across 21 documents and 3 tokenizers.

<div align="center">

| Format | Consensus avg rank | Median ratio vs JSON Compact |
| --- | ---: | ---: |
| **SDIF AI** | **1.10** | **56.8%** |
| SDIF | 2.60 | 59.5% |
| CSV Bundle | 2.70 | 61.2% |
| YAML | 5.35 | 95.3% |
| JSON Compact | 5.65 | 100.0% |
| JSON Pretty | 7.00 | 137.3% |
| XML | 8.00 | 171.7% |

</div>

<br>

SDIF AI wins 57 of 63 tokenizer/document pairs. SDIF canonical wins 2.

The benchmark repository contains the exact corpus model, generated artifacts and methodology needed to reproduce these numbers.

These results are corpus-dependent. Not every data shape benefits equally from tabular projection. Claude and Llama tokenizers require separate opt-in before claiming results for those models.

For full methodology, corpus model and per-document breakdowns, see [`sdif-benchmarks`](https://github.com/sdif-format/sdif-benchmarks).

<br>

---

## Ecosystem

<div align="center">

<table>
  <tr>
    <td width="33%" valign="top">
      <p><sub>CORE FORMAT</sub></p>
      <h3>sdif</h3>
      <p>
        Specification, parser, canonicalizer and CLI.<br>
        The normative reference for the format.
      </p>
      <p><em>This repository.</em></p>
    </td>
    <td width="33%" valign="top">
      <p><sub>MEASUREMENT</sub></p>
      <h3>sdif-benchmarks</h3>
      <p>
        Reproducible benchmark datasets and reports comparing SDIF with existing formats across token efficiency, context packing, round-trip fidelity and retrieval accuracy.
      </p>
      <p><a href="https://github.com/sdif-format/sdif-benchmarks"><strong>View benchmarks →</strong></a></p>
    </td>
    <td width="33%" valign="top">
      <p><sub>SYNTAX TOOLING</sub></p>
      <h3>tree-sitter-sdif</h3>
      <p>
        Tree-sitter grammar foundation for syntax highlighting and editor integrations.
        Registers both <code>.sdif</code> and <code>.sdif.ai</code> file types.
      </p>
      <p><a href="https://github.com/sdif-format/tree-sitter-sdif"><strong>Open grammar →</strong></a></p>
    </td>
  </tr>
</table>

</div>

<br>

---

## What SDIF is not

SDIF does not try to replace JSON, YAML, CSV, Markdown, XML, Parquet or Protocol Buffers. Those formats are useful and battle-tested.

<table>
  <tr>
    <td width="25%" valign="top">
      <strong>JSON</strong>
      <br><br>
      Universal and reliable, but noisy when repeated records dominate.
    </td>
    <td width="25%" valign="top">
      <strong>YAML</strong>
      <br><br>
      Readable, but too permissive for deterministic workflows.
    </td>
    <td width="25%" valign="top">
      <strong>CSV</strong>
      <br><br>
      Compact, but loses structure, relations and meaning quickly.
    </td>
    <td width="25%" valign="top">
      <strong>Markdown</strong>
      <br><br>
      Great for humans, not enough when data must be parsed and verified.
    </td>
  </tr>
</table>

<br>

SDIF focuses on a narrower problem:

<p align="center">
  <strong>
    compact, semantic, canonicalizable structured data<br>
    that can move cleanly between humans, machines and AI systems.
  </strong>
</p>

<br>

---

## Documentation

| Document | Description |
| --- | --- |
| [`docs/spec.md`](docs/spec.md) | Full v1.0.0 specification |
| [`docs/canonicalization.md`](docs/canonicalization.md) | Canonicalization contract |
| [`docs/comparison.md`](docs/comparison.md) | Format comparison |
| [`docs/semantic-quality.md`](docs/semantic-quality.md) | Semantic quality methodology |
| [`docs/ai-speed-profile.md`](docs/ai-speed-profile.md) | AI speed profile contract |
| [`examples/`](examples/) | Annotated examples |
| [`conformance/`](conformance/) | Shared conformance fixtures |

<br>

---

## Limitations

SDIF `1.0` is the stable core contract. Current benchmark results are promising, but should be read with these boundaries:

- results are corpus-dependent;
- not every data shape benefits equally from tabular projection;
- editors and tools must preserve literal tabs in table rows;
- `.sdif.ai` is an agent projection surface, not the canonical signing surface;
- Claude and Llama3 token counting must be enabled separately before claiming results for those tokenizers.

<br>

---

## License

MIT. See [LICENSE](LICENSE).
