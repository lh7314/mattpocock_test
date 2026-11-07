# CHANGES

项目：`本文件所在目录` · 样机需求分析与推荐 Agent
原始证据：`original_documents\Sample_Requirement_SKU_and_Demand_Baseline_CleanSheet_20261030_V01_FORMAL.xlsx`
SHA-256 `48A360FF2FFD086E41D6B90A916F64FE52D9BC13EFBA07B8377B2945C846AB5A` —— 三个阶段均未改动（每次任务首尾各校验一次）。

仓库不是 Git 仓库，因此本文件是人工维护的变更账目。

---

# Phase 3b · TASK-GAMING-NRE-SAMPLE-REQUIREMENT-APPENDIX-ADOPTION-AND-TEAM-TRIAL-01

日期：2026-11-05 · 基线：Phase 3a（`QMODEL-V3` / `RP-V3.0` / 101 探针）
结果：**DEC-10 生效（Certification 采用附表总量）** · 120 探针（119 PASS + `SR-09` 按设计 FAIL）
· Python↔Web **40/40 一致（含三种导出文件）** · Web UI **44/44** · 完整性 **PASS（118 项检查）**
· Directory Integrity **CLEAN（来源不明 0）** · 原始文件 SHA-256 **未变**

## 1. 落实的决定（DEC-10）

```
Certification 采用值 = 附表中该 Function × Phase × SKU 档位的总量      计入总量 1 次
主表单 SKU 数量（quantity_model 仍为 PER_SKU_RATE）                    保留为规则记录
主表派生总量 = 主表单 SKU 数量 × SKU 数                                保留为审计，计入 0 次
两列永不叠加 · J33 仍是 BREAKDOWN_EVIDENCE（计入 0 次）· FVT / SIT 各读自己的附表行
范围仍只能来自 SKU 档位（SKU_NOT_ESTABLISHED）· 用户覆盖只作用于本次 Analysis
```

40 格逐格复核结果与 Phase 3a 相同：**33 VERIFIED / 7 MISMATCH / 0 NOT_EVALUABLE**
—— DEC-10 改变"用哪一列"，不改变"两列是否相等"，因此 **ORI-02 仍为 `PARTIALLY_RESOLVED`**。

## 2. 重算结果（自底向上加总，不做历史总量的人工加减）

| SKU | FVT | SIT | Certification（采用） | 非 Certification | **总量** | 工作簿 | Phase 3a | Δ vs 工作簿 | Δ vs Phase 3a |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 177.0 | 189.0 | 32.0 | 334.0 | **366.0** | 365.0 | 373.0 | +1.0 | −7.0 |
| 3 | 196.5 | 211.5 | 33.0 | 375.0 | **408.0** | 417.0 | 417.0 | −9.0 | −9.0 |
| 4 | 211.4 | 227.4 | 36.0 | 402.8 | **438.8** | 443.8 | 443.8 | −5.0 | −5.0 |
| 5 | 226.0 | 243.0 | 37.0 | 432.0 | **469.0** | 474.0 | 474.0 | −5.0 | −5.0 |
| 6 | 242.0 | 260.0 | 38.0 | 464.0 | **502.0** | 507.0 | 506.6 | −5.0 | −4.6 |

归因（残差 0）：**A. Certification 采用附表** −7 / −9 / −5 / −5 / −4.6；
**B. MEPA / HW PA 临时 `PER_PHASE_FIXED`（ORI-10，未变）** +8 / 0 / 0 / 0 / −0.4。
其余 39 个单元格数值完全未变（`438.8`、`196.5`、`9.6`、`65.49999999999999` 保持底层小数）。
4–5 SKU 范围行为不变：438.8 对 469.0（差 30.2 台），Certification 36.0 / 37.0。
**6 SKU 专项复核**：42 行加总 = 发布值 502.0；两处分歧（Safety/FVT 10.0 对 9.6、
RF/SIT 10.0 对 15.0）；−5.0 台 = 采用附表 −4.6 + MEPA/HW PA −0.4。

## 3. 新增文件

| 文件 | 作用 |
|---|---|
| `tools/build_quantity_model_v4.py` | 生成 `QMODEL-V4`：8 个 Certification 格改为采用附表值，主表值与派生值保留为 `DERIVED_MAIN_TABLE_AUDIT` |
| `tools/build_rule_pack_v4.py` | 生成 `RP-V4.0`（含 `owner_decision` / `certification_adoption` / 19 条唯一 ORI + 影响标签分开统计）与 `web/assets/rulepack.js` |
| `tools/validate_rules_v4.py` | 120 项探针 + **探针台账**（ST-01 算术闭合、ST-02 ORI 唯一数与影响标签分列、ST-03 术语） |
| `tools/export_model_delta_v4.py` | 三方总量对比与两项归因（残差为 0），含 6 SKU 专项复核区块 |
| `tools/directory_integrity_report.py` | 由 `worktree_report.py` 更名并按 Directory Integrity 口径重写 |
| `docs/36…41_*.md` | 采用值语义、DEC-10 记录、Register v4、总量与 6 SKU 复核、Web 改动、目录完整性 |
| `docs/00_owner_checklist_v4.md` | Owner 一次性确认清单（11 问，含金额与推荐选项） |

`artifacts/model/quantity_model_v4.{json,md}`、`rule_pack_v4.json`、
`artifacts/validation/regression_(results|report)_v4.*`、`directory_integrity_report.*` 为可复现产物。

## 4. 修改文件

| 文件 | 改动 |
|---|---|
| `prototype/rules_v3.py` | DEC-10 采用逻辑（`ADOPTED_SOURCE` / `AUDIT` 常量、`certification_cell_audit`、`demand_rows` 输出 `main_table_derived_total`、`certification_result` 输出采用/审计双列与计数、`serialise` 升至 4.0）＋**新增三个权威导出器** `export_json_document / export_review_csv / export_trial_feedback_csv` |
| `tools/verify_certification.py` | `owner_semantics` 改写为 DEC-10（采用 1 次、审计 0 次、禁止叠加），impact 字段更名；网格与状态判定不变 |
| `schema/input.schema.json` | 4.0：`mode = SYSTEM_APPENDIX_ADOPTED / USER_OVERRIDE_FOR_MISMATCH_CELLS`、`override_scope = THIS_ANALYSIS_ONLY`；并接受 Input Snapshot 的派生字段 |
| `schema/output.schema.json` | 4.0：`adopted_value_role`、`main_table_role`、`main_derived_counted_in_project_total_times = const 0`、`main_table_and_appendix_added_together = const false`、`recounted_from_detail` |
| `schema/rule.schema.json` | 新增 `ADOPTED_ABSOLUTE_TOTAL` / `DERIVED_MAIN_TABLE_AUDIT` 证据角色与 `certificationAdoption` 定义 |
| `web/assets/core.js` | 内核移植同步（`certCellAudit`、`main_table_audit`、采用/审计双列、`sum()` 改为与 CPython `sum()` 相同的 Neumaier 补偿求和） |
| `web/assets/store.js` | 三种导出与 Python 端逐字节对齐；新增试用反馈表；行状态改用 `main_table_audit` |
| `web/assets/app.js` | 默认只显示采用值（附表），主表值与差值移入 `<details>`；Certification 卡片重写；覆盖输入对所有 Certification 格开放并写明"只影响本次分析" |
| `web/index.html` / `new.html` / `result.html` | 文案改为"采用附表总量、只计一次；主表值仅审计"；结果页新增"导出试用反馈表"按钮 |
| `web/ui_test.html` | 新增 UI-25 / UI-26 / UI-27 / UI-11a / UI-28 / UI-29 / UI-30；UI-08 / UI-09 改断言采用值文案；UI-16 / UI-17 的十进制样例改为 438.8 |
| `tools/check_python_web_parity.py` | 用例 24 → **40**；每例额外比较 `json_document`、`review_csv`、`feedback_csv`；记录不一致格覆盖表 |
| `tools/verify_integrity.py` | 重写为 v4 闸门（118 项检查：DEC-10 采用/计数、Schema const、探针台账、归因残差、导出、术语、目录分类） |
| `tools/run_all.py` | 主管线改为 v4 步骤；历史套件增加逐条停用原因 |
| `tools/lint_sources.py` | 增加"生成报告禁用版本库术语"检查 |
| `docs/22…35` | 头部加状态横幅，指向本轮 v4 文档（正文原样保留） |
| `docs/README.md` | 索引重写，指向 v4 文档与新工具 |

## 5. 退役与更名

- `worktree_report.py`（已删除）→ `tools/directory_integrity_report.py`；产物改为
  `artifacts/validation/directory_integrity_report.{json,md}`，删除旧的
  `worktree_report.json/.md`（纯派生证据，新报告内容覆盖其全部信息）。
