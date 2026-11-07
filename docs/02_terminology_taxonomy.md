# 02 — C. Business Terminology and Taxonomy

术语全部取自 `original_documents` 正式文件原文（单元格坐标随附）。**未从外部资料补词。**
每条标注：`[正式]` 文件内明确 / `[推断]` Agent 推断（附依据） / `[非规范]` 不作为规则。

---

## C.1 核心名词

| 术语 | 文件出处 | 本设计采用的定义 | 级别 |
|---|---|---|---|
| **SKU** | 列头 `SKU*2`…`SKU*6`（D2:H2）、`Sku Qty`（C47） | 一个项目内并行开发的**独立配置组合数**（2–6）。Agent 的**输出**，非用户输入 | [正式] |
| **SKU Definition** | 行 78 `备注：SKU Definition`，行 79–83 | 每个 SKU 档位对应的 CPU/GPU/Panel/SSD/Memory **Spec 数量区间** + 上下文注记 | [正式] |
| **Function** | A2 `Function`，B 列 21 个值 | 需要占用样机的**职能单位**；实际为两级（Category→Function），A 列是 Category | [正式]（两级结构为 [推断]，依据 A 列合并区跨度） |
| **Phase** | C2 `Phase`，取值仅 `FVT`/`SIT` | 同一 SKU 内的两个样机阶段；**MVP 只有这两个 Phase**，无 EVT/DVT/PVT | [正式] |
| **unit** | J/K 列高频（`1unit/sku`, `4-5unit/phase`） | 一台整机样机 | [正式] |
| **PCBA** | K3（`PCIE*1 PCBA`…）、K7 `其他配置给PCBA` | **主板级样机**，与整机 unit 不同计量单位；K3 明说 `remark option 的部分，还没加到样机data里面` | [正式] + **明确不计入 unit** |
| **TTL** | B48/B61/B74 `TTL SUM/phase`、J37/J43 `Total one phase on unit` | **Total 的缩写（总量）**，⚠️ **不是** Time-To-Live。术语陷阱，UI 必须写 `Total` | [正式] |
| **SUM/sku** | B45/B46/B52/B67 | 该 Phase 全部 Function 的**每 SKU 费率合计**（不是"求和每 SKU"） | [正式] |
| **Spec 数量 / key source 数量** | 行 79–83、行 92–93 `key source数量` / `CPU GPU PANEL SSD memory` | 某维度上**并行存在、需分别验证的规格/source 个数**（如 2 家 SSD supplier = SSD Spec 数量 2） | [正式]（精确判据缺失 → ORI-01） |
| **ODM** | J/K 列 `LCFC` / `HQ` / `Compal`（25 行） | 代工厂。⚠️ **无结构化 ODM 列**，差异只写在自由文本 | [正式] 概念 / 数据 [非结构化] |
| **leading（project）** | K35/K39 `the data is for leading CS project. Others less than this, case by case.` | 平台首发项目；**费率表的适用前提**。非 leading 项目应更少，但"少多少"未定义 | [正式] 限制 + [非规范] 缩减规则 |
| **第二波 / 2nd wave** | 行 80 `(or SSD/Mem spec *2, arrange 2nd wave)` | 把第 2 种 SSD/Memory Spec 延后到后一波安排，当前波不建 | [正式] 提法 / [非规范] 判据 |
| **G12 / G10 / SP** | K15 `remove it from G12`、J52 `refer to G10 G12 LCFC data`、行 88 `G12 build plan 和SP 作为经验值的数据支撑` | 历史 Build Plan 版本 / 数据来源代号。**本目录中不存在对应文件** → ORI-11 | [历史参考] |
| **PPA sample standard 1.0** | J21 `follow PPA sample standard 1.0.` | 一份**未随附**的上位标准；SWPA 数量据其制定 | [历史参考/外部依赖] → ORI-11 |
| **KP** | J27 `全套的KP`、K17 `都跟KP 强相关，理论上会要求sku*1` | 疑似 Key Platform / Key Parameter（测试覆盖项）。**文件内无定义** → ORI-14 | [用途不明缩写] |
| **TPM** | K17 `各家ODM 数据gap挺大的，跟TPM gap也有` | 疑似 Technical Program Manager | [推断] |
| **RD / PA / MFG** | A3/A21/A43 | Research&Development / **P**rocess **A**ssurance（含 SWPA/MEPA/HW PA）/ Manufacturing | [正式]（PA 全称展开为 [推断]） |
| **SED** | B15 | 文件内无定义，但内容全是 Panel 相关（x-rite、HDR cer.、panel debug、TP FW、ESI）→ 面板/显示职能 | [推断，依据 J15 全文] → ORI-14 |
| **SS** | B17 | 内容 = BIOS/EC/SA/HLK/Preload/OS → 软件职能 | [推断，依据 J17 全文] → ORI-14 |
| **HW PA / MEPA / SWPA** | B25/B23/B21 | PA 下三个子职能；MEPA 备注 `CS: 1 phase 36 units` | [正式] |
| **Certification 子类** | B27–B34 | `EMC` / `Green` / `Safety` / `RF Certification` | [正式] |
| **3rd Party Vendor 子类** | B35–B42 | `BIOS` / `ITE` / `NV` / `INTEL`（NV=NVIDIA、INTEL=Intel 平台团队） | [正式]（NV/INTEL 展开 [推断]） |
| **MFG** | B43，J43 `红丹test` | 制造职能，用途 = 红丹（蓝丹）配合测试，`Total one phase on unit` | [正式] |
| **复用 / leverage / share** | J29 `leverage safety`、J52 `can leverage sample unit`、J36/HQ `Leverage EE unit`、J29 `share 其他function 样机` | 跨 Function 共用同一台样机。文件内**只有可能性描述，无已确认复用台账** → H.5 | [正式] 概念 / 数据缺失 |
| **风险预留 Risk Reserve** | 文件内**无对应列或数值** | 任务书要求的计算项。工作簿无任何经验值 → 默认 0，须 Owner 定档 | [任务新增] |

