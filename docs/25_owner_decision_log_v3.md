# 25 — Owner Decision Log v3（交付物 G）
> **状态（DEC-10 之后）**：本文描述的是 Phase 3a 的 Certification 口径
> （采用主表派生值）。Owner 已决定在 MVP 与团队试用阶段**采用附表总量**，
> 最新口径见 `docs/36_certification_adoption_v4.md`、`docs/37_owner_decision_log_v4.md`、
> `docs/39_totals_v4_and_6sku_review.md`、`docs/40_web_mvp_v4_changes.md`。
> 本文按原文保留，作为阶段记录。


`docs/12_owner_decision_log.md` 保留 Phase 2 的 DEC-01…DEC-08 全文，不删改。
本文件登记 Phase 3 新增的 **DEC-09**，并记录 DEC-03 被**取代**这一事实。

| 决策 | 主题 | 状态 | 守护 |
|---|---|---|---|
| DEC-01 | 4 vs 5 SKU → RANGE，不强制单值 | 继续有效 | `SR-01..SR-10` |
| DEC-02 | Panel = Panel Spec Count，`D2:H2` 批注排除 | 继续有效 | `PL-01..PL-05` |
| ~~DEC-03~~ | ~~Certification 三套竞争模型~~ | **被 DEC-09 取代** | 旧探针已退役（见 §3） |
| DEC-04 | 显式 Wave Assignment，不推断 | 继续有效，新增界面映射 | `WV-01..WV-13` |
| DEC-05 | Quantity Model 五态，禁止伪费率 | 继续有效 | `QM-01..QM-09` |
| DEC-06 | Reuse 四态与重复扣减保护 | 继续有效，输出契约补齐 | `RS-01..RS-10` |
| DEC-07 | D-01 小数口径 | 继续有效 | `D01-01..D01-09` |
| DEC-08 | 手工输入 MVP 范围，ORI-09/11 解耦 | 继续有效，本任务落地为 Web MVP | `OR-01..OR-05`、Web 探针 |
| **DEC-09** | **Certification 单一模型 + 附表验证角色 + J33 说明角色** | **本任务新增** | `CT-V2-01..CT-V2-12`、`JG-01..JG-05` |

---

## DEC-09（ORI-02 修正）— 本任务核心

### Owner 指令（任务 §4 原文要点）

1. 主表表达**单个 SKU** 所需的样机数量；
2. 附表表达**对应 SKU 数量下的样机总量**；
3. 两者**不是**两套互斥模型；
4. 必须满足 `appendix_total = main_table_per_sku_quantity × sku_count`；
5. 附表是主表计算结果的**验证依据**，不是第二套独立规则；
6. 附表**不得再次加入项目总量**；
7. Certification 范围不再由"主表与附表竞争"产生；
8. 只有当 SKU 本身为范围时，Certification 才随 SKU 档位形成范围；
9. FVT 与 SIT 分别使用各自的主表单 SKU 数量计算；
10. 不使用全局 FVT/SIT 比例。

### 已实现的约束

| # | 约束 | 落点 | 守护探针 |
|---|---|---|---|
| 1 | Certification `quantity_model = PER_SKU_RATE`，8 格全部转换 | `build_quantity_model_v3.py` | `QM-08`、`LG-02` |
| 2 | `adopted_absolute = 主表每 SKU 数量 × SKU` | 同上 | `CT-V2-01`、`RT-02` |
| 3 | 附表 `evidence_role = DERIVED_TOTAL_VALIDATION`，且**不是** Quantity Model | `quantity_model_v3.policy` / `rule.schema.json` | `QM-09`、`LG-03` |
| 4 | 附表计入总量 0 次 | `output.schema.json` `const 0` | `CT-V2-02`、`SC-05` |
| 5 | 附表不得形成区间、不得覆盖主表、不是封顶模型 | `policy` + Schema | `LG-04`、`SC-10` |
| 6 | J33 = `BREAKDOWN_EVIDENCE`，`additive = false` | `certification_verification.j33_investigation` | `JG-01..05`、`CT-V2-08`、`SC-05` 组 |
| 7 | 单一 SKU → Certification 单值 | `rules_v3.certification_result()` | `CT-V2-03` |
| 8 | 4–5 SKU → 两档各自单值，范围原因 `SKU_NOT_ESTABLISHED` | `rules_v3.analyse()` | `CT-V2-04`、`CT-V2-05`、`UI-10` |
| 9 | FVT / SIT 各读自己源行，禁止全局比例 | Schema `phase_ratio_used: null` | `CT-V2-06`、`CT-V2-07` |
| 10 | 逐格不一致 → `SOURCE_VALIDATION_MISMATCH`，保留原值 | `rules_v3.analyse()` | `CT-V2-11` |
| 11 | 显示精度不回写 | `policy.display_precision_modifies_values = false` | `CT-V2-12`、`D01-08`、`UI-17` |
| 12 | 用户临时采用值只作用本次分析，三重来源并存 | `input.schema.json` / `certification.cells[]` | `SC-08`、`PR-05b`、parity `W-11/W-23` |

