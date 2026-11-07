# 26 — Owner Review Register（交付物 H，完整版）
> **状态（DEC-10 之后）**：本文描述的是 Phase 3a 的 Certification 口径
> （采用主表派生值）。Owner 已决定在 MVP 与团队试用阶段**采用附表总量**，
> 最新口径见 `docs/36_certification_adoption_v4.md`、`docs/37_owner_decision_log_v4.md`、
> `docs/39_totals_v4_and_6sku_review.md`、`docs/40_web_mvp_v4_changes.md`。
> 本文按原文保留，作为阶段记录。


从本任务起，所有需要 Owner 确认的问题集中在本文件。执行过程中未逐项询问 Owner。

- **一次性确认清单（精简版，可直接逐项回答）**：`docs/27_owner_confirmation_checklist_v3.md`
- 本文件是完整技术登记，字段按任务 §22 要求齐全。
- `discovered_in_phase`：`P1` = Phase 1，`P2` = Phase 2，`P3` = 本任务。
- **没有任何一项阻塞手工输入 MVP**（`blocks_manual_mvp` 全为 false，由 `OR-02`、`UI-23` 守护）。

Blocking Level 口径：

| 级别 | 含义 |
|---|---|
| `BLOCKS_EXECUTION` | 停止受影响的计算并给出解释（当前只有输入超出定义域时由引擎自动触发） |
| `BLOCKS_FORMALIZATION` | 规则包不能从 `DRAFT` 升级为 `CONFIRMED`，结果持续显示 `DRAFT_UNCONFIRMED_BY_OWNER` |
| `AFFECTS_ACCURACY` | 结果可用但存在已知不确定性，界面持续提示 |
| `ADVISORY` | 建议确认，不影响数值 |

---

## 汇总表

| ID | 标题 | 发现 | 级别 | 阻塞规则包定版 | 阻塞 MVP |
|---|---|---|---|---|---|
| ORI-01 | Panel 批注 `N*panel` 的正式业务含义 | P1 | `BLOCKS_FORMALIZATION` | 是 | 否 |
| **ORI-02** | **Certification 主表与附表逐格验证结果** | P1→P3 | `BLOCKS_FORMALIZATION` | 是 | 否 |
| ORI-02a | "源费率已验证"的口径（规则层 vs 逐格层） | **P3** | `BLOCKS_FORMALIZATION` | 是 | 否 |
| ORI-02b | J33 是否已被主表费率包含；主表/附表是否描述不同 Source 组合 | **P3** | `AFFECTS_ACCURACY` | 是 | 否 |
| ORI-03 | 波次判据缺失；需求表波次标记列 | P1 | `BLOCKS_FORMALIZATION` | 是 | 否 |
| **ORI-04** | **4 SKU 与 5 SKU 的真实分界条件** | P1 | `BLOCKS_FORMALIZATION` | 是 | 否 |
| ORI-05 | ODM 无结构化规则 + 3 处 Status 未关闭 | P1 | `BLOCKS_FORMALIZATION` | 是 | 否 |
| ORI-06 | Option 项是否启用 / PCBA 单位口径 | P1 | `AFFECTS_ACCURACY` | 是 | 否 |
| ORI-07 | Risk Reserve 比例与适用范围无来源 | P1 | `AFFECTS_ACCURACY` | 是 | 否 |
| ORI-08 | 匹配权重/阈值属 Agent 设定 | P1 | `BLOCKS_FORMALIZATION` | 是 | 否 |
| ORI-09 | 自动读取需求表所需真实样本 | P1 | `ADVISORY` | 是 | 否（已解耦） |
| **ORI-10** | MEPA 是否恒为每 Phase 36；HW PA 何时饱和于 4 | P1 | `BLOCKS_FORMALIZATION` | 是 | 否 |
| ORI-11 | Build Plan 与 PPA sample standard 1.0 | P1 | `ADVISORY` | 是 | 否（已解耦） |
| ORI-12 | 6 条 model questions（EMC Test / NV / INTEL 平坦费率） | P2 | `AFFECTS_ACCURACY` | 是 | 否 |
| ORI-13 | 定义域空洞（超出 2–6 SKU 无规则） | P2 | `AFFECTS_ACCURACY` | 是 | 否 |
| ORI-14 | 缩写与 Green FVT 自相矛盾 | P1 | `ADVISORY` | 是 | 否 |
| **ORI-15** | `Green/SIT/SKU3` 主表值与 1/N 规律不符 | **P3** | `AFFECTS_ACCURACY` | 是 | 否 |
| **ORI-16** | `Safety/FVT/SKU6 = 1.6` 与附表 10 不一致（D-01 相关） | **P3** | `AFFECTS_ACCURACY` | 是 | 否 |
| **ORI-17** | 主表"每 SKU"列实为总量的 1/N 回推（Safety SIT / RF SIT） | **P3** | `AFFECTS_ACCURACY` | 是 | 否 |

