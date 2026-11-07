# 04 — F. SKU Definition Model ＋ G. SKU Recommendation & Conflict Resolution Logic

输入 = 5 个 Key Factor（**不含** SKU 数量）；输出 = Recommended SKU / 范围 / 暂无法建议。
本章逻辑可在 `prototype/rules_v1.py::match_sku()` 运行，量化结果来自 `tools/validate_rules.py` 的 3,205 组合扫描。

---

# F. SKU Definition Model

## F.1 基线（唯一正式来源：行 79–83，逐格解析，原文存于 `baseline_v1.json`）

| 维度 | 2 SKU | 3 SKU | 4 SKU | 5 SKU | 6 SKU |
|---|---|---|---|---|---|
| **CPU** | 1–2 | 2–3 | 2–4 | 3–4 | **4–5** |
| **GPU** | 1 | 2 | 2–3 | 3 | 3 |
| **Panel Spec** | 1–2 | **1** | 2 | 2 | 2–3 |
| **SSD Spec** | 1 | 1 | 2 | 2 | 2 |
| **Mem Spec** | 1 | 1 | 2 | 2 | 2–3 |
| 上下文注记 | `VRAM match MB1 1-2 Source/X9/X11`；`N1x/Y9 source少，Volume 少` | `(or SSD/Mem spec *2, arrange 2nd wave)`；`Y7 DIS` | `Pro/LOQ /Y5` | `Pro/LOQ /Y5` | `ID./ME*2 ，Pro上` |

> 上下文注记**只作展示与追溯**，不进入判定（任务红线 + 行 88 `当前是基于经验值判断的`）。

## F.2 结构分析：重叠、单调性、判别力（自动计算，非人工印象）

**(a) 区间重叠矩阵**（同一维度上，哪些 SKU 档接受同一个值）

| 维度 | 值→可匹配的 SKU 档 | 判别力 |
|---|---|---|
| CPU | 1→{2} · 2→{2,3,4} · 3→{3,4,5} · 4→{4,5,6} · 5→{6} | **弱**（仅 1、5 唯一） |
| GPU | 1→{2} · 2→{3,4} · 3→{4,5,6} | **中** |
| Panel | 1→{2,3} · 2→{2,4,5,6} · 3→{6} | **中**（但见 (c) 反常） |
| SSD | 1→{2,3} · 2→{4,5,6} | **强**（1 vs 2 一刀切开 3/4 SKU） |
| Mem | 1→{2,3} · 2→{4,5,6} · 3→{6} | **强** |

→ **判别力排序：SSD ≈ Mem > GPU > Panel > CPU。**
单一维度**没有任何一个**能独立定档（实测：`ssd` 单独输入时 3/4 取值均为 `RANGE`）。
→ 任务要求"不得只按单一字段推荐"在数学上是**必然**的，不只是流程要求。

**(b) 包含关系（导致不可达）**

```
SKU5 定义 (CPU 3-4, GPU 3, Panel 2, SSD 2, Mem 2)
   ⊆  SKU4 定义 (CPU 2-4, GPU 2-3, Panel 2, SSD 2, Mem 2)     ← 全维度被包含
SKU3 定义 (CPU 2-3, GPU 2, Panel 1, SSD 1, Mem 1)
   ⊆  SKU2 定义 (CPU 1-2, GPU 1, Panel 1-2, SSD 1, Mem 1)？   ← 否，GPU=2 不在 {1} 内，两者互斥
```

**后果（实测）**：在 405 组"现实取值"空间（CPU 1-5 / GPU 1-3 / Panel 1-3 / SSD 1-3 / Mem 1-3）中，

```
SKU2: 唯一胜出 83 次
SKU3: 唯一胜出 39 次
SKU4: 唯一胜出 147 次
SKU5: 唯一胜出  0 次   ← 只能以 "4-5" 范围形式出现 29 次
SKU6: 唯一胜出 105 次
```

