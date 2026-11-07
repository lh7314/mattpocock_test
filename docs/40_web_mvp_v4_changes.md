# 40 — 三页 Web MVP 在 DEC-10 下的改动（交付物 E）

界面运行方式不变：双击 `web\index.html`，全程离线，无服务器、无账号、无权限、无审批流。

## 1. 默认显示：附表采用值

| 页面 | 改动 |
|---|---|
| `index.html` | 首页"不会做的事"清单改为：不会把主表值与附表值相加；Certification 采用附表在本次 SKU 档位上的总量，并且只计入一次 |
| `new.html` 高级选项 | Certification 预览表列顺序：**采用值（附表）→ 主表 /SKU → 主表 × 本次 SKU 数（审计）→ 差值 → 状态 → 本次覆盖（可选）**；说明文字明确"主表值只用于审计和差异分析，不进入总量" |
| `result.html` | Certification 区块默认表只有 `Function / Phase / SKU / 采用值（附表）/ 状态`；主表值与差值移到 `<details>`「展开：主表口径与差异（审计，不计入总量）」 |
| `result.html` | Function 明细表列名 `建议值 → 采用值`；技术详情里 `verification → main_table_audit`，并新增 `main_table_derived_total` |
| 所有页面 | **没有任何"选择主表 / 选择附表"的控件**（探针 UI-27 断言不存在这类控件，且页面写明采用附表） |

状态标签（普通用户可见，8 种）：
`已计算` / `已验证` / `请确认` / `临时采用` / `用户输入` / `结果范围` / `暂无法计算` / `已排除`。
其中 `已验证` = 主表派生与采用值一致；`请确认` = 两者不一致（差值在展开详情里）。

## 2. 本次分析手工覆盖

- 覆盖入口仍在 Certification 预览里（列名「本次覆盖（可选）」），**任何** Certification 格都可填，
  不再只限主表/附表不一致的格子——因为现在采用值来自附表，用户可能有项目级理由。
- 覆盖写入 `document.certification_input.overrides[]`，
  快照声明 `mode = USER_OVERRIDE_FOR_MISMATCH_CELLS`、`override_scope = THIS_ANALYSIS_ONLY`；
  未覆盖时 `mode = SYSTEM_APPENDIX_ADOPTED`。
- 覆盖结果行同时保留三个值：采用值（覆盖后）、`system_computed_value`（规则包默认）、
  `user_input_value`（用户输入），并给出
  `user_override_vs_adopted_value = MATCHES_ADOPTED_APPENDIX_VALUE / DOES_NOT_MATCH_ADOPTED_APPENDIX_VALUE`。
- 规则包文件在覆盖前后 SHA-256 不变（探针 `DA-11`）。

## 3. 导出（三种，全部由 Python 内核与 Web 内核分别实现并逐字节比对）

| 导出 | 文件 | 内容 |
|---|---|---|
| JSON | `sample-analysis-<项目>-<时间>.json` | 完整 payload + `owner_decision` + `certification_adopted_and_audit_values[]`（采用值、主表 /SKU、主表派生、附表、差值、`main_derived_counted_in_project_total=false`）+ 输入快照；范围保持范围，`range_collapsed_to_single_value_on_export = false` |
| 团队 Review 报告 CSV | `sample-review-<项目>-<时间>.csv` | 8 段：SKU 结果 / 总量 / Function 明细 / **Certification 采用值 vs 主表审计值（含 `Adopted counted,Audit counted = 1,0`）** / J33 / Reuse 账本 / Owner 待确认 / 被排除的 Panel 批注 |
| 试用反馈表 CSV | `trial-feedback-<项目>-<时间>.csv` | 本次结果逐项确认 + **主表/附表仍不一致的格子**（每格一行，附采用值、审计值、差值）+ 本次登记的待确认问题 + 规则包 19 条唯一 Owner 问题 + 界面反馈 |

导出实现在 Python 内核（`prototype/rules_v3.py` 内 `export_json_document /
export_review_csv / export_trial_feedback_csv`），`web/assets/store.js` 是同契约的移植。

## 4. 一致性与界面探针（本轮扩充）

- `tools/check_python_web_parity.py`：**40 个用例**（原 24 个 + 16 个），
  每个用例同时比较 `payload`、`input_snapshot`、`json_document`、`review_csv`、`feedback_csv`；
  数值容差 1e-9，枚举/字符串/null 必须完全一致，CSV 逐行比对。当前 **40/40 MATCH**。
- 覆盖点：7 个不一致格全部至少被两个用例覆盖（`RF/SIT@2,3,4,5,6`、`Green/SIT@3`、
  `Safety/FVT@6`）、附表只计一次、主表保留但不计入、J33 不叠加、4–5 范围、
  Current Wave vs Full Project、手工覆盖（等于/不等于采用值、覆盖已一致格）、
  底层小数（风险预留 0.065 / 0.075 组合）、三种导出文件。
- `tools/check_web_ui.py` + `web/ui_test.html`：**44 项界面检查**（原 37 项），新增
  `UI-25` 采用值默认可见（无需展开）、`UI-26` 主表值与差值只在展开详情、
  `UI-27` 页面无主表/附表选择控件、`UI-11a` 覆盖为可选且写明不写回规则库、
  `UI-28` 试用反馈导出、`UI-29` Review CSV 双列与计入次数、`UI-30` JSON 导出双列与计数标记。
  当前 **44/44 CLEAN**。
- 浏览器仍在无网络条件下运行（`--host-resolver-rules "MAP * ~NOTFOUND"`）。

## 5. 已知界面限制（团队试用前须知）

1. 记录存在浏览器 localStorage，换机器/清缓存即丢失 → 请及时导出 JSON。
2. 覆盖值是"绝对台数"，不是百分比；填错只能重跑一条分析。
3. 主表口径只在展开详情里，若团队习惯看主表列，需要主动展开（这是 DEC-10 的刻意设计）。
4. 规则包仍为 `DRAFT_PENDING_OWNER`，导出文件里 `policy.certification_model =
   "APPENDIX_ADOPTED_TOTAL (DEC-10)"`，试用结论应按"临时采用"理解。
