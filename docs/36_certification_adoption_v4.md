# 36 — Certification 采用值修正（DEC-10）与逐格复核（交付物 A / B / C）

- 依据：Owner 决定 `DEC-10`（本轮任务）
- 源文件：`original_documents\Sample_Requirement_SKU_and_Demand_Baseline_CleanSheet_20261030_V01_FORMAL.xlsx`
  SHA-256 `48A360FF2FFD086E41D6B90A916F64FE52D9BC13EFBA07B8377B2945C846AB5A`（任务开始与结束时复验一致，未修改）
- 证据产物：`artifacts/model/certification_verification.json`（40 格）、
  `artifacts/model/quantity_model_v4.json`（`QMODEL-V4`）
- 上一版模型 `artifacts/model/quantity_model_v3.json`（`QMODEL-V3`）原样保留，作为 Phase 3a 记录

---

## A. 当前采用的 Certification 模型

| 项目 | 内容 |
|---|---|
| 采用值（adopted） | **附表中该 Function、该 Phase、该 SKU 档位对应的总量** |
| 采用值来源 | `adopted_source = APPENDIX_TABLE_TOTAL`，`value_access = APPENDIX_TABLE_READ` |
| 采用值证据角色 | `ADOPTED_ABSOLUTE_TOTAL`，计入项目总量 **1 次** |
| 主表值保留 | 主表「单 SKU 数量」列原样保留，`quantity_model` 仍为 `PER_SKU_RATE`（作为规则记录） |
| 主表派生总量 | `主表单 SKU 数量 × SKU 数`，证据角色 `DERIVED_MAIN_TABLE_AUDIT`，计入总量 **0 次** |
| 二者关系 | **永不叠加**：`main_table_and_appendix_added_together = false` |
| J33 | `BREAKDOWN_EVIDENCE`，计入 **0 次**，`j33_added_to_result = false` |
| FVT / SIT | 各自读取附表自己的行（FVT：53/55/57/59；SIT：54/56/58/60），**无全局比例** |
| 取值方式 | 逐格绝对值读取；**不做「除以 SKU 数再乘回」的伪费率还原** |
| 范围（range） | 仍然只可能来自 SKU 档位（`SKU_NOT_ESTABLISHED`）；**不产生主表/附表区间** |

Schema 层已把上面几条钉死（`schema/output.schema.json`，`$defs.certification`）：
`counted_in_project_total_times = const 1`、
`main_derived_counted_in_project_total_times = const 0`、
`main_table_and_appendix_added_together = const false`、
`j33_counted_in_project_total_times = const 0`、`phase_ratio_used = null`。

---

## B. 40 格逐格复核（结论：数据事实不变）

`tools/verify_certification.py` 重新生成 40 格网格（4 Function × 2 Phase × 5 SKU），
每格字段包含 `function / phase / sku_count / main_table_per_sku_quantity / derived_total /
appendix_total / delta / verification_status / source_reference`。

| cells | VERIFIED | MISMATCH | NOT_EVALUABLE |
|---:|---:|---:|---:|
| 40 | 33 | 7 | 0 |

**DEC-10 改变的是"用哪一列"，不改变"两列是否相等"。** 因此验证结果与 Phase 3a 完全一致，
`ori_02_status` 仍为 `PARTIALLY_RESOLVED`。

### 7 处不一致（现在：采用值 = 附表，审计值 = 主表派生）

| Function | Phase | SKU | 采用值（附表） | 主表 /SKU | 主表 × SKU（审计） | 差值 | 主表行 / 附表行 |
|---|---|---:|---:|---:|---:|---:|---|
| RF Certification | SIT | 2 | 8.0 | 7.5 | 15.0 | −7.0 | 34 / 60 |
| RF Certification | SIT | 3 | 9.0 | 5.0 | 15.0 | −6.0 | 34 / 60 |
| Green | SIT | 3 | 6.0 | 3.0 | 9.0 | −3.0 | 30 / 56 |
| RF Certification | SIT | 4 | 10.0 | 3.75 | 15.0 | −5.0 | 34 / 60 |
| RF Certification | SIT | 5 | 10.0 | 3.0 | 15.0 | −5.0 | 34 / 60 |
| RF Certification | SIT | 6 | 10.0 | 2.5 | 15.0 | −5.0 | 34 / 60 |
| Safety | FVT | 6 | 10.0 | 1.6 | 9.6 | **+0.4** | 31 / 57 |

- `Safety/FVT/SKU6` 是唯一"附表更大"的一格：采用值 10.0 为整数，主表派生 9.6 作为审计值
  原样保留（`repr(9.6) == "9.6"`，未取整、未回写）。
- 附表盘自身仍然自洽（成分行之和 = TTL 行，10/10 一致），因此不能判定附表填错；
  反过来主表列也不能被证明填错 → 该差异继续留在 Register（ORI-02 / ORI-15 / ORI-16）。

---

## C. J33 复核（保持不变）

- 位置：`J33`（合并 `J33:J34`），附着于 RF Certification。
- 自述范围：`2 天线源 + 2 WLAN 卡` 的特定组合；结论 `DECLARED_NOT_GENERALIZED`。
- 由 J33 自身文字得到的区间：`11 … 27`（下限＝WLAN 全走 C1PC/模组路线；上限＝每项都要整机）。
- 附表采用值 8–10 **低于该区间下限**，主表派生 15 在区间内 → 进一步说明两列描述的 Source
  组合可能不同（已登记在 ORI-02b，仍需 Owner 确认）。
- 计入项目总量：**0 次**；不要求 MVP 现在采集天线/WLAN 输入。

---

## 本轮不再成立、已退役的旧口径

| 旧口径（Phase 3a / DEC-09） | 现在（DEC-10） |
|---|---|
| 采用主表「单 SKU 数量 × SKU 数」 | 采用附表总量 |
| 附表仅用于验证，计入 0 次 | 附表为采用值，计入 1 次 |
| 主表派生总量即项目贡献 | 主表派生总量仅作审计，计入 0 次 |
| 探针 `CT-V2-02`、`SC-05` | 由 `DA-01 / DA-02 / DA-03 / DA-05` 接替 |

仍然成立（DEC-09 未被推翻的部分）：Certification 只有一套规则、FVT 与 SIT 各自读自己的行、
不产生主表/附表区间、区间只能来自 SKU 档位、J33 不叠加。
