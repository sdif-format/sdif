# SDIF Benchmark Summary

- Generated at: `2026-05-21T18:50:53Z`
- Run directory: `benchmarks/results/token_efficiency`
- Full report: `benchmarks/results/token_efficiency/comparison.md`
- Structured JSON: `benchmarks/results/token_efficiency/comparison.json`
- Structured SDIF: `benchmarks/results/token_efficiency/comparison.sdif`
- SDIF AI projection: `benchmarks/results/token_efficiency/comparison.sdif.ai`
- Raw log: `benchmarks/results/token_efficiency/comparison.log`
- Documents compared: `21`
- Available tokenizers: `Estimate, tiktoken`

## Key Findings

- Best consensus format: **SDIF AI** (avg rank `1.12`, median ratio `61.5%`, coverage `42/42`).
- Ratios are computed independently per tokenizer against `JSON Compact`.
- `Estimate` winners: SDIF AI 19/21, CSV Bundle 1/21, SDIF 1/21.
- `tiktoken` winners: SDIF AI 18/21, CSV Bundle 3/21.

## Tokenizer Availability

| Tokenizer | Status | Type | Notes |
| --- | --- | --- | --- |
| `Estimate` | available | heuristic | Deterministic fallback: 4 UTF-8 bytes per token. |
| `TokenX` | disabled | heuristic | Disabled through SDIF_BENCHMARK_TOKENX=0. |
| `tiktoken` | available | model tokenizer | Encoding: cl100k_base. |
| `Llama3` | disabled | model tokenizer | Disabled through SDIF_BENCHMARK_LLAMA=0. |
| `Claude` | disabled | API tokenizer | Disabled. Set SDIF_BENCHMARK_CLAUDE=1 to enable API token counting. |

## Consensus Ranking

| Format | Avg Rank | Median Ratio | Best Ratio | Worst Ratio | Rank Spread | Coverage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SDIF AI | 1.12 | 61.5% | 28.7% | 83.1% | 1 | 42/42 |
| CSV Bundle | 2.12 | 62.8% | 28.7% | 95.4% | 2 | 42/42 |
| SDIF | 2.76 | 64.9% | 29.4% | 83.4% | 2 | 42/42 |
| JSON Compact | 4.48 | 100.0% | 100.0% | 100.0% | 1 | 42/42 |
| YAML | 4.52 | 107.5% | 92.0% | 137.8% | 1 | 42/42 |
| JSON Pretty | 6.00 | 148.0% | 127.0% | 192.5% | 0 | 42/42 |
| XML | 7.00 | 179.4% | 146.4% | 229.8% | 0 | 42/42 |

## Direct Comparison

Focused comparison of the main formats a reader is most likely to care about.

| Format | Consensus Avg Rank | Consensus Median Ratio | Wins Across Tokenizer/Document Pairs | `Estimate` Avg Ratio | `tiktoken` Avg Ratio |
| --- | ---: |---:|---:|---:|---:|
| SDIF AI | 1.12 | 61.5% | 37 | 56.2% | 64.9% |
| SDIF | 2.76 | 64.9% | 1 | 58.0% | 68.5% |
| CSV Bundle | 2.12 | 62.8% | 4 | 57.2% | 68.3% |
| JSON Compact | 4.48 | 100.0% | 0 | 100.0% | 100.0% |

## Artifacts

- Full benchmark report: `benchmarks/results/token_efficiency/comparison.md`
- Structured JSON report: `benchmarks/results/token_efficiency/comparison.json`
- Structured SDIF report: `benchmarks/results/token_efficiency/comparison.sdif`
- SDIF AI projection: `benchmarks/results/token_efficiency/comparison.sdif.ai`
- Raw benchmark log: `benchmarks/results/token_efficiency/comparison.log`
- Compared corpus files: `benchmarks/results/token_efficiency/corpus`
- Result directory: `benchmarks/results/token_efficiency`
