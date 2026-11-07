# 05 — H. Sample Demand Calculation Model（含 D-01 小数策略）

已批准决策 **D-01**：所有中间量与最终值按小数计算，不取整。显示精度统一，但不得改变底层值。
本章公式在 `prototype/rules_v1.py::finalise()` 中实现，`tools/validate_rules.py` 有 4 条 D-01 断言。

---

## H.1 主公式

```
Base Demand(f, phase)                = rate(f, phase, SKU) × SKU_qty        ← 唯一可自动计算项
+ Conditional Increment(f, phase)    = Σ 用户已确认的 Option / 自定义额外需求
+ Confirmed Reuse Adjustment(f,ph)   = − 已确认复用台数
+ Applicable Risk Reserve(f, phase)  = (Base + Conditional + ConfirmedReuse) × risk_pct(f, phase)
────────────────────────────────────────────────────────────────────────────
= Recommended Sample Demand(f, phase)

Total = Σ_f Σ_phase Recommended(f, phase)          （FVT / SIT 分别汇总）
```

**Potential Reuse 不在公式内**，仅作为展示项（任务红线，已断言：`potential reuse does not reduce demand`）。

## H.2 Base Demand 的费率来源与可复算性

工作簿行 45/46/48/49 的公式即此模型，Agent 复算结果与缓存值**逐格 0 误差**：

| SKU | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|
| SUM/sku FVT | 86.5 | 65.5 | 52.85 | 45.2 | 40.3 |
| SUM/sku SIT | 96 | 73.5 | 58.1 | 49.6 | 44.2 |
| TTL FVT | 173 | 196.5 | 211.4 | 226 | 241.8 |
| TTL SIT | 192 | 220.5 | 232.4 | 248 | 265.2 |
| **合计** | **365** | **417** | **443.8** | **474** | **507** |

> Agent 必须能逐格复现上表，否则说明解析或映射出错 —— 已固化为不变量
> `workbook grand totals reproduce (SKU2..6)`、`recommended total grows with SKU count`。

## H.3 Phase 拆分：不用全局比例

21 个 Function 中 **17 个 FVT/SIT 费率完全相同**（对称），只有 4 个 Certification 项不对称：

| Function | FVT rate | SIT rate | 特征 |
|---|---|---|---|
| EMC | 0 | 1 | 认证全部落在 SIT |
| Green | 0 | 3 / 3 / 1.5 / 1.2 / 1 | 同上 |
| RF Certification | 0 | 7.5 / 5 / 3.75 / 3 / 2.5 | 同上 |
| Safety | 5 / 3 / 2.5 / 2 / 1.6 | 3 / 2 / 1.5 / 1.2 / 1 | **FVT > SIT**，与其余相反 |

→ **禁止**用"FVT = 40% / SIT = 60%"这类全局拆分。
实现方式：`rate` 本身就是 `(function, phase, sku)` 三维查表，FVT/SIT 拆分是**查表结果**而非二次分配。
SKU 结果输出范围时，FVT/SIT 同步输出范围（例：`3–5 SKU → FVT 196.5–226.0`）。

## H.4 规模经济：必须用查表，禁止固定单价外推

对每个 Function 拟合 `TTL ∝ SKU^b`（`tools/analyze_baseline.py` 输出）：

| Function | b（总量对 SKU） | Function | b |
|---|---|---|---|
| SWPA | +0.546 | MEPA | +0.107 |
| SS | +0.349 | ME / PD / BIOS / ITE / MFG | +0.166 |
| HW | +0.273 | THM | +0.026 |
| SED | +0.608 | EMC Test | **0.000** |
| HW PA | +0.675 | RF Test | **−0.037** |
| EMC(cert) | +1.000 | Audio | **−0.096** |

含义：

- **总量亚线性增长**（多数 0 < b < 0.7），因为费率本身随 SKU 递减（`b_rate ≈ b_TTL − 1`）。
- **3 个 Function 总量随 SKU 增加反而下降或不变**（Audio、RF Test、EMC Test）。
  → 表内**已经内含"多 SKU 共享台数"的假设**。
  **后果**：Agent 若再叠加"复用扣减"，就是**重复扣减** → 见 H.5。
- **禁止**：`rate(SKU=7) = rate(SKU=6)`、或 `TTL(N) = TTL(6) × N/6`。
  超出 2–6 定义域时 → `暂无法计算` + 说明（不擅自拟合外推）→ ORI-13。
- **允许**：对 SKU **列之间**做插值仅当 Owner 明确允许（MVP：不允许，SKU 只有 5 个离散档）。

## H.5 Reuse 语义（防重复扣减）

| 类型 | 来源 | 处理 |
|---|---|---|
| **Confirmed Reuse** | 用户明确输入（哪台/哪个 Function/哪个 Phase 可复用） | 进入公式，**负向**，且**必须落到具体 Function×Phase 行**；只给总数时按 Base Demand 比例分摊并标注 `分配方式为 Agent 推断` |
| **Potential Reuse** | J 列 `can leverage` / `share` / `Leverage`（7 处）+ 用户填写 | **仅展示**：`另有 N 台可复用机会未扣减，若确认请转为 Confirmed` |

内置校验（防越界与重复扣减）：

```
confirmed_reuse(f, phase) ≤ base_demand(f, phase) + conditional(f, phase)
若某 Function 已属于"总量不随 SKU 增长"类（Audio/RF Test/EMC Test，H.4 b ≤ 0）
  → 额外提示：该 Function 基线已含共享假设，请确认复用未重复计算
```

