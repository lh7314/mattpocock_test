# 38 — Owner Review Register v4（交付物：Owner Review Register，完整版）

规则包中的机器版本：`artifacts/model/rule_pack_v4.json → open_owner_review_items`
（19 条唯一条目 + 影响标签统计），探针 `ST-02` 校验本文、规则包与引擎输出一一对应。

## 计数口径（本文与探针共用）

| 计数 | 数量 | 说明 |
|---|---:|---|
| **唯一 Owner 问题（ORI）** | **19** | 一个业务问题一条，跨情景重复不另开条目 |
| 影响标签 `BLOCKS_FORMALIZATION` | 6 | 阻止规则包定稿，不阻止 MVP |
| 影响标签 `AFFECTS_ACCURACY` | 9 | 影响准确度，可先用临时处理 |
| 影响标签 `ADVISORY` | 4 | 提示性，不影响当前计算 |
| 影响标签合计 | **19** | **每条问题只有一个主影响标签**，因此合计等于唯一问题数 |
| 阻止执行（`BLOCKS_EXECUTION`） | 0 | 只有 `OUT_OF_DOMAIN` 输入会停**该情景**，且不写入 Register |
| 阻止手动 MVP | **0** | 19 条全部 `blocks_manual_mvp = false` |

> 同一问题上的第二个影响标签（例如 ORI-13 既是准确度问题、其输入错误又会停单个情景）
> 在本文该条目正文里说明，**不再新建 ORI**。这是上一版报告把"标签数"当"问题数"的修正。

## 汇总表

| ID | 问题 | 影响标签 | 阻止定稿 | 阻止 MVP |
|---|---|---|---|---|
| ORI-01 | Panel 批注 `N*panel` 的正式业务含义 | `BLOCKS_FORMALIZATION` | 是 | 否 |
| ORI-02 | Certification 主表派生值与附表的 7 处差异原因 | `BLOCKS_FORMALIZATION` | 是 | 否 |
| ORI-02a | 「源费率已验证」的口径（DEC-10 后不再是阻塞项） | `ADVISORY` | 否 | 否 |
| ORI-02b | J33 是否已被采用值包含；两列是否描述不同 Source 组合 | `AFFECTS_ACCURACY` | 否 | 否 |
| ORI-03 | 波次判据缺失；需求表波次标记列 | `AFFECTS_ACCURACY` | 否 | 否 |
| ORI-04 | 4 SKU 与 5 SKU 的真实分界条件 ⭐ | `BLOCKS_FORMALIZATION` | 是 | 否 |
| ORI-05 | ODM 无结构化规则 + 3 处 Status 未关闭 | `BLOCKS_FORMALIZATION` | 是 | 否 |
| ORI-06 | Option 项是否启用 / PCBA 单位口径 | `AFFECTS_ACCURACY` | 否 | 否 |
| ORI-07 | Risk Reserve 比例与适用范围无来源 | `AFFECTS_ACCURACY` | 否 | 否 |
| ORI-08 | 匹配权重 / 阈值属 Agent 设定 | `BLOCKS_FORMALIZATION` | 是 | 否 |
| ORI-09 | 自动读取需求表所需真实样本（已与 MVP 解耦） | `ADVISORY` | 否 | 否（已解耦） |
| ORI-10 | MEPA 是否恒为每 Phase 36；HW PA 何时饱和于 4 ⭐ | `BLOCKS_FORMALIZATION` | 是 | 否 |
| ORI-11 | Build Plan 与 PPA sample standard 1.0（已与 MVP 解耦） | `ADVISORY` | 否 | 否（已解耦） |
| ORI-12 | 6 条 model questions（EMC Test / NV / INTEL 平坦费率） | `AFFECTS_ACCURACY` | 否 | 否 |
| ORI-13 | 定义域空洞：超出 2–6 SKU 无规则 | `AFFECTS_ACCURACY` | 否 | 否（仅停该情景） |
| ORI-14 | 缩写与 Green FVT 自相矛盾 | `ADVISORY` | 否 | 否 |
| ORI-15 | `Green/SIT/SKU3` 主表值与 1/N 规律不符 | `AFFECTS_ACCURACY` | 否 | 否 |
| ORI-16 | `Safety/FVT/SKU6` 主表 9.6 与附表 10 不一致 | `AFFECTS_ACCURACY` | 否 | 否 |
| ORI-17 | 主表「每 SKU」列实为总量的 1/N 回推 | `AFFECTS_ACCURACY` | 否 | 否 |

---

## 详细登记

### ORI-01 · Panel 批注 `N*panel` 的正式业务含义

