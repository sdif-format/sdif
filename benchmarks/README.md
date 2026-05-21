# SDIF Benchmarks

Benchmarks measuring SDIF's token efficiency, semantic fidelity, and model-facing readability compared to JSON, JSON Compact, YAML, XML, CSV Bundle, `.sdif.ai`, and TOON when the official TOON CLI is available.

The benchmark suite is intentionally evidence-first: every compared representation is derived from the same canonical JSON semantic source under `examples/golden/`, and every run writes machine-readable and human-readable evidence under `benchmarks/<timestamp>/` plus a refreshed `benchmarks/latest/` copy.

## Quick Start

```bash
# Run the token efficiency benchmark
make benchmark-token

# Run semantic-quality documentation checks
make benchmark-quality

# Regenerate the deterministic benchmark corpus
make benchmark-corpus

# Regenerate large benchmark fixtures
make benchmark-large-corpus
```

`make benchmark` remains an alias for the token efficiency benchmark.

## Benchmark Tracks

### Token Efficiency Track

Measures byte and token reduction across shared semantic fixtures:

1. Read each `examples/golden/<fixture>/equivalent.json` source.
2. Convert it to JSON Compact, JSON Pretty, YAML, XML, CSV Bundle, SDIF, `.sdif.ai`, and optionally TOON.
3. Count tokens through the available tokenizers.
4. Rank formats against JSON Compact as the stable baseline.
5. Write reports as Markdown, JSON, SDIF, and `.sdif.ai`.

Run it with:

```bash
make benchmark-token
```

The latest successful run is available in:

```text
benchmarks/latest/
```

### Semantic Quality Track

Checks that token claims are not the only story. SDIF must also preserve semantic structure: relations, rules, schema validation, canonicalization, and reversible AI projection boundaries.

Run it with:

```bash
make benchmark-quality
```

This currently verifies `docs/semantic-quality.md` and guards that the methodology stays separate from raw token counting.

### Retrieval Accuracy Track

Not implemented yet. The intended shape is deliberately close to the token track but with deterministic answer validation instead of an LLM judge:

1. Generate questions from each fixture profile.
2. Render each fixture into every supported format.
3. Ask selected models the same retrieval, filtering, aggregation, and structure-awareness questions.
4. Validate answers with deterministic, type-aware comparators.
5. Aggregate results by model, dataset profile, question type, and format.

This track should not block `v1.0.0`; it is a post-core-release evidence layer.

## Corpus Model

SDIF keeps the canonical semantic corpus in `examples/golden/` instead of duplicating it under `benchmarks/data/`. This avoids drift between parser/conformance fixtures and benchmark fixtures.

Each fixture should contain:

```text
examples/golden/<fixture>/
├── equivalent.json     # canonical semantic source
├── source.sdif         # hand-authored or generated SDIF source
├── canonical.sdif      # canonical SDIF form
└── canonical.sha256    # canonical hash evidence
```

Benchmark-oriented fixture generation lives in:

```text
scripts/generate_benchmark_golden.py
scripts/generate_large_golden.py
```

## Result Model

A normal token benchmark run writes:

```text
benchmarks/<timestamp>/
├── comparison.log
├── comparison.md
├── comparison.json
├── comparison.sdif
├── comparison.sdif.ai
├── summary.md
├── summary.json
├── summary.sdif
└── summary.sdif.ai
```

`benchmarks/latest/` is a copied snapshot of the latest run, not a symlink. That makes release archives and external review bundles easier to inspect.

## Environment

Useful switches:

```bash
SDIF_BENCHMARK_OUTPUT_DIR=/tmp/sdif-benchmarks  # redirect output
SDIF_BENCHMARK_TOON=0                           # disable TOON comparison
SDIF_BENCHMARK_TOKENX=0                         # disable TokenX estimation
SDIF_BENCHMARK_LLAMA=0                          # disable Llama tokenizer
SDIF_BENCHMARK_CLAUDE=1                         # enable Claude counting; needs ANTHROPIC_API_KEY
SDIF_BENCHMARK_VERBOSE=1                        # print optional-tool diagnostics
```

The benchmark script also loads `.env` when present unless `SDIF_ENV_OVERRIDE=0` is set.

## Organization Contract

The benchmark suite follows these rules:

- Token-efficiency evidence belongs in `benchmarks/`.
- Canonical semantic sources belong in `examples/golden/`.
- Release-facing summaries may be mirrored into the root README, but the detailed methodology lives here.
- Optional external tools must degrade gracefully.
- Claims must name the tokenizer/model coverage that produced them.
- Retrieval accuracy must use deterministic validators, not subjective LLM judging.
