# 43 — 团队试用包（S1：真实项目试用 → 反馈 → 定稿证据）

> 定位：`docs/42_known_limits_and_next_v4.md` 的 **S1** 步骤。
> S1 不等 Owner 回答 Q-01/Q-02/Q-03：**试用本身就是收集证据的动作**，
> 回答与不回答都会原样体现在汇总报告里。
> 机器版本：`artifacts/validation/trial_feedback_report.json` / `.md`
> 发卷工具：`tools/issue_trial_forms.py` → `trial_kit/ROSTER.md` + 空白反馈表
> + 网页案例数据 `web/assets/trialkit.js`
> 试用模式：`web/trial.html`（选案例 → 跑 → 答本案例的问题 → 导出一个 Submission JSON）
> 团队入口说明：`trial_kit/START_HERE.md`；投递说明：`feedback_inbox/DROP_FILES_HERE.txt`
> 设计说明：`docs/45_trial_web_mode_v4.md`
> 汇总工具：`tools/collect_trial_feedback.py`（自带 95 项自检，已进流水线；
> 提交件优先、旧格式兼容，并在回收端独立复检六道门禁）

## 0. 先"发卷"（一条命令，跑一次就够）

```
python tools\issue_trial_forms.py
```

它做三件事：固定 5 条案例、用**内核自己**算出每条案例的预期结果、生成 5 份空白反馈表
（`trial_kit\ROSTER.md`、`trial_kit\roster.json`、`trial_kit\forms\*.csv`）。
案例的 Key Factor 全部取自 CleanSheet 自己的 SKU 定义（C79:C83），不是编的示例。

它同时生成 `web/assets/trialkit.js`：网页试用模式只能显示这份清单里的案例，
`tools/verify_integrity.py` §9d 会核对「页面案例列表 == 发卷台账」，
所以页面不会多出案例、也不会停留在旧规则包。团队看 `trial_kit\START_HERE.md` 即可上手。

**为什么必须先发卷**：7 个仍然不一致的格子长在特定 SKU 数上，
项目没跑到那个 SKU 数，就永远取不到那一格的证据：

| 差异格 | 需要的 SKU 数 | 由哪条案例覆盖 |
|---|---|---|
| `Green / SIT @ SKU3`（附表 6.0 / 主表推算 9.0） | 必须是 3 SKU | C2 |
| `Safety / FVT @ SKU6`（附表 10.0 / 主表推算 9.6） | 必须是 6 SKU | C5 |
| `RF Certification / SIT @ SKU2` | 2 SKU | C1 |
| `RF Certification / SIT @ SKU3` | 3 SKU | C2 |
| `RF Certification / SIT @ SKU4` | 4 SKU | C3 / C4 |
| `RF Certification / SIT @ SKU5` | 5 SKU | C4 / C5 |
| `RF Certification / SIT @ SKU6` | 6 SKU | C5 |

只跑简单项目 → 7 格里最多拿到 2 格。这就是 5 条案例不可随意替换的原因。
`--check` 可以随时检查发卷内容是否被就地改动或已随规则包过期。

## 1. 跑几条、谁跑

| 项 | 建议 |
|---|---|
| 条数 | 3–5 条**真实**项目；手上没有就按 `trial_kit\ROSTER.md` 的 5 条案例跑，并在 Comment 里写清是案例配置 |
| 人员 | 每条 1 人操作 + 1 人复核结果（复核人写在反馈表 Reviewer name） |
| 时间 | 单条约 10 分钟：填输入 3 分钟、看结果 5 分钟、填反馈表 2 分钟 |
| 覆盖重点 | 5 条案例合计覆盖 **7/7** 差异格；缺一条就有点名的格子取不到证 |
| 必须包含 | 一条 3 SKU（C2）、一条 6 SKU（C5），否则 `Green/SIT`、`Safety/FVT` 永远没有证据 |

## 2A. 操作（推荐：网页内置试用模式，四步）

```
1) 双击  D:\GAMING_NRE_AGENT\web\index.html  → 点「参加团队试用」
2) 选一个案例（C1…C5）→「载入并运行」：项目名、Key Factors、Wave 自动填好并锁定
3) 看结果 → 只回答这个案例实际涉及的问题（6–11 条）→ 填姓名与日期
4) 点「导出试用提交件」→ 得到一个 trial-submission-<项目>-<时间>.json
   → 放进 feedback_inbox\
```