- **business_question**：D2:H2 的 `N*panel` 是否参与 SKU 判定？
- **current_evidence**：SKU Definition 行 79–84 只用 Panel Spec Count。
- **current_temporary_handling**：批注标 `UNRESOLVED_COMMENT`，永不参与匹配或算术。
- **impact_if_unresolved**：若批注才是正式判据，SKU 判定矩阵需重写。
- **blocking_level** `BLOCKS_FORMALIZATION` · **blocks_manual_mvp** false
- **recommended_options**：(A) 确认批注仅为备注；(B) 给出正式判据。
- **decision_status** `OPEN` · **related_tests** `PL-01 PL-02 PL-03 PL-04 PL-05`

### ORI-02 · Certification 主表派生值与附表的 7 处差异原因

- **business_question**：40 格里 7 格 `主表单 SKU 数量 × SKU 数 ≠ 附表总量`
  （见 `docs/36_certification_adoption_v4.md` 表 B）。差异是录入误差，
  还是两列本来描述不同东西？
- **current_evidence**：附表块自洽（成分和 = TTL 行）；主表 `Safety/SIT`、`RF/SIT`
  两格的主表列呈严格 1/N 递减（`BACK_DERIVED_FROM_FLAT_TOTAL`）。
- **current_temporary_handling**：**DEC-10 采用附表值**；主表值与派生值原样保留为审计，
  差值逐格上报，不修改源文件、不取整。
- **impact_if_uncovered**：7 格合计数额见 `docs/39_totals_v4_and_6sku_review.md`；
  对 SKU2–SKU6 总量影响 −7 / −9 / −5 / −5 / −4.6 台。
- **blocking_level** `BLOCKS_FORMALIZATION` · **blocks_manual_mvp** false
- **recommended_options**：(A) 确认附表为正式业务量（= DEC-10 已采用），并要求源表作者
  修正主表列；(B) 确认主表列正确 → 需要重新决定采用值；(C) 两列描述不同 Source 组合
  → 需要给出选择判据。
- **agent_recommendation**：把 DEC-10 的采用范围固化为规则前，请源表作者确认 7 格；
  最像单点录入错误的是 `Green/SIT/SKU3`。
- **decision_status** `PARTIALLY_RESOLVED` · **related_tests**
  `CT-V2-01 CT-V2-11 DA-01 DA-02 DA-12 EX-05`

### ORI-02a · 「Certification 源费率已验证」的口径（DEC-10 后降级）

- **变化**：Phase 3a 里"已验证"到底指规则层还是逐格层，会影响采用哪一个数；
  DEC-10 直接指定采用附表值后，这个口径问题**不再影响当前计算**。
- **仍保留的原因**：报告与界面里还会读到"主表核对 33 一致 / 7 不一致"这句话，
  口径需要 Owner 认可措辞。
- **blocking_level** `ADVISORY`（原 `BLOCKS_FORMALIZATION`，本轮下调并在此说明，
  **不新开 ORI**）· **blocks_manual_mvp** false
- **decision_status** `ANSWERED_AWAITING_SAMPLE` · **related_tests** `DA-03 CT-V2-01`

### ORI-02b · J33 是否已被采用值包含；两列是否描述不同 Source 组合

- **business_question**：J33 自述 2 天线源 + 2 WLAN 卡，可算出 11–27 的区间；
  主表派生 15 在区间内，**附表采用值 8–10 低于下限**。两列是否描述不同组合？
- **current_temporary_handling**：J33 仅作解释证据，计入 0 次；MVP 不采集天线 / WLAN。
- **impact_if_unresolved**：本轮无数值影响；若日后要求按 Source 组合建模才会显性化。
- **blocking_level** `AFFECTS_ACCURACY` · **blocks_manual_mvp** false
- **decision_status** `DECLARED_NOT_GENERALIZED` · **related_tests** `JG-01…JG-05 DA-04`

### ORI-03 · 波次判据缺失

- **business_question**：哪个 Spec 属于后续波次，由谁、在哪里判定？
- **current_temporary_handling**：未特别指定 = `NO_EXPLICIT_ASSIGNMENT` → 计入当前波次，
  Current Wave 与 Full Project 相同；只有用户显式标记 `LATER_WAVE` 才排除。
- **impact_if_unresolved**：需求表波次标记列出现后，两情景才可能真正分叉。
- **blocking_level** `AFFECTS_ACCURACY` · **blocks_manual_mvp** false
- **decision_status** `OPEN` · **related_tests** `WV-01…WV-13`

### ORI-04 · 4 SKU 与 5 SKU 的真实分界条件 ⭐

