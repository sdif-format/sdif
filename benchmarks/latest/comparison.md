# SDIF Benchmark Evidence Report

- Generated at: `2026-05-21T15:05:34Z`
- Run directory: `benchmarks/20260521T150432Z`
- Semantic source: `examples/golden/<document>/equivalent.json`
- Ratios are computed independently per tokenizer against `JSON Compact`.
- All formats are derived from the same canonical JSON semantic source.
- Console ordering tokenizer: `tiktoken`
- `.env` loaded: `yes`

## Executive Summary

### Tokenizer Availability

| Tokenizer | Status | Type | Notes |
| --- | --- | --- | --- |
| `Estimate` | available | heuristic | Deterministic fallback: 4 UTF-8 bytes per token. |
| `TokenX` | available | heuristic | Resolved through Node.js, local/global npm, or npx fallback. |
| `tiktoken` | available | model tokenizer | Encoding: cl100k_base. |
| `Llama3` | disabled | model tokenizer | Disabled through SDIF_BENCHMARK_LLAMA=0. |
| `Claude` | disabled | API tokenizer | Disabled. Set SDIF_BENCHMARK_CLAUDE=1 to enable API token counting. |

### Consensus Ranking

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

### Winners by Tokenizer

| Tokenizer | Winner Format | Wins | Documents |
| --- | --- | ---: | ---: |
| `Estimate` | SDIF AI | 20 | 21 |
| `Estimate` | SDIF | 1 | 21 |
| `TokenX` | SDIF AI | 20 | 21 |
| `TokenX` | SDIF | 1 | 21 |
| `tiktoken` | SDIF AI | 19 | 21 |
| `tiktoken` | CSV Bundle | 2 | 21 |

## Tokenizer Results

### `Estimate`

#### Summary

| Format | Avg Rank | Avg Ratio | Median Ratio | Avg Saved Tokens | Wins | Coverage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SDIF AI | 1.05 | 56.1% | 53.9% | 34294 | 20 | 21/21 |
| CSV Bundle | 2.29 | 57.2% | 55.0% | 34281 | 0 | 21/21 |
| SDIF | 2.90 | 58.0% | 55.7% | 32818 | 1 | 21/21 |
| TOON | 3.76 | 58.5% | 56.0% | 32661 | 0 | 21/21 |
| YAML | 5.05 | 96.0% | 95.3% | 2880 | 0 | 21/21 |
| JSON Compact | 5.95 | 100.0% | 100.0% | 0 | 0 | 21/21 |
| JSON Pretty | 7.00 | 142.2% | 138.1% | -29373 | 0 | 21/21 |
| XML | 8.00 | 173.3% | 170.4% | -52146 | 0 | 21/21 |

#### Per-document Ranking

