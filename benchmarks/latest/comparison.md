# SDIF Benchmark Evidence Report

- Generated at: `2026-05-21T17:03:57Z`
- Run directory: `benchmarks/20260521T170345Z`
- Semantic source: `examples/golden/<document>/equivalent.json`
- Ratios are computed independently per tokenizer against `JSON Compact`.
- All formats are derived from the same canonical JSON semantic source.
- Console ordering tokenizer: `Estimate`
- `.env` loaded: `yes`

## Executive Summary

### Tokenizer Availability

| Tokenizer | Status | Type | Notes |
| --- | --- | --- | --- |
| `Estimate` | available | heuristic | Deterministic fallback: 4 UTF-8 bytes per token. |
| `TokenX` | disabled | heuristic | Disabled through SDIF_BENCHMARK_TOKENX=0. |
| `tiktoken` | unavailable | model tokenizer | Unavailable because Python package `tiktoken` is not installed. |
| `Llama3` | disabled | model tokenizer | Disabled through SDIF_BENCHMARK_LLAMA=0. |
| `Claude` | disabled | API tokenizer | Disabled. Set SDIF_BENCHMARK_CLAUDE=1 to enable API token counting. |

### Consensus Ranking

| Format | Avg Rank | Median Ratio | Best Ratio | Worst Ratio | Rank Spread | Coverage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SDIF AI | 1.10 | 53.9% | 28.7% | 78.9% | 1 | 21/21 |
| CSV Bundle | 2.10 | 55.0% | 28.7% | 82.0% | 2 | 21/21 |
| SDIF | 2.81 | 55.7% | 29.4% | 77.6% | 2 | 21/21 |
| YAML | 4.05 | 95.3% | 92.0% | 108.4% | 1 | 21/21 |
| JSON Compact | 4.95 | 100.0% | 100.0% | 100.0% | 1 | 21/21 |
| JSON Pretty | 6.00 | 138.1% | 127.0% | 192.5% | 0 | 21/21 |
| XML | 7.00 | 170.4% | 146.4% | 229.8% | 0 | 21/21 |

### Winners by Tokenizer

| Tokenizer | Winner Format | Wins | Documents |
| --- | --- | ---: | ---: |
| `Estimate` | SDIF AI | 19 | 21 |
| `Estimate` | CSV Bundle | 1 | 21 |
| `Estimate` | SDIF | 1 | 21 |

## Tokenizer Results

### `Estimate`

#### Summary

| Format | Avg Rank | Avg Ratio | Median Ratio | Avg Saved Tokens | Wins | Coverage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SDIF AI | 1.10 | 56.2% | 53.9% | 34218 | 19 | 21/21 |
| CSV Bundle | 2.10 | 57.2% | 55.0% | 34281 | 1 | 21/21 |
| SDIF | 2.81 | 58.0% | 55.7% | 32818 | 1 | 21/21 |
| YAML | 4.05 | 96.0% | 95.3% | 2880 | 0 | 21/21 |
| JSON Compact | 4.95 | 100.0% | 100.0% | 0 | 0 | 21/21 |
| JSON Pretty | 6.00 | 142.2% | 138.1% | -29373 | 0 | 21/21 |
| XML | 7.00 | 173.3% | 170.4% | -52146 | 0 | 21/21 |

#### Per-document Ranking