统计：19 项（P1 沿用 12 项、P2 沿用 2 项、**P3 新增 5 项**）。
`BLOCKS_EXECUTION` 0 项 · `BLOCKS_FORMALIZATION` 10 项 · `AFFECTS_ACCURACY` 7 项 · `ADVISORY` 4 项。
**`blocks_manual_mvp = true` 的项：0。**

---

## 详细登记

### ORI-01 · Panel 批注 `N*panel` 的正式业务含义

- **business_question**：`D2:H2` 的 `2*panel / 3*panel / 4*panel / 5*panel / 6*panel` 批注，
  与 SKU Definition 行 79–83 的 Panel spec 数量 `[1-2] [1] [2] [2] [2-3]` 冲突时，哪个是业务口径？
- **affected_scope**：SKU 推荐的 Panel 维度；不影响任何数量算法。
- **affected_functions / phases / sku_bands**：无（不进入数量计算）；SKU3–SKU6。
- **current_evidence**：正式计算使用 SKU Definition 行 79–83（Panel Spec Count）。
- **conflicting_evidence**：`E2/F2/G2/H2` 批注给出 3/4/5/6；E2 同时与 CPU 定义冲突（`3*CPU` vs `4-5*CPU`）。
- **current_temporary_handling**：DEC-02 — Panel 按 Spec Count 匹配；批注整体降级
  `UNRESOLVED_COMMENT`，在输出 `unresolved_comments_excluded` 中原样回显，不删除 Panel 维度。
- **impact_if_unresolved**：若批注才是真口径，SKU3–SKU6 的 Panel 维度判定会全部改变，
  SKU 推荐结果随之改变；当前不会导致数量错误，但规则包无法定版。
- **blocking_level** `BLOCKS_FORMALIZATION` · **blocks_manual_mvp** false ·
  **blocks_rule_package_finalization** true
- **owner_needed**：是。
- **recommended_options**：(A) 确认批注仅是"送样 N 份"的注释，与 SKU Definition 无关 → 可直接关闭；
  (B) 确认批注是 Panel 维度的真值 → 需重写 SKU Definition 并重跑 SR 全组探针；
  (C) 批注适用于另一个维度（如送样份数）→ 需要新增一个输入维度并定义其用途。
- **agent_recommendation**：倾向 (A)。反例证据：`panel=1` 时系统给出 3 SKU，
  若 `E2 = 3*panel` 参与匹配则不可能（探针 `PL-04`）。
- **decision_status** `INTERIM_TREATMENT_ADOPTED` · **decision** DEC-02 · **decision_date** 2026-11-04
- **implementation_required_after_decision**：选 (B) 需重跑 `derive → rule pack → 全部探针`；选 (A) 只需把状态改 `CLOSED`。
- **related_tests** `PL-01 PL-02 PL-03 PL-04 PL-05`
- **related_files** `prototype/rules_v3.py`（`UNRESOLVED_COMMENTS`）· `tools/build_rule_pack_v3.py` · `web/assets/app.js`

### ORI-02 · Certification 主表与附表逐格验证结果

- **business_question**：40 格中有 7 格不满足 `附表 = 主表单 SKU 数量 × SKU 数`。
  这些格上，**主表值与附表值哪个是业务真值**？如果不是同一事实，各自适用什么条件？
- **affected_scope**：Certification 的 3 个 Function（Green / Safety / RF Certification），
  项目总量中 Certification 所占部分。
- **affected_functions** `F_GREEN(FVT) F_SAFETY(FVT) F_RF_CERTIFICATION(SIT)`；
  **affected_phases** FVT、SIT；**affected_sku_bands** SKU3、SKU6、SKU2–SKU6（RF 全档）。