| Document | Rank | Format | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| `deep-hierarchy-project` | 1 | SDIF AI | 73179 | 118574 | 45395 | 61.7% |
| `deep-hierarchy-project` | 2 | CSV Bundle | 73189 | 118574 | 45385 | 61.7% |
| `deep-hierarchy-project` | 3 | SDIF | 75551 | 118574 | 43023 | 63.7% |
| `deep-hierarchy-project` | 4 | TOON | 75554 | 118574 | 43020 | 63.7% |
| `deep-hierarchy-project` | 5 | YAML | 113041 | 118574 | 5533 | 95.3% |
| `deep-hierarchy-project` | 6 | JSON Compact | 118574 | 118574 | 0 | 100.0% |
| `deep-hierarchy-project` | 7 | JSON Pretty | 162017 | 118574 | -43443 | 136.6% |
| `deep-hierarchy-project` | 8 | XML | 192059 | 118574 | -73485 | 162.0% |
| `github.openapi` | 1 | SDIF AI | 41840 | 73106 | 31266 | 57.2% |
| `github.openapi` | 2 | CSV Bundle | 41885 | 73106 | 31221 | 57.3% |
| `github.openapi` | 3 | SDIF | 43413 | 73106 | 29693 | 59.4% |
| `github.openapi` | 4 | TOON | 43613 | 73106 | 29493 | 59.7% |
| `github.openapi` | 5 | YAML | 70814 | 73106 | 2292 | 96.9% |
| `github.openapi` | 6 | JSON Compact | 73106 | 73106 | 0 | 100.0% |
| `github.openapi` | 7 | JSON Pretty | 96711 | 73106 | -23605 | 132.3% |
| `github.openapi` | 8 | XML | 118164 | 73106 | -45058 | 161.6% |
| `large-audit-trail` | 1 | SDIF AI | 283498 | 432185 | 148687 | 65.6% |
| `large-audit-trail` | 2 | CSV Bundle | 283509 | 432185 | 148676 | 65.6% |
| `large-audit-trail` | 3 | SDIF | 288882 | 432185 | 143303 | 66.8% |
| `large-audit-trail` | 4 | TOON | 291646 | 432185 | 140539 | 67.5% |
| `large-audit-trail` | 5 | YAML | 416699 | 432185 | 15486 | 96.4% |
| `large-audit-trail` | 6 | JSON Compact | 432185 | 432185 | 0 | 100.0% |
| `large-audit-trail` | 7 | JSON Pretty | 555569 | 432185 | -123384 | 128.5% |
| `large-audit-trail` | 8 | XML | 644132 | 432185 | -211947 | 149.0% |
| `large-knowledge-graph` | 1 | SDIF AI | 69895 | 129721 | 59826 | 53.9% |
| `large-knowledge-graph` | 2 | CSV Bundle | 69905 | 129721 | 59816 | 53.9% |
| `large-knowledge-graph` | 3 | TOON | 72242 | 129721 | 57479 | 55.7% |
| `large-knowledge-graph` | 4 | SDIF | 72311 | 129721 | 57410 | 55.7% |
| `large-knowledge-graph` | 5 | YAML | 123802 | 129721 | 5919 | 95.4% |
| `large-knowledge-graph` | 6 | JSON Compact | 129721 | 129721 | 0 | 100.0% |
| `large-knowledge-graph` | 7 | JSON Pretty | 183302 | 129721 | -53581 | 141.3% |
| `large-knowledge-graph` | 8 | XML | 221097 | 129721 | -91376 | 170.4% |
| `large-plan` | 1 | SDIF AI | 123088 | 201176 | 78088 | 61.2% |
| `large-plan` | 2 | CSV Bundle | 123104 | 201176 | 78072 | 61.2% |
| `large-plan` | 3 | SDIF | 126199 | 201176 | 74977 | 62.7% |
| `large-plan` | 4 | TOON | 126205 | 201176 | 74971 | 62.7% |
| `large-plan` | 5 | YAML | 195083 | 201176 | 6093 | 97.0% |
| `large-plan` | 6 | JSON Compact | 201176 | 201176 | 0 | 100.0% |
| `large-plan` | 7 | JSON Pretty | 262124 | 201176 | -60948 | 130.3% |
| `large-plan` | 8 | XML | 318407 | 201176 | -117231 | 158.3% |
| `large-registry` | 1 | SDIF AI | 100680 | 220956 | 120276 | 45.6% |
| `large-registry` | 2 | CSV Bundle | 100693 | 220956 | 120263 | 45.6% |
| `large-registry` | 3 | SDIF | 106542 | 220956 | 114414 | 48.2% |
| `large-registry` | 4 | TOON | 106547 | 220956 | 114409 | 48.2% |
| `large-registry` | 5 | YAML | 209988 | 220956 | 10968 | 95.0% |
| `large-registry` | 6 | JSON Compact | 220956 | 220956 | 0 | 100.0% |
| `large-registry` | 7 | JSON Pretty | 321329 | 220956 | -100373 | 145.4% |
| `large-registry` | 8 | XML | 413066 | 220956 | -192110 | 186.9% |
| `large-schema-catalog` | 1 | SDIF AI | 53799 | 111880 | 58081 | 48.1% |
| `large-schema-catalog` | 2 | CSV Bundle | 53815 | 111880 | 58065 | 48.1% |
| `large-schema-catalog` | 3 | SDIF | 57239 | 111880 | 54641 | 51.2% |
| `large-schema-catalog` | 4 | TOON | 57282 | 111880 | 54598 | 51.2% |
| `large-schema-catalog` | 5 | YAML | 108758 | 111880 | 3122 | 97.2% |
| `large-schema-catalog` | 6 | JSON Compact | 111880 | 111880 | 0 | 100.0% |
| `large-schema-catalog` | 7 | JSON Pretty | 163270 | 111880 | -51390 | 145.9% |
| `large-schema-catalog` | 8 | XML | 197509 | 111880 | -85629 | 176.5% |
| `large-support-export` | 1 | SDIF AI | 85512 | 148025 | 62513 | 57.8% |
| `large-support-export` | 2 | CSV Bundle | 85524 | 148025 | 62501 | 57.8% |
| `large-support-export` | 3 | SDIF | 88110 | 148025 | 59915 | 59.5% |
| `large-support-export` | 4 | TOON | 88114 | 148025 | 59911 | 59.5% |
| `large-support-export` | 5 | YAML | 143347 | 148025 | 4678 | 96.8% |
| `large-support-export` | 6 | JSON Compact | 148025 | 148025 | 0 | 100.0% |
| `large-support-export` | 7 | JSON Pretty | 202532 | 148025 | -54507 | 136.8% |
| `large-support-export` | 8 | XML | 246683 | 148025 | -98658 | 166.6% |
| `large-validation-report` | 1 | SDIF AI | 95944 | 139832 | 43888 | 68.6% |
| `large-validation-report` | 2 | CSV Bundle | 95956 | 139832 | 43876 | 68.6% |
| `large-validation-report` | 3 | SDIF | 97634 | 139832 | 42198 | 69.8% |
| `large-validation-report` | 4 | TOON | 97917 | 139832 | 41915 | 70.0% |
| `large-validation-report` | 5 | YAML | 137495 | 139832 | 2337 | 98.3% |
| `large-validation-report` | 6 | JSON Compact | 139832 | 139832 | 0 | 100.0% |
| `large-validation-report` | 7 | JSON Pretty | 177596 | 139832 | -37764 | 127.0% |
| `large-validation-report` | 8 | XML | 204665 | 139832 | -64833 | 146.4% |
| `medium-invoice-batch` | 1 | SDIF AI | 18476 | 34890 | 16414 | 53.0% |
| `medium-invoice-batch` | 2 | CSV Bundle | 18486 | 34890 | 16404 | 53.0% |
| `medium-invoice-batch` | 3 | SDIF | 18965 | 34890 | 15925 | 54.4% |
| `medium-invoice-batch` | 4 | TOON | 18967 | 34890 | 15923 | 54.4% |
| `medium-invoice-batch` | 5 | YAML | 34258 | 34890 | 632 | 98.2% |
| `medium-invoice-batch` | 6 | JSON Compact | 34890 | 34890 | 0 | 100.0% |
| `medium-invoice-batch` | 7 | JSON Pretty | 47898 | 34890 | -13008 | 137.3% |
| `medium-invoice-batch` | 8 | XML | 59542 | 34890 | -24652 | 170.7% |
| `medium-observability-run` | 1 | SDIF AI | 13983 | 28689 | 14706 | 48.7% |
| `medium-observability-run` | 2 | CSV Bundle | 13995 | 28689 | 14694 | 48.8% |
| `medium-observability-run` | 3 | SDIF | 14595 | 28689 | 14094 | 50.9% |
| `medium-observability-run` | 4 | TOON | 14598 | 28689 | 14091 | 50.9% |
| `medium-observability-run` | 5 | YAML | 27275 | 28689 | 1414 | 95.1% |
| `medium-observability-run` | 6 | JSON Compact | 28689 | 28689 | 0 | 100.0% |
| `medium-observability-run` | 7 | JSON Pretty | 41996 | 28689 | -13307 | 146.4% |
| `medium-observability-run` | 8 | XML | 51497 | 28689 | -22808 | 179.5% |
| `medium-policy-catalog` | 1 | SDIF AI | 12446 | 24394 | 11948 | 51.0% |
| `medium-policy-catalog` | 2 | CSV Bundle | 12456 | 24394 | 11938 | 51.1% |
| `medium-policy-catalog` | 3 | SDIF | 12918 | 24394 | 11476 | 53.0% |
| `medium-policy-catalog` | 4 | TOON | 12920 | 24394 | 11474 | 53.0% |
| `medium-policy-catalog` | 5 | YAML | 22907 | 24394 | 1487 | 93.9% |
| `medium-policy-catalog` | 6 | JSON Compact | 24394 | 24394 | 0 | 100.0% |
| `medium-policy-catalog` | 7 | JSON Pretty | 34838 | 24394 | -10444 | 142.8% |
| `medium-policy-catalog` | 8 | XML | 41875 | 24394 | -17481 | 171.7% |
| `medium-product-catalog` | 1 | SDIF AI | 11888 | 27843 | 15955 | 42.7% |
| `medium-product-catalog` | 2 | CSV Bundle | 11900 | 27843 | 15943 | 42.7% |
| `medium-product-catalog` | 3 | SDIF | 12696 | 27843 | 15147 | 45.6% |
| `medium-product-catalog` | 4 | TOON | 12700 | 27843 | 15143 | 45.6% |
| `medium-product-catalog` | 5 | YAML | 26180 | 27843 | 1663 | 94.0% |
| `medium-product-catalog` | 6 | JSON Compact | 27843 | 27843 | 0 | 100.0% |
| `medium-product-catalog` | 7 | JSON Pretty | 42264 | 27843 | -14421 | 151.8% |
| `medium-product-catalog` | 8 | XML | 53712 | 27843 | -25869 | 192.9% |
| `plan` | 1 | SDIF | 246 | 317 | 71 | 77.6% |
| `plan` | 2 | SDIF AI | 250 | 317 | 67 | 78.9% |
| `plan` | 3 | TOON | 251 | 317 | 66 | 79.2% |
| `plan` | 4 | CSV Bundle | 260 | 317 | 57 | 82.0% |
| `plan` | 5 | YAML | 300 | 317 | 17 | 94.6% |
| `plan` | 6 | JSON Compact | 317 | 317 | 0 | 100.0% |
| `plan` | 7 | JSON Pretty | 422 | 317 | -105 | 133.1% |
| `plan` | 8 | XML | 520 | 317 | -203 | 164.0% |
| `registry` | 1 | SDIF AI | 166 | 240 | 74 | 69.2% |
| `registry` | 2 | SDIF | 169 | 240 | 71 | 70.4% |
| `registry` | 3 | TOON | 175 | 240 | 65 | 72.9% |
| `registry` | 4 | CSV Bundle | 180 | 240 | 60 | 75.0% |
| `registry` | 5 | YAML | 224 | 240 | 16 | 93.3% |
| `registry` | 6 | JSON Compact | 240 | 240 | 0 | 100.0% |
| `registry` | 7 | JSON Pretty | 324 | 240 | -84 | 135.0% |
| `registry` | 8 | XML | 401 | 240 | -161 | 167.1% |
| `schema` | 1 | SDIF AI | 275 | 529 | 254 | 52.0% |
| `schema` | 2 | CSV Bundle | 291 | 529 | 238 | 55.0% |
| `schema` | 3 | SDIF | 291 | 529 | 238 | 55.0% |
| `schema` | 4 | TOON | 296 | 529 | 233 | 56.0% |
| `schema` | 5 | YAML | 501 | 529 | 28 | 94.7% |
| `schema` | 6 | JSON Compact | 529 | 529 | 0 | 100.0% |
| `schema` | 7 | JSON Pretty | 809 | 529 | -280 | 152.9% |
| `schema` | 8 | XML | 1048 | 529 | -519 | 198.1% |
| `small-api-catalog` | 1 | SDIF AI | 410 | 791 | 381 | 51.8% |
| `small-api-catalog` | 2 | CSV Bundle | 417 | 791 | 374 | 52.7% |
| `small-api-catalog` | 3 | SDIF | 429 | 791 | 362 | 54.2% |
| `small-api-catalog` | 4 | TOON | 430 | 791 | 361 | 54.4% |
| `small-api-catalog` | 5 | YAML | 728 | 791 | 63 | 92.0% |
| `small-api-catalog` | 6 | JSON Compact | 791 | 791 | 0 | 100.0% |
| `small-api-catalog` | 7 | JSON Pretty | 1213 | 791 | -422 | 153.4% |
| `small-api-catalog` | 8 | XML | 1412 | 791 | -621 | 178.5% |
| `small-incident` | 1 | SDIF AI | 641 | 1037 | 396 | 61.8% |
| `small-incident` | 2 | CSV Bundle | 649 | 1037 | 388 | 62.6% |
| `small-incident` | 3 | SDIF | 660 | 1037 | 377 | 63.6% |
| `small-incident` | 4 | TOON | 660 | 1037 | 377 | 63.6% |
| `small-incident` | 5 | YAML | 987 | 1037 | 50 | 95.2% |
| `small-incident` | 6 | JSON Compact | 1037 | 1037 | 0 | 100.0% |
| `small-incident` | 7 | JSON Pretty | 1432 | 1037 | -395 | 138.1% |
| `small-incident` | 8 | XML | 1702 | 1037 | -665 | 164.1% |
| `small-invoice` | 1 | SDIF AI | 352 | 661 | 309 | 53.3% |
| `small-invoice` | 2 | CSV Bundle | 360 | 661 | 301 | 54.5% |
| `small-invoice` | 3 | SDIF | 364 | 661 | 297 | 55.1% |
| `small-invoice` | 4 | TOON | 365 | 661 | 296 | 55.2% |
| `small-invoice` | 5 | YAML | 635 | 661 | 26 | 96.1% |
| `small-invoice` | 6 | JSON Compact | 661 | 661 | 0 | 100.0% |
| `small-invoice` | 7 | JSON Pretty | 941 | 661 | -280 | 142.4% |
| `small-invoice` | 8 | XML | 1185 | 661 | -524 | 179.3% |
| `validation-report` | 1 | SDIF AI | 173 | 254 | 81 | 68.1% |
| `validation-report` | 2 | SDIF | 184 | 254 | 70 | 72.4% |
| `validation-report` | 3 | TOON | 193 | 254 | 61 | 76.0% |
| `validation-report` | 4 | CSV Bundle | 194 | 254 | 60 | 76.4% |
| `validation-report` | 5 | YAML | 234 | 254 | 20 | 92.1% |
| `validation-report` | 6 | JSON Compact | 254 | 254 | 0 | 100.0% |
| `validation-report` | 7 | JSON Pretty | 345 | 254 | -91 | 135.8% |
| `validation-report` | 8 | XML | 422 | 254 | -168 | 166.1% |
| `wide-table-survey` | 1 | SDIF AI | 4652 | 16230 | 11578 | 28.7% |
| `wide-table-survey` | 2 | CSV Bundle | 4658 | 16230 | 11572 | 28.7% |
| `wide-table-survey` | 3 | TOON | 4764 | 16230 | 11466 | 29.4% |
| `wide-table-survey` | 4 | SDIF | 4764 | 16230 | 11466 | 29.4% |
| `wide-table-survey` | 5 | JSON Compact | 16230 | 16230 | 0 | 100.0% |
| `wide-table-survey` | 6 | YAML | 17594 | 16230 | -1364 | 108.4% |
| `wide-table-survey` | 7 | JSON Pretty | 31238 | 16230 | -15008 | 192.5% |
| `wide-table-survey` | 8 | XML | 37292 | 16230 | -21062 | 229.8% |

### `TokenX`

#### Summary

| Format | Avg Rank | Avg Ratio | Median Ratio | Avg Saved Tokens | Wins | Coverage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SDIF AI | 1.05 | 49.1% | 47.7% | 52917 | 20 | 21/21 |
| SDIF | 1.95 | 49.3% | 47.7% | 52911 | 1 | 21/21 |
| TOON | 3.38 | 59.9% | 57.7% | 42007 | 0 | 21/21 |
| CSV Bundle | 3.62 | 59.7% | 57.1% | 44779 | 0 | 21/21 |
| YAML | 5.00 | 84.1% | 84.3% | 15023 | 0 | 21/21 |
| JSON Compact | 6.00 | 100.0% | 100.0% | 0 | 0 | 21/21 |
| JSON Pretty | 7.00 | 103.1% | 102.8% | -2762 | 0 | 21/21 |
| XML | 8.00 | 158.4% | 157.8% | -51718 | 0 | 21/21 |

#### Per-document Ranking