- 探针 **CT-V2-02**（"附表仅作验证、计入 0 次"）与 **SC-05**（"Schema 禁止附表计入总量"）
  被 DEC-10 取代 → 退役，接替者 `DA-01 / DA-02 / DA-03 / DA-05`；`CT-V2-04/06/08/09/11`、
  `D01-01/02/04`、`PR-05b`、`SC-02/06/08`、`LG-02/03/04`、`RT-02` 为**同一问题的适配**（共 16 项）。
- `artifacts/model/quantity_model_v3.json`、`rule_pack_v3.json` 原样保留为 Phase 3a 记录。

## 6. 修复的缺陷（本轮自发现、自修复）

| # | 症状 | 根因 | 修复 |
|---:|---|---|---|
| 1 | 探针台账 100 与 101 并存、退役探针无记录 | 报告先算 `total` 再追加 EF-01 | 台账改为**由实际执行结果计算**，并断言两条等式闭合（ST-01） |
| 2 | "ORI 数量"与"影响标签数"混用 | 旧汇总表只数行 | 规则包与探针分别输出唯一问题数与影响标签数，且标签合计=问题数（ST-02） |
| 3 | 报告使用 worktree / HEAD / branch 术语描述非版本库目录 | 沿用版本库口径 | 工具与报告改用 Directory Integrity（ST-03 + lint 检查） |
| 4 | CSV 中 FVT 出现 `196.50000000000003`（两端不一致） | JS 用 `+=` 累加，CPython `sum()` 用 Neumaier 补偿求和 | `core.js` 的 `sum()` 改为同一 Neumaier 算法 → 逐字节一致 |
| 5 | `input_snapshot.wave_assignment.declared_by` 两端不同 | 无 Spec 时 JS 返回 `[]`，Python 返回 `["NOT_PROVIDED"]` | JS 补 fallback |
| 6 | 试用反馈 CSV 出现 `recommended=None` | Python f-string 直接格式化 `None` | 统一走 `jsstr()` |
| 7 | `store.js` 一次改写中残留非法语句、`duplicate()` 被写坏 | 整文件重写时手误 | 复核并修正（`m[copy.id] = copy`），并由 UI/parity 探针确认 |
| 8 | 一致性用例里 `payload.certification_grid` 造成假差异 | 运行器把审计网格塞进 payload | 网格只放在 record 层，与 Python 侧一致 |
| 9 | 引擎名差异被当成缺陷 | Web 端口叫 `rules_v3_web` | 明确列入唯一声明差异（CSV 的 Engine 行按同一规则归一），其余逐字节比较 |
| 10 | `--history` 跑完后 `web/assets/rulepack.js` 与 `model_delta.json` 变回旧数字 | 被替代的**写入工具**与现行管线写同一批文件 | 三个旧写入工具加 `ALLOW_SUPERSEDED_WRITE` 保护并移出 history 清单；本轮已重新生成正确产物 |
| 11 | lint 报 `ui_test.html` 含可疑字面量反斜杠-n | JS 字符串里用了 `\r\n` | 改用 `\u000d\u000a` 转义，lint 恢复 CLEAN（行为不变，44/44 仍通过） |
| 12 | lint 报 CHANGES.md 存在悬空引用 | 报告工具改名后旧路径仍被引用 | 引用改为"旧文件（已删除）"写法，文档引用检查通过 |
| 13 | `validate_rules_v3.py` 以 KeyError 结束，旧报告未被覆盖 | 它断言的 `appendix_counted_in_project_total_times` 已被 DEC-10 取代 | 保留为 Phase 3a 记录（不修文件、不覆盖其报告），并在 `run_all.py --history` 中写明逐条原因 |

## 7. 本轮结束时的闸门结果

| 闸门 | 结果 |
|---|---|
| `validate_rules_v4.py` | 120 探针：119 持有 + `SR-09` 设计失败 · expected-fail 恰为 `['SR-09']` · **CLEAN** |
| `check_python_web_parity.py` | **40/40 MATCH**（含 JSON / Review CSV / 试用反馈 CSV） |
| `check_web_ui.py` | **44/44 CLEAN** |
| `verify_integrity.py` | **PASS（118 项检查）** |
| `directory_integrity_report.py` | **CLEAN**，来源不明文件 **0** |
| `original_documents` SHA-256 | 开始与结束一致：`48A360FF…AB5A`（1 个文件） |

## 8. 仍然打开的 Owner 问题

19 条唯一问题（6 条阻止规则包定稿、9 条影响准确度、4 条提示性），**0 条阻止手动 MVP**；
详见 `docs/38_owner_review_register_v4.md` 与一次性清单 `docs/00_owner_checklist_v4.md`。

---

# Phase 3 · TASK-GAMING-NRE-SAMPLE-REQUIREMENT-CERTIFICATION-CORRECTION-AND-WEB-MVP-01

日期：2026-11-05 · 基线：Phase 2（`QMODEL-V2` / `rules_v2` / 84 探针）
结果：**ORI-02 = `PARTIALLY_RESOLVED`** · 100 探针（99 PASS + `SR-09` 按设计 FAIL）·
Python↔Web 24/24 一致 · Web UI 37/37 · 完整性 **PASS（78 项检查）** · worktree **CLEAN**

## 1. 修正了什么

Certification 不再是"三套竞争模型 + 永远输出区间"，而是：

```
Certification Demand = 主表单 SKU 数量 × Applied SKU Count     （FVT / SIT 各读各的源行）
Project Certification Demand 计入总量 1 次；附表计入 0 次
附表 evidence_role = DERIVED_TOTAL_VALIDATION（证据角色，不是 Quantity Model）
J33  evidence_role = BREAKDOWN_EVIDENCE，disposition = DECLARED_NOT_GENERALIZED，additive = false
范围只能来自 SKU 档位本身 → reason = SKU_NOT_ESTABLISHED
```

逐格复验：**40 格 = 4 Function × 2 Phase × 5 SKU → 33 VERIFIED / 7 MISMATCH / 0 NOT_EVALUABLE**。
7 个不一致格保留原值与差值，进入 Register，未修改任何源数据。

| 格 | 主表 /SKU | 采用（主表×SKU） | 附表 | delta | 源行 |
|---|---:|---:|---:|---:|---|
| Green SIT @3SKU | 3.0 | 9.0 | 6.0 | −3.0 | 30 / 56 |
| Safety FVT @6SKU | 1.6 | 9.6 | 10.0 | +0.4 | 31 / 57 |
| RF SIT @2SKU | 7.5 | 15.0 | 8.0 | −7.0 | 34 / 60 |
| RF SIT @3SKU | 5.0 | 15.0 | 9.0 | −6.0 | 34 / 60 |
| RF SIT @4SKU | 3.75 | 15.0 | 10.0 | −5.0 | 34 / 60 |
| RF SIT @5SKU | 3.0 | 15.0 | 10.0 | −5.0 | 34 / 60 |
| RF SIT @6SKU | 2.5 | 15.0 | 10.0 | −5.0 | 34 / 60 |

修正后总量（单一值，不再区间）：

| SKU | Workbook | Phase 2 区间 | **修正后** | Certification | Δ vs Workbook |
|---:|---:|---:|---:|---:|---:|
| 2 | 365 | 366–373 | **373.0** | 39.0 | +8.0 |
| 3 | 417 | 408–417 | **417.0** | 42.0 | 0 |
| 4 | 443.8 | 438.8–443.8 | **443.8** | 41.0 | 0 |
| 5 | 474 | 469–474 | **474.0** | 42.0 | 0 |
| 6 | 507 | 502–506.6 | **506.6** | 42.6 | −0.4 |

**Certification 语义修正本身移动了 0 个数字**（Phase 2 的区间上界本就用主表算）；
剩下 +8.0 / −0.4 全部来自 Phase 2 的 MEPA / HW PA（4 格，ORI-10），本任务未触碰。

## 2. 新增文件

### 工具（`tools/`）
| 文件 | 作用 |
|---|---|
| `verify_certification.py` | 40 格逐格复验 + 附表自洽性检查 + 主表列形状分析 + J33 调查 → `certification_verification.{json,md}` |
| `build_quantity_model_v3.py` | 由 Phase 2 模型 + 逐格验证生成 **QMODEL-V3**（Certification 转 `PER_SKU_RATE`，其余逐字继承） |
| `build_rule_pack_v3.py` | 生成 **RP-V3.0** 规则包 + 浏览器形态 `web/assets/rulepack.js` |
| `export_model_delta_v3.py` | 五类归因的 model_delta（Certification / MEPA-HW PA / 未变 / SKU 范围 / 仅 Review） |
| `validate_rules_v3.py` | 100 探针回归套件（含强制的 `CT-V2-01..12`） |
| `check_python_web_parity.py` | Python↔Web 完整结构化输出比对（无头浏览器，禁用 DNS） |
| `check_web_ui.py` | 端到端 UI 探针运行器 |

