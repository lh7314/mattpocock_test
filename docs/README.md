# 样机需求分析与建议 Agent — 工作目录索引

- 正式输入（只读）：`original_documents\`，
  SHA-256 `48A360FF2FFD086E41D6B90A916F64FE52D9BC13EFBA07B8377B2945C846AB5A`
- 当前版本：计算内核 `rules_v3/4.0`、数量模型 `QMODEL-V4/4.0`、规则包 `RP-V4.0`、
  Schema `4.0`、Owner 决定 **DEC-10（Certification 采用附表总量）**，规则包状态 **DRAFT**
- 一键复现：`python tools\run_all.py`（加 `--history` 连带运行历史阶段测试套件）
- Web MVP：双击 `web\index.html`（离线，无需服务器、账号或权限）

## Python 环境

以下命令在项目根目录（包含 `tools/`、`prototype/` 和 `web/` 的目录）执行。
完整环境记录如下：

| 项目 | 当前验证环境 |
|---|---|
| 操作系统 | Windows，x86-64 |
| Python | 3.12.4，版本记录在 `.python-version` |
| 包管理器 | pip 24.0 |
| Python 依赖 | `requirements.txt` 固定全部 9 个已安装包的版本，包含 pip、2 个直接依赖及 6 个传递依赖 |
| 浏览器 | Python/Web 一致性及页面检查需要本机安装 Chromium 系 Edge 或 Chrome |

`requirements.txt` 安装 Python 包；Python 解释器和浏览器需要单独安装。
`.python-version` 记录目标版本，`python -m venv` 本身不会根据它自动切换解释器。

首次配置，或移动项目后重新创建环境：

```powershell
python --version  # 应为 Python 3.12.4；否则先选择对应解释器
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

日常运行可直接使用虚拟环境解释器，无需激活或修改 PowerShell 执行策略：

```powershell
.\.venv\Scripts\python.exe tools\lint_sources.py
.\.venv\Scripts\python.exe tools\run_all.py
```

若需要激活，在当前 PowerShell 终端执行 `.\.venv\Scripts\Activate.ps1`，
之后使用 `python`；结束时执行 `deactivate`。也可在 IDE 中选择
`.venv\Scripts\python.exe` 作为项目解释器。

`.venv/` 是本机生成的环境目录，不提交到 Git；共享项目时提交
`requirements.txt`，由接收者重新创建环境。Web 页面仍可直接离线打开；
Python/Web 一致性和界面检查另外需要本机安装 Edge 或 Chrome。

安装后可执行 `.\.venv\Scripts\python.exe -m pip freeze --all` 核对全部包的版本。
以后升级依赖时，验证通过后一起更新 `requirements.txt` 中的直接和传递依赖版本，
避免只修改其中一个版本导致环境不一致。

## 本轮（DEC-10）先看这四篇

| 文档 | 内容 |
|---|---|
| `36_certification_adoption_v4.md` | 采用值语义修正 + 40 格逐格复核 + J33 复述（交付物 A/B/C） |
| `37_owner_decision_log_v4.md` | DEC-10 记录，以及哪些既有决定保持不变 |
| `39_totals_v4_and_6sku_review.md` | SKU2–SKU6 重算、变化归因、**6 SKU 专项复核**（交付物 D） |
| `40_web_mvp_v4_changes.md` | 三页 MVP 的改动、导出、一致性与界面探针（交付物 E） |

| 文档 | 内容 |
|---|---|
| `38_owner_review_register_v4.md` | Owner Review Register：19 条**唯一问题**，影响标签单独统计（6 / 9 / 4） |
| `41_directory_integrity_v4.md` | 目录完整性报告（不使用任何版本库术语） |
| `42_known_limits_and_next_v4.md` | 已知限制（14 条）与下一步（S0–S6） |
| `00_owner_checklist_v4.md` | 任务结束时的一次性确认清单（11 问，含台数与推荐选项） |
| `43_trial_pack_v4.md` | **S1 团队试用包**：怎么发卷、试用、填反馈表、回收一条命令、定稿证据要求 |
| `44_owner_confirmation_one_shot_v4.md` | **Owner 一次性确认清单**：试用结束后一轮答完，19 条 ORI + 11 问全覆盖，分组不重叠 |
| `45_trial_web_mode_v4.md` | **S1 网页内置试用模式**：案例单一来源、每案例只问相关问题、单一 Submission JSON、六道提交前校验（页面 + 回收端各算一遍）、新增缺口 ORI-18/19/20 |

导出契约（JSON / 团队 Review CSV / 试用反馈 CSV 的字段与不变量）见 `40_web_mvp_v4_changes.md` §3。

## 内核与规则

| 路径 | 内容 |
|---|---|
| `prototype/rules_v3.py` | 计算内核（**行为基准**）+ 三个导出器（JSON / Review CSV / 试用反馈 CSV） |
| `artifacts/model/quantity_model_v4.json` | 每格采用值、证据角色、主表审计数据 |
| `artifacts/model/certification_verification.json` | 40 格逐格核对（33 一致 / 7 不一致 / 0 无法判定） |
| `artifacts/model/rule_pack_v4.json` | 规则包 RP-V4.0（Python 与 Web 共用的唯一数字来源） |
| `artifacts/model/model_delta.json` / `.md` | 三方总量对比与归因（残差为 0） |
| `schema/input.schema.json`、`schema/output.schema.json`、`schema/rule.schema.json` | 契约（4.0） |

## 验证

| 工具 | 作用 |
|---|---|
| `tools/validate_rules_v4.py` | 回归探针套件（122 项，含探针台账 ST-01） |
| `tools/check_python_web_parity.py` | Python ↔ Web 完整结构化输出一致性（40 用例 + 三种导出） |
| `tools/check_web_ui.py` | 三页 Web MVP 端到端界面探针（44 项） |
| `tools/verify_integrity.py` | 交付闸门（SHA、数字复算、Schema const、台账、术语、文件分类） |
| `tools/directory_integrity_report.py` | 目录完整性报告（不使用任何版本库术语） |
| `tools/lint_sources.py` | 结构体检：可编译、可解析、无乱码、文档引用不悬空 |
| `tools/issue_trial_forms.py` | S1 发卷：固定 5 条案例（Key Factor 取自 CleanSheet C79:C83）、用内核算预期结果、生成空白反馈表 + 每案例问题范围 + `web/assets/trialkit.js`；覆盖 7/7 差异格 |
| `tools/collect_trial_feedback.py` | 试用反馈回收汇总（S1 → S2 证据）：95 项自检 + 四态结论 + 案例覆盖 / 7 格取证 / 无效件清单；`trial-submission-*.json` 优先、旧 CSV+JSON 兼容，回收端独立复检六道门禁 |

## Expected Failure 政策

唯一被批准的 Expected Failure 是 **SR-09**（ORI-04：4 SKU 定义是 5 SKU 的子集，
真实分界条件未由 Owner 给出）。它变绿即为回归；新增任何 Expected Failure 都需要批准。

## 历史阶段文档

`01…21` 是 Phase 1 / Phase 2 的设计与决定记录，`22…35` 是 Phase 3a（Certification 修正为
主表口径）的完整交付记录，均按原文保留；`22…35` 头部已加说明并指向本轮 v4 文档。
