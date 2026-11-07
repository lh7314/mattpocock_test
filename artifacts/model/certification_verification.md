# Certification per-cell verification

- baseline: `BASELINE-CS-ODM-001` (original_documents\Sample_Requirement_SKU_and_Demand_Baseline_CleanSheet_20261030_V01_FORMAL.xlsx, SHA-256 `48a360ff2ffd086e41d6b90a916f64fe52d9bc13efba07b8377b2945c846ab5a`)
- generated: 2026-11-06T08:36:36+00:00 by `tools/verify_certification.py`
- tolerance: `1e-09` (D-01 - no business rounding, comparison only)

## Relationship being verified

```
derived_total = main_table_per_sku_quantity x sku_count
VERIFIED  when  derived_total == appendix_total   (within tolerance)
```

DEC-10: the Appendix total is the adopted value for the team-trial phase and is counted exactly once. The Main Table per-SKU quantity and its derived total stay on record for audit and difference analysis and are not counted again. There is still one model, never a band, never a main + appendix addition.

## Result

| cells | VERIFIED | MISMATCH | NOT_EVALUABLE |
|---:|---:|---:|---:|
| 40 | 33 | 7 | 0 |

**ORI-02 status: `PARTIALLY_RESOLVED`**

## Per-cell grid

| function | phase | SKU | main /SKU | derived | appendix | delta | status | main row | apx row |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| EMC | FVT | 2 | 0 | 0 | 0 | 0 | VERIFIED | 27 | 53 |
| EMC | FVT | 3 | 0 | 0 | 0 | 0 | VERIFIED | 27 | 53 |
| EMC | FVT | 4 | 0 | 0 | 0 | 0 | VERIFIED | 27 | 53 |
| EMC | FVT | 5 | 0 | 0 | 0 | 0 | VERIFIED | 27 | 53 |
| EMC | FVT | 6 | 0 | 0 | 0 | 0 | VERIFIED | 27 | 53 |
| EMC | SIT | 2 | 1 | 2 | 2 | 0 | VERIFIED | 28 | 54 |
| EMC | SIT | 3 | 1 | 3 | 3 | 0 | VERIFIED | 28 | 54 |
| EMC | SIT | 4 | 1 | 4 | 4 | 0 | VERIFIED | 28 | 54 |
| EMC | SIT | 5 | 1 | 5 | 5 | 0 | VERIFIED | 28 | 54 |
| EMC | SIT | 6 | 1 | 6 | 6 | 0 | VERIFIED | 28 | 54 |
| Green | FVT | 2 | 0 | 0 | 0 | 0 | VERIFIED | 29 | 55 |
| Green | FVT | 3 | 0 | 0 | 0 | 0 | VERIFIED | 29 | 55 |
| Green | FVT | 4 | 0 | 0 | 0 | 0 | VERIFIED | 29 | 55 |
| Green | FVT | 5 | 0 | 0 | 0 | 0 | VERIFIED | 29 | 55 |
| Green | FVT | 6 | 0 | 0 | 0 | 0 | VERIFIED | 29 | 55 |
| Green | SIT | 2 | 3 | 6 | 6 | 0 | VERIFIED | 30 | 56 |
| Green | SIT | 3 | 3 | 9 | 6 | -3 | MISMATCH | 30 | 56 |
| Green | SIT | 4 | 1.5 | 6 | 6 | 0 | VERIFIED | 30 | 56 |
| Green | SIT | 5 | 1.2 | 6 | 6 | 0 | VERIFIED | 30 | 56 |
| Green | SIT | 6 | 1 | 6 | 6 | 0 | VERIFIED | 30 | 56 |
| Safety | FVT | 2 | 5 | 10 | 10 | 0 | VERIFIED | 31 | 57 |
| Safety | FVT | 3 | 3 | 9 | 9 | 0 | VERIFIED | 31 | 57 |
| Safety | FVT | 4 | 2.5 | 10 | 10 | 0 | VERIFIED | 31 | 57 |
| Safety | FVT | 5 | 2 | 10 | 10 | 0 | VERIFIED | 31 | 57 |
| Safety | FVT | 6 | 1.6 | 9.6 | 10 | 0.4 | MISMATCH | 31 | 57 |
| Safety | SIT | 2 | 3 | 6 | 6 | 0 | VERIFIED | 32 | 58 |
| Safety | SIT | 3 | 2 | 6 | 6 | 0 | VERIFIED | 32 | 58 |
| Safety | SIT | 4 | 1.5 | 6 | 6 | 0 | VERIFIED | 32 | 58 |
| Safety | SIT | 5 | 1.2 | 6 | 6 | 0 | VERIFIED | 32 | 58 |
| Safety | SIT | 6 | 1 | 6 | 6 | 0 | VERIFIED | 32 | 58 |
| RF Certification | FVT | 2 | 0 | 0 | 0 | 0 | VERIFIED | 33 | 59 |
| RF Certification | FVT | 3 | 0 | 0 | 0 | 0 | VERIFIED | 33 | 59 |
| RF Certification | FVT | 4 | 0 | 0 | 0 | 0 | VERIFIED | 33 | 59 |
| RF Certification | FVT | 5 | 0 | 0 | 0 | 0 | VERIFIED | 33 | 59 |
| RF Certification | FVT | 6 | 0 | 0 | 0 | 0 | VERIFIED | 33 | 59 |
| RF Certification | SIT | 2 | 7.5 | 15 | 8 | -7 | MISMATCH | 34 | 60 |
| RF Certification | SIT | 3 | 5 | 15 | 9 | -6 | MISMATCH | 34 | 60 |
| RF Certification | SIT | 4 | 3.75 | 15 | 10 | -5 | MISMATCH | 34 | 60 |
| RF Certification | SIT | 5 | 3 | 15 | 10 | -5 | MISMATCH | 34 | 60 |
| RF Certification | SIT | 6 | 2.5 | 15 | 10 | -5 | MISMATCH | 34 | 60 |