> **这是可证明的结构性缺陷，不是实现 bug**：当前 SKU Definition 下 **5 SKU 永远无法被单独推荐**，
> 只能以 `4–5 SKU` 范围出现。→ **ORI-04（阻塞"单一推荐"能力）**。
> 修复需要 Owner 给出 4 SKU 与 5 SKU 的**判别维度**（例如：总 source 数阈值、是否含水冷、ID/ME 变体数、面板 source 家数），
> 或明确承认"4–5 一律输出范围"。

**(c) Panel 反常**：`2 SKU: 1-2 → 3 SKU: 1` 出现**下降**，违反"SKU 越多、可覆盖 Spec 越多"的单调预期。
配合 (a)：`Panel=2` 会把 3 SKU **完全排除**。若某项目 CPU/GPU/SSD/Mem 都指向 3 SKU 而 Panel 有 2 个 Spec，
当前规则会推荐 3 SKU（Panel 记 PARTIAL_MATCH）还是 4 SKU？→ 由 G.3 权重决定，属**可调参数** → **ORI-01**。

**(d) 定义域空洞**：SSD/Mem 的上界恒为 2（除 Mem@6SKU=3），CPU/GPU/Panel 有上界 4/5/6。
若项目 SSD Spec=3，当前 5 档定义**全部不覆盖** → 只能 `UNDETERMINED` 或提示"超出已定义范围" → ORI-13。

## F.3 正式数据模型

```jsonc
{
  "sku_definition_id": "SKUDEF-CS-001",
  "version": "v1.0-draft",
  "status": "DRAFT_UNCONFIRMED_BY_OWNER",
  "source": {"file": "…V01_FORMAL.xlsx", "sha256": "48A360FF…", "sheet": "CS ODM sample ",
             "rows": {"SKU2": 79, "SKU3": 80, "SKU4": 81, "SKU5": 82, "SKU6": 83}},
  "tiers": [
    {"sku": 4, "ranges": {"cpu": [2,4], "gpu": [2,3], "panel": [2,2], "ssd": [2,2], "mem": [2,2]},
     "context_note": "Pro/LOQ /Y5", "second_wave_option": false,
     "conflicts": ["ORI-01: 表头批注 F2 写 4*panel"]}
  ],
  "dimension_weights": {"cpu": 1.0, "gpu": 1.6, "panel": 1.0, "ssd": 1.4, "mem": 1.4},
  "conflict_refs": ["ORI-01","ORI-02","ORI-03","ORI-04","ORI-13"]
}
```

---

# G. SKU Recommendation and Conflict Resolution Logic

## G.1 判定单元：每维度 × 每 SKU 档

| 判定 | 条件 | 得分 |
|---|---|---|
| `MATCH` | `lo ≤ value ≤ hi` | 1.0 |
| `PARTIAL_MATCH` | `value ∈ {lo−1, hi+1}`（**相邻一档**） | 0.4 |
| `MISMATCH` | 其余 | 0.0 |
| `UNKNOWN` | 该维度未读取且未选择 | **不计入分母** |

维度权重（`DIM_WEIGHT`，MVP 初值，需 Owner 确认）：`gpu 1.6 > ssd 1.4 = mem 1.4 > cpu 1.0 = panel 1.0`
依据 = F.2(a) 的判别力排序 + 行 86 `source复杂度` 把 GPU 视为主要复杂度来源（`VRAM match MB` 注记亦指向 GPU 侧）。
**此权重是 Agent 设定，非文件规定** → **ORI-08**。

## G.2 候选评分与状态机

```
score(candidate) = Σ_d weight_d × verdict_score_d      （d 仅取已知维度）
normalized       = score / Σ_d weight_d
best             = max(normalized)
winners          = {c | normalized_c = best}
```

| 条件 | 输出状态 | 用户可见 |
|---|---|---|
| 无任何已知维度 | `UNDETERMINED` | **暂无法计算** + 5 个"请补充" |
| `best = 1.0` 且单一 winner 且无缺失维度 | `SINGLE` | 单一推荐（如 `4 SKU`） |
| `best < 1.0` 或存在缺失维度 | `SINGLE_WITH_RESERVATION` | 单一推荐 + **请确认** |
| 多 winner 并列 | `RANGE` | 范围建议（如 `4–5 SKU`） |
| `best = 0` | `UNDETERMINED` | 暂无法计算（输入与全部定义冲突） |