### 内核与前端
| 文件 | 作用 |
|---|---|
| `prototype/rules_v3.py` | **正式计算内核**（DEC-09；保留 `UNRESOLVED` 支持但无 Certification 格使用） |
| `web/index.html` `web/new.html` `web/result.html` | 三页 MVP（首页 / 新建分析 / 分析结果） |
| `web/assets/core.js` | `rules_v3.py` 的等价移植（不含任何业务数字） |
| `web/assets/rulepack.js` | 生成的规则包（前端唯一数值来源） |
| `web/assets/store.js` | localStorage 历史 + JSON/CSV 导出 + 显示格式化 |
| `web/assets/app.js` `web/assets/app.css` | 页面渲染与样式（不含业务判断） |
| `web/assets/parity_runner.js` `web/parity.html` `web/ui_test.html` | 一致性与 UI 探针运行页 |

### 文档（`docs/`，交付物 A–W）
`22_certification_correction_v3.md`（A/B/C）· `23_quantity_model_and_rule_pack_v3.md`（D/E）·
`24_schema_v3.md`（F）· `25_owner_decision_log_v3.md`（G）· `26_owner_review_register_v3.md`（H）·
`27_owner_confirmation_checklist_v3.md`（I）· `28_totals_v3_and_change_attribution.md`（J/K/L）·
`29_web_mvp_run_guide.md`（M/N）· `30_ui_fields_and_copy_v3.md`（O）·
`31_python_web_parity_v3.md`（P）· `32_tests_v3.md`（Q）· `33_export_contract_v3.md`（R/S）·
`34_mvp_known_limits_v3.md`（T）· `35_next_stage_v3.md`（U）

## 3. 修改文件

| 文件 | 变更 |
|---|---|
| `schema/input.schema.json` | → **3.0**：`project_name` / `project_type` / `phase_scope` / `spec_labels`；`specWave.wave` 增加 `NO_EXPLICIT_ASSIGNMENT`；`certification_input.mode` 取消"显示竞争区间" |
| `schema/output.schema.json` | → **3.0**：新增 `$defs.certification`（`const` 锁死附表计入 0 次、Certification 计入 1 次、J33 不叠加、Phase 比例为 null）、`$defs.j33`、`reuse_summary`、`owner_review_summary`、`scenario.excluded_specs`；删除竞争模型相关定义 |
| `schema/rule.schema.json` | → v3：新增 `evidenceRole` / `certificationCellVerification` / `j33Investigation` / `ori_02Status`；`ownerReviewItem` 增加 `blocking_level` / `decision_status` |
| `tools/verify_integrity.py` | 重写为 Phase 3 门禁：9 段、78 项检查，新增 Certification 逐格复验、QMODEL-V3、规则包与 Schema、回归与 Expected Failure、model_delta 归因、Web 一致性与 UI、文件分类 |
| `docs/13_ori_status_v2.md` | 顶部加 Phase 3 指针（ORI-02 → `PARTIALLY_RESOLVED`，新增 5 项） |
| `docs/README.md` | 重写为三阶段索引 |
| `CHANGES.md` | 本文件 |

## 4. 保留但不作为门禁

- `validate_rules.py`（Phase 1，因 `SR-01` 版 ORI-04 探针按设计退出码 1）
- `validate_rules_v2.py`（Phase 2，其 Certification 组断言的行为已被 DEC-09 废止）
- `prototype/rules_v2.py`、`artifacts/model/quantity_model_v2.json`、`regression_report_v{1,2}.md`
- 每个 QMODEL-V3 的 Certification 格内含 `phase2_superseded{}`，记录旧解释与废止理由

## 5. 退役探针及接替（不是删除证据）

`CT-01 CT-02 CT-03 CT-04 CT-07 CT-08` 退役；`CT-05`、`CT-06` 保留并加强。
映射表见 `docs/25_owner_decision_log_v3.md §3`。
`verify_integrity.py §6` 反向断言 `CT-01/02/03/08` 确实已不在当前套件中。

## 6. Owner Review Register

**19 项**：Phase 1 沿用 12 + Phase 2 沿用 2 + **Phase 3 新增 5**
（`ORI-02a`、`ORI-02b`、`ORI-15`、`ORI-16`、`ORI-17`）。
`ORI-02` 状态由 `INTERIM_TREATMENT_ADOPTED` → **`PARTIALLY_RESOLVED`**。
`BLOCKS_EXECUTION` 0 项；**阻塞手工 MVP 0 项**。
一次性确认清单：`docs/27_owner_confirmation_checklist_v3.md`（11 题，可直接逐项回答）。

## 7. 任务过程中发现并修复的缺陷（自查，非需求变更）

| # | 缺陷 | 发现方式 | 严重度 |
|---|---|---|---|
| 1 | `store.js` 对象字面量收尾多一个分号 → 整文件语法错误，所有页面脚本失效 | 专用脚本加载探针抓到 `SyntaxError @ store.js:132` | 致命 |
| 2 | `new.html` 缺 `#add-reuse` / `#add-extra` → `bindNew()` 提前抛异常，「运行分析」按钮未绑定 | `UI-18` 报 `nav=false` | 严重 |
| 3 | Python/Web 规则包版本字段取值来源不同 | parity 比对 | 中 |
| 4 | SKU 评分字符串格式不同（`1.0` vs `1`） | parity 比对 | 低 |
| 5 | Reuse 账本 `DEDUCTED` 文案不同 | parity 比对 | 低 |
| 6 | JS 缺 `source_validation.relationship` 字段 | parity 比对 | 中（结构缺字段） |
| 7 | JS 在无覆盖时省略 `user_override_vs_appendix` 键（Python 输出 null） | parity 比对 | 中 |
| 8 | J33 findings 键名两侧不一致 | parity 比对 | 中 |
| 9 | `check_web_ui.py` 重复包装 stdout 导致打印崩溃 | 运行期崩溃 | 工具侧 |
| 10 | `export_model_delta_v3.py` 把 Phase 2 区间下界算错（`366-365`）——对"所有含附表值的格"替换，实际 Phase 2 只对 Certification 替换 | 输出自检 | 中 |
| 11 | UI 探针 `UI-21` 断言自身写错（字符串与布尔混比）、`UI-06` 是恒真表达式 | 修 UI-18 时复查 | 探针侧 |
| 12 | 无头浏览器 profile 落在含非 ASCII 的用户目录 → Edge 静默无输出；`--host-resolver-rules` 含空格被拆成 3 个参数 | 逐变量排查 | 工具侧 |
| 13 | `verify_certification.py` 的"旧行为审计"只搜标签字符串本身 → 把 `PROHIBITED_RANGE_REASONS` 这个**禁令元组**误报成"竞争模型回来了" | `run_all` 全序列输出里看到 `legacy ... : [{'file': 'rules_v3.py'...}]` | 中（会在交付物里写入虚假告警） |
| 14 | 用 PowerShell `-replace` 补丁时，替换串里的 `\n` 被当字面量写入 → `verify_integrity.py` 里出现 5 处真正的反斜杠-n，文件语法被破坏 | 文件预览看到 `continue\n if ...` | 致命（门禁跑不起来） |
| 15 | 同一批 PowerShell `Set-Content -Encoding UTF8` 给多个源文件加了 UTF-8 BOM | 编辑工具报首字符异常 | 低（Python/浏览器可容忍，但不干净） |
| 16 | 文档里 5 处交叉引用缺 `_v3` 后缀，指向不存在的文件 | 新增 `tools/lint_sources.py` 的引用检查 | 低（文档可达性） |
| 17 | `tools/__pycache__/*.pyc` 被文件分类器判为"来源不明" → worktree 结论 NOT CLEAN | `worktree_report.py` 自检 | 中（会误报交付不干净） |
| 18 | `export_model_delta_v3.py` 的 Phase 2 区间下界算法把"所有有附表值的格"都替换了，而 Phase 2 实际只对 Certification 替换 → 输出 `366-365` 这种下界大于上界的区间 | 输出自检 | 中 |

新增两个防守性工具，就是为了让 14/16/17 这类问题不再靠人眼发现：
`tools/lint_sources.py`（编译/解析/编码/文档引用）、`worktree_report.py`（已删除）（文件分类与结论）。

修复原则：**改探针时不动被测代码**（#11）；**改 JS 时向 Python 对齐**（#3–#8，Python 是行为基准）。

## 8. 三阶段结果对照

| | Phase 1 | Phase 2 | Phase 3 |
|---|---|---|---|
| 探针 | 70 | 84 | **100** |
| 状态 | CLEAN | CLEAN | **CLEAN** |
| Expected Failure | `SR-09` | `SR-09` | **`SR-09`** |
| Quantity Model | 单一 per-SKU 费率 | 五态，8 格 UNRESOLVED | **38 `PER_SKU_RATE` + 4 `PER_PHASE_FIXED`，0 UNRESOLVED** |
| Certification 输出 | 单值（费率口径未质疑） | 区间（三套竞争） | **单值 + 逐格验证状态** |
| 交付物 | A–P | A–L | **A–W** |
| 可运行产物 | 设计文档 + 原型 | 设计文档 + 内核原型 | **+ 可双击运行的三页 Web MVP** |
| 完整性 | PASS | PASS | **PASS（78 检查）** |
| 原始文件 SHA | 未变 | 未变 | **未变** |

