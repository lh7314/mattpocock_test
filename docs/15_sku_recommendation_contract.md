# 15 — E. SKU Recommendation Contract

> 决策依据：**DEC-01**（4/5 SKU 分界）、**DEC-02**（Panel 语义）、**DEC-08**（输入不含 SKU 数量）。
> 实现：`prototype/rules_v2.py::match_sku` / `candidates_to_price`。
> 守护探针：`SR-01`…`SR-10`，其中 `SR-09` 是**必须持续失败**的设计缺口探针。

---

## 1. 输入与不变式

**输入**：`cpu` `gpu` `panel` `ssd` `mem` 五个维度，每个维度一个值或 `null`。
（SKU 数量、`Optional` 勾选、ODM 生效开关都**不在**输入契约里。）

| 不变式 | 说明 | 探针 |
|---|---|---|
| INV-1 | 用户已改值 > 文件读取值 > 未确认。`effective` 只按此序求值 | `PR-04` `PR-05` |
| INV-2 | 缺失维度保持 `null`，**永不**默认 0 / 1 / N-A；UI 显示 `请补充` | `PR-03` `SC-03` |
| INV-3 | `panel` 表示 **Panel Spec Count**，只与 SKU Definition 行 79–83 的区间比较 | `PL-01` `PL-04` |
| INV-4 | `D2:H2` 的 `N*panel` 批注不得进入匹配 | `PL-02` `PL-04` |
| INV-5 | 平局必须报范围，禁止用权重打破 | `SR-01` `SR-02` `SR-10` |
| INV-6 | 产品名、`case by case`、`Option`、Agent 推断不得进入理由 | `PR-01` |
| INV-7 | 超出支持域必须拒绝，不得外推 | `SR-08` |

---

## 2. 判定过程

```
对每个候选 SKU ∈ {2,3,4,5,6}：
  对每个维度 d ∈ {cpu, gpu, panel, ssd, mem}：
    value 为 null            -> UNKNOWN
    value ∈ [lo, hi]         -> MATCH
    value ∈ {lo-1, hi+1}     -> PARTIAL_MATCH      # 只允许一步
    否则                      -> MISMATCH
  score(SKU) = Σ VERDICT_WEIGHT[verdict] × DIM_WEIGHT[d]
             ÷ Σ DIM_WEIGHT[d]  （只对已回答维度求和）
```

**未知维度不参与分子也不参与分母**：没回答的维度既不加分也不拖分，
避免"少填一个维度反而被判得更确定"。

```python
DIM_WEIGHT     = {"cpu": 1.0, "gpu": 1.6, "panel": 1.0, "ssd": 1.4, "mem": 1.4}
VERDICT_WEIGHT = {"MATCH": 1.0, "PARTIAL_MATCH": 0.4, "MISMATCH": 0.0, "UNKNOWN": 0.0}
```

这两组常量属 **Agent 设定**（ORI-08），被探针 `SR-10` 冻结。它们的用途被 DEC-01 限定为
**仅排序**，不得用于打破平局。

---

## 3. 状态机

| 条件 | `state` | `recommended_sku` | `preferred_sku` | 计价范围 |
|---|---|---|---|---|
| 无任何维度回答 | `UNDETERMINED` | `null` | `NOT_ESTABLISHED` | 空 |
| 任一维度超出支持域 | `OUT_OF_DOMAIN` | `null` | `NOT_ESTABLISHED` | 空 |
| 最高分并列（>1 个候选） | `RANGE` | `null` | `NOT_ESTABLISHED` | **并列集合全体** |
| 唯一最高分但有维度未回答 | `SINGLE_WITH_RESERVATION` | 该候选 | 该候选 | 该候选 |
| 唯一最高分且落在 PARTIAL 带 | `SINGLE_WITH_RESERVATION` | 该候选 | 该候选 | 该候选 |
| 唯一最高分、全维度回答、全 MATCH | `SINGLE` | 该候选 | 该候选 | 该候选 |

**`RANGE` 时禁止填 `recommended_sku`**；`preferred_sku` 只能写 `"NOT_ESTABLISHED"`。
Schema 层进一步禁止：`single_value=false` 时任何单值字段必须为 `null`（探针 `SC-05`）。

---

## 4. 4 SKU / 5 SKU：本契约的核心后果

`CPU 3 · GPU 3 · Panel 2 · SSD 2 · Mem 2` 是典型平局输入：

