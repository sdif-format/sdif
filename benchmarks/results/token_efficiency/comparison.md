# SDIF Benchmark Evidence Report

- Generated at: `2026-05-21T18:50:53Z`
- Run directory: `benchmarks/results/token_efficiency`
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
| `TokenX` | disabled | heuristic | Disabled through SDIF_BENCHMARK_TOKENX=0. |
| `tiktoken` | available | model tokenizer | Encoding: cl100k_base. |
| `Llama3` | disabled | model tokenizer | Disabled through SDIF_BENCHMARK_LLAMA=0. |
| `Claude` | disabled | API tokenizer | Disabled. Set SDIF_BENCHMARK_CLAUDE=1 to enable API token counting. |

### Consensus Ranking

| Format | Avg Rank | Median Ratio | Best Ratio | Worst Ratio | Rank Spread | Coverage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SDIF AI | 1.12 | 61.5% | 28.7% | 83.1% | 1 | 42/42 |
| CSV Bundle | 2.12 | 62.8% | 28.7% | 95.4% | 2 | 42/42 |
| SDIF | 2.76 | 64.9% | 29.4% | 83.4% | 2 | 42/42 |
| JSON Compact | 4.48 | 100.0% | 100.0% | 100.0% | 1 | 42/42 |
| YAML | 4.52 | 107.5% | 92.0% | 137.8% | 1 | 42/42 |
| JSON Pretty | 6.00 | 148.0% | 127.0% | 192.5% | 0 | 42/42 |
| XML | 7.00 | 179.4% | 146.4% | 229.8% | 0 | 42/42 |

### Winners by Tokenizer

| Tokenizer | Winner Format | Wins | Documents |
| --- | --- | ---: | ---: |
| `Estimate` | SDIF AI | 19 | 21 |
| `Estimate` | CSV Bundle | 1 | 21 |
| `Estimate` | SDIF | 1 | 21 |
| `tiktoken` | SDIF AI | 18 | 21 |
| `tiktoken` | CSV Bundle | 3 | 21 |

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

#### Summary

| Format | Avg Rank | Avg Ratio | Median Ratio | Avg Saved Tokens | Wins | Coverage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SDIF AI | 1.14 | 64.9% | 64.8% | 29423 | 18 | 21/21 |
| CSV Bundle | 2.14 | 68.3% | 66.6% | 28530 | 3 | 21/21 |
| SDIF | 2.71 | 68.5% | 68.0% | 26522 | 0 | 21/21 |
| JSON Compact | 4.00 | 100.0% | 100.0% | 0 | 0 | 21/21 |
| YAML | 5.00 | 115.0% | 114.3% | -11129 | 0 | 21/21 |
| JSON Pretty | 6.00 | 157.4% | 157.7% | -43403 | 0 | 21/21 |
| XML | 7.00 | 191.5% | 191.6% | -69336 | 0 | 21/21 |

#### Per-document Ranking