- **current_evidence**（引擎当前采用，主表口径）：

  | 格 | 主表 /SKU | 主表×SKU（采用） | 附表 | delta | 源行 |
  |---|---:|---:|---:|---:|---|
  | Green/SIT/SKU3 | 3.0 | 9.0 | 6.0 | −3.0 | 30 / 56 |
  | Safety/FVT/SKU6 | 1.6 | 9.6 | 10.0 | +0.4 | 31 / 57 |
  | RF/SIT/SKU2 | 7.5 | 15.0 | 8.0 | −7.0 | 34 / 60 |
  | RF/SIT/SKU3 | 5.0 | 15.0 | 9.0 | −6.0 | 34 / 60 |
  | RF/SIT/SKU4 | 3.75 | 15.0 | 10.0 | −5.0 | 34 / 60 |
  | RF/SIT/SKU5 | 3.0 | 15.0 | 10.0 | −5.0 | 34 / 60 |
  | RF/SIT/SKU6 | 2.5 | 15.0 | 10.0 | −5.0 | 34 / 60 |

- **conflicting_evidence**：附表块自身完全自洽（TTL 行 61/62 = 成分行之和），
  因此两边都是有意数字，不存在"附表算错了"的解释空间。
- **current_temporary_handling**：按 Owner §4 采用主表值；逐格输出 `MISMATCH` + 原值 + delta；
  进入 Register；规则包保持 `DRAFT_PENDING_OWNER`；高级选项允许对 MISMATCH 格输入本次采用值。
- **impact_if_unresolved**：若附表才是真值，项目总量将按下表减少（**这是本 Register 中金额最大的一项**）：

  | SKU 档 | 当前总量 | 若以附表为准 | 差 |
  |---:|---:|---:|---:|
  | 2 | 373.0 | 366.0 | −7.0 |
  | 3 | 417.0 | 408.0 | −9.0 |
  | 4 | 443.8 | 438.8 | −5.0 |
  | 5 | 474.0 | 469.0 | −5.0 |
  | 6 | 506.6 | 501.6 | −5.0 |

- **blocking_level** `BLOCKS_FORMALIZATION` · **blocks_manual_mvp** false · 定版阻塞 **是**
- **owner_needed**：是（**最高优先**）。
- **recommended_options**：
  (A) 主表为准 → ORI-02 直接 `RESOLVED`，7 格差异归档为"附表过时"，规则包可定版；
  (B) 附表为准 → 需把 3 个格改为绝对量并说明其 Quantity Model（RF 那 5 格会像 MEPA 一样
      变成 `PER_PHASE_FIXED`，因为附表 8/9/10/10/10 不随 `rate×SKU` 变化）；
  (C) 按条件区分（如 Source 组合 / 项目类别）→ 需要给出判据，MVP 需新增一个输入维度；
  (D) 暂时维持现状（采用主表 + 持续提示）→ 规则包继续不能定版。
- **agent_recommendation**：请优先在 (A)/(B) 间做二元选择。附带证据支持先查 (C)：
  附表 RF SIT 的 8–10 **低于** J33 自述参考场景（2 天线 + 2 WLAN）的下限 11，
  说明附表与主表可能本来就不是同一个 Source 组合下的数（见 ORI-02b）。
- **decision_status** **`PARTIALLY_RESOLVED`**（本任务由 `INTERIM_TREATMENT_ADOPTED` 推进）
- **decision** DEC-09（模型层）· **decision_date** 2026-11-04 · 源数据层待回答
- **implementation_required_after_decision**：选 (A) → 7 格 verification 归档、
  `owner_review_cells` 由 7 降到 4（MEPA/HW PA 仍待 ORI-10）；选 (B)/(C) → 需重跑
  `verify_certification → build_quantity_model_v3 → build_rule_pack_v3 → 全部探针`，
  总量表与 model_delta 全部更新。
- **related_tests** `CT-V2-01 CT-V2-02 CT-V2-03 CT-V2-04 CT-V2-05 CT-V2-09 CT-V2-10 CT-V2-11`，
  parity `W-08 W-09 W-10 W-11 W-12`，Web `UI-08 UI-09 UI-10`
- **related_files** `tools/verify_certification.py` · `artifacts/model/certification_verification.json` ·
  `tools/build_quantity_model_v3.py` · `prototype/rules_v3.py` · `web/assets/core.js`

### ORI-02a · "Certification 源费率已验证"的口径（本任务新登记）

- **business_question**：任务 §8 要求输出单值须满足"Certification 源费率已验证"。
  这里的"已验证"指**计算规则已验证**，还是**每格附表校验都通过**？
- **affected_scope**：Green / Safety / RF Certification 三个 Function 能否输出单值。
- **current_evidence**：本任务实现为"规则层已验证 → 输出单值 + 逐格披露验证状态 + 允许本次临时采用值"。
- **conflicting_evidence**：若按"逐格附表校验都通过"解释，则 3 个含 MISMATCH 的 Function
  永久不能输出单值，与任务 §24 `CT-V2-03`（单一 SKU 时 Certification 输出单值）直接冲突。
