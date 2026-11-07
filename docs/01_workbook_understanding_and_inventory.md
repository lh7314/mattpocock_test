# 01 — A. Current Workbook Understanding ＋ B. Field & Structure Inventory

依据优先级：本文件全部数值来自 `original_documents` 正式文件的直接解析结果
（`artifacts/extraction/`），复算脚本 `tools/analyze_baseline.py`、`tools/build_baseline_dataset.py`。

---

# A. Current Workbook Understanding

## A.1 正式输入范围清单（第一步交付，先于业务结构调查）

递归扫描 `original_documents`（含隐藏文件）：

| # | 文件名 | 类型 | 相对路径 | 大小(B) | 修改时间 | SHA-256 |
|---|---|---|---|---|---|---|
| 1 | `Sample_Requirement_SKU_and_Demand_Baseline_CleanSheet_20261030_V01_FORMAL.xlsx` | xlsx (OOXML, 未加密, 无宏) | `original_documents/…V01_FORMAL.xlsx` | 26,839 | 2026-11-02 10:33:08 | `48A360FF2FFD086E41D6B90A916F64FE52D9BC13EFBA07B8377B2945C846AB5A` |

目录内**仅此 1 个文件，0 个子目录**。因此：

- **重复文件：无**（不存在多版本，故无需版本比较；SHA 比较结论=不适用）。
- **临时文件（`~$*`、`.tmp`、`.asd`）：无。**
- **无法读取 / 用途不明：无。**
- **建议正式输入范围：本文件 = 正式业务输入（Formal Business Input），单一来源。**
  分类依据：Owner 在本任务中显式指定该目录与"Owner 提供的样机需求工作簿"；文件名带 `FORMAL` 且标注 `CleanSheet`；
  文件内部结构完整（表头/Status/Purpose/Remark/SKU Definition 齐备），非草稿形态。
- 文件同时**内含历史参考内容**（`G12`、`G10`、`PPA sample standard 1.0`、`refer to G10 G12 LCFC data`、`Y7 DIS`、
  `VRAM match MB1 1-2 Source/X9/X11`）。这些是**同一文件内的历史参考层**，不升级为正式规则（见 C.4、ORI-11）。

> ⚠ 单一文件即唯一正式输入 = 当前**没有**可交叉验证的第二来源。工作簿内部的两套副表（B.5）是唯一的内部对照，
> 且它们与主表冲突。这意味着"正式规则"的可信边界比看起来更窄，必须靠 Owner Review 补齐。

## A.2 文件画像（OOXML 元数据，非业务结论）

| 属性 | 值 | 说明 |
|---|---|---|
| Worksheet 数量 | **1** — `CS ODM sample `（**名称含尾随空格**） | `app.xml` `TitlesOfParts` 与 `workbook.xml` 一致 |
| sheetId / 可见性 | 6 / `visible`；无 hidden sheet | — |
| 使用范围 | `A1:L95`；`autoFilter = A2:K49`；`freeze` 无 | L 列**无任何内容**（phantom 列） |
| 非空单元格 | 515 | 见 `artifacts/extraction/*.json` |
| 合并区域 | 91 | 见 B.2 |
| 隐藏行/列 | 0 / 0 | 无隐藏数据 |
| 公式 | 12 个 SUM/乘法公式（行 45/46/48/49/61/62/74/75），全部含缓存值 | 见 B.4 |
| 批注 | 5 条 threaded comment（作者 **Lingyu LY3 Rong**，2026-06-24）+ 5 条 legacy 镜像 | **不是注释掉的空值，是有效业务信息** |
| defined name | `_xlnm._FilterDatabase` = `'CS ODM sample '!$A$2:$K$49` (hidden) | 仅是筛选器残留 |
| 作者链 | `dc:creator = William HC`（2015-06-05 建模板）→ `lastModifiedBy = Lingyu LY3 Rong`（2026-10-30 08:51 UTC） | 表格模板 2015 年历史，内容为近期填充 |
| 上游路径 | SharePoint `…/rly0310/stamp/data breakdown/9月份最新final/` | 说明本表由"9 月最新 final 数据拆分"衍生的 CleanSheet；**上游原始 Build Plan 未在本目录中** → ORI-11 |

## A.3 这张表在业务上是什么

**一句话：一张"每 SKU 单价表"（unit-per-SKU rate card），不是样机需求清单。**

计算骨架（行 45–49，工作簿内自带公式，已复算一致）：

