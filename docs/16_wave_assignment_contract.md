# 16 — F. Wave Assignment Contract

> 决策依据：**DEC-04**。实现：`prototype/rules_v2.py` 的 `Spec` / `KeyFactor.normalise_specs`
> / `wave_scenarios`。守护探针：`WV-01`…`WV-10`、`SC-06`、`SC-07`。

---

## 1. 一句话契约

**Wave 只能被"声明"，不能被"推断"。**
引擎只把**明确标记为 `LATER_WAVE`** 的 Spec 排除出 Current Wave；
其余一律留在 Current Wave，并把"没说过"这件事作为待确认项持续显示。

---

## 2. 值域

```text
Wave        = CURRENT_WAVE | LATER_WAVE | UNKNOWN
WaveSource  = FORMAL_REQUIREMENT_SHEET   # 正式需求表明确标记
            | USER_SELECTED              # 用户在本工具里显式选择
            | IMPLICIT_SINGLE_SPEC       # 该维度只有 1 颗 Spec（见 §5）
            | NOT_PROVIDED               # 无人说过
```

只有前两种来源算"有依据"。`NOT_PROVIDED` 的 Spec 留在 Current Wave，
并生成 ORI `WAVE_ASSIGNMENT_NOT_PROVIDED`。

**Wave 挂在 Spec 上，不挂在维度上。** 一个维度有两颗 Spec 时必须逐颗指定，
不存在"SSD 维度属于第二波"这种粗粒度说法。

---

## 3. 明令禁止的推断

| 禁止动作 | 原因 | 探针 |
|---|---|---|
| 因为 SSD Spec = 2 就认为第 2 颗属于第二波 | 这正是 Owner 明令禁止的推断；会把答案从 4 SKU 错降为 3 SKU | `WV-05` |
| 因为 Memory Spec = 2 就套用 3 SKU 的 `arrange 2nd wave` 条款 | 该条款是原表括号里的说明文字，没有判据，属 ORI-03 | `WV-05` |
| 对 Current Wave 应用固定比例折减 | 波次只改变**参与计算的 Spec 数量**，不改变任何费率 | `WV-03` `WV-04` |
| 对 Current Wave 减去固定台数 | 同上 | `WV-04` |
| 让 Wave 影响 Quantity Model 或基础数值 | 同上 | `WV-03` |

引擎里**不存在任何按波次的比例常量或固定折减常量**。Current Wave 就是"用更少的 Spec 数量把同一张表重算一遍"。

`WV-04` 直接对比：同一 SKU 档，声明波次与否，每一行 `base_demand` 与 `TOTAL` 完全相同
（4 SKU 档同为 `443.8`）。

---

## 4. 两个分析口径

| 口径 | Spec 集合 | 何时需要 Wave |
|---|---|---|
| `FULL_PROJECT` | 全部 Spec（= 用户输入的五维数量） | 不需要，永不排除 |
| `CURRENT_WAVE` | 排除**明确** `LATER_WAVE` 的 Spec；`UNKNOWN` 的 Spec 做扇出 | 需要声明或显式 UNKNOWN |

两个口径**同时输出、并列展示**，不相互替代。若两者数量向量相同，
`CURRENT_WAVE` 场景打 `identical_to_full_project = true`，UI 可标"当前与全项目一致"，
但**仍然展示**（探针 `WV-09`），因为"一致"本身是 Owner 关心的结论。

---

## 5. 三种输入结果

### 5.1 全部明确标注（`WV-01`/`WV-02`/`WV-10`）

输入 `CPU2 GPU2 Panel1 SSD2 Mem2`，第二颗 SSD 与第二颗 Mem 标 `LATER_WAVE`：

| 口径 | 生效数量 | SKU 答案 |
|---|---|---|
| `CURRENT_WAVE` | `CPU2 GPU2 Panel1 SSD1 Mem1` | **3 SKU**（`SINGLE`） |
| `FULL_PROJECT` | `CPU2 GPU2 Panel1 SSD2 Mem2` | **4 SKU**（`SINGLE_WITH_RESERVATION`） |

这是波次声明**确实承载结论**的证据（`WV-10`）：波次没变就只是装饰。

### 5.2 完全没标注（`WV-05`）

同一输入但不标注：Current Wave **不**缩到 `SSD1 Mem1`，而是等于 Full Project（4 SKU），
并产生 `WAVE_ASSIGNMENT_NOT_PROVIDED`，文案要点：

> 这些 Factor 有多颗 Spec，但需求表没说每颗属于哪一波；目前按全部属于当前波处理，
> 因此 Current Wave 暂时等于 Full Project。Agent 不会推断第二波（DEC-04），
> 请确认波次，或接受当前读法。

