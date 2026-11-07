# 08 — M. Open Questions Requiring Owner Decision

> **本文件保留 Phase 1 的完整证据与提问原文，不作删改。**
> ORI 的**当前状态、临时处置与阻塞口径以
> [`13_ori_status_v2.md`](13_ori_status_v2.md) 为准**（Phase 2 更新）。
> 两处冲突时以 13 为准；下面的"阻塞"表述是 Phase 1 当时的口径。

共 **14 条** ORI（ORI-01 … ORI-14；本文件正文即为全部 14 条，末尾汇总表只列到 ORI-11，
ORI-12/13/14 见各自小节）。

Phase 1 口径的**阻塞项 6 项**（ORI-01 / 02 / 03 / 04 / 09 / 11）：不关闭则只能输出
"范围 + 请确认"，无法输出单一 Recommended SKU，也无法交付"文件自动读取"功能。
Phase 2 后：ORI-09 / ORI-11 已从手工输入主链路解耦，见 DEC-08。

每条含：发现 → 证据（单元格/原文）→ 影响 → 候选方案 → **Agent 当前默认（不升级为规则）**。

---

## ORI-01 · Panel Spec 语义冲突 ★阻塞

**发现**：同一文件内对"Panel"存在两套互斥口径。

| SKU | SKU Definition（行 79–83） | 表头批注（D2:H2，Lingyu LY3 Rong，2026-06-24） |
|---|---|---|
| 2 | Panel spec **1–2** | `2*panel+1*CPU+1*GPU` |
| 3 | Panel spec **1** | `3*panel+2*CPU+2*GPU` |
| 4 | Panel spec **2** | `4*panel+2*CPU+2*GPU` |
| 5 | Panel spec **2** | `5*panel+3*CPU+3*GPU` |
| 6 | Panel spec **2–3** | `6*panel+3*CPU+3*GPU` |

批注中 `panel` 恒等于 SKU 数量；另 CPU 也冲突（SKU6 批注 `3*CPU` vs 定义 `4–5`）。

**影响**：Panel 是 5 个 Key Factor 之一。若批注口径成立，"Panel Spec 数量"就不再是独立输入
（它恒等于输出 SKU 数），输入模型需从 5 维改为 4 维。

**候选方案**
- **A**：批注的 `panel` 指**整机样机台数/展示机**，不是 Panel Spec 数量 → 两者不冲突，输入保持 5 维。
- **B**：批注指 Panel **厂商/尺寸**等另一口径（行 92 `key source数量`）→ 需定义 source 计数规则。
- **C**：批注是 SKU Definition 早期草稿，已被行 79–83 取代 → 批注降级为历史参考。
- **D**：行 79–83 有误，以批注为准 → Panel 移出输入维度。

**Agent 当前默认**：采用行 79–83（依据：与 J15 `base sku 搭配不同的panel` 语义一致，且数值矩阵可复算），
批注记为 `CONFLICTED` 并在结果页持续提示。**未升级为规则。**
**需要 Owner**：判定 A/B/C/D；若选 B，请给出 Panel Spec 计数定义（尺寸？厂商？分辨率？HDR 与否？）。

---

## ORI-02 · Certification 两套模型冲突 ★阻塞

**发现**：Certification 在 B1 主表（行 27–34，per-SKU 费率）与 B2 副表（行 51–62，绝对 units/phase）中口径不同。

