# 22 — Certification 修正契约与逐格验证结果（Phase 3）
> **状态（DEC-10 之后）**：本文描述的是 Phase 3a 的 Certification 口径
> （采用主表派生值）。Owner 已决定在 MVP 与团队试用阶段**采用附表总量**，
> 最新口径见 `docs/36_certification_adoption_v4.md`、`docs/37_owner_decision_log_v4.md`、
> `docs/39_totals_v4_and_6sku_review.md`、`docs/40_web_mvp_v4_changes.md`。
> 本文按原文保留，作为阶段记录。


任务：`TASK-GAMING-NRE-SAMPLE-REQUIREMENT-CERTIFICATION-CORRECTION-AND-WEB-MVP-01`
交付物 **A**（逐格验证报告）、**B**（ORI-02 状态）、**C**（修正后的 Certification Contract）。

机器可读结果：`artifacts/model/certification_verification.json` / `.md`
（由 `tools/verify_certification.py` 从 `baseline_v1.json` 生成，不写入任何人工数字）。

---

## 1. 修正后的业务语义（Owner 指令，本任务 §4）

| 项 | 修正后的定义 |
|---|---|
| 主表 | 表达**单个 SKU** 所需的样机数量 → `quantity_model = PER_SKU_RATE` |
| 附表 | 表达**对应 SKU 数量下的总量** → `evidence_role = DERIVED_TOTAL_VALIDATION` |
| 关系 | `appendix_total == main_table_per_sku_quantity × sku_count`（容差 `1e-9`） |
| 附表用途 | 验证主表乘法关系；提供该 SKU 档位的总量参考；建立回归不变量；检查总量是否重复计入 |
| FVT / SIT | 各自读自己的主表源行，**不使用全局 Phase 比例** |
| 项目总量 | `Project Certification Demand = Main Table Per-SKU Rate × Applied SKU Count`，**只计入一次** |

附表**不得**：作为第二套独立规则 / 与主表生成上下界 / 再次加入项目总量 / 覆盖主表单 SKU 费率 /
被解释为封顶模型。

**废止的旧解释**（`tools/verify_integrity.py` 与 `validate_rules_v3.py:LG-01/LG-04` 守护，
`output.schema.json` 以 `const` 结构性禁止）：

1. 主表与附表属于竞争模型；
2. Certification 存在两套互斥规则；
3. 附表 8–10 代表独立封顶模型；
4. Certification 区间来自主表与附表竞争；
5. `adopted_absolute` 必须因竞争而保持 null。

---

## 2. 逐格验证结果（交付物 A）

验证对象：**4 个 Certification Function × 2 Phase × 5 SKU 档 = 40 格**，逐格验证，不验证合计。

| Function | FVT 主表行 | SIT 主表行 | 附表行 | VERIFIED | MISMATCH | NOT_EVALUABLE |
|---|---:|---:|---:|---:|---:|---:|
| EMC | 27 | 28 | 53 / 54 | 10 | 0 | 0 |
| Green | 29 | 30 | 55 / 56 | 9 | 1 | 0 |
| Safety | 31 | 32 | 57 / 58 | 9 | 1 | 0 |
| RF Certification | 33 | 34 | 59 / 60 | 5 | 5 | 0 |
| **合计** | | | | **33** | **7** | **0** |

### 全部 7 个不一致格（原值原样保留，未修改源数据）

| Function | Phase | SKU | 主表 /SKU | derived = /SKU × SKU | 附表 | delta | 主表行 / 附表行 |
|---|---|---:|---:|---:|---:|---:|---|
| Green | SIT | 3 | 3.0 | 9.0 | 6.0 | **−3.0** | 30 / 56 |
| Safety | FVT | 6 | 1.6 | 9.6 | 10.0 | **+0.4** | 31 / 57 |
| RF Certification | SIT | 2 | 7.5 | 15.0 | 8.0 | **−7.0** | 34 / 60 |
| RF Certification | SIT | 3 | 5.0 | 15.0 | 9.0 | **−6.0** | 34 / 60 |
| RF Certification | SIT | 4 | 3.75 | 15.0 | 10.0 | **−5.0** | 34 / 60 |
| RF Certification | SIT | 5 | 3.0 | 15.0 | 10.0 | **−5.0** | 34 / 60 |
| RF Certification | SIT | 6 | 2.5 | 15.0 | 10.0 | **−5.0** | 34 / 60 |

### 两个结构性观察（作为证据登记，不据此改数）

