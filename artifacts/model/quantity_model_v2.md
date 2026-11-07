# Quantity Model v2 (evidence driven, machine derived)

- baseline: `BASELINE-CS-ODM-001` (DRAFT_UNCONFIRMED_BY_OWNER)
- source: `original_documents\Sample_Requirement_SKU_and_Demand_Baseline_CleanSheet_20261030_V01_FORMAL.xlsx` / sheet `CS ODM sample `
- status: **DRAFT_UNCONFIRMED_BY_OWNER**
- tolerance `1e-09` - comparison only, D-01 rounding is NONE

## Summary

| key | value |
|---|---|
| cells_total | 42 |
| by_quantity_model | {"PER_SKU_RATE": 30, "PER_PHASE_FIXED": 4, "UNRESOLVED": 8} |
| by_value_access | {"MAIN_TABLE_DERIVED": 30, "ABSOLUTE_TABLE_READ": 12} |
| owner_review_cells | 12 |
| contested_cells | 4 |
| model_questions | 6 |
| embedded_sharing_suspected_functions | ['Audio', 'BIOS', 'EMC', 'EMC Test', 'Green', 'INTEL', 'ITE', 'ME', 'MFG', 'NV', 'PD', 'RF Certification', 'RF Test', 'Safety', 'THM'] |

## Quantity model per (Function, Phase)

| Function | Phase | Model | Shape | Value access | Conflicting SKU | Owner Review |
|---|---|---|---|---|---|---|
| HW | FVT | PER_SKU_RATE | RAMP | MAIN_TABLE_DERIVED | - |  |
| HW | SIT | PER_SKU_RATE | RAMP | MAIN_TABLE_DERIVED | - |  |
| ME | FVT | PER_SKU_RATE | NEAR_FLAT_WITH_DIP | MAIN_TABLE_DERIVED | - |  |
| ME | SIT | PER_SKU_RATE | NEAR_FLAT_WITH_DIP | MAIN_TABLE_DERIVED | - |  |
| THM | FVT | PER_SKU_RATE | NEAR_FLAT_WITH_DIP | MAIN_TABLE_DERIVED | - |  |
| THM | SIT | PER_SKU_RATE | NEAR_FLAT_WITH_DIP | MAIN_TABLE_DERIVED | - |  |
| Audio | FVT | PER_SKU_RATE | NEAR_FLAT_WITH_DIP | MAIN_TABLE_DERIVED | - |  |
| Audio | SIT | PER_SKU_RATE | NEAR_FLAT_WITH_DIP | MAIN_TABLE_DERIVED | - |  |
| RF Test | FVT | PER_SKU_RATE | NEAR_FLAT_WITH_DIP | MAIN_TABLE_DERIVED | - |  |
| RF Test | SIT | PER_SKU_RATE | NEAR_FLAT_WITH_DIP | MAIN_TABLE_DERIVED | - |  |
| EMC Test | FVT | PER_SKU_RATE | CONSTANT | MAIN_TABLE_DERIVED | - |  |
| EMC Test | SIT | PER_SKU_RATE | CONSTANT | MAIN_TABLE_DERIVED | - |  |
| SED | FVT | PER_SKU_RATE | RAMP | MAIN_TABLE_DERIVED | - |  |
| SED | SIT | PER_SKU_RATE | RAMP | MAIN_TABLE_DERIVED | - |  |
| SS | FVT | PER_SKU_RATE | RAMP | MAIN_TABLE_DERIVED | - |  |
| SS | SIT | PER_SKU_RATE | RAMP | MAIN_TABLE_DERIVED | - |  |
| PD | FVT | PER_SKU_RATE | NEAR_FLAT_WITH_DIP | MAIN_TABLE_DERIVED | - |  |
| PD | SIT | PER_SKU_RATE | NEAR_FLAT_WITH_DIP | MAIN_TABLE_DERIVED | - |  |
| SWPA | FVT | PER_SKU_RATE | RAMP | MAIN_TABLE_DERIVED | - |  |
| SWPA | SIT | PER_SKU_RATE | RAMP | MAIN_TABLE_DERIVED | - |  |
| MEPA | FVT | PER_PHASE_FIXED | RAMP | ABSOLUTE_TABLE_READ | SKU2 | YES |
| MEPA | SIT | PER_PHASE_FIXED | RAMP | ABSOLUTE_TABLE_READ | SKU2 | YES |
| HW PA | FVT | PER_PHASE_FIXED | RAMP | ABSOLUTE_TABLE_READ | - | YES |
| HW PA | SIT | PER_PHASE_FIXED | RAMP | ABSOLUTE_TABLE_READ | - | YES |
| EMC | FVT | UNRESOLVED | CONSTANT | ABSOLUTE_TABLE_READ | - | YES |
| EMC | SIT | UNRESOLVED | RAMP | ABSOLUTE_TABLE_READ | - | YES |
| Green | FVT | UNRESOLVED | CONSTANT | ABSOLUTE_TABLE_READ | - | YES |
| Green | SIT | UNRESOLVED | IRREGULAR | ABSOLUTE_TABLE_READ | SKU3 | YES |
| Safety | FVT | UNRESOLVED | NEAR_FLAT_WITH_DIP | ABSOLUTE_TABLE_READ | - | YES |
| Safety | SIT | UNRESOLVED | CONSTANT | ABSOLUTE_TABLE_READ | - | YES |
| RF Certification | FVT | UNRESOLVED | CONSTANT | ABSOLUTE_TABLE_READ | - | YES |
| RF Certification | SIT | UNRESOLVED | CONSTANT | ABSOLUTE_TABLE_READ | SKU2,SKU3,SKU4,SKU5,SKU6 | YES |
| BIOS | FVT | PER_SKU_RATE | NEAR_FLAT_WITH_DIP | MAIN_TABLE_DERIVED | - |  |
| BIOS | SIT | PER_SKU_RATE | NEAR_FLAT_WITH_DIP | MAIN_TABLE_DERIVED | - |  |
| ITE | FVT | PER_SKU_RATE | NEAR_FLAT_WITH_DIP | MAIN_TABLE_DERIVED | - |  |
| ITE | SIT | PER_SKU_RATE | NEAR_FLAT_WITH_DIP | MAIN_TABLE_DERIVED | - |  |
| NV | FVT | PER_SKU_RATE | CONSTANT | MAIN_TABLE_DERIVED | - |  |
| NV | SIT | PER_SKU_RATE | CONSTANT | MAIN_TABLE_DERIVED | - |  |
| INTEL | FVT | PER_SKU_RATE | CONSTANT | MAIN_TABLE_DERIVED | - |  |
| INTEL | SIT | PER_SKU_RATE | CONSTANT | MAIN_TABLE_DERIVED | - |  |
| MFG | FVT | PER_SKU_RATE | NEAR_FLAT_WITH_DIP | MAIN_TABLE_DERIVED | - |  |
| MFG | SIT | PER_SKU_RATE | NEAR_FLAT_WITH_DIP | MAIN_TABLE_DERIVED | - |  |