| Function/Phase | 主表 费率×SKU | B2 副表 | 差异 |
|---|---|---|---|
| EMC SIT | 2/3/4/5/6 | 2/3/4/5/6 | 0 ✓ |
| Green SIT | 6/**9**/6/6/6 | 6/6/6/6/6 | SKU3 **−3** |
| Safety FVT | 10/9/10/10/**9.6** | 10/9/10/10/**10** | +0.4 |
| Safety SIT | 6/6/6/6/6 | 6/6/6/6/6 | 0 ✓ |
| **RF Cert SIT** | **恒 15** | **8/9/10/10/10** | **−7/−6/−5/−5/−5** |
| TTL SIT | 29/33/31/32/**32.6** | **22/24/26/27/28** | −7…−4.6 |

**证据**：J33 原文自述其按 `2 antenna source + 2 wlan source` 推导：
`SRRC*2 / CE*4=antenna*wlan / FCC(wlan*antenna)*4 / 印尼*2 / Mexico*1 / 资安*2` → 2+4+4+2+1+2 = **15**，
与主表恒定 15 完全吻合 → **主表 = 特定 source 组合下的展开式**，而非随 SKU 变化的量。
J52 另称 `refer to G10 G12 LCFC data: WW certification including promition: range 34--36 units`，
而 B2 实际 FVT+SIT = 32/33/36/37/38，**仅 SKU3–5 落在 34–36** → 副表亦未完全自洽。

**影响**：Certification 占 SKU4 总量的 41.0/443.8 ≈ **9.2%**；两口径之差最高达 7 台/phase。
且这是**认证类需求**（送测不可返工），偏差后果最重。

**候选方案**
- **A**：Certification 改为 **source 驱动**而非 SKU 驱动：输入新增 `antenna_source`、`wlan_source`，按 J33 公式计算（与 SKU 数无关）。
- **B**：统一采用 B2 副表（绝对量，含 10 上限）。
- **C**：统一采用 B1 主表（per-SKU）。
- **D**：分档混用（EMC/Safety 用主表，RF Cert 用 source 公式，Green 用固定 6）。

**Agent 当前默认**：使用 B1 主表（因主表总量公式已包含它，改动会导致与 Owner 原表对不上），
B2 作为 `CONFLICTED` 参考表并列展示。**未升级为规则。**
**需要 Owner**：择一；若选 A，请给出各认证项的精确公式与封顶规则。

---

## ORI-03 · "第二波"（2nd wave）无判定规则 ★阻塞（仅波次功能）

**证据**：仅行 80 一句 `(or SSD/Mem spec *2, arrange 2nd wave)`，全文再无第二处提及；
无字段、无判据、无时间边界、无数量折扣。

**影响**：任务要求分别输出 `Current Wave Recommended SKU` 与 `Full Project Recommended SKU`。
当前只能靠用户显式声明波次（`prototype` 已实现 `wave=current|full_project` 双口径），
**无法自动判断"某第 2 种 SSD/Mem Spec 是否已安排第二波"**。

**需要 Owner**
1. "已安排至第二波"的判定依据是什么？（用户勾选？项目阶段？供应商定点状态？）
2. 第二波的 SSD/Mem Spec 在 Full Project 口径下是否**全额**计入 SKU Definition 匹配（当前假设：是）？
3. 第二波是否复用同一套 Function 费率，还是有折减（如仅补测某些 Function）？
4. 第二波是否只适用于 3 SKU（行 80），还是 2/4/5/6 SKU 也可有第二波？

**Agent 当前默认**：波次 = 用户手动开关；`current` 下把第 2 种 SSD/Mem Spec 从匹配中剔除，
`full_project` 下计入。**未升级为规则。**

---

## ORI-04 · 5 SKU 永远不会被单独推荐（结构性缺陷）★阻塞

**发现**：5 SKU 定义是 4 SKU 定义的**严格子集**：

```
SKU5 = {CPU 3-4, GPU 3,   Panel 2, SSD 2, Mem 2}
SKU4 = {CPU 2-4, GPU 2-3, Panel 2, SSD 2, Mem 2}     → SKU5 ⊂ SKU4
```

任何满足 5 SKU 的输入必然同时完美满足 4 SKU → 评分并列或 4 SKU 更优。

**实测**（`tools/validate_rules.py`，405 组现实取值空间）：

```
SKU2 唯一胜出  83 次      SKU4 唯一胜出 147 次      SKU6 唯一胜出 105 次
SKU3 唯一胜出  39 次      SKU5 唯一胜出   0 次  ← 仅以 "4-5" 范围出现 29 次
```

**候选方案**
- **A**：接受现实 —— 4/5 SKU 一律输出范围 `4–5 SKU`（Agent 当前行为），并删除"单一 5 SKU 推荐"的能力预期。
- **B**：引入**新判别维度**，例如：总 source 数阈值、ID/ME 变体数、水冷/高端 SKU 是否存在、面板厂商数、平台代际。
  （行 83 的 `ID./ME*2 ，Pro上` 与行 88 `source复杂度` 暗示 Owner 心里确有额外维度，只是未写出。）
- **C**：给 5 SKU 增加"优先级/加分"（如 CPU≥3 且 GPU=3 且 SSD=2 时强制 5），本质是硬编码 tie-break。

**Agent 当前默认**：**A**（输出 `4–5 SKU` 范围），并保留 `tie=[4,5]` 结构以便 Owner 选 B/C 后直接接入。
**需要 Owner**：明确 4 SKU 与 5 SKU 的分界条件（这是 6 个阻塞项里对结果影响最大的一个）。

---

## ORI-05 · ODM 维度无结构化规则 + 3 处 Status 未关闭

**发现**：Owner 行 94 明确把 `ODM` 列为 Input，但文件**没有 ODM→数量 映射**；
差异只存在于 25 行自由文本（示例见 `docs/03_input_model.md §E.6`）。
同时 Status 列有 3 处未关闭：

| Function | Status 原文 | 含义 |
|---|---|---|
| EMC Test | `待LCFC update` | LCFC 侧数据未回，费率待定 |
| MEPA | `LCFC:Confirmed ok as left data. HQ /Compal :to be clarify.` | 仅 LCFC 确认 |
| HW PA | `HQ gap比较大` | HQ 与表值差异未解决 |

**影响**：MVP 无法回答"同一输入在 LCFC vs HQ vs Compal 下各需要多少台"。

**需要 Owner**
1. 是否本阶段就要 ODM 差异化计算？（Agent 建议：**先不做**，ODM 仅作为记录 + 差异提示）
2. 若要：请提供 3 家 ODM × 21 Function 的费率或**修正系数表**（哪怕是 5 个 Function 试点）。
3. 上表 3 处 Status 的最终数值。

**Agent 当前默认**：ODM 记录不生效；3 处 Status 使对应 Function 规则状态 = `CONFLICTED`，
在结果页标注 `基线未确认`。

---

## ORI-06 · Option / 条件需求是否启用

**发现**：J 列 4 个 `Option:` 块共 12+ 条可量化项（`Smart AMP: add 1 unit`、`CPU OC *2 &GPU OC *2 /phase`、
`Battery team 1*vendor*sku*phase`、`EPEAT: 5unit`、`eyesafe/LBL/HGPD Golden*N台,如果Panel数量为N`、
`TP FW Tuning*3/FVT`、`ESI test: LCFC need 2 unit` …）。
K3 明确：`remark option 的部分，还没加到样机data里面。` → **Owner 已确认这些量不在基线内**。
另有 K3 的 PCBA 类 8 项（`PCIE*1 PCBA`…`VRAM tuning*7`）与整机 unit **单位不同**。

**需要 Owner**
1. MVP 是否提供"勾选 Option 项 → 计入额外需求"的能力？（Agent 建议：**提供但默认全不勾选**）
2. 勾选后按什么数量计算（固定值 or 公式，如 `1*vendor*sku*phase` 需要 vendor 输入）？
3. PCBA 需求是否需要单独输出（不与 unit 相加）？

**Agent 当前默认**：全部 `NON_NORMATIVE`，不计入；结果页"待确认项"列出可勾选项与原文；PCBA 单列展示。

---

## ORI-07 · Risk Reserve 无来源

**发现**：任务公式含 `Applicable Risk Reserve`，但工作簿**无任何**风险预留数值或比例。

**需要 Owner**
1. 默认比例？（0% / 5% / 10% / 按 Category 不同）
2. 作用层级：Function 级还是总量级？是否只作用于 CERT（认证送样失败需重测）？
3. 是否需要"新平台/新 ODM/新 source"这类触发条件？

**Agent 当前默认**：`risk_pct = 0.0`，UI 不预填任何"猜测值"；公式路径已实现并测试（`22.19` 断言通过）。

---

## ORI-08 · SKU 匹配的权重与阈值属 Agent 设定

**需要 Owner 确认的参数**（全部集中在 `prototype/rules_v1.py` 顶部，便于一次性改写）

| 参数 | Agent 当前值 | 依据 | 后果 |
|---|---|---|---|
| `WEIGHTS` | MATCH 1.0 / PARTIAL 0.4 / MISMATCH 0.0 | 无文件依据 | PARTIAL 权重提高 → 更倾向给单值 |
| `DIM_WEIGHT` | gpu 1.6 > ssd=mem 1.4 > cpu=panel 1.0 | 判别力分析（04 §F.2a）+ J3/K3 GPU 侧强调 | 直接改变推荐结果（如 T-13） |
| `PARTIAL` 宽度 | 相邻 1 档 | 保守假设 | 放宽 → 更多单值，风险更高 |
| 竞争阈值 | 0.05（0 < 差距 < 0.05 → 提示竞争，T-13） | Agent 设定 | T-13 是否降级为 RANGE 由此决定 |
| 越界处理 | 超出定义域 → 保留候选但强制带保留/无法计算 | 任务"不得伪精确" | 见 T-08 |

**需要 Owner**：确认或调整；尤其 **T-13（0.76 vs 0.74）** 应给单值还是范围。

---

## ORI-09 · 缺失"需求表"样本 ★阻塞自动读取

**发现**：`original_documents` 内**只有 SKU/需求基线表**，**没有任何项目需求表实例**。
任务第七节要求"上传需求表 → 自动读取 Key Factor"，但**目标输入格式未知**。

**需要 Owner 提供（任一即可，越真实越好）**
- 2–3 份真实历史需求表（可脱敏），覆盖不同 ODM/不同格式；
- 或一份官方模板与列名定义；
- 或明确"以 CPU/GPU/Panel/SSD/Memory 的 source 计数为准，口径如下：…"。

**影响**：`docs/03 §E` 的别名表、置信度阈值、多命中处理策略目前**全部是设计提案，未经真实样本验证**。
MVP 可先交付"手工输入 + 结果"闭环，自动读取作为第二阶段。

---

## ORI-10 · 副表数值回推不一致（MEPA / HW PA）

**发现**：B3 PA 副表（行 66–75）为绝对 units/phase；主表（行 21–26）为 per-SKU 费率。16 格中 15 格一致，2 处不一致：

| 项 | B3 绝对值 | 主表费率×SKU | 差异 | 判读 |
|---|---|---|---|---|
| MEPA @SKU2 | 36（全档恒 36） | 16×2 = 32 | **+4** | K23 `CS: 1 phase 36 units` 表明 MEPA 实为**每 phase 绝对量**；若 36/2 应为 18，主表写 16 → 回填不一致 |
| HW PA @SKU6 | 4 | 0.7×6 = 4.2 | −0.2 | 0.7 明显是 `round(4/6,1)=round(0.667,1)` 的显示精度回填 |

**影响**：这两项**不是"每 SKU 费率"，而是"每 phase 绝对量"**。
按费率模型算 SKU2 的 MEPA 会得 32 而非 36（差 4 台 × 2 phase = 8 台）。
同时这直接证明工作簿存在"先定绝对量 → 除以 SKU 数 → 四舍五入"的路径，
**说明 D-01（保留底层小数）对防止误差累积是必要的**。

**需要 Owner**：确认 MEPA/HW PA 是 `ABSOLUTE_PER_PHASE` 模型（建议），并提供其在 2/3/5 SKU 下的真实绝对量。
**Agent 当前默认**：`rule_type=ABSOLUTE_PER_PHASE` 建模（36 / 4），标记 `CONFLICTED`。

---

## ORI-11 · 上游数据源未提供 ★阻塞历史校验与差异比较

**发现**：文件内引用 `G12`、`G10`、`SP`、`PPA sample standard 1.0`；
`workbook.xml` 的 `absPath` 指向 SharePoint `…/stamp/data breakdown/9月份最新final/`。
这些文件**都不在** `original_documents` 中。

**影响**
1. 任务 §二.8"与现有 ODM 或 TPM Build Plan 进行简单差异比较"**无基准数据**，功能只能做成"用户上传后比较"。
2. J52 的经验锚点（34–36 units）无法验证（副表实算 32–38）。
3. `PPA sample standard 1.0` 是 SWPA 数量的上位依据（J21），SWPA 占总量约 22%，**其正确性当前不可验证**。

**需要 Owner**：提供（1）1–2 份真实 Build Plan（LCFC/HQ/Compal 任一）；（2）`PPA sample standard 1.0` 文档。

---

## ORI-12 · 疑似"统一假设"费率（6 个 Function 共用同一组值）

**发现**：以下 Function 的 per-SKU 费率在 5 档上**完全相同** `0.5 / 0.3 / 0.25 / 0.2 / 0.2`：

`RD-ME`、`RD-PD`、`3rd Party BIOS`、`3rd Party ITE`、`MFG`（5 个完全相同），
以及 `RD-EMC Test`、`3rd NV`、`3rd INTEL` 共用另一组 `3 / 2 / 1.5 / 1.2 / 1`。
J 列对这 8 个 Function 的解释极简（`for debug*1 or 0台 to common with ME PA.`、`1unit for debug`、
`Total one phase on unit`、`if no lighting feature,no need`）。

**判读**：这些更像**统一占位假设**而非逐项实测经验值（合计仅占 SKU4 总量 2.0+2.0+1.0+…，影响 <2%）。

**影响**：数值影响小，但**语义影响大** —— 若它们是占位值，则"按小数计算"会产生虚假精度感
（如 `0.25 × 5 = 1.25 台`）。

**需要 Owner**：确认这 8 项是真实经验值还是占位；若为占位，MVP 是否应把这些 Function 显示为
"经验值待补，暂按统一假设"。

**Agent 当前默认**：原样使用其数值，`confidence=LOW` 标记，在明细行注明"该 Function 费率为跨项统一值"。

---

## ORI-13 · 定义域空洞：输入超出 2–6 SKU 定义范围时无规则

**发现**：SKU Definition 各维上界为 `CPU 5 / GPU 3 / Panel 3 / SSD 2 / Mem 3`。
因此以下常见情形**落在全部 5 档之外**，当前无任何规则可依据：

| 情形 | 现状 |
|---|---|
| SSD Spec = 3 | 5 档全部不覆盖（SSD 上界恒 2） |
| GPU Spec = 4 | 全部不覆盖 |
| Panel Spec = 4 | 全部不覆盖 |
| CPU Spec = 6 | 全部不覆盖（上界 5） |
| SKU 数量 = 7（未来项目） | 表只有 5 列，无外推依据 |

**影响**：任务 §四只定义了 2–6 SKU。Agent 若擅自外推（如 `rate(SKU7)=rate(SKU6)`）即属"Agent 推断升级为规则"，红线禁止。

**需要 Owner**
1. SSD Spec=3 是否真实存在？若存在对应 SKU 档位是多少？
2. 是否需要 7 SKU 档（及对应 Function 费率列）？
3. 越界时的期望行为：`暂无法计算`（Agent 当前）还是"按最接近档 + 强制人工确认"？

**Agent 当前默认**：越界维度记 `MISMATCH`，结果强制带保留；若全部维度越界 → `UNDETERMINED`。
UI 文案：`超出 SKU Definition 已定义范围（当前仅覆盖 2–6 SKU）`。

---

## ORI-14 · 术语/缩写确认 + 一处表内自相矛盾

**(a) 缩写无定义即无法出中文标签**（详见 `docs/02 §C.6`）：
`CS`、`KP`、`DN`、`BCS`、`CEL`、`TDMS`、`HLK`、`PQL`、`ESI`、`EA`、`MB`、`ID.`、`TPM`、
以及 Function 名 `SED`、`SS` 的正式全称。
**需要 Owner**：给出正式全称与中文标签，否则 UI 只能原样显示英文缩写。

**(b) 表内自相矛盾一处**：`Green`（行 29）FVT 费率全档为 **0**，但同一合并区 J29 备注
`FVT for RD 内测,leverage safety.` 明确描述了一个 **FVT 阶段**的用途。
→ 二者矛盾：该 Function 的 FVT 究竟是 0（数量已并入 Safety）还是应有独立数量？
（同类：`EMC`/`RF Certification` FVT 亦为 0，但 J27 写 `认证*1/sku+全套的KP(只要SIT)` —— 这条**自洽**，
说明"认证只在 SIT"是有意设定，唯 `Green` 的 FVT 备注与 0 值冲突。）

**需要 Owner**：确认 `Green` FVT = 0 是正确的（即 FVT 用途由 Safety 承担），或给出 FVT 数量。
**Agent 当前默认**：按表值 0 计算，并在明细行展示 J29 原文作为 `说明`，不改数。

**(c) 已议定值与表值不一致**：J9（Audio）与 J11（RF Test）均写
`fianl : LCFC/HQ/Compal 都可按照4-5unit/phase.`，但左侧表值为
Audio `2/1/1/0.8/0.6`、RF Test `2.5/1.7/1.3/1/0.8`（且 FVT=SIT），
无法与"4–5 unit/phase"对应（SKU4 时 Audio 为 1×4 = 4 台，勉强落在区间；SKU6 为 0.6×6 = 3.6 台，低于区间）。
**需要 Owner**：确认 `final` 值是否应覆盖表值；若覆盖，请给出按 SKU 的对应关系。
**Agent 当前默认**：使用表值，J9/J11 原文作为说明展示，**不自动覆盖**。

---

## 汇总表

| ID | 主题 | 严重度 | 阻塞 MVP？ | Agent 默认（非规则） |
|---|---|---|---|---|
| ORI-01 | Panel 语义冲突（定义 vs 批注） | MAJOR | **是** | 采用行 79–83 |
| ORI-02 | Certification 两套模型（主表 vs 副表；RF Cert 15 vs 8–10） | MAJOR | **是** | 采用主表 |
| ORI-03 | 第二波无判据 | MAJOR | 是（波次功能） | 用户手动开关 |
| ORI-04 | **5 SKU 永不可被单独推荐**（SKU5 ⊂ SKU4） | MAJOR | **是** | 输出 `4–5 SKU` 范围 |
| ORI-05 | ODM 无结构化规则 + 3 处 Status 未关闭 | MAJOR | 否 | ODM 仅记录不生效 |
| ORI-06 | Option 项是否启用 / PCBA 单位 | MINOR | 否 | 全不勾选，单列展示 |
| ORI-07 | Risk Reserve 无来源 | MINOR | 否 | 0% |
| ORI-08 | 权重/阈值属 Agent 设定 | MINOR | 否 | 见 §ORI-08 表 |
| ORI-09 | **无需求表样本** | MAJOR | **是**（自动读取） | 别名表为提案 |
| ORI-10 | MEPA/HW PA 为绝对量，回推不一致 | MAJOR | 否 | 按绝对量建模并标记冲突 |
| ORI-11 | G10/G12/SP/PPA standard 未提供 | MAJOR | 是（差异比较） | 只能用户上传后比较 |
| ORI-12 | 疑似"统一假设"费率（6 个 Function 共用同一组值） | MINOR | 否 | 保持 PER_SKU_RATE，登记 model question |
| ORI-13 | 定义域空洞（超出 2–6 SKU 支持域无规则） | MAJOR | 否 | 新增 `OUT_OF_DOMAIN` 拒绝态，不外推 |
| ORI-14 | 缩写确认 + Green FVT 表内自相矛盾 | MINOR | 否 | 不自行解读，FVT 按表值 0 |

> 说明：本任务**未对任何上述冲突自行择一升级为正式规则**。所有"Agent 当前默认"仅为让原型可运行的临时口径，
> 均已在 `baseline_v1.json.conflicts` 与结果页 UI 中持续暴露给使用者。
>
> **Phase 2 更新**：上表"阻塞 MVP？"一列是 Phase 1 口径。按 DEC-08，
> 目前**没有任何 ORI 阻塞手工输入 MVP 主链路**（ORI-09 / ORI-11 已解耦）；
> 全部 14 项仍阻塞 `CONFIRMED_RULE_PACK`。逐项当前状态、临时处置与解锁价值排序见
> [`13_ori_status_v2.md`](13_ori_status_v2.md)。