```
SUM/sku(phase)  = Σ 21 个 Function 的 unit-per-SKU 费率
TTL SUM/phase   = SUM/sku(phase) × Sku Qty(行47)
```

| SKU Qty | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|
| SUM/sku **FVT** | 86.5 | 65.5 | 52.85 | 45.2 | 40.3 |
| SUM/sku **SIT** | 96.0 | 73.5 | 58.1 | 49.6 | 44.2 |
| **TTL FVT** | 173 | 196.5 | 211.4 | 226 | 241.8 |
| **TTL SIT** | 192 | 220.5 | 232.4 | 248 | 265.2 |
| **TOTAL/phase-pair** | **365** | **417** | **443.8** | **474** | **507** |

三个必须让 Owner 知道的结构性事实（均已用 `tools/analyze_baseline.py` 验证）：

1. **费率随 SKU 增多而下降，总量随 SKU 增多而上升（亚线性）。**
   对每个 Function 拟合 `TTL ∝ SKU^b`，`b` 介于 **−0.10（Audio）～ +0.68（HW PA）**，
   即"每加一个 SKU 的边际成本递减"。→ **禁止**用固定单价 × SKU 数做外推（见 H.4）。
2. **FVT 与 SIT 的费率在 21 个 Function 中有 17 个完全相同**，只有 4 个 Certification 类 Function 不同
   （`EMC` FVT=0/SIT=1、`Green` 0/3→1、`Safety` 5/3、`RF Certification` 0/7.5）。
   → Phase 差异**不是**全局比例系数，而是 4 个 Function 的局部特性（见 H.3）。
3. **浮点尾差真实存在**：`E45` 缓存值 `65.49999999999999`、`G48` `226.00000000000009`、
   `E49` `220.49999999999994`。→ D-01（不取整）下，显示层必须统一精度，底层保留原值（见 H.6）。

## A.4 文件内部的三层结构（同一 Sheet 内 4 个块）

| 块 | 行范围 | 内容 | 是否进入总量公式 | 业务地位 |
|---|---|---|---|---|
| **B1 主表** | 2–49 | 21 Function × 2 Phase 的 unit-per-SKU 费率 + SUM/sku + TTL | **是**（行 45/46/48/49） | 正式规则主来源 |
| **B2 Certification 副表** | 51–62 | 4 个 Certification Function 的**绝对 units/phase** + TTL | 独立行 61/62，**不**并入主表 | 与 B1 冲突 → ORI-02 |
| **B3 PA 副表** | 66–75 | 3 个 PA Function 的绝对 units/phase | 独立行 74/75 | B1 的**换算校验**（15/16 格一致） |
| **B4 SKU Definition + 设计意图** | 78–95 | 2–6 SKU 定义、行 86–95 的 Input→Output 概念图 | 否 | SKU 规则主来源 + 产品意图证据 |

行 86–95 是 Owner 亲笔写的**本 Agent 设计意图**（原文照录）：

```
86: source复杂度/ODM 是哪家 --SKU数量-> Function units 数量-->ODM UNIT
88: source的复杂度到sku的数量，当前是基于经验值判断的。   |  G12 build plan 和SP 作为经验值的数据支撑
91: Input                          |  output
92: key source数量                 |  Sku 数量
93: CPU GPU PANEL  SSD memory      |  推荐Build plan
94: ODM                            |  各个function 数量
95:                                |  total的数量
```

→ 本次任务的输入/输出设计与 Owner 既有意图**完全对齐**（Input=5 个 Key Factor + ODM；Output=SKU→Function 明细→Total）。
行 88 同时是**关键限制**：Owner 自己声明 source→SKU 目前是**经验值**，非确定规则。

---

# B. Workbook Field and Structure Inventory

## B.1 表头与字段清单（行 1–2）