- **business_question**：什么样的输入判 4 SKU、什么判 5 SKU？
- **current_evidence**：4 SKU 定义是 5 SKU 定义的子集 → 结构上 5 SKU 永远不是唯一解；
  405 组真实组合中 5 SKU 唯一命中 0 次（探针 SR-09 因此**故意保持失败**）。
- **current_temporary_handling**：输出 `RANGE = 4–5`，`recommended_sku = null`，
  `preferred_sku = NOT_ESTABLISHED`，两档分别完整计价（DEC-10 后 cert 分别为 36.0 / 37.0）。
- **impact_if_unresolved**：4–5 范围两档差 **29.2 台**（Phase 3a 口径）；
  DEC-10 后为 438.8 与 469.0，差 **30.2 台**。
- **blocking_level** `BLOCKS_FORMALIZATION` · **blocks_manual_mvp** false
- **recommended_options**：提供 2–3 个真实项目的"配置 + 实际 SKU 数"即可建立分界规则。
- **decision_status** `OPEN` · **related_tests** `SR-01…SR-05 SR-09 SR-10 DA-07`

### ORI-05 · ODM 无结构化规则 + 3 处 Status 未关闭

- **current_temporary_handling**：源表只作为唯一业务基线；Status 文本原样保留，不推断。
- **blocking_level** `BLOCKS_FORMALIZATION` · **blocks_manual_mvp** false
- **decision_status** `OPEN` · **related_tests** `RT-01 PR-02`

### ORI-06 · Option 项是否启用 / PCBA 单位口径

- **current_temporary_handling**：PCBA 行永不与台数相加（`pcba_lines_not_summed`）。
- **blocking_level** `AFFECTS_ACCURACY` · **related_tests** `D01-05 RS-08 PR-01`

### ORI-07 · Risk Reserve 比例与适用范围无来源

- **current_temporary_handling**：默认 0；用户填写时按基线需求计提，且不对用户追加需求计提。
- **impact_if_unresolved**：以 4 SKU 为例，5% = 438.8 × 0.05 = **21.94 台**。
- **blocking_level** `AFFECTS_ACCURACY` · **related_tests** `D01-02 D01-07`

### ORI-08 · 匹配权重 / 阈值属 Agent 设定

- **current_temporary_handling**：权重仅用于排序，绝不用于把并列压成单一答案（DEC-01）。
- **blocking_level** `BLOCKS_FORMALIZATION` · **related_tests** `SR-10`

### ORI-09 · 自动读取需求表所需的真实样本

- **current_temporary_handling**：MVP 只用手动输入，自动读取推迟（DEC-08）。
- **blocking_level** `ADVISORY` · **decision_status** `ANSWERED_AWAITING_SAMPLE`

### ORI-10 · MEPA 是否恒为每 Phase 36；HW PA 何时饱和于 4 ⭐

- **current_evidence**：主表 MEPA FVT 写 32.0、SIT 写 36.0，但两 Phase 总量恒 36；
  HW PA 恒 4.0（主表 6 SKU 为 4.2，作为审计值保留）。
- **current_temporary_handling**：`PER_PHASE_FIXED`（临时模型，界面显示"临时采用"）。
- **impact_if_unresolved**：SKU2 总量 **+8.0 台**，SKU6 **−0.4 台**。
- **blocking_level** `BLOCKS_FORMALIZATION` · **blocks_manual_mvp** false
- **decision_status** `OPEN` · **related_tests** `QM-01 QM-03 QM-04 QM-07`

### ORI-11 · Build Plan 与 PPA sample standard 1.0

- **current_temporary_handling**：与手动 MVP 解耦，等真实样本再对比。
- **blocking_level** `ADVISORY` · **decision_status** `ANSWERED_AWAITING_SAMPLE`

### ORI-12 · 6 条 model questions（EMC Test / NV / INTEL）

- **current_temporary_handling**：平坦总量**不**自动升级为 `PER_PHASE_FIXED`，保持
  `PER_SKU_RATE` 并登记为模型问题。
- **blocking_level** `AFFECTS_ACCURACY` · **related_tests** `QM-05 RS-07`

### ORI-13 · 定义域空洞（超出 2–6 SKU）

- **current_temporary_handling**：越界输入不外推，只停**该情景**并给出解释，
  另一情景照常输出。此处附带一个执行期影响标签（`BLOCKS_EXECUTION` 仅作用于该情景），
  **不作为新 ORI**。
- **blocking_level** `AFFECTS_ACCURACY` · **related_tests** `SR-08 OR-03 WV-…`、UI-24

### ORI-14 · 缩写与 Green FVT 自相矛盾

- **blocking_level** `ADVISORY` · **decision_status** `OPEN`

