# feedback_inbox — 试用反馈回收目录（外来证据）

放什么：试用者填好后**复制**进来的。两种格式都收，**优先采信提交件**。

推荐（网页内置试用模式，`web\trial.html`）：

- `trial-submission-<项目>-<时间>.json` —— 一个文件就够：锁定的输入、完整分析、
  实际跑到的 SKU 数与差异格、逐题回答、姓名日期都在里面，
  回收端还会用它独立复检六道门禁。

备用（不用网页）：

- 必须：`trial-feedback-<项目>-<时间>.csv`（Web 结果页导出的那份）
- 必须：`sample-analysis-<项目>-<时间>.json`
  没有它，汇总只能说到"这一组被回答了"，说不到"这一格真被跑到过"
  （状态会写成 `ANSWERED_NO_JSON`）
- 可选：`sample-review-<项目>-<时间>.csv`（团队评审表，便于追溯）

同一项目既有提交件又有旧 CSV 时：按提交件统计，旧文件登记进
`superseded_legacy_files`（只登记、不删除、不重复计入）。

怎么用：

```
python tools\collect_trial_feedback.py
```

产出 `artifacts\validation\trial_feedback_report.md`（人看）与 `.json`（机器读）。

## 规矩

1. **只新增，不修改已回收的文件**。要更正就再导一份新的放进来；
   同一 `Analysis ID` 重复提交会被报告点名。
2. 空白表留在 `trial_kit\forms\`，**不要在那里就地填写**；填完的这份复制到这里。
3. 空白 ≠ 同意。没写的条目一律算 `UNANSWERED`，含糊表述算 `OTHER`，都不算回答。
4. 姓名 / 日期**缺任何一个** → `UNATTRIBUTED`，报告标注"不作为定稿证据"
   （提交件同样适用：`reviewer.name` / `reviewer.date` 缺一样就挡下来）。
5. 规则包版本与当前 `RP-V4.0` 不一致的反馈表仍然统计，但明确不作为定稿证据。
6. 不是反馈表的 CSV、既不是提交件也不是分析导出的 JSON →
   工具**报错并点名文件**，不会被误算。
6b. 提交件里 `submit_checks` 写的"已通过"**不被采信**：
   回收端按文件里的分析结果重算姓名、日期、是否真跑过、规则包、必答题、目标差异格；
   不合格的文件进 `submission_gate_findings` 并压低判决。
7. 想先演练：`--inbox <临时目录> --report-dir <临时目录>`，别动这里的正式证据。

本目录是**外来证据**，不是项目正式输入（正式输入只有 `original_documents\`）；
汇总工具只读不写这里，也绝不修改规则包。
