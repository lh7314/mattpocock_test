# 31 — Python 与 Web 一致性报告（交付物 P）
> **状态（DEC-10 之后）**：本文描述的是 Phase 3a 的 Certification 口径
> （采用主表派生值）。Owner 已决定在 MVP 与团队试用阶段**采用附表总量**，
> 最新口径见 `docs/36_certification_adoption_v4.md`、`docs/37_owner_decision_log_v4.md`、
> `docs/39_totals_v4_and_6sku_review.md`、`docs/40_web_mvp_v4_changes.md`。
> 本文按原文保留，作为阶段记录。


工具：`tools/check_python_web_parity.py`
机器可读结果：`artifacts/validation/python_web_parity.json` / `.md`

## 1. 基准与移植

- **行为基准**：`prototype/rules_v3.py`（`rules_v3/3.0`）
- **移植目标**：`web/assets/core.js`（`rules_v3_web/3.0`）
- **共同数值来源**：`artifacts/model/rule_pack_v3.json` → `web/assets/rulepack.js`（`RP-V3.0`）。
  两边读同一份规则包，前端不保存任何业务数字，因此不存在"两边各抄一份数字"的漂移可能。

**为什么要有移植**：MVP 必须能双击 `file://` 直接运行、完全离线；Python 内核无法在浏览器里执行。
移植的代价由本文件消除：两套内核在每个字段上被强制一致。

## 2. 比对方法

| 维度 | 做法 |
|---|---|
| 输入 | 24 个案例，全部以 `schema/input.schema.json` 文档形式给出（与前端提交的内容完全同构） |
| 执行 | Python 侧直接调用 `analyse()+serialise()`；Web 侧在**无头 Edge**里加载 `web/index.html` 同级的 `rulepack.js` 与 `core.js` 运行同一批文档 |
| 网络 | `--host-resolver-rules="MAP * ~NOTFOUND"`（禁用 DNS），检查本身也无法联网 |
| 比对范围 | **完整结构化输出**，不是抽查几个数：SKU `state` / `recommended_sku` / `preferred_sku` / `sku_range` / `tie_set` / `candidates_priced`、Current Wave 与 Full Project 的 `counts` / `wave_basis` / `wave_report` / `excluded_specs`、每一条 Function 行与其 Quantity Model 与 `source_validation`、Certification 的主表值/系统值/采用值/用户值/附表值/差值/验证状态/J33 字段、Reuse 账本每一项与 `reuse_summary`、每一个 Review Item、**每一个 null 字段**、每一个底层小数 |
| 数值容差 | `1e-9`（D-01）；字符串、枚举、null 必须**完全相等** |
| 结构 | 递归比较：字典按键集合、数组按长度逐项；Python 侧先 `json.loads(json.dumps(...))` 归一（JSON 键只能是字符串，这是存储形态而非数值差异） |
| 忽略字段 | 仅 `generated_at_utc` 与 `engine_version`（两者本就应当不同：时间戳、以及 Python/Web 内核各自的标识） |

## 3. 结果

```
24/24 match | divergent: none | STATUS: MATCH
```

| 案例 | 覆盖点 | 结果 |
|---|---|---|
| W-01 | 单一 SKU（2 SKU） | MATCH |
| W-02 | 4–5 SKU 并列 → RANGE，两档都计价 | MATCH |
| W-03 | 关键配置缺失（Panel 未填） | MATCH |
| W-04 | 完全未设置 Wave | MATCH |
| W-05 | 明确 LATER_WAVE 被排除出 Current Wave | MATCH |
| W-06 | Current Wave 与 Full Project 相同 | MATCH |
| W-07 | Current Wave 与 Full Project 不同 | MATCH |
| W-08 | 附表一致的 Certification 格 | MATCH |
| W-09 | 6 SKU 下的浮点尾差（`1.6 × 6 = 9.6`） | MATCH |
| W-10 | Certification 范围只由 SKU 范围产生 | MATCH |
| W-11 | 用户临时覆盖一个 MISMATCH 格 | MATCH |
| W-12 | J33 不叠加 | MATCH |
| W-13 | MEPA / HW PA 在 2 SKU 按固定量读取 | MATCH |
| W-14 | Reuse 允许扣减 | MATCH |
| W-15 | Reuse 证据不足未扣减 | MATCH |
| W-16 | 信息不足时无任何计价结果（`single_value=false` 语义） | MATCH |
| W-17 | 超出定义域，停止该情景 | MATCH |
| W-18 | 风险预留只按 baseline 计 | MATCH |
| W-19 | PCBA 额外需求不与台数相加 | MATCH |
| W-20 | 只算 FVT | MATCH |
| W-21 | 显式 UNKNOWN 波次展开多情景 | MATCH |
| W-22 | 「未特别指定」→ `NO_EXPLICIT_ASSIGNMENT`，不是 UNKNOWN | MATCH |
| W-23 | 覆盖 + Reuse + 风险预留同时发生 | MATCH |
| W-24 | 混合 Reuse 状态账本 | MATCH |

## 4. 移植过程中真实发现并修复的 6 处偏差

这些都不是纸面推演——每一项都是比对器报出来后修掉的。**如果只看代码自测，
其中至少 3 项（评分字符串、账本文案、附表 relationship 字段）不会被发现。**

| # | 偏差 | 表现 | 处理 |
|---|---|---|---|
| 1 | 规则包版本字段 | Python 报 `v1.0-draft`（baseline 版本），Web 报 `RP-V3.0`（pack 版本） | Python 侧改为优先读取 `rule_pack_v3.json` 的 `pack_version`，缺失时才回退 |
| 2 | 评分小数格式 | Python `f"{score}"` → `1.0`；JS `String(score)` → `1` | 两侧统一 `toFixed(6)` / `:.6f` |
| 3 | Reuse 账本文案 | `DEDUCTED` 项 `why` 文案不同 | 以 Python 为准，JS 对齐（Python 是行为基准） |
| 4 | `source_validation.relationship` | JS 未输出该字段 → 结构缺字段 | JS 补齐 |
| 5 | `user_override_vs_appendix` | Python 恒输出该键（无覆盖时为 null）；JS 在无覆盖时省略该键 | JS 显式输出 null，避免"字段消失"与"字段为空"被当成同一件事 |
| 6 | J33 findings 键名 | Python `explains_main_table_per_sku_quantity`，JS `explains_main_table_quantity` | 对齐为 Python 的键名 |

## 5. 一致性门禁

`tools/verify_integrity.py §8` 每次都会复检 `python_web_parity.json`：

- `status` 必须为 `MATCH`；
- `tolerance` 必须是 `1e-9`；
- 必须记录 DNS 已禁用；
- 同时校验 8 个 MVP 文件均存在，并检查 `core.js` 里**没有**硬编码业务总量。

**任一不一致都会让完整性门禁失败，属于交付阻塞项**（任务 §26）。

## 6. UI 层是否复制了业务判断？

没有。`web/assets/app.js` 只做输入采集与渲染：SKU 匹配、Certification 计价、Reuse 判定、
波次情景全部来自 `core.js`。可核验的机械证据：

- `app.js` 不调用任何阈值/权重常量，只读 `NRE.analyse()` 的输出；
- 「已验证 / 请确认 / 临时采用 / 用户输入」等状态是从输出的结构化字段
  （`verification_status`、`is_temporary_model`、`value_source`、`base_demand is null`）**映射**而来，
  不重新判断业务语义；
- `store.js` 的 `fmt()` 只做显示格式化，导出的 JSON 直接取 `payload` 原值，
  `policy.display_precision_modifies_values = false` 由 Schema 锁定。