页面上的六道提交前校验（姓名 / 日期 / 已运行 / 规则包 / 必答 / 目标差异格）
在回收端会**再算一遍**：页面自检只是提示，判据是文件里的事实。
每条案例问什么、为什么只问这些，见 `docs/45_trial_web_mode_v4.md` §3。

## 2B. 操作（备用：不用网页的五步，标准完全一样）

```
1) 双击  D:\GAMING_NRE_AGENT\web\index.html          （或整个 web\ 目录拷给同事）
2) 新建分析：Project Name + 五个 Key Factor（CPU / GPU / Panel / SSD / Memory 数量）
             逐 Spec 波次按需标记 LATER_WAVE；高级选项可留空
3) 运行分析 → 结果页（SKU 档位或 4–5 范围、Current Wave、Full Project、Function 明细）
4) 导出三份文件：JSON（完整精度）+ 团队 Review CSV + 试用反馈表 CSV
5) 用 Excel 打开试用反馈表，填 Reviewer name / Review date 与各段答案，保存
```

界面字段含义与文案见 `docs/30_ui_fields_and_copy_v3.md`；
导出文件字段契约见 `docs/40_web_mvp_v4_changes.md` §3。

## 3. 反馈表怎么填（判定口径很重要）

| 段 | 问的是什么 | 填法 |
|---|---|---|
| 1 本次结果逐项确认 | SKU 结论、各档总量、采用值口径是否认可 | `同意` / `不同意` / `待确认` + 说明 |
| 2 主表/附表仍不一致的格子 | **哪个数字才是业务上正确的量**（Q-01） | 在 `Is the adopted value correct?` 列填 `同意`（附表对）或 `不同意`（主表对）+ 依据 |
| 3 本次登记的待确认问题 | 这条分析自己冒出来的问题 | 同上三选一 |
| 4 规则包 19 条唯一 Owner 问题 | 与具体项目无关的口径问题 | 同上三选一；不知道就留空，别写"略" |
| 5 界面与流程反馈 | 字段够不够、看不看得懂、导出够不够用 | 自由文字，越具体越好 |

三条硬规则（汇总工具按此判定，界面不解释）：

- 只有写明的 `同意` / `不同意` 才算**回答了**；`待确认` 算"看到了但没决定"；
  含糊表述（如"先这样吧"）一律归入"其它"，**同样不算回答**，但会在报告里逐字列出。
- **空白 ≠ 同意**。汇总报告永远把没回答的条目列成缺口清单，不会因为多数人没意见就通过。
- 反馈表只增不改：要更正就再导一份新的放进回收目录（同一 `Analysis ID` 重复提交会被点名）。

## 4. 回收（一条命令）

