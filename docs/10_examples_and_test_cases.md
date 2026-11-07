# 10 — 输入示例 / SKU 推荐示例 / 输出示例 / 测试案例

本文件**所有数值由 `prototype/rules_v1.py` 实算产出**（不是手算），完整输出见
`artifacts/validation/validation_report.md`、`artifacts/validation/worked_examples.md`。
重跑：`python tools\validate_rules.py` ／ `python tools\gen_examples.py`。

---

## 1. 输入示例

### 1.1 需求表自动读取成功（用户未修改）

```yaml
project: Sample-X
odm: LCFC                    # 仅记录，MVP 不参与计算（ORI-05）
key_factors:
  cpu:   {file_value: 3, file_confidence: 0.95, user_edited: false}   # 已读取
  gpu:   {file_value: 2, file_confidence: 0.95, user_edited: false}   # 已读取
  panel: {file_value: 2, file_confidence: 0.92, user_edited: false}   # 已读取
  ssd:   {file_value: 2, file_confidence: 0.90, user_edited: false}
  mem:   {file_value: 2, file_confidence: 0.90, user_edited: false}
confirmed_reuse: 0.0
potential_reuse: 0.0
optional_confirmed: []
wave_scope: CURRENT
```

### 1.2 部分读取 + 用户修改 + 缺失

```yaml
key_factors:
  cpu:   {file_value: 3,  user_edited: false}                       # 已读取
  gpu:   {file_value: 2,  user_value: 3, user_edited: true}         # 用户已修改（原读取值 2）
  panel: {file_value: null, user_value: 2, user_edited: true}       # 用户已修改（原：未读取到）
  ssd:   {file_value: 2,  user_edited: false}
  mem:   {file_value: null, user_edited: false}                     # 请补充（绝不默认）
confirmed_reuse: 0.5          # 已确认：SIT 阶段 0.5 台可复用
potential_reuse: 10.0         # 潜在机会，仅展示
optional_confirmed:
  - {id: OPTION:AUDIO:1, label: "Smart AMP: add 1 unit", qty: 1.0, source_cell: "J9"}
risk_reserve_pct: 0.05
```

### 1.3 第二波配置

```yaml
key_factors:
  cpu: {file_value: 2}
  gpu: {file_value: 2}
  panel: {file_value: 1}
  ssd: {file_value: 2, second_wave_deferred: true}   # 第 2 种 SSD Spec 已安排第二波
  mem: {file_value: 2, second_wave_deferred: true}
# 需同时产出两个口径（ORI-03：波次目前由用户声明）
```

---

## 2. SKU 推荐示例

### 2.1 单一推荐（实算）

输入 `cpu=3 gpu=2 panel=2 ssd=2 mem=2` →

```
state       = SINGLE
recommended = 4 SKU
候选得分     SKU4=1.00  SKU5=0.85  SKU6=0.76  SKU3=0.64  SKU2=0.49
相邻候选     SKU5(0.85) 未推荐原因：gpu=2 落在 5SKU 定义[3,3] 之外（MISMATCH）
输入来源     cpu=FILE gpu=FILE panel=FILE ssd=FILE mem=FILE
未关闭冲突    ORI-01（Panel 口径）, ORI-04
```

### 2.2 范围建议（实算）

输入 `cpu=3`（其余 4 维请补充）→

```
state       = RANGE
range       = 3–5 SKU   （tie=[3,4,5]，各自 normalized=1.00）
请补充       gpu, panel, ssd, mem
样机需求      同步输出范围：Total 417 – 474；FVT 196.5 – 226；SIT 220.5 – 248
（绝不输出 445.5 这类伪精确中点）
```

### 2.3 暂无法建议（实算）

```
输入：全部缺失 → state=UNDETERMINED, reason="no key factor supplied"
UI：暂无法计算 + 5 行"请补充"
```

### 2.4 竞争案例（实算，对应 T-13）

输入 `cpu=2 gpu=1 panel=1 ssd=2 mem=2` →

```
state = SINGLE_WITH_RESERVATION, recommended = 4
SKU4=0.76   SKU2=0.74   ← 差距 0.02
竞争解读：ssd/mem=2 指向 4/5/6 SKU；cpu/gpu/panel 指向 2 SKU
处置：结果页固定展示 SKU2 为竞争候选及其理由；
      若 Owner 将竞争阈值(0.05)设为强制降级 → 输出 "2 或 4 SKU，请确认"（见 ORI-08）
```

---

## 3. 样机需求输出示例（页面 3 默认视图）

