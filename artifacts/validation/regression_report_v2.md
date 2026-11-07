# Phase 2 regression report - manual-input calculation core

| item | value |
|---|---|
| core | `prototype/rules_v2.py` |
| quantity model | `QMODEL-CS-ODM-002` v2.0-draft |
| baseline | `BASELINE-CS-ODM-001` (DRAFT_UNCONFIRMED_BY_OWNER) |
| status | **REGRESSION** |

## Expected PASS / FAIL list

| ID | Invariant | Expected | Actual | Verdict |
|---|---|---|---|---|
| RT-01 | workbook grand totals still reproduce from the derived cells | PASS | PASS | as expected |
| QM-01 | MEPA and HW PA are PER_PHASE_FIXED candidates, not pseudo rates | PASS | PASS | as expected |
| QM-02 | the engine performs no divide-by-SKU-then-multiply-back anywhere | PASS | PASS | as expected |
| QM-03 | MEPA absolute is 36.0 at every SKU (Main Table said 32.0 at SKU2) | PASS | PASS | as expected |
| QM-04 | HW PA absolute at 6 SKU is 4.0, the pseudo-rate 4.2 is kept as evidence | PASS | PASS | as expected |
| QM-05 | a flat derived total is NOT promoted to PER_PHASE_FIXED on shape alone | PASS | PASS | as expected |
| QM-06 | every demand line states which Quantity Model produced it | PASS | PASS | as expected |
| QM-07 | the adopted value always carries its provenance | PASS | PASS | as expected |
| QM-08 | PER_PROJECT_FIXED and FORMULA_DRIVEN are supported by the contract | PASS | PASS | as expected |
| CT-01 | all 8 Certification cells stay UNRESOLVED and OWNER_REVIEW_REQUIRED | PASS | PASS | as expected |
| CT-02 | nothing is auto-selected: the whole demand is priced once per model | PASS | PASS | as expected |
| CT-03 | the competing models produce a band, never a merged or averaged number | PASS | PASS | as expected |
| CT-04 | J33 formula is kept as evidence but marked not evaluable | PASS | PASS | as expected |
| CT-05 | manual Certification override is accepted and labelled USER_MANUAL_OVERRIDE | PASS | PASS | as expected |
| CT-06 | FVT / SIT split is a table lookup, never a global ratio | PASS | PASS | as expected |
| CT-07 | certification cells where both models agree are still reported UNRESOLVED | PASS | PASS | as expected |
| CT-08 | disagreement between the models raises Owner Review Items automatically | PASS | PASS | as expected |
| PL-01 | Panel is matched as Panel Spec Count taken from the SKU Definition rows | PASS | PASS | as expected |
| PL-02 | D2:H2 'N*panel' comments are retained as evidence but excluded from calculation | PASS | PASS | as expected |
| PL-03 | Panel Spec Count stays an independent input dimension (not deleted) | PASS | PASS | as expected |
| PL-04 | proof by counter-example: panel=1 still yields 3 SKU, which the E2 comment forbids | PASS | PASS | as expected |
| SR-01 | 4 SKU and 5 SKU co-match returns a RANGE, not a forced single SKU | PASS | PASS | as expected |
| SR-02 | recommended_sku is null and preferred_sku is NOT_ESTABLISHED on a range | PASS | PASS | as expected |
| SR-03 | a RANGE prices every candidate SKU - 4 SKU and 5 SKU are both calculated | PASS | PASS | as expected |
| SR-04 | the priced candidate list is never padded beyond the tie set | PASS | PASS | as expected |
| SR-05 | a genuine SINGLE is still returned where the evidence separates the tiers | PASS | PASS | as expected |
| SR-06 | partial evidence never produces a fake SINGLE | PASS | PASS | as expected |
| SR-07 | empty input -> UNDETERMINED, nothing recommended, nothing priced | PASS | PASS | as expected |
| SR-08 | out-of-domain input is refused and routed to ORI-13, never extrapolated | PASS | PASS | as expected |
| SR-09 | every SKU definition is reachable as a unique recommendation | FAIL | FAIL | EXPECTED FAIL (open design gap) |
| SR-10 | no weighting trick is used to break a tie (weights unchanged since phase 1) | PASS | PASS | as expected |
| WV-01 | explicit LATER_WAVE specs are excluded from CURRENT_WAVE only | PASS | PASS | as expected |
| WV-02 | CURRENT_WAVE and FULL_PROJECT can recommend different SKU counts | PASS | PASS | as expected |
| WV-03 | wave assignment never changes the base rates | PASS | PASS | as expected |
| WV-04 | wave assignment only changes the spec counts - it is not a deduction factor | PASS | PASS | as expected |
| WV-05 | the existence of a second spec is never treated as a second wave | PASS | PASS | as expected |
| WV-06 | an explicitly UNKNOWN wave yields a range of scenarios plus an Owner Review Item | PASS | PASS | as expected |
| WV-07 | wave source is recorded per spec: user-tagged, implicit single, or not provided | PASS | PASS | as expected |
| WV-07b | NOT_PROVIDED factors are raised as an Owner Review Item, not resolved silently | PASS | PASS | as expected |
| WV-08 | FULL_PROJECT never silently drops a spec because a wave was declared | PASS | PASS | as expected |
| WV-09 | when no factor has a LATER_WAVE spec, CURRENT_WAVE is flagged identical to FULL_PROJECT | PASS | PASS | as expected |
| WV-10 | a declared second wave does change the SKU answer, so the wave is load-bearing | PASS | PASS | as expected |
| WV-11 | wave_basis distinguishes 'nobody declared' from 'declared' from 'unknown' | PASS | PASS | as expected |
| RS-01 | ALREADY_EMBEDDED_IN_BASELINE is never deducted (double-count guard) | PASS | PASS | as expected |
| RS-02 | ADDITIONAL_CONFIRMED_REUSE with proof is deducted once | PASS | PASS | as expected |
| RS-03 | ADDITIONAL_CONFIRMED_REUSE without proof is not deducted and raises an ORI | PASS | PASS | as expected |
| RS-04 | POTENTIAL_REUSE stays display only and never reduces demand | PASS | PASS | as expected |
| RS-05 | UNKNOWN_OVERLAP is never deducted when double deduction cannot be excluded | PASS | PASS | as expected |
| RS-06 | a mixed reuse ledger applies only the proven item and audits every decision | PASS | PASS | as expected |
| RS-07 | flat-total Functions are flagged so reuse needs extra proof | PASS | PASS | as expected |
| RS-08 | a PCBA reuse claim can never reduce unit demand | PASS | PASS | as expected |
| D01-01 | the 4 SKU Main Table total stays 443.8, never 444 | PASS | PASS | as expected |
| D01-02 | fractional risk reserve is kept to full precision | PASS | PASS | as expected |
| D01-03 | the engine reports rounding = NONE | PASS | PASS | as expected |
| D01-04 | comparison uses an explicit tolerance, business values stay untouched | PASS | PASS | as expected |
| D01-05 | PCBA extra demand is listed but never summed into unit totals | PASS | PASS | as expected |
| D01-06 | control: extra UNIT demand does enter the total | PASS | PASS | as expected |
| D01-07 | risk reserve is charged on baseline demand, never on user-added extra demand | PASS | PASS | as expected |
| PR-01 | no product series name is ever used as a judgement basis | PASS | PASS | as expected |
| PR-02 | every demand line carries rule_id, source file, sheet and row | PASS | PASS | as expected |
| PR-03 | missing key factors stay null and are listed as 请补充, never defaulted | PASS | PASS | as expected |
| PR-04 | user value overrides the file-read value while the file value is retained | PASS | PASS | as expected |
| PR-05 | an unedited factor keeps the file value as the effective value | PASS | PASS | as expected |
| SC-01 | engine output validates against schema/output.schema.json | PASS | FAIL | REGRESSION |
| SC-02 | a full manual-entry document validates against schema/input.schema.json | PASS | FAIL | REGRESSION |
| SC-03 | input schema refuses a text sentinel in place of a missing factor | PASS | PASS | as expected |
| SC-04 | input schema refuses an unknown reuse status | PASS | PASS | as expected |
| SC-05 | output schema refuses a single total while cells are UNRESOLVED | PASS | PASS | as expected |
| SC-06 | AnalysisInput.from_document() honours the input contract exactly | PASS | PASS | as expected |
| SC-07 | a declared LATER_WAVE spec reaches the wave engine through the contract | PASS | PASS | as expected |