把 `trial-submission-*.json`（推荐）**或者**「反馈表 + 分析 JSON」这一对放进
`feedback_inbox\`，然后：

```
python tools\collect_trial_feedback.py
```

产出 `artifacts\validation\trial_feedback_report.md`（人看）与 `.json`（机器读）。
不是反馈表的 CSV 会让它**报错并点名文件**——防止别的表格混进来被误算。

回收目录的三条规矩：

- **只新增，不改已回收的文件**。要更正就再导一份新的放进来；
- 空白表留在 `trial_kit\forms\`，**不要在那里就地填写**（`--check` 会发现发卷内容被改动）；
- 想先演练一遍再动真格：`--inbox <临时目录> --report-dir <临时目录>`，
  这样不会覆盖 `artifacts\validation\` 里那份正式证据。

JSON 不是可选项：没有它，汇总只能说"这组被回答了"，不能说"这一格真被跑到过"
（状态会写成 `ANSWERED_NO_JSON`）。

## 5. 报告怎么读

| 结论 | 含义 | 该做什么 |
|---|---|---|
| `TRIAL_NOT_STARTED` | 回收目录里还没有反馈表 | 按 §2 跑真实项目 |
| `EVIDENCE_INCOMPLETE` | 收到了反馈，但仍有差异格或 Owner 问题没有明确回答 | 报告点名缺哪几格、哪几条 ORI，继续找对应的人确认 |
| `DECISION_REQUIRED` | 全部条目都有明确回答，但存在**互相矛盾**、旧规则包产出、或没写姓名/日期的反馈 | Owner 就矛盾处裁决；补齐姓名与日期；旧规则包的反馈不作为定稿证据 |
| `READY_FOR_S2` | 3 个差异格 + 19 条 ORI 各有明确回答，无矛盾、无旧规则包、无匿名反馈 | 可以进入 S2：规则包 `DRAFT` → `CONFIRMED` |

报告里还有几份原始清单，**逐字保留、不改写**：

- **案例覆盖清单**：5 条发卷案例逐条标 `RETURNED` / `NOT_RETURNED` / `STALE_RULE_PACK` /
  `UNATTRIBUTED`，非清单项单独标 `RETURNED_NOT_IN_ROSTER`；
- **7 个底层差异格的取证状态**：`EVIDENCED` / `ANSWERED_NOT_EXERCISED` /
  `EXERCISED_NOT_ANSWERED` / `NOT_COVERED` / `ANSWERED_NO_JSON`；
- **无效件与旧版本清单**、**冲突反馈清单**、**尚未覆盖问题清单**；
- 所有 `不同意 / 待确认 / 其它` 的回答原文（含来自哪个文件、哪个项目）；
- 界面与流程反馈原文。

注意：案例覆盖与 7 格取证状态**只如实上报，不改变结论**。
`READY_FOR_S2` 的门槛仍是"3 组差异 + 19 条 ORI 都有明确回答、无矛盾、无旧规则包、无匿名"，
没有因为加了统计而悄悄加严，也没有因为加了统计就放松。

## 6. S2 定稿的证据要求（写在这里是为了不用口头承诺）

进入 S2 必须同时满足：

1. `trial_feedback_report.json` 的 `verdict = READY_FOR_S2`；
2. 每条反馈都能归到具体的人与日期（`Reviewer name` / `Review date` 非空）；
3. 反馈表的 `Rule pack` 与当前规则包一致（当前 `RP-V4.0`）；
4. 3 个差异格（`Green / SIT`、`RF Certification / SIT`、`Safety / FVT`）都有明确结论；
5. Owner 明确写下结论落在哪一条：改源表（Q-01 A）/ 改采用口径（Q-01 B）/ 给出判据（Q-01 C）。

完整性门禁会检查这一点：**规则包一旦是 `CONFIRMED` 而试用结论不是 `READY_FOR_S2`，
`tools\verify_integrity.py` 直接失败**——不允许"先定稿、证据以后补"。

## 7. 试用期间不要做的事

| 不要 | 原因 |
|---|---|
| 调整权重让 4–5 范围收敛成单一档 | DEC-01 明令禁止用权重压结论；SR-09 必须保持红色直到 ORI-04 有样本 |
| 把界面上的 `438.8` 抄成业务定稿值 | 显示层统一 1 位小数，导出才是底层精度（见 `docs/42` C2） |
| 直接改 `artifacts\model\rule_pack_v4.json` 的数字 | 它是生成物，重跑就没了；改数字要改生成它的模型与来源 |
| 动 `original_documents\` | Owner 正式输入，只读；本轮所有写文件工具都拒绝写入该目录 |
| 用反馈表改主表 | 差异的更正应在源表或 Owner 决定里，工具只负责如实上报 |
| 在 `trial_kit\forms\` 里直接填写 | 发卷内容是"工具导出了什么"的基线；填完的那份复制到 `feedback_inbox\` |
| 试用过程中逐条去问 Owner | 试用中冒出的问题一律写进反馈表，试用结束统一并入 `docs/44_owner_confirmation_one_shot_v4.md` 一次确认 |

## 8. 试用前必须让团队知道的限制

摘自 `docs/42_known_limits_and_next_v4.md` §B，试用最容易撞到的四条：

- **A1** 4 与 5 SKU 现在输出 `RANGE 4–5`，两档都算，需要人工选档（等 Q-02 样本）；
- **A2** Certification 采用附表总量是 **DEC-10 的临时决定**，规则包仍是 `DRAFT`；
- **B1** 分析记录存在浏览器 localStorage，换机器/清缓存即丢 → 每次分析都要导出 JSON；
- **B4** 波次判据未落地，`未特别指定` 计入当前波次，所以 Current Wave 常等于 Full Project。
  C5 实测：只有把具体 Spec 明确标成「后续波次」时两个场景才会分开
  （Full Project `SINGLE 6 / 502.0`，Current Wave `RANGE 4–6`）；
  只要还有 Factor 没标完，就仍会登记 `WAVE_ASSIGNMENT_NOT_PROVIDED`。
