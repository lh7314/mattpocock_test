# 20 — K. 三页 Web MVP：最小字段与输出

> 只有三页。没有登录、没有团队、没有审批、没有后台管理。
> 每个字段都对应 `input.schema.json` / `output.schema.json` 里的一个键，不额外发明字段。

---

## 页面 1 · Home（首页）

| 元素 | 说明 |
|---|---|
| `新建分析` | 进入页面 2 |
| `最近分析`（本地 IndexedDB） | 显示 project_label、五维摘要、SKU 答案、生成时间、规则版本 |
| 规则版本条 | `rule_pack_version` + `quantity_model_version` + 来源文件名与 SHA 前 8 位 |
| 状态徽标 | `DRAFT_UNCONFIRMED_BY_OWNER`（常驻，直到规则包定版） |
| `打开已有分析` | 复现历史结果（含当时的 input document） |

**不放**：使用人数、导入模板下载、任何"管理"入口。需求表模板要等 ORI-09，
不提供模板就等于不暗示自动读取已可用。

---

## 页面 2 · New Analysis（新建/编辑）

### 2.1 基本信息

| 字段 | 类型 | 必填 | 契约 |
|---|---|---|---|
| `project_label` | 文本 | 否 | 仅本地标识 |
| `odm` | 下拉 `LCFC / HQ / Compal / Other` | 否 | **只记录不生效**；旁边显示灰字 `ORI-05 未结构化，当前不参与计算` |

### 2.2 五个关键因子（主输入区）

每个因子一行，四列：

| 列 | 内容 |
|---|---|
| 值 | 数字输入。未填即 `null`，占位符显示 `请补充` |
| 来源徽标 | `文件读取` / `用户已修改` / `未确认` |
| 采纳值 | 只读回显 `effective`（= 用户已改值 > 文件值 > 未确认） |
| 「恢复文件值」 | 仅在存在 `file_value` 时出现 |

**硬规则**

1. 界面上**不存在 SKU 数量输入框**（DEC-08）。
2. 空值不默认 0 / 1 / N-A。提交时空值保留为 `null`。
3. 用户改过任一值 → 该行标记为 `USER`，文件值不丢，可回退。

| 因子 | 标签 | 说明文字 |
|---|---|---|
| cpu | CPU 组合数 | 项目中不同 CPU 源的数量 |
| gpu | GPU 组合数 | 权重最高（GPU 在 SKU Definition 中区分度最强） |
| panel | **Panel Spec 数** | 灰字：`口径 = Panel Spec Count（DEC-02）。D2:H2 批注的 N*panel 含义待确认，未参与计算` |
| ssd | SSD Spec 数 | 超过 2 触发越域提示 |
| mem | Memory Spec 数 | 超过 3 触发越域提示 |

### 2.3 Wave Assignment（仅当某因子 ≥ 2 时展开）

对每个数量 ≥ 2 的因子，逐颗 Spec 一行：

| 列 | 内容 |
|---|---|
| Spec 标签 | `ssd1` `ssd2` … |
| Wave | 单选 `CURRENT_WAVE / LATER_WAVE / UNKNOWN` |
| 来源徽标 | `FORMAL_REQUIREMENT_SHEET` / `USER_SELECTED` / `NOT_PROVIDED` |

- 初始一律 `NOT_PROVIDED`，UI 明确提示：
  **「不选 = 全部按当前波计算，不会产生第二波」**（DEC-04）。
- 选了 `UNKNOWN` 会即时提示"结果将展开为多个 Current Wave 读法"。
- 数量 = 1 的因子不显示本区（引擎内部 `IMPLICIT_SINGLE_SPEC`）。

### 2.4 进阶（默认折叠）

| 区块 | 字段 | 契约要点 |
|---|---|---|
| Certification 手工值 | 4 个 Function × FVT/SIT 各一个数字框 + 必填 `reason` | 空 = 保持 `UNRESOLVED_SHOW_BAND`；填了 = `USER_MANUAL_OVERRIDE`，行上标"用户手工值"。旁边并排显示两套模型的候选值供参考，**不预选任何一个** |
| 额外需求 | 行式：`label` / `qty` / `unit(UNIT\|PCBA)` / `phase` / `basis` | **不预置任何 `Option:` 项**（原表 K3：Option 未纳入官方样机数据） |
| Reuse 信息 | 行式：`function_id` / `qty` / `unit` / `reuse_status`(四态) / `proven_not_in_baseline` 勾选 / `basis` | 选 `ADDITIONAL_CONFIRMED_REUSE` 时强制勾选"已证明未被基线包含"+ 填依据；若该 Function 是 `BLOCK_UNLESS_PROVEN`，行上方直接显示其 spread / growth 数据 |
| 风险预留 | `percent`（默认 0） | 灰字 `ORI-07：Owner 未提供比例，默认 0` |

### 2.5 提交前校验

- 走 `input.schema.json`。失败时**定位到具体字段**，不做任何"善意纠正"（不补 0、不改类型）。
- 五维全空时允许提交，结果会是 `UNDETERMINED` —— 让用户看到"什么都没填会怎样"，
  比禁按钮更能建立信任。

---

## 页面 3 · Result（结果）

### 3.1 顶部摘要

