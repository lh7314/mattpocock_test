# Regression report v3 - Certification corrected + manual-input MVP core

| item | value |
|---|---|
| core | `prototype/rules_v3.py` |
| engine | `rules_v3/3.0` |
| quantity model | `QMODEL-V3` 3.0 |
| baseline | `BASELINE-CS-ODM-001` (DRAFT_UNCONFIRMED_BY_OWNER) |
| certification per-cell verification | 33 verified / 7 mismatch / 0 not evaluable |
| ORI-02 | **PARTIALLY_RESOLVED** |
| status | **CLEAN** |

## Expected PASS / FAIL list

| ID | Group | Invariant | Expected | Actual | Verdict |
|---|---|---|---|---|---|
| RT-01 | RT | workbook grand totals still reproduce from the raw Main Table cells | PASS | PASS | as expected |
| RT-02 | RT | the corrected engine publishes ONE total per SKU band, not a band | PASS | PASS | as expected |
| QM-01 | QM | MEPA and HW PA are still PER_PHASE_FIXED candidates, not pseudo rates | PASS | PASS | as expected |
| QM-02 | QM | the engine performs no divide-by-SKU-then-multiply-back anywhere | PASS | PASS | as expected |
| QM-03 | QM | MEPA absolute stays 36.0 at every SKU (Main Table said 32.0 at SKU2) | PASS | PASS | as expected |
| QM-04 | QM | HW PA absolute at 6 SKU is 4.0, the pseudo-rate 4.2 is kept as evidence | PASS | PASS | as expected |
| QM-05 | QM | a flat derived total is still NOT promoted to PER_PHASE_FIXED on shape alone | PASS | PASS | as expected |
| QM-06 | QM | every demand line states which Quantity Model produced it | PASS | PASS | as expected |
| QM-07 | QM | MEPA / HW PA are surfaced as temporary models pending business confirmation | PASS | PASS | as expected |
| QM-08 | QM | PER_PROJECT_FIXED and FORMULA_DRIVEN are still supported by the contract | PASS | PASS | as expected |
| QM-09 | QM | DERIVED_TOTAL_VALIDATION exists but is NOT a Quantity Model | PASS | PASS | as expected |
| CT-V2-01 | CT-V2 | every Appendix Certification cell equals the Main Table per-SKU quantity times the SKU count, cell by cell | PASS | PASS | as expected |
| CT-V2-02 | CT-V2 | the Appendix is validation only and is not added to the total a second time | PASS | PASS | as expected |
| CT-V2-03 | CT-V2 | a single SKU produces a single Certification value, not a range | PASS | PASS | as expected |
| CT-V2-04 | CT-V2 | a 4-5 SKU range produces Certification values coming from 4 SKU and 5 SKU separately | PASS | PASS | as expected |
| CT-V2-05 | CT-V2 | a Certification range is caused by SKU_NOT_ESTABLISHED, never by competing models | PASS | PASS | as expected |
| CT-V2-06 | CT-V2 | FVT and SIT each use their own source rate, never a shared number | PASS | PASS | as expected |
| CT-V2-07 | CT-V2 | no global FVT/SIT ratio exists anywhere in the engine | PASS | PASS | as expected |
| CT-V2-08 | CT-V2 | J33 is never added on top of the Main Table result | PASS | PASS | as expected |
| CT-V2-09 | CT-V2 | a verified Certification cell raises no competing-model item | PASS | PASS | as expected |
| CT-V2-10 | CT-V2 | Certification is counted exactly once in the project total | PASS | PASS | as expected |
| CT-V2-11 | CT-V2 | any inconsistent Appendix cell raises SOURCE_VALIDATION_MISMATCH with the original values preserved | PASS | PASS | as expected |
| CT-V2-12 | CT-V2 | display precision never changes the underlying Certification result | PASS | PASS | as expected |
| JG-01 | JG | J33 is registered as breakdown evidence, not as a competing model | PASS | PASS | as expected |
| JG-02 | JG | J33 is not reproduced as an executable formula and does not force new inputs | PASS | PASS | as expected |
| JG-03 | JG | J33 is scoped to RF Certification and to its own declared source combination | PASS | PASS | as expected |
| JG-04 | JG | only the RF Certification cell carries breakdown evidence | PASS | PASS | as expected |
| JG-05 | JG | J33 raises an Advisory Register entry, never an execution blocker | PASS | PASS | as expected |
| PL-01 | PL | Panel is matched as Panel Spec Count taken from the SKU Definition rows | PASS | PASS | as expected |
| PL-02 | PL | D2:H2 'N*panel' comments are retained as evidence but excluded from calculation | PASS | PASS | as expected |
| PL-03 | PL | Panel Spec Count stays an independent input dimension (not deleted) | PASS | PASS | as expected |
| PL-04 | PL | proof by counter-example: panel=1 still yields 3 SKU, which the E2 comment forbids | PASS | PASS | as expected |
| PL-05 | PL | the excluded Panel annotation evidence travels with every exported result | PASS | PASS | as expected |
| SR-01 | SR | 4 SKU and 5 SKU co-match returns a RANGE, not a forced single SKU | PASS | PASS | as expected |
| SR-02 | SR | recommended_sku is null and preferred_sku is NOT_ESTABLISHED on a range | PASS | PASS | as expected |
| SR-03 | SR | a RANGE prices every candidate SKU - 4 SKU and 5 SKU are both calculated | PASS | PASS | as expected |
| SR-04 | SR | the priced candidate list is never padded beyond the tie set | PASS | PASS | as expected |
| SR-05 | SR | a genuine SINGLE is still returned where the evidence separates the tiers | PASS | PASS | as expected |
| SR-06 | SR | partial evidence never produces a fake SINGLE | PASS | PASS | as expected |
| SR-07 | SR | empty input -> UNDETERMINED, nothing recommended, nothing priced | PASS | PASS | as expected |
| SR-08 | SR | out-of-domain input is refused and routed to ORI-13, never extrapolated | PASS | PASS | as expected |
| SR-09 | SR | every SKU definition is reachable as a unique recommendation | FAIL | FAIL | EXPECTED FAIL (open design gap) |
| SR-10 | SR | no weighting trick is used to break a tie (weights unchanged since phase 1) | PASS | PASS | as expected |
| WV-01 | WV | explicit LATER_WAVE specs are excluded from CURRENT_WAVE only | PASS | PASS | as expected |
| WV-02 | WV | CURRENT_WAVE and FULL_PROJECT can recommend different SKU counts | PASS | PASS | as expected |
| WV-03 | WV | wave assignment never changes the base rates | PASS | PASS | as expected |
| WV-04 | WV | a declared wave is never a fixed quantity or a ratio deduction | PASS | PASS | as expected |
| WV-05 | WV | the existence of a second spec is never treated as a second wave | PASS | PASS | as expected |
| WV-06 | WV | an explicitly UNKNOWN wave yields a range of scenarios plus a Register entry | PASS | PASS | as expected |
| WV-07 | WV | wave source is recorded per spec: user-tagged, implicit single, not provided | PASS | PASS | as expected |
| WV-08 | WV | FULL_PROJECT never silently drops a spec because a wave was declared | PASS | PASS | as expected |
| WV-09 | WV | with no LATER_WAVE spec, CURRENT_WAVE is flagged identical to FULL_PROJECT | PASS | PASS | as expected |
| WV-10 | WV | a declared second wave does change the SKU answer, so the wave is load-bearing | PASS | PASS | as expected |
| WV-11 | WV | wave_basis distinguishes 'nobody declared' from 'declared' from 'unknown' | PASS | PASS | as expected |
| WV-12 | WV | the UI wording 未特别指定 maps to NO_EXPLICIT_ASSIGNMENT and never to UNKNOWN | PASS | PASS | as expected |
| WV-13 | WV | the excluded specs are named so the result page can explain the difference | PASS | PASS | as expected |
| RS-01 | RS | ALREADY_EMBEDDED_IN_BASELINE is never deducted (double-count guard) | PASS | PASS | as expected |
| RS-02 | RS | ADDITIONAL_CONFIRMED_REUSE with proof is deducted once | PASS | PASS | as expected |
| RS-03 | RS | ADDITIONAL_CONFIRMED_REUSE without proof is not deducted and raises an entry | PASS | PASS | as expected |
| RS-04 | RS | POTENTIAL_REUSE stays display only and never reduces demand | PASS | PASS | as expected |
| RS-05 | RS | UNKNOWN_OVERLAP is never deducted when double deduction cannot be excluded | PASS | PASS | as expected |
| RS-06 | RS | a mixed reuse ledger applies only the proven item and audits every decision | PASS | PASS | as expected |
| RS-07 | RS | flat-total Functions are flagged so reuse needs extra proof | PASS | PASS | as expected |
| RS-08 | RS | a PCBA reuse claim can never reduce unit demand | PASS | PASS | as expected |
| RS-09 | RS | the ledger states requested, adopted and rejected amounts separately | PASS | PASS | as expected |
| RS-10 | RS | a negative reuse quantity is rejected rather than used to inflate demand | PASS | PASS | as expected |
| D01-01 | D01 | the 4 SKU total stays 443.8, never 444 | PASS | PASS | as expected |
| D01-02 | D01 | fractional risk reserve is kept to full precision | PASS | PASS | as expected |
| D01-03 | D01 | the engine reports rounding = NONE | PASS | PASS | as expected |
| D01-04 | D01 | comparison uses an explicit tolerance, business values stay untouched | PASS | PASS | as expected |
| D01-05 | D01 | PCBA extra demand is listed but never summed into unit totals | PASS | PASS | as expected |
| D01-06 | D01 | control: extra UNIT demand does enter the total | PASS | PASS | as expected |
| D01-07 | D01 | risk reserve is charged on baseline demand, never on user-added extra demand | PASS | PASS | as expected |
| D01-08 | D01 | 65.49999999999999 style float tails are never written back as 65.5 | PASS | PASS | as expected |
| D01-09 | D01 | the export declares that display precision does not modify values | PASS | PASS | as expected |
| PR-01 | PR | no product series name is ever used as a judgement basis | PASS | PASS | as expected |
| PR-02 | PR | every demand line carries rule_id, source file, sheet and row | PASS | PASS | as expected |
| PR-03 | PR | missing key factors stay null and are listed as 请补充, never defaulted | PASS | PASS | as expected |
| PR-04 | PR | user value overrides the file-read value while the file value is retained | PASS | PASS | as expected |
| PR-05 | PR | an unedited factor keeps the file value as the effective value | PASS | PASS | as expected |
| PR-05b | PR | every exported Certification cell keeps system value, user value and source | PASS | PASS | as expected |
| OR-01 | OR | an Owner Review Item never blocks the whole analysis | PASS | PASS | as expected |
| OR-02 | OR | BLOCKS_FORMALIZATION items do not block the manual MVP | PASS | PASS | as expected |
| OR-03 | OR | a BLOCKS_EXECUTION condition stops the affected calculation with an explanation | PASS | PASS | as expected |
| OR-04 | OR | Register entries carry the fields the Register template requires | PASS | PASS | as expected |
| OR-05 | OR | the same question repeated across scenarios is folded into one entry | PASS | PASS | as expected |
| SC-01 | SC | engine output validates against schema/output.schema.json | PASS | PASS | as expected |
| SC-02 | SC | a full manual-entry document validates against schema/input.schema.json | PASS | PASS | as expected |
| SC-03 | SC | input schema refuses a text sentinel in place of a missing factor | PASS | PASS | as expected |
| SC-04 | SC | input schema refuses an unknown reuse status and an unknown wave | PASS | PASS | as expected |
| SC-05 | SC | output schema refuses an Appendix that is counted in the project total | PASS | PASS | as expected |
| SC-06 | SC | AnalysisInput.from_document() honours the input contract exactly | PASS | PASS | as expected |
| SC-07 | SC | a declared LATER_WAVE spec reaches the wave engine through the contract | PASS | PASS | as expected |
| SC-08 | SC | an overridden Certification cell validates and keeps provenance | PASS | PASS | as expected |
| SC-09 | SC | output schema refuses a single_value result with a null total | PASS | PASS | as expected |
| SC-10 | SC | output schema refuses the Appendix being re-labelled as a quantity model | PASS | PASS | as expected |
| LG-01 | LG | the Phase 2 competing-Certification behaviour cannot return from rules_v3 | PASS | PASS | as expected |
| LG-02 | LG | QMODEL v3 carries no competing_candidates field and no UNRESOLVED cell | PASS | PASS | as expected |
| LG-03 | LG | no Quantity Model value may be the Appendix evidence role | PASS | PASS | as expected |
| LG-04 | LG | the appendix may never be added, banded, overriding or treated as a cap | PASS | PASS | as expected |
| EF-01 | EF | the Expected Failure set is exactly the approved ['SR-09'] | PASS | PASS | as expected |