| Document | Rank | Format | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| `deep-hierarchy-project` | 1 | SDIF AI | 73179 | 118574 | 45395 | 61.7% |
| `deep-hierarchy-project` | 2 | CSV Bundle | 73189 | 118574 | 45385 | 61.7% |
| `deep-hierarchy-project` | 3 | SDIF | 75551 | 118574 | 43023 | 63.7% |
| `deep-hierarchy-project` | 4 | YAML | 113041 | 118574 | 5533 | 95.3% |
| `deep-hierarchy-project` | 5 | JSON Compact | 118574 | 118574 | 0 | 100.0% |
| `deep-hierarchy-project` | 6 | JSON Pretty | 162017 | 118574 | -43443 | 136.6% |
| `deep-hierarchy-project` | 7 | XML | 192059 | 118574 | -73485 | 162.0% |
| `github.openapi` | 1 | SDIF AI | 41843 | 73106 | 31263 | 57.2% |
| `github.openapi` | 2 | CSV Bundle | 41885 | 73106 | 31221 | 57.3% |
| `github.openapi` | 3 | SDIF | 43413 | 73106 | 29693 | 59.4% |
| `github.openapi` | 4 | YAML | 70814 | 73106 | 2292 | 96.9% |
| `github.openapi` | 5 | JSON Compact | 73106 | 73106 | 0 | 100.0% |
| `github.openapi` | 6 | JSON Pretty | 96711 | 73106 | -23605 | 132.3% |
| `github.openapi` | 7 | XML | 118164 | 73106 | -45058 | 161.6% |
| `large-audit-trail` | 1 | SDIF AI | 283498 | 432185 | 148687 | 65.6% |
| `large-audit-trail` | 2 | CSV Bundle | 283509 | 432185 | 148676 | 65.6% |
| `large-audit-trail` | 3 | SDIF | 288882 | 432185 | 143303 | 66.8% |
| `large-audit-trail` | 4 | YAML | 416699 | 432185 | 15486 | 96.4% |
| `large-audit-trail` | 5 | JSON Compact | 432185 | 432185 | 0 | 100.0% |
| `large-audit-trail` | 6 | JSON Pretty | 555569 | 432185 | -123384 | 128.5% |
| `large-audit-trail` | 7 | XML | 644132 | 432185 | -211947 | 149.0% |
| `large-knowledge-graph` | 1 | SDIF AI | 69895 | 129721 | 59826 | 53.9% |
| `large-knowledge-graph` | 2 | CSV Bundle | 69905 | 129721 | 59816 | 53.9% |
| `large-knowledge-graph` | 3 | SDIF | 72311 | 129721 | 57410 | 55.7% |
| `large-knowledge-graph` | 4 | YAML | 123802 | 129721 | 5919 | 95.4% |
| `large-knowledge-graph` | 5 | JSON Compact | 129721 | 129721 | 0 | 100.0% |
| `large-knowledge-graph` | 6 | JSON Pretty | 183302 | 129721 | -53581 | 141.3% |
| `large-knowledge-graph` | 7 | XML | 221097 | 129721 | -91376 | 170.4% |
| `large-plan` | 1 | SDIF AI | 123089 | 201176 | 78087 | 61.2% |
| `large-plan` | 2 | CSV Bundle | 123104 | 201176 | 78072 | 61.2% |
| `large-plan` | 3 | SDIF | 126199 | 201176 | 74977 | 62.7% |
| `large-plan` | 4 | YAML | 195083 | 201176 | 6093 | 97.0% |
| `large-plan` | 5 | JSON Compact | 201176 | 201176 | 0 | 100.0% |
| `large-plan` | 6 | JSON Pretty | 262124 | 201176 | -60948 | 130.3% |
| `large-plan` | 7 | XML | 318407 | 201176 | -117231 | 158.3% |
| `large-registry` | 1 | SDIF AI | 100680 | 220956 | 120276 | 45.6% |
| `large-registry` | 2 | CSV Bundle | 100693 | 220956 | 120263 | 45.6% |
| `large-registry` | 3 | SDIF | 106542 | 220956 | 114414 | 48.2% |
| `large-registry` | 4 | YAML | 209988 | 220956 | 10968 | 95.0% |
| `large-registry` | 5 | JSON Compact | 220956 | 220956 | 0 | 100.0% |
| `large-registry` | 6 | JSON Pretty | 321329 | 220956 | -100373 | 145.4% |
| `large-registry` | 7 | XML | 413066 | 220956 | -192110 | 186.9% |
| `large-schema-catalog` | 1 | CSV Bundle | 53815 | 111880 | 58065 | 48.1% |
| `large-schema-catalog` | 2 | SDIF AI | 55400 | 111880 | 56480 | 49.5% |
| `large-schema-catalog` | 3 | SDIF | 57239 | 111880 | 54641 | 51.2% |
| `large-schema-catalog` | 4 | YAML | 108758 | 111880 | 3122 | 97.2% |
| `large-schema-catalog` | 5 | JSON Compact | 111880 | 111880 | 0 | 100.0% |
| `large-schema-catalog` | 6 | JSON Pretty | 163270 | 111880 | -51390 | 145.9% |
| `large-schema-catalog` | 7 | XML | 197509 | 111880 | -85629 | 176.5% |
| `large-support-export` | 1 | SDIF AI | 85512 | 148025 | 62513 | 57.8% |
| `large-support-export` | 2 | CSV Bundle | 85524 | 148025 | 62501 | 57.8% |
| `large-support-export` | 3 | SDIF | 88110 | 148025 | 59915 | 59.5% |
| `large-support-export` | 4 | YAML | 143347 | 148025 | 4678 | 96.8% |
| `large-support-export` | 5 | JSON Compact | 148025 | 148025 | 0 | 100.0% |
| `large-support-export` | 6 | JSON Pretty | 202532 | 148025 | -54507 | 136.8% |
| `large-support-export` | 7 | XML | 246683 | 148025 | -98658 | 166.6% |
| `large-validation-report` | 1 | SDIF AI | 95944 | 139832 | 43888 | 68.6% |
| `large-validation-report` | 2 | CSV Bundle | 95956 | 139832 | 43876 | 68.6% |
| `large-validation-report` | 3 | SDIF | 97634 | 139832 | 42198 | 69.8% |
| `large-validation-report` | 4 | YAML | 137495 | 139832 | 2337 | 98.3% |
| `large-validation-report` | 5 | JSON Compact | 139832 | 139832 | 0 | 100.0% |
| `large-validation-report` | 6 | JSON Pretty | 177596 | 139832 | -37764 | 127.0% |
| `large-validation-report` | 7 | XML | 204665 | 139832 | -64833 | 146.4% |
| `medium-invoice-batch` | 1 | SDIF AI | 18476 | 34890 | 16414 | 53.0% |
| `medium-invoice-batch` | 2 | CSV Bundle | 18486 | 34890 | 16404 | 53.0% |
| `medium-invoice-batch` | 3 | SDIF | 18965 | 34890 | 15925 | 54.4% |
| `medium-invoice-batch` | 4 | YAML | 34258 | 34890 | 632 | 98.2% |
| `medium-invoice-batch` | 5 | JSON Compact | 34890 | 34890 | 0 | 100.0% |
| `medium-invoice-batch` | 6 | JSON Pretty | 47898 | 34890 | -13008 | 137.3% |
| `medium-invoice-batch` | 7 | XML | 59542 | 34890 | -24652 | 170.7% |
| `medium-observability-run` | 1 | SDIF AI | 13983 | 28689 | 14706 | 48.7% |
| `medium-observability-run` | 2 | CSV Bundle | 13995 | 28689 | 14694 | 48.8% |
| `medium-observability-run` | 3 | SDIF | 14595 | 28689 | 14094 | 50.9% |
| `medium-observability-run` | 4 | YAML | 27275 | 28689 | 1414 | 95.1% |
| `medium-observability-run` | 5 | JSON Compact | 28689 | 28689 | 0 | 100.0% |
| `medium-observability-run` | 6 | JSON Pretty | 41996 | 28689 | -13307 | 146.4% |
| `medium-observability-run` | 7 | XML | 51497 | 28689 | -22808 | 179.5% |
| `medium-policy-catalog` | 1 | SDIF AI | 12446 | 24394 | 11948 | 51.0% |
| `medium-policy-catalog` | 2 | CSV Bundle | 12456 | 24394 | 11938 | 51.1% |
| `medium-policy-catalog` | 3 | SDIF | 12918 | 24394 | 11476 | 53.0% |
| `medium-policy-catalog` | 4 | YAML | 22907 | 24394 | 1487 | 93.9% |
| `medium-policy-catalog` | 5 | JSON Compact | 24394 | 24394 | 0 | 100.0% |
| `medium-policy-catalog` | 6 | JSON Pretty | 34838 | 24394 | -10444 | 142.8% |
| `medium-policy-catalog` | 7 | XML | 41875 | 24394 | -17481 | 171.7% |
| `medium-product-catalog` | 1 | SDIF AI | 11888 | 27843 | 15955 | 42.7% |
| `medium-product-catalog` | 2 | CSV Bundle | 11900 | 27843 | 15943 | 42.7% |
| `medium-product-catalog` | 3 | SDIF | 12696 | 27843 | 15147 | 45.6% |
| `medium-product-catalog` | 4 | YAML | 26180 | 27843 | 1663 | 94.0% |
| `medium-product-catalog` | 5 | JSON Compact | 27843 | 27843 | 0 | 100.0% |
| `medium-product-catalog` | 6 | JSON Pretty | 42264 | 27843 | -14421 | 151.8% |
| `medium-product-catalog` | 7 | XML | 53712 | 27843 | -25869 | 192.9% |
| `plan` | 1 | SDIF | 246 | 317 | 71 | 77.6% |
| `plan` | 2 | SDIF AI | 250 | 317 | 67 | 78.9% |
| `plan` | 3 | CSV Bundle | 260 | 317 | 57 | 82.0% |
| `plan` | 4 | YAML | 300 | 317 | 17 | 94.6% |
| `plan` | 5 | JSON Compact | 317 | 317 | 0 | 100.0% |
| `plan` | 6 | JSON Pretty | 422 | 317 | -105 | 133.1% |
| `plan` | 7 | XML | 520 | 317 | -203 | 164.0% |
| `registry` | 1 | SDIF AI | 166 | 240 | 74 | 69.2% |
| `registry` | 2 | SDIF | 169 | 240 | 71 | 70.4% |
| `registry` | 3 | CSV Bundle | 180 | 240 | 60 | 75.0% |
| `registry` | 4 | YAML | 224 | 240 | 16 | 93.3% |
| `registry` | 5 | JSON Compact | 240 | 240 | 0 | 100.0% |
| `registry` | 6 | JSON Pretty | 324 | 240 | -84 | 135.0% |
| `registry` | 7 | XML | 401 | 240 | -161 | 167.1% |
| `schema` | 1 | SDIF AI | 275 | 529 | 254 | 52.0% |
| `schema` | 2 | CSV Bundle | 291 | 529 | 238 | 55.0% |
| `schema` | 3 | SDIF | 291 | 529 | 238 | 55.0% |
| `schema` | 4 | YAML | 501 | 529 | 28 | 94.7% |
| `schema` | 5 | JSON Compact | 529 | 529 | 0 | 100.0% |
| `schema` | 6 | JSON Pretty | 809 | 529 | -280 | 152.9% |
| `schema` | 7 | XML | 1048 | 529 | -519 | 198.1% |
| `small-api-catalog` | 1 | SDIF AI | 410 | 791 | 381 | 51.8% |
| `small-api-catalog` | 2 | CSV Bundle | 417 | 791 | 374 | 52.7% |
| `small-api-catalog` | 3 | SDIF | 429 | 791 | 362 | 54.2% |
| `small-api-catalog` | 4 | YAML | 728 | 791 | 63 | 92.0% |
| `small-api-catalog` | 5 | JSON Compact | 791 | 791 | 0 | 100.0% |
| `small-api-catalog` | 6 | JSON Pretty | 1213 | 791 | -422 | 153.4% |
| `small-api-catalog` | 7 | XML | 1412 | 791 | -621 | 178.5% |
| `small-incident` | 1 | SDIF AI | 641 | 1037 | 396 | 61.8% |
| `small-incident` | 2 | CSV Bundle | 649 | 1037 | 388 | 62.6% |
| `small-incident` | 3 | SDIF | 660 | 1037 | 377 | 63.6% |
| `small-incident` | 4 | YAML | 987 | 1037 | 50 | 95.2% |
| `small-incident` | 5 | JSON Compact | 1037 | 1037 | 0 | 100.0% |
| `small-incident` | 6 | JSON Pretty | 1432 | 1037 | -395 | 138.1% |
| `small-incident` | 7 | XML | 1702 | 1037 | -665 | 164.1% |
| `small-invoice` | 1 | SDIF AI | 352 | 661 | 309 | 53.3% |
| `small-invoice` | 2 | CSV Bundle | 360 | 661 | 301 | 54.5% |
| `small-invoice` | 3 | SDIF | 364 | 661 | 297 | 55.1% |
| `small-invoice` | 4 | YAML | 635 | 661 | 26 | 96.1% |
| `small-invoice` | 5 | JSON Compact | 661 | 661 | 0 | 100.0% |
| `small-invoice` | 6 | JSON Pretty | 941 | 661 | -280 | 142.4% |
| `small-invoice` | 7 | XML | 1185 | 661 | -524 | 179.3% |
| `validation-report` | 1 | SDIF AI | 173 | 254 | 81 | 68.1% |
| `validation-report` | 2 | SDIF | 184 | 254 | 70 | 72.4% |
| `validation-report` | 3 | CSV Bundle | 194 | 254 | 60 | 76.4% |
| `validation-report` | 4 | YAML | 234 | 254 | 20 | 92.1% |
| `validation-report` | 5 | JSON Compact | 254 | 254 | 0 | 100.0% |
| `validation-report` | 6 | JSON Pretty | 345 | 254 | -91 | 135.8% |
| `validation-report` | 7 | XML | 422 | 254 | -168 | 166.1% |
| `wide-table-survey` | 1 | SDIF AI | 4652 | 16230 | 11578 | 28.7% |
| `wide-table-survey` | 2 | CSV Bundle | 4658 | 16230 | 11572 | 28.7% |
| `wide-table-survey` | 3 | SDIF | 4764 | 16230 | 11466 | 29.4% |
| `wide-table-survey` | 4 | JSON Compact | 16230 | 16230 | 0 | 100.0% |
| `wide-table-survey` | 5 | YAML | 17594 | 16230 | -1364 | 108.4% |
| `wide-table-survey` | 6 | JSON Pretty | 31238 | 16230 | -15008 | 192.5% |
| `wide-table-survey` | 7 | XML | 37292 | 16230 | -21062 | 229.8% |