## Adopted absolute values (what the engine reads)

Adopted source is shown so every number carries its provenance and interim state.

| Function | Phase | Model | Adopted from | SKU2 | SKU3 | SKU4 | SKU5 | SKU6 | Competing |
|---|---|---|---|---|---|---|---|---|---|
| HW | FVT | PER_SKU_RATE | MAIN_TABLE | 12 | 12.9 | 14 | 15 | 16.2 | - |
| HW | SIT | PER_SKU_RATE | MAIN_TABLE | 12 | 12.9 | 14 | 15 | 16.2 | - |
| ME | FVT | PER_SKU_RATE | MAIN_TABLE | 1 | 0.9 | 1 | 1 | 1.2 | - |
| ME | SIT | PER_SKU_RATE | MAIN_TABLE | 1 | 0.9 | 1 | 1 | 1.2 | - |
| THM | FVT | PER_SKU_RATE | MAIN_TABLE | 7 | 6.9 | 7.2 | 7 | 7.2 | - |
| THM | SIT | PER_SKU_RATE | MAIN_TABLE | 7 | 6.9 | 7.2 | 7 | 7.2 | - |
| Audio | FVT | PER_SKU_RATE | MAIN_TABLE | 4 | 3 | 4 | 4 | 3.6 | - |
| Audio | SIT | PER_SKU_RATE | MAIN_TABLE | 4 | 3 | 4 | 4 | 3.6 | - |
| RF Test | FVT | PER_SKU_RATE | MAIN_TABLE | 5 | 5.1 | 5.2 | 5 | 4.8 | - |
| RF Test | SIT | PER_SKU_RATE | MAIN_TABLE | 5 | 5.1 | 5.2 | 5 | 4.8 | - |
| EMC Test | FVT | PER_SKU_RATE | MAIN_TABLE | 6 | 6 | 6 | 6 | 6 | - |
| EMC Test | SIT | PER_SKU_RATE | MAIN_TABLE | 6 | 6 | 6 | 6 | 6 | - |
| SED | FVT | PER_SKU_RATE | MAIN_TABLE | 4 | 5.1 | 6 | 7 | 7.8 | - |
| SED | SIT | PER_SKU_RATE | MAIN_TABLE | 4 | 5.1 | 6 | 7 | 7.8 | - |
| SS | FVT | PER_SKU_RATE | MAIN_TABLE | 18 | 21 | 22 | 25 | 26.4 | - |
| SS | SIT | PER_SKU_RATE | MAIN_TABLE | 18 | 21 | 22 | 25 | 26.4 | - |
| PD | FVT | PER_SKU_RATE | MAIN_TABLE | 1 | 0.9 | 1 | 1 | 1.2 | - |
| PD | SIT | PER_SKU_RATE | MAIN_TABLE | 1 | 0.9 | 1 | 1 | 1.2 | - |
| SWPA | FVT | PER_SKU_RATE | MAIN_TABLE | 56 | 72 | 80 | 90 | 102 | - |
| SWPA | SIT | PER_SKU_RATE | MAIN_TABLE | 56 | 72 | 80 | 90 | 102 | - |
| MEPA | FVT | PER_PHASE_FIXED | SECONDARY_ABSOLUTE_TABLE | 36 | 36 | 36 | 36 | 36 | MAIN_TABLE |
| MEPA | SIT | PER_PHASE_FIXED | SECONDARY_ABSOLUTE_TABLE | 36 | 36 | 36 | 36 | 36 | MAIN_TABLE |
| HW PA | FVT | PER_PHASE_FIXED | SECONDARY_ABSOLUTE_TABLE | 2 | 3 | 4 | 4 | 4 | MAIN_TABLE |
| HW PA | SIT | PER_PHASE_FIXED | SECONDARY_ABSOLUTE_TABLE | 2 | 3 | 4 | 4 | 4 | MAIN_TABLE |
| EMC | FVT | UNRESOLVED | NONE_UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | MAIN_TABLE,SECONDARY_TABLE |
| EMC | SIT | UNRESOLVED | NONE_UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | MAIN_TABLE,SECONDARY_TABLE |
| Green | FVT | UNRESOLVED | NONE_UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | MAIN_TABLE,SECONDARY_TABLE |
| Green | SIT | UNRESOLVED | NONE_UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | MAIN_TABLE,SECONDARY_TABLE |
| Safety | FVT | UNRESOLVED | NONE_UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | MAIN_TABLE,SECONDARY_TABLE |
| Safety | SIT | UNRESOLVED | NONE_UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | MAIN_TABLE,SECONDARY_TABLE |
| RF Certification | FVT | UNRESOLVED | NONE_UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | MAIN_TABLE,SECONDARY_TABLE |
| RF Certification | SIT | UNRESOLVED | NONE_UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | MAIN_TABLE,SECONDARY_TABLE,J33_FORMULA |
| BIOS | FVT | PER_SKU_RATE | MAIN_TABLE | 1 | 0.9 | 1 | 1 | 1.2 | - |
| BIOS | SIT | PER_SKU_RATE | MAIN_TABLE | 1 | 0.9 | 1 | 1 | 1.2 | - |
| ITE | FVT | PER_SKU_RATE | MAIN_TABLE | 1 | 0.9 | 1 | 1 | 1.2 | - |
| ITE | SIT | PER_SKU_RATE | MAIN_TABLE | 1 | 0.9 | 1 | 1 | 1.2 | - |
| NV | FVT | PER_SKU_RATE | MAIN_TABLE | 6 | 6 | 6 | 6 | 6 | - |
| NV | SIT | PER_SKU_RATE | MAIN_TABLE | 6 | 6 | 6 | 6 | 6 | - |
| INTEL | FVT | PER_SKU_RATE | MAIN_TABLE | 6 | 6 | 6 | 6 | 6 | - |
| INTEL | SIT | PER_SKU_RATE | MAIN_TABLE | 6 | 6 | 6 | 6 | 6 | - |
| MFG | FVT | PER_SKU_RATE | MAIN_TABLE | 1 | 0.9 | 1 | 1 | 1.2 | - |
| MFG | SIT | PER_SKU_RATE | MAIN_TABLE | 1 | 0.9 | 1 | 1 | 1.2 | - |

