# 14 — D. Quantity Model v2

> 决策依据：**DEC-05**。机器推导产物：`artifacts/model/quantity_model_v2.json` / `.md`、
> `artifacts/model/model_delta.json` / `.md`。生成器：`tools/derive_quantity_model.py`、
> `tools/export_model_delta.py`。**本文不手填任何业务数值。**

---

## 1. 为什么必须改

Phase 1 把所有主表数值当作"每 SKU 费率"，用 `rate × SKU` 还原总量。这个模型有两个问题：

1. **它把派生量当原始量。** 主表 MEPA 那行是 `16 / 12 / 9 / 7.2 / 6`，
   乘回 SKU 得 `32 / 36 / 36 / 36 / 36`；而副表行 70/71 直接写 `36/36/36/36/36`，
   备注还写着 `CS: 1 phase 36 units`。原始事实是"每个相位 36 台"，那个 16 是 `36÷2` 的产物，
   并且在 2 SKU 档还凑不回 36。
2. **`0.7 × 6 = 4.2` 台物理上不成立。** HW PA 副表写 `2/3/4/4/4`，饱和在 4；
   主表那个 0.7 同样是回推出来的。

继续用统一费率模型，就会在 2 SKU 少算 8 台、在 6 SKU 多算 0.4 台，
而且掩盖"这块表其实是绝对配额"这个业务事实。

---

## 2. 模型定义

| Quantity Model | 语义 | 引擎如何取值 | 是否随 SKU 变 |
|---|---|---|---|
| `PER_SKU_RATE` | 主表值随 SKU 档位变化，代表该档位的实际需求；档位间是**查表**关系而非同一常量费率 | 读 `adopted_absolute[SKU_n]` | 变 |
| `PER_PHASE_FIXED` | 该 Function 每相位投放固定绝对量，与 SKU 数无关 | 读 `adopted_absolute[SKU_n]`（各档同值） | 不变 |
| `PER_PROJECT_FIXED` | 整个项目固定绝对量，相位间再分配 | 读项目级常量 + 相位分配 | 不变 |
| `FORMULA_DRIVEN` | 由源数量公式驱动（如天线数 × WLAN 卡数 × 4） | 需要公式输入；缺输入即 `INPUTS_UNAVAILABLE_IN_MVP` | 由公式决定 |
| `UNRESOLVED` | 存在多套竞争证据，Owner 未选定 | `base_demand = null`，另给 `candidate_values` | 输出为区间 |

### 2.1 硬约束

- **禁止伪费率**：引擎内不得出现"先除以 SKU、再乘回 SKU"的还原动作。
  探针 `QM-02` 直接对 `rules_v2.py` 源码断言不含 `per_sku_rate` / `ttl_per_phase`。
  所有 cell 一律 `value_access = ABSOLUTE_TABLE_READ`。
- **平坦不等于固定**。合计跨 SKU 平坦只是**线索**，不足以升级为 `PER_PHASE_FIXED`；
  必须有独立绝对量表或明确备注。否则登记为 `model_questions` 交 Owner。
- `PER_PROJECT_FIXED` 目前**无成员**，但契约、Schema、探针 `QM-08` 都已支持，
  以便 Owner 指定后直接落地。

---

## 3. 当前分布（42 个 cell = 21 Function × 2 Phase）

| Quantity Model | cell 数 | 涉及 Function |
|---|---:|---|
| `PER_SKU_RATE` | 30 | RD 全部 9 项、SWPA、EMC Test、Vendor 4 项、MFG、PD、ME、THM… |
| `PER_PHASE_FIXED` | 4 | MEPA FVT/SIT、HW PA FVT/SIT |
| `UNRESOLVED` | 8 | EMC、Green、Safety、RF Certification（各 FVT/SIT） |

- `owner_review_cells = 12`
- `contested_cells = 4`（主表与副表实质冲突）
- `model_questions = 6`（形状平坦但无独立证据）
- 副表与主表完全一致的 7 个 cell（SWPA 两相位、EMC 两相位、Green FVT、Safety SIT 等）
  记为 `MAIN_AND_SECONDARY_AGREE`，属于互相印证，不改变模型。

### 3.1 `PER_PHASE_FIXED` 的证据

| Function | Phase | 采用值（SKU2→6） | 证据 |
|---|---|---|---|
| MEPA | FVT / SIT | `36 / 36 / 36 / 36 / 36` | 副表行 70/71 跨 SKU 恒定；备注 `CS: 1 phase 36 units` |
| HW PA | FVT / SIT | `2 / 3 / 4 / 4 / 4` | 副表行 72/73 为整数且与"费率×SKU"不符；备注 `TTL3-4unit one phase` |

竞争证据保留：MEPA 主表 2 SKU = 32（差 +4）；HW PA 主表 6 SKU = 4.2（差 −0.2）。
两者都完整保留在 `main_table_absolute` 里，供 Owner 复核。

### 3.2 HW PA 的诚实说明

`2 / 3 / 4 / 4 / 4` 不是严格恒定，而是**随档位上升后饱和**。把它标为 `PER_PHASE_FIXED`
是把它从"伪费率"纠正为"绝对投放量"，**不等于**声称它与 SKU 完全无关。
真正的饱和规则（在几 SKU 之后封顶）仍属 ORI-10，需 Owner 给出。
引擎的做法是按档位读绝对量、不外推、不拟合曲线。

---

## 4. Certification 全部保持 `UNRESOLVED`（DEC-03）