| 列 | 表头 | 类型 | 语义 | Agent 映射 |
|---|---|---|---|---|
| A | `Function`（行2）/ 行1 标题 `CleanSheet Project By Senario/By SKU Qty Breakdown` | 文本(合并) | 一级分类：`RD`/`PA`/`Certification`/`3rd Party Vendor`/`MFG` | `function.category` |
| B | （无表头，行2 为空） | 文本(合并) | **二级 Function 名**（21 个，唯一标识） | `function.name` |
| C | `Phase` | 枚举 | `FVT` / `SIT` / `Sku Qty`（行47 复用该列）/ `SUM/sku`（行52/67 复用） | `demand.phase` |
| D–H | `SKU*2` `SKU*3` `SKU*4` `SKU*5` `SKU*6` | 浮点 | **该 Function 在该 Phase、该 SKU 档位下，每个 SKU 需要的 unit 数** | `per_sku_rate` |
| I | `Status` | 自由文本 | 数据可信度/ODM 确认状态，非空仅 7 处 | `confidence` / ORI 触发 |
| J | `Purpose and Explanation` | 自由文本 | 计算构成解释、**含 Option: 条件项、ODM 差异、L/T** | 规则证据 + 条件增量候选 |
| K | `Remark` | 自由文本 | 补充/例外/未决问题/PCBA 项 | 条件增量候选 + 未决项 |
| L | （无） | — | 空列 | 忽略 |

## B.2 合并单元格的结构含义（91 处，抽样归类）

| 合并模式 | 示例 | 含义 / 风险 |
|---|---|---|
| A 列跨 14–18 行 | `A3:A20=RD`, `A21:A26=PA`, `A27:A34=Certification`, `A35:A42=3rd Party Vendor`, `A43:A44=MFG` | 一级分类。解析时必须向下填充，否则 21 行中 16 行 category 为空 |
| B 列成对跨 2 行 | `B3:B4=HW`, `B17:B18=SS` … 共 21 处 | **每个 Function 占 2 行 = FVT + SIT**。解析器若按行取值会漏掉 SIT 的 Function 名 |
| I/K 列跨多行且**值为空** | `I35:I44=""`, `I28:I34=""`, `K21:K22=""`, `K11:K12=""` | 视觉上"分组留空"，易被误判为"无 Status"。**空字符串 ≠ 无该字段**，须记录为 `explicit_empty` |
| `A1:K1` | 标题 | 报表标题 |
| `C79:J79` … `C83:J83` | SKU Definition 单行长文本 | **一行一 SKU**，中间用大量空格分隔"定义"与"上下文注记"，非结构化 |
| `J9:J10`、`J21:J26`、`J31:J32` | 多行文本 | 一个 J 合并区覆盖 2–6 行 → 文本**不能**按行 1:1 归属，须按合并区归属 |
| `J52:J62` | Certification 副表解释 | 覆盖 11 行，是 B2 的唯一说明 |
| `K39:K42` | `the data is for leading CS project. Others less than this, case by case.` | 覆盖 NV + INTEL 两行；**这是适用范围限制，不是规则** |

## B.3 21 个 Function 完整清单（含状态与数据特征）

`Sym` = FVT/SIT 费率是否完全相同；`ΣTTL` = 该 Function 在 SKU2→SKU6 的总量区间。