---

# Phase 3b 补充 · S1 试用回收闭环（同一任务基线，DEC-10 之后）

日期：2026-11-05 · 触发：`docs/42` 的 **S1** 是当时唯一不依赖 Owner 回答就能推进的步骤
结果：新增 1 个回收工具（自带 45 项自检）+ 1 个回收目录 + 1 篇试用包
· 完整性检查 **118 → 125 项 PASS** · 流水线 **14 → 16 步** · `python tools\run_all.py` **ALL GREEN**
· Python↔Web 仍 **40/40** · Web UI 仍 **44/44** · 120 探针不变（`SR-09` 仍按设计 FAIL）
· Directory Integrity **CLEAN** · 原始文件 SHA-256 **未变**

## 新增

| 路径 | 作用 |
|---|---|
| `tools/collect_trial_feedback.py` | 读回试用者导出的反馈表，汇总 3 个差异格 + 19 条 Owner 问题的回答，产出四态结论；`--self-test` 跑 45 项解析/聚合断言（其中 6 项直接解析**内核真实导出的反馈表**，防止导出格式与解析器各自漂移），不写任何项目文件 |
| `feedback_inbox\README.md` | 回收目录说明：放什么文件、只增不改、非反馈表会被点名拒绝 |
| `docs/43_trial_pack_v4.md` | S1 试用包：跑几条、谁填什么、判定口径、报告四态怎么读、S2 定稿的五条证据要求 |
| `artifacts/validation/trial_feedback_report.json` / `.md` | 机器与人各一份的汇总报告（当前：回收 0 份，`TRIAL_NOT_STARTED`） |

## 修改