1. **主表"每 SKU"列的形状**。真正的单 SKU 费率应随 SKU 档保持不变。实测形状：

   | Function/Phase | 形状 | 主表 /SKU（SKU2→6） | 主表 ×SKU |
   |---|---|---|---|
   | EMC FVT / SIT | `TRUE_PER_SKU_RATE` | 0,0,0,0,0 / 1,1,1,1,1 | 0 / 2,3,4,5,6 ✅ |
   | Green FVT | `TRUE_PER_SKU_RATE` | 0,… | 0 ✅ |
   | Green SIT | `IRREGULAR` | 3, **3**, 1.5, 1.2, 1 | 6, **9**, 6, 6, 6 |
   | Safety FVT | `IRREGULAR` | 5, 3, 2.5, 2, **1.6** | 10, 9, 10, 10, **9.6** |
   | Safety SIT | `BACK_DERIVED_FROM_FLAT_TOTAL` | 3, 2, 1.5, 1.2, 1 | 6,6,6,6,6 ✅ |
   | RF Certification SIT | `BACK_DERIVED_FROM_FLAT_TOTAL` | 7.5, 5, 3.75, 3, 2.5 | 15,15,15,15,15 |

   - `Green/SIT/SKU3 = 3.0` 与相邻档的 1/N 规律不符（按规律应为 2.0），单点异常；
   - `Safety/FVT/SKU6 = 1.6` 是 `9.6/6` 的回推值，而附表在该档写 10；
   - `Safety/SIT` 与 `RF/SIT` 的主表"每 SKU"列实际上是**同一总量按 1/N 回推**的产物，
     即"每 SKU 数量"随 SKU 增大而减小。这与 Owner 语义（主表 = 单个 SKU 所需数量）在字面上不完全一致，
     但不改变任何数字（`rate × SKU` 恒等于那个总量）。

2. **附表自身完全自洽**：附表 TTL 行 61/62 逐档等于其成分行之和
   （`FVT: 0+0+10+0=10,9,10,10,10`；`SIT: 2+6+6+8=22, 3+6+6+9=24, 4+6+6+10=26, 5+6+6+10=27, 6+6+6+10=28`）。
   因此附表数字是有意的业务数字，不是残留公式错误。这是 ORI-02 必须由 Owner 裁决、
   而不能由 Agent 判定"哪一边写错了"的关键理由。

**主表 ×SKU 恒等于 15（RF）而附表为 8–10，两者都是自洽数字。** 引擎按 Owner 指令采用主表值，
把差额完整登记为 `CERTIFICATION_SOURCE_VALIDATION_MISMATCH`，不改源数据、不取中位、不求平均。

---

## 3. ORI-02 状态（交付物 B）

> **`ORI-02 = PARTIALLY_RESOLVED`**

判定依据（任务 §5 第 6–8 条）：

- 不是 `RESOLVED`：40 格中有 7 格不满足 `附表 = 主表 ×SKU`；
- 不是 `OWNER_REVIEW_REQUIRED`：33 格已验证通过，且**规则本身已经明确**（单一模型、单一采用值、
  FVT/SIT 各读各行、附表不再竞争），Certification 已能输出单一值；
- 因此为 `PARTIALLY_RESOLVED`：模型层已解决，源数据层仍有 7 格待 Owner 裁决。

阻塞级别：`BLOCKS_FORMALIZATION`（规则包不能定版），**`blocks_manual_mvp = false`**
（手工输入 MVP 不受阻，已由 `validate_rules_v3.py:OR-02` 与 Web 探针 `UI-23` 守护）。

**关闭 ORI-02 只需 Owner 回答一个问题**：7 个不一致格中，主表值与附表值哪一个才是业务真值？
（详见 `docs/27_owner_confirmation_checklist_v3.md` 第 1 项。）

---

## 4. 输出逻辑契约（交付物 C）

### 4.1 SKU 为单一值

```
Certification Demand(FVT) = FVT 主表每 SKU 数量 × Applied SKU Count
Certification Demand(SIT) = SIT 主表每 SKU 数量 × Applied SKU Count
Certification Total       = FVT + SIT        ← 计入项目总量 1 次
```

输出单值的前置条件与结果：

| 条件 | 状态 |
|---|---|
| SKU 结果为单一值 | 由 SKU 推荐层决定 |
| Certification 源费率已验证 | **规则层已验证**（单一模型、公式固定、FVT/SIT 各读各行） |
| 无影响当前结果的未解决冲突 | 无**模型层**冲突；源数据层的 7 格不一致作为 `SOURCE_VALIDATION_MISMATCH` 登记 |

