# 44 — Owner 一次性确认清单（试用结束后的唯一一轮确认）

> 规矩：**试用过程中不逐条问 Owner**。试用者把疑问写进反馈表，回收汇总后统一并进本清单，
> Owner 一次答完，避免"每天被问一条、每条都被口头答复"。
> 规则包当前 `RP-V4.0 / DRAFT_PENDING_OWNER`，本清单答完之前**不改状态**。
> 空白不等于同意：没答的条目继续留在 `trial_feedback_report` 的缺口清单里。

## 0. 一分钟版：这次要你确认什么

| 组 | 要你定的事 | 条数 | 不答的后果 |
|---|---|---|---|
| A | 主表 / 附表 7 处不一致，哪一列是业务上正确的量（Q-01） | 7 格 / 3 条 ORI | 采用值只能一直挂"临时"，S2 不能定稿 |
| B | 4 SKU 与 5 SKU 的真实分界（Q-02） | 1 | `SR-09` 继续红，`RANGE 4–5` 继续要人工选档 |
| C | MEPA 是否恒 36 / HW PA 何时饱和（Q-03） | 1 | 总量保持临时偏差（SKU2 +8.0、SKU6 −0.4） |
| D | 其余 Owner 问题（含平坦总量、Risk Reserve、波次、ODM、权重、定义域…） | 14 | 对应影响标签保持不变 |

另外 **D′ 组**是本轮"试用改网页内置模式"新带来的 3 条候选问题（ORI-18 / 19 / 20），
它们**不在**规则包的 19 条里，答完是否登记由你定。

合计覆盖规则包里的 **19 条唯一 Owner 问题**（`BLOCKS_FORMALIZATION` 6、`AFFECTS_ACCURACY` 9、
`ADVISORY` 4）与 `docs/00_owner_checklist_v4.md` 的 11 问，一条不漏；
分组不重叠：**A 组 3 条**（ORI-02 / 15 / 16）+ **B 组 1 条**（ORI-04）+ **C 组 1 条**（ORI-10）
+ **D 组 14 条** = 19 条（D 组末行 Q-11 是反馈表格式，不属于 ORI）。
每条后面都标了对应的 ORI，答完就能直接写回 Owner Review Register。

## A 组 · 7 处主表 / 附表不一致（对应 Q-01，ORI-02 / ORI-15 / ORI-16）

当前采用**附表总量**（DEC-10，计 1 次）；主表派生值（每 SKU 数量 × SKU 数）只作审计，计 0 次。
两列**任何情况下都不相加**，J33 也只作解释，计 0 次。

| # | 格子 | 附表采用 | 主表推算 | 差 | 请选择 |
|---|---|---:|---:|---:|---|
| 1 | `RF Certification / SIT` @ SKU2 | 8.0 | 15.0 | −7.0 | ☐ 附表对 ☐ 主表对 ☐ 给判据：______ |
| 2 | `RF Certification / SIT` @ SKU3 | 9.0 | 15.0 | −6.0 | 同上 |
| 3 | `RF Certification / SIT` @ SKU4 | 10.0 | 15.0 | −5.0 | 同上 |
| 4 | `RF Certification / SIT` @ SKU5 | 10.0 | 15.0 | −5.0 | 同上 |
| 5 | `RF Certification / SIT` @ SKU6 | 10.0 | 15.0 | −5.0 | 同上 |
| 6 | `Green / SIT` @ SKU3 | 6.0 | 9.0 | −3.0 | 同上（主表值还与 1/N 规律不符 → ORI-15） |
| 7 | `Safety / FVT` @ SKU6 | 10.0 | 9.6 | +0.4 | 同上（主表 1.6/SKU → ORI-16、ORI-17） |

若改为采用主表口径，项目总量变化（当前 366.0 / 408.0 / 438.8 / 469.0 / 502.0）：

| SKU | 2 | 3 | 4 | 5 | 6 |
|---|---:|---:|---:|---:|---:|
| 变化 | +7.0 | +9.0 | +5.0 | +5.0 | +4.6 |

> 试用取证的现实约束：`Green/SIT` 只有 **3 SKU** 项目才看得到，`Safety/FVT` 只有 **6 SKU**
> 项目才看得到（见 `trial_kit/ROSTER.md`）。没有对应 SKU 数的项目，这一格就只能由 Owner 直接裁定。

## B 组 · 4 SKU 与 5 SKU 的真实分界（对应 Q-02，ORI-04，`SR-09` 仍红）

现状：CleanSheet 的 4 SKU 定义（C81：2–4×CPU + 2–3×GPU + 2×Panel + 2×SSD + 2×Mem）
是 5 SKU 定义（C82：3–4×CPU + 3×GPU + 2×Panel + 2×SSD + 2×Mem）的**真子集**，
工具只能报 `RANGE 4–5` 并把两档都算出来，不允许用权重压成单值（DEC-01）。

请给出**任一**即可：

