# 12 — A. Owner Decision Log（Phase 2 收敛）

> 本文件记录 **Owner 在 Phase 2 已明确下达的决策**，以及 Agent 据此落到模型里的具体约束。
> 每条决策都有编号（`DEC-nn`），后续文档、Schema、探针注释都引用该编号，便于追溯。
>
> **决策来源**：Owner Phase 2 任务书（本地会话指令），非网络资料、非 Agent 推断。
> **状态口径**：`ADOPTED` = 已写入模型且有回归探针守护；`ADOPTED_PARTIAL` = 临时处置已落地，
> 但最终结论仍等待 Owner 或真实样本。

---

## DEC-01 · 4 SKU / 5 SKU 分界（对应 ORI-04）

| 项 | 内容 |
|---|---|
| 状态 | `ADOPTED_PARTIAL`（临时处置已实现，业务分界仍缺） |
| Owner 指令 | 证据不足以建立 4/5 SKU 可靠分界；同时匹配时输出 4–5 SKU 范围 |

**已落地的约束**

1. 输入同时匹配 4 SKU 与 5 SKU → `state = RANGE`，`sku_range = [4, 5]`。
2. `recommended_sku = null`，`preferred_sku = "NOT_ESTABLISHED"`。
3. 范围成员**全部计价**：`candidates_priced = [4, 5]`，两个 SKU 的 FVT/SIT/Function 明细都输出。
4. **不允许**通过调整评分权重制造唯一答案。权重常量被探针 `SR-10` 锁死为 Phase 1 的值，
   改动即视为回归。
5. `SR-09` 探针（"每个 SKU 定义都必须能被单独推荐"）保持 `expected="FAIL"`。
   在拿到真实 4 SKU / 5 SKU 项目样本与正式分界条件之前，**不得**改为 PASS、不得删除、
   不得弱化。

**探针**：`SR-01` `SR-02` `SR-03` `SR-04` `SR-09`（EXPECTED FAIL） `SR-10`

**仍未关闭**：ORI-04 保持 `OPEN`，仍阻塞 `CONFIRMED_RULE_PACK`，**不阻塞**手工输入 MVP 主链路
（主链路输出范围即为正确交付，不是降级）。

---

## DEC-02 · Panel 语义冲突（对应 ORI-01）

| 项 | 内容 |
|---|---|
| 状态 | `ADOPTED`（临时口径已落地，批注真实含义仍待确认） |
| Owner 指令 | SKU Definition 的 Panel 字段按 **Panel Spec Count** 建模；`D2:H2` 批注 `N*panel` 保持 `UNRESOLVED_COMMENT`，不进入推荐与算量；不删除 Panel Spec 独立输入维度；保留冲突证据 |

**已落地的约束**

1. 匹配器只读 `SKU Definition`（行 79–83）的 Panel 区间：
   `SKU2 [1,2] · SKU3 [1,1] · SKU4 [2,2] · SKU5 [2,2] · SKU6 [2,3]`。
2. `D2:H2` 批注（Panel = 2/3/4/5/6，CPU 在 6 SKU 处还写 3 而定义是 4–5）
   整体降级为 `UNRESOLVED_COMMENT`，在输出里以
   `unresolved_comments_excluded` 字段**原样回显**，让 Owner 看得见被排除了什么。
3. `panel` 仍是五维输入之一，UI 不删该字段。
4. 反证探针 `PL-04`：`panel=1` 仍能得出 3 SKU —— 若 E2 批注参与了匹配，这在数学上不可能，
   因此可证明批注确实不在计算路径上。

**探针**：`PL-01` `PL-02` `PL-03` `PL-04`

---

## DEC-03 · Certification 竞争模型（对应 ORI-02）

| 项 | 内容 |
|---|---|
| 状态 | `ADOPTED`（三模型并列保留，业务选型未定） |
| Owner 指令 | Main Table / Secondary Table / J33 Formula 作为三份独立竞争证据；Certification Quantity Model 保持 `UNRESOLVED`；结果标记 `OWNER_REVIEW_REQUIRED`；不使用全局 FVT/SIT 比例；不自动选择或合并；MVP 预留手工输入/覆盖接口；当前采用值需显示来源与临时状态 |

