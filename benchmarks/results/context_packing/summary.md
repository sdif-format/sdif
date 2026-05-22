# SDIF Context Packing Benchmark — Summary

- Generated at: `2026-05-22T08:11:06Z`
- Tokenizer: `tiktoken/cl100k_base`
- Documents: `21`
- Budgets: `4K`, `8K`, `32K`, `128K` tokens

## Key Finding

- **SDIF AI** is the most compact format: avg 62274 tokens (67.9% of JSON Compact).

## Fit Rate: % of 21 documents that fit at least once

| Format | Avg tokens | vs JSON | `4K` | `8K` | `32K` | `128K` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SDIF AI | 62274 | 67.9% | 33% | 33% | 57% | 86% |
| CSV Bundle | 63167 | 68.9% | 33% | 33% | 57% | 86% |
| SDIF | 65174 | 71.1% | 33% | 33% | 57% | 86% |
| TOON | 66119 | 72.1% | 33% | 33% | 57% | 86% |
| JSON Compact | 91696 | 100.0% | 33% | 33% | 43% | 67% |
| YAML | 102826 | 112.1% | 33% | 33% | 38% | 62% |
| JSON Pretty | 135099 | 147.3% | 33% | 33% | 33% | 62% |
| XML | 161032 | 175.6% | 33% | 33% | 33% | 62% |

## Avg documents per context budget

| Format | `4K` | `8K` | `32K` | `128K` |
| --- | ---: | ---: | ---: | ---: |
| SDIF AI | 4.9 | 10.0 | 40.8 | 164.7 |
| CSV Bundle | 4.3 | 8.6 | 35.2 | 141.9 |
| SDIF | 4.7 | 9.5 | 38.7 | 155.6 |
| TOON | 4.2 | 8.6 | 35.2 | 142.1 |
| JSON Compact | 3.3 | 6.8 | 27.9 | 112.8 |
| YAML | 3.0 | 6.2 | 25.1 | 101.3 |
| JSON Pretty | 2.0 | 4.1 | 16.7 | 67.8 |
| XML | 1.5 | 3.2 | 13.3 | 54.0 |

## Methodology

- All formats are derived from the same canonical `equivalent.json` source.
- **Fit rate**: % of corpus documents where `floor(budget / tokens) >= 1`.
- **Avg docs**: mean number of copies that fit per document across the corpus.
- Tokenizer: `tiktoken/cl100k_base`.
- Ratios computed against JSON Compact as the stable baseline.