**不做**的事：不取中点、不四舍五入成单值、不在并列时用"就近取低/取高"伪装确定性。

## G.3 冲突消解优先级（与任务证据优先级一致）

```
1. Owner 已确认的正式规则            ← 当前为空（尚无 Review 结论）
2. 正式文件内的数值矩阵（行 3–44）    ← 费率权威来源
3. 文件内明确的规则/说明/Comment      ← 行 79–83 定义、D2:H2 批注、J/K 说明
4. 历史参考（G10/G12、PPA standard、产品名） ← 仅展示，不改算
5. Agent 推断（维度权重、PARTIAL 阈值）      ← 必须显式标记
```

同级冲突（如 ORI-01 批注 vs 行 79–83、ORI-02 主表 vs 副表）→ **不消解，降级为 `请确认` 并输出双值**，
绝不静默择一。当前 MVP 因此对 ORI-01 采取：**沿用行 79–83 作为默认（数值矩阵可复算性更强），
同时在结果页与 ORI 面板持续展示批注口径差异**。这是"不阻塞使用但不假装已解决"的折中，需 Owner 复核。

## G.4 输出契约（每个候选都给全，满足任务第五节）

```jsonc
{
  "recommended_sku": 4,
  "state": "SINGLE_WITH_RESERVATION",
  "match_degree": {"cpu": "MATCH", "gpu": "MATCH", "panel": "MATCH", "ssd": "MISMATCH", "mem": "MISMATCH"},
  "score": 0.76,
  "basis": ["ssd=2 vs [1,1] -> MISMATCH", "…"],          // 主要判断依据（逐维）
  "neighbors": [
    {"sku": 2, "normalized": 0.74, "why_not": "lower weighted match"},
    {"sku": 5, "normalized": 0.56, "why_not": "hard mismatch on cpu"}
  ],
  "missing_or_competing": ["ssd/mem 双 2 但 gpu=1，指向 4SKU 与 2SKU 竞争（T-13）"],
  "input_source": {"cpu": "FILE", "gpu": "FILE", "panel": "USER", "ssd": "FILE", "mem": "FILE"},
  "unresolved_conflicts": ["ORI-01", "ORI-04"]
}
```

## G.5 实测场景矩阵（15 例，完整输出见 `artifacts/validation/validation_report.md`）

| 案例 | 输入 (cpu/gpu/panel/ssd/mem) | 状态 | 结果 | 关键说明 |
|---|---|---|---|---|
| T-01 正向 | 3/2/2/2/2 | `SINGLE` | **4 SKU** | 唯一 norm=1.00；SKU5=0.85 因 gpu |
| T-02 正向 | 1/1/1/1/1 | `SINGLE` | **2 SKU** | 1.00 vs SKU3 0.76 |
| T-03 正向 | 2/2/1/1/1 | `SINGLE` | **3 SKU** | 1.00 vs SKU2 0.85 |
| T-04 正向 | 5/3/3/2/3 | `SINGLE` | **6 SKU** | 1.00；SKU4/5 均 0.68 |
| T-05 边界 | 4/2/2/2/2 | `SINGLE` | **4 SKU** | CPU 处于 4SKU 上界 |
| T-06 边界 | 4/1/2/2/2 | `SINGLE_WITH_RESERVATION` | 4 SKU (0.85) | GPU=1 与 4/5/6 档硬冲突 |
| T-07 边界 | 2/2/2/1/1 | `SINGLE_WITH_RESERVATION` | 3 SKU (0.91) | **Panel=2 使 3SKU 由 MATCH 变 PARTIAL**，F.2(c) |
| T-08 边界 | 6/5/4/4/4 | `SINGLE_WITH_RESERVATION` | 6 SKU (0.21) | 全维越界 → 提示超出定义域 ORI-13 |
| T-09 边界 | 1/1/1/1/2 | `SINGLE_WITH_RESERVATION` | 2 SKU (0.87) | Mem=2 单维越界 |
| T-10 缺失 | 3/2/–/2/2 | `SINGLE_WITH_RESERVATION` | 4 SKU (1.00) | Panel 缺失→`请补充`，不计分母 |
| T-11 缺失 | 3/–/–/–/– | `RANGE` | **3–5 SKU** | 三维并列 1.00，正确拒绝给单值 |
| T-12 缺失 | 全无 | `UNDETERMINED` | — | `no key factor supplied` |
| T-13 竞争 | 2/1/1/2/2 | `SINGLE_WITH_RESERVATION` | 4 SKU (0.76) vs 2 SKU (0.74) | **ssd/mem 指向 4，cpu/gpu/panel 指向 2**，差距 <0.03 |
| T-14 第二波 | 2/2/1/2/2 | `SINGLE_WITH_RESERVATION` | 4 SKU (0.91) | **未声明**波次时的默认行为；声明后为 3 / 4 双口径（G.6，已实算） |
| T-15 竞争 | 2/2/1/1/1 | `SINGLE` | 3 SKU | CPU=2 跨 2/3/4 档，被 GPU/Panel 定档 |

