# Regression report v4 - Certification adopted from the Appendix (DEC-10)

## Probe ledger (this is the arithmetic the previous report was missing)

| | count |
|---|---:|
| probes executed in the previous suite (`validate_rules_v3.py`) | 101 |
| carried forward unchanged | 83 |
| carried forward, adapted to DEC-10 | 16 |
| retired by DEC-10 (each with a named successor) | 2 |
| added in this task (DA / EX / ST) | 21 |
| **executed here** | **120** |

Previous suite = carried + adapted + retired; this suite = carried + adapted + added. Both equations hold: `True` and `True`.

Retired probes and their successors:

- **CT-V2-02** -> DA-01 + DA-02 + DA-03 (the Appendix is adopted, counted once, and the Main Table derivation is counted 0 times)
- **SC-05** -> DA-05 (the schema const-locks 1 adopted / 0 audit instead)

Probes adapted to the adopted source (same question, new column):

`RT-02`, `CT-V2-04`, `CT-V2-06`, `CT-V2-08`, `CT-V2-09`, `CT-V2-11`, `D01-01`, `D01-02`, `D01-04`, `PR-05b`, `SC-02`, `SC-06`, `SC-08`, `LG-02`, `LG-03`, `LG-04`

## Owner Review Items: unique questions vs impact tags (counted separately)

- unique Owner Review Items: **19**
- impact tags: **{"ADVISORY": 4, "AFFECTS_ACCURACY": 9, "BLOCKS_FORMALIZATION": 6}** (they sum to 19, i.e. one tag per question - an extra tag on an existing question is never a new ORI)

## Result

