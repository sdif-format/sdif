# SDIF Round-Trip Fidelity Benchmark — Summary

- Generated at: `2026-05-22T08:11:56Z`
- Documents: `21`

## Key Findings

Fidelity measures semantic preservation when converting `JSON → format → JSON`.
100% = lossless. Lower = semantic loss (type coercion, nesting collapse, etc.).

| Format | Avg Overall | Coverage |
| --- | ---: | ---: |
| JSON Compact | 100.0% | 21/21 |
| JSON Pretty | 100.0% | 21/21 |
| YAML | 100.0% | 21/21 |
| SDIF | 100.0% | 20/21 |
| CSV Bundle | 98.5% | 21/21 |
| XML | 89.2% | 21/21 |

## Score Definitions

| Score | Definition |
| --- | --- |
| **Value fidelity** | % of leaf values that round-trip to the same value (string comparison). |
| **Type fidelity** | % of leaf values whose Python type is preserved exactly. |
| **Structure fidelity** | % of key paths from the original that exist in the round-tripped document. |
| **Overall fidelity** | Harmonic mean of the three scores above. |
