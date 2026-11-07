# Python vs Web consistency report

- Python core: `prototype/rules_v3.py` (rules_v3/4.0)
- Web core: `web/assets/core.js` (rules_v3_web/4.0)
- rule pack: `RP-V4.0` (single source for both)
- browser: `msedge.exe` headless, disabled (--host-resolver-rules=MAP * ~NOTFOUND)
- numeric tolerance: `1e-09` (D-01). Enums, strings, nulls and the exported CSV text must match exactly.
- exported artefacts compared per case: `json_document`, `review_csv`, `feedback_csv`
- result: **MATCH** - 40/40 cases match on the complete structured payload

| case | scenario under test | result |
|---|---|---|
| W-01 | 2 SKU single answer; RF/SIT mismatch at SKU2 | MATCH |
| W-02 | 4-5 SKU tie -> RANGE, both priced (RF/SIT@4 and @5) | MATCH |
| W-03 | missing key factor (panel unanswered) | MATCH |
| W-04 | no wave declared anywhere | MATCH |
| W-05 | explicit LATER_WAVE specs excluded from the current wave | MATCH |
| W-06 | current wave identical to full project | MATCH |
| W-07 | current wave differs from full project | MATCH |
| W-08 | 3 SKU single answer: Green/SIT and RF/SIT mismatches at 3 SKU | MATCH |
| W-09 | 6 SKU: Safety/FVT 9.6 vs adopted 10, RF/SIT 15 vs adopted 10 | MATCH |
| W-10 | certification range comes only from the SKU range | MATCH |
| W-11 | override equal to the adopted Appendix value | MATCH |
| W-12 | J33 never added on top of the adopted value | MATCH |
| W-13 | MEPA / HW PA read as fixed per-phase amounts at 2 SKU | MATCH |
| W-14 | reuse deduction is allowed | MATCH |
| W-15 | reuse without proof is not deducted | MATCH |
| W-16 | single_value=false has no priced result at all (undetermined input) | MATCH |
| W-17 | out-of-domain input stops that scenario only | MATCH |
| W-18 | risk reserve charged on baseline demand | MATCH |
| W-19 | PCBA extra demand is never summed with units | MATCH |
| W-20 | FVT only phase scope | MATCH |
| W-21 | explicitly UNKNOWN wave fans the current wave out | MATCH |
| W-22 | NO_EXPLICIT_ASSIGNMENT (UI: 未特别指定) is not UNKNOWN | MATCH |
| W-23 | override plus reuse plus risk together | MATCH |
| W-24 | mixed reuse states in one ledger | MATCH |
| W-25 | 4 SKU single answer: the Appendix total is counted exactly once | MATCH |
| W-26 | 3 SKU: Green/SIT adopts 6.0 while the Main Table 9.0 stays as audit | MATCH |
| W-27 | 6 SKU: Safety/FVT adopts 10.0; the 9.6 audit value keeps its decimal | MATCH |
| W-28 | 4-5 RANGE prices Certification separately for both candidates | MATCH |
| W-29 | override on a cell whose Main Table already agrees with the Appendix | MATCH |
| W-30 | override that does not match the adopted value is flagged, not hidden | MATCH |
| W-31 | override never escapes into the rule pack: snapshot keeps THIS_ANALYSIS_ONLY | MATCH |
| W-32 | underlying decimals survive risk and export (D-01) | MATCH |
| W-33 | Current Wave versus Full Project with a real later wave and a SKU range | MATCH |
| W-34 | 2 SKU: J33 evidence plus MEPA / HW PA fixed amounts together | MATCH |
| W-35 | integration: reuse + PCBA + extra demand + risk in one analysis | MATCH |
| W-36 | SIT only phase scope (FVT excluded, no global phase ratio) | MATCH |
| W-37 | 2 SKU: RF/SIT override to exactly the adopted value plus a risk reserve | MATCH |
| W-38 | UNKNOWN wave at 3 SKU with Certification mismatches | MATCH |
| W-39 | 6 SKU with a reuse deduction and a risk reserve (decimal chain) | MATCH |
| W-40 | out-of-domain in the current wave only, full project still priced | MATCH |

## Certification mismatch coverage

Every cell where the retained Main Table derivation disagrees with the adopted Appendix total is exercised by the cases below (each case also compares the exports).

| mismatch cell | cases |
|---|---|
| Green/SIT@3 | W-08, W-26 |
| Safety/FVT@6 | W-09, W-27 |
| RF/SIT@2 | W-01, W-08, W-11, W-30, W-31, W-37, W-38 |
| RF/SIT@3 | W-08, W-11, W-26, W-30, W-31, W-38 |
| RF/SIT@4 | W-02, W-10, W-28, W-33, W-36 |
| RF/SIT@5 | W-02, W-10, W-28, W-33, W-36 |
| RF/SIT@6 | W-09, W-27 |

## What is compared

Every field of the serialised output: SKU state, recommended_sku, preferred_sku, SKU range, priced candidates, Current Wave and Full Project counts and wave basis, every Function line and its Quantity Model, the adopted Certification value (Appendix), the retained Main Table value, the derived audit value, the delta, the verification status, the counted-times flags, the J33 role, the reuse ledger, every Review Item, every null field and every underlying decimal - plus the JSON export document and both CSV exports as text.

Any divergence blocks delivery (task section 26).