**已落地的约束**

1. 4 个 Certification Function × 2 Phase = **8 个 cell 全部 `quantity_model = UNRESOLVED`**，
   `adopted_source = NONE_UNRESOLVED`，`adopted_absolute = null` —— 引擎**不持有**任何被
   自动采纳的 Certification 数值。
2. 输出用 `totals_by_model.variants` **按证据源分别完整计价**：
   `MAIN_TABLE` 一条、`SECONDARY_TABLE` 一条，`band` 给出区间。明确禁止平均/折中。
3. `J33_FORMULA` 作为 `FORMULA_DRIVEN` 候选保留在 `variants_not_evaluable`：
   它需要 antenna source / WLAN card 数量，而这不在 MVP 五维输入里，因此**声明但不可评估**，
   不会被静默丢弃，也不会被别的模型替代。
4. `certification_input.overrides` 提供逐项手工输入；一旦填写，该行 `value_source =
   USER_MANUAL_OVERRIDE`、`owner_review_required = false`，其余 cell 仍 `UNRESOLVED`。
   （EX-G 显示：只覆盖 RF Certification SIT 后，4 SKU 区间从 `438.8–443.8` 收敛到 `438.8`，
   因为剩余 cell 两套模型恰好一致。）
5. FVT/SIT 一律逐 cell 查表。探针 `CT-06` 证明各 SKU 档的 FVT 占比互不相同（0.4712…0.4769），
   因此**不存在**可使用的全局比例，也不允许构造一个。
6. 两套模型恰好一致的 cell（如 EMC、Green FVT）**仍保持 `UNRESOLVED`**，只是额外标注
   `models_agree = true`——一致性是信息，不是把模型升级为 CONFIRMED 的理由。

**探针**：`CT-01`…`CT-08`

---

## DEC-04 · Wave Assignment（对应 ORI-03）

| 项 | 内容 |
|---|---|
| 状态 | `ADOPTED` |
| Owner 指令 | 采用显式 Wave Assignment：`CURRENT_WAVE` / `LATER_WAVE` / `UNKNOWN`；Wave 只能来自正式需求表明确标记或用户选择；Agent 不得仅因存在第二种 SSD/Memory Spec 就推断第二波；Current Wave 排除明确属于 LATER_WAVE 的 Spec；Full Project 包含全部 Spec；不使用固定比例或固定数量折减；UNKNOWN 产生范围和 Owner Review Item |

**已落地的约束**

1. Wave 挂在 **单个 Spec** 上（`Spec.wave` + `Spec.wave_source`），不挂在"维度"上——
   一个维度有两颗 Spec 时，必须逐颗指定。
2. `wave_source ∈ FORMAL_REQUIREMENT_SHEET / USER_SELECTED / IMPLICIT_SINGLE_SPEC / NOT_PROVIDED`。
   只有前两者算"有依据"。
3. **未标注 ≠ UNKNOWN**。未标注的 Spec 计入 Current Wave 并标记 `NOT_PROVIDED` + 生成 ORI
   `WAVE_ASSIGNMENT_NOT_PROVIDED`；`UNKNOWN` 只在 Owner/需求表**明确说"待定"**时出现，
   才做扇出并生成 `WAVE_ASSIGNMENT_UNKNOWN`。
   > Phase 2 实现过程中这里出过一次错：最初把"未标注"当 UNKNOWN，导致四颗 Spec 全部扇出成
   > 15 个场景。按 Owner 规则修正为"只排除明确 LATER_WAVE"，扇出只由显式 UNKNOWN 触发。
4. 唯一允许的推断是 `IMPLICIT_SINGLE_SPEC`：某维度只有 1 颗 Spec 时，可排除集合为空，
   因此 Current Wave = 该 Spec。这是对"集合为空"的陈述，不是对未来波次的猜测；已在文档与
   Schema 中记录，Owner 可推翻。