### 产品名称（一律不作为规则条件）

`Pro`、`LOQ`、`Y5`、`Y7`、`Y9`、`N1x`、`X9`、`X11`、`G12`、`G10`、`CS`、`PCB refresh`
→ 全部只作为 SKU Definition 的**上下文注记**保留展示（K/L 层 `context_note`），
**不参与** SKU 判定（任务红线；亦是行 88 `当前是基于经验值判断的` 的必然结论）。

### 拼写与列复用（实现期必须容忍）

`Senario`(Scenario)、`Acountic`(Acoustic)、`fianl`(final)、`promition`(promotion)、`shengfei`(人名拼音)、
`TTL3- 4unit one phase`(TTL 3–4 unit/phase)、`ID.`(ID 工业设计?)、`MB1`(MB 主板?)、`B17:B18=SS` 与 `B9:B10=Audio` 等
**B 列 Function 名以原文为准**，Agent 侧另建 canonical id（`F_MEPA`、`F_SS`…），见 K。
列 **C 复用**：行 47=`Sku Qty`、行 52/67=`SUM/sku`、其余=`FVT|SIT` → 解析器必须按块解析，不能整列当枚举。

---

## C.2 Function 分类法（正式，来自 A/B 列合并结构）

```
Sample Demand
├── RD  (A3:A20, 9 functions)     HW, ME, THM, Audio, RF Test, EMC Test, SED, SS, PD
├── PA  (A21:A26, 3)              SWPA, MEPA, HW PA
├── Certification (A27:A34, 4)    EMC, Green, Safety, RF Certification
├── 3rd Party Vendor (A35:A42, 4) BIOS, ITE, NV, INTEL
└── MFG (A43:A44, 1)              MFG
                                     合计 21 Function × 2 Phase = 42 费率格 × 5 SKU = 210 个数据点
```

## C.3 Spec 维度分类法（输入侧，来自行 79–83 + 行 93）

| 维度 id | 原文 | 出现于 | 备注 |
|---|---|---|---|
| `cpu` | `CPU` | 行 79–83 全部 | 上界 5（SKU6），批注 H2 与之冲突 |
| `gpu` | `GPU` | 行 79–83 全部 | VRAM 差异相关（行 79 `VRAM match MB`） |
| `panel` | `Panel` / `Panel spec` | 行 79–83 全部 | **语义冲突未决**（ORI-01）；且非单调（1-2 → **1** → 2 → 2 → 2-3） |
| `ssd` | `SSD SPEC` | 行 79–83 全部 | 上界恒为 2 |
| `mem` | `Mem spec` | 行 79–83 全部 | 行 80 与 `ssd` 共用"第 2 spec → 第二波"分支 |
| `odm` | 行 94 `ODM` | 行 86/94 | Owner 明确列为 Input，但**无 ODM→费率**映射规则 |

Owner 行 86 给出的因果链是本设计的**主脊**：