## H.6 D-01 小数策略（实现级约定）

| 层 | 规则 |
|---|---|
| 存储 | 全程 `REAL`/`float`，**不做** `round()`；原始缓存值原样保留（含 `65.49999999999999` 这类源表尾差） |
| 计算 | 不引入 `int()`、不做显示性四舍五入参与运算 |
| 显示 | 统一 `1` 位小数（可切换 2 位）；`443.8` 显示 `443.8`，`226.00000000000009` 显示 `226.0` |
| 容差比较 | 一律用 `abs(a-b) ≤ 1e-9`，禁止 `==`（源表即有 1e-14 尾差） |
| 导出 | CSV/JSON 输出**全精度**原值 + 一列 `display` 展示值，避免下游再次取整 |
| UI 文案 | 明示"按小数计算，未取整（D-01）"，避免用户以为可以按台数直接下单 |

示例（实测）：4 SKU、+1.0 条件增量、−0.5 已确认复用、5% 风险预留

```
base 443.8  FVT 211.4  SIT 232.4  cond 1.0  reuse −0.5  risk 22.215000
→ recommended 466.515000        （不显示为 467，也不显示 466.5 参与后续运算）
```

## H.7 Conditional Increment 的启用规则（当前默认全部关闭）

工作簿 J 列 4 个 `Option:` 块 + K3 PCBA 项，共 12+ 条候选（`artifacts/extraction/text_signals.md §A`）。
K3 原文明确：`remark option 的部分，还没加到样机data里面。` → **官方确认这些量未计入基线**。

| 候选项（原文摘录） | 出处 | 可计数量 | 默认 |
|---|---|---|---|
| `Smart AMP: add 1 unit` | J9 Audio | +1.0/phase | OFF |
| `Battery team 1*vendor*sku*phase for Q test for new source` | J3 HW | 公式化：1×vendor×sku×phase | OFF |
| `CPU OC *2 & GPU OC *2 /phase`（LCFC/Compal）；`HQ: Leverage EE unit.` | J3 HW | +4.0/phase（LCFC/Compal），HQ=0 | OFF |
| `Camera win Hello cer. unit(for IR feature)` | J15 SED | 未定量 | OFF |
| `TP FW Tuning*3/ FVT` | J15 SED | +3.0 仅 FVT | OFF |
| `ESI test: LCFC need … 2 unit` | J15 SED | +2.0（LCFC 限定） | OFF |
| `EPEAT: 5unit` / `E-Star9.0 *1` / `UL golden*1` / `eyesafe/LBL/HGPD Golden*N（N=Panel 数）` | J29 Green | 定量，其中 1 项与 Panel 数联动 | OFF |
| `PCIE*1 PCBA … VRAM tuning*7`（**PCBA 单位，非 unit**） | K3 HW | 不可与 unit 相加 | OFF + 单位隔离 |

规则：

1. 默认 **OFF**（任务：`Option` 不得视为确定规则）；
2. 用户勾选才计入，且记录 `rule_id = OPTION:<function>:<序号>` + 原文引用；
3. **单位隔离**：PCBA 项永不与 unit 项相加，单独一区展示；
4. 与 Panel/CPU/SKU 联动的项（eyesafe N=Panel 数、Battery 1×vendor×sku×phase）标注为**公式型**，
   其联动变量缺失 → 该项状态 `请补充`，不计入。

## H.8 Risk Reserve

文件内**无任何**风险预留经验值 → `risk_pct` 默认 **0.0**，UI 不提供"猜一个"的默认值。
Owner 若给档，需明确：按 Function 级还是总量级、是否只对 CERT 类生效（认证送样失败重测最典型的预留场景）。→ **ORI-07**

## H.9 与现有 ODM / TPM Build Plan 的差异比较（MVP 轻量版）

只做**同一 Function×Phase 粒度**的三方对照，不做审批、不做版本链：

| 列 | 来源 |
|---|---|
| Agent Recommended | 本模型输出 |
| Existing Plan | 用户上传/粘贴（列名映射失败则让用户手工对应一次，记住该映射） |
| Δ = Agent − Plan | 小数 |
| Δ% | Δ / Plan（Plan=0 时显示 `N/A`，不显示 ∞） |
| 说明 | 引用该 Function 的 Status 原文（如 `HQ gap比较大`、`待LCFC update`）作为**已知不确定性提示** |

排序：按 `|Δ|` 降序，默认只展示 Top 10 + "展开全部"。
基线自身 Status 未关闭的 Function（`EMC Test`、`MEPA`、`HW PA`）在差异行加 `基线未确认` 标记，避免用户把基线误差读成 ODM 偏差。

## H.10 计算侧不变量（已在 `validate_rules.py` 断言）

```
[PASS] workbook grand totals reproduce (SKU2..6)          365 / 417 / 443.8 / 474 / 507
[PASS] recommended total grows with SKU count             365.0 -> 507.0
[PASS] D-01: decimals preserved, never rounded to int     SKU4 base=443.8（不是 444）
[PASS] D-01: fractional risk reserve not rounded          22.19
[PASS] potential reuse does not reduce demand             base=443.8 rec=443.8
[PASS] confirmed reuse does reduce demand
```

待补（需 Owner 定档后实现）：`risk_pct` 生效路径、Option 项启用后的单位隔离测试、Build Plan 差异符号约定。