### `TokenX`

Disabled. Disabled through SDIF_BENCHMARK_TOKENX=0.

### `tiktoken`

Unavailable. Unavailable because Python package `tiktoken` is not installed.

### `Llama3`

Disabled. Disabled through SDIF_BENCHMARK_LLAMA=0.

### `Claude`

Disabled. Disabled. Set SDIF_BENCHMARK_CLAUDE=1 to enable API token counting.

## Document Analysis

### `deep-hierarchy-project`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 73179 | 118574 | 45395 | 61.7% |

#### Ratio Matrix

| Format | `Estimate` |
|---|---:|
| SDIF AI | 61.7% |
| CSV Bundle | 61.7% |
| SDIF | 63.7% |
| YAML | 95.3% |
| JSON Compact | 100.0% |
| JSON Pretty | 136.6% |
| XML | 162.0% |

### `github.openapi`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 41843 | 73106 | 31263 | 57.2% |

#### Ratio Matrix

| Format | `Estimate` |
|---|---:|
| SDIF AI | 57.2% |
| CSV Bundle | 57.3% |
| SDIF | 59.4% |
| YAML | 96.9% |
| JSON Compact | 100.0% |
| JSON Pretty | 132.3% |
| XML | 161.6% |

### `large-audit-trail`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 283498 | 432185 | 148687 | 65.6% |