1. 真实样本（≥1 条，越多越好）：项目名 + cpu/gpu/panel/ssd/mem + 实际 SKU 数 + 为什么；
   模板：`项目名 / 2 / 1 / 1 / 1 / 1 → 实际 2 SKU，因为 ______`
2. 或者明确规则（例如"GPU≥3 且 CPU≥3 即按 5 SKU"）；
3. 或者明确"4–5 一律人工判定，工具不得给单值"（这样 `SR-09` 改为按人工口径结案）。

代价参考：4 档与 5 档相差 **30.2 台**（438.8 → 469.0）。

## C 组 · MEPA 与 HW PA（对应 Q-03，ORI-10）

现行临时口径：MEPA 每 Phase 恒 36、HW PA 恒 4（来源：源表 C 列备注，非正式规则）。
影响：SKU2 约 **+8.0**、SKU6 约 **−0.4**。

☐ 是，就按恒 36 / 恒 4 定稿　☐ 否，规则是：______　☐ 分项目类型：______

## D 组 · 其余 Owner 问题（一条都别漏，答不了就写"暂不"）

| ORI | 影响标签 | 要你确认的事 | 对应 checklist | 答复 |
|---|---|---|---|---|
| ORI-01 | BLOCKS_FORMALIZATION | Panel 批注 `N*panel` 的正式业务含义（DEC-02 现在完全不参与计算） | 新增 | ______ |
| ORI-03 | AFFECTS_ACCURACY | 波次判据在哪里维护：需求表新增列 / 立项文档 / 暂不区分 | Q-06 | ______ |
| ORI-05 | BLOCKS_FORMALIZATION | ODM 差异（LCFC / HQ / Compal）无结构化规则 + 3 处 Status 未关闭 | Q-09 | ☐ 暂不 ☐ 规则文本：______ |
| ORI-06 | AFFECTS_ACCURACY | Option 项是否计入、PCBA 单位口径 | 新增 | ______ |
| ORI-07 | AFFECTS_ACCURACY | Risk Reserve 默认比例与计提基数（现 0；4 SKU 下 5% ≈ 21.94 台） | Q-05 | ______ %，基数 ☐ 基线需求 ☐ 含追加需求 |
| ORI-08 | BLOCKS_FORMALIZATION | 匹配权重 / 阈值目前由 Agent 设定（cpu1.0 gpu1.6 panel1.0 ssd1.4 mem1.4） | 新增 | ☐ 认可 ☐ 调整为：______ |
| ORI-09 | ADVISORY | 自动读取需求表所需的真实样本（与 MVP 已解耦，不阻塞试用） | 新增 | ☐ 暂不 ☐ 提供样本 |
| ORI-11 | ADVISORY | Build Plan 与 PPA sample standard 1.0 的对照样本 | 新增 | ☐ 暂不 ☐ 提供样本 |
| ORI-12 | AFFECTS_ACCURACY | EMC Test / NV / INTEL 的平坦总量是固定量还是每 SKU 量 | Q-04 | ☐ 固定 ☐ 每 SKU：______ |
| ORI-13 | AFFECTS_ACCURACY | 定义域只覆盖 2–6 SKU，超出即 `OUT_OF_DOMAIN_INPUT` | 新增 | ☐ 接受 ☐ 扩到 ______ |
| ORI-14 | ADVISORY | 缩写表与 `Green / FVT` 自相矛盾的写法 | 新增 | ______ |
| ORI-02a | ADVISORY | "源费率已验证"的口径（DEC-10 后已不再是阻塞项） | Q-07 | ☐ 导出列够用 ☐ 需要 ______ |
| ORI-02b | AFFECTS_ACCURACY | J33 是否已被采用值包含；主表/附表是否描述不同 Source 组合；天线源 / WLAN 数量是否要在 MVP 采集 | Q-10 | ☐ 暂不采集 ☐ 需要 |
| ORI-17 | AFFECTS_ACCURACY | 主表"每 SKU"列实为总量的 1/N 回推，是否长期保留为审计列 | Q-08 | ☐ 长期保留 ☐ 将来可删 |
| 反馈表格式 | — | 试用反馈表的字段/段落是否够用，缺什么 | Q-11 | ☐ 够用 ☐ 需增加 ______ |

## D′ 组 · 试用模式本身带来的新问题（**尚未登记进规则包**，规则包仍是 19 条）

这三条是"把试用改成网页内置模式"这个动作换来的新缺口，与业务数字无关，
但它们决定 S2 的"证据齐备"到底怎么定义，所以需要 Owner 一并表态。

