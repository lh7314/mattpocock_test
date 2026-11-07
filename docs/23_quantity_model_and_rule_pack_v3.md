# 23 — Quantity Model v3 与 Rule Package v3（交付物 D、E）
> **状态（DEC-10 之后）**：本文描述的是 Phase 3a 的 Certification 口径
> （采用主表派生值）。Owner 已决定在 MVP 与团队试用阶段**采用附表总量**，
> 最新口径见 `docs/36_certification_adoption_v4.md`、`docs/37_owner_decision_log_v4.md`、
> `docs/39_totals_v4_and_6sku_review.md`、`docs/40_web_mvp_v4_changes.md`。
> 本文按原文保留，作为阶段记录。


机器可读：`artifacts/model/quantity_model_v3.json` / `.md`、`artifacts/model/rule_pack_v3.json`、
`web/assets/rulepack.js`。生成器：`tools/build_quantity_model_v3.py`、`tools/build_rule_pack_v3.py`。
两者都只读 `baseline_v1.json` + `certification_verification.json`，不含任何人工录入的业务数字。

---

## 1. Quantity Model 枚举（保持不变）

`PER_SKU_RATE` / `PER_PHASE_FIXED` / `PER_PROJECT_FIXED` / `FORMULA_DRIVEN` / `UNRESOLVED`

新增**证据角色**枚举（与 Quantity Model 正交，绝不可当作可叠加的 Quantity Model 使用）：

`PRIMARY_QUANTITY_MODEL` / `DERIVED_TOTAL_VALIDATION` / `BREAKDOWN_EVIDENCE` /
`ABSOLUTE_RESTATEMENT` / `UNRESOLVED_COMMENT`

`validate_rules_v3.py:QM-09` 与 `verify_integrity.py §4` 双向守护：
`DERIVED_TOTAL_VALIDATION` 必须存在于 evidence role 枚举，且**必须不存在**于 Quantity Model 枚举。

## 2. 分布（42 格 = 21 Function × 2 Phase）

| | Phase 2 (QMODEL-V2) | **Phase 3 (QMODEL-V3)** |
|---|---|---|
| `PER_SKU_RATE` | 30 | **38** |
| `PER_PHASE_FIXED` | 4 | **4**（MEPA FVT/SIT、HW PA FVT/SIT，未变） |
| `UNRESOLVED` | 8 | **0** |
| `value_access = MAIN_TABLE_DERIVED` | 30 | 38 |
| `value_access = ABSOLUTE_TABLE_READ` | 12 | 4 |
| `owner_review_cells` | 12 | **7** |
| model questions | 6 | 6（未变） |
| embedded-sharing Functions | 15 | 15（未变） |

Certification 8 格全部转为 `PER_SKU_RATE`；其中 5 格 `CONFIRMED_BY_SOURCE_VALIDATION`，
3 格（Green/SIT、Safety/FVT、RF Certification/SIT）保持 `DRAFT_PENDING_OWNER` 并携带逐格验证结果。

## 3. 逐格字段

每个 cell 现在带：`quantity_model`、`evidence_role`、`adopted_absolute{SKU2..6}`、
`main_table_per_sku_quantity{}`、`main_table_absolute{}`、`adopted_source`、`owner_review_required`、
`is_temporary_model`、`status`、`rule_id`(`QM3:<fid>:<phase>`)、`evidence{}`、
`validation{}`（Certification）、`breakdown_evidence{}`（仅 RF Certification）、
`phase2_superseded{}`（记录 Phase 2 曾如何解释以及为何废止）。

`validation{}` 内含 `evidence_role=DERIVED_TOTAL_VALIDATION`、`appendix_row`、`relationship`、
`per_sku{SKU2..6}{main_table_per_sku_quantity, derived_total, appendix_total, delta,
verification_status, main_table_row, appendix_row}`、`fully_verified`、
**`counted_in_project_total = false`**、`may_form_a_band = false`。