| Document | Rank | Format | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| `deep-hierarchy-project` | 1 | CSV Bundle | 101645 | 137942 | 36297 | 73.7% |
| `deep-hierarchy-project` | 2 | SDIF AI | 103205 | 137942 | 34737 | 74.8% |
| `deep-hierarchy-project` | 3 | SDIF | 107951 | 137942 | 29991 | 78.3% |
| `deep-hierarchy-project` | 4 | JSON Compact | 137942 | 137942 | 0 | 100.0% |
| `deep-hierarchy-project` | 5 | YAML | 153735 | 137942 | -15793 | 111.4% |
| `deep-hierarchy-project` | 6 | JSON Pretty | 204303 | 137942 | -66361 | 148.1% |
| `deep-hierarchy-project` | 7 | XML | 243817 | 137942 | -105875 | 176.8% |
| `github.openapi` | 1 | SDIF AI | 37829 | 62704 | 24875 | 60.3% |
| `github.openapi` | 2 | CSV Bundle | 39074 | 62704 | 23630 | 62.3% |
| `github.openapi` | 3 | SDIF | 41867 | 62704 | 20837 | 66.8% |
| `github.openapi` | 4 | JSON Compact | 62704 | 62704 | 0 | 100.0% |
| `github.openapi` | 5 | YAML | 72783 | 62704 | -10079 | 116.1% |
| `github.openapi` | 6 | JSON Pretty | 97266 | 62704 | -34562 | 155.1% |
| `github.openapi` | 7 | XML | 117756 | 62704 | -55052 | 187.8% |
| `large-audit-trail` | 1 | SDIF AI | 412926 | 540663 | 127737 | 76.4% |
| `large-audit-trail` | 2 | CSV Bundle | 422357 | 540663 | 118306 | 78.1% |
| `large-audit-trail` | 3 | SDIF | 423698 | 540663 | 116965 | 78.4% |
| `large-audit-trail` | 4 | JSON Compact | 540663 | 540663 | 0 | 100.0% |
| `large-audit-trail` | 5 | YAML | 584405 | 540663 | -43742 | 108.1% |
| `large-audit-trail` | 6 | JSON Pretty | 723268 | 540663 | -182605 | 133.8% |
| `large-audit-trail` | 7 | XML | 831285 | 540663 | -290622 | 153.8% |
| `large-knowledge-graph` | 1 | SDIF AI | 86155 | 132864 | 46709 | 64.8% |
| `large-knowledge-graph` | 2 | CSV Bundle | 88495 | 132864 | 44369 | 66.6% |
| `large-knowledge-graph` | 3 | SDIF | 90989 | 132864 | 41875 | 68.5% |
| `large-knowledge-graph` | 4 | JSON Compact | 132864 | 132864 | 0 | 100.0% |
| `large-knowledge-graph` | 5 | YAML | 153731 | 132864 | -20867 | 115.7% |
| `large-knowledge-graph` | 6 | JSON Pretty | 213005 | 132864 | -80141 | 160.3% |
| `large-knowledge-graph` | 7 | XML | 254541 | 132864 | -121677 | 191.6% |
| `large-plan` | 1 | SDIF AI | 141145 | 213238 | 72093 | 66.2% |
| `large-plan` | 2 | CSV Bundle | 144465 | 213238 | 68773 | 67.7% |
| `large-plan` | 3 | SDIF | 147369 | 213238 | 65869 | 69.1% |
| `large-plan` | 4 | JSON Compact | 213238 | 213238 | 0 | 100.0% |
| `large-plan` | 5 | YAML | 229718 | 213238 | -16480 | 107.7% |
| `large-plan` | 6 | JSON Pretty | 302381 | 213238 | -89143 | 141.8% |
| `large-plan` | 7 | XML | 366170 | 213238 | -152932 | 171.7% |
| `large-registry` | 1 | SDIF AI | 154451 | 253063 | 98612 | 61.0% |
| `large-registry` | 2 | CSV Bundle | 159696 | 253063 | 93367 | 63.1% |
| `large-registry` | 3 | SDIF | 166177 | 253063 | 86886 | 65.7% |
| `large-registry` | 4 | JSON Compact | 253063 | 253063 | 0 | 100.0% |
| `large-registry` | 5 | YAML | 283892 | 253063 | -30829 | 112.2% |
| `large-registry` | 6 | JSON Pretty | 399186 | 253063 | -146123 | 157.7% |
| `large-registry` | 7 | XML | 494780 | 253063 | -241717 | 195.5% |
| `large-schema-catalog` | 1 | CSV Bundle | 71357 | 126532 | 55175 | 56.4% |
| `large-schema-catalog` | 2 | SDIF AI | 75464 | 126532 | 51068 | 59.6% |
| `large-schema-catalog` | 3 | SDIF | 79144 | 126532 | 47388 | 62.5% |
| `large-schema-catalog` | 4 | JSON Compact | 126532 | 126532 | 0 | 100.0% |
| `large-schema-catalog` | 5 | YAML | 149601 | 126532 | -23069 | 118.2% |
| `large-schema-catalog` | 6 | JSON Pretty | 199367 | 126532 | -72835 | 157.6% |
| `large-schema-catalog` | 7 | XML | 235726 | 126532 | -109194 | 186.3% |
| `large-support-export` | 1 | SDIF AI | 94839 | 149622 | 54783 | 63.4% |
| `large-support-export` | 2 | CSV Bundle | 96002 | 149622 | 53620 | 64.2% |
| `large-support-export` | 3 | SDIF | 100037 | 149622 | 49585 | 66.9% |
| `large-support-export` | 4 | JSON Compact | 149622 | 149622 | 0 | 100.0% |
| `large-support-export` | 5 | YAML | 169236 | 149622 | -19614 | 113.1% |
| `large-support-export` | 6 | JSON Pretty | 229579 | 149622 | -79957 | 153.4% |
| `large-support-export` | 7 | XML | 274660 | 149622 | -125038 | 183.6% |
| `large-validation-report` | 1 | SDIF AI | 99633 | 134533 | 34900 | 74.1% |
| `large-validation-report` | 2 | CSV Bundle | 99656 | 134533 | 34877 | 74.1% |
| `large-validation-report` | 3 | SDIF | 103015 | 134533 | 31518 | 76.6% |
| `large-validation-report` | 4 | JSON Compact | 134533 | 134533 | 0 | 100.0% |
| `large-validation-report` | 5 | YAML | 150198 | 134533 | -15665 | 111.6% |
| `large-validation-report` | 6 | JSON Pretty | 192034 | 134533 | -57501 | 142.7% |
| `large-validation-report` | 7 | XML | 225834 | 134533 | -91301 | 167.9% |
| `medium-invoice-batch` | 1 | CSV Bundle | 25965 | 39858 | 13893 | 65.1% |
| `medium-invoice-batch` | 2 | SDIF AI | 26707 | 39858 | 13151 | 67.0% |
| `medium-invoice-batch` | 3 | SDIF | 27688 | 39858 | 12170 | 69.5% |
| `medium-invoice-batch` | 4 | JSON Compact | 39858 | 39858 | 0 | 100.0% |
| `medium-invoice-batch` | 5 | YAML | 46758 | 39858 | -6900 | 117.3% |
| `medium-invoice-batch` | 6 | JSON Pretty | 58931 | 39858 | -19073 | 147.9% |
| `medium-invoice-batch` | 7 | XML | 70501 | 39858 | -30643 | 176.9% |
| `medium-observability-run` | 1 | SDIF AI | 18170 | 32253 | 14083 | 56.3% |
| `medium-observability-run` | 2 | CSV Bundle | 19018 | 32253 | 13235 | 59.0% |
| `medium-observability-run` | 3 | SDIF | 20572 | 32253 | 11681 | 63.8% |
| `medium-observability-run` | 4 | JSON Compact | 32253 | 32253 | 0 | 100.0% |
| `medium-observability-run` | 5 | YAML | 38569 | 32253 | -6316 | 119.6% |
| `medium-observability-run` | 6 | JSON Pretty | 52300 | 32253 | -20047 | 162.2% |
| `medium-observability-run` | 7 | XML | 63274 | 32253 | -31021 | 196.2% |
| `medium-policy-catalog` | 1 | SDIF AI | 18106 | 28086 | 9980 | 64.5% |
| `medium-policy-catalog` | 2 | SDIF | 19054 | 28086 | 9032 | 67.8% |
| `medium-policy-catalog` | 3 | CSV Bundle | 19159 | 28086 | 8927 | 68.2% |
| `medium-policy-catalog` | 4 | JSON Compact | 28086 | 28086 | 0 | 100.0% |
| `medium-policy-catalog` | 5 | YAML | 32094 | 28086 | -4008 | 114.3% |
| `medium-policy-catalog` | 6 | JSON Pretty | 43999 | 28086 | -15913 | 156.7% |
| `medium-policy-catalog` | 7 | XML | 52678 | 28086 | -24592 | 187.6% |
| `medium-product-catalog` | 1 | SDIF AI | 21319 | 33936 | 12617 | 62.8% |
| `medium-product-catalog` | 2 | CSV Bundle | 21445 | 33936 | 12491 | 63.2% |
| `medium-product-catalog` | 3 | SDIF | 22938 | 33936 | 10998 | 67.6% |
| `medium-product-catalog` | 4 | JSON Compact | 33936 | 33936 | 0 | 100.0% |
| `medium-product-catalog` | 5 | YAML | 39958 | 33936 | -6022 | 117.7% |
| `medium-product-catalog` | 6 | JSON Pretty | 55984 | 33936 | -22048 | 165.0% |
| `medium-product-catalog` | 7 | XML | 69082 | 33936 | -35146 | 203.6% |
| `plan` | 1 | SDIF AI | 251 | 302 | 51 | 83.1% |
| `plan` | 2 | SDIF | 252 | 302 | 50 | 83.4% |
| `plan` | 3 | CSV Bundle | 288 | 302 | 14 | 95.4% |
| `plan` | 4 | JSON Compact | 302 | 302 | 0 | 100.0% |
| `plan` | 5 | YAML | 334 | 302 | -32 | 110.6% |
| `plan` | 6 | JSON Pretty | 479 | 302 | -177 | 158.6% |
| `plan` | 7 | XML | 602 | 302 | -300 | 199.3% |
| `registry` | 1 | SDIF AI | 149 | 205 | 56 | 72.7% |
| `registry` | 2 | SDIF | 154 | 205 | 51 | 75.1% |
| `registry` | 3 | CSV Bundle | 175 | 205 | 30 | 85.4% |
| `registry` | 4 | JSON Compact | 205 | 205 | 0 | 100.0% |
| `registry` | 5 | YAML | 220 | 205 | -15 | 107.3% |
| `registry` | 6 | JSON Pretty | 341 | 205 | -136 | 166.3% |
| `registry` | 7 | XML | 438 | 205 | -233 | 213.7% |
| `schema` | 1 | SDIF AI | 298 | 534 | 236 | 55.8% |
| `schema` | 2 | SDIF | 323 | 534 | 211 | 60.5% |
| `schema` | 3 | CSV Bundle | 331 | 534 | 203 | 62.0% |
| `schema` | 4 | JSON Compact | 534 | 534 | 0 | 100.0% |
| `schema` | 5 | YAML | 630 | 534 | -96 | 118.0% |
| `schema` | 6 | JSON Pretty | 953 | 534 | -419 | 178.5% |
| `schema` | 7 | XML | 1213 | 534 | -679 | 227.2% |
| `small-api-catalog` | 1 | SDIF AI | 544 | 912 | 368 | 59.6% |
| `small-api-catalog` | 2 | CSV Bundle | 585 | 912 | 327 | 64.1% |
| `small-api-catalog` | 3 | SDIF | 585 | 912 | 327 | 64.1% |
| `small-api-catalog` | 4 | JSON Compact | 912 | 912 | 0 | 100.0% |
| `small-api-catalog` | 5 | YAML | 1109 | 912 | -197 | 121.6% |
| `small-api-catalog` | 6 | JSON Pretty | 1564 | 912 | -652 | 171.5% |
| `small-api-catalog` | 7 | XML | 1894 | 912 | -982 | 207.7% |
| `small-incident` | 1 | SDIF AI | 706 | 1064 | 358 | 66.4% |
| `small-incident` | 2 | SDIF | 723 | 1064 | 341 | 68.0% |
| `small-incident` | 3 | CSV Bundle | 740 | 1064 | 324 | 69.5% |
| `small-incident` | 4 | JSON Compact | 1064 | 1064 | 0 | 100.0% |
| `small-incident` | 5 | YAML | 1157 | 1064 | -93 | 108.7% |
| `small-incident` | 6 | JSON Pretty | 1657 | 1064 | -593 | 155.7% |
| `small-incident` | 7 | XML | 1941 | 1064 | -877 | 182.4% |
| `small-invoice` | 1 | SDIF AI | 476 | 718 | 242 | 66.3% |
| `small-invoice` | 2 | CSV Bundle | 485 | 718 | 233 | 67.5% |
| `small-invoice` | 3 | SDIF | 503 | 718 | 215 | 70.1% |
| `small-invoice` | 4 | JSON Compact | 718 | 718 | 0 | 100.0% |
| `small-invoice` | 5 | YAML | 850 | 718 | -132 | 118.4% |
| `small-invoice` | 6 | JSON Pretty | 1159 | 718 | -441 | 161.4% |
| `small-invoice` | 7 | XML | 1414 | 718 | -696 | 196.9% |
| `validation-report` | 1 | SDIF AI | 149 | 225 | 76 | 66.2% |
| `validation-report` | 2 | SDIF | 166 | 225 | 59 | 73.8% |
| `validation-report` | 3 | CSV Bundle | 195 | 225 | 30 | 86.7% |
| `validation-report` | 4 | JSON Compact | 225 | 225 | 0 | 100.0% |
| `validation-report` | 5 | YAML | 246 | 225 | -21 | 109.3% |
| `validation-report` | 6 | JSON Pretty | 382 | 225 | -157 | 169.8% |
| `validation-report` | 7 | XML | 480 | 225 | -255 | 213.3% |
| `wide-table-survey` | 1 | SDIF AI | 15224 | 36372 | 21148 | 41.9% |
| `wide-table-survey` | 2 | CSV Bundle | 15365 | 36372 | 21007 | 42.2% |
| `wide-table-survey` | 3 | SDIF | 15451 | 36372 | 20921 | 42.5% |
| `wide-table-survey` | 4 | JSON Compact | 36372 | 36372 | 0 | 100.0% |
| `wide-table-survey` | 5 | YAML | 50113 | 36372 | -13741 | 137.8% |
| `wide-table-survey` | 6 | JSON Pretty | 58948 | 36372 | -22576 | 162.1% |
| `wide-table-survey` | 7 | XML | 73594 | 36372 | -37222 | 202.3% |

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
| `tiktoken` | CSV Bundle | 101645 | 137942 | 36297 | 73.7% |