| 显示 | 数据来源 | 规则 |
|---|---|---|
| SKU 答案 | `match.state` / `recommended_sku` / `preferred_sku` | `SINGLE*` → 显示"N SKU（含保留意见）"；`RANGE` → 显示 **`N–M SKU`，Preferred: NOT_ESTABLISHED**；`UNDETERMINED` / `OUT_OF_DOMAIN` → 显示原因 |
| 样机总量 | `recommended_total` 或 `recommended_total_band` | `single_value=false` 时**必须**显示区间（Schema `if/then` 禁止单值） |
| FVT / SIT | `fvt_total` / `sit_total` | 同样随 `single_value` 决定单值或区间 |
| 状态徽标 | `status` | 常驻 `DRAFT_UNCONFIRMED_BY_OWNER` |
| 精度徽标 | `policy.rounding` | 常驻 `NONE (D-01)` |
| 规则版本 | `rule_pack_version` / `quantity_model_version` | 点击查看来源文件 + SHA |

### 3.2 场景切换（Current Wave / Full Project）

两个 Tab。若 `identical_to_full_project = true`，Current Wave Tab 顶部提示
"当前波次与全项目一致（未声明第二波）"，但**照常展示全部数据**。
若存在 `unknown_factors` 扇出，Tab 内用子选择器列出各 `scenario_id`，并标 `truncated`。

### 3.3 候选 SKU 对照表（`RANGE` 时的核心视图）

| SKU | 样机总量 | FVT | SIT | 与相邻档差量 | Quantity Model 概况 |
|---:|---:|---:|---:|---:|---|
| 4 | `438.8 – 443.8` | 区间 | 区间 | — | 全表 42 cell：30 RATE / 4 FIXED / 8 UNRESOLVED |
| 5 | `469 – 474` | 区间 | 区间 | +30.2 – +30.2 | 同上 |

- 两档**并列不排序、不预选、不高亮"推荐"**。
- 表下固定一行说明：`4 SKU 与 5 SKU 在当前 SKU Definition 下无法区分（ORI-04）`。

### 3.4 每个候选 SKU 的明细（可展开）

1. **按证据源分列的总量**（DEC-03）：`MAIN_TABLE` 一行、`SECONDARY_TABLE` 一行、
   `not evaluable: J33_FORMULA` 一行，最后 band 行。文案：
   "两套模型分别完整计价，未平均、未合并"。
2. **Category 小计**：RD / PA / CERT / VENDOR / MFG。
3. **Function × Phase 明细表**：列 =
   `Function | Phase | Quantity Model | 数量 | 来源 | 行号 | 状态`。
   `UNRESOLVED` 行的"数量"显示 `待确认 (主表 X / 副表 Y)`。
   `MEPA`/`HW PA` 显示 `SECONDARY_ABSOLUTE_TABLE` 并可展开看主表那个伪费率。
4. **Certification 未决区块**：8 行，含 `models_agree` 标记。
5. **Reuse 账本**：每条 `qty / unit / status / applied / decision / why`；
   顶部一行 `声称 14.0 → 实扣 4.0`。
6. **PCBA 区块**：单独列出，标注"不计入整机型需求"。
7. **计算式**：以本例数值展示
   `Base + Conditional + Confirmed Reuse + Risk Reserve = Recommended`，
   并标出未参与计算的 `potential_reuse_display_only`。

### 3.5 理由与待确认

| 区块 | 内容 |
|---|---|
| 为什么是这个答案 | `match.reasons` 逐条 + `dimension_detail` 逐维度 MATCH/PARTIAL/MISMATCH 表 |
| 为什么不是别的档 | `neighbour_scores` |
| 被排除的证据 | `unresolved_comments_excluded`（D2:H2 批注原文 + "不参与计算"） |
| **Owner Review Items** | 按 `kind` 分组，含 `why` 与受影响场景 `scenario_ids`；顶部计数 |
| 输入回显 | 五维采纳值 + 来源 + Wave 声明 + 手工覆盖项 |

### 3.6 导出

| 文件 | 内容 |
|---|---|
| `analysis-<id>.json` | 完整 output payload（过 Schema），含全部证据字段 |
| `analysis-<id>.csv` | Function × Phase × SKU × 场景明细；含 `rule_id`、`source_file`、`row`、`quantity_model`、`value_source`；数量列同时给 `value_full_precision` 与 `value_display` 两栏 |
| 两者页脚 | `baseline_id` / `rule_pack_version` / `quantity_model_version` / `rounding: NONE (D-01)` / `status` |

---

## 文案红线（UI 层同样受探针约束）

| 禁止 | 应显示 |
|---|---|
| `建议 N SKU`（当状态为 RANGE） | `4–5 SKU（无法区分，待确认）` |
| 把区间显示成 `441.3（取中值）` | `438.8 – 443.8`，并说明来自两套未合并模型 |
| `根据历史项目 Pro/Y5…` | 只允许引用 Function/Phase/SKU Definition 行号 |
| `已自动匹配 ODM = LCFC` | `ODM 已记录，暂不参与计算（ORI-05）` |
| `系统推断第二波` | `未声明第二波，当前波次 = 全项目` |
| `约 444 台` | `443.8`（或区间），并保留全精度导出 |
