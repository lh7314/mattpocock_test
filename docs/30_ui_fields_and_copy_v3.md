# 30 — 用户输入字段与界面文案清单（交付物 O）
> **状态（DEC-10 之后）**：本文描述的是 Phase 3a 的 Certification 口径
> （采用主表派生值）。Owner 已决定在 MVP 与团队试用阶段**采用附表总量**，
> 最新口径见 `docs/36_certification_adoption_v4.md`、`docs/37_owner_decision_log_v4.md`、
> `docs/39_totals_v4_and_6sku_review.md`、`docs/40_web_mvp_v4_changes.md`。
> 本文按原文保留，作为阶段记录。


界面语言：中文为主，关键内部术语保留英文枚举，便于与规则包/导出字段对照。
普通用户界面**不显示** Rule ID、Rule Version、Schema 字段、内部状态代码、测试探针名称、
完整 Evidence Registry —— 这些都在「展开详情」与导出文件中。

---

## 1. 首页 `index.html`

| 元素 | 文案 |
|---|---|
| 工具名称 | 样机需求分析工具 · Sample Requirement Agent |
| 一句话用途 | 按 CPU / GPU / Panel / SSD / Memory 关键配置推导 SKU 档位，并算出 FVT 与 SIT 各阶段的样机需求量。**你不需要输入 SKU 数量。** |
| 主按钮 | 新建分析 |
| 隐私说明 | 分析在本机浏览器内完成，不上传任何数据。 |
| 区块标题 | 最近分析（计数 `无` / `N 条`） |
| 次要说明 | 打开＝查看已保存结果；复制＝带原输入新建；删除＝仅删除本机记录 |
| 存储不可用提示 | 本机浏览器存储不可用，历史记录无法保存；分析结果仍然可以计算并导出 JSON / CSV。 |
| 空列表 | 还没有分析记录。点击「新建分析」开始。 |
| 「不会做的事」清单 | ① 不会替你选一个 SKU 档位。4 SKU 与 5 SKU 无法区分时，两档都会完整计算并并列显示。② 不会把 Certification 附表当成第二套规则重复加进总量；附表只验证主表的乘法关系。③ 不会因为存在第二个 SSD / Memory Spec 就推断有第二波次；只有明确标为后续波次的 Spec 才被排除。④ 不会做业务取整；443.8 就是 443.8。⑤ 不会在没有证据时扣减复用样机。 |
| 页脚 | 规则包与业务数值来自仓库内已验证的产物，前端不保存任何业务数字。本工具为 MVP：无账号、无团队、无权限、无审批流。 |

**最近分析表头**：`Project Name` / `分析时间` / `SKU 结果` / `样机需求` / `状态` /（操作）
**行内状态**：`未发布草稿` · `N 项待确认` · `无待确认`
**操作按钮**：`打开` · `复制` · `删除`（删除二次确认：「删除这条本地分析？该操作只影响本机浏览器保存的记录。」）

---

## 2. 新建分析 `new.html`

### 2.1 基本信息

| 字段 | 标签 | 类型 | 必填 | 说明文案 |
|---|---|---|---|---|
| project_name | Project Name（可选） | 文本 | 否 | 占位符「留空会自动命名」；首页列表显示 |
| project_type | Project Type | 下拉 | 是，默认 `Clean Sheet` | `Clean Sheet` / `Existing Plan` / `Other` |
| odm | ODM（可选，仅记录） | 文本 | 否 | 占位符「LCFC / HQ / Compal / …」；**仅记录，不参与计算**（ORI-05） |
| phase_scope | Phase Scope | 复选 | 默认全选 | `FVT` / `SIT`；「FVT 与 SIT 各自读自己的源行，不使用全局比例。」 |

### 2.2 SKU Key Factors

区块说明：**SKU 数量由这些配置推导，不需要（也不能）直接输入。Panel 填的是 Panel Spec 数量；
源表 D2:H2 的「N*panel」批注含义未确认，已作为证据保留但不参与计算。**

| 字段 | 标签 | 类型 | 空值显示 |
|---|---|---|---|
| cpu | CPU Count | 整数 | 占位符 `请补充`，输入框转为橙色底 |
| gpu | GPU Count | 整数 | 同上 |
| panel | Panel Spec Count | 整数 | 同上 |
| ssd | SSD Spec 数量 | 整数 0–8 | 同上；下方按数量展开逐 Spec 行 |
| mem | Memory Spec 数量 | 整数 0–8 | 同上 |

每个 Spec 行（SSD / Memory）：

| 字段 | 标签 | 选项 |
|---|---|---|
| spec_label | Spec Name（可选） | 自由文本，占位符 `spec 1` |
| wave | Wave Assignment | **当前波次** / **后续波次** / **未特别指定** |
| wave_source | Wave Source | **未指定** / **本次手动选择** / **正式需求表标记** |

波次说明文案：**Wave Assignment 三选一：当前波次 / 后续波次 / 未特别指定。
只有「后续波次」会把该 Spec 从 Current Wave 排除；「未特别指定」表示计入当前波次、没有人做过安排，
它不等于"未知"，也不会被系统猜成第二波。**