| # | 行 | Category | Function (B列原文) | Sym | unit/SKU FVT (2→6) | unit/SKU SIT (2→6) | ΣTTL(SKU2→SKU6) | Status 原文 |
|---|---|---|---|---|---|---|---|---|
| 1 | 3 | RD | HW | ✓ | 6 / 4.3 / 3.5 / 3 / 2.7 | 同 FVT | 12 → 16.2 | `OK` |
| 2 | 5 | RD | ME | ✓ | 0.5 / 0.3 / 0.25 / 0.2 / 0.2 | 同 FVT | 1 → 1.2 | — |
| 3 | 7 | RD | THM | ✓ | 3.5 / 2.3 / 1.8 / 1.4 / 1.2 | 同 FVT | 7 → 7.2 | `ok`(行8) |
| 4 | 9 | RD | Audio | ✓ | 2 / 1 / 1 / 0.8 / 0.6 | 同 FVT | 4 → 3.6 ↓ | — |
| 5 | 11 | RD | RF Test | ✓ | 2.5 / 1.7 / 1.3 / 1 / 0.8 | 同 FVT | 5 → 4.8 ↓ | — |
| 6 | 13 | RD | EMC Test | ✓ | 3 / 2 / 1.5 / 1.2 / 1 | 同 FVT | 6 → 6 | **`待LCFC update`** |
| 7 | 15 | RD | SED | ✓ | 2 / 1.7 / 1.5 / 1.4 / 1.3 | 同 FVT | 4 → 7.8 | — |
| 8 | 17 | RD | SS | ✓ | 9 / 7 / 5.5 / 5 / 4.4 | 同 FVT | 18 → 26.4 | `LCFC BIOS and SA 建议根据复杂度，4-6unit/phase. HQ 数量偏少` |
| 9 | 19 | RD | PD | ✓ | 0.5 / 0.3 / 0.25 / 0.2 / 0.2 | 同 FVT | 1 → 1.2 | — |
| 10 | 21 | PA | SWPA | ✓ | 28 / 24 / 20 / 18 / 17 | 同 FVT | 56 → 102 | — |
| 11 | 23 | PA | MEPA | ✓ | 16 / 12 / 9 / 7.2 / 6 | 同 FVT | 32 → 36 | `LCFC:Confirmed ok as left data. HQ/Compal:to be clarify.` |
| 12 | 25 | PA | HW PA | ✓ | 1 / 1 / 1 / 0.8 / 0.7 | 同 FVT | 2 → 4.2 | **`HQ gap比较大`** |
| 13 | 27 | Certification | EMC | ✗ | 0（全档） | 1（全档） | 2 → 6 | — |
| 14 | 29 | Certification | Green | ✗ | 0（全档） | 3 / 3 / 1.5 / 1.2 / 1 | 6 → 6 | — |
| 15 | 31 | Certification | Safety | ✗ | 5 / 3 / 2.5 / 2 / 1.6 | 3 / 2 / 1.5 / 1.2 / 1 | 10 → 9.6 / 6 → 6 | — |
| 16 | 33 | Certification | RF Certification | ✗ | 0（全档） | 7.5 / 5 / 3.75 / 3 / 2.5 | 15（恒定） | — |
| 17 | 35 | 3rd Party Vendor | BIOS | ✓ | 0.5 / 0.3 / 0.25 / 0.2 / 0.2 | 同 FVT | 1 → 1.2 | — |
| 18 | 37 | 3rd Party Vendor | ITE | ✓ | 0.5 / 0.3 / 0.25 / 0.2 / 0.2 | 同 FVT | 1 → 1.2 | — |
| 19 | 39 | 3rd Party Vendor | NV | ✓ | 3 / 2 / 1.5 / 1.2 / 1 | 同 FVT | 6 → 6 | — |
| 20 | 41 | 3rd Party Vendor | INTEL | ✓ | 3 / 2 / 1.5 / 1.2 / 1 | 同 FVT | 6 → 6 | — |
| 21 | 43 | MFG | MFG | ✓ | 0.5 / 0.3 / 0.25 / 0.2 / 0.2 | 同 FVT | 1 → 1.2 | — |

数据特征（对建模有后果）：

- **4 个 Function 的费率在 5 档完全相同**（`EMC`=1、`Green` FVT=0、`RF Cert` FVT=0、`EMC/Green/RF` FVT=0）→ 它们不是"每 SKU 费率"，实为**每 phase 固定量**（`EMC` SIT=1/SKU 恰好等价）。
- **3 个 Function 的总量随 SKU 增加而下降**（Audio 4→3.6、RF Test 5→4.8、Safety FVT 10→9.6）→ 表内**已内含规模经济/共享台数**假设，Agent 不得再加"复用扣减"，否则重复扣减（→ H.5）。
- **6 个 Function 共用同一组值** `0.5/0.3/0.25/0.2/0.2`（ME、PD、BIOS、ITE、MFG + 同型）→ 高度疑似**占位/统一假设**，非逐项实测（→ ORI-12）。
- **`Certification` 4 项在 FVT 全为 0**（EMC/Green/RF Cert）→ 表内假设"认证样机集中在 SIT"，与 J29 `FVT for RD 内测,leverage safety.` 矛盾（→ ORI-14）。

## B.4 公式与计算结果（12 处，全部复算一致）

| 单元格 | 公式 | 缓存值 | 复算 |
|---|---|---|---|
| `D45…H45` | `=SUM(D3+D5+D7+…+D43)`（仅**奇数行**=FVT 行，21 项） | 86.5 / 65.49999999999999 / 52.85 / 45.20000000000002 / 40.30000000000001 | ✓ 0 误差 |
| `D46…H46` | `=SUM(D4+D6+…+D44)`（仅**偶数行**=SIT 行，21 项） | 96 / 73.49999999999999 / 58.1 / 49.60000000000002 / 44.20000000000001 | ✓ 0 误差 |
| `D47…H47` | 常量 `2,3,4,5,6` | — | SKU Qty 锚点行 |
| `D48…H48` | `=D45*D47` | 173 / 196.49999999999994 / 211.4 / 226.00000000000009 / 241.80000000000007 | ✓ |
| `D49…H49` | `=D46*D47` | 192 / 220.49999999999994 / 232.4 / 248.0000000000001 / 265.20000000000005 | ✓ |
| `D61…H61` | `=SUM(D53+D55+D57+D59)` | 10 / 9 / 10 / 10 / 10 | ✓ B2 FVT |
| `D62…H62` | `=SUM(D54+D56+D58+D60)` | 22 / 24 / 26 / 27 / 28 | ✓ B2 SIT |
| `D74…H74` | `=SUM(D68+D70+D72)` | 94 / 111 / 120 / 130 / 142 | ✓ B3 FVT |
| `D75…H75` | `=SUM(D69+D71+D73)` | 94 / 111 / 120 / 130 / 142 | ✓ B3 SIT |

