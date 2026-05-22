# SDIF AI speed profile

The `SDIF AI speed profile` is the repository contract for using SDIF to reduce
LLM latency beyond raw token count. It treats `.sdif.ai` as a compact,
reversible input surface that should also lower the model's structural work:
finding data, interpreting relationships, preserving context, and emitting
parseable output.

This is not a claim that every SDIF document is faster for every model. The
claim is narrower: for structured semantic data, SDIF AI should optimize the
parts of an LLM workflow that are commonly dominated by prompt size,
locality, cacheability, and output validation.

## Goals

- Reduce prefill cost by avoiding repeated keys, redundant punctuation, and
  unnecessary pretty-printing.
- Preserve locality by placing related facts close together.
- Keep compact aliases semantic enough for a model to infer their meaning.
- Support fast partial reads through summary-first artifacts.
- Support caching through canonical hash boundaries.
- Support incremental processing through future delta artifacts.
- Reduce output retries by making SDIF-shaped responses small and parseable.

## Speed-profile rules

1. Prefer `summary.sdif.ai` for normal LLM questions.
2. Use `comparison.sdif.ai` only when document-level evidence is needed.
3. Put intent, summary, schema, primary tables, relations, and evidence in that
   order unless a profile-specific reason says otherwise.
4. Use stable aliases for frequent fields, but aliases must remain semantic;
   examples: `desc`, `auth`, `ev`, `rel`, `cfg`, `src`, `st`, `pri`.
5. Avoid opaque one-letter aliases except where the surrounding header makes the
   meaning obvious and local.
6. Keep enums short and stable.
7. Normalize booleans, nulls, dates, and numeric-looking strings according to
   the reversible `.sdif.ai` contract.
8. Do not repeat schema or policy text when a trusted canonical hash identifies
   an unchanged section.
9. Keep raw matrices and large evidence sections behind explicit references or a
   chunk manifest when a summary can answer the likely question.
10. Prefer SDIF or SDIF AI output contracts for model responses that need to be
    parsed by tools.

## Prompt locality

A speed-oriented SDIF AI document should be ordered for low search overhead:

```text
intent -> summary -> schema -> compact tables -> relations -> evidence -> raw data
```

Bad locality forces a model to search across the whole context. Good locality
keeps the natural answer path near the beginning and keeps supporting evidence
adjacent to the entities it explains.

## Summary-first artifacts

Benchmark output intentionally separates human reading, structured evidence, and
LLM input:

```text
comparison.md       -> full human report
comparison.sdif     -> canonical structured evidence
comparison.sdif.ai  -> compact full evidence for LLMs
summary.sdif.ai     -> fast LLM entry point for common questions
```

For most benchmark questions, start with `summary.sdif.ai`. Escalate to
`comparison.sdif.ai` only when the question asks for per-document rankings,
raw matrix values, or tokenizer-specific evidence not present in the summary.

## Chunk manifest

Large SDIF AI artifacts should expose a section index before raw evidence:

```sdif
@sdif 1.0
kind ChunkManifest
id bench.20260521.index
chunks[id,kind,priority,tokens,hash,path]:
  S1	summary	high	320	sha256:...	sdif-benchmarks/results/token_efficiency/summary.sdif.ai
  C1	consensus	high	480	sha256:...	sdif-benchmarks/results/token_efficiency/comparison.sdif.ai#consensus
  D1	documents	medium	9000	sha256:...	sdif-benchmarks/results/token_efficiency/comparison.sdif.ai#documents
  R1	raw	low	24000	sha256:...	sdif-benchmarks/results/token_efficiency/comparison.json
```

The purpose is to let an orchestrator choose the smallest sufficient context
instead of blindly injecting the full benchmark report.

## Canonical hash caching

Canonical SDIF makes stable sections cacheable. A system can cache by canonical
hash and send only the changed section on repeated workflows:

```text
schema.hash
summary.hash
table.hash
relations.hash
```

When the hash is unchanged, the orchestration layer can avoid recomputing
embeddings, avoid resending stable context, or send a short reference plus a
small update.

## Delta direction

Future incremental workflows should prefer a delta surface over resending whole
documents:

```sdif
@sdif 1.0
kind Delta
base bench.20260521
changes[id,op,path,value]:
  C1	update	documents.large-plan.status	done
  C2	add	findings.F9	"SDIF AI remains best"
```

Deltas are a speed feature because they reduce prefill, preserve locality, and
make repeated agent/reporting workflows cheaper.

## Measurement

The token-efficiency benchmark is only the first layer. A latency benchmark
should record:

- input tokens;
- output tokens;
- time to first token;
- total latency;
- generated tokens per second;
- estimated cost;
- parse success rate;
- retries required;
- final prompt size;
- useful information per token.

The preferred end-to-end metric is `useful_answer_ms`: elapsed time until the
system receives a valid, parseable, task-sufficient answer. A compact format
that increases ambiguity or retries does not satisfy this profile.

## Output contracts

For tool-facing answers, ask the model for SDIF-shaped output instead of free
prose when practical:

```sdif
@sdif 1.0
kind FindingSet
findings[id,severity,claim,evidence]:
  F1	info	"SDIF AI has the best median token ratio"	sdif-benchmarks/results/token_efficiency/summary.sdif.ai
```

This reduces output tokens, narrows the response shape, and makes invalid output
easier to detect and retry.