| item | value |
|---|---|
| core | `prototype/rules_v3.py` |
| engine | `rules_v3/4.0` |
| quantity model | `QMODEL-V4` 4.0 |
| baseline | `BASELINE-CS-ODM-001` (DRAFT_UNCONFIRMED_BY_OWNER) |
| certification per-cell verification | 33 verified / 7 mismatch / 0 not evaluable |
| owner decision | **DEC-10** - adopted from `APPENDIX_TABLE_TOTAL` |
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
| CT-V2-03 | CT-V2 | a single SKU produces a single Certification value, not a range | PASS | PASS | as expected |
| CT-V2-04 | CT-V2 | a 4-5 SKU range produces Certification values coming from 4 SKU and 5 SKU separately | PASS | PASS | as expected |
| CT-V2-05 | CT-V2 | a Certification range is caused by SKU_NOT_ESTABLISHED, never by competing models | PASS | PASS | as expected |
| CT-V2-06 | CT-V2 | FVT and SIT each read their own Appendix row, never a shared number | PASS | PASS | as expected |
| CT-V2-07 | CT-V2 | no global FVT/SIT ratio exists anywhere in the engine | PASS | PASS | as expected |
| CT-V2-08 | CT-V2 | J33 is never added on top of the adopted Appendix total | PASS | PASS | as expected |
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
| D01-01 | D01 | the 4 SKU total stays 438.8, never 439 (DEC-10 adopted value) | PASS | PASS | as expected |
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
| SC-06 | SC | AnalysisInput.from_document() honours the input contract exactly | PASS | PASS | as expected |
| SC-07 | SC | a declared LATER_WAVE spec reaches the wave engine through the contract | PASS | PASS | as expected |
| SC-08 | SC | an overridden Certification cell validates and keeps provenance | PASS | PASS | as expected |
| SC-09 | SC | output schema refuses a single_value result with a null total | PASS | PASS | as expected |
| SC-10 | SC | output schema refuses the Appendix being re-labelled as a quantity model | PASS | PASS | as expected |
| LG-01 | LG | the Phase 2 competing-Certification behaviour cannot return from rules_v3 | PASS | PASS | as expected |
| LG-02 | LG | QMODEL v4 carries no competing_candidates field and no UNRESOLVED cell | PASS | PASS | as expected |
| LG-03 | LG | no Quantity Model value may be the Appendix evidence role | PASS | PASS | as expected |
| LG-04 | LG | neither column may be added to the other, banded or used as a cap | PASS | PASS | as expected |
| DA-01 | DA | the adopted Certification value IS the Appendix total, cell by cell | PASS | PASS | as expected |
| DA-02 | DA | the adopted value is counted exactly once and is never added to the Main Table value | PASS | PASS | as expected |
| DA-03 | DA | the Main Table per-SKU value and its derived total are still on the record | PASS | PASS | as expected |
| DA-04 | DA | J33 is not added on top of the adopted value at any SKU band | PASS | PASS | as expected |
| DA-05 | DA | the output schema const-locks the adoption (1 adopted, 0 audit, no addition) | PASS | PASS | as expected |
| DA-06 | DA | FVT and SIT each adopt their own Appendix row (no global phase ratio) | PASS | PASS | as expected |
| DA-07 | DA | the 4-5 SKU range still prices both candidates, each with its own adopted total | PASS | PASS | as expected |
| DA-08 | DA | prohibited range reasons are still never emitted (engine and Web core) | PASS | PASS | as expected |
| DA-09 | DA | no Certification value is produced by dividing by the SKU count and multiplying back | PASS | PASS | as expected |
| DA-10 | DA | 6 SKU special review: the total is rebuilt from the bottom-up detail | PASS | PASS | as expected |
| DA-11 | DA | a manual override changes this Analysis only and never reaches the rule pack | PASS | PASS | as expected |
| DA-12 | DA | adoption does not silence the seven disagreements | PASS | PASS | as expected |
| EX-01 | EX | the JSON export carries adopted value, audit value and difference per cell | PASS | PASS | as expected |
| EX-02 | EX | the review CSV keeps the eight sections and states the counted times | PASS | PASS | as expected |
| EX-03 | EX | exports keep a range as a range and never publish a hidden single value | PASS | PASS | as expected |
| EX-04 | EX | underlying decimals survive the export path unchanged (D-01) | PASS | PASS | as expected |
| EX-05 | EX | the trial feedback export lists every disagreeing cell and every open ORI once | PASS | PASS | as expected |
| EX-06 | EX | the exported audit columns are the same numbers the engine published | PASS | PASS | as expected |
| ST-01 | ST | the probe ledger closes arithmetically (previous = carried + adapted + retired, current = carried + adapted + added) | PASS | PASS | as expected |
| ST-02 | ST | unique Owner Review Items and impact tags are counted separately and agree | PASS | PASS | as expected |
| ST-03 | ST | the project is described as a directory, not a Git working tree | PASS | PASS | as expected |
| EF-01 | EF | the Expected Failure set is exactly the approved ['SR-09'] | PASS | PASS | as expected |

## Probe notes

