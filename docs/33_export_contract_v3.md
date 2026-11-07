# 33 — 导出契约：JSON 与团队 Review 报告（交付物 R、S）
> **状态（DEC-10 之后）**：本文描述的是 Phase 3a 的 Certification 口径
> （采用主表派生值）。Owner 已决定在 MVP 与团队试用阶段**采用附表总量**，
> 最新口径见 `docs/36_certification_adoption_v4.md`、`docs/37_owner_decision_log_v4.md`、
> `docs/39_totals_v4_and_6sku_review.md`、`docs/40_web_mvp_v4_changes.md`。
> 本文按原文保留，作为阶段记录。


实现位置：`web/assets/store.js`（结果页「导出 JSON」/「导出团队 Review 报告 (CSV)」）。
CSV 带 UTF-8 BOM，Excel 双击直接打开，中文不乱码。

**首要约束：区间在导出时不会变成单值。**
JSON 直接序列化引擎 payload，`policy.display_precision_modifies_values = false`、
`export.range_collapsed_to_single_value_on_export = false` 由 Schema 锁定（`CT-V2-12`、`D01-09`、
`UI-17`×3）。

---

## 1. JSON 导出（顶层键）

| 键 | 内容 | 对应任务 §21 要求 |
|---|---|---|
| `export_kind` / `export_version` | `SAMPLE_REQUIREMENT_ANALYSIS` / `3.0` | — |
| `exported_at_local` | 导出时刻（本地时区，含时区名） | 生成时间 |
| `analysis_id` / `project_name` | 记录标识 | — |
| `analysis_engine_version` | `rules_v3/3.0`（Web 侧为 `rules_v3_web/3.0`） | Analysis Engine Version |
| `rule_package_version` | `RP-V3.0` | Rule Package Version |
| `schema_version` | `3.0` | Schema Version |
| `quantity_model_version` | `QMODEL-V3/3.0` | — |
| `baseline_id` | `BASELINE-CS-ODM-001` | — |
| `input_snapshot` | 完整输入文档（与前端提交内容同构） | Input Snapshot |
| `file_read_value_vs_user_confirmed_value` | 每个 Key Factor 的 `file_value` / `user_value` / `user_edited` / `effective` / `value_source` / `user_status` | File-read Value 与 User-confirmed Value |
| `applied_value` | 实际生效值（同一结构，便于左右对照） | Applied Value |
| `sku_result` | 每情景的 `state` / `recommended_sku` / `preferred_sku` / `sku_range` / `candidates_priced` | SKU 结果或范围 |
| `current_wave` / `full_project` | 两个情景的完整对象 | Current Wave / Full Project 结果 |
| （scenario[].results[]） | `recommended_total` 或 `recommended_total_band`、`fvt_total`、`sit_total`、`certification_demand`、`non_certification_demand`、`risk_reserve`、`conditional_increment`、`confirmed_reuse_adjustment` | 样机需求值或范围、FVT/SIT 拆分 |
| `certification_main_table_values` | 逐格 `main_table_per_sku` / `applied_total` / `appendix_total` / `verification_status` / `value_source`（按情景 × SKU 展开） | Certification 主表值 + 附表验证值 |
| `certification_cell_verification` | **40 格完整网格**：`function` / `phase` / `sku_count` / `main_table_per_sku_quantity` / `derived_total` / `appendix_total` / `delta` / `verification_status` / `source_reference` | Certification 逐格验证状态 |
| `j33_evidence` | `evidence_role` / `disposition` / `declared_reference_scenario` / `reference_total_under_readings` / `bracket` / `added_to_certification_result=false` / `raw_text` | J33 Evidence 状态 |
| `reuse_ledger` | 按情景 × SKU 的 `requested` / `adopted` / `rejected_or_deferred` + 每项 `decision` 与 `why` | Reuse 账本 |
| `review_items` | 全部 Owner Review Item（含 `blocking_level`、`blocks_manual_mvp`） | Review Items |
| `panel_annotation_excluded` | D2:H2 批注原样回显 | 被排除的 Panel 批注证据 |
| `policy` | 舍入口径、显示精度、比较容差、Certification 与 J33 角色、波次与复用口径 | — |
| `values_full_precision` | `true` | 底层值未被格式化改写 |
| `payload` | 引擎完整输出（Function 明细、Quantity Model、`totals_by_model`、`by_function`、`by_category`、`wave_report`、`match.scores`、`rule_id`、`evidence.row` 全在内部） | Function 明细、Quantity Model |