> **注意**：主表总量（365/417/443.8/474/507）**已经包含** B1 内的 Certification 行（行 28/30/32/34，SIT）。
> 若再把 B2（行 61/62）加进去即为**重复计算**。B2 是否应替换 B1 的 Certification，是 ORI-02 的核心。
> B3 的量与 B1 换算后一致（见 B.5），不产生重复计算问题。

## B.5 主表 vs 副表：逐格差异（自动比对，`baseline_v1.json → conflicts`）

**B3 PA 副表**（15/16 格一致 → 判定为换算校验表）：

| 项 | 副表绝对值 | 主表 费率×SKU | 差异 |
|---|---|---|---|
| MEPA FVT/SIT @SKU2 | 36 | 16×2 = 32 | **+4.0** |
| HW PA FVT/SIT @SKU6 | 4 | 0.7×6 = 4.2 | −0.2 |
| 其余 SWPA/MEPA/HW PA 全档 | 完全一致 | — | 0 |

- MEPA 副表全档恒定 36，且 K23 原文 `CS: 1 phase 36 units / PCB refresh: 1 phase 12-16units.`
  → **MEPA 本质是"每 phase 绝对量 36"，被除回 SKU 数时产生 16/12/9/7.2/6 的伪费率。**
  SKU=2 时 36/2=18 而表内写 16（16×2=32≠36）→ 该行是**回填不一致**（→ ORI-10）。
- HW PA 0.7 = round(4/6,1)=round(0.667,1)，属**显示精度回填**产物 → 若 Agent 再用 0.7×6 计算得 4.2，与源表 4 不符。
  证明"先定绝对量、再除以 SKU 数并四舍五入"的反推路径，也证明 **D-01 必须保留底层值、只在显示层统一精度**。

**B2 Certification 副表**（4 项中 2 项冲突，MAJOR）：

| Function/Phase | 副表(SKU2→6) | 主表费率×SKU | 差异 | 判定 |
|---|---|---|---|---|
| EMC SIT | 2 / 3 / 4 / 5 / 6 | 1×SKU = 2/3/4/5/6 | 0 | 一致 |
| Green SIT | 6 / **6** / 6 / 6 / 6 | 6 / **9** / 6 / 6 / 6 | SKU3: **−3** | **MAJOR** |
| Safety FVT | 10 / 9 / 10 / 10 / **10** | 10 / 9 / 10 / 10 / **9.6** | SKU6: +0.4 | MINOR（精度） |
| Safety SIT | 6 / 6 / 6 / 6 / 6 | 6×5 | 0 | 一致 |
| RF Cert SIT | 8 / 9 / 10 / 10 / 10 | **恒 15** | −7 / −6 / −5 / −5 / −5 | **MAJOR ×5** |
| **TTL FVT / SIT** | 10/9/10/10/10 与 22/24/26/27/28 | 10/9/10/10/9.6 与 29/33/31/32/32.6 | SIT 差 5–7 台 | — |

- **RF Certification 是真正的模型分歧**，不是精度问题：主表隐含"恒定 15 台/phase"，副表是"8→10 封顶增长"。
  J33 原文（`this data for 2 antenna source +2 wlan source refrence… SRRC*2 / CE*4=antenna*wlan / FCC(wlan*antenna)*4 / 印尼*2 / Mexico*1 / 资安*2`）
  按其自述 2+2 source 组合算得 2+4+4+2+1+2=15 → **主表 15 = 该 source 组合下的展开式**；副表 8–10 是另一口径（未说明）。
  → 两条规则互斥，Owner 必须择一（→ ORI-02）。