- **RT-01** - raw Main Table read - proves extraction -> baseline -> quantity model is intact and nothing was hand-edited _({"SKU2": 365.0, "SKU3": 417.0, "SKU4": 443.8, "SKU5": 474.0, "SKU6": 507.0})_
- **RT-02** - DEC-10: every total is built bottom-up from the adopted cells - the Appendix Certification totals plus everything else - and remains a single value. The difference from the workbook is now Certification adoption plus the MEPA / HW PA PER_PHASE_FIXED model (ORI-10). 6 SKU is reviewed separately (DA-10). _({"SKU2": 366.0, "SKU3": 408.0, "SKU4": 438.8, "SKU5": 469.0, "SKU6": 502.0})_
- **QM-02** - rules_v3 reads adopted_absolute straight out of the Quantity Model table _(no per_sku_rate / ttl_per_phase reference in rules_v3.py)_
- **QM-04** - D-01: 4.2 is not rounded away, it is reported as the competing Main Table value
- **QM-05** - EMC Test / NV / INTEL stay PER_SKU_RATE and are raised as model questions instead of being silently re-modelled (task section 18) _(6 model questions)_
- **QM-07** - task section 18: the front end must show 临时采用，待业务确认
- **QM-08** - no cell uses UNRESOLVED or FORMULA_DRIVEN any more; the enum stays so the contract does not narrow, and J33 is registered as BREAKDOWN_EVIDENCE instead
- **QM-09** - task section 18: the Appendix role is an evidence role, never a stackable Quantity Model _(evidence roles = ('PRIMARY_QUANTITY_MODEL', 'DERIVED_TOTAL_VALIDATION', 'BREAKDOWN_EVIDENCE', 'ABSOLUTE_RESTATEMENT', 'UNRESOLVED_COMMENT', 'DERIVED_MAIN_TABLE_AUDIT', 'ADOPTED_ABSOLUTE_TOTAL'))_
- **CT-V2-01** - each cell is checked on its own, never a Certification total alone; the seven cells that do not satisfy the relationship are reported as MISMATCH with their original values intact rather than corrected _(40 cells | verified 33 | mismatch 7 | not_evaluable 0)_
- **CT-V2-05** - the wording the UI must carry: the Certification rule is settled, the range exists only because the SKU band is not established between 4 and 5 SKU _(ORI kinds = ['CERTIFICATION_APPENDIX_VALIDATION_INCOMPLETE', 'CERTIFICATION_BREAKDOWN_EVIDENCE_NOT_GENERALIZED', 'CERTIFICATION_SOURCE_VALIDATION_MISMATCH', 'SKU_TIE_NOT_RESOLVABLE', 'WAVE_ASSIGNMENT_NOT_PROVIDED'])_
- **CT-V2-07** - the FVT share of the total moves with the SKU band, which is only possible if each row is read from its own cell _(FVT share at 2 SKU 0.4818 at 4 SKU 0.4818)_
- **CT-V2-08** - if the J33 reference totals (11 or 27) were added the 4 SKU Certification demand would no longer equal the sum of the adopted Appendix cells _(certification total 36 with J33 bracket 11..27 not added)_
- **CT-V2-09** - the two old labels appear in rules_v3.py only inside the DEC-09 docstring and the tuple that names them as prohibited; neither is ever emitted as an Owner Review Item kind _(certification ORI kinds = ['CERTIFICATION_APPENDIX_VALIDATION_INCOMPLETE', 'CERTIFICATION_BREAKDOWN_EVIDENCE_NOT_GENERALIZED', 'CERTIFICATION_SOURCE_VALIDATION_MISMATCH'])_
- **CT-V2-11** - the workbook is never edited to remove the difference; the mismatch is routed to the Owner Review Register (ORI-02 PARTIALLY_RESOLVED) _(3 function/phase pairs mismatch somewhere; 1 at 4 SKU -> 1 Register entries)_
- **CT-V2-12** - Safety FVT at 6 SKU keeps its Main Table decimal 9.6 in the audit column (D-01: not rounded to 10) while DEC-10 adopts the Appendix 10.0 as the applied value _(adopted 10.0 / audit 9.6)_
- **JG-02** - the MVP does not collect antenna / WLAN card counts; J33's declared combination stays a stated assumption recorded in the Register
- **JG-03** - both bounds are derived from wording inside J33 itself; the Appendix 8-10 lies below the floor of a 2-antenna/2-WLAN project, so it cannot be the same scenario _(bracket 11..27 | main 15 inside = True | appendix 8-10 below floor = True)_
- **PL-04** - if the E2 comment (3*panel) were in the matching path, panel=1 could not be 3 SKU
- **SR-09** - UNRESOLVED DESIGN GAP -> ORI-04. The 5 SKU definition is a strict subset of the 4 SKU definition, so 5 SKU can never win alone and only ever appears as the range 4-5 SKU. Closing this needs real 4-SKU and 5-SKU project samples plus an official boundary rule from the Owner. This probe is EXPECTED TO FAIL and must not be weakened, deleted or turned green by re-weighting. _(SKU5 unique winners = 0 over 405 realistic combinations)_
- **SR-10** - ORI-08: these weights are agent-set, not Owner-confirmed. They rank candidates but DEC-01 forbids using them to manufacture a single answer.
- **WV-03** - the same SKU-3 column is read whether or not waves were declared
- **WV-04** - there is no per-wave percentage and no per-wave unit constant in the engine _(same 4 SKU total 438.8 either way)_
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
- **SC-09** - a front end cannot publish 'single value' and leave the number out, which is how a hidden default would sneak back in
- **SC-10** - DERIVED_TOTAL_VALIDATION is an enum member of evidence_role only, never of quantity_model (task section 18)
- **LG-01** - the competing-model machinery is gone from the live core; UNRESOLVED remains supported as a Quantity Model but no Certification cell uses it _(forbidden phrases found = none)_
- **DA-01** - every Certification cell reads the Appendix total for that Function, Phase and SKU count; nothing is multiplied back from a rate _(F_EMC/FVT 0 | F_EMC/SIT 4 | F_GREEN/FVT 0 | F_GREEN/SIT 6 | F_SAFETY/FVT 10 | F_SAFETY/SIT 6 | F_RF_CERTIFICATION/FVT 0 | F_RF_CERTIFICATION/SIT 10)_
- **DA-02** - the old double count (adopted Appendix plus Main x SKU) is what this guard prevents; the project total is non-Certification + Certification, once _(4 SKU total 438.8 = non-cert 402.8 + cert 36; main derived sum would have been 41)_
- **DA-03** - audit evidence is retained at row level (per-SKU quantity, derived total, delta, source rows) so any difference can still be traced back to the workbook _(main derived at 4 SKU 41 vs adopted 36)_
- **DA-04** - adding the J33 bracket (11..27) would move the 4 SKU Certification demand away from the adopted Appendix total of 36 _(adopted cert by SKU: 2:32, 3:33, 4:36, 5:37, 6:38)_
- **DA-05** - replaces SC-05: the structural prohibition moved from 'the Appendix may not be counted' to 'the adopted value is counted once and the Main Table derivation is counted zero times' _(schema consts verified)_
- **DA-06** - the numbers adopted for FVT are the Appendix FVT rows (rows 53/55/57/59) and for SIT the Appendix SIT rows (54/56/58/60) - never a share of the project total _(FVT [10.0, 9.0, 10.0, 10.0, 10.0] | SIT [22.0, 24.0, 26.0, 27.0, 28.0])_
- **DA-07** - DEC-01 is unchanged by DEC-10: the range comes from the SKU answer, each candidate is priced in full, and neither endpoint is collapsed into a hidden single value _(4 SKU cert 36 / 5 SKU cert 37)_
- **DA-08** - the two labels exist only inside the docstring and the tuple that names them as prohibited; they are emitted by neither core _(prohibited = ['COMPETING_CERTIFICATION_MODELS', 'CERTIFICATION_MODEL_UNRESOLVED'])_
- **DA-09** - the adopted cell is an absolute read of the Appendix row; the Main Table per-SKU column is kept as the rule of record, not as a rate that is multiplied back in _(8 Certification cells adopt as ABSOLUTE Appendix reads)_
- **DA-10** - 6 SKU is the band where Safety FVT (adopted 10.0 against a Main derivation of 9.6) and RF SIT (adopted 10.0 against 15.0) both disagree, so it is recomputed from the rows rather than from any historical total (task section 5) _(6 SKU total 502.0 = rows 502.0; cert 38 (audit main 42.6))_
- **DA-11** - the override is stored in the Analysis snapshot with the adopted value beside it; the rule package bytes are unchanged before and after the overridden run _(rule pack sha unchanged: True)_
- **DA-12** - adopting the Appendix answers 'which number do we use'; it does not explain why the two columns differ, so ORI-02 stays PARTIALLY_RESOLVED and the rule pack stays DRAFT (task section 4: the rule pack must not be promoted) _(33 matching / 7 mismatch | 1 Register entries at 4 SKU)_
- **EX-02** - the adopted column comes first, the Main Table audit column second, and the counted-times pair makes the once-only rule visible in the spreadsheet
- **EX-03** - both endpoints stay in the file; a reviewer cannot mistake the export for a decision that was never made
- **EX-04** - the 4 SKU total is published as 438.8 and would have to stay 438.8 whatever the display precision says; 443.8 is the Phase 3a number and must not reappear _(438.8 kept, 443.8 gone)_
- **EX-05** - the reviewer is asked one question per open item - not one question per scenario and not one question per impact tag. At 3 SKU two cells disagree (Green/SIT and RF/SIT) and each is listed once. _(19 ORI rows)_
- **ST-01** - the previous report said '100' while 101 probes were executed and never reconciled the retired ones; the ledger below is computed from the executed probes, not typed _({"previous_suite": "tools/validate_rules_v3.py", "previous_total": 101, "retired_in_this_task": 2, "retired_ids": ["CT-V2-02", "SC-05"], "adapted_in_this_task": 16, "carried_unchanged": 83, "added_in_this_task": 21, "added_ids": ["DA-01", "DA-02", "DA-03", "DA-04", "DA-05", "DA-06", "DA-07", "DA-08", "DA-09", "DA-10", "DA-11", "DA-12", "EX-01", "EX-02", "EX-03", "EX-04", "EX-05", "EX-06", "ST-01",)_
- **ST-02** - an impact tag is a label on a question, not a second question: the tag counts sum back to the unique ORI count, and the Register and the rule pack list the same ids _(unique 19 | tags {'ADVISORY': 4, 'AFFECTS_ACCURACY': 9, 'BLOCKS_FORMALIZATION': 6} | register sections 19)_
- **ST-03** - this folder has never been under version control, so version-control vocabulary described nothing; the report tool was renamed to directory_integrity_report.py and the deliverable document uses Directory Integrity wording. The obsolete artefact names kept in the classifier (worktree_report.*) are file names being recognised, not vocabulary used in a report. _(banned words in the deliverable wording = none)_
- **EF-01** - an unexpected green SR-09 or a new Expected Failure is a regression (task sections 24 and 29) _(expected_fail = ['SR-09'])_

## Summary

```json
{
 "generated_at_utc": "2026-11-06T08:36:37+00:00",
 "core": "prototype/rules_v3.py",
 "engine": "rules_v3/4.0",
 "quantity_model": "QMODEL-V4",
 "baseline": "BASELINE-CS-ODM-001",
 "certification_verification": "33 verified / 7 mismatch / 0 not evaluable",
 "ori_02_status": "PARTIALLY_RESOLVED",
 "owner_decision": "DEC-10",
 "adopted_value_source": "APPENDIX_TABLE_TOTAL",
 "probe_ledger": {
  "previous_suite": "tools/validate_rules_v3.py",
  "previous_total": 101,
  "retired_in_this_task": 2,
  "retired_ids": [
   "CT-V2-02",
   "SC-05"
  ],
  "adapted_in_this_task": 16,
  "adapted_ids": [
   "RT-02",
   "CT-V2-04",
   "CT-V2-06",
   "CT-V2-08",
   "CT-V2-09",
   "CT-V2-11",
   "D01-01",
   "D01-02",
   "D01-04",
   "PR-05b",
   "SC-02",
   "SC-06",
   "SC-08",
   "LG-02",
   "LG-03",
   "LG-04"
  ],
  "carried_unchanged": 83,
  "added_in_this_task": 21,
  "added_ids": [
   "DA-01",
   "DA-02",
   "DA-03",
   "DA-04",
   "DA-05",
   "DA-06",
   "DA-07",
   "DA-08",
   "DA-09",
   "DA-10",
   "DA-11",
   "DA-12",
   "EX-01",
   "EX-02",
   "EX-03",
   "EX-04",
   "EX-05",
   "EX-06",
   "ST-01",
   "ST-02",
   "ST-03"
  ],
  "current_total": 120,
  "closure_previous": true,
  "closure_current": true,
  "unexpected_retirements": [],
  "undocumented_additions": []
 },
 "owner_review_item_count": 19,
 "owner_review_impact_tag_counts": {
  "ADVISORY": 4,
  "AFFECTS_ACCURACY": 9,
  "BLOCKS_FORMALIZATION": 6
 },
 "total": 120,
 "probes_holding": 119,
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
