# 35 — 下一阶段建议（交付物 U）
> **状态（DEC-10 之后）**：本文描述的是 Phase 3a 的 Certification 口径
> （采用主表派生值）。Owner 已决定在 MVP 与团队试用阶段**采用附表总量**，
> 最新口径见 `docs/36_certification_adoption_v4.md`、`docs/37_owner_decision_log_v4.md`、
> `docs/39_totals_v4_and_6sku_review.md`、`docs/40_web_mvp_v4_changes.md`。
> 本文按原文保留，作为阶段记录。


前提：手工输入闭环已经可用（Python 内核 + Web MVP + 一致性门禁）。
下一阶段的瓶颈**不是开发量，而是 Owner 决策**。

---

## S0 · Owner 决策收口（**优先于一切开发工作**）

回答 `docs/27_owner_confirmation_checklist_v3.md` 的前 3 题即可解锁规则包定版：

| 题 | 解锁什么 | 无头绪的开发工作量 |
|---|---|---|
| ORI-02（主表 vs 附表 7 格） | 规则包定版；Certification 从「请确认」变「已验证」 | 0（改一行采用来源标记 + 重跑流水线） |
| ORI-04（4 vs 5 SKU 分界 + 真实样本） | 单一 SKU 建议；`SR-09` 按新口径重写 | 小（`match_sku` 判据 + 探针重写） |
| ORI-10（MEPA 恒 36？HW PA 饱和点？） | 取消最后 4 个「临时采用」格 | 0（改模型标注） |

**建议**：这三题一次会开完。三题都不需要写代码，只需要业务口径。

---

## S1 · 把内核从"两份实现"收成"一份发布"（1 天）

**当前状态**：`prototype/rules_v3.py` 是行为基准，`web/assets/core.js` 是移植，
24 例全字段一致（`docs/31`）。这是可用的，但每次改规则都要同步两处，靠回归测试兜底。

**建议做法**：把 **规则包作为唯一发布物**，Python 侧改为"参照实现 + 生成器"：

```
artifacts/model/rule_pack_v3.json  ← 唯一数值来源（已存在）
web/assets/rulepack.js             ← 同一对象的浏览器形态（已存在）
prototype/rules_v3.py              ← 参照实现（保留，作为回归基准）
web/assets/core.js                 ← 唯一执行实现
tools/check_python_web_parity.py   ← 发布前强制门（已存在）
```

再加两件事就够：
1. **版本号入包**：`rule_pack_version` 已随每份输出流动，补一条 `verify_integrity` 断言
   "Python 与 Web 报告的规则包版本字符串必须相同"（现在等价于比较 pack 内同一字段，已经成立）。
2. **一致性用例扩充到 40 例**：把 40 格 Certification 验证每格至少覆盖一次
   （现在 24 例已覆盖全部 Function，但没有逐 SKU 档扫过 MISMATCH 格）。

**不要做的事**：不要在 UI 里再写一套业务判断（任务 §14）。当前分层已经干净，保持它。

---

## S2 · 规则包定版与版本治理（0.5 天，依赖 S0）

- `QMODEL-V3` 与 `RP-V3.0` 从 `DRAFT_PENDING_OWNER` → `CONFIRMED`；
- `schema/rule.schema.json` 的 `rulePack.status` 已支持三态；
- 新增 **规则包差异清单**：每次 Owner 决策后自动生成
  "哪些格从 MISMATCH 变 VERIFIED、哪些 ORI 关闭、总量表怎么变"——
  本任务的 `model_delta.md` 就是这个东西的第一个实例，可以固化成常规产物。

---

## S3 · 团队试用与反馈收口（1–2 周真实使用）

MVP 已可发出去试用（`docs/29_web_mvp_run_guide.md`，双击即可）。建议收集：

1. 用户是否理解 `4–5 SKU` 范围（有没有人反复问"到底选哪个"）→ 直接反映 ORI-04 的业务痛感；
2. 「请确认」的 7 格有没有人看懂 delta 和源行号；
3. 「临时采用」（MEPA / HW PA）有没有被当成最终数；
4. Reuse 四种状态有没有被误用（特别是 `ADDITIONAL_CONFIRMED_REUSE` 但没勾"已证明"）；
5. 高级选项的三个折叠区有没有人找不到。

**建议**：让试用者**保留导出的 JSON**，把 JSON 当作反馈载体（它自带输入快照、
逐格验证与 Review Items），比截图有效得多。

---

## S4 · 需求表自动读取（3–5 天，**硬依赖 ORI-09**）

需要 Owner 先给 2–3 份真实/脱敏需求表。拿到后建议顺序：

1. 只做**识别与回显**，不做推断：列出识别到的关键配置与 Phase 数量，让用户确认；
2. 任何识别不确定项一律落成 `Review Item`，不允许静默默认；
3. 用 `file_provenance.read_mode = FILE_READ` 与手工输入区分，`file_value` 与 `user_value` 分开存
   （契约里已经有这两个字段，`file_read_value_vs_user_confirmed_value` 导出项也已就位）；
4. 真实表结构差异 → 新增 ORI，不要往现有规则里塞特例。

**风险**：真实表几乎肯定没有波次列（ORI-03），届时"Current Wave"仍只能靠人选。

---

## S5 · Build Plan 差异比较（3–5 天，**硬依赖 ORI-11**）

需要既有 Build Plan 样本 + PPA sample standard 1.0。建议：

- 先做**只读差异表**（Plan vs 本工具计算值），不做双向同步；
- SWPA 校验等"标准比对"要有正式标准文档才可上线，否则只是把两套数碰在一起。

---

## S6 · 明确**不做**的事（避免范围漂移）

账号 / 团队 / 权限 / 审批流 / 管理后台 / 在线规则编辑 / 自学习 / 企业集成 / 跨项目复用优化
—— 这些在本期被明确排除（任务 §10、`docs/34 §B`）。
若将来要加，正确的触发条件是：**试用者开始抱怨"结果无法追溯"或"没法共享"**，
而不是"看起来更专业"。当前用导出的 JSON 已经能解决追溯问题。

---

## 建议顺序与工作量

| 阶段 | 内容 | 工作量 | 依赖 |
|---|---|---|---|
| **S0** | Owner 回答前 3 题 | 0 代码 | Owner |
| **S1** | 一致性用例扩到 40 例 + 版本断言 | 1 天 | 无 |
| **S2** | 规则包定版 + 差异清单固化 | 0.5 天 | S0 |
| **S3** | 团队试用 + 用 JSON 收反馈 | 1–2 周（被动） | 无（现在就能开始） |
| **S4** | 需求表自动读取 | 3–5 天 | ORI-09 |
| **S5** | Build Plan 差异比较 | 3–5 天 | ORI-11 |

**我的建议**：S3 立刻开始（工具已经可用），同时把 S0 排进最近一次评审会。
S1 在试用期内并行做掉。S4/S5 在拿到样本前不要开工，否则会把"猜测的表结构"固化进规则。