## Probe notes

- **RT-01** - raw Main Table read - proves extraction -> baseline -> quantity model is intact and nothing was hand-edited _({"SKU2": 365.0, "SKU3": 417.0, "SKU4": 443.8, "SKU5": 474.0, "SKU6": 507.0})_
- **RT-02** - Certification no longer drags every total into a band; the only remaining difference from the workbook is the MEPA / HW PA PER_PHASE_FIXED model (ORI-10) _({"SKU2": 373.0, "SKU3": 417.0, "SKU4": 443.8, "SKU5": 474.0, "SKU6": 506.6})_
- **QM-02** - rules_v3 reads adopted_absolute straight out of the Quantity Model table _(no per_sku_rate / ttl_per_phase reference in rules_v3.py)_
- **QM-04** - D-01: 4.2 is not rounded away, it is reported as the competing Main Table value
- **QM-05** - EMC Test / NV / INTEL stay PER_SKU_RATE and are raised as model questions instead of being silently re-modelled (task section 18) _(6 model questions)_
- **QM-07** - task section 18: the front end must show 临时采用，待业务确认
- **QM-08** - no cell uses UNRESOLVED or FORMULA_DRIVEN any more; the enum stays so the contract does not narrow, and J33 is registered as BREAKDOWN_EVIDENCE instead
- **QM-09** - task section 18: the Appendix role is an evidence role, never a stackable Quantity Model _(evidence roles = ('PRIMARY_QUANTITY_MODEL', 'DERIVED_TOTAL_VALIDATION', 'BREAKDOWN_EVIDENCE', 'ABSOLUTE_RESTATEMENT', 'UNRESOLVED_COMMENT'))_
- **CT-V2-01** - each cell is checked on its own, never a Certification total alone; the seven cells that do not satisfy the relationship are reported as MISMATCH with their original values intact rather than corrected _(40 cells | verified 33 | mismatch 7 | not_evaluable 0)_
- **CT-V2-02** - the project total contains Certification exactly once; the Appendix numbers exist only in the verification block _(total 443.8 = non-cert 402.8 + cert 41 (appendix sum 36 excluded))_
- **CT-V2-05** - the wording the UI must carry: the Certification rule is settled, the range exists only because the SKU band is not established between 4 and 5 SKU _(ORI kinds = ['CERTIFICATION_APPENDIX_VALIDATION_INCOMPLETE', 'CERTIFICATION_BREAKDOWN_EVIDENCE_NOT_GENERALIZED', 'CERTIFICATION_SOURCE_VALIDATION_MISMATCH', 'SKU_TIE_NOT_RESOLVABLE', 'WAVE_ASSIGNMENT_NOT_PROVIDED'])_
- **CT-V2-07** - the FVT share of the total moves with the SKU band, which is only possible if each row is read from its own cell _(FVT share at 2 SKU 0.4763 at 4 SKU 0.4763)_
- **CT-V2-08** - if the J33 reference totals (11 or 27) were added the 4 SKU Certification demand would no longer equal Main x SKU _(certification total 41 with J33 bracket 11..27 not added)_
- **CT-V2-09** - the two old labels appear in rules_v3.py only inside the DEC-09 docstring and the tuple that names them as prohibited; neither is ever emitted as an Owner Review Item kind _(certification ORI kinds = ['CERTIFICATION_APPENDIX_VALIDATION_INCOMPLETE', 'CERTIFICATION_BREAKDOWN_EVIDENCE_NOT_GENERALIZED', 'CERTIFICATION_SOURCE_VALIDATION_MISMATCH'])_
- **CT-V2-11** - the workbook is never edited to remove the difference; the mismatch is routed to the Owner Review Register (ORI-02 PARTIALLY_RESOLVED) _(3 function/phase pairs mismatch somewhere; 1 at 4 SKU -> 1 Register entries)_
- **CT-V2-12** - Safety FVT at 6 SKU is 1.6 x 6 = 9.599999999999999 in raw float; it is stored as the table value 1.6 x 6 and reported as 9.6 without being rounded into shape _(9.6)_
- **JG-02** - the MVP does not collect antenna / WLAN card counts; J33's declared combination stays a stated assumption recorded in the Register
- **JG-03** - both bounds are derived from wording inside J33 itself; the Appendix 8-10 lies below the floor of a 2-antenna/2-WLAN project, so it cannot be the same scenario _(bracket 11..27 | main 15 inside = True | appendix 8-10 below floor = True)_
- **PL-04** - if the E2 comment (3*panel) were in the matching path, panel=1 could not be 3 SKU
- **SR-09** - UNRESOLVED DESIGN GAP -> ORI-04. The 5 SKU definition is a strict subset of the 4 SKU definition, so 5 SKU can never win alone and only ever appears as the range 4-5 SKU. Closing this needs real 4-SKU and 5-SKU project samples plus an official boundary rule from the Owner. This probe is EXPECTED TO FAIL and must not be weakened, deleted or turned green by re-weighting. _(SKU5 unique winners = 0 over 405 realistic combinations)_
- **SR-10** - ORI-08: these weights are agent-set, not Owner-confirmed. They rank candidates but DEC-01 forbids using them to manufacture a single answer.
- **WV-03** - the same SKU-3 column is read whether or not waves were declared
- **WV-04** - there is no per-wave percentage and no per-wave unit constant in the engine _(same 4 SKU total 443.8 either way)_
- **WV-05** - untagged second specs stay in the current wave by default; the Agent does not guess a second wave
- **WV-11** - the UI needs this to explain why CURRENT_WAVE equals FULL_PROJECT
- **WV-12** - task section 12: 未特别指定 must not be shown or treated as UNKNOWN; it means 'counted in the current wave, nobody said otherwise'
- **RS-09** - task section 19 output contract
- **D01-08** - the workbook SUM/sku FVT at 3 SKU is 65.49999999999999. The engine may display 65.5 but stores and exports the untouched value (task section 20) _(3 SKU SUM/sku FVT = 196.5)_
- **PR-05b** - task section 13: a temporary user override must remain distinguishable from the system value and must not be promoted to a rule
- **OR-01** - task section 25 test 22: pages must still produce a result while ORI items are open
- **OR-02** - task section 25 test 23
- **OR-03** - task section 25 test 24
- **OR-05** - one question per (function, phase), not one per scenario x SKU
- **SC-03** - file_value is number|null, so 'N/A' cannot be smuggled in; the UI must leave it null and show 请补充
- **SC-05** - appendix_counted_in_project_total_times is const 0, so the schema itself forbids the double count that DEC-09 prohibits (task section 29)
- **SC-09** - a front end cannot publish 'single value' and leave the number out, which is how a hidden default would sneak back in
- **SC-10** - DERIVED_TOTAL_VALIDATION is an enum member of evidence_role only, never of quantity_model (task section 18)
- **LG-01** - the competing-model machinery is gone from the live core; UNRESOLVED remains supported as a Quantity Model but no Certification cell uses it _(forbidden phrases found = none)_
- **EF-01** - an unexpected green SR-09 or a new Expected Failure is a regression (task sections 24 and 29) _(expected_fail = ['SR-09'])_

## Summary

```json
{
 "generated_at_utc": "2026-11-04T08:02:29+00:00",
 "core": "prototype/rules_v3.py",
 "engine": "rules_v3/3.0",
 "quantity_model": "QMODEL-V3",
 "baseline": "BASELINE-CS-ODM-001",
 "certification_verification": "33 verified / 7 mismatch / 0 not evaluable",
 "ori_02_status": "PARTIALLY_RESOLVED",
 "total": 100,
 "probes_holding": 99,
 "probes_failing": [
  "SR-09"
 ],
 "expected_failures": [
  "SR-09"
 ],
 "approved_expected_failures": [
  "SR-09"
 ],
 "unapproved_expected_failures": [],
 "regressions": [],
 "status": "CLEAN"
}
```