#### Ratio Matrix

| Format | `Estimate` |
|---|---:|
| SDIF AI | 65.6% |
| CSV Bundle | 65.6% |
| SDIF | 66.8% |
| YAML | 96.4% |
| JSON Compact | 100.0% |
| JSON Pretty | 128.5% |
| XML | 149.0% |

### `large-knowledge-graph`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 69895 | 129721 | 59826 | 53.9% |

#### Ratio Matrix

| Format | `Estimate` |
|---|---:|
| SDIF AI | 53.9% |
| CSV Bundle | 53.9% |
| SDIF | 55.7% |
| YAML | 95.4% |
| JSON Compact | 100.0% |
| JSON Pretty | 141.3% |
| XML | 170.4% |

### `large-plan`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 123089 | 201176 | 78087 | 61.2% |

#### Ratio Matrix

| Format | `Estimate` |
|---|---:|
| SDIF AI | 61.2% |
| CSV Bundle | 61.2% |
| SDIF | 62.7% |
| YAML | 97.0% |
| JSON Compact | 100.0% |
| JSON Pretty | 130.3% |
| XML | 158.3% |

### `large-registry`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 100680 | 220956 | 120276 | 45.6% |

#### Ratio Matrix

| Format | `Estimate` |
|---|---:|
| SDIF AI | 45.6% |
| CSV Bundle | 45.6% |
| SDIF | 48.2% |
| YAML | 95.0% |
| JSON Compact | 100.0% |
| JSON Pretty | 145.4% |
| XML | 186.9% |