```
source 复杂度 / ODM  ──▶  SKU 数量  ──▶  Function units 数量  ──▶  ODM UNIT
   [输入 D/E]           [输出 F/G]        [输出 H/I 明细]         [输出 I 汇总]
```

## C.4 需求成分分类法（计算侧，对应任务第六节）

| 成分 | 内部 id | 工作簿来源 | 是否可直接进入计算 |
|---|---|---|---|
| Base Demand | `base_demand` | 行 3–44 费率 × SKU 数量 | ✅ 是（唯一可自动计算项） |
| Conditional Increment | `conditional_increment` | J 列 4 处 `Option:` 块 + K3 PCBA 项 + `最高配sku*2unit` 等 | ❌ 默认 **0**；仅用户显式确认后计入 → ORI-06 |
| Confirmed Reuse Adjustment | `confirmed_reuse_adj` | 文件内**无**已确认复用记录 | ❌ 仅接受用户输入，且需防重复扣减（H.5） |
| Potential Reuse | `potential_reuse` | J29/J52/J36 的 `leverage`/`share`/`can leverage`（共 7 处） | ❌ **仅展示**，永不扣减（任务红线） |
| Applicable Risk Reserve | `risk_reserve` | 文件内无 | ❌ 默认 0，待 Owner 定档 → ORI-07 |
| Existing Plan Diff | `plan_delta` | 文件内无 Build Plan 明细（仅 J52 引用） | ⚠️ 需用户上传 → ORI-11 |

## C.5 非规范语汇表（解析器必须识别为"规则边界"，不得当规则）

自动统计（`artifacts/extraction/text_signals.md`，126 行有效文本）：

| 语汇 | 出现 | 语义 | Agent 处置 |
|---|---|---|---|
| `Option:` / `option` | 4 处小标题（HW/Audio/SED/Green），下挂 12+ 条 | 可选需求，**未纳入样机 data**（K3 原文确认） | 归入 `conditional_candidate`，默认不计数，列为"可勾选增量" |
| `case by case` | K35/K39、J15 | 视项目而定 | 标记 `NON_NORMATIVE`，只作提示 |
| `to be clarify` / `to be confirm` / `待…` | I23、I13 | 未决 | 生成 `请确认` 状态，不得用于计算 |
| `maybe` | J31 `哈萨克斯坦1pcs maybe` | 不确定量 | 丢弃为候选项 |
| `suggest` | J13 `shengfei suggest: …` | 个人建议 | 记录为证据，不升级 |
| `gap比较大` / `数量偏少` | I25、I17 | 数据分歧未解决 | 降低该 Function 置信度（H.7） |
| `can leverage` / `Leverage` / `share` | 7 处 | 复用可能性 | `potential_reuse` 展示 |
| `是否…?` `跟team 去check?` `PM confirm` | K15 | 待决策 | 转 ORI |
| `fianl : LCFC/HQ/Compal 都可按照4-5unit/phase` | J9、J11 | 已议定但**与左侧数字不一致**（Audio 表值 2/1/1/0.8/0.6，4-5 unit/phase 无法对应） | 记为 ORI-14(c)，不自动覆盖表值 |
| `refer to G10 G12 … range 34--36 units` | J52 | 外部锚点 | 只作校验参考（见 01 B.5 不自洽） |

## C.6 缩写歧义登记（须 Owner 确认，否则 UI 无法给出中文标签）

| 缩写 | Agent 猜测 | 依据 | 若猜错的后果 |
|---|---|---|---|
| `CS` | Consumer Slim / CS 机型线 | K23 `CS: 1 phase 36 units`、Sheet 名 `CS ODM sample`、B1 标题 | MEPA 适用范围判断错误 |
| `KP` | Key Platform | J27/K17 语境为送样覆盖单位 | 认证需求算错 |
| `DN` | Declared Nomination? (`越南DN1`) | J29 | Green 需求算错 |
| `BCS` / `CEL` / `TDMS` / `HLK` / `PQL` / `ESI` / `EA` | 未定义 | J29/J13/J17 | 条件增量无法自动匹配 |
| `HQ` | ODM 名 | J/K 列与 LCFC/Compal 并列 | ODM 维度整体失效 |
| `MB` | Motherboard | 行 79 `VRAM match MB1` | SKU2 判定辅助信息误读 |
| `ID.` | Industrial Design | 行 83 `ID./ME*2` | SKU6 复杂度解释误读 |

> **实现约定**：上表任何缩写**不得**被写进面向用户的中文标签，除非 Owner 确认。默认直接展示原文。