- **current_temporary_handling**：采用规则层解释；`CT-V2-11` 保证不一致一定被登记并显示。
- **impact_if_unresolved**：影响结果形态（单值 vs 需确认），不影响数值本身。
- **blocking_level** `BLOCKS_FORMALIZATION` · **blocks_manual_mvp** false
- **recommended_options**：(A) 确认规则层口径（当前实现）；(B) 改为逐格口径 → 需同步修订 §24
  与 `CT-V2-03`，并让这 3 个 Function 输出"请确认"而非单值。
- **agent_recommendation**：(A)。理由：单值 + 显著差异披露，比人为制造区间更可用，
  且区间本身仍会被要求折叠成一个数。
- **decision_status** `OPEN` · **related_tests** `CT-V2-03 CT-V2-11` · **related_files** `docs/22 §4.1`

### ORI-02b · J33 是否已被主表费率包含（本任务新登记）

- **business_question**：J33 描述的 SRRC / CE / FCC / 印尼 / Mexico / 资安 整机需求，
  是否已经包含在主表 RF 的 15 里？主表 15 与附表 8–10 是否描述不同 Source 组合？
- **affected_scope**：仅 RF Certification（FVT 恒 0，SIT 见上）。
- **current_evidence**：J33 自述 `this data for 2 antenna source +2 wlan source refrence`；
  按其自身两种读法给出 **11 … 27** 区间（下限：FCC 走 C1PC 模组不需整机；上限：FCC = intel_wlan×天线×4）。
  主表 15 落在区间内；附表 8–10 **低于下限 11**。
- **conflicting_evidence**：无法从工作簿证明 J33 已被主表包含（无公式引用天线/WLAN 数）。
- **current_temporary_handling**：J33 登记为 `BREAKDOWN_EVIDENCE` / `DECLARED_NOT_GENERALIZED`，
  `additive = false`，MVP 不新增天线 / WLAN 输入。
- **impact_if_unresolved**：若 J33 未被包含而只是被遗漏，RF Certification 可能被低估；
  若被包含而再叠加，则重复计入（风险 HIGH）。当前选择不叠加，属保守侧。
- **blocking_level** `AFFECTS_ACCURACY` · **blocks_manual_mvp** false
- **recommended_options**：(A) 确认 J33 只是构成说明，主表 15 已包含 → 归档；
  (B) 确认 J33 是独立补充 → 需要定义叠加规则（会改变总量，须重新评审）；
  (C) 确认附表对应单一 Source 组合、主表对应 2+2 组合 → 归入 ORI-02 (C)。
- **agent_recommendation**：(A) 或 (C)。不建议 (B)：当前无任何判据可确定叠加条件。
- **decision_status** `DECLARED_NOT_GENERALIZED` · **decision_date** 2026-11-04
- **related_tests** `JG-01 JG-02 JG-03 JG-04 JG-05 CT-V2-08`
- **related_files** `artifacts/model/certification_verification.json#j33_investigation`

### ORI-03 · 波次判据缺失

- **business_question**：需求表用哪一列/哪个标记表示第二波？是否接受"只有 1 个 Spec 时视为
  `IMPLICIT_SINGLE_SPEC`"这一口径？
- **affected_scope**：Current Wave 情景的 Spec 计数。
- **current_evidence**：源表无波次列；引擎只排除**明确标记** `LATER_WAVE` 的 Spec；
  未标记的 Spec 计入当前波并产生 `WAVE_ASSIGNMENT_NOT_PROVIDED`。
- **current_temporary_handling**：DEC-04 + 界面三选项（`CURRENT_WAVE/LATER_WAVE/NO_EXPLICIT_ASSIGNMENT`）。
- **impact_if_unresolved**：Current Wave 与 Full Project 目前多半相同（没人声明波次时）；
  一旦实际存在第二波而未声明，Current Wave 会被高估。**注意：波次不产生任何比例或固定量折减。**
- **blocking_level** `BLOCKS_FORMALIZATION` · **blocks_manual_mvp** false
- **recommended_options**：(A) 需求表新增波次列（推荐）；(B) 由使用者每次手选（MVP 已支持）；
  (C) 确认不存在第二波 → 可移除该输入。
- **agent_recommendation**：短期 (B)，中期 (A)。
- **decision_status** `INTERIM_TREATMENT_ADOPTED` · **decision** DEC-04
- **related_tests** `WV-01..WV-13`，parity `W-04 W-05 W-07 W-21 W-22`，Web `UI-06 UI-07 UI-12c`
- **related_files** `prototype/rules_v3.py` · `schema/input.schema.json#specWave` · `web/assets/app.js`