### `large-schema-catalog`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | CSV Bundle | 53815 | 111880 | 58065 | 48.1% |

#### Ratio Matrix

| Format | `Estimate` |
|---|---:|
| CSV Bundle | 48.1% |
| SDIF AI | 49.5% |
| SDIF | 51.2% |
| YAML | 97.2% |
| JSON Compact | 100.0% |
| JSON Pretty | 145.9% |
| XML | 176.5% |

### `large-support-export`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 85512 | 148025 | 62513 | 57.8% |

#### Ratio Matrix

| Format | `Estimate` |
|---|---:|
| SDIF AI | 57.8% |
| CSV Bundle | 57.8% |
| SDIF | 59.5% |
| YAML | 96.8% |
| JSON Compact | 100.0% |
| JSON Pretty | 136.8% |
| XML | 166.6% |

### `large-validation-report`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 95944 | 139832 | 43888 | 68.6% |

#### Ratio Matrix

| Format | `Estimate` |
|---|---:|
| SDIF AI | 68.6% |
| CSV Bundle | 68.6% |
| SDIF | 69.8% |
| YAML | 98.3% |
| JSON Compact | 100.0% |
| JSON Pretty | 127.0% |
| XML | 146.4% |

### `medium-invoice-batch`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 18476 | 34890 | 16414 | 53.0% |

#### Ratio Matrix

| Format | `Estimate` |
|---|---:|
| SDIF AI | 53.0% |
| CSV Bundle | 53.0% |
| SDIF | 54.4% |
| YAML | 98.2% |
| JSON Compact | 100.0% |
| JSON Pretty | 137.3% |
| XML | 170.7% |

### `medium-observability-run`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 13983 | 28689 | 14706 | 48.7% |

#### Ratio Matrix

| Format | `Estimate` |
|---|---:|
| SDIF AI | 48.7% |
| CSV Bundle | 48.8% |
| SDIF | 50.9% |
| YAML | 95.1% |
| JSON Compact | 100.0% |
| JSON Pretty | 146.4% |
| XML | 179.5% |

### `medium-policy-catalog`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 12446 | 24394 | 11948 | 51.0% |

#### Ratio Matrix

| Format | `Estimate` |
|---|---:|
| SDIF AI | 51.0% |
| CSV Bundle | 51.1% |
| SDIF | 53.0% |
| YAML | 93.9% |
| JSON Compact | 100.0% |
| JSON Pretty | 142.8% |
| XML | 171.7% |

### `medium-product-catalog`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 11888 | 27843 | 15955 | 42.7% |

#### Ratio Matrix

| Format | `Estimate` |
|---|---:|
| SDIF AI | 42.7% |
| CSV Bundle | 42.7% |
| SDIF | 45.6% |
| YAML | 94.0% |
| JSON Compact | 100.0% |
| JSON Pretty | 151.8% |
| XML | 192.9% |

### `plan`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF | 246 | 317 | 71 | 77.6% |

#### Ratio Matrix

| Format | `Estimate` |
|---|---:|
| SDIF | 77.6% |
| SDIF AI | 78.9% |
| CSV Bundle | 82.0% |
| YAML | 94.6% |
| JSON Compact | 100.0% |
| JSON Pretty | 133.1% |
| XML | 164.0% |