内部映射：`当前波次→CURRENT_WAVE`、`后续波次→LATER_WAVE`、`未特别指定→NO_EXPLICIT_ASSIGNMENT`
（在契约边界归一为 `CURRENT_WAVE + NOT_PROVIDED`，**不显示也不当作 UNKNOWN**）。

### 2.3 当前判断（实时预览，随输入更新）

`SKU 结果` = `4–5 SKU` / `2 SKU` / `超出范围` / `暂无法建议`
徽标 = `RANGE 范围` / `单一值` / `单一值（有保留）` / `超出规则库范围` / `信息不足`
缺失提示 = `请补充：panel、ssd`

### 2.4 高级选项（默认全部收起）

**Certification 补充信息**
说明块：**Certification 只有一套计算规则：主表单 SKU 数量 × 本次 SKU 数。附表的作用是验证这个
乘法关系，不会再次加入总量。J33 是 RF Certification 的构成说明（2 天线源 + 2 WLAN 卡），
只用于解释，不叠加。状态：DECLARED_NOT_GENERALIZED。**

表格列：`Function` / `Phase` / `主表 /SKU` / `× N SKU` / `附表` / `附表验证` / `本次采用值`
状态徽标：`已验证` / `请确认（不一致）`；一致的格显示 `（系统计算）` 且不提供输入框。
底部说明：**此处填写的采用值只对本次分析生效，不会写回规则库，也不会升级成正式规则；
系统计算值与你填写的值会一起保留在导出文件中。**

**Additional Requirement**：`Quantity` / `Unit(UNIT·PCBA)` / `Label` + `+ 增加一行`。
说明：**用户额外提出的需求。UNIT 会计入合计；PCBA 永不与台数相加，也不会产生风险预留。**

**Reuse 信息**：`Quantity` / `Reuse Status` / `Unit` / `Evidence Note` +
`Function（可选）` + `已证明不在基准内含共享中（否·是）` + `+ 增加一行`。
Reuse Status 四个选项：`已含在基准内 (ALREADY_EMBEDDED_IN_BASELINE)` ·
`额外且已确认的复用 (ADDITIONAL_CONFIRMED_REUSE)` · `潜在复用（仅展示） (POTENTIAL_REUSE)` ·
`重叠情况未知 (UNKNOWN_OVERLAP)`。
说明：**四种状态……只有「额外且已确认」并且已证明不在基准内含共享中的 UNIT 数量才会扣减，
其余一律只展示。**

**Risk Reserve %（默认 0，需业务确认）**
说明：**源表没有任何已确认的风险预留比例（ORI-07），因此默认 0，不会自动加数。**

主按钮：**运行分析**

---

## 3. 分析结果 `result.html`

### 3.1 顶部

`{Project Name}` · `保存于 YYYY-MM-DD HH:MM` · `ORI-02 PARTIALLY_RESOLVED` ·
`N 项需要 Owner 确认` · `数值未做业务取整（D-01）` · `区间不会被折叠成单一数字`
按钮：`以此次输入新建` · `导出 JSON` · `导出团队 Review 报告 (CSV)`

### 3.2 每个情景（Current Wave / Full Project 各一块）

标题：`Current Wave 当前波次` / `Full Project 全项目`，可带 `与 Full Project 相同` 徽标。

| KPI | 文案 |
|---|---|
| Recommended SKU | `4–5 SKU` / `2 SKU` + 形态徽标 |
| Sample Demand 样机需求 | 单值或 `443.8 – 474` + `FVT / SIT 合计` |

**范围说明（4–5 SKU 时，逐字）**：
> **这是一个范围，不是漏填。** 4 SKU 与 5 SKU 在现有 SKU Definition 下无法区分
> （SKU_NOT_ESTABLISHED）。两档都已完整计算，系统没有、也不会默认替你选一档。
> Certification 的计算规则本身是明确的，这里的范围来自 SKU 档位尚未建立正式分界。

**波次相同说明（无 LATER_WAVE 时，逐字）**：
> 当前没有明确安排到后续波次的 Spec，因此 Current Wave 与 Full Project 使用相同配置范围。

**波次不同说明**：
> 已从 Current Wave 排除的 Spec：**ssd2、mem2**（明确标记为后续波次）。
> 当前波次关键配置：cpu=2, gpu=2, panel=1, ssd=1, mem=1；全项目：…=2。
> 差异只来自被排除的 Spec，同一 SKU 档位的 base_demand 不因波次改变。

**波次未知说明**：
> 以下维度的波次被标记为未知：ssd，因此当前波次给出多个情景。系统不会替你决定波次。

**超范围说明（唯一会停止计算的情形）**：
> **本情景已停止计算。** 输入超出规则库覆盖的 SKU Definition 范围，系统不会外推一个数字。
> 请修正输入后重试。

### 3.3 按 SKU 档位的完整计价（表头）

`SKU` / `FVT` / `SIT` / `Certification` / `非 Certification` / `Reuse 采用` / `风险预留` /
`合计` / `结果形态`（`单一值` 或 `443.8 – 474`）
PCBA 行单独一行提示：`PCBA 行（不计入样机台数）：[…]`