## Contested cells - competing evidence kept apart

| Function | Phase | SKU | Main Table | Secondary Table | Delta |
|---|---|---|---|---|---|
| MEPA | FVT | SKU2 | 32 | 36 | +4 |
| MEPA | SIT | SKU2 | 32 | 36 | +4 |
| Green | SIT | SKU3 | 9 | 6 | -3 |
| RF Certification | SIT | SKU2 | 15 | 8 | -7 |
| RF Certification | SIT | SKU3 | 15 | 9 | -6 |
| RF Certification | SIT | SKU4 | 15 | 10 | -5 |
| RF Certification | SIT | SKU5 | 15 | 10 | -5 |
| RF Certification | SIT | SKU6 | 15 | 10 | -5 |

## Model questions raised (not promoted on shape alone)

| Function | Phase | Candidate models | Issue |
|---|---|---|---|
| EMC Test | FVT | PER_SKU_RATE, PER_PHASE_FIXED | derived total is constant across SKU2-6, but there is no independent evidence that the allocation is fixed per phase |
| EMC Test | SIT | PER_SKU_RATE, PER_PHASE_FIXED | derived total is constant across SKU2-6, but there is no independent evidence that the allocation is fixed per phase |
| NV | FVT | PER_SKU_RATE, PER_PHASE_FIXED | derived total is constant across SKU2-6, but there is no independent evidence that the allocation is fixed per phase |
| NV | SIT | PER_SKU_RATE, PER_PHASE_FIXED | derived total is constant across SKU2-6, but there is no independent evidence that the allocation is fixed per phase |
| INTEL | FVT | PER_SKU_RATE, PER_PHASE_FIXED | derived total is constant across SKU2-6, but there is no independent evidence that the allocation is fixed per phase |
| INTEL | SIT | PER_SKU_RATE, PER_PHASE_FIXED | derived total is constant across SKU2-6, but there is no independent evidence that the allocation is fixed per phase |