```
推荐 SKU：4 SKU                                    基线版本 v1.0-draft（未确认）
判断依据：GPU 2 命中(2–3)｜CPU 3 命中(2–4)｜Panel 2 命中｜SSD 2 命中｜Memory 2 命中

建议样机需求（按小数计算，未取整 · D-01）
   总计        466.990 台
   FVT         211.4 台
   SIT         232.4 台
   = 基础需求 443.8 + 额外需求 1.0 − 已确认复用 0.5 + 风险预留 22.190
   可复用机会 10.0 台（仅提示，未扣减）

分类汇总   RD 132.8 ｜ PA 240.0 ｜ Certification 41.0 ｜ 3rd Party Vendor 28.0 ｜ MFG 2.0

待确认（4）
 · Memory Spec 数量未读取到 → 请补充
 · EMC Test 基线未关闭：「待LCFC update」
 · MEPA 基线未关闭：「LCFC:Confirmed ok / HQ,Compal:to be clarify」，且主表 32 与副表 36 不一致（ORI-10）
 · RF Certification 存在两套口径：主表恒定 15 vs 副表 8–10（ORI-02）—— 本次按主表计算
```

<details><summary>对应的 Function/Phase 明细（21×2=42 行，节选，全量见 worked_examples.md）</summary>

| Function | Cat | Phase | 费率/SKU | ×SKU | Base |
|---|---|---|---|---|---|
| HW | RD | FVT | 3.5 | 4 | 14 |
| HW | RD | SIT | 3.5 | 4 | 14 |
| ME | RD | FVT | 0.25 | 4 | 1 |
| THM | RD | FVT | 1.8 | 4 | 7.2 |
| Audio | RD | FVT | 1.0 | 4 | 4 |
| RF Test | RD | FVT | 1.3 | 4 | 5.2 |
| EMC Test | RD | FVT | 1.5 | 4 | 6 |
| SED | RD | FVT | 1.5 | 4 | 6 |
| SS | RD | FVT | 5.5 | 4 | 22 |
| SWPA | PA | FVT | 20.0 | 4 | 80 |
| MEPA | PA | FVT | 9.0 | 4 | 36 |
| HW PA | PA | FVT | 1.0 | 4 | 4 |
| EMC | CERT | SIT | 1.0 | 4 | 4 |
| Green | CERT | SIT | 1.5 | 4 | 6 |
| Safety | CERT | FVT | 2.5 | 4 | 10 |
| Safety | CERT | SIT | 1.5 | 4 | 6 |
| RF Certification | CERT | SIT | 3.75 | 4 | 15 |
| BIOS | VENDOR | FVT | 0.25 | 4 | 1 |
| NV | VENDOR | FVT | 1.5 | 4 | 6 |
| INTEL | VENDOR | SIT | 1.5 | 4 | 6 |
| MFG | MFG | FVT | 0.25 | 4 | 1 |

</details>

---

## 4. 测试案例

### 4.1 正向案例（Happy Path）

| ID | 输入 | 期望 | 实算 | 结果 |
|---|---|---|---|---|
| P-01 | 1/1/1/1/1 | 2 SKU，Total 365 | SINGLE 2 → 365.0 | ✅ |
| P-02 | 2/2/1/1/1 | 3 SKU，Total 417 | SINGLE 3 → 417.0 | ✅ |
| P-03 | 3/2/2/2/2 | 4 SKU，Total 443.8 | SINGLE 4 → 443.8 | ✅ |
| P-04 | 3/3/2/2/2 | 5 SKU **或** 4–5 范围 | RANGE 4–5 | ✅ 符合 ORI-04 降级行为 |
| P-05 | 5/3/3/2/3 | 6 SKU，Total 507 | SINGLE 6 → 507.0 | ✅ |
| P-06 | P-03 + 复用 0.5 + 额外 1.0 + 风险 5% | 小数链路完整 | 466.990 | ✅ |

### 4.2 边界案例

