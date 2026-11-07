# Web MVP end-to-end test log

- generated: 2026-11-06T08:37:00+00:00
- driven headless from `tools/check_web_ui.py`; the pages run from `file://` with no server and no network

**98/98 checks pass - CLEAN**

| check | result | detail |
|---|---|---|
| UI-18 localStorage available | PASS |  |
| UI-18 history saved | PASS |  |
| UI-18 recent lists saved records | PASS | UIWAVE,UIOOD,UISINGLE,UITIE |
| UI-20 history copy creates a new independent record | PASS | UITIE（副本） |
| UI-18 history delete | PASS |  |
| UI-19 home lists recent analyses with project names | PASS |  |
| UI-19 home shows SKU result and demand | PASS |  |
| UI-02 range page says 4–5 SKU | PASS |  |
| UI-02 page states the range is not a gap and no candidate was chosen | PASS |  |
| UI-10 range reason is SKU_NOT_ESTABLISHED, not competing certification models | PASS |  |
| UI-04 result page shows both 4 SKU and 5 SKU priced | PASS |  |
| UI-08 certification states the adopted source and the once-only count | PASS |  |
| UI-09 the adopted value is counted once and the Main Table derivation zero times | PASS |  |
| UI-25 adopted Appendix values are visible without expanding anything | PASS | SKU|FVT|SIT|Certification|非 Certification|Reuse 采用|风险预留|合计|结果形态|Function|Phase|SKU|采用值（附表）|状态|SKU|FVT|SIT|Certification|非 Certification|Reuse 采用|风险预留|合计|结果形态|Function|Phase|SKU|采用值（附表）|状态|待确认事项|级别|条目|内部标识 |
| UI-26 Main Table value and delta are only in the expandable details | PASS | Function|Phase|Quantity Model|建议值|状态|主要原因|Function|Phase|SKU|采用值（附表）|主表 /SKU|主表 × SKU（审计）|差值|用户输入|来源行|Function|Phase|Quantity Model|建议值|状态|主要原因|Function|Phase|SKU|采用值（附表）|主表 /SKU|主表 × SKU（审计）|差值|用户输入|来源行 |
| UI-12 J33 shown as non-additive evidence | PASS |  |
| UI-21 open review items are collected and counted | PASS | open=5 |
| UI-22 review items do not block the result page | PASS |  |
| UI-16 no hidden single value: a range keeps both endpoints | PASS |  |
| UI-29 review CSV publishes adopted and audit columns with the counted-times flags | PASS | section 4 present |
| UI-30 JSON export keeps the adopted value, the audit value and the difference | PASS | cells=32 |
| UI-28 trial feedback export lists the mismatched cells and the open ORIs | PASS | ori rows=19 |
| UI-21 export payload keeps RANGE with null recommended sku | PASS |  |
| UI-01 single SKU page | PASS |  |
| UI-13 MEPA and HW PA shown as temporary | PASS |  |
| UI-06 with no LATER_WAVE the page says Current Wave equals Full Project | PASS |  |
| UI-06 both scopes are still shown side by side | PASS |  |
| UI-07 current wave differs from full project and the reason is explained | PASS |  |
| UI-15 wave does not change base_demand at the same SKU band | PASS |  |
| UI-24 out-of-domain stops the affected scenario with an explanation | PASS |  |
| UI-24 other scenario is still produced | PASS |  |
| UI-27 the user is never asked to choose between Main Table and Appendix | PASS | pickers=0 |
| UI-11a per-cell override stays analysis-only and is optional | PASS | override inputs=8 |
| UI-12b new page does not ask for a SKU count | PASS |  |
| UI-12c wave options are the three Chinese labels, not UNKNOWN | PASS |  |
| UI-02 live preview reports the 4-5 SKU range before running | PASS |  |
| UI-18 pressing 运行分析 saves the analysis and opens the result | PASS | nav=true storeBefore=4 storeAfter=5 href=result.html?id=AMW4Q0R6I err= |
| UI-02 run-through reproduces the range | PASS |  |
| UI-16 display precision never invents an integer | PASS | 438.8,438.8 |
| UI-17 JSON export carries full precision, not the display value | PASS |  |
| UI-17 export declares display precision does not modify values | PASS |  |
| UI-17 export refuses to collapse a range | PASS |  |
| UI-23 BLOCKS_FORMALIZATION items exist and the run still produced totals | PASS |  |
| UI-22 no item claims it blocks the manual MVP | PASS |  |
| UI-40 trial mode offers exactly the five issued controlled cases | PASS | 5 |
| UI-40 each case states on screen what it exists to prove | PASS |  |
| UI-41 the page takes its cases from the generated roster, not its own copy | PASS | RP-V4.0 7 |
| UI-41 C1-C5 together still cover 7/7 disagreeing cells | PASS | RF Certification / SIT @ SKU2,Green / SIT @ SKU3,RF Certification / SIT @ SKU3,RF Certification / SIT @ SKU4,RF Certification / SIT @ SKU5,RF Certification / SIT @ SKU6,Safety / FVT @ SKU6 |
| UI-42 the home page has a 参加团队试用 entry | PASS |  |
| UI-43 picking a case auto-fills the project name | PASS |  |
| UI-43 the case config is locked, not editable | PASS | no free input for key factors on the trial page |
| UI-43 C5's LATER_WAVE preset is shown, not left to the reviewer | PASS |  |
| UI-44 running the case produced a result on the same page | PASS |  |
| UI-44 C5 result really reaches 6 SKU and the Safety / FVT cell | PASS |  |
| UI-44 the feedback panel asks only about what this case produced | PASS | asked: @ SKU4,@ SKU4,@ SKU5,@ SKU5,@ SKU6,@ SKU6,@ SKU6,@ SKU6,@ SKU4,@ SKU5,@ SKU6,@ SKU6,@ SKU4,@ SKU5,@ SKU6,@ SKU6,@ SKU4,@ SKU5,@ SKU6,@ SKU6 |
| UI-44 C5 is not asked to answer all 19 Owner questions as mandatory | PASS | 11 required / 10 optional |
| UI-45 export is blocked before anything is filled | PASS |  |
| UI-45 name + date alone still does not unlock the export | PASS | 必答问题已全部作答（0/11） |
| UI-51 typing an answer everywhere else does not answer a v4.1 cell question | PASS | 本案例的必答问题已全部作答（7/11） | 仍未作答：RF Certification / SIT @ SKU4；RF Certification /  |
| UI-51 a value the dropdown does not offer is refused, never half-stored | PASS | NOT_A_TEXT_CONTROL value=[] |
| UI-51 choosing an option without writing the reason keeps the export locked | PASS | 本案例的必答问题已全部作答（11/11） | 缺理由：RF Certification / SIT @ SKU4；RF Certification / S |
| UI-45 every gate passes once the required answers are in | PASS | ✅试用者姓名已填写演练员✅评审日期已填写2026-11-05✅本案例已实际运行TRIAL-C5-SKU6-WAVE / AMW4Q0RFY✅规则包版本正确RP-V4.0（当前规则包 RP-V4.0，案例发卷时是 RP-V4.0）✅本案例的必答问题已全部作答（11/11）✅需要理由的问题都写了理由（4/4）✅案例目标差异格已实际跑到（4/4）RF Certification / SIT @ SKU4 |
| UI-46 one submission file, named as the collector expects | PASS | trial-submission-TRIAL-C5-SKU6-WAVE-20261106-1636.json |
| UI-46 submission carries case, project, reviewer and the rule pack it was run on | PASS | RP-V4.0 |
| UI-46 submission carries both the locked input and the full analysis | PASS |  |
| UI-46 submission names the cells this case covered and proves it exercised them | PASS | ["RF Certification / SIT @ SKU4","RF Certification / SIT @ SKU5","RF Certification / SIT @ SKU6","Safety / FVT @ SKU6"] |
| UI-46 every answer the page asked for is in the file, plus the optional ORIs | PASS | 11/10 checks=7 |
| UI-50 v4.1: every mismatch cell is a four-way choice with a mandatory reason | PASS | 4 cell question(s) |
| UI-50 the returned submission says which form version it answers | PASS | 4.1 |
| UI-50 the submission records the form version and the reason gate passed | PASS | 4.1 |
| UI-47 a stale rule pack fails the re-check even with everything else filled | PASS |  |
| UI-47 a case that never reached its target cells fails the re-check | PASS | 本次没有产出：RF Certification / SIT @ SKU4；RF Certification / SIT @ SKU5；RF Certification / SIT @ SKU6；Safety / FVT @ SKU6 |
| UI-47 a blank required answer is not treated as agreement | PASS |  |
| UI-47 a missing name or date blocks the submission | PASS |  |
| UI-47 a case that was never run cannot produce evidence | PASS |  |
| UI-48 a properly run case with its own cells passes all six checks | PASS | [] |
| UI-48 the locked config records that no override was used | PASS |  |
| UI-49 C1 loads and runs in one click, and asks about exactly its own cells | PASS | missing  | foreign  |
| UI-49 C1 can pass all six checks when its own case is run | PASS | [] |
| UI-49 C2 loads and runs in one click, and asks about exactly its own cells | PASS | missing  | foreign  |
| UI-49 C2 can pass all six checks when its own case is run | PASS | [] |
| UI-49 C3 loads and runs in one click, and asks about exactly its own cells | PASS | missing  | foreign  |
| UI-49 C3 can pass all six checks when its own case is run | PASS | [] |
| UI-49 C4 loads and runs in one click, and asks about exactly its own cells | PASS | missing  | foreign  |
| UI-49 C4 can pass all six checks when its own case is run | PASS | [] |
| UI-49 C5 loads and runs in one click, and asks about exactly its own cells | PASS | missing  | foreign  |
| UI-49 C5 can pass all six checks when its own case is run | PASS | [] |
| UI-51 the reason stays mandatory: emptying one locks the export and names it | PASS | 缺理由：RF Certification / SIT @ SKU4 |
| UI-54 C3, C4 and C5 each hand back one submission with all seven checks green | PASS | ["C3=trial-submission-TRIAL-C3-SKU4-20261106-1636.json checks7","C4=trial-submission-TRIAL-C4-RANGE45-20261106-1637.json checks7","C5=trial-submission-TRIAL-C5-SKU6-WAVE-20261106-1637.json checks7"] |
| UI-55 the draft a v4.1 review leaves behind says which form it was written on | PASS | {"v":"4.1","ran":true,"sent":true} |
| UI-56 a refresh restores the chosen option and its reason, not a blank form | PASS | 11/11 |
| UI-57 a v4.0 draft is never read as a v4.1 choice: the dropdown comes up empty | PASS | 4/4 blank | 仍未作答：RF Certification / SIT @ SKU4；RF Certif |
| UI-57 and the reason it left behind no longer satisfies the reason gate | PASS | 缺理由：RF Certification / SIT @ SKU4；RF Certification / S |
| UI-57 the reviewer is told, and the old wording is kept rather than dropped | PASS | {"needs":4,"kept":4} |
| UI-58 a case that does not exist is reported as missing, not as empty | PASS | byId(C9)=null |
| UI-58 an answer filed under a question this case never asked is not an answer | PASS | 本案例的必答问题已全部作答（0/11） | 缺理由：RF Certification / SIT @ SKU4；RF Certifi |
| UI-59 C5 states under its wave table that the wave is an assumption, not a fact | PASS | 波次为案例预设的试用假设，未经 Owner 确认；需求表没有波次列（ORI-03），本案不据此下业务结论 |
| UI-59 a case that presets no wave shows no wave table and no such warning | PASS | C3 case box mentions wave=false |