| 候选 ORI | 影响 | 要你确认的事 | 不答的后果 | 答复 |
|---|---|---|---|---|
| ORI-18（候选） | AFFECTS_ACCURACY | 受控案例的项目名 / Key Factors / Wave 是**锁定**的，
试用因此不再覆盖"真人自己输配置、自己判波次"这一段。要不要让 1–2 位试用者
在受控案例之外，用自己的真实项目走备用通道（`docs/43` §2B）再跑一次？ | 输入体验与波次误标风险没有试用证据，
只能靠 parity / Web UI 的机器断言支撑 | ☐ 需要补跑 ☐ 不需要：______ |
| ORI-19（候选） | ADVISORY | 反馈现在只问与本案例相关的问题，"还想要什么功能 / 哪里不顺手"
只剩 Comment 一栏。要不要恢复一个结构化的"新增需求"栏？ | 功能诉求只能从自由文字里捞，
可能漏；也可能捞回一堆超出 MVP 范围的请求 | ☐ 保持现状 ☐ 增加需求栏 |
| ORI-20（候选） | BLOCKS_FORMALIZATION | 19/19 的闭合依赖页面底部**可选**区被回答。
若没人答，ORI-02a / 05 / 06 / 09 / 11 / 12 / 13 / 14 / 17 只能由你在这里直接定。
"证据齐备"是否接受"团队只答必答、其余由 Owner 定"？ | 判决会长期停在
`EVIDENCE_INCOMPLETE`，且原因不是有人反对，而是没人答 | ☐ 接受 ☐ 必须团队答完 |

> 说明：这一组**没有**写进 `artifacts/model/rule_pack_v4.json`。
> 规则包 `owner_review_item_count` 仍是 19，`tools/verify_integrity.py` 也仍按 19 条对账；
> 只有 Owner 决定登记时才会改（那属于 S2 的动作，不属于本轮）。

## D″. ORI-02 按 Function / Phase 的子决策确认区（不新增 ORI 编号）

ORI-02 仍是一条正式 ORI。试用者在不同 Function 上给出了不同结论，因此请分别裁决；只有同一个子决策里出现相反答案才算冲突。

| 子决策 | 目前证据（试用回收） | 请 Owner 明确 | 结论 |
|---|---|---|---|
| `GREEN_SIT`（Green / SIT） | C2：附表 6.0 正确，主表 9.0 是记录失误 | 6.0 适用于哪些 SKU / 项目类型 | ☐ 附表 ☐ 主表 ☐ 按条件 |
| `SAFETY_FVT`（Safety / FVT） | 无人作答（只有 C5 能看到 SKU6） | 附表 10.0 还是主表推算 9.6 | ☐ 附表 ☐ 主表 ☐ 按条件 |
| `RF_CERTIFICATION_SIT` | C1、C2：都认为主表 15 正确（「RF Certification 是15」） | 附表 8–10 与主表 15 谁是采用值；两者业务含义 | ☐ 附表 ☐ 主表 ☐ 按条件 |

> 三条子决策都填完后，回收端会停止把 ORI-02 报成「矛盾」，改报 `FUNCTION_SPECIFIC_DECISION_REQUIRED`（已在 `tools/collect_trial_feedback.py` 实现）。

## E 组 · 试用证据状态（本轮由机器给出，Owner 不用手填）

| 项 | 位置 |
|---|---|
| 试用结论 | `artifacts\validation\trial_feedback_report.json` 的 `verdict` |
| 案例覆盖与回收情况 | 同上 `trial_cases`；人读版同名 `.md` §3 |
| 7 格取证状态 | 同上 `mismatch_cell_coverage`；`.md` §4 |
| 无效件 / 旧版本 / 冲突 / 未覆盖 | `.md` §5–§7 |
| 定稿门禁 | `tools\verify_integrity.py`：规则包若为 `CONFIRMED` 而 `verdict ≠ READY_FOR_S2` → 直接失败 |

## F 组 · 答复写回哪里（顺序固定）

1. Owner 在本清单逐项写结论并签名 / 日期（或邮件答复后由记录人粘贴原文）；
2. 结论登记进 `docs/38_owner_review_register_v4.md`，对应 ORI 关闭或改写；
3. 需要改口径的，改 `tools/build_quantity_model_v4.py` / `tools/build_rule_pack_v4.py` 的**来源与规则**，
   重跑 `python tools\run_all.py`；**不直接改** `artifacts\model\rule_pack_v4.json`；
4. 采用来源若变更（A 组选主表），按 `docs/42` 的 **S3** 切换来源并重跑，同时复核 `GOLDEN_ADOPTED`；
5. 试用结论到 `READY_FOR_S2` 且上述登记完成后，才把规则包状态改为 `CONFIRMED`。

## G 组 · 本清单不做什么

- 不替 Owner 猜结论：所有格子默认"未答"，报告不会因"没人反对"而视为通过；
- 不新增团队管理、权限、审批、自学习功能；
- 不改 `original_documents\`、不改 Certification 采用来源、不改 4–5 SKU 逻辑、不动 `SR-09`；
- 不在试用中调整权重或业务数字让结果"看起来更合理"。

---

签名：__________　日期：__________　规则包版本：`RP-V4.0`　试用结论：__________