### ORI-04 · 4 SKU 与 5 SKU 的真实分界条件 ⭐

- **business_question**：什么条件下应判 4 SKU、什么条件下应判 5 SKU？能否提供真实 4 SKU 与
  5 SKU 项目各若干，以及正式分界规则？
- **affected_scope**：SKU 推荐结果形态（单值 vs `4–5 SKU` 范围），以及随 SKU 变化的全部数量。
- **current_evidence**：SKU5 定义是 SKU4 定义的**严格子集**；在 405 组真实合理的
  (CPU,GPU,Panel,SSD,Mem) 组合中，**5 SKU 作为唯一最优解出现的次数 = 0**。
  因此 5 SKU 只能以 `4–5 SKU` 范围出现。
- **conflicting_evidence**：无替代规则；这是定义本身的结构性缺口。
- **current_temporary_handling**：DEC-01 — `state=RANGE`、`recommended_sku=null`、
  `preferred_sku=NOT_ESTABLISHED`，4 与 5 两档都完整计价，页面并列、不预选、不暗示。
  `SR-09` 探针**永久按设计 FAIL**，`EF-01` 探针保证 Expected Failure 集合恒等于 `['SR-09']`。
- **impact_if_unresolved**：4–5 SKU 区间的样机需求差 **474.0 − 443.8 = 29.2 台**（本 Register 第二金额项）。
- **blocking_level** `BLOCKS_FORMALIZATION` · **blocks_manual_mvp** false
- **owner_needed**：是（高价值）。
- **recommended_options**：(A) 提供真实 4/5 SKU 样本 + 正式分界条件 → 可关闭并让 `SR-09` 转绿；
  (B) 确认 5 SKU 不是独立档位（应从定义中移除或合并）→ `SR-09` 需按新口径重写（不是删除）；
  (C) 维持范围输出 → 每次都要人工在 4 与 5 之间选，工具不代选。
- **agent_recommendation**：(A)。只有真实样本能证明 SKU5 何时独立成立；
  任何权重调整都只是掩盖问题，且被 `SR-10` 明确禁止。
- **decision_status** `OPEN`（仅 DEC-01 临时口径）· **decision** DEC-01
- **related_tests** `SR-01 SR-02 SR-03 SR-04 SR-08 SR-09(EXPECTED FAIL) SR-10 EF-01 CT-V2-04 CT-V2-05`，
  Web `UI-02 UI-04 UI-10 UI-16`
- **related_files** `artifacts/model/baseline_v1.json#sku_definition` ·
  `prototype/rules_v3.py:match_sku` · `docs/15_sku_recommendation_contract.md`

### ORI-05 · ODM 无结构化规则 + 3 处 Status 未关闭

- **business_question**：EMC Test `待LCFC update`、MEPA `HQ/Compal: to be clarify`、
  HW PA `HQ gap比较大` 这三处未关闭状态，是否影响数量口径？ODM 是否改变任何数量？
- **current_evidence**：源表没有任何 `ODM → 数量` 映射；工作簿公式不按 ODM 分支。
- **current_temporary_handling**：ODM 仅记录、不参与计算（`input.schema.json.odm` 注明）。
- **impact_if_unresolved**：若某些 Function 实际按 ODM 取值，当前结果对部分 ODM 偏差未知。
- **blocking_level** `BLOCKS_FORMALIZATION` · **blocks_manual_mvp** false
- **recommended_options**：(A) 确认 ODM 不影响数量 → 归档；(B) 提供 ODM 差异表 → 新增规则维度。
- **agent_recommendation**：(A)，除非业务确实按 ODM 分账。
- **decision_status** `OPEN` · **related_tests** `PR-01`（产品名/ODM 不作判据）
- **related_files** `artifacts/model/baseline_v1.json#conflicts`

### ORI-06 · Option 项是否启用 / PCBA 单位口径

- **business_question**：EPEAT、Smart AMP、UL golden、Flicker Free 等 Option 是否计入基线？
  PCBA 计数单位与台数如何换算？
- **current_temporary_handling**：不预置任何 Option 效果；`PCBA` 与 `UNIT` 严格隔离，
  PCBA 永不加入台数、不产生风险预留（`D01-05`、`RS-08`）。
- **impact_if_unresolved**：启用未启用的 Option 会让 FVT/SIT 各偏若干台（EPEAT 备注为 5 unit）。
- **blocking_level** `AFFECTS_ACCURACY` · **blocks_manual_mvp** false
- **recommended_options**：(A) 确认 Option 一律不预置，由使用者在 Additional Requirement 手输
  （MVP 已支持）；(B) 给出 Option → 数量的正式表。
