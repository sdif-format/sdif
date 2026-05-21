# SDIF Benchmark Summary

- Generated at: `2026-05-21T15:05:34Z`
- Run directory: `benchmarks/20260521T150432Z`
- Full report: `benchmarks/20260521T150432Z/comparison.md`
- Structured JSON: `benchmarks/20260521T150432Z/comparison.json`
- Structured SDIF: `benchmarks/20260521T150432Z/comparison.sdif`
- SDIF AI projection: `benchmarks/20260521T150432Z/comparison.sdif.ai`
- Raw log: `benchmarks/20260521T150432Z/comparison.log`
- Documents compared: `21`
- Available tokenizers: `Estimate, TokenX, tiktoken`

## Key Findings

- Best consensus format: **SDIF AI** (avg rank `1.06`, median ratio `56.3%`, coverage `63/63`).
- Ratios are computed independently per tokenizer against `JSON Compact`.
- `Estimate` winners: SDIF AI 20/21, SDIF 1/21.
- `TokenX` winners: SDIF AI 20/21, SDIF 1/21.
- `tiktoken` winners: SDIF AI 19/21, CSV Bundle 2/21.

## Tokenizer Availability

| Tokenizer | Status | Type | Notes |
| --- | --- | --- | --- |
| `Estimate` | available | heuristic | Deterministic fallback: 4 UTF-8 bytes per token. |
| `TokenX` | available | heuristic | Resolved through Node.js, local/global npm, or npx fallback. |
| `tiktoken` | available | model tokenizer | Encoding: cl100k_base. |
| `Llama3` | disabled | model tokenizer | Disabled through SDIF_BENCHMARK_LLAMA=0. |
| `Claude` | disabled | API tokenizer | Disabled. Set SDIF_BENCHMARK_CLAUDE=1 to enable API token counting. |

## Consensus Ranking

| Format | Avg Rank | Median Ratio | Best Ratio | Worst Ratio | Rank Spread | Coverage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SDIF AI | 1.06 | 56.3% | 26.3% | 82.8% | 1 | 63/63 |
| SDIF | 2.60 | 59.5% | 26.3% | 83.4% | 3 | 63/63 |
| CSV Bundle | 2.73 | 61.2% | 28.7% | 95.4% | 3 | 63/63 |
| TOON | 3.60 | 63.2% | 29.4% | 91.4% | 1 | 63/63 |
| YAML | 5.35 | 95.3% | 75.7% | 137.8% | 1 | 63/63 |
| JSON Compact | 5.65 | 100.0% | 100.0% | 100.0% | 1 | 63/63 |
| JSON Pretty | 7.00 | 137.3% | 100.7% | 192.5% | 0 | 63/63 |
| XML | 8.00 | 171.7% | 131.4% | 229.8% | 0 | 63/63 |

## Direct Comparison

Focused comparison of the main formats a reader is most likely to care about.

| Format | Consensus Avg Rank | Consensus Median Ratio | Wins Across Tokenizer/Document Pairs | `Estimate` Avg Ratio | `TokenX` Avg Ratio | `tiktoken` Avg Ratio |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 1.06 | 56.3% | 59 | 56.1% | 49.1% | 64.6% |
| SDIF | 2.60 | 59.5% | 2 | 58.0% | 49.3% | 68.5% |
| TOON | 3.60 | 63.2% | 0 | 58.5% | 59.9% | 70.8% |
| CSV Bundle | 2.73 | 61.2% | 2 | 57.2% | 59.7% | 68.3% |
| JSON Compact | 5.65 | 100.0% | 0 | 100.0% | 100.0% | 100.0% |

## Artifacts

- Full benchmark report: `benchmarks/20260521T150432Z/comparison.md`
- Structured JSON report: `benchmarks/20260521T150432Z/comparison.json`
- Structured SDIF report: `benchmarks/20260521T150432Z/comparison.sdif`
- SDIF AI projection: `benchmarks/20260521T150432Z/comparison.sdif.ai`
- Raw benchmark log: `benchmarks/20260521T150432Z/comparison.log`
- Latest directory: `benchmarks/latest`