| 路径 | 改动 |
|---|---|
| `tools/run_all.py` | 流水线加入 `collect_trial_feedback --self-test` 与正式回收汇总两步（`run()` 现在支持 `("脚本", ["参数"])` 形式） |
| `tools/verify_integrity.py` | 新增 §9b（7 项）：汇总报告必须针对当前规则包、跟踪的 ORI 与差异格必须与规则包一致、四态结论合法，且**规则包若为 `CONFIRMED` 而试用结论不是 `READY_FOR_S2` 即失败**；文件分类新增 `INCOMING (team trial feedback)` 桶 |
| `tools/directory_integrity_report.py` | 归类新工具、新产物与 `docs/43`；`feedback_inbox\` 的说明文件算本轮交付物，进来的反馈表算外来证据 |
| `docs/README.md`、`docs/41`、`docs/42` | 索引加入试用包与新工具；分类表加入 INCOMING 桶；S1 行写明流程与一条命令；基线数字 118 → 125、14 → 16 步 |

## 设计约束（刻意不做的事）

- **不把沉默当同意**：空白 = `UNANSWERED`，含糊表述（"先这样吧"）= `OTHER`，都不计入"已回答"，
  但会在报告里逐字列出；`不同意` 必须先于 `同意` 匹配（否则 `不同意` 会被读成同意）。
- **不替 Owner 决定**：工具只统计谁在哪个项目上答了什么，不改规则包、不改源表。
- **不让旧规则包的反馈定稿**：`Rule pack` 与当前 `RP-V4.0` 不一致 → 标注为不作为定稿证据。
- **不新增 Expected Failure**，也不动任何业务数字：本轮 0 个内核改动、0 个数字变化。

## 本轮修复的缺陷（自查，非需求变更）

| # | 缺陷 | 发现方式 | 严重度 |
|---:|---|---|---|
| 19 | `verdict_of` 先匹配"同意"后匹配"不同意"、且 `是/对/y` 这类单字会误判 | 自检第 1 版就抓到 `不同意 → AGREE` | 高（会把反对读成赞成） |
| 20 | `canonical_keys()` 读 `certification_verification.json` 用了不存在的 `grid` 键（实为 `verification_grid`） | 自检运行即 `KeyError` | 致命（工具跑不起来） |
| 21 | `run_all.py` 的 `run()` 只接受脚本名字符串，无法把 `--self-test` 作为一步运行 | 加入流水线时 `TypeError` | 工具侧 |
| 22 | 补丁脚本以 `newline='\r\n'` 打开文件**又**预先把 `\n` 换成 `\r\n` → `run_all.py` 出现 116 处 `\r\r\n`，按行读取多出 116 个空行 | 结构复查（`def run` 看起来"已改"实际在另一个偏移处） | 致命（自己把工具文件写坏） |

第 22 条的教训已固化：写文件时**只由 `newline` 参数决定行尾**，不再手工预转换；
收尾用全字节扫描确认 `\r\r\n` 为 0，并复跑 `tools/lint_sources.py`（可编译 / 可解析 / 无乱码 / 引用不悬空）。

## 复验

```
python tools\collect_trial_feedback.py --self-test   # SELF-TEST: 45 checks | FAIL: none
python tools\run_all.py                              # 16 步全 OK，PIPELINE: ALL GREEN
```

---

# Phase 3b 补充 2 · S1 受控试用发卷 + 取证口径（同一任务基线，DEC-10 之后）

任务要求：**启动受控试用，不再扩功能**。本轮 0 个内核改动、0 个业务数字变化、
0 个新增 Web 功能；规则包仍是 `DRAFT_PENDING_OWNER`，`SR-09` 仍是唯一 Expected Failure。

## 为什么还要写代码

试用卡在一个具体的坑上：**7 个仍然不一致的格子长在特定 SKU 数上**。
`Green / SIT` 只在 3 SKU 出现，`Safety / FVT` 只在 6 SKU 出现。
让团队"随便跑 3–5 条真实项目"，很可能 7 格里只取证到 2 格，而报告只会说"3 组里回答了 1 组"，
看不出**为什么**没答上。所以补两件事：发卷（固定案例 + 空白表）与按 7 格展开的取证状态。

## 新增 / 修改

| 文件 | 变化 |
|---|---|
| `tools/issue_trial_forms.py`（新） | S1 发卷：5 条案例的 Key Factor 全部取自 CleanSheet 自己的 SKU 定义（C79:C83），预期结果由 `prototype/rules_v3.py` 实算；生成 `trial_kit\roster.json`、`ROSTER.md`、`forms\*.csv`。**已存在的表一律不覆盖**（填过的表是证据），`--check` 只查漂移不写文件 |
| `trial_kit\`（新目录） | 案例清单 + 5 份空白反馈表。刻意不放 `feedback_inbox\`，避免空白表被当成回收件计入 |
| `tools/collect_trial_feedback.py` | ① `--report-dir`：演练写到别处，正式证据不被覆盖；② 解析随附分析 JSON，得到"实际跑到过哪些 SKU 数"；③ 与 `trial_kit\roster.json` 关联（按 Project 名），逐案例标 `RETURNED / NOT_RETURNED / STALE_RULE_PACK / UNATTRIBUTED`；④ 7 个底层格子逐格出证状态；⑤ 报告新增回收一览、案例清单、7 格状态、无效件、冲突、未覆盖六节。自检 45 → **60** 项 |
| `tools/verify_integrity.py` | 新增 §9c（9 项）：发卷必须针对当前规则包、必须能覆盖全部 7 格、项目名唯一、空白表存在且不在回收目录、报告案例数与发卷一致；文件分类新增 `TRIAL KIT` 桶。闸门 125 → **134** 项 |
| `tools/directory_integrity_report.py` | 归类 `issue_trial_forms.py`、`trial_kit\`（清单算本轮交付物，空白表标注"填写并放回才算证据"）、`docs/44` |
| `docs/43_trial_pack_v4.md` | 新增 §0 发卷与"SKU 数 → 差异格"对照表；回收三条规矩（只新增、不在 `trial_kit` 就地填、演练用 `--report-dir`）；报告读法补齐六节；B4 补实测结论 |
| `docs/44_owner_confirmation_one_shot_v4.md`（新） | Owner 一次性确认清单：A 组 7 格（3 条 ORI）/ B 组 4–5 分界 / C 组 MEPA-HW PA / D 组 14 条，**19 条 ORI 与 11 问全覆盖且不重叠**，末尾是签名与写回顺序 |
| `docs/README.md`、`docs/41`、`docs/42` | 索引与基线数字（134 项、60/60、TRIAL KIT 桶、S0 改为按 `docs/44` 一轮答完） |

## 本轮量到的事实（写进文档，不改规则）

- 5 条案例合计覆盖 **7/7** 差异格；缺 C2 就拿不到 `Green / SIT`，缺 C5 就拿不到 `Safety / FVT`；
- 反馈表第 2 段按 `Function / Phase` 去重（只有 3 行），一行代表不了 7 格——
  所以取证状态在**汇总侧**按 7 格展开，导出契约一个字节都没动；
- 案例配置同时落在 4 SKU 与 5 SKU 定义里（C81 与 C82 的交集），这就是 `RANGE 4–5` 与 `SR-09`
  的可复现实物，试用者看到的正是 Owner 自己那张表造成的分界问题；
- B4 实测：只有把具体 Spec 明确标为「后续波次」，Current Wave 才与 Full Project 分开
  （`SINGLE 6 / 502.0` vs `RANGE 4–6`）；只要有 Factor 没标完，仍登记 `WAVE_ASSIGNMENT_NOT_PROVIDED`。

## 刻意不做的事

不改 `original_documents\`、不改规则包状态、不改 Certification 采用来源、
不改 4–5 SKU 范围逻辑、不动 `SR-09`、不改任何业务数字；
不新增团队管理 / 权限 / 审批 / 自学习 / Web 功能；
**案例覆盖与 7 格状态只如实上报，不改变四态结论的门槛**（没有悄悄加严，也没有放松）；
试用过程中不逐条问 Owner，问题统一并入 `docs/44`。

## 本轮修复的缺陷（自查，非需求变更）

| # | 缺陷 | 发现方式 | 严重度 |
|---:|---|---|---|
| 23 | 新增自检写到已关闭的临时目录 → `FileNotFoundError` | 自检运行即崩 | 致命（工具跑不起来） |
| 24 | `cell_level_coverage` 里 `if not known` 分支是死代码（该分支下 `projects` 必为空） | 复查状态机时发现的不可达分支 | 中（状态含义会被误读）→ 改为显式 `ANSWERED_NO_JSON` |
| 25 | 发卷漂移比较用 `read_text()`，通用换行转换会把 CRLF 文件读成 LF → 永远"不一致" | 逻辑自查 | 中（会把没改过的表报成被篡改）→ 新增 `raw()` 以 `newline` 为空的方式读取 |
| 26 | `issue(force, check_only)` 被按 `issue(a.check, a.force)` 位置传参 → `--check` 实际以 `--force` 运行，**会覆盖空白表** | 第一次跑 `--check` 就打印出 "issued 5 blank form(s)" | 高（违背"填过的表不被覆盖"）→ 参数改为 keyword-only，调用处显式命名 |
| 27 | 发卷写文件用 `utf-8-sig`，而内核导出的文本本身已带 BOM → 文件出现**双 BOM**，漂移检查把 5 份没动过的表全报成被改过 | `--check` 对全新发卷返回 `CHECK: DRIFT` | 高（告警全假，等于没有告警）→ 改为 `utf-8` 写入并重新发卷，复验 `CHECK: OK` |

第 26、27 条各暴露同一类风险：**"看起来在工作"的检查其实没有检查**。
因此补了两条可执行验证——篡改一份发卷表后 `--check` 必须只点名那一份且返回码为 1，
还原后必须回到 `CHECK: OK` 且字节完全一致；演练用 `--report-dir` 写到临时目录，
正式报告始终保持 `TRIAL_NOT_STARTED`。

## 复验

```
python tools\issue_trial_forms.py                    # 5 条案例，覆盖 7/7 差异格
python tools\issue_trial_forms.py --check            # CHECK: OK
python tools\collect_trial_feedback.py --self-test   # SELF-TEST: 60 checks | FAIL: none
python tools\collect_trial_feedback.py               # VERDICT: TRIAL_NOT_STARTED
python tools\run_all.py                              # 16 步全 OK，PIPELINE: ALL GREEN
```

端到端演练（发卷 → 模拟填写 → 回收，全部在临时目录）：案例关联正确、
取证格数 2/7、缺失案例点名 C1/C3/C4/C5、结论 `EVIDENCE_INCOMPLETE`，
正式报告保持 `TRIAL_NOT_STARTED` 未被污染。

---

# Phase 3b 补充 3 · S1 试用改为「网页内置试用模式」（同一任务基线，DEC-10 之后）

## 为什么改

上一轮把卷发出去了，但试用者要做的动作仍然很重：抄项目名、手输五个 Key Factor、
C5 还要自己把 cpu5 / panel3 标成后续波次，然后在 Excel 里对五个区块逐行填，
**其中包含与本人案例无关的 19 条 Owner 问题**，最后交回两个文件。
两处会直接毁掉证据：配置输错 → 案例没跑到目标差异格（白跑）；
表太长 → 后半段整片留空，而留空在回收端只等于"没回答"。
本轮把这些压成：选案例 → 跑 → 答本案例涉及的问题 → 导出**一个** Submission JSON。

**本轮没有新增业务功能**：没有账号 / 团队 / 权限 / 审批 / 自学习，
没有改 Certification 采用口径、4–5 SKU 范围、SR-09、规则包状态与任何业务数字。

## 新增 / 修改

| 文件 | 动作 | 说明 |
|---|---|---|
| `tools/issue_trial_forms.py` | 修改 | 每案例计算**问题范围**（必答 = 本案例真的跑到的差异格 / 真的登记的待确认项 / Panel≥2 / 两条通例）；生成 `web/assets/trialkit.js`（去掉时间戳以便 `--check` 判漂移）；打印必答 / 可选分布 |
| `web/assets/trial.js` | 新增 | 试用模式纯逻辑：锁定输入 → `NRE` 跑分析 → 六道提交前校验 → 构造 Submission JSON。可被 `ui_test.html` 直接调用，页面与测试用同一份代码 |
| `web/trial.html` | 新增 | 选案例 / 锁定输入展示 / 结果 / 只列本案例问题 / 可选题折叠区 / 提交前检查表 / 一键导出 |
| `web/index.html`、`web/assets/app.js`、`web/assets/app.css` | 修改 | 首页「参加团队试用」入口与规则包徽标；`app.js` 导出 `AppViews`，试用页复用同一套结果渲染（不再抄第二份表格代码） |
| `tools/collect_trial_feedback.py` | 修改 | 优先读 `trial-submission-*.json`；同项目旧 CSV 记为 `superseded_legacy_files`（登记不重复计入）；回收端**独立复检**六道门禁（不采信页面自检）；7 格状态新增"谁在这一格上答了什么"；缺日期与缺姓名同样 `UNATTRIBUTED` |
| `tools/verify_integrity.py` | 修改 | 新增 §9d（18 类断言）：页面案例列表 == 发卷台账、案例锁定、每案例只问它跑得到的格、必答 ≠ 19、必答 ∪ 可选 == 19、六道门禁 ID 两端都在、旧格式仍被读取、`START_HERE` 与投递说明存在且与台账一致 |
| `tools/check_web_ui.py`、`web/ui_test.html` | 修改 | 新增 `UI-40…UI-49` 驱动真实 `trial.html`（headless、`file://`、断网）：一键载入、配置锁定、只问本案例问题、门禁拦截、提交件字段 |
| `tools/run_all.py` | 修改 | `issue_trial_forms.py` 纳入固定顺序（`trialkit.js` 与 `roster.json` 不会再各跑各的） |
| `tools/directory_integrity_report.py` | 修改 | 新文件归类：`trial_kit/START_HERE.md`、`feedback_inbox/DROP_FILES_HERE.txt`、`web/trial.html`、`web/assets/trial{kit,}.js`；docs 范围延到 45 |
| `trial_kit/START_HERE.md` | 新增 | 团队上手页：30 秒流程、五条案例的理由、每人必答条数、六道门禁、故障排查 |
| `feedback_inbox/DROP_FILES_HERE.txt` | 新增 | 投递说明：放什么、规矩、回收端采信规则 |
| `docs/45_trial_web_mode_v4.md` | 新增 | 设计说明 + 前后对比 + Submission 字段契约 + 门禁两端表 + **本轮新缺口 ORI-18/19/20** |
| `docs/43`、`docs/42`、`docs/41`、`docs/README`、`feedback_inbox/README.md` | 修改 | 试用通道改为 2A（网页）/2B（备用）、基线数字、目录分类、提交件优先与不采信自检 |

## 本轮量到的事实

- 案例覆盖不变：**C1–C5 覆盖 7/7 差异格**（`--check` 与 §9d 双重确认）。
- 必答条数：C1 6 / C2 7 / C3 7 / C4 9 / C5 11；必答覆盖 ORI **10/19**，
  其余 9 条为每页底部的可选项 → 整轮 19/19 可达，但**没有任何人被要求答 19 条**。
- 自检 / 闸门：`collect_trial_feedback --self-test` **60 → 95**；
  `check_web_ui` **44 → 81**；`verify_integrity` **134 → 181**；`run_all` 16 → 17 步全绿。