- **decision_status** `OPEN` · **related_tests** `D01-05 D01-06 D01-07 RS-08`

### ORI-07 · Risk Reserve 比例与适用范围

- **business_question**：源表有 `Risk Reserve` 行但**没有任何百分比**。是否有正式比例？
  适用于哪些 Function？
- **current_temporary_handling**：默认 0%，由使用者显式填写；风险预留只按 baseline demand 计，
  **不因用户额外添加的需求而增加**（`D01-07`）。
- **impact_if_unresolved**：确认 5% 时，4 SKU 会多出 22.19 台（`443.8 × 0.05`）。
- **blocking_level** `AFFECTS_ACCURACY` · **blocks_manual_mvp** false
- **recommended_options**：(A) 0%（现状）；(B) 给正式百分比 + 适用域。
- **agent_recommendation**：保持 0% 直到 Owner 给出正式值，绝不猜测。
- **decision_status** `OPEN` · **related_tests** `D01-02 D01-07`

### ORI-08 · 匹配权重 / 阈值属 Agent 设定

- **business_question**：`gpu 1.6 / ssd 1.4 / mem 1.4 / cpu 1.0 / panel 1.0` 与
  `PARTIAL_MATCH 0.4` 是否符业务直觉？`PARTIAL` 的"差 1 档"判定是否成立？
- **current_temporary_handling**：权重仅用于**排序**；DEC-01 禁止用它制造单一答案；
  `SR-10` 把权重值冻结成断言，改动会被立即发现。
- **impact_if_unresolved**：影响 SKU 推荐与 tie 集合（包括 ORI-04 的 4–5 并列）。
- **blocking_level** `BLOCKS_FORMALIZATION` · **blocks_manual_mvp** false
- **recommended_options**：(A) 用真实项目样本反推权重；(B) 改为规则式（先硬条件后打分）。
- **decision_status** `OPEN` · **related_tests** `SR-05 SR-06 SR-10`

### ORI-09 · 自动读取需求表所需的真实样本

- **business_question**：需要 2–3 份真实（或脱敏）需求表才能定义自动解析。能否提供？
- **current_temporary_handling**：MVP 只做手工输入（DEC-08 已解耦，不阻塞主链路）。
- **blocking_level** `ADVISORY` · **blocks_manual_mvp** **false**
- **decision_status** `ANSWERED_AWAITING_SAMPLE` · **decision** DEC-08

### ORI-10 · MEPA 是否恒为每 Phase 36；HW PA 何时饱和于 4 ⭐

- **business_question**：MEPA 附表各行恒为 36，是否表示各 SKU 档位恒为每 Phase 36？
  HW PA 附表 `2,3,4,4,4` 是否表示 4 SKU 起饱和于 4？
- **affected_scope**：MEPA FVT/SIT、HW PA FVT/SIT 共 4 格（当前唯一与 Workbook 总量不同的格）。
- **current_evidence**：附表行 70/71 恒 36；主表在 SKU2 给 `16×2 = 32`。附表 72/73 为整数
  `2,3,4,4,4`；主表在 SKU6 给 `0.7×6 = 4.2`（非整数）。
- **current_temporary_handling**：`PER_PHASE_FIXED` 候选模型，前端显示 **临时采用**；
  不使用"除以 SKU 再乘回"的伪费率（`QM-02` 从源码层面守护）。
- **impact_if_unresolved**：`+8.0` @2 SKU、`−0.4` @6 SKU（Phase 2 起即如此，本任务未改）。
- **blocking_level** `BLOCKS_FORMALIZATION` · **blocks_manual_mvp** false
- **recommended_options**：(A) 确认附表绝对量正确 → 转 `CONFIRMED`，同时承认 MEPA 不随 SKU 变化；
  (B) 确认主表费率正确 → 回退 `PER_SKU_RATE`（会撤销 DEC-05 的这两格）；
  (C) MEPA 取 (A)、HW PA 取饱和模型 → 需给出饱和点。
- **agent_recommendation**：(C)。整数附表值（2/3/4/4/4、36）比 `4.2` 这类回推小数更像业务原意。
- **decision_status** `INTERIM_TREATMENT_ADOPTED` · **decision** DEC-05
- **related_tests** `QM-01 QM-03 QM-04 QM-07 LG-02`，parity `W-13`，Web `UI-13`
- **related_files** `tools/build_quantity_model_v3.py` · `artifacts/model/model_delta.md`