## Probe notes

- **RT-01** - raw Main Table read - proves the extraction -> baseline -> quantity model chain is intact and nothing was hand-edited _({"SKU2": 365.0, "SKU3": 417.0, "SKU4": 443.8, "SKU5": 474.0, "SKU6": 507.0})_
- **QM-01** - evidence: absolute restatement rows 70/71 are constant across SKU2-6 for MEPA; rows 72/73 are integer-valued and disagree with rate x SKU for HW PA
- **QM-02** - rules_v2 reads adopted_absolute straight from the Quantity Model table _(no per_sku_rate / ttl_per_phase reference in rules_v2.py)_
- **QM-03** - the Main Table value is retained as competing evidence, not merged away _(adopted 36.0 / main 32.0 at SKU2)_
- **QM-04** - D-01: 4.2 is not rounded away, it is reported as the competing Main Table value
- **QM-05** - EMC Test / NV / INTEL stay PER_SKU_RATE and are raised as model questions (candidate_models both listed) instead of being silently re-modelled _(6 model questions)_
- **QM-08** - PER_PROJECT_FIXED currently has no member; FORMULA_DRIVEN appears only as the non-evaluable J33 candidate on RF Certification
- **CT-04** - required inputs (antenna source / WLAN card counts) are not MVP key factors - the formula is neither dropped nor silently substituted
- **CT-05** - the MVP keeps an entry point for hand-entered Certification quantities
- **CT-07** - agreement is surfaced as information; the model is not promoted to confirmed without the Owner
- **PL-02** - comment Panel counts (2/3/4/5/6) never appear as a definition range, so they cannot reach the matcher or the arithmetic. The same comments also conflict on CPU at 6 SKU (comment 3*CPU vs definition 4-5*CPU) and are also excluded _(comment panel = [2,3,4,5,6] vs definition [1-2] [1] [2] [2] [2-3])_
- **PL-04** - if the E2 comment (3*panel) were in the matching path, panel=1 could not be 3 SKU
- **SR-09** - UNRESOLVED DESIGN GAP -> ORI-04. The 5 SKU definition is a strict subset of the 4 SKU definition, so 5 SKU can never win alone and only ever appears as the range 4-5 SKU. Closing this needs real 4-SKU and 5-SKU project samples plus an official boundary rule from the Owner. This probe is EXPECTED TO FAIL and must not be weakened, deleted or turned green by re-weighting. _(SKU5 unique winners = 0 over 405 realistic combinations)_
- **SR-10** - ORI-08: these weights are agent-set, not Owner-confirmed. They rank candidates but DEC-01 forbids using them to manufacture a single answer.
- **WV-03** - the same SKU-3 column is read whether or not waves were declared
- **WV-04** - declaring a second wave changes which specs are counted, never the arithmetic. There is no per-wave percentage and no per-wave unit constant in the engine. _(same 4 SKU total 443.8 with or without waves)_
- **WV-05** - untagged second specs stay in the current wave by default and raise an ORI asking the Owner to confirm. The Agent does not guess a second wave and does not drop the SKU answer from 4 to 3 on its own.
- **WV-07** - cpu and gpu also have two specs here but nobody said which wave they belong to, so they are reported NOT_PROVIDED rather than being guessed
- **WV-09** - both scopes are still shown side by side, but the UI can say 'same as full project'
- **WV-11** - the UI needs this to explain why CURRENT_WAVE equals FULL_PROJECT: it is because nobody declared a second wave, not because a second wave was declared and cancelled
- **RS-08** - unit mismatch is an exclusion reason in its own right
- **SC-01** - policy: 'certification_model' is a required property; policy: 'certification_adopted_value_source' is a required property; policy: 'certification_main_table_role' is a required property; policy: 'certification_main_derived_added_to_total' is a required property
- **SC-02** - certification_input/mode: 'UNRESOLVED_SHOW_BAND' is not one of ['SYSTEM_APPENDIX_ADOPTED', 'USER_OVERRIDE_FOR_MISMAT; schema_version: '4.0' was expected
- **SC-03** - file_value is number|null, so 'N/A' / 'case by case' cannot be smuggled in; the UI must leave it null and show 请补充
- **SC-05** - the if/then rule in output.schema.json makes this a validation error, so a front end cannot quietly publish one number out of a band

## Summary

```json
{
 "generated_at_utc": "2026-11-04T09:23:43+00:00",
 "core": "prototype/rules_v2.py",
 "quantity_model": "QMODEL-CS-ODM-002",
 "baseline": "BASELINE-CS-ODM-001",
 "total": 70,
 "probes_holding": 67,
 "probes_failing": [
  "SR-09",
  "SC-01",
  "SC-02"
 ],
 "expected_failures": [
  "SR-09"
 ],
 "regressions": [
  "SC-01",
  "SC-02"
 ],
 "status": "REGRESSION"
}
```
