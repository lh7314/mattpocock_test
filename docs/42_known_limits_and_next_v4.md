# 42 — 已知限制与下一步建议（DEC-10 之后）

## A. 当前版本能做什么（可交付给团队试用）

- 手动输入关键配置 → SKU 档位建议（含 4–5 范围）→ 按 Function × Phase 的样机需求明细
- Certification **采用附表总量**（DEC-10），只计入 1 次；主表值与主表派生值在展开详情中作审计
- 当前波次 / 全项目两个情景；波次永不改变同一 SKU 档位的 base_demand
- Reuse 四态账本（只有已证明的额外复用才抵扣）；PCBA 永不与台数相加
- 三种导出：JSON（完整精度）、团队 Review CSV（8 段）、试用反馈 CSV
- 全部离线：双击 `web\index.html`；Python 内核与 Web 内核由 40 个一致性用例锁死

## B. 已知限制（试用前必须让团队知道）

| # | 限制 | 现状处理 | 何时会咬人 |
|---:|---|---|---|
| A1 | 5 SKU 结构上无法被单独推荐（4 SKU 定义是其子集） | 输出 `RANGE 4–5`，两档都算 | 需要单一 SKU 结论时（等 ORI-04 样本） |
| A2 | Certification 采用值是**临时决定**，不是定稿规则 | 规则包 `DRAFT_PENDING_OWNER`；导出文件写明 `APPENDIX_ADOPTED_TOTAL (DEC-10)` | 源表作者若主张主表口径 → 需改 `adopted_source` 并重跑（可回退） |
| A3 | 7 处主表/附表差异未解释 | 逐格上报，进 Register（ORI-02/15/16） | 若业务上应取主表：SKU2–6 会变 +7/+9/+5/+5/+4.6 台 |
| A4 | MEPA / HW PA 是临时 `PER_PHASE_FIXED` | 界面显示"临时采用" | 业务确认前，SKU2 有 +8.0 台、SKU6 有 −0.4 台偏差 |
| B1 | 分析记录存在浏览器 localStorage | 提供 JSON 导出；提示及时备份 | 换机器 / 清缓存 |
| B2 | 覆盖输入是绝对台数，无草稿校验 | 与采用值、主表值三者并存并可导出 | 填错只能重跑一条分析 |
| B3 | 无团队空间、无账号、无权限、无审批 | 明确排除在范围外 | 需要协作评审时只能靠导出文件 |
| B4 | 波次判据未落地，`未特别指定` 计入当前波次 | Current Wave 常等于 Full Project | 需求表加入波次列后才有真实差异 |
| B5 | 只覆盖 2–6 SKU 定义域 | 越界输入**只停该情景**并解释 | 真实项目出现 7 SKU 时（ORI-13） |
| B6 | J33 只能解释 11–27 区间的特定组合，附表 8–10 在下限以下 | 仅作解释证据，不叠加 | 若要按天线源/WLAN 组合建模（ORI-02b） |
| C1 | Web 端是内核的**移植**，不是同一份代码 | 40 个用例逐字段 + CSV 逐行比对；任何差异都会阻断交付 | 以后改内核忘记同步 Web（闸门会抓到） |
| C2 | 显示精度只做格式化 | 导出永远是底层小数（如 `438.8`、`9.6`） | 有人把显示值抄成业务值 |

## C. 下一步（按依赖顺序）

| 步骤 | 内容 | 依赖 | 量级 |
|---|---|---|---|
| **S0** | Owner 一次性确认：试用结束后按 `docs/44_owner_confirmation_one_shot_v4.md`（含 `docs/00_owner_checklist_v4.md` 的 11 问）一轮答完 | 无（试用期间不逐条问） | 回答即解锁后续全部步骤 |
| **S1** | 团队试用 3–5 条真实项目：网页内置试用模式选案例 → 跑 → 答本案例涉及的问题 → 导出**一个** `trial-submission-*.json`（发卷 `python tools\issue_trial_forms.py`，入口 `web\index.html`，说明 `trial_kit\START_HERE.md`，设计 `docs/45_trial_web_mode_v4.md`，回收命令 `python tools\collect_trial_feedback.py`；旧 CSV+JSON 通道继续可用） | 已发卷 + 网页试用模式已就绪（5 条案例，覆盖 7/7 差异格）；**仍无人提交** | 0.5 天 |
| **S2** | 按 S0/S1 结论把规则包 `DRAFT` → `CONFIRMED`（含 7 格处置结论） | S0、S1 | 0.5 天 + 重跑闸门 |
| **S3** | 若采用口径再次变化：切换 `adopted_source` 并复跑 `tools\run_all.py`（差异表即变化清单） | 决定变化时 | 0.5 天 |
| **S4** | 真实样本到位后做自动读取（ORI-09），并用 `main_table_derived_total` 做回归对比 | ORI-09 样本 | 3–5 天 |
| **S5** | Build Plan / PPA sample standard 对比（ORI-11） | ORI-11 样本 | 2 天 |
| S6 | 若业务要求：波次列落地（ORI-03）后启用 Current Wave 的真实分叉 | ORI-03 判据 | 1–2 天 |

**不要提前做的事**：S4/S5 在拿到样本前不要开工；不要为让 SR-09 变绿而调整权重（那是 DEC-01
明令禁止的"用权重压结论"）；不要在 S0 之前把规则包改成 CONFIRMED。

## D. 复现与验收（一条命令）

```
python tools\run_all.py            # 16 步，末行 PIPELINE: ALL GREEN
python tools\run_all.py --history  # 追加历史阶段套件（逐条说明其停用原因）
```

当前基线：`validate_rules_v4` 120 探针（119 持有 + SR-09 设计失败）·
`check_python_web_parity` 40/40 MATCH · `check_web_ui` 81/81 CLEAN（含试用模式 UI-40…UI-49）·
`verify_integrity` PASS（181 项，含 §9d 试用模式闸门）· `collect_trial_feedback --self-test` 95 项 ·
`directory_integrity_report` CLEAN（来源不明 0）·
`collect_trial_feedback` 自检 60/60，已发卷 5 条案例（覆盖 7/7 差异格），当前试用结论 `TRIAL_NOT_STARTED`（尚未回收反馈表，不阻塞交付）·
`original_documents` SHA-256 任务首尾一致。