### `registry`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 166 | 240 | 74 | 69.2% |

#### Ratio Matrix

| Format | `Estimate` |
|---|---:|
| SDIF AI | 69.2% |
| SDIF | 70.4% |
| CSV Bundle | 75.0% |
| YAML | 93.3% |
| JSON Compact | 100.0% |
| JSON Pretty | 135.0% |
| XML | 167.1% |

### `schema`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 275 | 529 | 254 | 52.0% |

#### Ratio Matrix

| Format | `Estimate` |
|---|---:|
| SDIF AI | 52.0% |
| CSV Bundle | 55.0% |
| SDIF | 55.0% |
| YAML | 94.7% |
| JSON Compact | 100.0% |
| JSON Pretty | 152.9% |
| XML | 198.1% |

### `small-api-catalog`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 410 | 791 | 381 | 51.8% |

#### Ratio Matrix

| Format | `Estimate` |
|---|---:|
| SDIF AI | 51.8% |
| CSV Bundle | 52.7% |
| SDIF | 54.2% |
| YAML | 92.0% |
| JSON Compact | 100.0% |
| JSON Pretty | 153.4% |
| XML | 178.5% |

### `small-incident`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 641 | 1037 | 396 | 61.8% |

#### Ratio Matrix

| Format | `Estimate` |
|---|---:|
| SDIF AI | 61.8% |
| CSV Bundle | 62.6% |
| SDIF | 63.6% |
| YAML | 95.2% |
| JSON Compact | 100.0% |
| JSON Pretty | 138.1% |
| XML | 164.1% |

### `small-invoice`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 352 | 661 | 309 | 53.3% |

#### Ratio Matrix

| Format | `Estimate` |
|---|---:|
| SDIF AI | 53.3% |
| CSV Bundle | 54.5% |
| SDIF | 55.1% |
| YAML | 96.1% |
| JSON Compact | 100.0% |
| JSON Pretty | 142.4% |
| XML | 179.3% |

### `validation-report`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 173 | 254 | 81 | 68.1% |

#### Ratio Matrix

| Format | `Estimate` |
|---|---:|
| SDIF AI | 68.1% |
| SDIF | 72.4% |
| CSV Bundle | 76.4% |
| YAML | 92.1% |
| JSON Compact | 100.0% |
| JSON Pretty | 135.8% |
| XML | 166.1% |

### `wide-table-survey`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 4652 | 16230 | 11578 | 28.7% |

#### Ratio Matrix

| Format | `Estimate` |
|---|---:|
| SDIF AI | 28.7% |
| CSV Bundle | 28.7% |
| SDIF | 29.4% |
| JSON Compact | 100.0% |
| YAML | 108.4% |
| JSON Pretty | 192.5% |
| XML | 229.8% |

## Raw Count Matrix

This section contains raw counts only. Ratios are intentionally excluded here because they are tokenizer-specific.

### `deep-hierarchy-project`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 292716 | 73179 | - | - | - | - |
| CSV Bundle | 292754 | 73189 | - | - | - | - |
| SDIF | 302202 | 75551 | - | - | - | - |
| YAML | 452163 | 113041 | - | - | - | - |
| JSON Compact | 474294 | 118574 | - | - | - | - |
| JSON Pretty | 648068 | 162017 | - | - | - | - |
| XML | 768236 | 192059 | - | - | - | - |

### `github.openapi`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 167369 | 41843 | - | - | - | - |
| CSV Bundle | 167539 | 41885 | - | - | - | - |
| SDIF | 173649 | 43413 | - | - | - | - |
| YAML | 283256 | 70814 | - | - | - | - |
| JSON Compact | 292422 | 73106 | - | - | - | - |
| JSON Pretty | 386842 | 96711 | - | - | - | - |
| XML | 472655 | 118164 | - | - | - | - |

### `large-audit-trail`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 1133989 | 283498 | - | - | - | - |
| CSV Bundle | 1134036 | 283509 | - | - | - | - |
| SDIF | 1155527 | 288882 | - | - | - | - |
| YAML | 1666793 | 416699 | - | - | - | - |
| JSON Compact | 1728738 | 432185 | - | - | - | - |
| JSON Pretty | 2222275 | 555569 | - | - | - | - |
| XML | 2576525 | 644132 | - | - | - | - |

### `large-knowledge-graph`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 279580 | 69895 | - | - | - | - |
| CSV Bundle | 279620 | 69905 | - | - | - | - |
| SDIF | 289242 | 72311 | - | - | - | - |
| YAML | 495208 | 123802 | - | - | - | - |
| JSON Compact | 518882 | 129721 | - | - | - | - |
| JSON Pretty | 733208 | 183302 | - | - | - | - |
| XML | 884387 | 221097 | - | - | - | - |