### 5.3 显式标 UNKNOWN（`WV-06`）

Owner/需求表明确说"第二颗待定"时，Current Wave **扇出**成多个场景，
每个场景独立出 SKU 答案与数量，并产生一个 `WAVE_ASSIGNMENT_UNKNOWN`
（去重后一条，附 `scenario_ids` 说明影响面）。

示例（`EX-F`）：SSD 第二颗与 Mem 第二颗各标 `UNKNOWN` → 4 个 Current Wave 场景，
答案落在 `3 SKU` 与 `4 SKU` 两种读法上。这就是 Owner 要求的"UNKNOWN 产生范围"。

扇出上限 `MAX_WAVE_COMBOS = 32`；超限折叠为两个极值场景并置 `truncated = true`。
折叠只是**限制算力开销**，不改变"范围"这一结论性质。

---

## 6. 唯一允许的推断：`IMPLICIT_SINGLE_SPEC`

某维度只有 1 颗 Spec 时，可排除集合天然为空，Current Wave 必然包含它。
这不是对未来波次的猜测，而是对"没有东西可排除"的陈述。

- 已在 `wave_source` 中显式标注，UI 可见。
- Owner 若认为"唯一那颗也可能属于第二波"，推翻它只需把该 Spec 标为 `LATER_WAVE`；
  此时 Current Wave 该维度变成 0 颗，会落入 `OUT_OF_DOMAIN` 并被拒绝，
  而不是悄悄算出一个怪数。

---

## 7. 输出结构

```jsonc
"scenario": {
  "scenario_id": "CURRENT_WAVE:cpu2-gpu2-panel1-ssd1-mem1",
  "scope": "CURRENT_WAVE",
  "wave_basis": "EXPLICIT_ASSIGNMENT",
  // ALL_SPECS = FULL_PROJECT 口径
  // EXPLICIT_ASSIGNMENT   = 有人（需求表或用户）声明过波次
  // NO_EXPLICIT_ASSIGNMENT= 没人声明过 —— 这就是 CURRENT_WAVE 等于 FULL_PROJECT 的原因
  // UNKNOWN_FANOUT        = 有 Spec 被明确标为 UNKNOWN，Current Wave 已扇出为多个场景
  "unknown_factors": [],
  "untagged_factors": ["cpu", "gpu"],       // 多 Spec 但没人说波次
  "truncated": false,
  "identical_to_full_project": false,
  "counts": { "cpu": 2, "gpu": 2, "panel": 1, "ssd": 1, "mem": 1 },
  "wave_report": [
    { "factor": "cpu",   "count": 2, "current": 2, "later": 0, "unknown": 0,
      "untagged": 2, "wave_state": "NOT_PROVIDED", "sources": ["NOT_PROVIDED"] },
    { "factor": "panel", "count": 1, "current": 1, "later": 0, "unknown": 0,
      "untagged": 1, "wave_state": "ALL_CURRENT",  "sources": ["IMPLICIT_SINGLE_SPEC"] },
    { "factor": "ssd",   "count": 2, "current": 1, "later": 1, "unknown": 0,
      "untagged": 0, "wave_state": "ASSIGNED",     "sources": ["USER_SELECTED"] }
  ],
  "match": { ... }, "candidates_priced": [3], "results": [ ... ]
}
```

`wave_state ∈ ALL_CURRENT | ASSIGNED | UNKNOWN | NOT_PROVIDED | NOT_APPLICABLE`。
UI 必须把 `NOT_PROVIDED` 和 `UNKNOWN` 用不同颜色显示——前者是"你没告诉我"，
后者是"这事本身没定"，对应两种不同的 Owner 动作。

---

## 8. 与原表条款的关系

原表 3 SKU 行写着 `... +Mem spec *1 (or SSD/Mem spec *2, arrange 2nd wave)`。

- 这句话**没有**给出"何时算安排了第二波"的判据，因此**不实现为规则**。
- 它被保留在 `sku_definition[SKU3].second_wave_clause` 里作为证据，UI 可显示为"原表备注"。
- 本契约用 Spec 级 `Wave` 声明取代它：如果第二颗 SSD/Mem 被明确标为 `LATER_WAVE`，
  Current Wave 的 `ssd=1, mem=1`，自然会匹配到 3 SKU —— 这正是那句话想表达的效果，
  但触发条件来自**声明**而不是来自 Agent 的猜测。
- 该条款是否也适用于 4/5/6 SKU 档，属 ORI-03，未由 Agent 自行推广。