### 3.4 Function 明细（折叠，默认取最低 SKU 档）

主表列：`Function` / `Phase` / `Quantity Model` / `建议值` / **`状态`** / `主要原因`

**普通用户可见状态（8 种，本任务要求）**

| 界面状态 | 触发条件 |
|---|---|
| `已计算` | 有值、无验证要求、非临时模型 |
| `已验证` | Certification 格附表校验 `VERIFIED` 且无需复核 |
| `结果范围` | 合计层面出现多档（由 `recommended_total_band.exact=false` 驱动） |
| `请确认` | 附表校验 `MISMATCH`，或 `owner_review_required` 为真 |
| `临时采用` | `is_temporary_model`（MEPA / HW PA 的 `PER_PHASE_FIXED` 候选） |
| `用户输入` | `value_source = USER_MANUAL_OVERRIDE` |
| `暂无法计算` | `base_demand` 为 null（当前数据下不会出现） |
| `已排除` | 被波次排除的 Spec（在情景说明中以 Spec 名呈现） |

`主要原因` 文案示例：
- `主表单 SKU 数量 1 × 4 个 SKU，附表一致`
- `主表单 SKU 数量 7.5 × 2 个 SKU = 15，附表给出 8，两者不一致，已保留原值待确认`
- `附表按每 Phase 固定量给出，不随 SKU 数量缩放（临时采用，待业务确认）`

`展开详情` 标题：**展开技术详情：源值 / 采用值 / 计算基准 / Source Reference /
Verification Status / Reuse 账本**（内含 `system_computed_value`、`user_input_value`、
`value_source`、`main_table_per_sku_quantity`、`applied`、`unit`、`rule_id`、
`is_temporary_model`、`source_reference`、`verification`、`breakdown_evidence_role`）。

### 3.5 Certification 区块

> 计算规则：主表单 SKU 数量 × 本次 SKU 数（N）。FVT 与 SIT 各自读自己的源行，不使用全局比例。
> 附表仅作验证，已计入项目总量 1 次、附表计入 0 次。J33 角色：BREAKDOWN_EVIDENCE，
> 状态 DECLARED_NOT_GENERALIZED，未叠加到结果上。
> （含用户覆盖时追加）**本次分析包含用户输入的采用值。**

徽标：`FVT 10` · `SIT 29` · `合计 39` · `附表验证 7 一致 / 1 不一致 / 0 无法判定`
`逐格验证明细`（折叠）列：`Function` / `Phase` / `SKU` / `主表 /SKU` / `系统计算` / `采用` /
`用户输入` / `附表` / `差值` / `状态(已验证·请确认)` / `来源(row 34 / 60)`

### 3.6 需要确认的问题

顶部说明：**这些问题只是提示，不会阻止你继续使用该工具；其中「BLOCKS_FORMALIZATION」
只表示规则包还不能定版，「BLOCKS_EXECUTION」才会停止受影响的计算。**

界面标签映射：`SKU_TIE_NOT_RESOLVABLE→SKU 档位无法区分` ·
`CERTIFICATION_SOURCE_VALIDATION_MISMATCH→Certification 附表校验不一致` ·
`CERTIFICATION_APPENDIX_VALIDATION_INCOMPLETE→Certification 逐格验证未全部通过` ·
`CERTIFICATION_BREAKDOWN_EVIDENCE_NOT_GENERALIZED→J33 说明仅适用于特定组合` ·
`WAVE_ASSIGNMENT_NOT_PROVIDED→波次未指定` · `WAVE_ASSIGNMENT_UNKNOWN→波次标记为未知` ·
`OUT_OF_DOMAIN_INPUT→输入超出规则库覆盖范围` ·
`REUSE_PROOF_MISSING→复用缺少证明` · `REUSE_OVERLAP_UNPROVEN→复用重叠未知`

无问题时：**本次分析没有产生需要确认的问题。**
折叠区：**完整技术条目（Owner Review Register 输入）**

### 3.7 找不到记录

**找不到这条分析** — 它可能在另一台机器上，或已被删除。返回首页

---

## 4. 术语对照（界面 ↔ 内部）

| 界面 | 内部值 |
|---|---|
| 当前波次 / 后续波次 / 未特别指定 | `CURRENT_WAVE` / `LATER_WAVE` / `NO_EXPLICIT_ASSIGNMENT` |
| 单一值 / 范围 / 暂无法建议 / 超出范围 | `SINGLE` · `SINGLE_WITH_RESERVATION` / `RANGE` / `UNDETERMINED` / `OUT_OF_DOMAIN` |
| 未确立 | `preferred_sku = NOT_ESTABLISHED` |
| 主表 / 附表 | `MAIN_TABLE`（`PER_SKU_RATE`）/ `DERIVED_TOTAL_VALIDATION` |
| 临时采用 | `is_temporary_model = true`（`PER_PHASE_FIXED`，MEPA / HW PA） |
| 本次采用值 | `USER_MANUAL_OVERRIDE`（不落规则库） |
| 待确认 | Owner Review Item |