#### Ratio Matrix

| Format | `Estimate` | `tiktoken` |
|---|---:|---:|
| CSV Bundle | 61.7% | 73.7% |
| SDIF AI | 61.7% | 74.8% |
| SDIF | 63.7% | 78.3% |
| JSON Compact | 100.0% | 100.0% |
| YAML | 95.3% | 111.4% |
| JSON Pretty | 136.6% | 148.1% |
| XML | 162.0% | 176.8% |

### `github.openapi`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 41843 | 73106 | 31263 | 57.2% |
| `tiktoken` | SDIF AI | 37829 | 62704 | 24875 | 60.3% |

#### Ratio Matrix

| Format | `Estimate` | `tiktoken` |
|---|---:|---:|
| SDIF AI | 57.2% | 60.3% |
| CSV Bundle | 57.3% | 62.3% |
| SDIF | 59.4% | 66.8% |
| JSON Compact | 100.0% | 100.0% |
| YAML | 96.9% | 116.1% |
| JSON Pretty | 132.3% | 155.1% |
| XML | 161.6% | 187.8% |

### `large-audit-trail`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 283498 | 432185 | 148687 | 65.6% |
| `tiktoken` | SDIF AI | 412926 | 540663 | 127737 | 76.4% |

#### Ratio Matrix