⚠ **本任务做出的一项解释性决定（已登记，需 Owner 确认）**：
"Certification 源费率已验证"被解释为**计算规则已验证**，而不是"每一格的附表校验都通过"。
若解释为后者，则 3 个含 MISMATCH 的 Function 会永久无法输出单值，与 §24 `CT-V2-03`
（单一 SKU 时 Certification 输出单值）直接冲突。当前实现的取舍是：
**输出单值 + 逐格披露验证状态 + 允许本次分析临时采用值**，并把该取舍登记为
`ORI-02a`（`docs/26_owner_review_register_v3.md`）。

### 4.2 SKU 为范围（例如 4–5 SKU）

- 分别计算 4 SKU 与 5 SKU 的 Certification Demand（各自单值，两档并列）；
- 范围原因固定为 **`SKU_NOT_ESTABLISHED`**；
- **禁止**使用 `COMPETING_CERTIFICATION_MODELS` / `CERTIFICATION_MODEL_UNRESOLVED`
  （`rules_v3.PROHIBITED_RANGE_REASONS`，探针 `CT-V2-09` 守护）；
- 页面必须说明："Certification 计算规则已经明确，当前结果范围来自 SKU 档位尚未在
  4 SKU 与 5 SKU 之间建立正式分界"（`web/assets/app.js` 已按此文案实现，Web 探针 `UI-10` 守护）；
- 不得用 lower / upper / midpoint / 默认候选生成隐藏单值（`output.schema.json` 的
  `single_value=false → 单值字段必须为 null` 结构性保证，探针 `SC-09`）。

### 4.3 用户临时采用值

- 入口：高级选项 → Certification（仅对 `verification_status = MISMATCH` 的格开放）；
- 作用域：仅本次 Analysis，写入 `certification_input.overrides`；
- 记录：`system_computed_total`（系统值）、`user_input_total`（用户值）、
  `value_source = USER_MANUAL_OVERRIDE` 三者同时保留（`CT-PR-05b`、parity `W-11`/`W-23`）；
- **不写回规则库、不升级为正式规则**（规则包由 Python 侧产物生成，Web 无任何写回通道）。

---

## 5. J33 调查结论

| 调查项 | 结论 |
|---|---|
| J33 明细合计能否解释主表单 SKU 数量？ | **不能。** J33 只按其自述的参考场景成立：2 天线源 + 2 WLAN 卡。按 J33 自身两种读法给出区间 **11 … 27**（下限：FCC 走 C1PC/模组路线不需整机 → 2+4+2+1+2=11；上限：FCC = intel_wlan×天线×4 = 16 → 27）。主表 derived 值 15 **落在该区间内**；附表 8–10 **低于下限**。 |
| 是否只适用于特定 Certification Function？ | 是。J33（合并区 `J33:J34`）只挂在 **RF Certification** 的 FVT/SIT 行上。 |
| 是否只适用于特定项目 / Source 组合？ | 是。原文首句即声明 `this data for 2 antenna source +2 wlan source refrence`。 |
| Antenna / WLAN 是业务构成说明还是正式计算变量？ | **业务构成说明。** 工作簿内没有任何公式消费天线数或 WLAN 卡数；`antenna_source_count` / `wlan_card_count` 不存在于任何公式或命名区域。 |
| J33 是否已被主表单 SKU 费率包含？ | **无法从工作簿证明**（`CANNOT_BE_PROVEN_FROM_THE_WORKBOOK`）。这是唯一真正需要 Owner 回答的 J33 问题。 |
| 若叠加是否有重复计入风险？ | **HIGH。** 主表 RF 值本身已是整机数量；把 J33 条目再加一遍会重复计同一批样机。 |

**处置**：`evidence_role = BREAKDOWN_EVIDENCE`，`disposition = DECLARED_NOT_GENERALIZED`，
`additive_to_main_table_result = false`，`mvp_requires_antenna_wlan_input_now = false`。
规则包等级别：`EXPLANATORY_EVIDENCE_NOT_A_RULE`。
因此本任务**没有**为 MVP 增加天线 / WLAN 输入项，也**没有**把 J33 叠加到任何结果上
（探针 `JG-01`…`JG-05`、`CT-V2-08`、Web `UI-12`）。

一个附带结论值得 Owner 注意：附表 RF SIT 的 8–10 **低于** J33 参考场景的下限 11，
说明附表对应的不是"2 天线 + 2 WLAN 卡"这一场景。也就是说，主表 15 与附表 8–10
很可能描述的是**不同 Source 组合**，而不是同一事实的两个互相矛盾的写法。
这会把 ORI-02 的答案从"哪个数字对"变成"两者各自适用哪种 Source 组合"。
