# 41 — Directory Integrity（目录完整性报告，交付物：Directory Integrity 报告）

> 术语说明：本目录从未纳入版本控制，因此本报告不使用任何版本库术语，
> 改用 **Directory Integrity** 表述（任务要求第 6 条）。
> 机器版本：`artifacts/validation/directory_integrity_report.json` / `.md`
> 生成工具：`tools/directory_integrity_report.py`

## 1. Owner 正式输入（只读）

| 项 | 结果 |
|---|---|
| 目录 | `original_documents\` |
| 文件数 | 1（预期 1） |
| SHA-256 | `48A360FF2FFD086E41D6B90A916F64FE52D9BC13EFBA07B8377B2945C846AB5A` |
| 复验时点 | 任务开始、任务结束各一次 |
| 结论 | **ZERO CHANGES（零变更）** |

三个阶段的每一次任务都以同一算法复验：读全部字节 → SHA-256 → 与冻结清单比对。
本轮同样没有向该目录写入任何文件（所有写文件工具都带 `guard()` 拒绝写入该目录）。

## 2. 文件来源分类

分类由 `tools/directory_integrity_report.py` 依据路径与文件名规则计算，
不是人工点数；任何无法归类的文件都会让 `tools/verify_integrity.py` 直接失败。

| 来源阶段 | 含义 |
|---|---|
| `SOURCE (Owner, read-only)` | 业主正式输入，只读 |
| `Phase 1 / Phase 2 (retained)` | 早期阶段工具与文档，保留为阶段证据 |
| `Phase 3 (retained, still runnable)` | 上一轮任务工具与文档，仍可运行；文档头部已指向本轮 |
| `current task (...)` | 本轮任务交付物（内核、Schema、规则包、Web、工具、文档） |
| `task evidence (reproducible artefact)` | 可由 `tools/run_all.py` 复现的产物 |
| `INCOMING (team trial feedback)` | `feedback_inbox\` 里试用者回收回来的提交件 / 反馈表（外来证据，不是项目正式输入）；目录内的 `README.md` 与 `DROP_FILES_HERE.txt` 是说明文件，不算证据 |
| `TRIAL KIT (issued cases, blank forms)` | `trial_kit\`：S1 发卷内容（案例清单 + 空白反馈表 + `START_HERE.md` 团队说明）。空白表与说明都不是证据，被填写并放回 `feedback_inbox\` 才算 |
| `UNKNOWN` | **必须为 0** |

本轮结束时的实测数字见
`artifacts/validation/directory_integrity_report.md`（第 2 节表格）。

## 3. 变更台账

因为不是版本库目录，变更以手工台账记录：`CHANGES.md`
（本轮条目：新增文件、修改文件、退役探针、修复缺陷、复验结果）。

## 4. 本轮结论

- original_documents：**零变更**（开始与结束 SHA-256 相同）
- 来源不明文件：**0**
- 交付物全部可由 `python tools\run_all.py` 按固定顺序复现
- 历史阶段产物保留为阶段证据，未为了让目录看起来整洁而删除
- 报告术语：**Directory Integrity**（不使用任何版本库术语）——探针 `ST-03` 会检查这一点