| Document | Rank | Format | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| `deep-hierarchy-project` | 1 | SDIF AI | 81732 | 150426 | 68694 | 54.3% |
| `deep-hierarchy-project` | 2 | SDIF | 81738 | 150426 | 68688 | 54.3% |
| `deep-hierarchy-project` | 3 | CSV Bundle | 91221 | 150426 | 59205 | 60.6% |
| `deep-hierarchy-project` | 4 | TOON | 91221 | 150426 | 59205 | 60.6% |
| `deep-hierarchy-project` | 5 | YAML | 125936 | 150426 | 24490 | 83.7% |
| `deep-hierarchy-project` | 6 | JSON Compact | 150426 | 150426 | 0 | 100.0% |
| `deep-hierarchy-project` | 7 | JSON Pretty | 155171 | 150426 | -4745 | 103.2% |
| `deep-hierarchy-project` | 8 | XML | 219188 | 150426 | -68762 | 145.7% |
| `github.openapi` | 1 | SDIF AI | 46321 | 90705 | 44384 | 51.1% |
| `github.openapi` | 2 | SDIF | 46333 | 90705 | 44372 | 51.1% |
| `github.openapi` | 3 | CSV Bundle | 52839 | 90705 | 37866 | 58.3% |
| `github.openapi` | 4 | TOON | 53807 | 90705 | 36898 | 59.3% |
| `github.openapi` | 5 | YAML | 77837 | 90705 | 12868 | 85.8% |
| `github.openapi` | 6 | JSON Compact | 90705 | 90705 | 0 | 100.0% |
| `github.openapi` | 7 | JSON Pretty | 92880 | 90705 | -2175 | 102.4% |
| `github.openapi` | 8 | XML | 135694 | 90705 | -44989 | 149.6% |
| `large-audit-trail` | 1 | SDIF AI | 268759 | 536764 | 268005 | 50.1% |
| `large-audit-trail` | 2 | SDIF | 268764 | 536764 | 268000 | 50.1% |
| `large-audit-trail` | 3 | CSV Bundle | 306240 | 536764 | 230524 | 57.1% |
| `large-audit-trail` | 4 | TOON | 357989 | 536764 | 178775 | 66.7% |
| `large-audit-trail` | 5 | YAML | 455642 | 536764 | 81122 | 84.9% |
| `large-audit-trail` | 6 | JSON Compact | 536764 | 536764 | 0 | 100.0% |
| `large-audit-trail` | 7 | JSON Pretty | 547537 | 536764 | -10773 | 102.0% |
| `large-audit-trail` | 8 | XML | 705489 | 536764 | -168725 | 131.4% |
| `large-knowledge-graph` | 1 | SDIF AI | 73765 | 157533 | 83768 | 46.8% |
| `large-knowledge-graph` | 2 | SDIF | 73770 | 157533 | 83763 | 46.8% |
| `large-knowledge-graph` | 3 | TOON | 89415 | 157533 | 68118 | 56.8% |
| `large-knowledge-graph` | 4 | CSV Bundle | 89705 | 157533 | 67828 | 56.9% |
| `large-knowledge-graph` | 5 | YAML | 129722 | 157533 | 27811 | 82.3% |
| `large-knowledge-graph` | 6 | JSON Compact | 157533 | 157533 | 0 | 100.0% |
| `large-knowledge-graph` | 7 | JSON Pretty | 162366 | 157533 | -4833 | 103.1% |
| `large-knowledge-graph` | 8 | XML | 245137 | 157533 | -87604 | 155.6% |
| `large-plan` | 1 | SDIF AI | 143533 | 255952 | 112419 | 56.1% |
| `large-plan` | 2 | SDIF | 143540 | 255952 | 112412 | 56.1% |
| `large-plan` | 3 | CSV Bundle | 159261 | 255952 | 96691 | 62.2% |
| `large-plan` | 4 | TOON | 159262 | 255952 | 96690 | 62.2% |
| `large-plan` | 5 | YAML | 229824 | 255952 | 26128 | 89.8% |
| `large-plan` | 6 | JSON Compact | 255952 | 255952 | 0 | 100.0% |
| `large-plan` | 7 | JSON Pretty | 262181 | 255952 | -6229 | 102.4% |
| `large-plan` | 8 | XML | 381913 | 255952 | -125961 | 149.2% |
| `large-registry` | 1 | SDIF AI | 148685 | 307177 | 158492 | 48.4% |
| `large-registry` | 2 | SDIF | 148692 | 307177 | 158485 | 48.4% |
| `large-registry` | 3 | CSV Bundle | 172514 | 307177 | 134663 | 56.2% |
| `large-registry` | 4 | TOON | 172514 | 307177 | 134663 | 56.2% |
| `large-registry` | 5 | YAML | 279687 | 307177 | 27490 | 91.1% |
| `large-registry` | 6 | JSON Compact | 307177 | 307177 | 0 | 100.0% |
| `large-registry` | 7 | JSON Pretty | 318906 | 307177 | -11729 | 103.8% |
| `large-registry` | 8 | XML | 528580 | 307177 | -221403 | 172.1% |
| `large-schema-catalog` | 1 | SDIF AI | 59883 | 146598 | 86715 | 40.8% |
| `large-schema-catalog` | 2 | SDIF | 59890 | 146598 | 86708 | 40.9% |
| `large-schema-catalog` | 3 | CSV Bundle | 77252 | 146598 | 69346 | 52.7% |
| `large-schema-catalog` | 4 | TOON | 77470 | 146598 | 69128 | 52.8% |
| `large-schema-catalog` | 5 | YAML | 119551 | 146598 | 27047 | 81.6% |
| `large-schema-catalog` | 6 | JSON Compact | 146598 | 146598 | 0 | 100.0% |
| `large-schema-catalog` | 7 | JSON Pretty | 150285 | 146598 | -3687 | 102.5% |
| `large-schema-catalog` | 8 | XML | 235160 | 146598 | -88562 | 160.4% |
| `large-support-export` | 1 | SDIF AI | 81684 | 188515 | 106831 | 43.3% |
| `large-support-export` | 2 | SDIF | 81689 | 188515 | 106826 | 43.3% |
| `large-support-export` | 3 | TOON | 94672 | 188515 | 93843 | 50.2% |
| `large-support-export` | 4 | CSV Bundle | 94673 | 188515 | 93842 | 50.2% |
| `large-support-export` | 5 | YAML | 149111 | 188515 | 39404 | 79.1% |
| `large-support-export` | 6 | JSON Compact | 188515 | 188515 | 0 | 100.0% |
| `large-support-export` | 7 | JSON Pretty | 193714 | 188515 | -5199 | 102.8% |
| `large-support-export` | 8 | XML | 276343 | 188515 | -87828 | 146.6% |
| `large-validation-report` | 1 | SDIF AI | 91316 | 160800 | 69484 | 56.8% |
| `large-validation-report` | 2 | SDIF | 91323 | 160800 | 69477 | 56.8% |
| `large-validation-report` | 3 | CSV Bundle | 100374 | 160800 | 60426 | 62.4% |
| `large-validation-report` | 4 | TOON | 105973 | 160800 | 54827 | 65.9% |
| `large-validation-report` | 5 | YAML | 142953 | 160800 | 17847 | 88.9% |
| `large-validation-report` | 6 | JSON Compact | 160800 | 160800 | 0 | 100.0% |
| `large-validation-report` | 7 | JSON Pretty | 164183 | 160800 | -3383 | 102.1% |
| `large-validation-report` | 8 | XML | 227604 | 160800 | -66804 | 141.5% |
| `medium-invoice-batch` | 1 | SDIF AI | 20700 | 45845 | 25145 | 45.2% |
| `medium-invoice-batch` | 2 | SDIF | 20707 | 45845 | 25138 | 45.2% |
| `medium-invoice-batch` | 3 | TOON | 24954 | 45845 | 20891 | 54.4% |
| `medium-invoice-batch` | 4 | CSV Bundle | 24956 | 45845 | 20889 | 54.4% |
| `medium-invoice-batch` | 5 | YAML | 39703 | 45845 | 6142 | 86.6% |
| `medium-invoice-batch` | 6 | JSON Compact | 45845 | 45845 | 0 | 100.0% |
| `medium-invoice-batch` | 7 | JSON Pretty | 46892 | 45845 | -1047 | 102.3% |
| `medium-invoice-batch` | 8 | XML | 72517 | 45845 | -26672 | 158.2% |
| `medium-observability-run` | 1 | SDIF AI | 16712 | 39221 | 22509 | 42.6% |
| `medium-observability-run` | 2 | SDIF | 16717 | 39221 | 22504 | 42.6% |
| `medium-observability-run` | 3 | TOON | 20632 | 39221 | 18589 | 52.6% |
| `medium-observability-run` | 4 | CSV Bundle | 20633 | 39221 | 18588 | 52.6% |
| `medium-observability-run` | 5 | YAML | 33200 | 39221 | 6021 | 84.6% |
| `medium-observability-run` | 6 | JSON Compact | 39221 | 39221 | 0 | 100.0% |
| `medium-observability-run` | 7 | JSON Pretty | 40448 | 39221 | -1227 | 103.1% |
| `medium-observability-run` | 8 | XML | 64697 | 39221 | -25476 | 165.0% |
| `medium-policy-catalog` | 1 | SDIF AI | 16021 | 33616 | 17595 | 47.7% |
| `medium-policy-catalog` | 2 | SDIF | 16026 | 33616 | 17590 | 47.7% |
| `medium-policy-catalog` | 3 | TOON | 19134 | 33616 | 14482 | 56.9% |
| `medium-policy-catalog` | 4 | CSV Bundle | 19136 | 33616 | 14480 | 56.9% |
| `medium-policy-catalog` | 5 | YAML | 27840 | 33616 | 5776 | 82.8% |
| `medium-policy-catalog` | 6 | JSON Compact | 33616 | 33616 | 0 | 100.0% |
| `medium-policy-catalog` | 7 | JSON Pretty | 34563 | 33616 | -947 | 102.8% |
| `medium-policy-catalog` | 8 | XML | 51599 | 33616 | -17983 | 153.5% |
| `medium-product-catalog` | 1 | SDIF AI | 14784 | 37474 | 22690 | 39.5% |
| `medium-product-catalog` | 2 | SDIF | 14789 | 37474 | 22685 | 39.5% |
| `medium-product-catalog` | 3 | TOON | 18377 | 37474 | 19097 | 49.0% |
| `medium-product-catalog` | 4 | CSV Bundle | 18378 | 37474 | 19096 | 49.0% |
| `medium-product-catalog` | 5 | YAML | 32289 | 37474 | 5185 | 86.2% |
| `medium-product-catalog` | 6 | JSON Compact | 37474 | 37474 | 0 | 100.0% |
| `medium-product-catalog` | 7 | JSON Pretty | 39094 | 37474 | -1620 | 104.3% |
| `medium-product-catalog` | 8 | XML | 66733 | 37474 | -29259 | 178.1% |
| `plan` | 1 | SDIF | 266 | 389 | 123 | 68.4% |
| `plan` | 2 | SDIF AI | 274 | 389 | 115 | 70.4% |
| `plan` | 3 | TOON | 307 | 389 | 82 | 78.9% |
| `plan` | 4 | CSV Bundle | 324 | 389 | 65 | 83.3% |
| `plan` | 5 | YAML | 333 | 389 | 56 | 85.6% |
| `plan` | 6 | JSON Compact | 389 | 389 | 0 | 100.0% |
| `plan` | 7 | JSON Pretty | 406 | 389 | -17 | 104.4% |
| `plan` | 8 | XML | 614 | 389 | -225 | 157.8% |
| `registry` | 1 | SDIF AI | 190 | 301 | 111 | 63.1% |
| `registry` | 2 | SDIF | 192 | 301 | 109 | 63.8% |
| `registry` | 3 | TOON | 227 | 301 | 74 | 75.4% |
| `registry` | 4 | CSV Bundle | 240 | 301 | 61 | 79.7% |
| `registry` | 5 | YAML | 255 | 301 | 46 | 84.7% |
| `registry` | 6 | JSON Compact | 301 | 301 | 0 | 100.0% |
| `registry` | 7 | JSON Pretty | 313 | 301 | -12 | 104.0% |
| `registry` | 8 | XML | 478 | 301 | -177 | 158.8% |
| `schema` | 1 | SDIF AI | 291 | 665 | 374 | 43.8% |
| `schema` | 2 | SDIF | 296 | 665 | 369 | 44.5% |
| `schema` | 3 | CSV Bundle | 384 | 665 | 281 | 57.7% |
| `schema` | 4 | TOON | 384 | 665 | 281 | 57.7% |
| `schema` | 5 | YAML | 554 | 665 | 111 | 83.3% |
| `schema` | 6 | JSON Compact | 665 | 665 | 0 | 100.0% |
| `schema` | 7 | JSON Pretty | 703 | 665 | -38 | 105.7% |
| `schema` | 8 | XML | 1242 | 665 | -577 | 186.8% |
| `small-api-catalog` | 1 | SDIF AI | 516 | 1126 | 610 | 45.8% |
| `small-api-catalog` | 2 | SDIF | 521 | 1126 | 605 | 46.3% |
| `small-api-catalog` | 3 | TOON | 624 | 1126 | 502 | 55.4% |
| `small-api-catalog` | 4 | CSV Bundle | 628 | 1126 | 498 | 55.8% |
| `small-api-catalog` | 5 | YAML | 876 | 1126 | 250 | 77.8% |
| `small-api-catalog` | 6 | JSON Compact | 1126 | 1126 | 0 | 100.0% |
| `small-api-catalog` | 7 | JSON Pretty | 1162 | 1126 | -36 | 103.2% |
| `small-api-catalog` | 8 | XML | 1742 | 1126 | -616 | 154.7% |
| `small-incident` | 1 | SDIF AI | 692 | 1304 | 612 | 53.1% |
| `small-incident` | 2 | SDIF | 698 | 1304 | 606 | 53.5% |
| `small-incident` | 3 | TOON | 824 | 1304 | 480 | 63.2% |
| `small-incident` | 4 | CSV Bundle | 827 | 1304 | 477 | 63.4% |
| `small-incident` | 5 | YAML | 1077 | 1304 | 227 | 82.6% |
| `small-incident` | 6 | JSON Compact | 1304 | 1304 | 0 | 100.0% |
| `small-incident` | 7 | JSON Pretty | 1341 | 1304 | -37 | 102.8% |
| `small-incident` | 8 | XML | 1968 | 1304 | -664 | 150.9% |
| `small-invoice` | 1 | SDIF AI | 391 | 848 | 457 | 46.1% |
| `small-invoice` | 2 | SDIF | 396 | 848 | 452 | 46.7% |
| `small-invoice` | 3 | TOON | 495 | 848 | 353 | 58.4% |
| `small-invoice` | 4 | CSV Bundle | 498 | 848 | 350 | 58.7% |
| `small-invoice` | 5 | YAML | 715 | 848 | 133 | 84.3% |
| `small-invoice` | 6 | JSON Compact | 848 | 848 | 0 | 100.0% |
| `small-invoice` | 7 | JSON Pretty | 872 | 848 | -24 | 102.8% |
| `small-invoice` | 8 | XML | 1443 | 848 | -595 | 170.2% |
| `validation-report` | 1 | SDIF AI | 180 | 300 | 120 | 60.0% |
| `validation-report` | 2 | SDIF | 190 | 300 | 110 | 63.3% |
| `validation-report` | 3 | TOON | 226 | 300 | 74 | 75.3% |
| `validation-report` | 4 | CSV Bundle | 228 | 300 | 72 | 76.0% |
| `validation-report` | 5 | YAML | 253 | 300 | 47 | 84.3% |
| `validation-report` | 6 | JSON Compact | 300 | 300 | 0 | 100.0% |
| `validation-report` | 7 | JSON Pretty | 316 | 300 | -16 | 105.3% |
| `validation-report` | 8 | XML | 494 | 300 | -194 | 164.7% |
| `wide-table-survey` | 1 | SDIF AI | 7878 | 29998 | 22120 | 26.3% |
| `wide-table-survey` | 2 | SDIF | 7883 | 29998 | 22115 | 26.3% |
| `wide-table-survey` | 3 | TOON | 14893 | 29998 | 15105 | 49.6% |
| `wide-table-survey` | 4 | CSV Bundle | 14897 | 29998 | 15101 | 49.7% |
| `wide-table-survey` | 5 | YAML | 22708 | 29998 | 7290 | 75.7% |
| `wide-table-survey` | 6 | JSON Compact | 29998 | 29998 | 0 | 100.0% |
| `wide-table-survey` | 7 | JSON Pretty | 30220 | 29998 | -222 | 100.7% |
| `wide-table-survey` | 8 | XML | 52992 | 29998 | -22994 | 176.7% |