### ORI-15 · `Green/SIT/SKU3` 主表值与 1/N 规律不符

- **current_evidence**：主表 `3.0` → `3.0 × 3 = 9`，附表行 56 恒为 6；相邻档 `1.5×4`、`1.2×5` 都是 6。
- **current_temporary_handling**：**DEC-10 采用附表 6.0**；主表 9.0 作为审计值保留，
  差值 −3.0 上报，不修改源表。
- **impact_if_unresolved**：3 SKU 档：附表口径 408.0 对主表口径 417.0，差 **9.0 台**。
- **blocking_level** `AFFECTS_ACCURACY` · **blocks_manual_mvp** false
- **recommended_options**：(A) 确认主表 `3.0` 有效（则需重新决定采用口径）；
  (B) 更正为 `2.0`，该格随即变为 VERIFIED。
- **agent_recommendation**：先向源表作者确认是否笔误——7 格里最像录入错误的一格。
- **decision_status** `OPEN` · **related_tests** `CT-V2-01 CT-V2-11 DA-01`

### ORI-16 · `Safety/FVT/SKU6` 主表 9.6 与附表 10 不一致

- **current_evidence**：主表 Safety FVT 前四档总量为 10 / 9 / 10 / 10，第六档为 `1.6 × 6 = 9.6`；
  附表行 57 在 SKU4/5/6 都是 10。
- **current_temporary_handling**：**DEC-10 采用附表 10.0**；9.6 作为审计值原样保留，
  不因"看起来该是整数"而改写（D-01）。
- **impact_if_unresolved**：6 SKU 档：采用口径 FVT 242.0，主表口径 241.6，差 **0.4 台**。
- **blocking_level** `AFFECTS_ACCURACY` · **blocks_manual_mvp** false
- **decision_status** `OPEN` · **related_tests** `CT-V2-12 DA-10 D01-08`

### ORI-17 · 主表「每 SKU」列实为总量的 1/N 回推

- **business_question**：`Safety/SIT`（3,2,1.5,1.2,1 → 恒 6）与
  `RF Certification/SIT`（7.5,5,3.75,3,2.5 → 恒 15）两格，主表列随 SKU 数严格 1/N 递减，
  字面语义更像"该 Phase 总量再摊分"。请确认真实语义。
- **current_evidence**：`rate_shape = BACK_DERIVED_FROM_FLAT_TOTAL`（自动判定）；
  同一张表里 EMC 是真正的常数率（`1,1,1,1,1 → 2,3,4,5,6`）。
- **current_temporary_handling**：DEC-10 后两格都直接采用附表值（6 / 8–10），
  **数值上不再有歧义**；主表列只作为审计与差异分析。
- **impact_if_unresolved**：本轮无数值影响；若将来某档主表缺失，两种语义会给出不同补全。
- **blocking_level** `AFFECTS_ACCURACY` · **blocks_manual_mvp** false
- **recommended_options**：(A) 确认表内数值即单 SKU 用量 → 归档；
  (B) 确认这两格语义是"Phase 总量" → 标注改为与 MEPA 同处理（数值不变）。
- **decision_status** `OPEN` · **related_tests** `CT-V2-01 DA-09 QM-02`

---

## 与输出中 ORI kind 的对应关系

| 引擎输出的 `kind` | Register ID | blocking_level | blocks_manual_mvp |
|---|---|---|---|
| `SKU_TIE_NOT_RESOLVABLE` | ORI-04 | BLOCKS_FORMALIZATION | false |
| `WAVE_ASSIGNMENT_NOT_PROVIDED` / `_UNKNOWN` | ORI-03 | AFFECTS_ACCURACY | false |
| `OUT_OF_DOMAIN_INPUT` | ORI-13 | BLOCKS_EXECUTION（仅该情景） | false |
| `CERTIFICATION_SOURCE_VALIDATION_MISMATCH` | ORI-02 / ORI-15 / ORI-16 | BLOCKS_FORMALIZATION | false |
| `CERTIFICATION_APPENDIX_VALIDATION_INCOMPLETE` | ORI-02（+ ORI-02a） | BLOCKS_FORMALIZATION | false |
| `CERTIFICATION_BREAKDOWN_EVIDENCE_NOT_GENERALIZED` | ORI-02b | ADVISORY | false |
| `REUSE_PROOF_MISSING` / `REUSE_OVERLAP_UNPROVEN` | DEC-06 执行结果 | AFFECTS_ACCURACY | false |

`temp` 模型（MEPA / HW PA）与 6 条 model question 不产生运行期 kind，
而是通过 `row.is_temporary_model = true` 与界面 **临时采用** 状态呈现（ORI-10、ORI-12）。