5. 引擎中**不存在任何按波次的比例或固定折减常量**。Current Wave 就是"用更少的 Spec 数量重算一遍"。
   探针 `WV-04` 直接对比：同一 SKU 档，声明波次与否，`base_demand` 与 `TOTAL` 完全相同。
6. `UNKNOWN` 扇出上限 `MAX_WAVE_COMBOS = 32`，超限折叠为两个极值并置 `truncated = true`。

**探针**：`WV-01`…`WV-10`（`WV-10` 确认波次声明**确实会**改变 SKU 答案，即该契约是有承载力的，
不是摆设）

---

## DEC-05 · Quantity Model 修正（取消"全部按每 SKU 费率"）

| 项 | 内容 |
|---|---|
| 状态 | `ADOPTED` |
| Owner 指令 | 不要再将全部表格数值统一建模为每 SKU 费率。至少支持 `PER_SKU_RATE` / `PER_PHASE_FIXED` / `PER_PROJECT_FIXED` / `FORMULA_DRIVEN` / `UNRESOLVED`。MEPA 与 HW PA 按调查证据建模为 `PER_PHASE_FIXED` 候选，保留来源和 Owner Review 状态，不继续使用除以 SKU 后再乘回的伪费率模型 |

**已落地的约束**

1. 逐 cell（Function × Phase，共 42 个）标注 `quantity_model`，由
   `tools/derive_quantity_model.py` **从证据推导**，不手填。当前分布：
   `PER_SKU_RATE 30 · PER_PHASE_FIXED 4 · UNRESOLVED 8`。
2. MEPA、HW PA 的 4 个 cell → `PER_PHASE_FIXED`，取值**直接读绝对量**：
   MEPA 各档均 36/相位；HW PA 2/3/4/4/4。依据：副表行 70/71 跨 SKU 恒定、行 72/73 为整数
   且与"费率×SKU"不一致（后者说明主表那个数是回推出来的）。
3. **禁止伪费率**：`rules_v2.py` 里不出现 `per_sku_rate`、不出现 `ttl_per_phase`，
   探针 `QM-02` 直接对源码做断言。所有值走 `ABSOLUTE_TABLE_READ`。
4. **平坦不等于 PER_PHASE_FIXED**。EMC Test / NV / INTEL 的合计跨 SKU 完全平坦，
   但没有独立证据说明它们是"每相位固定配额"，因此**不升级**，只登记为
   `model_questions`（6 条）交给 Owner，并作为 DEC-06 的嵌入式复用信号来源。
5. 该决策对总数的实际影响被量化在 `artifacts/model/model_delta.md`：只有 4 个 cell 变化
   （MEPA FVT/SIT @2 SKU 各 +4；HW PA FVT/SIT @6 SKU 各 −0.2），
   其余档位与 workbook 完全一致。**没有**大面积改数，也**没有**手改。

**探针**：`QM-01`…`QM-08`、`RT-01`（原始 Main Table 复现 365/417/443.8/474/507 作为回归锚点）

---

## DEC-06 · Baseline Embedded Reuse 保护

| 项 | 内容 |
|---|---|
| 状态 | `ADOPTED` |
| Owner 指令 | 当前费率随 SKU 增加下降、部分 Function 总量反而下降，说明基线可能内含共享或规模效应。新增四种 Reuse 状态；只有能证明未被 Baseline 包含的 `ADDITIONAL_CONFIRMED_REUSE` 可以扣减；无法排除重复扣减时不扣减，只输出 Review Item |

**已落地的约束**

1. `ReuseItem.reuse_status ∈ ALREADY_EMBEDDED_IN_BASELINE / ADDITIONAL_CONFIRMED_REUSE /
   POTENTIAL_REUSE / UNKNOWN_OVERLAP`。
2. 扣减条件（三者同时满足）：状态为 `ADDITIONAL_CONFIRMED_REUSE`
   **且** `proven_not_in_baseline = true` **且** `unit = UNIT`。