| Format | `Estimate` | `tiktoken` |
|---|---:|---:|
| SDIF AI | 65.6% | 76.4% |
| CSV Bundle | 65.6% | 78.1% |
| SDIF | 66.8% | 78.4% |
| JSON Compact | 100.0% | 100.0% |
| YAML | 96.4% | 108.1% |
| JSON Pretty | 128.5% | 133.8% |
| XML | 149.0% | 153.8% |

### `large-knowledge-graph`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 69895 | 129721 | 59826 | 53.9% |
| `tiktoken` | SDIF AI | 86155 | 132864 | 46709 | 64.8% |

#### Ratio Matrix

| Format | `Estimate` | `tiktoken` |
|---|---:|---:|
| SDIF AI | 53.9% | 64.8% |
| CSV Bundle | 53.9% | 66.6% |
| SDIF | 55.7% | 68.5% |
| JSON Compact | 100.0% | 100.0% |
| YAML | 95.4% | 115.7% |
| JSON Pretty | 141.3% | 160.3% |
| XML | 170.4% | 191.6% |

### `large-plan`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 123089 | 201176 | 78087 | 61.2% |
| `tiktoken` | SDIF AI | 141145 | 213238 | 72093 | 66.2% |

#### Ratio Matrix

| Format | `Estimate` | `tiktoken` |
|---|---:|---:|
| SDIF AI | 61.2% | 66.2% |
| CSV Bundle | 61.2% | 67.7% |
| SDIF | 62.7% | 69.1% |
| JSON Compact | 100.0% | 100.0% |
| YAML | 97.0% | 107.7% |
| JSON Pretty | 130.3% | 141.8% |
| XML | 158.3% | 171.7% |

### `large-registry`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 100680 | 220956 | 120276 | 45.6% |
| `tiktoken` | SDIF AI | 154451 | 253063 | 98612 | 61.0% |

#### Ratio Matrix

| Format | `Estimate` | `tiktoken` |
|---|---:|---:|
| SDIF AI | 45.6% | 61.0% |
| CSV Bundle | 45.6% | 63.1% |
| SDIF | 48.2% | 65.7% |
| JSON Compact | 100.0% | 100.0% |
| YAML | 95.0% | 112.2% |
| JSON Pretty | 145.4% | 157.7% |
| XML | 186.9% | 195.5% |

