# 45 · S1 网页内置试用模式（Trial mode）与单一提交件

> 本轮只改「试用者怎么把反馈交回来」这一件事：手工填案例 + 外部 CSV + Analysis JSON
> → 网页里选案例 → 跑 → 答本案例涉及的问题 → 导出**一个** Submission JSON。
> 业务规则、Certification 采用口径、4–5 SKU 范围、SR-09、规则包状态、所有业务数字都没动。

---

## 1. 试用者视角的前后对比

| 步骤 | 旧流程 | 现在 |
|---|---|---|
| 找到要跑什么 | 读 `trial_kit\ROSTER.md`，自己抄项目名与 Key Factors | 在 `web\index.html` →「参加团队试用」里点一个案例 |
| 输入 | 在「新建分析」逐格手输；C5 还要自己把 cpu5 / panel3 选成「后续波次」 | 自动填写并**锁定**（页面上没有可编辑的配置框） |
| 运行 | 点运行 | 点运行（同一个按钮语义） |
| 反馈 | 打开导出的 CSV，在 Excel 里对 5 个区块逐行填，其中包括**全部 19 条** ORI | 页面上只列**本案例真正涉及**的 6–11 条必答；其余 ORI 折叠在可选项里 |
| 交回 | 反馈表 CSV + `sample-analysis-*.json` 两个文件 | 一个 `trial-submission-<项目>-<时间>.json` |
| 收卷 | `python tools\collect_trial_feedback.py` | 同一条命令（旧格式仍照收） |

---

## 2. 案例数据只有一个来源

```
tools/issue_trial_forms.py            ← 案例定义（Key Factors 取自 CleanSheet C79:C83）
        │  用 prototype/rules_v3.py 实算预期结果与「这一案例会暴露哪几格」
        ├──→ trial_kit/roster.json     ← 回收端用（发卷台账）
        ├──→ trial_kit/ROSTER.md       ← 不用网页的人看的清单
        ├──→ trial_kit/forms/*.csv     ← 备用通道空白表
        └──→ web/assets/trialkit.js    ← 网页用（window.TRIALKIT）
```

`web\trial.html` 里**没有**任何案例数据：它读 `trialkit.js`。
`tools/verify_integrity.py` §9d 检查「页面给出的案例列表 == 发卷台账」，
所以页面不可能悄悄多出案例、少掉案例或换成旧规则包的案例。

`trialkit.js` 不含生成时间戳，因此对同一规则包是**逐字节稳定**的，
`python tools\issue_trial_forms.py --check` 才能区分「真的被改过」和「只是重跑了一次」。

---

## 3. 「只显示当前案例实际涉及的问题」是怎么定的

每个案例的问题清单由**这条案例自己跑出来的事实**决定，不是拍脑袋：

| 触发条件（来自内核输出） | 生成的必答问题 | 顺带覆盖的 Owner 问题 |
|---|---|---|
| 该案例实算出现某格主表/附表不一致 | 「这一格里附表 X 与主表推算 Y，哪个才是业务上正确的数量」 | ORI-02（+ `RF Certification` 格 → ORI-02b；Green/SIT@3 → ORI-15；Safety/FVT@6 → ORI-16） |
| 结果里出现 `RANGE`（4 与 5 同时成立） | 「这个范围在你的项目里能接受吗？不能的话你靠什么判定」 | ORI-04、ORI-08 |
| 登记了波次相关待确认项 | 「你们实际按什么条件划分当前/后续波次」 | ORI-03 |
| 登记了认证校验类待确认项 | 「这些提示看得懂吗？影响你使用结果吗」 | ORI-02、ORI-02b |
| Panel Spec 数 ≥ 2 | 「源表 N*panel 批注到底指什么」 | ORI-01 |
| 每个案例都有（Function 明细里就有这两行） | MEPA/HW PA 固定量是否成立 | ORI-10 |
| 每个案例都有（合计按 0% 算出来） | Risk Reserve 默认 0 是否符合实际 | ORI-07 |
| 每个案例都有 | 输出看得懂吗、字段够用吗 | — |

结果：

- 必答条数 **C1 6 / C2 7 / C3 7 / C4 9 / C5 11**；
- 必答覆盖的 Owner 问题 **10/19**（ORI-01、02、02b、03、04、07、08、10、15、16）；
- 其余 **9 条**（ORI-02a、05、06、09、11、12、13、14、17）在每个人页面底部的**可选**区，
  可空；整轮 19/19 都能被问到，没有任何人被要求独自答完 19 条。