| ID | 输入 | 期望行为 | 实算 |
|---|---|---|---|
| B-01 | 4/2/2/2/2（CPU 处 4SKU 上界） | 单一 4 SKU | SINGLE 4 ✅ |
| B-02 | 4/1/2/2/2（GPU 低于所有高档定义） | 带保留，标注 gpu 硬冲突 | SINGLE_WITH_RESERVATION 4（0.85）✅ |
| B-03 | 2/2/**2**/1/1（Panel=2 与 3SKU 定义"1"冲突） | Panel=PARTIAL，结果仍需提示 Panel 口径待确认 | SWR 3（0.91）✅ |
| B-04 | 1/1/1/1/**2**（仅 Mem 越界） | 带保留 | SWR 2（0.87）✅ |
| B-05 | 6/5/4/4/4（全维超出定义域） | 强制带保留 / 提示超出范围，**不外推** | SWR 6（0.21）✅ |
| B-06 | 4/3/2/2/2（同时命中 4 与 5 定义） | 输出范围 4–5，不给单值 | RANGE ✅ |
| B-07 | 小数复用 0.5 台 | 保留小数，不进位 | ✅ |
| B-08 | 复用 > 该行需求 | 拒绝/截断并报错 | ⏳ 待 P3 实现（校验规则见 05 §H.5） |

### 4.3 缺失输入案例

| ID | 缺失 | 期望 | 实算 |
|---|---|---|---|
| M-01 | 缺 Panel | `请补充`；结果带保留；**Panel 不默认 0/1** | SWR 4 + `请补充: panel` ✅ |
| M-02 | 仅剩 CPU=3 | **RANGE 3–5** + 4 项请补充 | RANGE [3,5] ✅ |
| M-03 | 全缺 | `UNDETERMINED`，不产生任何数字 | ✅ |
| M-04 | 读到空值/`-`/`N/A`/`TBD` | 一律 `请补充`，不得映射为 0 | 设计规则（E.4），待 P5 实现 |
| M-05 | 读到区间 `2-3` | `请确认`，不取中点/不取上界 | 设计规则（E.4），待 P5 实现 |

### 4.4 SKU Definition 竞争案例

| ID | 输入 | 冲突描述 | 期望处置 |
|---|---|---|---|
| C-01 | 2/1/1/2/2 | ssd+mem→4/5/6；cpu+gpu+panel→2 | 显示 0.76 vs 0.74 双候选，`请确认`（实算 SWR 4）✅ |
| C-02 | 4/3/2/2/2 | 4 与 5 定义重叠（SKU5⊂SKU4） | 输出 `4–5 SKU`（ORI-04）✅ |
| C-03 | 任意 + Panel=2 | 定义(2) vs 批注(4*panel) 冲突 | 按定义计算 + 固定横幅提示 ORI-01 ✅ |
| C-04 | 3/3/2/2/**3** | Mem=3 只有 6SKU 覆盖，其余维度指向 4/5 | 结果带保留，列出 Mem 为关键分歧点 ✅（SWR） |
| C-05 | 2/2/1/**2**/**2** | 行 80 括注分支：SSD/Mem 第 2 Spec → 第二波 | 未声明波次 → 4 SKU(SWR 0.91)；声明后 → Current **3** / Full **4** 双口径（✅实算，见 4.5） |

### 4.5 第二波配置案例

| ID | 场景 | Current Wave | Full Project |
|---|---|---|---|
| W-01 | 3SKU 基线 + SSD/Mem 第 2 Spec 已安排第二波 | **3 SKU**（417.0）✅实算 | **4 SKU**（443.8）✅实算 |
| W-02 | 同上，但用户未勾选"已安排第二波" | 4 SKU（443.8） | 4 SKU（443.8） |
| W-03 | SSD 第二波、Mem 无第 2 Spec | 3 SKU | 4 SKU |
| W-04 | 波次不明 | 必须提示"波次未声明"，只输出单口径 | — |

输出形态（不得合并为单一数字）：

```
Current Wave Recommended SKU : 3 SKU    样机需求 Total 417.0（FVT 196.5 / SIT 220.5）
Full Project Recommended SKU : 4 SKU    样机需求 Total 443.8（FVT 211.4 / SIT 232.4）
依据：SSD/Mem 第 2 种 Spec 已安排至第二波（行 80 括注）；波次由用户声明，非系统判定（ORI-03）
```

### 4.6 回归不变量（自动化，Phase 1 套件 15/16 PASS）

> **Phase 2 已扩为 70 条探针**：`tools/validate_rules_v2.py` →
> `artifacts/validation/regression_report_v2.md`（含逐条 Expected / Actual / Verdict），
> 说明与预期 PASS/FAIL 清单见 `docs/19_regression_v2.md`，
> 走输入契约的 11 个新用例见 `artifacts/validation/worked_examples_v2.md`。
> 下面列出的 Phase 1 不变量仍然有效并被 v2 套件覆盖或加强。

```
[PASS] workbook grand totals reproduce (SKU2..6)
[PASS] recommended total grows with SKU count
[PASS] D-01: decimals preserved, never rounded to int
[PASS] D-01: fractional risk reserve not rounded
[PASS] missing field never defaults to 0/1
[PASS] user value overrides file value
[PASS] file value retained alongside user value
[PASS] potential reuse does not reduce demand
[PASS] confirmed reuse does reduce demand
[PASS] empty input -> UNDETERMINED
[PASS] tie -> RANGE, not a fake single number
[PASS] second wave splits into two SKU views          current=3 / full=4
[PASS] second wave does not change base rates         417.0 / 443.8
[PASS] PCBA rules are excluded from UNIT totals       (单位隔离)
[PASS] no product series token in judgement           (Pro/LOQ/Y5/... 不进入判定)
[FAIL] every SKU definition is reachable as a unique recommendation
       ↑ 刻意保留的 ORI-04 探针（SKU5 ⊂ SKU4，唯一胜出 0 次）。
         Owner 关闭 ORI-04 前应保持 FAIL，不得改断言使其变绿。
```