### `large-plan`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 492354 | 123089 | - | - | - | - |
| CSV Bundle | 492413 | 123104 | - | - | - | - |
| SDIF | 504796 | 126199 | - | - | - | - |
| YAML | 780329 | 195083 | - | - | - | - |
| JSON Compact | 804703 | 201176 | - | - | - | - |
| JSON Pretty | 1048494 | 262124 | - | - | - | - |
| XML | 1273626 | 318407 | - | - | - | - |

### `large-registry`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 402720 | 100680 | - | - | - | - |
| CSV Bundle | 402772 | 100693 | - | - | - | - |
| SDIF | 426166 | 106542 | - | - | - | - |
| YAML | 839949 | 209988 | - | - | - | - |
| JSON Compact | 883824 | 220956 | - | - | - | - |
| JSON Pretty | 1285316 | 321329 | - | - | - | - |
| XML | 1652261 | 413066 | - | - | - | - |

### `large-schema-catalog`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| CSV Bundle | 215257 | 53815 | - | - | - | - |
| SDIF AI | 221599 | 55400 | - | - | - | - |
| SDIF | 228953 | 57239 | - | - | - | - |
| YAML | 435031 | 108758 | - | - | - | - |
| JSON Compact | 447520 | 111880 | - | - | - | - |
| JSON Pretty | 653078 | 163270 | - | - | - | - |
| XML | 790035 | 197509 | - | - | - | - |

### `large-support-export`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 342047 | 85512 | - | - | - | - |
| CSV Bundle | 342094 | 85524 | - | - | - | - |
| SDIF | 352437 | 88110 | - | - | - | - |
| YAML | 573388 | 143347 | - | - | - | - |
| JSON Compact | 592098 | 148025 | - | - | - | - |
| JSON Pretty | 810127 | 202532 | - | - | - | - |
| XML | 986732 | 246683 | - | - | - | - |

### `large-validation-report`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 383776 | 95944 | - | - | - | - |
| CSV Bundle | 383821 | 95956 | - | - | - | - |
| SDIF | 390534 | 97634 | - | - | - | - |
| YAML | 549978 | 137495 | - | - | - | - |
| JSON Compact | 559328 | 139832 | - | - | - | - |
| JSON Pretty | 710381 | 177596 | - | - | - | - |
| XML | 818657 | 204665 | - | - | - | - |

### `medium-invoice-batch`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 73903 | 18476 | - | - | - | - |
| CSV Bundle | 73941 | 18486 | - | - | - | - |
| SDIF | 75859 | 18965 | - | - | - | - |
| YAML | 137030 | 34258 | - | - | - | - |
| JSON Compact | 139558 | 34890 | - | - | - | - |
| JSON Pretty | 191590 | 47898 | - | - | - | - |
| XML | 238165 | 59542 | - | - | - | - |

### `medium-observability-run`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 55931 | 13983 | - | - | - | - |
| CSV Bundle | 55978 | 13995 | - | - | - | - |
| SDIF | 58377 | 14595 | - | - | - | - |
| YAML | 109099 | 27275 | - | - | - | - |
| JSON Compact | 114756 | 28689 | - | - | - | - |
| JSON Pretty | 167981 | 41996 | - | - | - | - |
| XML | 205986 | 51497 | - | - | - | - |

### `medium-policy-catalog`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 49782 | 12446 | - | - | - | - |
| CSV Bundle | 49822 | 12456 | - | - | - | - |
| SDIF | 51672 | 12918 | - | - | - | - |
| YAML | 91628 | 22907 | - | - | - | - |
| JSON Compact | 97573 | 24394 | - | - | - | - |
| JSON Pretty | 139351 | 34838 | - | - | - | - |
| XML | 167499 | 41875 | - | - | - | - |

### `medium-product-catalog`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 47552 | 11888 | - | - | - | - |
| CSV Bundle | 47599 | 11900 | - | - | - | - |
| SDIF | 50784 | 12696 | - | - | - | - |
| YAML | 104720 | 26180 | - | - | - | - |
| JSON Compact | 111369 | 27843 | - | - | - | - |
| JSON Pretty | 169056 | 42264 | - | - | - | - |
| XML | 214848 | 53712 | - | - | - | - |

### `plan`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF | 984 | 246 | - | - | - | - |
| SDIF AI | 1000 | 250 | - | - | - | - |
| CSV Bundle | 1039 | 260 | - | - | - | - |
| YAML | 1197 | 300 | - | - | - | - |
| JSON Compact | 1268 | 317 | - | - | - | - |
| JSON Pretty | 1688 | 422 | - | - | - | - |
| XML | 2080 | 520 | - | - | - | - |

### `registry`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 662 | 166 | - | - | - | - |
| SDIF | 674 | 169 | - | - | - | - |
| CSV Bundle | 720 | 180 | - | - | - | - |
| YAML | 896 | 224 | - | - | - | - |
| JSON Compact | 960 | 240 | - | - | - | - |
| JSON Pretty | 1293 | 324 | - | - | - | - |
| XML | 1601 | 401 | - | - | - | - |

