# 17 — G. Reuse Protection Contract

> 决策依据：**DEC-06**、**DEC-05**。实现：`prototype/rules_v2.py::reuse_ledger`、
> `tools/derive_quantity_model.py::baseline_embedded_sharing`。
> 守护探针：`RS-01`…`RS-08`、`D01-04`、`D01-05`。

---

## 1. 问题：基线里很可能已经扣过了

Phase 1 的量化事实：

- 主表**费率**随 SKU 增加而单调下降（几乎每个 Function 都是）。
- 更关键的是，有 **15 个 Function 的合计数量完全不随 SKU 增长**，有的还下降：
  Audio、BIOS、EMC、EMC Test、Green、INTEL、ITE、ME、MFG、NV、PD、RF Certification、
  RF Test、Safety、THM。

如果这些数字里没有预先假设共享，`3 SKU → 6 SKU` 时合计不可能保持不动。
也就是说：**这张表在编制时已经假定了一部分"多台共用/规模效应"**。

后果很直接：使用者再说"我这 5 台可以复用"，很可能是在**同一份共享上扣第二次**。
在样机需求这种"少算就是漏测"的场景里，重复扣减是危险方向的错误。

因此本契约的默认立场是**不扣减**，除非能证明没有重复。

---

## 2. 四种 Reuse 状态

| `reuse_status` | 语义 | 可否扣减 | 引擎动作 |
|---|---|---|---|
| `ALREADY_EMBEDDED_IN_BASELINE` | Owner 明确说明这份共享已经体现在基线费率里 | **否** | `NOT_DEDUCTED_ALREADY_EMBEDDED` |
| `ADDITIONAL_CONFIRMED_REUSE` | 在基线之外新确认的复用 | **仅当已证明未被基线包含** | `DEDUCTED` 或 `BLOCKED_PROOF_MISSING` |
| `POTENTIAL_REUSE` | 可能复用，未确认 | **否** | `DISPLAY_ONLY`（展示，不进入算式） |
| `UNKNOWN_OVERLAP` | 是否与基线重叠无法判断 | **否** | `BLOCKED_UNTIL_PROVEN` + ORI |

**扣减三条件（必须同时成立）**

```text
reuse_status == ADDITIONAL_CONFIRMED_REUSE
   AND proven_not_in_baseline == true
   AND unit == UNIT
```

任一不成立 → 扣减额 0，并在账本里写明原因；后两种情形还生成 Owner Review Item。

---

## 3. 账本：每个决定都要可审计

```jsonc
"reuse_ledger": {
  "deduction": -4.0,
  "policy": "only a proven ADDITIONAL_CONFIRMED_REUSE reduces demand (DEC-06)",
  "items": [
    { "qty": 5.0, "unit": "UNIT", "reuse_status": "ALREADY_EMBEDDED_IN_BASELINE",
      "applied": 0.0, "decision": "NOT_DEDUCTED_ALREADY_EMBEDDED",
      "why": "the Owner states this sharing is already inside the baseline rate - deducting again would double count" },
    { "qty": 3.0, "unit": "UNIT", "reuse_status": "POTENTIAL_REUSE",
      "applied": 0.0, "decision": "DISPLAY_ONLY",
      "why": "potential reuse is shown, never subtracted" },
    { "qty": 2.0, "unit": "UNIT", "reuse_status": "UNKNOWN_OVERLAP",
      "applied": 0.0, "decision": "BLOCKED_UNTIL_PROVEN",
      "why": "overlap with the baseline cannot be excluded" },
    { "qty": 4.0, "unit": "UNIT", "reuse_status": "ADDITIONAL_CONFIRMED_REUSE",
      "applied": -4.0, "decision": "DEDUCTED",
      "why": "confirmed SIT spare pool, not in the baseline rate" }
  ],
  "owner_review_items": [ { "kind": "REUSE_OVERLAP_UNPROVEN", "qty": 2.0 },
                          { "kind": "REUSE_PROOF_MISSING", "qty": 5.0 } ]
}
```

