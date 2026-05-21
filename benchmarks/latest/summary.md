# SDIF Benchmark Summary

- Generated at: `2026-05-21T17:03:57Z`
- Run directory: `benchmarks/20260521T170345Z`
- Full report: `benchmarks/20260521T170345Z/comparison.md`
- Structured JSON: `benchmarks/20260521T170345Z/comparison.json`
- Structured SDIF: `benchmarks/20260521T170345Z/comparison.sdif`
- SDIF AI projection: `benchmarks/20260521T170345Z/comparison.sdif.ai`
- Raw log: `benchmarks/20260521T170345Z/comparison.log`
- Documents compared: `21`
- Available tokenizers: `Estimate`

## Key Findings

- Best consensus format: **SDIF AI** (avg rank `1.10`, median ratio `53.9%`, coverage `21/21`).
- Ratios are computed independently per tokenizer against `JSON Compact`.
- `Estimate` winners: SDIF AI 19/21, CSV Bundle 1/21, SDIF 1/21.

## Tokenizer Availability

| Tokenizer | Status | Type | Notes |
| --- | --- | --- | --- |
| `Estimate` | available | heuristic | Deterministic fallback: 4 UTF-8 bytes per token. |
| `TokenX` | disabled | heuristic | Disabled through SDIF_BENCHMARK_TOKENX=0. |
| `tiktoken` | unavailable | model tokenizer | Unavailable because Python package `tiktoken` is not installed. |
| `Llama3` | disabled | model tokenizer | Disabled through SDIF_BENCHMARK_LLAMA=0. |
| `Claude` | disabled | API tokenizer | Disabled. Set SDIF_BENCHMARK_CLAUDE=1 to enable API token counting. |

## Consensus Ranking

| Format | Avg Rank | Median Ratio | Best Ratio | Worst Ratio | Rank Spread | Coverage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SDIF AI | 1.10 | 53.9% | 28.7% | 78.9% | 1 | 21/21 |
| CSV Bundle | 2.10 | 55.0% | 28.7% | 82.0% | 2 | 21/21 |
| SDIF | 2.81 | 55.7% | 29.4% | 77.6% | 2 | 21/21 |
| YAML | 4.05 | 95.3% | 92.0% | 108.4% | 1 | 21/21 |
| JSON Compact | 4.95 | 100.0% | 100.0% | 100.0% | 1 | 21/21 |
| JSON Pretty | 6.00 | 138.1% | 127.0% | 192.5% | 0 | 21/21 |
| XML | 7.00 | 170.4% | 146.4% | 229.8% | 0 | 21/21 |

## Direct Comparison

Focused comparison of the main formats a reader is most likely to care about.

| Format | Consensus Avg Rank | Consensus Median Ratio | Wins Across Tokenizer/Document Pairs | `Estimate` Avg Ratio |
| --- | ---: |---:|---:|---:|
| SDIF AI | 1.10 | 53.9% | 19 | 56.2% |
| SDIF | 2.81 | 55.7% | 1 | 58.0% |
| CSV Bundle | 2.10 | 55.0% | 1 | 57.2% |
| JSON Compact | 4.95 | 100.0% | 0 | 100.0% |

## Artifacts

- Full benchmark report: `benchmarks/20260521T170345Z/comparison.md`
- Structured JSON report: `benchmarks/20260521T170345Z/comparison.json`
- Structured SDIF report: `benchmarks/20260521T170345Z/comparison.sdif`
- SDIF AI projection: `benchmarks/20260521T170345Z/comparison.sdif.ai`
- Raw benchmark log: `benchmarks/20260521T170345Z/comparison.log`
- Latest directory: `benchmarks/latest`