## DEC-06 baseline-embedded sharing signal

| Function | signal | FVT spread | FVT growth | SIT spread | SIT growth | reuse policy |
|---|---|---|---|---|---|---|
| Audio | SUSPECTED | 1 | -0.4 | 1 | -0.4 | BLOCK_UNLESS_PROVEN |
| BIOS | SUSPECTED | 0.3 | +0.2 | 0.3 | +0.2 | BLOCK_UNLESS_PROVEN |
| EMC | SUSPECTED | 0 | +0 | 4 | +4 | BLOCK_UNLESS_PROVEN |
| EMC Test | SUSPECTED | 0 | +0 | 0 | +0 | BLOCK_UNLESS_PROVEN |
| Green | SUSPECTED | 0 | +0 | 3 | +0 | BLOCK_UNLESS_PROVEN |
| INTEL | SUSPECTED | 0 | +0 | 0 | +0 | BLOCK_UNLESS_PROVEN |
| ITE | SUSPECTED | 0.3 | +0.2 | 0.3 | +0.2 | BLOCK_UNLESS_PROVEN |
| ME | SUSPECTED | 0.3 | +0.2 | 0.3 | +0.2 | BLOCK_UNLESS_PROVEN |
| MFG | SUSPECTED | 0.3 | +0.2 | 0.3 | +0.2 | BLOCK_UNLESS_PROVEN |
| NV | SUSPECTED | 0 | +0 | 0 | +0 | BLOCK_UNLESS_PROVEN |
| PD | SUSPECTED | 0.3 | +0.2 | 0.3 | +0.2 | BLOCK_UNLESS_PROVEN |
| RF Certification | SUSPECTED | 0 | +0 | 0 | +0 | BLOCK_UNLESS_PROVEN |
| RF Test | SUSPECTED | 0.4 | -0.2 | 0.4 | -0.2 | BLOCK_UNLESS_PROVEN |
| Safety | SUSPECTED | 1 | -0.4 | 0 | +0 | BLOCK_UNLESS_PROVEN |
| THM | SUSPECTED | 0.3 | +0.2 | 0.3 | +0.2 | BLOCK_UNLESS_PROVEN |

> SUSPECTED = the baseline total does not grow when SKU count grows, so sharing or a scale effect is very likely already inside the number. Under DEC-06 a further manual reuse claim on these Functions is blocked unless the user proves it is not already in the baseline.