- 提交件端到端：C2 + C5 两份完整提交件即可让判决走到 `READY_FOR_S2`
  （3 组差异全答 + 19 条 ORI 全答 + 6/7 格取证）；再加 C1 → **7/7**。
  这条是自检测试，写在临时目录里，**没有**写进 `feedback_inbox\`。
- 正式 `feedback_inbox\` 仍然一份提交都没有 → 判决保持 `TRIAL_NOT_STARTED`。

## 刻意不做的事

- 不把"案例是否回收"塞进 `READY_FOR_S2` 阈值（只增加报告维度）。
- 不新增判决状态，不降低任何一条证据口径；缺日期反而**新判**为 `UNATTRIBUTED`。
- 不做提交件签名 / 身份核验（任务范围排除账号体系），因此署名仍是自报，见缺口 ORI-18/20。
- 不删除旧通道：`trial_kit\forms\*.csv` 与 CSV+JSON 回收路径继续可用、继续被自检覆盖。

## 本轮修复的缺陷（自查，非需求变更）

| # | 缺陷 | 怎么发现的 | 严重度 → 处置 |
|---|---|---|---|
| 28 | `trial.js` 的 `gates()` 用 `String(answers[id] \|\| "")` 判断必答题，而答案实际是 `{answer, comment}` 对象 → **任何空白都被判成已作答**，六道门禁里最关键的一道在页面上形同虚设 | 新增端到端检查 `UI-45`：一条没答却显示"必答问题已全部作答（11/11）" | 高（正是"空白不算同意"这条硬规则）→ 按对象取 `answer` 字段，复验 0/11 → 11/11 才放行 |
| 29 | 新加的 UI 检查沿用 `UI-25…UI-30`，与既有探针编号冲突 → 证据日志里同一编号两种含义 | 汇总 `web_ui_results.json` 的 id 列表时看到重号 | 中（证据可读性）→ 试用模式整体改为 `UI-40…UI-49` |
| 30 | §9d 首版在 `trial.html` 里找"案例配置不可修改"文案，但该文案由 `trial.js` 渲染 → 闸门假失败 | 首跑 `RESULT: FAIL` | 中（闸门自身可信度）→ 断言改为读真正写文案的那一侧 |
| 31 | 回收端门禁前缀写成 `TARGET_CELL`，与页面 ID `TARGET_CELLS_EXERCISED` 不一致 → §9d"两端同 ID"断言失败 | §9d 自己抓到 | 低（字面漂移，正是该闸门存在的理由）→ 两端统一用同一组 ID 常量 |

## 对 real-data 结论的影响

**无。** 采用值仍为 `366.0 / 408.0 / 438.8 / 469.0 / 502.0`，
`SR-09` 仍是唯一 Expected Failure（regression 119/120 保持），
规则包仍 `RP-V4.0 / DRAFT_PENDING_OWNER`，`original_documents\` SHA-256 复验一致。
本轮只改变**证据怎么收**，没有改变**任何数字怎么算**。

## 新增待决事项（并入 `docs/44_owner_confirmation_one_shot_v4.md`，不逐条打断试用）

- **ORI-18**：案例配置锁定后，试用不再覆盖"真人自己输 Key Factor / 自己判波次"这一段；
  建议让 1–2 位试用者在受控案例之外用自己的真实项目再跑一次（走 2B 通道）。
- **ORI-19**：反馈被裁剪到本案例相关问题，"还想要什么功能 / 哪里不顺手"只剩 Comment；
  是否需要恢复一个结构化的"新增需求"栏。
- **ORI-20**：19/19 的闭合依赖可选题被回答；若无人答，
  ORI-02a / 05 / 06 / 09 / 11 / 12 / 13 / 14 / 17 只能由 Owner 在一次性清单里直接定，
  S2 的"证据齐备"定义需要 Owner 明确接受这一点。

## 复验

```
python tools\issue_trial_forms.py                          :: 5 案例 / 7 格 / 必答 10 可选 9
python tools\issue_trial_forms.py --check                   :: CHECK: OK（空白表与 trialkit.js 未被改）
python tools\collect_trial_feedback.py --self-test           :: SELF-TEST: 95 checks | FAIL: none
python tools\check_web_ui.py                                 :: 81/81 CLEAN（含试用模式端到端）
python tools\verify_integrity.py                             :: RESULT: PASS (181 checks)
python tools\directory_integrity_report.py                   :: VERDICT: CLEAN / 来源不明 0 / SHA 一致
python tools\run_all.py                                      :: 17 步全 OK，PIPELINE: ALL GREEN
```

端到端演练（`file://` headless，断网）：载入 C5 → 结果到 6 SKU 与 `Safety / FVT @ SKU6` →
只问 11 条必答 → 空表被拦（0/11）→ 填满放行 → 导出
`trial-submission-TRIAL-C5-SKU6-WAVE-*.json`（4 个目标格全部 `exercised: true`）。
门禁负例（缺姓名 / 缺日期 / 旧规则包 / 未跑 / 目标格没跑到 / 必答题留空）逐一被拦。
所有演练都在临时目录与 headless 页面里，正式 `feedback_inbox\` 与正式报告未被写入。

---

# Phase 3b 补充 4 · 回收卷取证修复（#32 / #33）+ Trial Form v4.1 + 网页提交修复（#34）

日期：2026-11-06 · 基线：Phase 3b 补充 3（网页内置试用模式，81/81 UI / 95 自测 / 181 完整性）
触发：第一次收到真人试用卷（`lingyu`，C1 + C2），回收过程暴露三个缺陷。
结果：**#32 / #33 / #34 全部 RESOLVED** · UI 96/96 · 采集器自测 119 · 完整性 227 · 17 步 ALL GREEN
本文件不改任何业务数字：Certification 仍按 DEC-10 采用附表总量，规则包仍是
`RP-V4.0 / DRAFT_PENDING_OWNER`，`SR-09` 仍是唯一 Expected Failure，ORI 仍是 19 条。

## 0. 回收到的两份真人试用卷（事实，不是评价）

| 案例 | 项目 | 试用者 / 日期 | 分析号 | 结果 | 目标差异格 |
|---|---|---|---|---|---|
| C1 | TRIAL-C1-SKU2 | lingyu / 2026-11-05 | AMW4JRAUF | SINGLE，推荐 SKU2，候选 `[2]`，总量 366 | `RF Certification / SIT @ SKU2`（附表 8 / 主表 15 / −7） |
| C2 | TRIAL-C2-SKU3 | lingyu / 2026-11-05 | AMW4K83XG | SINGLE，推荐 SKU3，候选 `[3]`，总量 408 | `Green / SIT @ SKU3`（6/9/−3）、`RF Certification / SIT @ SKU3`（9/15/−6） |

- 两份都被内核重算复核：与金标准数字一致，锁定项未被改，未用 Certification 覆盖，规则包正确；
  差异仅在 `analysis_id` / `engine_version`（`rules_v3/4.0` vs `rules_v3_web/4.0`）等元数据。
- 业务信号（原话进报告，不做推断）：Green 接受附表（“主表数据记录失误，应该是 6，Green 是固定
  数值”）；RF Certification 拒绝附表（“RF Certification 是 15”“以主表为主……不以 SKU 数量强相关”）；
  ORI-10 同意但注明“只是 LCFC 这一家 ODM 的数据”；UI 项不同意并说“应该显示主表全部 function 数据”。
- 独立性问题（记录，不当缺陷）：源表批注作者是 `Lingyu LY3 Rong`，与试用者同名，
  因此这两卷是有价值的业务反馈，但不能当作独立的界面可用性证据。
- 原始文件字节不变：
  C1 `a2e1401698e051cde4e464207968b0328e557696ed4987d2d09ea094c932cf95`、
  C2 `30eef08ed6fc603c2b7330d4eb9286ce10b99ee2c255d8bdf1dc88496731f502`（修复前后各校验一次）。

## 1. #32 · 报告把试用者写的理由丢了（RESOLVED）

现象：Owner 报告里只剩“同意 / 不同意”，行级 Comment 大量不见，
`RF Certification 是15`、`应该是 6`、`只是 LCFC 这一家 ODM 的数据` 这些取证原话没进报告。

修复（`tools/collect_trial_feedback.py`）：
- 台账行携带 `case` / `reviewer` / `sub_decision`，作答行同时保存 `answer` 与 `comment`；
- Markdown 第 11 节改为逐条输出「选择 + 理由 + 案例 + 试用者 + 来源文件」，同意也保留；
- 自测锁死：写入标记串后，必须在 JSON 与 Markdown 里都逐字找得回来。

## 2. #33 · ORI-02 被误报为自相矛盾（RESOLVED）

现象：C2 里 Green 同意附表、RF Certification 不同意附表，两格都映射到 ORI-02，
于是同一人被记成“既同意又不同意”；ORI-02b 因“验证提示同意 + RF 不同意”同理被误判。

修复（同一文件）：ORI-02 仍是一条正式 ORI，只在其下按 Function/Phase 建子决策
`GREEN_SIT` / `SAFETY_FVT` / `RF_CERTIFICATION_SIT`；只有**同一子决策内**出现相反答案才算冲突；
不同 Function 结论不同 → `FUNCTION_SPECIFIC_DECISION_REQUIRED`，交 Owner 定。
回收实测：`GREEN_SIT = AGREE(1)`、`RF Certification/SIT = DISAGREE(2)`、`conflict = false`，
`conflicting = []`，`function_specific_owner_items = [ORI-02, ORI-02b]`，ORI 台账仍 19 条。
`docs\44_owner_confirmation_one_shot_v4.md` 增加 D″ 子决策确认区（不新增 ORI 编号）。

## 3. Trial Form v4.1 发卷（C3 / C4 / C5）

- 差异格提问从自由文本“同意 / 不同意”改为四选一：**附表正确 / 主表正确 / 按条件区分 / 无法判断**，
  理由改为必填，页面同时显示两个候选数量（附表采用值 / 主表推算值）。
- 采集端把四选项映射为 `AGREE / DISAGREE / OTHER / OPEN`：`按条件区分` 仍是待 Owner 决的结论，
  `无法判断` 永远不算同意；`ANSWER_REASON` 门禁在页面与采集器两端同名同名。
- C1 / C2 在 roster 内标为 `issue_status: RETURNED`（记录已回收，不重发、不改写原卷）。
- **发卷闸门**：v4.1 在 #34 修好、UI 恢复 96/96 之前只是“已生成”，不算可发布版本；
  本轮全绿后才具备发 C3 / C4 / C5 的条件。

## 4. #34 · v4.1 网页提交不出去（RESOLVED）

### 根因

`web/ui_test.html` 用旧办法作答：对每道必答题执行
`setQ(q.id, "answer", "同意")`，即把元素 `.value` 直接设为 `同意`。
v4.0 的差异格是 `<textarea>`，这是合法文本；v4.1 起差异格是 `<select>`，
`同意` 不在四个 option 里，浏览器于是把 `selectedIndex` 置为 −1、`value` 变成空串。

### 实际失败位置与传导链

1. `web/ui_test.html`（作答步）：`setQ(..., "同意")` 打在 `<select>` 上 → 4 道差异格题仍为空；
2. `web/assets/trial.js` `gates()` 的 `REQUIRED_ANSWERED` → C5 记 7/11 → `canSubmit()` false
   → `refreshChecks()` 把 `#submit-btn` 保持 `disabled`；