`EX-H` 就是这个例子：**声称 14.0，实际扣减 4.0**。UI 必须把这两个数并列显示，
让使用者立刻看见"哪一条被挡了、为什么"。

---

## 4. 嵌入式共享信号

`quantity_model_v2.baseline_embedded_sharing` 对每个 Function 计算：

```text
spread = max(TTL over SKU2..SKU6) - min(...)
growth = TTL(SKU6) - TTL(SKU2)
signal = SUSPECTED  if spread <= 1.0  or  growth <= 0      # 容差 1e-9
         NONE       otherwise
reuse_policy = BLOCK_UNLESS_PROVEN   if SUSPECTED
               PERMIT_WHEN_CONFIRMED otherwise
```

当前 **15 个 Function** 命中 `SUSPECTED`。

该信号有两个用途：

1. 当使用者对这些 Function 提交 `ADDITIONAL_CONFIRMED_REUSE` 却未提供证明时，
   ORI 文案会额外写明"`{function}` 的基线合计跨 SKU 基本不动，本身已疑似包含共享"。
2. 结果页在 Function 明细上打 `⚠ 基线疑似已含共享` 标记，
   提示这里的任何复用主张都需要更强证据。

信号**不改变任何数量**，只改变举证责任。

---

## 5. 单位隔离

`unit = PCBA` 的复用主张**永远**不能扣减 unit 需求：

```json
{ "decision": "EXCLUDED_UNIT_MISMATCH",
  "why": "PCBA quantity must never be summed with or deducted from unit demand" }
```

`RS-08` 探针验证：一条 `proven_not_in_baseline = true` 的 PCBA 复用，扣减后总数**不变**。
同理，`additional_demand` 里的 PCBA 行只出现在 `pcba_lines_not_summed`，
不进入 unit 总量（`D01-04`）；而相同数量的 `UNIT` 行**会**进入总量（`D01-05` 控制组）。

---

## 6. 与其他条款的相互位置

```text
Base Demand(f, phase, SKU)          ← Quantity Model 直读绝对量（DEC-05）
  + Conditional Increment           ← 用户输入 UNIT 额外需求（Option 不预置）
  + Confirmed Reuse Adjustment      ← 本契约，≤ 0，且仅 proven 项
  + Risk Reserve                    ← 只对 (Base + Reuse) 计费，不对额外需求计费（ORI-07）
  = Recommended Total
```

`Potential Reuse` 只出现在 `potential_reuse_display_only` 字段，**不出现在算式里**。

`D01-07` 探针专门验证：加 12 台 UNIT 额外需求后，风险预留仍是 `443.8 × 0.05`，
不会因为额外需求而放大——预留是应对不确定性的，不该奖励"多报需求"。

---

## 7. 举证责任怎么落地（MVP 做法）

MVP 不引入审批流，只做三件事：

1. 用户选 `ADDITIONAL_CONFIRMED_REUSE` 时，**必须**勾一个复选框
   「我已确认这份复用未被基线费率包含」并填一句依据（`basis`，非空校验）。
   未勾选 → `proven_not_in_baseline = false` → 不扣减。
2. 若该 Function 处于 `BLOCK_UNLESS_PROVEN`，表单顶部直接显示基线的 spread / growth 数据，
   让用户在知情前提下勾选。
3. 导出与结果页把账本原样带出，`decision` 与 `why` 不可折叠隐藏。

Owner 之后若给出"哪些 Function 的基线确实已含共享"的正式清单，
就把 `baseline_embedded_sharing` 从"推断信号"升级为 `CONFIRMED` 规则，
并把对应 Function 的默认 Reuse 状态改成 `ALREADY_EMBEDDED_IN_BASELINE`。
这一步需要 Owner 输入，属 ORI-06 / ORI-12 范围，不由 Agent 自行认定。