### `large-schema-catalog`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | CSV Bundle | 53815 | 111880 | 58065 | 48.1% |
| `tiktoken` | CSV Bundle | 71357 | 126532 | 55175 | 56.4% |

#### Ratio Matrix

| Format | `Estimate` | `tiktoken` |
|---|---:|---:|
| CSV Bundle | 48.1% | 56.4% |
| SDIF AI | 49.5% | 59.6% |
| SDIF | 51.2% | 62.5% |
| JSON Compact | 100.0% | 100.0% |
| YAML | 97.2% | 118.2% |
| JSON Pretty | 145.9% | 157.6% |
| XML | 176.5% | 186.3% |

### `large-support-export`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 85512 | 148025 | 62513 | 57.8% |
| `tiktoken` | SDIF AI | 94839 | 149622 | 54783 | 63.4% |

#### Ratio Matrix

| Format | `Estimate` | `tiktoken` |
|---|---:|---:|
| SDIF AI | 57.8% | 63.4% |
| CSV Bundle | 57.8% | 64.2% |
| SDIF | 59.5% | 66.9% |
| JSON Compact | 100.0% | 100.0% |
| YAML | 96.8% | 113.1% |
| JSON Pretty | 136.8% | 153.4% |
| XML | 166.6% | 183.6% |

### `large-validation-report`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 95944 | 139832 | 43888 | 68.6% |
| `tiktoken` | SDIF AI | 99633 | 134533 | 34900 | 74.1% |

#### Ratio Matrix

| Format | `Estimate` | `tiktoken` |
|---|---:|---:|
| SDIF AI | 68.6% | 74.1% |
| CSV Bundle | 68.6% | 74.1% |
| SDIF | 69.8% | 76.6% |
| JSON Compact | 100.0% | 100.0% |
| YAML | 98.3% | 111.6% |
| JSON Pretty | 127.0% | 142.7% |
| XML | 146.4% | 167.9% |

### `medium-invoice-batch`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 18476 | 34890 | 16414 | 53.0% |
| `tiktoken` | CSV Bundle | 25965 | 39858 | 13893 | 65.1% |

#### Ratio Matrix

| Format | `Estimate` | `tiktoken` |
|---|---:|---:|
| CSV Bundle | 53.0% | 65.1% |
| SDIF AI | 53.0% | 67.0% |
| SDIF | 54.4% | 69.5% |
| JSON Compact | 100.0% | 100.0% |
| YAML | 98.2% | 117.3% |
| JSON Pretty | 137.3% | 147.9% |
| XML | 170.7% | 176.9% |

### `medium-observability-run`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 13983 | 28689 | 14706 | 48.7% |
| `tiktoken` | SDIF AI | 18170 | 32253 | 14083 | 56.3% |

#### Ratio Matrix

| Format | `Estimate` | `tiktoken` |
|---|---:|---:|
| SDIF AI | 48.7% | 56.3% |
| CSV Bundle | 48.8% | 59.0% |
| SDIF | 50.9% | 63.8% |
| JSON Compact | 100.0% | 100.0% |
| YAML | 95.1% | 119.6% |
| JSON Pretty | 146.4% | 162.2% |
| XML | 179.5% | 196.2% |

### `medium-policy-catalog`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 12446 | 24394 | 11948 | 51.0% |
| `tiktoken` | SDIF AI | 18106 | 28086 | 9980 | 64.5% |

#### Ratio Matrix

| Format | `Estimate` | `tiktoken` |
|---|---:|---:|
| SDIF AI | 51.0% | 64.5% |
| CSV Bundle | 51.1% | 68.2% |
| SDIF | 53.0% | 67.8% |
| JSON Compact | 100.0% | 100.0% |
| YAML | 93.9% | 114.3% |
| JSON Pretty | 142.8% | 156.7% |
| XML | 171.7% | 187.6% |

### `medium-product-catalog`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 11888 | 27843 | 15955 | 42.7% |
| `tiktoken` | SDIF AI | 21319 | 33936 | 12617 | 62.8% |

#### Ratio Matrix

| Format | `Estimate` | `tiktoken` |
|---|---:|---:|
| SDIF AI | 42.7% | 62.8% |
| CSV Bundle | 42.7% | 63.2% |
| SDIF | 45.6% | 67.6% |
| JSON Compact | 100.0% | 100.0% |
| YAML | 94.0% | 117.7% |
| JSON Pretty | 151.8% | 165.0% |
| XML | 192.9% | 203.6% |

### `plan`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF | 246 | 317 | 71 | 77.6% |
| `tiktoken` | SDIF AI | 251 | 302 | 51 | 83.1% |

#### Ratio Matrix

| Format | `Estimate` | `tiktoken` |
|---|---:|---:|
| SDIF | 77.6% | 83.4% |
| SDIF AI | 78.9% | 83.1% |
| CSV Bundle | 82.0% | 95.4% |
| JSON Compact | 100.0% | 100.0% |
| YAML | 94.6% | 110.6% |
| JSON Pretty | 133.1% | 158.6% |
| XML | 164.0% | 199.3% |

### `registry`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 166 | 240 | 74 | 69.2% |
| `tiktoken` | SDIF AI | 149 | 205 | 56 | 72.7% |

#### Ratio Matrix