## Appendix internal consistency

Does the appendix block add up to its own TTL rows? A consistent appendix is a strong argument that the appendix numbers are deliberate, not stray formulas.

| appendix row label | phase | SKU | sum of components | appendix TTL | status |
|---|---|---:|---:|---:|---|
| TTL FVT | FVT | 2 | 10 | 10 | VERIFIED |
| TTL FVT | FVT | 3 | 9 | 9 | VERIFIED |
| TTL FVT | FVT | 4 | 10 | 10 | VERIFIED |
| TTL FVT | FVT | 5 | 10 | 10 | VERIFIED |
| TTL FVT | FVT | 6 | 10 | 10 | VERIFIED |
| TTL SIT | SIT | 2 | 22 | 22 | VERIFIED |
| TTL SIT | SIT | 3 | 24 | 24 | VERIFIED |
| TTL SIT | SIT | 4 | 26 | 26 | VERIFIED |
| TTL SIT | SIT | 5 | 27 | 27 | VERIFIED |
| TTL SIT | SIT | 6 | 28 | 28 | VERIFIED |

Appendix internally consistent across every SKU band: **YES**

## Main Table column shape

A genuine per-SKU rate stays flat as the SKU count changes. A column that falls as 1/N is a back-derivation from a flat total. This is reported as evidence only - the Owner's stated relationship is still the one being verified, and the workbook values are never modified.

| function | phase | shape | main /SKU at SKU2..SKU6 | main x SKU at SKU2..SKU6 |
|---|---|---|---|---|
| EMC | FVT | `TRUE_PER_SKU_RATE` | 0, 0, 0, 0, 0 | 0, 0, 0, 0, 0 |
| EMC | SIT | `TRUE_PER_SKU_RATE` | 1, 1, 1, 1, 1 | 2, 3, 4, 5, 6 |
| Green | FVT | `TRUE_PER_SKU_RATE` | 0, 0, 0, 0, 0 | 0, 0, 0, 0, 0 |
| Green | SIT | `IRREGULAR` | 3, 3, 1.5, 1.2, 1 | 6, 9, 6, 6, 6 |
| Safety | FVT | `IRREGULAR` | 5, 3, 2.5, 2, 1.6 | 10, 9, 10, 10, 9.6 |
| Safety | SIT | `BACK_DERIVED_FROM_FLAT_TOTAL` | 3, 2, 1.5, 1.2, 1 | 6, 6, 6, 6, 6 |
| RF Certification | FVT | `TRUE_PER_SKU_RATE` | 0, 0, 0, 0, 0 | 0, 0, 0, 0, 0 |
| RF Certification | SIT | `BACK_DERIVED_FROM_FLAT_TOTAL` | 7.5, 5, 3.75, 3, 2.5 | 15, 15, 15, 15, 15 |