### ORI-11 · Build Plan 与 PPA sample standard 1.0

- **business_question**：能否提供现有 Build Plan 与 PPA sample standard 1.0 样本？
- **current_temporary_handling**：不做 Build Plan 差异比较，不做 SWPA 正式校验（DEC-08 解耦）。
- **blocking_level** `ADVISORY` · **blocks_manual_mvp** **false**
- **decision_status** `ANSWERED_AWAITING_SAMPLE` · **decision** DEC-08

### ORI-12 · 6 条 model questions（EMC Test / NV / INTEL）

- **business_question**：这 3 个 Function（FVT+SIT 共 6 格）的 derived total 在 SKU2–6 上完全平坦，
  但没有独立证据说明它是"每 Phase 固定量"。是固定量，还是共享效应已经内含在费率里？
- **current_temporary_handling**：保持 `PER_SKU_RATE`（与 Workbook 一致），登记 model question；
  **不因数值平坦就升级为固定量**（`QM-05`）。同时它们进入 DEC-06 内含共享信号
  （15 个 Function 被标 `SUSPECTED`，其 Reuse 默认 `BLOCK_UNLESS_PROVEN`）。
- **impact_if_unresolved**：若其实是固定量，高 SKU 档会系统性偏高；当前选择与 Workbook 一致的一侧。
- **blocking_level** `AFFECTS_ACCURACY` · **blocks_manual_mvp** false
- **decision_status** `OPEN` · **related_tests** `QM-05 RS-07`

### ORI-13 · 定义域空洞

- **business_question**：输入落在 2–6 SKU 支持域之外（例如 cpu=9）时应如何处理？
- **current_temporary_handling**：`OUT_OF_DOMAIN` 拒绝态 —— 停止**该情景**的计算并解释，不外推；
  另一情景照常输出。这是当前唯一实际存在的 `BLOCKS_EXECUTION` 语义。
- **blocking_level** `AFFECTS_ACCURACY`（规则本身缺失时才是 `BLOCKS_EXECUTION`）
- **blocks_manual_mvp** false · **decision_status** `INTERIM_TREATMENT_ADOPTED`
- **related_tests** `SR-08 OR-03`，parity `W-17`，Web `UI-24`

### ORI-14 · 缩写与 Green FVT 自相矛盾

- **business_question**：`CS / ODM / TTL / PA / SWPA / MEPA / PA` 等缩写的正式定义？
  Green FVT 主表为 0 而备注写 `FVT for RD 内测, leverage safety`，是否表示该格应 > 0？
- **current_temporary_handling**：以数值为准，备注作为证据保留；术语表见 `docs/02`。
- **blocking_level** `ADVISORY` · **blocks_manual_mvp** false · **decision_status** `OPEN`

### ORI-15 · `Green/SIT/SKU3` 主表值与 1/N 规律不符（本任务新登记）

- **business_question**：Green SIT 主表每 SKU 数量为 `3, 3, 1.5, 1.2, 1`；除 SKU3 外都严格等于 `6/N`。
  SKU3 的 `3.0` 是笔误（应为 `2.0`），还是刻意表示 3 SKU 项目需要更多 Green 认证机？
- **current_evidence**：`3.0 × 3 = 9`，而附表行 56 恒为 6；相邻档 `1.5×4=6`、`1.2×5=6`。
- **conflicting_evidence**：附表块自洽（TTL 行 = 成分和），不能据此判定附表错误。
- **current_temporary_handling**：采用主表 9.0，登记 MISMATCH，delta −3.0；高级选项允许本次采用值。
- **impact_if_unresolved**：3 SKU 档总量 417.0 vs 408.0，差 **9.0 台**。
- **blocking_level** `AFFECTS_ACCURACY` · **blocks_manual_mvp** false
- **recommended_options**：(A) 确认主表 3.0 有效；(B) 更正为 2.0（则 ORI-02 该格变 VERIFIED）。
- **agent_recommendation**：先向源表作者确认是否笔误。这是 7 格里最像单点录入错误的一个。
- **decision_status** `OPEN` · **related_tests** `CT-V2-01 CT-V2-11` · **related_files**
  `artifacts/model/certification_verification.json`（row 30 / 56）

### ORI-16 · `Safety/FVT/SKU6 = 1.6` 与附表 10 不一致（本任务新登记）