| Format | `Estimate` | `tiktoken` |
|---|---:|---:|
| SDIF AI | 69.2% | 72.7% |
| SDIF | 70.4% | 75.1% |
| CSV Bundle | 75.0% | 85.4% |
| JSON Compact | 100.0% | 100.0% |
| YAML | 93.3% | 107.3% |
| JSON Pretty | 135.0% | 166.3% |
| XML | 167.1% | 213.7% |

### `schema`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 275 | 529 | 254 | 52.0% |
| `tiktoken` | SDIF AI | 298 | 534 | 236 | 55.8% |

#### Ratio Matrix

| Format | `Estimate` | `tiktoken` |
|---|---:|---:|
| SDIF AI | 52.0% | 55.8% |
| SDIF | 55.0% | 60.5% |
| CSV Bundle | 55.0% | 62.0% |
| JSON Compact | 100.0% | 100.0% |
| YAML | 94.7% | 118.0% |
| JSON Pretty | 152.9% | 178.5% |
| XML | 198.1% | 227.2% |

### `small-api-catalog`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 410 | 791 | 381 | 51.8% |
| `tiktoken` | SDIF AI | 544 | 912 | 368 | 59.6% |

#### Ratio Matrix

| Format | `Estimate` | `tiktoken` |
|---|---:|---:|
| SDIF AI | 51.8% | 59.6% |
| CSV Bundle | 52.7% | 64.1% |
| SDIF | 54.2% | 64.1% |
| JSON Compact | 100.0% | 100.0% |
| YAML | 92.0% | 121.6% |
| JSON Pretty | 153.4% | 171.5% |
| XML | 178.5% | 207.7% |

### `small-incident`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 641 | 1037 | 396 | 61.8% |
| `tiktoken` | SDIF AI | 706 | 1064 | 358 | 66.4% |

#### Ratio Matrix

| Format | `Estimate` | `tiktoken` |
|---|---:|---:|
| SDIF AI | 61.8% | 66.4% |
| SDIF | 63.6% | 68.0% |
| CSV Bundle | 62.6% | 69.5% |
| JSON Compact | 100.0% | 100.0% |
| YAML | 95.2% | 108.7% |
| JSON Pretty | 138.1% | 155.7% |
| XML | 164.1% | 182.4% |

### `small-invoice`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 352 | 661 | 309 | 53.3% |
| `tiktoken` | SDIF AI | 476 | 718 | 242 | 66.3% |

#### Ratio Matrix

| Format | `Estimate` | `tiktoken` |
|---|---:|---:|
| SDIF AI | 53.3% | 66.3% |
| CSV Bundle | 54.5% | 67.5% |
| SDIF | 55.1% | 70.1% |
| JSON Compact | 100.0% | 100.0% |
| YAML | 96.1% | 118.4% |
| JSON Pretty | 142.4% | 161.4% |
| XML | 179.3% | 196.9% |

### `validation-report`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 173 | 254 | 81 | 68.1% |
| `tiktoken` | SDIF AI | 149 | 225 | 76 | 66.2% |

#### Ratio Matrix

| Format | `Estimate` | `tiktoken` |
|---|---:|---:|
| SDIF AI | 68.1% | 66.2% |
| SDIF | 72.4% | 73.8% |
| CSV Bundle | 76.4% | 86.7% |
| JSON Compact | 100.0% | 100.0% |
| YAML | 92.1% | 109.3% |
| JSON Pretty | 135.8% | 169.8% |
| XML | 166.1% | 213.3% |

### `wide-table-survey`

#### Winners by Tokenizer

| Tokenizer | Winner | Tokens | JSON Compact Tokens | Saved Tokens | Ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| `Estimate` | SDIF AI | 4652 | 16230 | 11578 | 28.7% |
| `tiktoken` | SDIF AI | 15224 | 36372 | 21148 | 41.9% |

#### Ratio Matrix

| Format | `Estimate` | `tiktoken` |
|---|---:|---:|
| SDIF AI | 28.7% | 41.9% |
| CSV Bundle | 28.7% | 42.2% |
| SDIF | 29.4% | 42.5% |
| JSON Compact | 100.0% | 100.0% |
| YAML | 108.4% | 137.8% |
| JSON Pretty | 192.5% | 162.1% |
| XML | 229.8% | 202.3% |

## Raw Count Matrix

This section contains raw counts only. Ratios are intentionally excluded here because they are tokenizer-specific.

### `deep-hierarchy-project`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| CSV Bundle | 292754 | 73189 | - | 101645 | - | - |
| SDIF AI | 292716 | 73179 | - | 103205 | - | - |
| SDIF | 302202 | 75551 | - | 107951 | - | - |
| JSON Compact | 474294 | 118574 | - | 137942 | - | - |
| YAML | 452163 | 113041 | - | 153735 | - | - |
| JSON Pretty | 648068 | 162017 | - | 204303 | - | - |
| XML | 768236 | 192059 | - | 243817 | - | - |

### `github.openapi`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 167369 | 41843 | - | 37829 | - | - |
| CSV Bundle | 167539 | 41885 | - | 39074 | - | - |
| SDIF | 173649 | 43413 | - | 41867 | - | - |
| JSON Compact | 292422 | 73106 | - | 62704 | - | - |
| YAML | 283256 | 70814 | - | 72783 | - | - |
| JSON Pretty | 386842 | 96711 | - | 97266 | - | - |
| XML | 472655 | 118164 | - | 117756 | - | - |