### `schema`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 1097 | 275 | - | - | - | - |
| CSV Bundle | 1161 | 291 | - | - | - | - |
| SDIF | 1161 | 291 | - | - | - | - |
| YAML | 2004 | 501 | - | - | - | - |
| JSON Compact | 2113 | 529 | - | - | - | - |
| JSON Pretty | 3235 | 809 | - | - | - | - |
| XML | 4189 | 1048 | - | - | - | - |

### `small-api-catalog`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 1640 | 410 | - | - | - | - |
| CSV Bundle | 1666 | 417 | - | - | - | - |
| SDIF | 1716 | 429 | - | - | - | - |
| YAML | 2909 | 728 | - | - | - | - |
| JSON Compact | 3163 | 791 | - | - | - | - |
| JSON Pretty | 4849 | 1213 | - | - | - | - |
| XML | 5647 | 1412 | - | - | - | - |

### `small-incident`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 2563 | 641 | - | - | - | - |
| CSV Bundle | 2594 | 649 | - | - | - | - |
| SDIF | 2637 | 660 | - | - | - | - |
| YAML | 3947 | 987 | - | - | - | - |
| JSON Compact | 4148 | 1037 | - | - | - | - |
| JSON Pretty | 5727 | 1432 | - | - | - | - |
| XML | 6808 | 1702 | - | - | - | - |

### `small-invoice`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 1406 | 352 | - | - | - | - |
| CSV Bundle | 1439 | 360 | - | - | - | - |
| SDIF | 1454 | 364 | - | - | - | - |
| YAML | 2537 | 635 | - | - | - | - |
| JSON Compact | 2643 | 661 | - | - | - | - |
| JSON Pretty | 3764 | 941 | - | - | - | - |
| XML | 4738 | 1185 | - | - | - | - |

### `validation-report`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 691 | 173 | - | - | - | - |
| SDIF | 735 | 184 | - | - | - | - |
| CSV Bundle | 773 | 194 | - | - | - | - |
| YAML | 934 | 234 | - | - | - | - |
| JSON Compact | 1014 | 254 | - | - | - | - |
| JSON Pretty | 1378 | 345 | - | - | - | - |
| XML | 1685 | 422 | - | - | - | - |

### `wide-table-survey`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 18606 | 4652 | - | - | - | - |
| CSV Bundle | 18632 | 4658 | - | - | - | - |
| SDIF | 19054 | 4764 | - | - | - | - |
| JSON Compact | 64917 | 16230 | - | - | - | - |
| YAML | 70375 | 17594 | - | - | - | - |
| JSON Pretty | 124951 | 31238 | - | - | - | - |
| XML | 149167 | 37292 | - | - | - | - |

## Environment

| Variable | Value |
| --- | --- |
| `.env loaded` | `yes` |
| `SDIF_BENCHMARK_TOON` | `0` |
| `SDIF_BENCHMARK_TOKENX` | `0` |
| `SDIF_TOKENX_DEFAULT_CHARS_PER_TOKEN` | `6` |
| `SDIF_TOKENX_RESOLVE_DIRS` | `tokenx_tokenizers` |
| `SDIF_BENCHMARK_CLAUDE` | `0` |
| `SDIF_CLAUDE_MODEL` | `claude-sonnet-4-6` |
| `SDIF_BENCHMARK_LLAMA` | `0` |
| `SDIF_LLAMA_TOKENIZER` | `meta-llama/Meta-Llama-3-8B` |
| `SDIF_LLAMA_LOCAL_ONLY` | `1` |
| `SDIF_TIKTOKEN_ENCODING` | `cl100k_base` |
| `HF_TOKEN` | _unset_ |
| `ANTHROPIC_API_KEY` | _unset_ |

## Notes

- TOON skipped because `SDIF_BENCHMARK_TOON=0`.
- `TokenX` is disabled: Disabled through SDIF_BENCHMARK_TOKENX=0.
- `tiktoken` is unavailable: Unavailable because Python package `tiktoken` is not installed.
- `Llama3` is disabled: Disabled through SDIF_BENCHMARK_LLAMA=0.
- `Claude` is disabled: Disabled. Set SDIF_BENCHMARK_CLAUDE=1 to enable API token counting.

## Artifacts

- Raw log: `benchmarks/20260521T170345Z/comparison.log`
- Markdown report: `benchmarks/20260521T170345Z/comparison.md`
- Summary report: `benchmarks/20260521T170345Z/summary.md`
- Structured JSON report: `benchmarks/20260521T170345Z/comparison.json`
- Structured SDIF report: `benchmarks/20260521T170345Z/comparison.sdif`
- SDIF AI projection: `benchmarks/20260521T170345Z/comparison.sdif.ai`
- Latest directory: `benchmarks/latest`