### `tiktoken`

#### Summary

| Format | Avg Rank | Avg Ratio | Median Ratio | Avg Saved Tokens | Wins | Coverage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SDIF AI | 1.10 | 64.6% | 64.8% | 29837 | 19 | 21/21 |
| CSV Bundle | 2.29 | 68.3% | 66.6% | 28530 | 2 | 21/21 |
| SDIF | 2.95 | 68.5% | 68.0% | 26522 | 0 | 21/21 |
| TOON | 3.67 | 70.8% | 69.7% | 25577 | 0 | 21/21 |
| JSON Compact | 5.00 | 100.0% | 100.0% | 0 | 0 | 21/21 |
| YAML | 6.00 | 115.0% | 114.3% | -11129 | 0 | 21/21 |
| JSON Pretty | 7.00 | 157.4% | 157.7% | -43403 | 0 | 21/21 |
| XML | 8.00 | 191.5% | 191.6% | -69336 | 0 | 21/21 |

#### Per-document Ranking

| Document | Rank | Format | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| `deep-hierarchy-project` | 1 | CSV Bundle | 101645 | 137942 | 36297 | 73.7% |
| `deep-hierarchy-project` | 2 | SDIF AI | 103204 | 137942 | 34738 | 74.8% |
| `deep-hierarchy-project` | 3 | TOON | 106382 | 137942 | 31560 | 77.1% |
| `deep-hierarchy-project` | 4 | SDIF | 107951 | 137942 | 29991 | 78.3% |
| `deep-hierarchy-project` | 5 | JSON Compact | 137942 | 137942 | 0 | 100.0% |
| `deep-hierarchy-project` | 6 | YAML | 153735 | 137942 | -15793 | 111.4% |
| `deep-hierarchy-project` | 7 | JSON Pretty | 204303 | 137942 | -66361 | 148.1% |
| `deep-hierarchy-project` | 8 | XML | 243817 | 137942 | -105875 | 176.8% |
| `github.openapi` | 1 | SDIF AI | 37824 | 62704 | 24880 | 60.3% |
| `github.openapi` | 2 | CSV Bundle | 39074 | 62704 | 23630 | 62.3% |
| `github.openapi` | 3 | TOON | 41529 | 62704 | 21175 | 66.2% |
| `github.openapi` | 4 | SDIF | 41867 | 62704 | 20837 | 66.8% |
| `github.openapi` | 5 | JSON Compact | 62704 | 62704 | 0 | 100.0% |
| `github.openapi` | 6 | YAML | 72783 | 62704 | -10079 | 116.1% |
| `github.openapi` | 7 | JSON Pretty | 97266 | 62704 | -34562 | 155.1% |
| `github.openapi` | 8 | XML | 117756 | 62704 | -55052 | 187.8% |
| `large-audit-trail` | 1 | SDIF AI | 412926 | 540663 | 127737 | 76.4% |
| `large-audit-trail` | 2 | CSV Bundle | 422357 | 540663 | 118306 | 78.1% |
| `large-audit-trail` | 3 | SDIF | 423698 | 540663 | 116965 | 78.4% |
| `large-audit-trail` | 4 | TOON | 433120 | 540663 | 107543 | 80.1% |
| `large-audit-trail` | 5 | JSON Compact | 540663 | 540663 | 0 | 100.0% |
| `large-audit-trail` | 6 | YAML | 584405 | 540663 | -43742 | 108.1% |
| `large-audit-trail` | 7 | JSON Pretty | 723268 | 540663 | -182605 | 133.8% |
| `large-audit-trail` | 8 | XML | 831285 | 540663 | -290622 | 153.8% |
| `large-knowledge-graph` | 1 | SDIF AI | 86155 | 132864 | 46709 | 64.8% |
| `large-knowledge-graph` | 2 | CSV Bundle | 88495 | 132864 | 44369 | 66.6% |
| `large-knowledge-graph` | 3 | SDIF | 90989 | 132864 | 41875 | 68.5% |
| `large-knowledge-graph` | 4 | TOON | 93032 | 132864 | 39832 | 70.0% |
| `large-knowledge-graph` | 5 | JSON Compact | 132864 | 132864 | 0 | 100.0% |
| `large-knowledge-graph` | 6 | YAML | 153731 | 132864 | -20867 | 115.7% |
| `large-knowledge-graph` | 7 | JSON Pretty | 213005 | 132864 | -80141 | 160.3% |
| `large-knowledge-graph` | 8 | XML | 254541 | 132864 | -121677 | 191.6% |
| `large-plan` | 1 | SDIF AI | 141143 | 213238 | 72095 | 66.2% |
| `large-plan` | 2 | CSV Bundle | 144465 | 213238 | 68773 | 67.7% |
| `large-plan` | 3 | SDIF | 147369 | 213238 | 65869 | 69.1% |
| `large-plan` | 4 | TOON | 150679 | 213238 | 62559 | 70.7% |
| `large-plan` | 5 | JSON Compact | 213238 | 213238 | 0 | 100.0% |
| `large-plan` | 6 | YAML | 229718 | 213238 | -16480 | 107.7% |
| `large-plan` | 7 | JSON Pretty | 302381 | 213238 | -89143 | 141.8% |
| `large-plan` | 8 | XML | 366170 | 213238 | -152932 | 171.7% |
| `large-registry` | 1 | SDIF AI | 154449 | 253063 | 98614 | 61.0% |
| `large-registry` | 2 | CSV Bundle | 159696 | 253063 | 93367 | 63.1% |
| `large-registry` | 3 | SDIF | 166177 | 253063 | 86886 | 65.7% |
| `large-registry` | 4 | TOON | 171412 | 253063 | 81651 | 67.7% |
| `large-registry` | 5 | JSON Compact | 253063 | 253063 | 0 | 100.0% |
| `large-registry` | 6 | YAML | 283892 | 253063 | -30829 | 112.2% |
| `large-registry` | 7 | JSON Pretty | 399186 | 253063 | -146123 | 157.7% |
| `large-registry` | 8 | XML | 494780 | 253063 | -241717 | 195.5% |
| `large-schema-catalog` | 1 | SDIF AI | 66788 | 126532 | 59744 | 52.8% |
| `large-schema-catalog` | 2 | CSV Bundle | 71357 | 126532 | 55175 | 56.4% |
| `large-schema-catalog` | 3 | TOON | 78231 | 126532 | 48301 | 61.8% |
| `large-schema-catalog` | 4 | SDIF | 79144 | 126532 | 47388 | 62.5% |
| `large-schema-catalog` | 5 | JSON Compact | 126532 | 126532 | 0 | 100.0% |
| `large-schema-catalog` | 6 | YAML | 149601 | 126532 | -23069 | 118.2% |
| `large-schema-catalog` | 7 | JSON Pretty | 199367 | 126532 | -72835 | 157.6% |
| `large-schema-catalog` | 8 | XML | 235726 | 126532 | -109194 | 186.3% |
| `large-support-export` | 1 | SDIF AI | 94839 | 149622 | 54783 | 63.4% |
| `large-support-export` | 2 | CSV Bundle | 96002 | 149622 | 53620 | 64.2% |
| `large-support-export` | 3 | SDIF | 100037 | 149622 | 49585 | 66.9% |
| `large-support-export` | 4 | TOON | 101190 | 149622 | 48432 | 67.6% |
| `large-support-export` | 5 | JSON Compact | 149622 | 149622 | 0 | 100.0% |
| `large-support-export` | 6 | YAML | 169236 | 149622 | -19614 | 113.1% |
| `large-support-export` | 7 | JSON Pretty | 229579 | 149622 | -79957 | 153.4% |
| `large-support-export` | 8 | XML | 274660 | 149622 | -125038 | 183.6% |
| `large-validation-report` | 1 | SDIF AI | 99631 | 134533 | 34902 | 74.1% |
| `large-validation-report` | 2 | CSV Bundle | 99656 | 134533 | 34877 | 74.1% |
| `large-validation-report` | 3 | SDIF | 103015 | 134533 | 31518 | 76.6% |
| `large-validation-report` | 4 | TOON | 103027 | 134533 | 31506 | 76.6% |
| `large-validation-report` | 5 | JSON Compact | 134533 | 134533 | 0 | 100.0% |
| `large-validation-report` | 6 | YAML | 150198 | 134533 | -15665 | 111.6% |
| `large-validation-report` | 7 | JSON Pretty | 192034 | 134533 | -57501 | 142.7% |
| `large-validation-report` | 8 | XML | 225834 | 134533 | -91301 | 167.9% |
| `medium-invoice-batch` | 1 | CSV Bundle | 25965 | 39858 | 13893 | 65.1% |
| `medium-invoice-batch` | 2 | SDIF AI | 26706 | 39858 | 13152 | 67.0% |
| `medium-invoice-batch` | 3 | TOON | 26932 | 39858 | 12926 | 67.6% |
| `medium-invoice-batch` | 4 | SDIF | 27688 | 39858 | 12170 | 69.5% |
| `medium-invoice-batch` | 5 | JSON Compact | 39858 | 39858 | 0 | 100.0% |
| `medium-invoice-batch` | 6 | YAML | 46758 | 39858 | -6900 | 117.3% |
| `medium-invoice-batch` | 7 | JSON Pretty | 58931 | 39858 | -19073 | 147.9% |
| `medium-invoice-batch` | 8 | XML | 70501 | 39858 | -30643 | 176.9% |
| `medium-observability-run` | 1 | SDIF AI | 18170 | 32253 | 14083 | 56.3% |
| `medium-observability-run` | 2 | CSV Bundle | 19018 | 32253 | 13235 | 59.0% |
| `medium-observability-run` | 3 | SDIF | 20572 | 32253 | 11681 | 63.8% |
| `medium-observability-run` | 4 | TOON | 21408 | 32253 | 10845 | 66.4% |
| `medium-observability-run` | 5 | JSON Compact | 32253 | 32253 | 0 | 100.0% |
| `medium-observability-run` | 6 | YAML | 38569 | 32253 | -6316 | 119.6% |
| `medium-observability-run` | 7 | JSON Pretty | 52300 | 32253 | -20047 | 162.2% |
| `medium-observability-run` | 8 | XML | 63274 | 32253 | -31021 | 196.2% |
| `medium-policy-catalog` | 1 | SDIF AI | 18106 | 28086 | 9980 | 64.5% |
| `medium-policy-catalog` | 2 | SDIF | 19054 | 28086 | 9032 | 67.8% |
| `medium-policy-catalog` | 3 | CSV Bundle | 19159 | 28086 | 8927 | 68.2% |
| `medium-policy-catalog` | 4 | TOON | 20095 | 28086 | 7991 | 71.5% |
| `medium-policy-catalog` | 5 | JSON Compact | 28086 | 28086 | 0 | 100.0% |
| `medium-policy-catalog` | 6 | YAML | 32094 | 28086 | -4008 | 114.3% |
| `medium-policy-catalog` | 7 | JSON Pretty | 43999 | 28086 | -15913 | 156.7% |
| `medium-policy-catalog` | 8 | XML | 52678 | 28086 | -24592 | 187.6% |
| `medium-product-catalog` | 1 | SDIF AI | 21319 | 33936 | 12617 | 62.8% |
| `medium-product-catalog` | 2 | CSV Bundle | 21445 | 33936 | 12491 | 63.2% |
| `medium-product-catalog` | 3 | SDIF | 22938 | 33936 | 10998 | 67.6% |
| `medium-product-catalog` | 4 | TOON | 23051 | 33936 | 10885 | 67.9% |
| `medium-product-catalog` | 5 | JSON Compact | 33936 | 33936 | 0 | 100.0% |
| `medium-product-catalog` | 6 | YAML | 39958 | 33936 | -6022 | 117.7% |
| `medium-product-catalog` | 7 | JSON Pretty | 55984 | 33936 | -22048 | 165.0% |
| `medium-product-catalog` | 8 | XML | 69082 | 33936 | -35146 | 203.6% |
| `plan` | 1 | SDIF AI | 250 | 302 | 52 | 82.8% |
| `plan` | 2 | SDIF | 252 | 302 | 50 | 83.4% |
| `plan` | 3 | TOON | 276 | 302 | 26 | 91.4% |
| `plan` | 4 | CSV Bundle | 288 | 302 | 14 | 95.4% |
| `plan` | 5 | JSON Compact | 302 | 302 | 0 | 100.0% |
| `plan` | 6 | YAML | 334 | 302 | -32 | 110.6% |
| `plan` | 7 | JSON Pretty | 479 | 302 | -177 | 158.6% |
| `plan` | 8 | XML | 602 | 302 | -300 | 199.3% |
| `registry` | 1 | SDIF AI | 149 | 205 | 56 | 72.7% |
| `registry` | 2 | SDIF | 154 | 205 | 51 | 75.1% |
| `registry` | 3 | TOON | 169 | 205 | 36 | 82.4% |
| `registry` | 4 | CSV Bundle | 175 | 205 | 30 | 85.4% |
| `registry` | 5 | JSON Compact | 205 | 205 | 0 | 100.0% |
| `registry` | 6 | YAML | 220 | 205 | -15 | 107.3% |
| `registry` | 7 | JSON Pretty | 341 | 205 | -136 | 166.3% |
| `registry` | 8 | XML | 438 | 205 | -233 | 213.7% |
| `schema` | 1 | SDIF AI | 298 | 534 | 236 | 55.8% |
| `schema` | 2 | SDIF | 323 | 534 | 211 | 60.5% |
| `schema` | 3 | CSV Bundle | 331 | 534 | 203 | 62.0% |
| `schema` | 4 | TOON | 342 | 534 | 192 | 64.0% |
| `schema` | 5 | JSON Compact | 534 | 534 | 0 | 100.0% |
| `schema` | 6 | YAML | 630 | 534 | -96 | 118.0% |
| `schema` | 7 | JSON Pretty | 953 | 534 | -419 | 178.5% |
| `schema` | 8 | XML | 1213 | 534 | -679 | 227.2% |
| `small-api-catalog` | 1 | SDIF AI | 544 | 912 | 368 | 59.6% |
| `small-api-catalog` | 2 | CSV Bundle | 585 | 912 | 327 | 64.1% |
| `small-api-catalog` | 3 | SDIF | 585 | 912 | 327 | 64.1% |
| `small-api-catalog` | 4 | TOON | 615 | 912 | 297 | 67.4% |
| `small-api-catalog` | 5 | JSON Compact | 912 | 912 | 0 | 100.0% |
| `small-api-catalog` | 6 | YAML | 1109 | 912 | -197 | 121.6% |
| `small-api-catalog` | 7 | JSON Pretty | 1564 | 912 | -652 | 171.5% |
| `small-api-catalog` | 8 | XML | 1894 | 912 | -982 | 207.7% |
| `small-incident` | 1 | SDIF AI | 704 | 1064 | 360 | 66.2% |
| `small-incident` | 2 | SDIF | 723 | 1064 | 341 | 68.0% |
| `small-incident` | 3 | CSV Bundle | 740 | 1064 | 324 | 69.5% |
| `small-incident` | 4 | TOON | 742 | 1064 | 322 | 69.7% |
| `small-incident` | 5 | JSON Compact | 1064 | 1064 | 0 | 100.0% |
| `small-incident` | 6 | YAML | 1157 | 1064 | -93 | 108.7% |
| `small-incident` | 7 | JSON Pretty | 1657 | 1064 | -593 | 155.7% |
| `small-incident` | 8 | XML | 1941 | 1064 | -877 | 182.4% |
| `small-invoice` | 1 | SDIF AI | 476 | 718 | 242 | 66.3% |
| `small-invoice` | 2 | CSV Bundle | 485 | 718 | 233 | 67.5% |
| `small-invoice` | 3 | TOON | 501 | 718 | 217 | 69.8% |
| `small-invoice` | 4 | SDIF | 503 | 718 | 215 | 70.1% |
| `small-invoice` | 5 | JSON Compact | 718 | 718 | 0 | 100.0% |
| `small-invoice` | 6 | YAML | 850 | 718 | -132 | 118.4% |
| `small-invoice` | 7 | JSON Pretty | 1159 | 718 | -441 | 161.4% |
| `small-invoice` | 8 | XML | 1414 | 718 | -696 | 196.9% |
| `validation-report` | 1 | SDIF AI | 149 | 225 | 76 | 66.2% |
| `validation-report` | 2 | SDIF | 166 | 225 | 59 | 73.8% |
| `validation-report` | 3 | CSV Bundle | 195 | 225 | 30 | 86.7% |
| `validation-report` | 4 | TOON | 197 | 225 | 28 | 87.6% |
| `validation-report` | 5 | JSON Compact | 225 | 225 | 0 | 100.0% |
| `validation-report` | 6 | YAML | 246 | 225 | -21 | 109.3% |
| `validation-report` | 7 | JSON Pretty | 382 | 225 | -157 | 169.8% |
| `validation-report` | 8 | XML | 480 | 225 | -255 | 213.3% |
| `wide-table-survey` | 1 | SDIF AI | 15224 | 36372 | 21148 | 41.9% |
| `wide-table-survey` | 2 | CSV Bundle | 15365 | 36372 | 21007 | 42.2% |
| `wide-table-survey` | 3 | SDIF | 15451 | 36372 | 20921 | 42.5% |
| `wide-table-survey` | 4 | TOON | 15579 | 36372 | 20793 | 42.8% |
| `wide-table-survey` | 5 | JSON Compact | 36372 | 36372 | 0 | 100.0% |
| `wide-table-survey` | 6 | YAML | 50113 | 36372 | -13741 | 137.8% |
| `wide-table-survey` | 7 | JSON Pretty | 58948 | 36372 | -22576 | 162.1% |
| `wide-table-survey` | 8 | XML | 73594 | 36372 | -37222 | 202.3% |

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
| `TokenX` | SDIF AI | 81732 | 150426 | 68694 | 54.3% |
| `tiktoken` | CSV Bundle | 101645 | 137942 | 36297 | 73.7% |