### `large-audit-trail`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 1133989 | 283498 | - | 412926 | - | - |
| CSV Bundle | 1134036 | 283509 | - | 422357 | - | - |
| SDIF | 1155527 | 288882 | - | 423698 | - | - |
| JSON Compact | 1728738 | 432185 | - | 540663 | - | - |
| YAML | 1666793 | 416699 | - | 584405 | - | - |
| JSON Pretty | 2222275 | 555569 | - | 723268 | - | - |
| XML | 2576525 | 644132 | - | 831285 | - | - |

### `large-knowledge-graph`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 279580 | 69895 | - | 86155 | - | - |
| CSV Bundle | 279620 | 69905 | - | 88495 | - | - |
| SDIF | 289242 | 72311 | - | 90989 | - | - |
| JSON Compact | 518882 | 129721 | - | 132864 | - | - |
| YAML | 495208 | 123802 | - | 153731 | - | - |
| JSON Pretty | 733208 | 183302 | - | 213005 | - | - |
| XML | 884387 | 221097 | - | 254541 | - | - |

### `large-plan`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 492354 | 123089 | - | 141145 | - | - |
| CSV Bundle | 492413 | 123104 | - | 144465 | - | - |
| SDIF | 504796 | 126199 | - | 147369 | - | - |
| JSON Compact | 804703 | 201176 | - | 213238 | - | - |
| YAML | 780329 | 195083 | - | 229718 | - | - |
| JSON Pretty | 1048494 | 262124 | - | 302381 | - | - |
| XML | 1273626 | 318407 | - | 366170 | - | - |

### `large-registry`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 402720 | 100680 | - | 154451 | - | - |
| CSV Bundle | 402772 | 100693 | - | 159696 | - | - |
| SDIF | 426166 | 106542 | - | 166177 | - | - |
| JSON Compact | 883824 | 220956 | - | 253063 | - | - |
| YAML | 839949 | 209988 | - | 283892 | - | - |
| JSON Pretty | 1285316 | 321329 | - | 399186 | - | - |
| XML | 1652261 | 413066 | - | 494780 | - | - |

### `large-schema-catalog`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| CSV Bundle | 215257 | 53815 | - | 71357 | - | - |
| SDIF AI | 221599 | 55400 | - | 75464 | - | - |
| SDIF | 228953 | 57239 | - | 79144 | - | - |
| JSON Compact | 447520 | 111880 | - | 126532 | - | - |
| YAML | 435031 | 108758 | - | 149601 | - | - |
| JSON Pretty | 653078 | 163270 | - | 199367 | - | - |
| XML | 790035 | 197509 | - | 235726 | - | - |

### `large-support-export`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 342047 | 85512 | - | 94839 | - | - |
| CSV Bundle | 342094 | 85524 | - | 96002 | - | - |
| SDIF | 352437 | 88110 | - | 100037 | - | - |
| JSON Compact | 592098 | 148025 | - | 149622 | - | - |
| YAML | 573388 | 143347 | - | 169236 | - | - |
| JSON Pretty | 810127 | 202532 | - | 229579 | - | - |
| XML | 986732 | 246683 | - | 274660 | - | - |

### `large-validation-report`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 383776 | 95944 | - | 99633 | - | - |
| CSV Bundle | 383821 | 95956 | - | 99656 | - | - |
| SDIF | 390534 | 97634 | - | 103015 | - | - |
| JSON Compact | 559328 | 139832 | - | 134533 | - | - |
| YAML | 549978 | 137495 | - | 150198 | - | - |
| JSON Pretty | 710381 | 177596 | - | 192034 | - | - |
| XML | 818657 | 204665 | - | 225834 | - | - |

### `medium-invoice-batch`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| CSV Bundle | 73941 | 18486 | - | 25965 | - | - |
| SDIF AI | 73903 | 18476 | - | 26707 | - | - |
| SDIF | 75859 | 18965 | - | 27688 | - | - |
| JSON Compact | 139558 | 34890 | - | 39858 | - | - |
| YAML | 137030 | 34258 | - | 46758 | - | - |
| JSON Pretty | 191590 | 47898 | - | 58931 | - | - |
| XML | 238165 | 59542 | - | 70501 | - | - |

### `medium-observability-run`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 55931 | 13983 | - | 18170 | - | - |
| CSV Bundle | 55978 | 13995 | - | 19018 | - | - |
| SDIF | 58377 | 14595 | - | 20572 | - | - |
| JSON Compact | 114756 | 28689 | - | 32253 | - | - |
| YAML | 109099 | 27275 | - | 38569 | - | - |
| JSON Pretty | 167981 | 41996 | - | 52300 | - | - |
| XML | 205986 | 51497 | - | 63274 | - | - |

### `medium-policy-catalog`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 49782 | 12446 | - | 18106 | - | - |
| SDIF | 51672 | 12918 | - | 19054 | - | - |
| CSV Bundle | 49822 | 12456 | - | 19159 | - | - |
| JSON Compact | 97573 | 24394 | - | 28086 | - | - |
| YAML | 91628 | 22907 | - | 32094 | - | - |
| JSON Pretty | 139351 | 34838 | - | 43999 | - | - |
| XML | 167499 | 41875 | - | 52678 | - | - |