## Impact of every mismatch on the project total

DEC-10 adopts the Appendix total, so this column is now the change of the adopted number against the Main Table derivation that Phase 3a published. The Main Table column is audit evidence and is not counted in the total.

| function | phase | SKU | main derived (audit, not counted) | Appendix (adopted) | change of adopted value |
|---|---|---:|---:|---:|---:|
| Green | SIT | 3 | 9 | 6 | -3 |
| Safety | FVT | 6 | 9.6 | 10 | 0.4 |
| RF Certification | SIT | 2 | 15 | 8 | -7 |
| RF Certification | SIT | 3 | 15 | 9 | -6 |
| RF Certification | SIT | 4 | 15 | 10 | -5 |
| RF Certification | SIT | 5 | 15 | 10 | -5 |
| RF Certification | SIT | 6 | 15 | 10 | -5 |

## J33

- cell: `J33` (merged `J33:J34`, attached to RF Certification)
- declared scope: *this data for 2 antenna source +2 wlan source refrence*
- declared reference scenario: 2 antenna sources, 2 WLAN cards
- role assigned: `DECLARED_NOT_GENERALIZED` (candidate `CERTIFICATION_BREAKDOWN_EVIDENCE`)
- additive to the Main Table result: **NO**
- MVP must add Antenna / WLAN inputs now: **NO**

| reading | total | main x SKU | appendix | explains main | explains appendix |
|---|---:|---:|---:|---|---|
| SKU2 SIT CERTIFICATION_SUBSET | 11 | 15 | 8 | False | False |
| SKU2 SIT FULL | 27 | 15 | 8 | False | False |
| SKU3 SIT CERTIFICATION_SUBSET | 11 | 15 | 9 | False | False |
| SKU3 SIT FULL | 27 | 15 | 9 | False | False |
| SKU4 SIT CERTIFICATION_SUBSET | 11 | 15 | 10 | False | False |
| SKU4 SIT FULL | 27 | 15 | 10 | False | False |
| SKU5 SIT CERTIFICATION_SUBSET | 11 | 15 | 10 | False | False |
| SKU5 SIT FULL | 27 | 15 | 10 | False | False |
| SKU6 SIT CERTIFICATION_SUBSET | 11 | 15 | 10 | False | False |
| SKU6 SIT FULL | 27 | 15 | 10 | False | False |

J33 bracket sensitivity (both bounds come from wording inside J33 itself, nothing is invented):

- floor (11) - every WLAN card takes the C1PC / module route, so FCC needs no whole machine
- ceiling (27) - every line item needs its own whole machines, FCC = intel_wlan x antenna x 4
- Main Table derived total 15 inside that bracket: **True**
- Appendix totals 8-10 inside that bracket: **False**
- Appendix below the floor: **True**

> 15 is inside the bracket: consistent with a mix where some WLAN cards take the C1PC/module route (no whole machine) and others do not. The Appendix 8-10 sits BELOW the floor of a 2-antenna / 2-WLAN-card project, so the Appendix cannot be the same reference scenario as J33. Neither value is reproducible from J33 alone.

Raw J33 text (verbatim, unmodified source evidence):

```
this data for 2 antenna source +2 wlan source refrence:
1.SRRC *2(PRC 型号核准);如果网卡数量大于天线数量，整机需求基于WLAN卡型号数量；
2.CE *4 =antenna *wlan（欧盟）,如果网卡数量大于天线数量，需额外提供网卡单体送测；
3.FCC(intel WLAN 数量*天线数量)*4（如果是C1PC ,就不需要整机）,其他wlan source(Non-intel) combine with CE.;
4.印尼* 2  .
5.Mexico *1.
6.资安*2（欧盟网络安全）
```

## Legacy competing-model behaviour audit

Forbidden phrases in the live calculation path (`rules_v3.py`, `core.js`, `quantity_model_v3.json`):

- none. The Phase 2 competing-model wording is gone from the live path.

## Superseded interpretations (must never return)

- Main Table and Appendix are competing models
- Certification has two mutually exclusive rules
- Appendix 8-10 is an independent capping model
- the Certification range comes from Main vs Appendix competition
- adopted_absolute must stay null because of model competition
- the Main Table derived total is the adopted project number (superseded by DEC-10; it stays as audit evidence only)