```text
state           RANGE
tie_set         [4, 5]
score           {4: 1.0, 5: 1.0}      # 完全同分，不是接近
recommended_sku null
preferred_sku   NOT_ESTABLISHED
candidates_priced [4, 5]
```

原因（结构性，不是权重问题）：

```text
SKU5 = CPU 3–4 · GPU 3 · Panel 2 · SSD 2 · Mem 2
SKU4 = CPU 2–4 · GPU 2–3 · Panel 2 · SSD 2 · Mem 2      ⊇ SKU5
```

5 SKU 定义是 4 SKU 定义的**严格子集**：任何满足 5 SKU 的输入必然同时满足 4 SKU，
且 5 SKU 没有任何独占判别维度。扫描 405 组现实输入（cpu1–5 × gpu1–3 × panel1–3 ×
ssd1–3 × mem1–3）的结果：**5 SKU 作为唯一答案出现 0 次**。

因此本契约规定：

1. 平局 → `RANGE [4,5]`，两个 SKU 档的样机需求**都算、都输出**（FVT/SIT/Function 明细齐全）。
2. UI 上两档并列，不预选、不排序偏好、不"建议"其一。
3. `SR-09`（每个 SKU 定义都能被单独推荐）保持 `EXPECTED FAIL`，指标行持续打印
   `SKU5 unique winners = 0 over 405 realistic combinations`。
4. 关闭该探针的**唯一**路径是 Owner 提供：真实 4 SKU 项目样本、真实 5 SKU 项目样本、
   正式分界条件。**调权重不算关闭。**

> 产品期望校准：在当前 SKU Definition 下，"干净单值答案"是少数情形。
> 系统的正确形态是**频繁输出范围 + 待确认项**，这不是缺陷。

---

## 5. 输出结构

```jsonc
"match": {
  "state": "RANGE",
  "recommended_sku": null,
  "preferred_sku": "NOT_ESTABLISHED",
  "sku_range": [4, 5],
  "tie_set": [4, 5],
  "scores": { "2": 0.44, "3": 0.72, "4": 1.0, "5": 1.0, "6": 0.78 },
  "neighbour_scores": { "2": 0.44, "3": 0.72, "6": 0.78 },
  "dimension_detail": {
    "4": { "cpu":   {"verdict": "MATCH", "range": [2, 4], "weight": 1.0},
           "gpu":   {"verdict": "MATCH", "range": [2, 3], "weight": 1.6},
           "panel": {"verdict": "MATCH", "range": [2, 2], "weight": 1.0},
           "ssd":   {"verdict": "MATCH", "range": [2, 2], "weight": 1.4},
           "mem":   {"verdict": "MATCH", "range": [2, 2], "weight": 1.4} },
    "5": { ... }
  },
  "reasons": [
    "SKU 4, 5 are indistinguishable on the available evidence (score 1.0)",
    "DEC-01: the tie is reported as a range, no weighting is used to force a single answer"
  ],
  "out_of_domain": []
}
```

`dimension_detail` 让使用者逐维度看到"为什么是 4、为什么也是 5"，
而不是只看到结论。`reasons` 文案禁止出现产品系列名（探针 `PR-01`）。

---

## 6. 计价范围规则

```python
def candidates_to_price(match):
    UNDETERMINED / OUT_OF_DOMAIN -> []
    RANGE                        -> tie_set 内所有档位（升序）
    其他                          -> [recommended_sku]
```

- **不填充**：范围 `[4,5]` 不会扩展成 `[3,4,5,6]`（探针 `SR-04`）。
- 平局集合按升序输出，UI 顺序稳定。
- 每一档独立走完整算量流程（Quantity Model、Reuse、Risk Reserve、Wave）。

---

## 7. 相邻档参考

`neighbour_scores` 提供未胜出档位的得分，用于结果页"为什么不是 6 SKU"这类追问。
它**不**参与状态判定，也**不**用于把平局拆开。

---

## 8. 已知不彻底之处（不隐藏）

| 问题 | 现状 | 归属 |
|---|---|---|
| 5 SKU 不可达 | 只能输出 `4–5 SKU` | ORI-04，探针 `SR-09` 保持失败 |
| 权重与 PARTIAL 带宽（±1）是 Agent 设定 | 冻结待确认，且禁止用于打破平局 | ORI-08 |
| 支持域外输入 | 一律拒绝，不封顶也不升档 | ORI-13 |
| ODM 不参与匹配 | 仅记录 | ORI-05 |
| SKU Definition 的 Panel 语义 | 按 Spec Count 处理，批注含义未明 | ORI-01 |