### 仍开放（不能由 Agent 关闭）

- **ORI-02 源数据层**：7 格 `主表 ×SKU ≠ 附表`。`PARTIALLY_RESOLVED`。
- **ORI-02a（本任务新登记）**：本任务把"Certification 源费率已验证"解释为**规则层**已验证。
  若 Owner 认为应当指"每格附表校验都通过"，则 3 个含 MISMATCH 的 Function 必须退回非单值输出，
  这与 §24 `CT-V2-03` 冲突，需要 Owner 明确取舍。
- **ORI-02b（本任务新登记）**：J33 无法证明已被主表费率包含；且附表 RF SIT 的 8–10 低于
  J33 参考场景下限 11，提示主表与附表可能描述**不同 Source 组合**。

---

## DEC-03 的退役说明（§3）

Phase 2 的 `CT-01`…`CT-08` 探针断言的是"三套模型并存、输出区间、`adopted_absolute` 为 null"。
本任务明令**禁止保留该计算行为**，因此这 8 个探针被**退役并替换**，映射如下：

| Phase 2 探针 | 原断言 | 处置 | 由谁接替 |
|---|---|---|---|
| `CT-01` | 8 格全部 UNRESOLVED 且需复核 | 退役（与 DEC-09 冲突） | `QM-08` + `CT-V2-11` |
| `CT-02` | 按模型各算一遍 | 退役 | `CT-V2-02`（附表只验证） |
| `CT-03` | 竞争模型形成区间，从不平均 | 退役 | `CT-V2-03`（单值） |
| `CT-04` | J33 保留但不可求值 | 语义变更 | `JG-01..05` |
| `CT-05` | 手工覆盖可用 | **保留并加强** | `CT-V2-11` + `SC-08` + `PR-05b` |
| `CT-06` | FVT/SIT 拆分不是全局比例 | **保留** | `CT-V2-06` |
| `CT-07` | 两模型一致的格仍标 UNRESOLVED | 退役 | `CT-V2-01`（VERIFIED 即 VERIFIED） |
| `CT-08` | 竞争自动产生 ORI | 语义变更 | `CT-V2-11`（改为源数据校验 ORI） |

退役不是删除证据：`artifacts/validation/regression_report_v2.md` 保留 Phase 2 全绿记录，
`quantity_model_v2.json` 保留 Phase 2 模型，`phase2_superseded{}` 在**每一格**里记录了旧解释与
废止理由。`verify_integrity.py §6` 反向检查 `CT-01/02/03/08` 确实已不在当前套件中——
它们既没有被偷偷留着"碰巧变绿"，也没有被无声消失。

## DEC-04 的界面侧补充

Wave 三个界面选项「当前波次 / 后续波次 / 未特别指定」映射到
`CURRENT_WAVE / LATER_WAVE / NO_EXPLICIT_ASSIGNMENT`。
`NO_EXPLICIT_ASSIGNMENT` 在契约边界即归一为 `CURRENT_WAVE + NOT_PROVIDED`，
**不会**触发 UNKNOWN 情景展开——因为"用户没说"不等于"用户说不知道"。
守护：`WV-12`、parity `W-22`、Web `UI-12c`。