#### Ratio Matrix

| Format | `Estimate` | `TokenX` | `tiktoken` |
|---|---:|---:|---:|
| SDIF AI | 61.7% | 54.3% | 74.8% |
| CSV Bundle | 61.7% | 60.6% | 73.7% |
| SDIF | 63.7% | 54.3% | 78.3% |
| TOON | 63.7% | 60.6% | 77.1% |
| YAML | 95.3% | 83.7% | 111.4% |
| JSON Compact | 100.0% | 100.0% | 100.0% |
| JSON Pretty | 136.6% | 103.2% | 148.1% |
| XML | 162.0% | 145.7% | 176.8% |

### `github.openapi`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 41840 | 73106 | 31266 | 57.2% |
| `TokenX` | SDIF AI | 46321 | 90705 | 44384 | 51.1% |
| `tiktoken` | SDIF AI | 37824 | 62704 | 24880 | 60.3% |

#### Ratio Matrix

| Format | `Estimate` | `TokenX` | `tiktoken` |
|---|---:|---:|---:|
| SDIF AI | 57.2% | 51.1% | 60.3% |
| CSV Bundle | 57.3% | 58.3% | 62.3% |
| SDIF | 59.4% | 51.1% | 66.8% |
| TOON | 59.7% | 59.3% | 66.2% |
| YAML | 96.9% | 85.8% | 116.1% |
| JSON Compact | 100.0% | 100.0% | 100.0% |
| JSON Pretty | 132.3% | 102.4% | 155.1% |
| XML | 161.6% | 149.6% | 187.8% |

