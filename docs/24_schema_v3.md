# 24 — Schema v3 变更（交付物 F）
> **状态（DEC-10 之后）**：本文描述的是 Phase 3a 的 Certification 口径
> （采用主表派生值）。Owner 已决定在 MVP 与团队试用阶段**采用附表总量**，
> 最新口径见 `docs/36_certification_adoption_v4.md`、`docs/37_owner_decision_log_v4.md`、
> `docs/39_totals_v4_and_6sku_review.md`、`docs/40_web_mvp_v4_changes.md`。
> 本文按原文保留，作为阶段记录。


三个 Schema 全部升到 **`3.0`**。变更都是**收紧**，没有放宽任何口径。

---

## 1. `schema/input.schema.json`（v2 → v3）

| 变更 | 说明 |
|---|---|
| `schema_version` | `const "3.0"` |
| `project_name` | 新增（可选），首页列表显示用；`project_label` 保留为 v2 兼容别名 |
| `project_type` | 新增：`CLEAN_SHEET`（默认）/ `EXISTING_PLAN` / `OTHER` |
| `phase_scope` | 新增：`FVT` / `SIT` 子集，默认两者 |
| `spec_labels` | 新增（可选）：SSD / Memory 的 Spec 名称，**永不参与计算** |
| `specWave.wave` | 枚举加入 **`NO_EXPLICIT_ASSIGNMENT`**（界面文案「未特别指定」）。`UNKNOWN` 保留但只用于用户显式选择"未知"的情形 |
| `certification_input.mode` | 由 `UNRESOLVED_SHOW_BAND`/`MANUAL_OVERRIDE` 改为 **`SYSTEM_MAIN_TABLE`** / **`USER_OVERRIDE_FOR_MISMATCH_CELLS`** — 契约层面取消了"显示竞争区间"这一模式 |
| `certification_input.overrides[].qty` | 语义改为"本次分析对该格的采用总量"，`reason` 必填；系统值与用户值同时保留 |
| `reuse_items[]` | 新增 `note`（Evidence Note），与 `basis` 等价保留 |
| `keyFactor.file_value` | 仍为 `number|null`，因此 `"N/A"` / `"case by case"` 无法混入（探针 `SC-03`） |
| `risk_reserve.percent` | 默认 0，`0..1`；ORI-07 未确认前不自动加数 |

## 2. `schema/output.schema.json`（v2 → v3）

**删除**：`certification_unresolved`、`competing_candidates`、`variants_not_evaluable` 中的
`J33_FORMULA`、`SINGLE_ADOPTED_MODEL` 变体名。

**新增 `$defs.certification`**，并用 `const` 把 DEC-09 写进 Schema：

| 字段 | 约束 | 意义 |
|---|---|---|
| `counted_in_project_total_times` | **`const 1`** | Certification 在项目总量中恰好计入一次 |
| `appendix_role` | **`const "DERIVED_TOTAL_VALIDATION"`** | 附表角色不可被改写 |
| `appendix_counted_in_project_total_times` | **`const 0`** | 附表再次计入 = Schema 校验失败 |
| `j33_added_to_result` | **`const false`** | J33 叠加 = Schema 校验失败 |
| `phase_ratio_used` | **`type: null`** | 任何全局 FVT/SIT 比例都无法通过校验 |
| `model` | `const "PER_SKU_RATE"` | 只有一套模型 |
| `verification` | `{cells_total, verified, mismatch, not_evaluable, status, comparison_tolerance}` | 逐格验证结果 |
| `cells[]` | 每格含 `main_table_per_sku_quantity` / `system_computed_total` / `applied_total` / `user_input_total` / `value_source` / `appendix_total` / `delta_appendix_minus_derived` / `verification_status` / `main_table_row` / `appendix_row` | 系统值、用户值、采用来源、来源行全部可追溯 |
| `range_reason` | `type: null` | Certification 自身**不可能**产生范围 |

其他新增：

- `$defs.j33`（`evidence_role const BREAKDOWN_EVIDENCE`、`disposition` 枚举、`added_to_certification_result const false`）
- `scenario.excluded_specs`（被排除出 Current Wave 的 Spec，页面据此解释差异）
- `row.evidence_role` / `system_computed_value` / `user_input_value` / `main_table_per_sku_quantity` /
  `source_validation` / `breakdown_evidence_role` / `is_temporary_model`
- `reuse_summary`：`requested_reuse_quantity` / `adopted_reuse_quantity` /
  `rejected_or_deferred_quantity` / `adoption_reason` / `non_adoption_reason`（§19 输出契约）
- `owner_review_summary`（含 `blocks_manual_mvp`）
- `engine_version`、`policy.certification_*`、`policy.display_precision_modifies_values = false`
- `export.range_collapsed_to_single_value_on_export`（导出折叠区间 = 显式否证）

保留的结构性红线（v2 已有，v3 继续）：

- `single_value = false` → `base_demand` / `fvt_total` / `sit_total` / `risk_reserve` /
  `recommended_total` **必须全部为 null**（防止前端把区间偷偷变成一个数）
- `single_value = true` → 上述字段必须是真实数字且 `recommended_total_band.exact = true`
- `match.state = RANGE` → `recommended_sku` 必须 null、`preferred_sku` 必须 `NOT_ESTABLISHED`、
  `tie_set` 至少 2 项
- `row.rounding` 恒为 `"NONE (D-01)"`

## 3. `schema/rule.schema.json`（v2 → v3）

新增 `$defs`：

- **`evidenceRole`**（5 值枚举 + 语义说明）
- **`certificationCellVerification`**（逐格验证记录；`additionalProperties:false`，
  要求 `main_table_per_sku_quantity` / `derived_total` / `appendix_total` / `delta` /
  `verification_status` / `source_reference` 齐全）
- **`j33Investigation`**（`source_cell const "J33"`、`evidence_role const BREAKDOWN_EVIDENCE`、
  `disposition` 枚举、`additive_to_main_table_result const false`）
- **`ori_02Status`**（`OPEN`/`OWNER_REVIEW_REQUIRED`/`PARTIALLY_RESOLVED`/`RESOLVED`/`CLOSED_BY_DECISION`）

`quantityModel` 增加 `evidenceRole`、`validation`、`mainTablePerSkuQuantity`；
`ownerReviewItem` 增加 `review_item_id`、`blocking_level`（4 级枚举）、`decision_status`（5 值枚举）。
根节点增加 `certification_verification[]`、`j33_investigation`、`ori_02_status`。

## 4. 契约一致性探针

| 探针 | 断言 |
|---|---|
| `SC-01` | 引擎真实输出通过 `output.schema.json` |
| `SC-02` | 完整手工输入文档通过 `input.schema.json` |
| `SC-03` | 文本哨兵 `"N/A"` 不能冒充缺失数值 |
| `SC-04` | 未知 Reuse 状态与未知 Wave 值都被拒绝 |
| `SC-05` | `appendix_counted_in_project_total_times = 1` 被拒绝 |
| `SC-06/07` | `from_document()` 与波次引擎严格按契约工作 |
| `SC-08` | 覆盖后的 Certification 仍通过校验且保留三重来源 |
| `SC-09` | `single_value = true` 而总量为 null 被拒绝 |
| `SC-10` | 附表被改标为 Quantity Model 被拒绝 |