3. 每条 Reuse 都必须产出 `decision` + `why`，形成可审计账本 `reuse_ledger`：
   `DEDUCTED / BLOCKED_PROOF_MISSING / BLOCKED_UNTIL_PROVEN /
   NOT_DEDUCTED_ALREADY_EMBEDDED / DISPLAY_ONLY / EXCLUDED_UNIT_MISMATCH`。
4. 新增 `baseline_embedded_sharing` 信号：合计跨 SKU 极差 ≤ 1 **或**增长 ≤ 0 的 Function
   标记 `SUSPECTED`（**15 个 Function**），其 Reuse 策略为 `BLOCK_UNLESS_PROVEN`。
5. PCBA 单位的 Reuse 一律不参与 unit 扣减（`EXCLUDED_UNIT_MISMATCH`）。

**探针**：`RS-01`…`RS-08`、`D01-05`

---

## DEC-07 · D-01 继续有效，并补充比较口径

| 项 | 内容 |
|---|---|
| 状态 | `ADOPTED` |
| Owner 指令 | 所有底层计算保留原始小数，不做业务取整；显示层可统一精度，但不得修改底层计算值；浮点比较和回归校验使用明确容差，不通过改变业务值消除浮点尾差 |

**已落地的约束**

- `rounding = "NONE (D-01)"` 是 Schema `const`，写错即校验失败。
- 比较统一走 `approx(a, b, tol=1e-9)`；容差只服务于比较。
- 输出同时给 `display_precision`（显示）与原始值（存储/导出）。`export.full_precision_present`
  为 Schema `const: true`。
- 443.8 在链路上任何一点都必须是 443.8；4.2 作为竞争证据被原样保留，同时 4.0 作为
  另一来源的采用值并存（两者都不被"四舍五入成一个"）。

**探针**：`D01-01`…`D01-07`

---

## DEC-08 · 当前 MVP 范围：手工输入闭环优先

| 项 | 内容 |
|---|---|
| 状态 | `ADOPTED` |
| Owner 指令 | 优先支持手工输入（五维 + Wave + 可选 Certification 手工值 + 可选额外需求 + 可选 Reuse 信息）；ORI-09 与 ORI-11 暂不阻塞手工输入主链路 |

**已落地的约束**

1. 输入端不出现 SKU 数量字段。
2. 输出必须同时含：SKU 候选匹配、Recommended SKU 或 SKU Range、Current Wave 与 Full Project、
   每候选 SKU 的样机需求、FVT/SIT 明细、Function 明细、Quantity Model、主要理由、
   Owner Review Items、小数结果。
3. 自动读取真实需求表 → 等 ORI-09（2–3 份样本）。
   Existing Build Plan 比较与 SWPA 正式校验 → 等 ORI-11（Build Plan + PPA sample standard 1.0）。
   这两项**不在**本次 MVP 主链路里，也不因缺失而阻塞主链路。
4. 不实现团队管理、权限系统、在线审批、复杂规则管理、企业集成。

---

## 未成为决策的内容（明确划在规则之外）

| 内容 | 处理 | 依据 |
|---|---|---|
| `Pro / LOQ / Y5 / Y7 / X9 / X11 / N1x / Y9` 等产品名 | `NOT_A_RULE`，探针禁止其出现在理由字段 | Phase 1 边界；探针 `PR-01` |
| `case by case` / `to be clarify` / `maybe` / `suggest` / `gap` / `待` | 不确定语料，只登记不生效 | Phase 1 语料扫描 |
| `Option:` 项数量 | 不预置、不默认勾选。K3 明确"remark option 的部分，还没加到样机 data 里面" | 原表 `K3` |
| 匹配维度权重 `DIM_WEIGHT` / 判定权重 `VERDICT_WEIGHT` | Agent 设定值，被 `SR-10` 冻结待 ORI-08 确认；且被 DEC-01 禁止用于打破平局 | ORI-08 |
| 风险预留比例 | 无 Owner 来源，`percent` 默认 0 | ORI-07 |
| ODM 差异化条款（LCFC / HQ / Compal 共 25 行） | 仅记录，不参与算量 | ORI-05 |