### `large-audit-trail`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 283498 | 432185 | 148687 | 65.6% |
| `TokenX` | SDIF AI | 268759 | 536764 | 268005 | 50.1% |
| `tiktoken` | SDIF AI | 412926 | 540663 | 127737 | 76.4% |

#### Ratio Matrix

| Format | `Estimate` | `TokenX` | `tiktoken` |
|---|---:|---:|---:|
| SDIF AI | 65.6% | 50.1% | 76.4% |
| CSV Bundle | 65.6% | 57.1% | 78.1% |
| SDIF | 66.8% | 50.1% | 78.4% |
| TOON | 67.5% | 66.7% | 80.1% |
| YAML | 96.4% | 84.9% | 108.1% |
| JSON Compact | 100.0% | 100.0% | 100.0% |
| JSON Pretty | 128.5% | 102.0% | 133.8% |
| XML | 149.0% | 131.4% | 153.8% |

### `large-knowledge-graph`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 69895 | 129721 | 59826 | 53.9% |
| `TokenX` | SDIF AI | 73765 | 157533 | 83768 | 46.8% |
| `tiktoken` | SDIF AI | 86155 | 132864 | 46709 | 64.8% |

#### Ratio Matrix

| Format | `Estimate` | `TokenX` | `tiktoken` |
|---|---:|---:|---:|
| SDIF AI | 53.9% | 46.8% | 64.8% |
| CSV Bundle | 53.9% | 56.9% | 66.6% |
| SDIF | 55.7% | 46.8% | 68.5% |
| TOON | 55.7% | 56.8% | 70.0% |
| YAML | 95.4% | 82.3% | 115.7% |
| JSON Compact | 100.0% | 100.0% | 100.0% |
| JSON Pretty | 141.3% | 103.1% | 160.3% |
| XML | 170.4% | 155.6% | 191.6% |

### `large-plan`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 123088 | 201176 | 78088 | 61.2% |
| `TokenX` | SDIF AI | 143533 | 255952 | 112419 | 56.1% |
| `tiktoken` | SDIF AI | 141143 | 213238 | 72095 | 66.2% |

#### Ratio Matrix

| Format | `Estimate` | `TokenX` | `tiktoken` |
|---|---:|---:|---:|
| SDIF AI | 61.2% | 56.1% | 66.2% |
| CSV Bundle | 61.2% | 62.2% | 67.7% |
| SDIF | 62.7% | 56.1% | 69.1% |
| TOON | 62.7% | 62.2% | 70.7% |
| YAML | 97.0% | 89.8% | 107.7% |
| JSON Compact | 100.0% | 100.0% | 100.0% |
| JSON Pretty | 130.3% | 102.4% | 141.8% |
| XML | 158.3% | 149.2% | 171.7% |

### `large-registry`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 100680 | 220956 | 120276 | 45.6% |
| `TokenX` | SDIF AI | 148685 | 307177 | 158492 | 48.4% |
| `tiktoken` | SDIF AI | 154449 | 253063 | 98614 | 61.0% |

#### Ratio Matrix

| Format | `Estimate` | `TokenX` | `tiktoken` |
|---|---:|---:|---:|
| SDIF AI | 45.6% | 48.4% | 61.0% |
| CSV Bundle | 45.6% | 56.2% | 63.1% |
| SDIF | 48.2% | 48.4% | 65.7% |
| TOON | 48.2% | 56.2% | 67.7% |
| YAML | 95.0% | 91.1% | 112.2% |
| JSON Compact | 100.0% | 100.0% | 100.0% |
| JSON Pretty | 145.4% | 103.8% | 157.7% |
| XML | 186.9% | 172.1% | 195.5% |

### `large-schema-catalog`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 53799 | 111880 | 58081 | 48.1% |
| `TokenX` | SDIF AI | 59883 | 146598 | 86715 | 40.8% |
| `tiktoken` | SDIF AI | 66788 | 126532 | 59744 | 52.8% |

#### Ratio Matrix

| Format | `Estimate` | `TokenX` | `tiktoken` |
|---|---:|---:|---:|
| SDIF AI | 48.1% | 40.8% | 52.8% |
| CSV Bundle | 48.1% | 52.7% | 56.4% |
| SDIF | 51.2% | 40.9% | 62.5% |
| TOON | 51.2% | 52.8% | 61.8% |
| YAML | 97.2% | 81.6% | 118.2% |
| JSON Compact | 100.0% | 100.0% | 100.0% |
| JSON Pretty | 145.9% | 102.5% | 157.6% |
| XML | 176.5% | 160.4% | 186.3% |

### `large-support-export`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 85512 | 148025 | 62513 | 57.8% |
| `TokenX` | SDIF AI | 81684 | 188515 | 106831 | 43.3% |
| `tiktoken` | SDIF AI | 94839 | 149622 | 54783 | 63.4% |

#### Ratio Matrix

| Format | `Estimate` | `TokenX` | `tiktoken` |
|---|---:|---:|---:|
| SDIF AI | 57.8% | 43.3% | 63.4% |
| SDIF | 59.5% | 43.3% | 66.9% |
| CSV Bundle | 57.8% | 50.2% | 64.2% |
| TOON | 59.5% | 50.2% | 67.6% |
| YAML | 96.8% | 79.1% | 113.1% |
| JSON Compact | 100.0% | 100.0% | 100.0% |
| JSON Pretty | 136.8% | 102.8% | 153.4% |
| XML | 166.6% | 146.6% | 183.6% |

### `large-validation-report`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 95944 | 139832 | 43888 | 68.6% |
| `TokenX` | SDIF AI | 91316 | 160800 | 69484 | 56.8% |
| `tiktoken` | SDIF AI | 99631 | 134533 | 34902 | 74.1% |

#### Ratio Matrix

| Format | `Estimate` | `TokenX` | `tiktoken` |
|---|---:|---:|---:|
| SDIF AI | 68.6% | 56.8% | 74.1% |
| CSV Bundle | 68.6% | 62.4% | 74.1% |
| SDIF | 69.8% | 56.8% | 76.6% |
| TOON | 70.0% | 65.9% | 76.6% |
| YAML | 98.3% | 88.9% | 111.6% |
| JSON Compact | 100.0% | 100.0% | 100.0% |
| JSON Pretty | 127.0% | 102.1% | 142.7% |
| XML | 146.4% | 141.5% | 167.9% |

### `medium-invoice-batch`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 18476 | 34890 | 16414 | 53.0% |
| `TokenX` | SDIF AI | 20700 | 45845 | 25145 | 45.2% |
| `tiktoken` | CSV Bundle | 25965 | 39858 | 13893 | 65.1% |

#### Ratio Matrix

| Format | `Estimate` | `TokenX` | `tiktoken` |
|---|---:|---:|---:|
| SDIF AI | 53.0% | 45.2% | 67.0% |
| CSV Bundle | 53.0% | 54.4% | 65.1% |
| SDIF | 54.4% | 45.2% | 69.5% |
| TOON | 54.4% | 54.4% | 67.6% |
| YAML | 98.2% | 86.6% | 117.3% |
| JSON Compact | 100.0% | 100.0% | 100.0% |
| JSON Pretty | 137.3% | 102.3% | 147.9% |
| XML | 170.7% | 158.2% | 176.9% |

### `medium-observability-run`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 13983 | 28689 | 14706 | 48.7% |
| `TokenX` | SDIF AI | 16712 | 39221 | 22509 | 42.6% |
| `tiktoken` | SDIF AI | 18170 | 32253 | 14083 | 56.3% |

#### Ratio Matrix

| Format | `Estimate` | `TokenX` | `tiktoken` |
|---|---:|---:|---:|
| SDIF AI | 48.7% | 42.6% | 56.3% |
| SDIF | 50.9% | 42.6% | 63.8% |
| CSV Bundle | 48.8% | 52.6% | 59.0% |
| TOON | 50.9% | 52.6% | 66.4% |
| YAML | 95.1% | 84.6% | 119.6% |
| JSON Compact | 100.0% | 100.0% | 100.0% |
| JSON Pretty | 146.4% | 103.1% | 162.2% |
| XML | 179.5% | 165.0% | 196.2% |

### `medium-policy-catalog`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 12446 | 24394 | 11948 | 51.0% |
| `TokenX` | SDIF AI | 16021 | 33616 | 17595 | 47.7% |
| `tiktoken` | SDIF AI | 18106 | 28086 | 9980 | 64.5% |

#### Ratio Matrix

| Format | `Estimate` | `TokenX` | `tiktoken` |
|---|---:|---:|---:|
| SDIF AI | 51.0% | 47.7% | 64.5% |
| SDIF | 53.0% | 47.7% | 67.8% |
| CSV Bundle | 51.1% | 56.9% | 68.2% |
| TOON | 53.0% | 56.9% | 71.5% |
| YAML | 93.9% | 82.8% | 114.3% |
| JSON Compact | 100.0% | 100.0% | 100.0% |
| JSON Pretty | 142.8% | 102.8% | 156.7% |
| XML | 171.7% | 153.5% | 187.6% |