| Function | Phase | 主表（SKU2→6） | 副表（SKU2→6） | 一致？ |
|---|---|---|---|---|
| EMC | FVT | `0/0/0/0/0` | `0/0/0/0/0` | ✅ |
| EMC | SIT | `2/3/4/5/6` | `2/3/4/5/6` | ✅ |
| Green | FVT | `0/0/0/0/0` | `0/0/0/0/0` | ✅ |
| Green | SIT | `6/9/6/6/6` | `6/6/6/6/6` | ❌ 3 SKU 差 −3 |
| Safety | FVT | `10/9/10/10/9.6` | `10/9/10/10/10` | ❌ 6 SKU 差 +0.4 |
| Safety | SIT | `6/6/6/6/6` | `6/6/6/6/6` | ✅ |
| RF Cert | FVT | `0/0/0/0/0` | `0/0/0/0/0` | ✅ |
| RF Cert | SIT | `15/15/15/15/15` | `8/9/10/10/10` | ❌ 差 −7/−6/−5/−5/−5 |

要点：

- 即便某 cell 两套模型一致，也**保持 `UNRESOLVED`**，只额外标 `models_agree = true`。
  一致是信息，不是把模型升为 CONFIRMED 的理由（探针 `CT-07`）。
- `J33_FORMULA`（`SRRC*2; CE*4 = antenna*wlan; FCC = intel WLAN × antenna × 4; ID*2;
  Mexico*1; 资安*2`）作为 `FORMULA_DRIVEN` 候选保留。它需要 `antenna_source_count`、
  `wlan_card_count`、`intel_wlan_count`，不在 MVP 五维输入里，因此状态
  `INPUTS_UNAVAILABLE_IN_MVP`，落在 `totals_by_model.variants_not_evaluable`。
  **不丢弃、不用别的模型顶替。**
- 手工覆盖入口：`certification_input.overrides`，写入后该行 `value_source =
  USER_MANUAL_OVERRIDE` 且不再 `owner_review_required`，其余 cell 不受影响。

---

## 5. 这个决策到底改变了多少个数

`artifacts/model/model_delta.md`：

| SKU | workbook 复现 | 引擎（Cert=主表） | 引擎（Cert=副表） | 无争议 cell 小计 | 引擎−workbook | 发布区间 |
|---:|---:|---:|---:|---:|---:|---|
| 2 | 365 | 373.0 | 366.0 | 334.0 | **+8** | `366–373` |
| 3 | 417 | 417.0 | 408.0 | 375.0 | 0 | `408–417` |
| 4 | 443.8 | 443.8 | 438.8 | 402.8 | 0 | `438.8–443.8` |
| 5 | 474 | 474.0 | 469.0 | 432.0 | 0 | `469–474` |
| 6 | 507 | 506.6 | 502.0 | 464.0 | **−0.4** | `502–506.6` |

被 DEC-05 改动的 cell **只有 4 个**：MEPA FVT/SIT @2 SKU 各 +4；HW PA FVT/SIT @6 SKU 各 −0.2。
3/4/5 SKU 档与 workbook 完全一致——因为那三档上 MEPA 的伪费率恰好能乘回 36、
HW PA 恰好是整数。这说明改的是**模型性质**，不是批量改数。

`workbook 复现` 那一列由探针 `RT-01` 持续断言（365 / 417 / 443.8 / 474 / 507），
是提取链路的回归锚点，不是 MVP 对外发布的答案。

---

## 6. 输出契约（每行数量必带）

```jsonc
{
  "function_id": "F_MEPA",
  "phase": "FVT",
  "sku_qty": 2,
  "quantity_model": "PER_PHASE_FIXED",
  "base_demand": 36.0,                       // UNRESOLVED 时为 null
  "candidate_values": {},                    // UNRESOLVED 时放各来源数值
  "models_not_evaluable": [],                // 例如 ["J33_FORMULA"]
  "value_source": "SECONDARY_ABSOLUTE_TABLE",// MAIN_TABLE | SECONDARY_ABSOLUTE_TABLE
                                             // | USER_MANUAL_OVERRIDE | NONE_UNRESOLVED
  "unit": "UNIT",
  "owner_review_required": true,
  "rule_id": "QM2:F_MEPA:FVT",
  "evidence": { "source_file": "...", "sheet": "CS ODM sample ", "row": 23,
                "secondary_row": 70, "remark_text": "CS: 1 phase 36 units ..." }
}
```

Schema 约束（`schema/output.schema.json`）：

- `quantity_model` 是五值枚举，写别的值直接校验失败。
- `single_value = false` 时 `if/then` 规则强制 `recommended_total / base_demand / fvt_total /
  sit_total / risk_reserve` 必须为 `null` —— 前端**无法**把区间偷偷显示成单值（探针 `SC-05`）。
- `rounding` 是 `const: "NONE (D-01)"`。

---

## 7. 与 DEC-06 的连接

`quantity_model_v2.baseline_embedded_sharing` 记录每个 Function 合计随 SKU 的增长情况。
极差 ≤ 1 **或**增长 ≤ 0 → `SUSPECTED`，reuse 策略置 `BLOCK_UNLESS_PROVEN`。
当前 15 个 Function 命中：Audio、BIOS、EMC、EMC Test、Green、INTEL、ITE、ME、MFG、NV、PD、
RF Certification、RF Test、Safety、THM。

这不改变数量，只改变"用户声称的复用能不能扣减"的默认立场。详见 `docs/17_reuse_protection_contract.md`。