3. `web/assets/trial.js` `submit()` 从未被调用 → `Export.download()` 未执行 →
   测试捕获句柄 `frame.contentWindow.__dl` 仍为 **null**；
4. 报错点 `web/ui_test.html`：`JSON.parse(W.__dl.text)` →
   `TypeError: Cannot read properties of null (reading 'text')`——为 null 的是**导出捕获对象**，
   不是题目、不是 session、也不是 DOM 渲染；
5. 次生失败：UI-46 四条断言与 `sub.trial_form_version`（当时未判空）在同一 null 上继续取值 → FATAL。

C1 / C2 旧格式之所以没触发：那时差异格是自由文本框，且根本没有 `ANSWER_REASON` 门禁（当时 6 项检查）。

### 顺带查出的两处真实缺陷（不在测试脚本里）

- `qBlock()` 在 `return` 之后残留 13 行死代码（补丁时期留下，运行不到但会误导后续维护）；
- v4.0 旧草稿在 v4.1 页面上被 `refreshChecks() → saveSession()` **静默清空**：
  下拉框显示空白却没有任何解释，而旧草稿里那句旧理由还能把 `ANSWER_REASON` 蒙过去。

### 修复内容

`web/assets/trial.js`
- 删除 `qBlock()` 中不可达的死代码；
- 新增 `formVersion(c)` / `migrateDraft(c)`：打开案例时比较草稿的 `form_version` 与本卷版本，
  凡差异格存的自由文本不在四个选项内 → 答案与它的理由一起退回空白，原文搬到 `legacy_v40`，
  案例记入 `needs_reanswer`，并把版本写回草稿（不会每次载入都重复迁移）；
- 提示不静默：顶部横幅 + 原题下方逐题写明「原回答『同意』不是四个选项之一，已作废，请重新选择
  （旧理由：…）」；仍是必答，不预填任何默认答案；
- 发布只读诊断出口 `Trial.lastChecks = {case, analysis_id, gates[], can_submit}`，
  供自动化按门禁 id 读页面实际跑出的结果（不是第二权威，回收仍以文件重算为准）。

`web/ui_test.html`
- `setQ()` 只写文本控件，遇到 `<select>` 返回 `NOT_A_TEXT_CONTROL`，**不再制造空白假答案**；
  新增 `pickQ()`（只能选真实存在的 option）、`selectValue()`、`gLast(id)`、`gateSummary()`；
- UI-44 的答案控件计数由“只数 textarea”改为 `select + textarea` 并要求 4 个下拉；
- UI-45 改为分阶段：姓名日期 → 只写文本 → 只选不写理由 → 写满，逐一验证是哪个门禁在拦；
- 导出捕获为 null 时，UI-46 报“页面根本没产文件 + 当时失败的门禁”，不再抛裸 TypeError；
  UI-50 先判 `sub` 存在再取字段；
- 新增回归：UI-51（未选/非选项值/选了没写理由/清空一条理由重新锁死）、
  UI-54（C3、C4、C5 各出一卷、7 项门禁全绿、四选项 + 理由齐）、UI-55（草稿记录本机所答版本）、
  UI-56（刷新后选项与理由原样恢复）、UI-57（v4.0 草稿显式失效：下拉空白、旧理由不再算数、
  提示可见、原文保留在 `legacy_v40`）、UI-58（不存在的案例返回 null；挂在没问过的题号下的答案不算作答）。

`tools/collect_trial_feedback.py` 自测 +8：页面 v4.1 形状的提交件原样回灌可读、门禁零告警；
缺理由被采集端独立拦下；`ANSWER`（选择）与 `ANSWER_REASON`（理由）互不替代；
未知案例查不到就报未知，不去猜。