### `medium-product-catalog`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 11888 | 27843 | 15955 | 42.7% |
| `TokenX` | SDIF AI | 14784 | 37474 | 22690 | 39.5% |
| `tiktoken` | SDIF AI | 21319 | 33936 | 12617 | 62.8% |

#### Ratio Matrix

| Format | `Estimate` | `TokenX` | `tiktoken` |
|---|---:|---:|---:|
| SDIF AI | 42.7% | 39.5% | 62.8% |
| SDIF | 45.6% | 39.5% | 67.6% |
| CSV Bundle | 42.7% | 49.0% | 63.2% |
| TOON | 45.6% | 49.0% | 67.9% |
| YAML | 94.0% | 86.2% | 117.7% |
| JSON Compact | 100.0% | 100.0% | 100.0% |
| JSON Pretty | 151.8% | 104.3% | 165.0% |
| XML | 192.9% | 178.1% | 203.6% |

### `plan`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF | 246 | 317 | 71 | 77.6% |
| `TokenX` | SDIF | 266 | 389 | 123 | 68.4% |
| `tiktoken` | SDIF AI | 250 | 302 | 52 | 82.8% |

#### Ratio Matrix

| Format | `Estimate` | `TokenX` | `tiktoken` |
|---|---:|---:|---:|
| SDIF | 77.6% | 68.4% | 83.4% |
| SDIF AI | 78.9% | 70.4% | 82.8% |
| TOON | 79.2% | 78.9% | 91.4% |
| CSV Bundle | 82.0% | 83.3% | 95.4% |
| YAML | 94.6% | 85.6% | 110.6% |
| JSON Compact | 100.0% | 100.0% | 100.0% |
| JSON Pretty | 133.1% | 104.4% | 158.6% |
| XML | 164.0% | 157.8% | 199.3% |

### `registry`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 166 | 240 | 74 | 69.2% |
| `TokenX` | SDIF AI | 190 | 301 | 111 | 63.1% |
| `tiktoken` | SDIF AI | 149 | 205 | 56 | 72.7% |

#### Ratio Matrix

| Format | `Estimate` | `TokenX` | `tiktoken` |
|---|---:|---:|---:|
| SDIF AI | 69.2% | 63.1% | 72.7% |
| SDIF | 70.4% | 63.8% | 75.1% |
| TOON | 72.9% | 75.4% | 82.4% |
| CSV Bundle | 75.0% | 79.7% | 85.4% |
| YAML | 93.3% | 84.7% | 107.3% |
| JSON Compact | 100.0% | 100.0% | 100.0% |
| JSON Pretty | 135.0% | 104.0% | 166.3% |
| XML | 167.1% | 158.8% | 213.7% |

### `schema`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 275 | 529 | 254 | 52.0% |
| `TokenX` | SDIF AI | 291 | 665 | 374 | 43.8% |
| `tiktoken` | SDIF AI | 298 | 534 | 236 | 55.8% |

#### Ratio Matrix

| Format | `Estimate` | `TokenX` | `tiktoken` |
|---|---:|---:|---:|
| SDIF AI | 52.0% | 43.8% | 55.8% |
| SDIF | 55.0% | 44.5% | 60.5% |
| CSV Bundle | 55.0% | 57.7% | 62.0% |
| TOON | 56.0% | 57.7% | 64.0% |
| YAML | 94.7% | 83.3% | 118.0% |
| JSON Compact | 100.0% | 100.0% | 100.0% |
| JSON Pretty | 152.9% | 105.7% | 178.5% |
| XML | 198.1% | 186.8% | 227.2% |

### `small-api-catalog`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 410 | 791 | 381 | 51.8% |
| `TokenX` | SDIF AI | 516 | 1126 | 610 | 45.8% |
| `tiktoken` | SDIF AI | 544 | 912 | 368 | 59.6% |

#### Ratio Matrix

| Format | `Estimate` | `TokenX` | `tiktoken` |
|---|---:|---:|---:|
| SDIF AI | 51.8% | 45.8% | 59.6% |
| SDIF | 54.2% | 46.3% | 64.1% |
| CSV Bundle | 52.7% | 55.8% | 64.1% |
| TOON | 54.4% | 55.4% | 67.4% |
| YAML | 92.0% | 77.8% | 121.6% |
| JSON Compact | 100.0% | 100.0% | 100.0% |
| JSON Pretty | 153.4% | 103.2% | 171.5% |
| XML | 178.5% | 154.7% | 207.7% |

### `small-incident`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 641 | 1037 | 396 | 61.8% |
| `TokenX` | SDIF AI | 692 | 1304 | 612 | 53.1% |
| `tiktoken` | SDIF AI | 704 | 1064 | 360 | 66.2% |

#### Ratio Matrix

| Format | `Estimate` | `TokenX` | `tiktoken` |
|---|---:|---:|---:|
| SDIF AI | 61.8% | 53.1% | 66.2% |
| SDIF | 63.6% | 53.5% | 68.0% |
| CSV Bundle | 62.6% | 63.4% | 69.5% |
| TOON | 63.6% | 63.2% | 69.7% |
| YAML | 95.2% | 82.6% | 108.7% |
| JSON Compact | 100.0% | 100.0% | 100.0% |
| JSON Pretty | 138.1% | 102.8% | 155.7% |
| XML | 164.1% | 150.9% | 182.4% |

### `small-invoice`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 352 | 661 | 309 | 53.3% |
| `TokenX` | SDIF AI | 391 | 848 | 457 | 46.1% |
| `tiktoken` | SDIF AI | 476 | 718 | 242 | 66.3% |

#### Ratio Matrix

| Format | `Estimate` | `TokenX` | `tiktoken` |
|---|---:|---:|---:|
| SDIF AI | 53.3% | 46.1% | 66.3% |
| CSV Bundle | 54.5% | 58.7% | 67.5% |
| SDIF | 55.1% | 46.7% | 70.1% |
| TOON | 55.2% | 58.4% | 69.8% |
| YAML | 96.1% | 84.3% | 118.4% |
| JSON Compact | 100.0% | 100.0% | 100.0% |
| JSON Pretty | 142.4% | 102.8% | 161.4% |
| XML | 179.3% | 170.2% | 196.9% |

### `validation-report`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 173 | 254 | 81 | 68.1% |
| `TokenX` | SDIF AI | 180 | 300 | 120 | 60.0% |
| `tiktoken` | SDIF AI | 149 | 225 | 76 | 66.2% |

#### Ratio Matrix

| Format | `Estimate` | `TokenX` | `tiktoken` |
|---|---:|---:|---:|
| SDIF AI | 68.1% | 60.0% | 66.2% |
| SDIF | 72.4% | 63.3% | 73.8% |
| TOON | 76.0% | 75.3% | 87.6% |
| CSV Bundle | 76.4% | 76.0% | 86.7% |
| YAML | 92.1% | 84.3% | 109.3% |
| JSON Compact | 100.0% | 100.0% | 100.0% |
| JSON Pretty | 135.8% | 105.3% | 169.8% |
| XML | 166.1% | 164.7% | 213.3% |

### `wide-table-survey`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 4652 | 16230 | 11578 | 28.7% |
| `TokenX` | SDIF AI | 7878 | 29998 | 22120 | 26.3% |
| `tiktoken` | SDIF AI | 15224 | 36372 | 21148 | 41.9% |

#### Ratio Matrix

| Format | `Estimate` | `TokenX` | `tiktoken` |
|---|---:|---:|---:|
| SDIF AI | 28.7% | 26.3% | 41.9% |
| CSV Bundle | 28.7% | 49.7% | 42.2% |
| SDIF | 29.4% | 26.3% | 42.5% |
| TOON | 29.4% | 49.6% | 42.8% |
| JSON Compact | 100.0% | 100.0% | 100.0% |
| YAML | 108.4% | 75.7% | 137.8% |
| JSON Pretty | 192.5% | 100.7% | 162.1% |
| XML | 229.8% | 176.7% | 202.3% |

## Raw Count Matrix

This section contains raw counts only. Ratios are intentionally excluded here because they are tokenizer-specific.

### `deep-hierarchy-project`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| CSV Bundle | 292754 | 73189 | 91221 | 101645 | - | - |
| SDIF AI | 292715 | 73179 | 81732 | 103204 | - | - |
| TOON | 302214 | 75554 | 91221 | 106382 | - | - |
| SDIF | 302202 | 75551 | 81738 | 107951 | - | - |
| JSON Compact | 474294 | 118574 | 150426 | 137942 | - | - |
| YAML | 452163 | 113041 | 125936 | 153735 | - | - |
| JSON Pretty | 648068 | 162017 | 155171 | 204303 | - | - |
| XML | 768236 | 192059 | 219188 | 243817 | - | - |

### `github.openapi`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 167358 | 41840 | 46321 | 37824 | - | - |
| CSV Bundle | 167539 | 41885 | 52839 | 39074 | - | - |
| TOON | 174452 | 43613 | 53807 | 41529 | - | - |
| SDIF | 173649 | 43413 | 46333 | 41867 | - | - |
| JSON Compact | 292422 | 73106 | 90705 | 62704 | - | - |
| YAML | 283256 | 70814 | 77837 | 72783 | - | - |
| JSON Pretty | 386842 | 96711 | 92880 | 97266 | - | - |
| XML | 472655 | 118164 | 135694 | 117756 | - | - |

### `large-audit-trail`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 1133989 | 283498 | 268759 | 412926 | - | - |
| CSV Bundle | 1134036 | 283509 | 306240 | 422357 | - | - |
| SDIF | 1155527 | 288882 | 268764 | 423698 | - | - |
| TOON | 1166582 | 291646 | 357989 | 433120 | - | - |
| JSON Compact | 1728738 | 432185 | 536764 | 540663 | - | - |
| YAML | 1666793 | 416699 | 455642 | 584405 | - | - |
| JSON Pretty | 2222275 | 555569 | 547537 | 723268 | - | - |
| XML | 2576525 | 644132 | 705489 | 831285 | - | - |

### `large-knowledge-graph`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 279580 | 69895 | 73765 | 86155 | - | - |
| CSV Bundle | 279620 | 69905 | 89705 | 88495 | - | - |
| SDIF | 289242 | 72311 | 73770 | 90989 | - | - |
| TOON | 288966 | 72242 | 89415 | 93032 | - | - |
| JSON Compact | 518882 | 129721 | 157533 | 132864 | - | - |
| YAML | 495208 | 123802 | 129722 | 153731 | - | - |
| JSON Pretty | 733208 | 183302 | 162366 | 213005 | - | - |
| XML | 884387 | 221097 | 245137 | 254541 | - | - |

### `large-plan`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 492352 | 123088 | 143533 | 141143 | - | - |
| CSV Bundle | 492413 | 123104 | 159261 | 144465 | - | - |
| SDIF | 504796 | 126199 | 143540 | 147369 | - | - |
| TOON | 504817 | 126205 | 159262 | 150679 | - | - |
| JSON Compact | 804703 | 201176 | 255952 | 213238 | - | - |
| YAML | 780329 | 195083 | 229824 | 229718 | - | - |
| JSON Pretty | 1048494 | 262124 | 262181 | 302381 | - | - |
| XML | 1273626 | 318407 | 381913 | 366170 | - | - |