## 4. policy 中的硬约束

| 键 | 值 | 守护探针 |
|---|---|---|
| `certification_model` | `PER_SKU_RATE from the Main Table` | `CT-V2-03` |
| `certification_relationship` | `appendix_total == main × sku_count` | `CT-V2-01` |
| `certification_appendix_may_be_added_to_total` | **false** | `CT-V2-02`、`LG-04`、`SC-05` |
| `certification_appendix_may_form_a_band` | **false** | `CT-V2-03`、`LG-04` |
| `certification_appendix_may_override_main_table` | **false** | `LG-04` |
| `certification_appendix_is_a_capping_model` | **false** | `LG-04` |
| `certification_j33_role` | `BREAKDOWN_EVIDENCE - explanatory, never additive` | `JG-01`、`CT-V2-08` |
| `certification_global_phase_ratio` | `PROHIBITED - FVT and SIT read their own row` | `CT-V2-06/07` |
| `certification_band_origin_after_correction` | `SKU_NOT_ESTABLISHED only` | `CT-V2-05` |
| `pseudo_rate_models` | `PROHIBITED (no divide-by-SKU-then-multiply-back)` | `QM-02` |
| `flat_shape_alone_is_not_evidence_for_PER_PHASE_FIXED` | true | `QM-05` |
| `panel_annotation_d2_h2` | `UNRESOLVED_COMMENT - excluded` | `PL-01..PL-05` |
| `reuse` | 只有已证明的 `ADDITIONAL_CONFIRMED_REUSE` 才扣减 | `RS-01..RS-10` |
| `mepa_hw_pa` | `PER_PHASE FIXED candidate, temporary pending Owner (ORI-10)` | `QM-01/QM-07` |
| `rounding` | `NONE (D-01)` | `D01-03` |

## 5. MEPA / HW PA / EMC Test / NV / INTEL 的处置（未变，按要求复述）

- **MEPA、HW PA**：继续 `PER_PHASE_FIXED` 候选模型（附表 70/71 恒为 36；72/73 为整数且与
  `rate × SKU` 不一致）。前端显示 **临时采用**，`is_temporary_model = true`。
  不恢复为"除以 SKU 再乘回"的伪费率。
- **EMC Test、NV、INTEL**：继续 `PER_SKU_RATE`；6 条 model questions 原样保留；
  不因数值表现平坦而自动升级为固定量。

---

## 6. Rule Package v3（交付物 E）

`artifacts/model/rule_pack_v3.json`，版本 **`RP-V3.0`**，状态 `DRAFT_PENDING_OWNER`。

内容：`source_file` + SHA-256、`sku_definition`、`sku_definition_header_comments`（被排除的
Panel 批注证据）、21 个 Function（含 purpose/status 原文）、42 个 cell、
`certification_verification`（40 格网格 + 摘要 + ORI-02 状态 + Owner 语义）、
`j33_investigation` 全文、`baseline_embedded_sharing`、`model_questions`、`policy`、
`tolerance = 1e-9`、`dim_weight` / `verdict_weight`（附 ORI-08 免责说明）、
`open_owner_review_items`（11 项，全部 `blocks_manual_mvp = false`）、`blocking_rule`。

同一对象以 `window.RULEPACK = {...}` 形式写入 `web/assets/rulepack.js`，
因为 MVP 需要双击 `file://` 直接运行，而 `file://` 下 `fetch()` 本地 JSON 会被浏览器拦截。

**前端不保存任何业务数字**：`web/assets/core.js` 里没有任何总量常量（`verify_integrity.py §8`
检查这一点）。SKU 推荐、Certification、Reuse、Wave 的判断只有一份实现语义，
由 `tools/check_python_web_parity.py` 逐字段比对（见 `docs/31_python_web_parity_v3.md`）。

`rule_pack_version` 会出现在每一份输出里（Python 与 Web 一致，均为 `RP-V3.0`）。