### 底层精度示例

导出中会出现 `"FVT": 65.49999999999999`（3 SKU 的 Workbook SUM/sku），
**不会**被写成 `65.5`；同样 `9.6` 保持 `9.6`。显示层可以渲染成 `65.5`，
但那只是渲染（任务 §20 第 7、8 条）。

### 区间示例（4–5 SKU）

```json
"sku_result": [
  {"scenario": "FULL_PROJECT", "state": "RANGE", "recommended_sku": null,
   "preferred_sku": "NOT_ESTABLISHED", "sku_range": [4, 5], "candidates_priced": [4, 5]}
]
```
两档各自的 `recommended_total`（443.8 与 474.0）都在 `results[]` 里，
`recommended_total_band.exact = false`。文件里**没有**任何"代表值"字段。

---

## 2. 团队 Review 报告（CSV，7 个区块）

| 区块 | 列 | 说明 |
|---|---|---|
| 头部元数据 | Project / Analysis ID / Engine / Rule pack / Schema / Quantity model / Saved / Rounding | Rounding 恒为 `NONE (D-01) - underlying values keep their decimals` |
| **1. SKU result** | Scenario, State, Recommended SKU（null → `not established`）, Preferred, Range, Candidates priced | 范围不会被写成单档 |
| **2. Totals** | Scenario, SKU, FVT, SIT, Certification, Non-certification, Reuse adopted, Risk reserve, Recommended total, Single value | 每档一行，不做合并 |
| **3. Function detail** | Scenario, SKU, Function, Phase, Quantity model, Applied, **User status**, Main /SKU, Reason, Rule, Source row | User status 用普通语言：已计算 / 已验证 / 请确认 / 临时采用 / 用户输入 / 暂无法计算 |
| **4. Certification cell verification** | Function, Phase, SKU, Main /SKU, Derived, Appendix, Delta, Status, Main row, Appendix row | 逐格，附源表行号，便于直接翻回工作簿 |
| **5. J33** | Role / Disposition / `Added to result = NO` / Declared reference | 明确写 NO，避免读者以为已叠加 |
| **6. Reuse ledger** | Scenario, SKU, Status, Qty, Unit, Applied, Decision, Why | 未扣减的也全部列出并给原因 |
| **7. Review items for the Owner** | Kind, Blocking level, Blocks manual MVP, Function, Phase, Why | 与 Register 口径一致 |
| **8. Excluded Panel annotation evidence** | SKU n, 批注原样内容 | DEC-02 要求随结果同行 |

CSV 是**摘要**，用于会议过一遍；需要复算或审计时用 JSON。
两者都不含账号、团队、审批等概念（本 MVP 无这些概念）。

---

## 3. 已知限制

- CSV 用 `-`（连字符）作数值区间的分隔（如 `4-5`），JSON 保留 `–`；这是 CSV 单元格内
  的展示选择，不改变 `sku_range` 本身。
- CSV 的 Function 明细默认取该情景**第一个**（最低）SKU 档位；两档差异在区块 2 的逐档总量里体现。
  需要两档逐 Function 对照请用 JSON。
- 导出下载依赖浏览器 Blob；`file://` 下 Chrome/Edge 均正常。
- 报告是"一次分析"的快照。多项目横向汇总不在本期范围（任务 §10）。