**T-13 是设计红线用例**：0.76 vs 0.74 差距 0.02。MVP 规则：
`0 < best − runner_up < 0.05` 时**强制降级为 RANGE**（或 `请确认`），即使形式上存在单一 winner。
该阈值属 Agent 设定 → ORI-08。（当前实现在 T-13 输出单值 4 SKU，故 §G.3 的"竞争提示"必须同时展示 2 SKU 为竞争者；
若 Owner 希望强制 RANGE，仅需调整此阈值，已在 `runner_up_excluded` 中留好结构。）

## G.6 第二波（Current Wave vs Full Project）

行 80 原文：`3SKU: 2-3*CPU +2*GPU+ 1*Panel spec +SSD SPEC*1 +Mem spec *1 (or SSD/Mem spec *2, arrange 2nd wave)`

**波次感知评估**（原型 `match_sku(wave=…)`）：

| 波次口径 | 对 ssd/mem 的解释 | 同一输入 `2/2/1/2/2` 的输出 |
|---|---|---|
| `current`（默认） | 第 2 个 SSD/Mem Spec **尚未安排**，不计入当前波规格数 → ssd/mem 视为 1 | **Current Wave = 3 SKU** |
| `full_project` | 第 2 个 Spec 计入 → ssd/mem = 2 | **Full Project = 4 SKU** |

因此 T-14 的正确输出是**两行**，而不是一个数：

```
Current Wave Recommended SKU : 3 SKU     （依据：SSD/Mem 第 2 种 Spec 已安排至第二波）
Full Project Recommended SKU : 4 SKU     （依据：第 2 种 Spec 在整项目范围内计入）
样机需求：分别输出 3 SKU 与 4 SKU 的对应范围，不做加权平均
```

**限制**：波次是用户显式声明的开关；文件内没有"哪些 Spec 属于第二波"的判定规则 → **ORI-03**。
该双口径已由回归断言覆盖（`second wave splits into two SKU views: current=3 full=4`），且波次**只改变参与匹配的 Spec 数量，不改变任何 Function 费率**（`second wave does not change base rates`）。

## G.7 量化模糊性（必须让 Owner 知道的现实）

对 2,800 组宽域取值（cpu1-7/gpu1-5/panel1-5/ssd1-4/mem1-4）扫描：

| 状态 | 占比 | 含义 |
|---|---|---|
| `SINGLE`（无任何保留） | **0.6%** | 完全落在唯一档位内 |
| `SINGLE_WITH_RESERVATION` | 85.6% | 有单值，但存在 PARTIAL 或缺失维度 |
| `RANGE` | 13.8% | 并列，输出范围 |
| `UNDETERMINED` | 0.0%（宽域内 0；空输入时 100%） | — |

**结论**：在 Owner 补齐判别规则前，"干净的单一推荐"几乎不存在（0.6%）。
这**不是**算法不够聪明，而是 SKU Definition 区间天然高度重叠（F.2a）。
→ 产品预期应设为"**默认给范围 + 理由 + 待确认项**，单一值只在完全匹配时给出"，
与任务要求"当 SKU 为范围时同步输出范围、不生成伪精确单一总数"完全一致。