- **business_question**：Safety FVT 在 6 SKU 应取 `9.6`（主表 `1.6×6`）还是 `10`（附表）？
- **current_evidence**：`1.6` 恰为 `9.6/6` 的回推值；主表 Safety FVT 其余档为 `5,3,2.5,2` → `10,9,10,10`，
  即前四档总量都是整数 10/9/10/10，第六档突然变成 9.6。
- **conflicting_evidence**：附表行 57 在 SKU4/5/6 都是 10。
- **current_temporary_handling**：采用 9.6（D-01：不因"看起来该是整数"而改成 10）。
- **impact_if_unresolved**：6 SKU 总量 506.6 vs 507.0，差 **0.4 台**。
- **blocking_level** `AFFECTS_ACCURACY` · **blocks_manual_mvp** false
- **recommended_options**：(A) 保留 9.6 小数；(B) 更正为 10。
- **agent_recommendation**：(A) 维持 D-01 口径，除非 Owner 明确 10 才是业务值。
  注意：不得为了消除浮点尾差而修改业务数值（任务 §20）。
- **decision_status** `OPEN` · **related_tests** `CT-V2-01 CT-V2-11 D01-01`

### ORI-17 · 主表"每 SKU"列实为总量的 1/N 回推（本任务新登记）

- **business_question**：`Safety/SIT`（`3,2,1.5,1.2,1` → 恒 6）与
  `RF Certification/SIT`（`7.5,5,3.75,3,2.5` → 恒 15）两格，主表的"每 SKU 数量"随 SKU 增大而
  严格 1/N 递减。这与 Owner 语义"主表 = 单个 SKU 所需的样机数量"字面不符：
  实际语义更像"该项目该 Phase 的认证总量，再按 SKU 数摊分"。请确认真实语义。
- **current_evidence**：`rate_shape = BACK_DERIVED_FROM_FLAT_TOTAL`（自动判定，未人工标注）。
- **conflicting_evidence**：EMC 是真正的常数率（`1,1,1,1,1` → `2,3,4,5,6`），说明同一张表里
  两种语义并存。
- **current_temporary_handling**：按 Owner 指令执行 `每 SKU 数量 × SKU 数`。
  对这两格，结果等于那个恒定总量（6 与 15），**数值上无歧义**，只是解释不同。
- **impact_if_unresolved**：本任务内无数值影响。但若未来出现"某档主表缺失"的情形，
  两种语义会给出不同补全结果，届时会突然变成实际差异。
- **blocking_level** `AFFECTS_ACCURACY` · **blocks_manual_mvp** false
- **recommended_options**：(A) 确认"表内数值就是单 SKU 用量，1/N 只是作者填表习惯"→ 归档；
  (B) 确认这两格语义是"Phase 总量" → 应改标 `PER_PHASE_FIXED`（与 MEPA 同处理，数值不变）。
- **agent_recommendation**：(B) 在模型标注上更诚实，且不改任何数字；但请 Owner 确认，
  因为这会改变"新增 SKU 档位时如何外推"的行为。
- **decision_status** `OPEN` · **related_tests** `CT-V2-01 CT-V2-06 QM-02`
- **related_files** `artifacts/model/certification_verification.json#main_table_rate_shape`

---

## 与输出中 ORI kind 的对应关系

| 引擎输出的 `kind` | Register ID | blocking_level | blocks_manual_mvp |
|---|---|---|---|
| `SKU_TIE_NOT_RESOLVABLE` | ORI-04 | BLOCKS_FORMALIZATION | false |
| `WAVE_ASSIGNMENT_NOT_PROVIDED` / `_UNKNOWN` | ORI-03 | AFFECTS_ACCURACY | false |
| `OUT_OF_DOMAIN_INPUT` | ORI-13 | BLOCKS_EXECUTION | false（只停该情景） |
| `CERTIFICATION_SOURCE_VALIDATION_MISMATCH` | ORI-02 / ORI-15 / ORI-16 | BLOCKS_FORMALIZATION | false |
| `CERTIFICATION_APPENDIX_VALIDATION_INCOMPLETE` | ORI-02（+ ORI-02a） | BLOCKS_FORMALIZATION | false |
| `CERTIFICATION_BREAKDOWN_EVIDENCE_NOT_GENERALIZED` | ORI-02b | ADVISORY | false |
| `REUSE_PROOF_MISSING` / `REUSE_OVERLAP_UNPROVEN` | DEC-06 执行结果 | AFFECTS_ACCURACY | false |

`temp` 模型（MEPA / HW PA）与 6 条 model question 不产生运行期 ORI kind，
而是通过 `row.is_temporary_model = true` 与界面 **临时采用** 状态呈现（ORI-10、ORI-12）。