`tools/verify_integrity.py` §9d：门禁清单补 `ANSWER_REASON`；新增 §9d-2 检查
`form_version = 4.1`、四选项完整且与发卷一致、`reason_required` 有效、两端门禁命名一致、
C1/C2 = RETURNED、C3/C4/C5 = 可发卷、#32 的逐字理由可达、#33 按子决策判冲突、ORI 仍 19、
以及“演练产生的提交件绝不能落进正式 `feedback_inbox\`”。

## 5. 本轮量到的事实

- 真人方式（选真实 option）跑 C3 / C4 / C5：三卷都能一键载入运行并导出，
  `trial_form_version: 4.1`，7 项门禁全绿，目标格全部 `exercised: true`
  （C3 覆盖 1 格 / C4 覆盖 2 格 / C5 覆盖 4 格，C5 实跑 SKU 4、5、6）；
- 页面真实生成的 C3 提交件（452,774 B）直接喂给 `parse_submission()`：
  `gate_findings = []`，`主表正确 → DISAGREE`，目标格被记为已取证，未触发覆盖；
- 门禁逐步表现：全空 0/11 → 只写文本 7/11（缺 4 个差异格）→ 只选不写理由 11/11 + 理由 0/4
  → 写满 7 项全绿；清空任意一条理由立刻重新锁定并点名那一格；
- C1 / C2 的 `RETURNED` 标记不影响 C3 / C4 / C5 载入与运行（探针实测）；
- 回收结论未变：`EVIDENCE_INCOMPLETE` —— 2/5 案例、2/3 差异组、3/7 差异格、5/19 Owner 问题。

## 6. 刻意不做的事

- 不改业务规则、案例配置、Certification 采用口径、4–5 SKU 范围、`SR-09`；
- 不改回收判定逻辑（只加自测），不重写已回收的 C1 / C2；
- 不新增网页功能：本轮只加了不兼容草稿的显式提示与一个只读诊断出口；
- 不用 try/catch 吞掉 null，不用默认答案绕过下拉，不删 session 恢复；
- 不启动 S2；不把演练提交件写进 `feedback_inbox\`。

## 7. 新增待决事项

`trial_kit\FOLLOW_UP_LINGYU.md`：6 条追问（RF=15 的出处与适用范围、附表 8–10 的业务含义、
Green 固定 6 的适用边界、Wave“待确认”的具体位置、要求显示主表全部 Function 具体指哪些列、
MEPA 36 / HW PA 4 是否只对 LCFC 成立）。这些追问不新增 ORI 编号，答案并回 `docs\44`。

## 复验

```
python tools\collect_trial_feedback.py --self-test   :: SELF-TEST: 119 checks | FAIL: none
python tools\issue_trial_forms.py --check             :: CHECK: OK（roster / 空白表 / trialkit.js 一致）
python tools\check_python_web_parity.py               :: 40/40 match | STATUS: MATCH
python tools\check_web_ui.py                          :: 96/96 | STATUS: CLEAN
python tools\verify_integrity.py                      :: RESULT: PASS (227 checks)
python tools\directory_integrity_report.py            :: VERDICT: CLEAN / 153 files / 来源不明 0 / SHA 一致
python tools\run_all.py                               :: 17 步全 OK，PIPELINE: ALL GREEN
```

SHA-256 校验：`original_documents` 仍为
`48A360FF2FFD086E41D6B90A916F64FE52D9BC13EFBA07B8377B2945C846AB5A`（未改）；
C1 / C2 原始提交件哈希与修复前一致（见第 0 节）。

---

# Phase 3b 补充 5 · C3/C4/C5 发卷前核对：Wave 声明的出处（ORI-03）+ 回收现状

任务：分发并回收 Trial Form v4.1 的 C3、C4、C5 真实试用反馈。
基线：#32 / #33 / #34 已关闭；C1、C2 已回收不重发；RP-V4.0 / DRAFT_PENDING_OWNER；
Certification 继续采用附表；SR-09 继续是唯一 Expected Failure。

## 1. 发卷前门禁（指令第 1 步，先跑再决定是否继续）

| 命令 | 结果 |
|---|---|
| `python tools\issue_trial_forms.py --check` | **CHECK: OK**（5 案例，差异格 7/7，ORI 必答 10/19、可达 19/19） |
| `python tools\run_all.py` | **PIPELINE: ALL GREEN**（17 步；parity 40/40；web UI 96/96；self-test 119；verify_integrity 227） |

## 2. 第 3 步核对：C5 的 Wave 预设引用了一个不存在的出处（发卷前拦下）

C5 靠 `cpu` 第 5 条 + `panel` 第 3 条 = `LATER_WAVE` 制造 Current Wave / Full Project 分叉，
但 `wave_assignment` 上写的是 `declared_by` / `wave_source` = **`FORMAL_REQUIREMENT_SHEET`**，
即「这个波次是正式需求表声明的」。核对后这句话不成立：

- 需求表根本没有波次列 —— ORI-03 的 summary 逐字是「波次判据缺失；需求表波次标记列」；
- 全表唯一与波次有关的文字是 C80（行 80）括号里的
  `(or SSD/Mem spec *2, arrange 2nd wave)`：只提 SSD / Memory，没提 CPU / Panel，也没给判据；
- DEC-04 明令 Agent 不得仅因存在第二种 SSD / Memory Spec 就推断第二波（docs/16「WV-05」）。

提交件会把锁定的输入原样带走，这条错误出处会随每一份 C5 提交件进入 Owner 视野，
并且试用者在页面上改不了（`locked.wave_assignment = true`）——所以必须在发卷前改掉。

## 3. 指令的备选方案（改用 SSD / Memory 产生分叉）实测后未采用

用 `prototype/rules_v3.py` 直接跑 C5 配置（cpu5 / gpu3 / panel3 / ssd2 / mem2）：

| Wave 预设 | CURRENT_WAVE | 定价 SKU | C5 覆盖差异格 |
|---|---|---|---|
| 不声明 | SINGLE(6)/6-6 | {6} | 2 |
| cpu5 + panel3（原配置） | RANGE/4-6 | {4,5,6} | **4** |
| ssd2 | SINGLE_WITH_RESERVATION/6-6 | {6} | 2 |
| mem2 | SINGLE_WITH_RESERVATION/6-6 | {6} | 2 |
| ssd2 + mem2 | SINGLE_WITH_RESERVATION/6-6 | {6} | 2 |

改用 SSD / Memory 会让 Current Wave 塔回 6 SKU，`RF Certification / SIT @ SKU4` 与 `@ SKU5`
在 C5 里不再被真实跑到（C5 从 4 格跌到 2 格）；而那条 C80 括号文字恰恰是 DEC-04 点名
禁止推断的对象，换过去在规则上更不站得住。因此**保留显式分叉，只改出处标注**。

## 4. 改动

| 文件 | 改动 |
|---|---|
| `tools/issue_trial_forms.py` | C5 `wave` 的 `declared_by` / `wave_source`：`FORMAL_REQUIREMENT_SHEET` → `USER_SELECTED`；新增 `assumption: true` + `assumption_note`；`source` / `goal` 改写为「唯一波次提法是 C80 括号、只提 SSD/Mem、无判据（ORI-03）」+ 「该波次只是案例预设的试用假设」 |
| `web/assets/trial.js` | Wave Assignment（案例预设）表下方按 `assumption_note` 打印提示；数据驱动，没有预设波次的案例不出现 |
| `trial_kit/START_HERE.md` | ① 同一提示；② v4.1 对齐：差异格是四选一 + 必填理由，提交前检查从「六件事」补成「七件事」（补上理由门）；③ 「本轮请选 C3/C4/C5，C1、C2 已回收不要重复提交」 |
| `tools/verify_integrity.py` | 新增 §9d-3（7 项）：只有 C5 预设波次、不得引用需求表作为波次出处、必须带 assumption 标记、页面与 START_HERE 都要打印该提示、分叉仍是 4-6 vs 6-6、四个差异仍被 C5 跑到、不得从 SSD/Mem 推断波次；另加 START_HERE 门禁（门数与页面一致、四个选项齐全、已回收案例不重收）与 UI-59 登记 |
| `web/ui_test.html` | UI-59 × 2：C5 的波次表下确实写着「未经 Owner 确认 / ORI-03」；没有预设波次的 C3 既无波次表也无该提示 |

业务数字、Rule Pack 版本、Certification 采用来源、4–5 SKU 范围、SR-09：均未改动。

## 5. 没做的事（明确记录，避免被误读为已完成）

- **没有生成任何模拟提交件，也没有替试用者填写一个字。**
- C3、C4、C5 至今 **0 份真实提交件**：`feedback_inbox\` 与全机检索均无
  `trial-submission-TRIAL-C3/C4/C5-*`；状态是「**已发卷、待回收**」，不是「已回收」。
- C1、C2 原始提交件、五份空白表单、`original_documents` 逐字节不变（见 §7）。

## 6. 修完后复核

| 项目 | 结果 |
|---|---|
| `collect_trial_feedback.py --self-test` | 119 checks，FAIL: none |
| `check_python_web_parity.py` | 40/40 MATCH |
| `check_web_ui.py` | **98/98 CLEAN**（含新增 UI-59 × 2） |
| `verify_integrity.py` | **PASS 240 checks**（227 → 240） |
| `run_all.py` | 17 步全部 OK，**PIPELINE: ALL GREEN**；regression 119/120 hold；EF = ['SR-09'] |
| `directory_integrity_report.py` | **CLEAN**，153 files，unknown-origin: none；original_documents ZERO CHANGES |
| 回收现状（真实） | 2/5 案例；3/7 底层差异格；5/19 ORI 有结论；conflict 0；Verdict = **EVIDENCE_INCOMPLETE** |

## 7. SHA-256（发卷前后对照，全部不变）

| 文件 | SHA-256 |
|---|---|
| original_documents 正式输入 | `48a360ff2ffd086e41d6b90a916f64fe52d9bc13efba07b8377b2945c846ab5a` |
| C1 提交件 | `a2e1401698e051cde4e464207968b0328e557696ed4987d2d09ea094c932cf95` |
| C2 提交件 | `30eef08ed6fc603c2b7330d4eb9286ce10b99ee2c255d8bdf1dc88496731f502` |
| C3 空白表单 | `62266288620af5ad0a511e4c6c93ea75f68e21d694a310bc720c096eb3434b0e` |
| C4 空白表单 | `8a6ecf78ceb3a214a7c6c4921724156da5f620c61557d468f6fe46cb1f83cee3` |
| C5 空白表单 | `9ac0d0863ee83fdd95335d1ed0af2e0d175c2a089f540c658a83c6b58e27cb99` |

> 波次判据本身仍然开着：ORI-03 的正式回答只能来自试用者在 C5 的 WAVE 问题上写下的
> 「你们实际按什么条件划分当前波次 / 后续波次」，不能来自案例自己的预设。


# Phase 2（摘要）

Owner Decision 收口 + 手工输入内核准备：DEC-01…DEC-08、`QMODEL-V2`、`rules_v2.py`、
Wave Assignment 契约、Reuse 四态防重复扣减、Panel 语义降级、D-01 小数口径、
Schema v2、84 探针、交付物 A–L。`SR-09` 起为唯一 Expected Failure。
详见 `docs/12`…`docs/21` 与 `docs/README.md`。

# Phase 1（摘要）

单份正式工作簿的只读取证、术语与分类、SKU 定义、计算模型、Schema 草案、
Owner Review Items（ORI-01…ORI-14）、原型规则与设计验证。
关键发现：**5 SKU 定义是 4 SKU 的严格子集，结构上永不可被单独推荐** → `SR-09` 按设计 FAIL。
详见 `docs/01`…`docs/11`。