> 闸门：`§9d` 检查「必答问题 ≠ 19 条」（否则等于没减负）
> 且「每人必答 ∪ 可选 == 19 条」（否则等于偷偷丢问题）。

---

## 4. Submission JSON 里有什么

`trial-submission-<项目名>-<时间>.json`（UTF-8，缩进 JSON，可直接 diff）：

| 字段 | 内容 | 为什么必须在 |
|---|---|---|
| `case_id` / `project_name` / `analysis_id` | 案例、逐字项目名、本次分析 ID | 回收对账的键 |
| `analysis_input` | 发卷时锁定的输入（项目名、Key Factors、Wave、Risk Reserve） | 「Analysis 输入」要求 |
| `analysis` | 完整的分析导出（与 `sample-analysis-*.json` 同结构、同内核） | 「Analysis 结果」要求 |
| `rule_package_version` / `roster_rule_pack` | 跑的时候用的规则包 / 案例发卷时的规则包 | 旧规则包不作定稿证据 |
| `exercised_skus` / `scenarios` / `registered_items` | 真的给哪些 SKU 数出过价、两个波次场景、登记了哪些待确认项 | 证明「跑过」而不是「答过」 |
| `exercised_mismatch_cells` / `covered_mismatch_cells` | 实算出现的不一致格 / 案例应覆盖的格（含 `exercised` 布尔） | 覆盖目标可核验 |
| `reviewer.name` / `reviewer.date` | 姓名与日期 | 缺任一 → UNATTRIBUTED |
| `feedback.required[]` | 每条必答题的 `id`、问题原文、`answer`、`comment`、对应 ORI | 反馈主体，逐字保留 |
| `feedback.optional_oris[]` | 可选题的答复（可空） | 让 19/19 可闭合 |
| `feedback.comment` | 总体 Comment（真实项目名写这里） | 任务要求 |
| `submit_checks[]` | 页面自检结果（**仅供参考**） | 见第 5 节 |
| `config_locked` / `certification_override_used` | 配置锁定声明；是否出现过用户覆盖值 | 页面被绕过时会露出来 |
| `generated_at_utc` | 生成时间 | 任务要求 |

---

## 5. 六道提交前校验：页面算一遍，回收端再算一遍

| 校验 ID | 挡的是什么 | 页面 | 回收端 |
|---|---|---|---|
| `REVIEWER_NAME` | 没署名 → 无法归因 | 不填则导出按钮灰 | 标 `unattributed`，不作定稿证据 |
| `REVIEW_DATE` | 没有时间点的反馈无法解释 | 同上 | **本轮起**：缺日期同样算 `unattributed` |
| `CASE_RUN` | 没跑过就没有事实可评 | 无结果时不放行 | 提交件里没有 scenarios → 判未跑 |
| `RULE_PACK` | 旧规则包的数评的是旧规则 | 与当前规则包不符则不放行 | 与 `rule_pack_v4.json` 不符 → `stale` |
| `REQUIRED_ANSWERED` | **空白不算同意** | 必答题留空不放行 | 逐题按字面判定，空 → `UNANSWERED` |
| `TARGET_CELLS_EXERCISED` | 案例存在的理由就是那一格 | 目标格没跑到不放行 | 对照发卷台账的 `covers_cells` 核验 |

回收端**不采信** `submit_checks` 里写的结论：它从文件里的分析结果自己重算
（`submission_gates()`）。手改过、伪造过、过期过的文件会被点名并列进
`submission_gate_findings`，同时把判决压回 `DECISION_REQUIRED`。

---

## 6. 回收端的取舍（以及为什么没有降低证据要求）

| 情形 | 处理 |
|---|---|
| 只有 `trial-submission-*.json` | 采信；分析、跑过的 SKU 数、出现的不一致格都从文件内部读 |
| 只有旧版 CSV + `sample-analysis-*.json` | 照旧采信（格式兼容，不减分） |
| 同一项目既有提交件又有旧 CSV | **按提交件统计**；旧文件登记为 `superseded_legacy_files`，不重复计入，也不删除 |
| 必答题空白 | `UNANSWERED`，进缺口清单；绝不会折算成同意 |
| 缺姓名**或**缺日期 | `UNATTRIBUTED`，不作定稿证据 |
| 旧规则包 | 照常统计，但明确标注不作定稿证据；判决最多到 `DECISION_REQUIRED` |
| 案例目标格没跑到 | `TARGET_CELLS_EXERCISED` 失败，进无效件清单 |