### `large-registry`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 402718 | 100680 | 148685 | 154449 | - | - |
| CSV Bundle | 402772 | 100693 | 172514 | 159696 | - | - |
| SDIF | 426166 | 106542 | 148692 | 166177 | - | - |
| TOON | 426185 | 106547 | 172514 | 171412 | - | - |
| JSON Compact | 883824 | 220956 | 307177 | 253063 | - | - |
| YAML | 839949 | 209988 | 279687 | 283892 | - | - |
| JSON Pretty | 1285316 | 321329 | 318906 | 399186 | - | - |
| XML | 1652261 | 413066 | 528580 | 494780 | - | - |

### `large-schema-catalog`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 215193 | 53799 | 59883 | 66788 | - | - |
| CSV Bundle | 215257 | 53815 | 77252 | 71357 | - | - |
| TOON | 229126 | 57282 | 77470 | 78231 | - | - |
| SDIF | 228953 | 57239 | 59890 | 79144 | - | - |
| JSON Compact | 447520 | 111880 | 146598 | 126532 | - | - |
| YAML | 435031 | 108758 | 119551 | 149601 | - | - |
| JSON Pretty | 653078 | 163270 | 150285 | 199367 | - | - |
| XML | 790035 | 197509 | 235160 | 235726 | - | - |

### `large-support-export`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 342047 | 85512 | 81684 | 94839 | - | - |
| CSV Bundle | 342094 | 85524 | 94673 | 96002 | - | - |
| SDIF | 352437 | 88110 | 81689 | 100037 | - | - |
| TOON | 352453 | 88114 | 94672 | 101190 | - | - |
| JSON Compact | 592098 | 148025 | 188515 | 149622 | - | - |
| YAML | 573388 | 143347 | 149111 | 169236 | - | - |
| JSON Pretty | 810127 | 202532 | 193714 | 229579 | - | - |
| XML | 986732 | 246683 | 276343 | 274660 | - | - |

### `large-validation-report`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 383774 | 95944 | 91316 | 99631 | - | - |
| CSV Bundle | 383821 | 95956 | 100374 | 99656 | - | - |
| SDIF | 390534 | 97634 | 91323 | 103015 | - | - |
| TOON | 391666 | 97917 | 105973 | 103027 | - | - |
| JSON Compact | 559328 | 139832 | 160800 | 134533 | - | - |
| YAML | 549978 | 137495 | 142953 | 150198 | - | - |
| JSON Pretty | 710381 | 177596 | 164183 | 192034 | - | - |
| XML | 818657 | 204665 | 227604 | 225834 | - | - |

### `medium-invoice-batch`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| CSV Bundle | 73941 | 18486 | 24956 | 25965 | - | - |
| SDIF AI | 73901 | 18476 | 20700 | 26706 | - | - |
| TOON | 75867 | 18967 | 24954 | 26932 | - | - |
| SDIF | 75859 | 18965 | 20707 | 27688 | - | - |
| JSON Compact | 139558 | 34890 | 45845 | 39858 | - | - |
| YAML | 137030 | 34258 | 39703 | 46758 | - | - |
| JSON Pretty | 191590 | 47898 | 46892 | 58931 | - | - |
| XML | 238165 | 59542 | 72517 | 70501 | - | - |

### `medium-observability-run`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 55931 | 13983 | 16712 | 18170 | - | - |
| CSV Bundle | 55978 | 13995 | 20633 | 19018 | - | - |
| SDIF | 58377 | 14595 | 16717 | 20572 | - | - |
| TOON | 58391 | 14598 | 20632 | 21408 | - | - |
| JSON Compact | 114756 | 28689 | 39221 | 32253 | - | - |
| YAML | 109099 | 27275 | 33200 | 38569 | - | - |
| JSON Pretty | 167981 | 41996 | 40448 | 52300 | - | - |
| XML | 205986 | 51497 | 64697 | 63274 | - | - |

### `medium-policy-catalog`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 49782 | 12446 | 16021 | 18106 | - | - |
| SDIF | 51672 | 12918 | 16026 | 19054 | - | - |
| CSV Bundle | 49822 | 12456 | 19136 | 19159 | - | - |
| TOON | 51680 | 12920 | 19134 | 20095 | - | - |
| JSON Compact | 97573 | 24394 | 33616 | 28086 | - | - |
| YAML | 91628 | 22907 | 27840 | 32094 | - | - |
| JSON Pretty | 139351 | 34838 | 34563 | 43999 | - | - |
| XML | 167499 | 41875 | 51599 | 52678 | - | - |

### `medium-product-catalog`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 47552 | 11888 | 14784 | 21319 | - | - |
| CSV Bundle | 47599 | 11900 | 18378 | 21445 | - | - |
| SDIF | 50784 | 12696 | 14789 | 22938 | - | - |
| TOON | 50798 | 12700 | 18377 | 23051 | - | - |
| JSON Compact | 111369 | 27843 | 37474 | 33936 | - | - |
| YAML | 104720 | 26180 | 32289 | 39958 | - | - |
| JSON Pretty | 169056 | 42264 | 39094 | 55984 | - | - |
| XML | 214848 | 53712 | 66733 | 69082 | - | - |

### `plan`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 998 | 250 | 274 | 250 | - | - |
| SDIF | 984 | 246 | 266 | 252 | - | - |
| TOON | 1002 | 251 | 307 | 276 | - | - |
| CSV Bundle | 1039 | 260 | 324 | 288 | - | - |
| JSON Compact | 1268 | 317 | 389 | 302 | - | - |
| YAML | 1197 | 300 | 333 | 334 | - | - |
| JSON Pretty | 1688 | 422 | 406 | 479 | - | - |
| XML | 2080 | 520 | 614 | 602 | - | - |

### `registry`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 662 | 166 | 190 | 149 | - | - |
| SDIF | 674 | 169 | 192 | 154 | - | - |
| TOON | 697 | 175 | 227 | 169 | - | - |
| CSV Bundle | 720 | 180 | 240 | 175 | - | - |
| JSON Compact | 960 | 240 | 301 | 205 | - | - |
| YAML | 896 | 224 | 255 | 220 | - | - |
| JSON Pretty | 1293 | 324 | 313 | 341 | - | - |
| XML | 1601 | 401 | 478 | 438 | - | - |

### `schema`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 1097 | 275 | 291 | 298 | - | - |
| SDIF | 1161 | 291 | 296 | 323 | - | - |
| CSV Bundle | 1161 | 291 | 384 | 331 | - | - |
| TOON | 1181 | 296 | 384 | 342 | - | - |
| JSON Compact | 2113 | 529 | 665 | 534 | - | - |
| YAML | 2004 | 501 | 554 | 630 | - | - |
| JSON Pretty | 3235 | 809 | 703 | 953 | - | - |
| XML | 4189 | 1048 | 1242 | 1213 | - | - |

### `small-api-catalog`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 1640 | 410 | 516 | 544 | - | - |
| CSV Bundle | 1666 | 417 | 628 | 585 | - | - |
| SDIF | 1716 | 429 | 521 | 585 | - | - |
| TOON | 1718 | 430 | 624 | 615 | - | - |
| JSON Compact | 3163 | 791 | 1126 | 912 | - | - |
| YAML | 2909 | 728 | 876 | 1109 | - | - |
| JSON Pretty | 4849 | 1213 | 1162 | 1564 | - | - |
| XML | 5647 | 1412 | 1742 | 1894 | - | - |

### `small-incident`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 2561 | 641 | 692 | 704 | - | - |
| SDIF | 2637 | 660 | 698 | 723 | - | - |
| CSV Bundle | 2594 | 649 | 827 | 740 | - | - |
| TOON | 2640 | 660 | 824 | 742 | - | - |
| JSON Compact | 4148 | 1037 | 1304 | 1064 | - | - |
| YAML | 3947 | 987 | 1077 | 1157 | - | - |
| JSON Pretty | 5727 | 1432 | 1341 | 1657 | - | - |
| XML | 6808 | 1702 | 1968 | 1941 | - | - |

### `small-invoice`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 1406 | 352 | 391 | 476 | - | - |
| CSV Bundle | 1439 | 360 | 498 | 485 | - | - |
| TOON | 1459 | 365 | 495 | 501 | - | - |
| SDIF | 1454 | 364 | 396 | 503 | - | - |
| JSON Compact | 2643 | 661 | 848 | 718 | - | - |
| YAML | 2537 | 635 | 715 | 850 | - | - |
| JSON Pretty | 3764 | 941 | 872 | 1159 | - | - |
| XML | 4738 | 1185 | 1443 | 1414 | - | - |

### `validation-report`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 691 | 173 | 180 | 149 | - | - |
| SDIF | 735 | 184 | 190 | 166 | - | - |
| CSV Bundle | 773 | 194 | 228 | 195 | - | - |
| TOON | 770 | 193 | 226 | 197 | - | - |
| JSON Compact | 1014 | 254 | 300 | 225 | - | - |
| YAML | 934 | 234 | 253 | 246 | - | - |
| JSON Pretty | 1378 | 345 | 316 | 382 | - | - |
| XML | 1685 | 422 | 494 | 480 | - | - |

### `wide-table-survey`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 18606 | 4652 | 7878 | 15224 | - | - |
| CSV Bundle | 18632 | 4658 | 14897 | 15365 | - | - |
| SDIF | 19054 | 4764 | 7883 | 15451 | - | - |
| TOON | 19053 | 4764 | 14893 | 15579 | - | - |
| JSON Compact | 64917 | 16230 | 29998 | 36372 | - | - |
| YAML | 70375 | 17594 | 22708 | 50113 | - | - |
| JSON Pretty | 124951 | 31238 | 30220 | 58948 | - | - |
| XML | 149167 | 37292 | 52992 | 73594 | - | - |

## Environment

| Variable | Value |
| --- | --- |
| `.env loaded` | `yes` |
| `SDIF_BENCHMARK_TOON` | `1` |
| `SDIF_BENCHMARK_TOKENX` | `1` |
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

- `Llama3` is disabled: Disabled through SDIF_BENCHMARK_LLAMA=0.
- `Claude` is disabled: Disabled. Set SDIF_BENCHMARK_CLAUDE=1 to enable API token counting.

## Artifacts

- Raw log: `benchmarks/20260521T150432Z/comparison.log`
- Markdown report: `benchmarks/20260521T150432Z/comparison.md`
- Summary report: `benchmarks/20260521T150432Z/summary.md`
- Structured JSON report: `benchmarks/20260521T150432Z/comparison.json`
- Structured SDIF report: `benchmarks/20260521T150432Z/comparison.sdif`
- SDIF AI projection: `benchmarks/20260521T150432Z/comparison.sdif.ai`
- Latest directory: `benchmarks/latest`