### `medium-product-catalog`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 47552 | 11888 | - | 21319 | - | - |
| CSV Bundle | 47599 | 11900 | - | 21445 | - | - |
| SDIF | 50784 | 12696 | - | 22938 | - | - |
| JSON Compact | 111369 | 27843 | - | 33936 | - | - |
| YAML | 104720 | 26180 | - | 39958 | - | - |
| JSON Pretty | 169056 | 42264 | - | 55984 | - | - |
| XML | 214848 | 53712 | - | 69082 | - | - |

### `plan`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 1000 | 250 | - | 251 | - | - |
| SDIF | 984 | 246 | - | 252 | - | - |
| CSV Bundle | 1039 | 260 | - | 288 | - | - |
| JSON Compact | 1268 | 317 | - | 302 | - | - |
| YAML | 1197 | 300 | - | 334 | - | - |
| JSON Pretty | 1688 | 422 | - | 479 | - | - |
| XML | 2080 | 520 | - | 602 | - | - |

### `registry`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 662 | 166 | - | 149 | - | - |
| SDIF | 674 | 169 | - | 154 | - | - |
| CSV Bundle | 720 | 180 | - | 175 | - | - |
| JSON Compact | 960 | 240 | - | 205 | - | - |
| YAML | 896 | 224 | - | 220 | - | - |
| JSON Pretty | 1293 | 324 | - | 341 | - | - |
| XML | 1601 | 401 | - | 438 | - | - |

### `schema`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 1097 | 275 | - | 298 | - | - |
| SDIF | 1161 | 291 | - | 323 | - | - |
| CSV Bundle | 1161 | 291 | - | 331 | - | - |
| JSON Compact | 2113 | 529 | - | 534 | - | - |
| YAML | 2004 | 501 | - | 630 | - | - |
| JSON Pretty | 3235 | 809 | - | 953 | - | - |
| XML | 4189 | 1048 | - | 1213 | - | - |

### `small-api-catalog`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 1640 | 410 | - | 544 | - | - |
| CSV Bundle | 1666 | 417 | - | 585 | - | - |
| SDIF | 1716 | 429 | - | 585 | - | - |
| JSON Compact | 3163 | 791 | - | 912 | - | - |
| YAML | 2909 | 728 | - | 1109 | - | - |
| JSON Pretty | 4849 | 1213 | - | 1564 | - | - |
| XML | 5647 | 1412 | - | 1894 | - | - |

### `small-incident`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 2563 | 641 | - | 706 | - | - |
| SDIF | 2637 | 660 | - | 723 | - | - |
| CSV Bundle | 2594 | 649 | - | 740 | - | - |
| JSON Compact | 4148 | 1037 | - | 1064 | - | - |
| YAML | 3947 | 987 | - | 1157 | - | - |
| JSON Pretty | 5727 | 1432 | - | 1657 | - | - |
| XML | 6808 | 1702 | - | 1941 | - | - |

### `small-invoice`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 1406 | 352 | - | 476 | - | - |
| CSV Bundle | 1439 | 360 | - | 485 | - | - |
| SDIF | 1454 | 364 | - | 503 | - | - |
| JSON Compact | 2643 | 661 | - | 718 | - | - |
| YAML | 2537 | 635 | - | 850 | - | - |
| JSON Pretty | 3764 | 941 | - | 1159 | - | - |
| XML | 4738 | 1185 | - | 1414 | - | - |

### `validation-report`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 691 | 173 | - | 149 | - | - |
| SDIF | 735 | 184 | - | 166 | - | - |
| CSV Bundle | 773 | 194 | - | 195 | - | - |
| JSON Compact | 1014 | 254 | - | 225 | - | - |
| YAML | 934 | 234 | - | 246 | - | - |
| JSON Pretty | 1378 | 345 | - | 382 | - | - |
| XML | 1685 | 422 | - | 480 | - | - |

### `wide-table-survey`

| Format | Bytes | `Estimate` | `TokenX` | `tiktoken` | `Llama3` | `Claude` |
| --- | ---: |---:|---:|---:|---:|---:|
| SDIF AI | 18606 | 4652 | - | 15224 | - | - |
| CSV Bundle | 18632 | 4658 | - | 15365 | - | - |
| SDIF | 19054 | 4764 | - | 15451 | - | - |
| JSON Compact | 64917 | 16230 | - | 36372 | - | - |
| YAML | 70375 | 17594 | - | 50113 | - | - |
| JSON Pretty | 124951 | 31238 | - | 58948 | - | - |
| XML | 149167 | 37292 | - | 73594 | - | - |

## Environment

| Variable | Value |
| --- | --- |
| `.env loaded` | `yes` |
| `SDIF_BENCHMARK_TOON` | `0` |
| `SDIF_BENCHMARK_GOLDEN_DIR` | _unset_ |
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
- `Llama3` is disabled: Disabled through SDIF_BENCHMARK_LLAMA=0.
- `Claude` is disabled: Disabled. Set SDIF_BENCHMARK_CLAUDE=1 to enable API token counting.

## Artifacts

- Raw log: `benchmarks/results/token_efficiency/comparison.log`
- Markdown report: `benchmarks/results/token_efficiency/comparison.md`
- Summary report: `benchmarks/results/token_efficiency/summary.md`
- Structured JSON report: `benchmarks/results/token_efficiency/comparison.json`
- Structured SDIF report: `benchmarks/results/token_efficiency/comparison.sdif`
- SDIF AI projection: `benchmarks/results/token_efficiency/comparison.sdif.ai`
- Compared corpus files: `benchmarks/results/token_efficiency/corpus`
- Result directory: `benchmarks/results/token_efficiency`