判决四态与阈值**未改**：要走到 `READY_FOR_S2`，仍然需要
3 个差异组都有明确答复 + **19 条 Owner 问题全部**有明确答复 + 无冲突 / 无旧版本 /
无缺署名 / 无重复 Analysis ID。网页试用只减少**每个人被问到的条数**，
没有减少**整轮必须收齐的证据**。

自检：`python tools\collect_trial_feedback.py --self-test` → **95 项**，
其中包含「C2+C5 两份提交件即可答满 19 条与 3 组差异」「加 C1 后 7/7 取证」
「缺姓名 / 缺日期 / 旧规则包 / 未跑 / 目标格没跑到 全部被拦」
「同一项目提交件优先、旧 CSV 只登记」以及「`web/assets/trial.js` 仍写出回收依赖的每个字段」。

---

## 7. 本轮明确没有做的事

- 没有加团队管理、账号、权限、审批流、自学习；提交件仍是本机导出的普通文件。
- 没有改 Certification 采用口径（仍 DEC-10 附表，采用 1 次、主表派生值计 0 次）。
- 没有改 4–5 SKU 行为（仍给 RANGE，仍登记 `SKU_TIE_NOT_RESOLVABLE`，SR-09 仍红）。
- 没有改规则包状态（仍 `RP-V4.0` / `DRAFT_PENDING_OWNER`）。
- 没有改任何业务数字：`366.0 / 408.0 / 438.8 / 469.0 / 502.0` 不变。
- 没有碰 `original_documents\`（SHA-256 复验一致）。
- 没有新增第四个判决状态，也没有把「案例覆盖」塞进 `READY_FOR_S2` 的阈值。

---

## 8. 这一轮的取舍带来的新缺口（如实记录，统一进 Owner 清单）

| 编号 | 缺口 | 为什么算缺口 |
|---|---|---|
| **ORI-18**（待登记） | 案例配置锁定后，试用不再覆盖「真人自己输入 Key Factors / 自己判波次」这一段 | 原 RISK-11 里「试用者会不会标错波次」这类问题只能靠真实项目自由输入才能暴露；计算正确性仍由 parity 40/40 与 Web UI 81/81 覆盖，但**输入体验**这一维本轮没有证据 |
| **ORI-19**（待登记） | 反馈被裁剪成本案例相关问题后，「我还想要什么功能 / 哪里不顺手」只剩 Comment 一栏 | 结构化自由反馈通道变窄；如果团队更习惯逐条写表单，备用 CSV 通道仍在，但不会自动汇总 |
| **ORI-20**（待登记） | 19/19 的闭合依赖**可选区**被回答；实践上可选区常常没人答 | 若没人答，ORI-02a/05/06/09/11/12/13/14/17 只能走 `docs/44_owner_confirmation_one_shot_v4.md` 由 Owner 直接定；这不影响规则正确性，但影响 S2 的「证据齐备」定义 |
| — | 姓名与日期是自报，工具不验真（任务范围明确排除账号体系） | 提交件可被手改署名；回收端只能标注，不能核实身份。因此试用结论的证据强度是「署名自报 + 内容可复算」 |
| — | 一条案例 = 一份提交件；同一案例多人提交会各自计入同一组问题 | 多人同答会产生冲突项（这是设计意图：冲突要 Owner 裁决），但需要收卷人知道「同一案例多人交」不是重复提交而是分歧证据 |

> 建议：ORI-18 用一个「自由输入」补充案例解决（让 1–2 位试用者在受控案例之外，
> 用自己的真实项目跑一次并写 Comment），ORI-19 / ORI-20 由 Owner 在一次性清单里直接定。

---

## 9. 怎么验（本轮涉及的每一条命令）

```
python tools\issue_trial_forms.py            :: 发卷 + 生成 trialkit.js（打印必答/可选分布）
python tools\issue_trial_forms.py --check    :: 空白表与 trialkit.js 是否被改过
python tools\collect_trial_feedback.py --self-test   :: 95 项（含提交件契约、六道门禁、旧格式）
python tools\collect_trial_feedback.py       :: 收卷（提交件优先，旧格式兼容）
python tools\check_web_ui.py                 :: 81 项（新增 UI-40…UI-49 驱动真实 trial.html）
python tools\verify_integrity.py             :: 181 项（新增 §9d 试用模式闸门）
python tools\run_all.py                      :: 固定顺序全跑（已含 issue_trial_forms）
```
