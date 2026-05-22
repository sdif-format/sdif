# SDIF Benchmarks

Evidence-first benchmarks measuring SDIF against JSON, YAML, XML, CSV Bundle, SDIF AI, and TOON from the perspective of AI and LLM developers. Every compared representation is derived from the same canonical JSON source under `examples/golden/`. Each run writes evidence to `benchmarks/tmp/<track>/` while running and promotes it to `benchmarks/results/<track>/` on success.

## Quick Start

```bash
# Token reduction across formats
make benchmark-token

# Context-window fit rate by budget
make benchmark-packing

# JSON→format→JSON round-trip fidelity
make benchmark-roundtrip

# Mutation sensitivity (re-send overhead)
make benchmark-delta

# LLM retrieval accuracy by format — opt-in
SDIF_BENCHMARK_RETRIEVAL=1 ANTHROPIC_API_KEY=<key> make benchmark-retrieval

# Semantic-quality documentation checks
make benchmark-quality
```

## Benchmark Tracks

### Token Efficiency

Measures byte and token reduction across shared semantic fixtures:

1. Read each `examples/golden/<fixture>/equivalent.json` source.
2. Convert to JSON Compact, JSON Pretty, YAML, XML, CSV Bundle, SDIF, SDIF AI, and optionally TOON.
3. Count tokens with tiktoken (`cl100k_base`) or a byte-estimate fallback.
4. Rank formats against JSON Compact as the stable baseline.
5. Write Markdown, JSON, SDIF, SDIF AI, and HTML reports.

Results: `benchmarks/results/token_efficiency/` — run with `make benchmark-token`.

### Context Packing

Measures how many document copies of each format fit inside fixed token budgets (4K, 8K, 32K, 128K). Reports:

- **Fit rate**: % of corpus documents where at least one copy fits.
- **Avg docs** / **Median docs**: mean and median copies per budget.

Results: `benchmarks/results/context_packing/` — run with `make benchmark-packing`.

### Round-trip Fidelity

Measures JSON→format→JSON preservation. Scores value fidelity, type fidelity, and structure fidelity (harmonic mean = overall fidelity). N/A for SDIF AI and TOON, which are projections, not full encodings.

Results: `benchmarks/results/roundtrip_fidelity/` — run with `make benchmark-roundtrip`.

### Delta Compactness (Mutation Sensitivity)

Measures the token overhead of re-sending a mutated document vs the original. Applies a deterministic mutation to the first 10% of leaf values. Reports token delta, % overhead, and unified-diff line counts. This is a full-resend measurement — not a true SDIF delta protocol.

Results: `benchmarks/results/delta_compactness/` — run with `make benchmark-delta`.

### Retrieval Accuracy

Measures LLM answer quality by format. Generates deterministic questions from each fixture (scalar lookup, count, aggregation, filtered count) and validates answers deterministically — no LLM judge. Opt-in: requires `SDIF_BENCHMARK_RETRIEVAL=1` and `ANTHROPIC_API_KEY`.

Run with: `SDIF_BENCHMARK_RETRIEVAL=1 make benchmark-retrieval`.

### Semantic Quality

Guards that SDIF preserves semantic structure beyond token efficiency: relations, rules, schema validation, canonicalization, and reversible AI projection boundaries. Verifies `docs/semantic-quality.md` methodology. Run with `make benchmark-quality`.

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

Executable benchmark runners live in:

```text
benchmarks/scripts/
```

## Result Model

Each benchmark run writes:

```text
benchmarks/tmp/<track>/           # while running
└── moved on success to benchmarks/results/<track>/
    ├── comparison.log            # console output
    ├── comparison.md             # per-document detail
    ├── summary.md                # key findings
    ├── summary.json              # machine-readable summary
    ├── summary.sdif              # SDIF encoding
    ├── summary.sdif.ai           # compact AI projection
    ├── dashboard.html            # self-contained HTML dashboard
    └── corpus/                   # exact format files measured
        └── <document>/
            ├── json_compact.json
            ├── json_pretty.json
            ├── yaml.yaml
            ├── xml.xml
            ├── csv_bundle.csv
            ├── sdif.sdif
            ├── sdif_ai.sdif.ai
            └── toon.toon         # when TOON is enabled
```

`benchmarks/results/<track>/` is replaced only after a successful run. Failed runs leave `benchmarks/tmp/<track>/` for diagnosis without touching the last clean result.

## Environment

Common environment switches (all tracks):

```bash
SDIF_BENCHMARK_OUTPUT_DIR=/tmp/sdif-benchmarks  # redirect all benchmark output
SDIF_BENCHMARK_GOLDEN_DIR=/tmp/golden-fixtures   # use a custom corpus
SDIF_BENCHMARK_TOON=0                           # disable TOON comparison
SDIF_BENCHMARK_VERBOSE=1                        # print optional-tool diagnostics
SDIF_ENV_OVERRIDE=0                             # keep existing env vars instead of loading .env
```

Token efficiency additional switches:

```bash
SDIF_TIKTOKEN_ENCODING=cl100k_base              # tiktoken encoding (default)
SDIF_BENCHMARK_TOKENX=0                         # disable TokenX estimation
SDIF_BENCHMARK_LLAMA=0                          # disable Llama tokenizer
SDIF_BENCHMARK_CLAUDE=1                         # enable Claude counting; needs ANTHROPIC_API_KEY
```

Retrieval accuracy:

```bash
SDIF_BENCHMARK_RETRIEVAL=1                      # opt-in to retrieval accuracy track
ANTHROPIC_API_KEY=<key>                         # required for retrieval accuracy
```

All scripts load `.env` from the repository root when present, unless `SDIF_ENV_OVERRIDE=0`.

## Project Structure

```text
benchmarks/
├── README.md              # this file — methodology and operating contract
├── scripts/               # executable benchmark runners (one per track)
├── src/                   # reusable helpers shared across tracks
├── tmp/                   # in-progress benchmark output (gitignored)
└── results/               # completed benchmark results
```

## Organization Contract

- Executable benchmark runners belong in `benchmarks/scripts/`.
- Reusable helpers belong in `benchmarks/src/` — code shared by two or more tracks.
- Each track writes scratch output to `benchmarks/tmp/<track>/`; completed evidence goes to `benchmarks/results/<track>/`.
- Canonical semantic sources belong in `examples/golden/`, unless `SDIF_BENCHMARK_GOLDEN_DIR` overrides.
- Optional external tools (TOON, tiktoken) must degrade gracefully.
- Claims must name the tokenizer and model coverage that produced them.
- Retrieval accuracy must use deterministic validators, not subjective LLM judging.