- J52 原文 `refer to G10 G12 LCFC data: WW certification including promition: range 34--36 units`：
  副表 FVT+SIT 合计 = 32/33/36/37/38，**仅 SKU3–SKU5 落在 34–36 区间内** → 副表自身与其经验锚点也不完全自洽（→ ORI-11）。

## B.6 SKU Definition 原文（行 79–83）与表头批注（D2:H2）

自动解析（`baseline_v1.json → sku_definition`），原文逐字符保留于 JSON：

| SKU | 行 | 解析出的范围（CPU/GPU/Panel/SSD/Mem） | 原文上下文注记 |
|---|---|---|---|
| 2 | 79 | 1–2 / 1 / 1–2 / 1 / 1 | `VRAM match MB1 1-2 Source/X9/X11.` `N1x/Y9 source少，Volume 少` |
| 3 | 80 | 2–3 / 2 / 1 / 1 / 1 | `(or SSD/Mem spec *2, arrange 2nd wave)` `Y7 DIS` |
| 4 | 81 | 2–4 / 2–3 / 2 / 2 / 2 | `Pro/LOQ /Y5` |
| 5 | 82 | 3–4 / 3 / 2 / 2 / 2 | `Pro/LOQ /Y5` |
| 6 | 83 | 4–5 / 3 / 2–3 / 2 / 2–3 | `ID./ME*2 ，Pro上` |

表头 threaded comment（作者 Lingyu LY3 Rong，2026-06-24 08:52–08:54，逐条时间递增）：

| Cell | SKU | 原文 | Panel vs 行 79–83 | CPU / GPU vs 行 79–83 |
|---|---|---|---|---|
| D2 | 2 | `2*panel+1*CPU+1*GPU` | 2 vs 1–2 → 落在区间内 ✓ | 1 vs 1–2 ✓ / 1 vs 1 ✓ |
| E2 | 3 | `3*panel+2*CPU+2*GPU` | **3 vs 1** ✗ | 2 vs 2–3 ✓ / 2 vs 2 ✓ |
| F2 | 4 | `4*panel+2*CPU+2*GPU` | **4 vs 2** ✗ | 2 vs 2–4 ✓ / 2 vs 2–3 ✓ |
| G2 | 5 | `5*panel+3*CPU+3*GPU` | **5 vs 2** ✗ | 3 vs 3–4 ✓ / 3 vs 3 ✓ |
| H2 | 6 | `6*panel+3*CPU+3*GPU` | **6 vs 2–3** ✗ | **3 vs 4–5** ✗ / 3 vs 3 ✓ |

→ **4 处 Panel 硬冲突 + 1 处 CPU 硬冲突**（SKU6 批注 CPU=3，定义要求 4–5）。
批注位于**表头行**（SKU 列标题），按文档语义属于"列含义说明"，权威度不低于行 79–83 的备注块；
Agent **不得自行择一**（→ **ORI-01**，阻塞项）。

## B.7 已确认不存在的内容（避免 Owner 重复追问）

| 任务要求检查项 | 是否存在 | 说明 |
|---|---|---|
| 多个 Worksheet | ✗ | 仅 1 个 |
| 隐藏行 / 隐藏列 / 隐藏 Sheet | ✗ | 均为 0 |
| 白色字体白底（WHITE_ON_WHITE）隐藏文本 | ✗ | 解析器已检测，0 命中 |
| 超链接 / 外部链接 | ✗ | 仅 `printerSettings1.bin`、`vmlDrawing1.vml`（批注绘图） |
| 数据有效性下拉（Data Validation） | ✗ | 无下拉枚举可继承 |
| 条件格式驱动的状态色 | 未使用为语义 | Status 语义在文本里，不在颜色里 |
| ODM 专属列（LCFC/HQ/Compal 分列） | ✗ | **ODM 差异只存在于 J/K/I 自由文本**（25 行），无结构化字段 → E.6、ORI-05 |
| 独立 Optional Requirement 列 | ✗ | 仅 J 列内 4 处 `Option:` 小标题（HW/Audio/SED/Green）→ ORI-06 |
| Certification/PA/3rd Party/MFG 分文件 | ✗ | 均在同一 Sheet |
| 第二波（2nd wave）结构化字段 | ✗ | 仅行 80 一句 `(or SSD/Mem spec *2, arrange 2nd wave)` → ORI-03 |
| 需求表模板（供用户上传的 Key Factor 表） | ✗ | **本目录内不存在**任何"需求表样例" → **ORI-09，阻塞自动读取功能** |