## Mapping to task section 25

| required coverage | check id |
|---|---|
| 1 单一 SKU 结果 | UI-01 |
| 2 4–5 SKU 范围 | UI-02 |
| 6 Current Wave 与 Full Project 一致 | UI-06 |
| 7 Current Wave 与 Full Project 不同 | UI-07 |
| 8 主表与附表验证通过 | UI-08 |
| 9 附表不重复计入 | UI-09 |
| 10 范围只由 SKU 范围产生 | UI-10 |
| 11 用户临时覆盖 | covered by W-11/W-23 in the parity harness |
| 12 J33 不重复叠加 | UI-12, UI-12b |
| 13 MEPA/HW PA 固定量 | UI-13 |
| 14/15 Reuse 扣减与未扣减 | covered by W-14/W-15/W-24 in the parity harness |
| 16 single_value=false 时单值字段为 null | UI-16 |
| 17 显示精度不改变底层值 | UI-17 |
| 18 历史分析保存 | UI-18 |
| 19 历史分析打开 | UI-19 |
| 20 历史分析复制 | UI-20 |
| 21 Review Register 收集新问题 | UI-21 |
| 22 Review Item 不阻断分析 | UI-22 |
| 23 BLOCKS_FORMALIZATION 不阻塞手工 MVP | UI-23 |
| 24 BLOCKS_EXECUTION 停止受影响计算并解释 | UI-24 |

## Mapping to the S1 in-browser trial mode (this round)

| required behaviour | check id |
|---|---|
| 首页有「参加团队试用」入口 | UI-42 |
| C1-C5 一键载入、配置锁定、覆盖目标可见 | UI-40, UI-41, UI-43 |
| 五个案例合起来仍覆盖 7/7 差异格 | UI-41 |
| 运行后查看结果 | UI-44 |
| 反馈只显示本案例涉及的问题（不要求 19 条 ORI） | UI-44 |
| 提交前校验：姓名 / 日期 / 已运行 / 规则包 / 必答 / 目标格 | UI-45, UI-47 |
| 单一 Submission JSON 字段齐全 | UI-46, UI-48 |
| 案例确实跑到了目标差异格 | UI-46 |
