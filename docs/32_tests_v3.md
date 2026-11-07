# 32 — 自动化测试清单（交付物 Q）
> **状态（DEC-10 之后）**：本文描述的是 Phase 3a 的 Certification 口径
> （采用主表派生值）。Owner 已决定在 MVP 与团队试用阶段**采用附表总量**，
> 最新口径见 `docs/36_certification_adoption_v4.md`、`docs/37_owner_decision_log_v4.md`、
> `docs/39_totals_v4_and_6sku_review.md`、`docs/40_web_mvp_v4_changes.md`。
> 本文按原文保留，作为阶段记录。


## 1. 当前门禁

一条命令跑完整流水线：

```
python tools\run_all.py                  # 13 步，最后一句是总结论
python tools\run_all.py --history        # 附带跑 Phase 1/2 历史套件，标 HIST，不计结论
```

拆开跑：

```
python tools\validate_rules_v3.py        # 100 探针：99 PASS + SR-09 EXPECTED FAIL
python tools\check_python_web_parity.py  # 24 例 Python↔Web 逐字段一致
python tools\check_web_ui.py             # 37 项端到端 UI 探针（真实驱动三页）
python tools\lint_sources.py             # 语法/编码/文档交叉引用检查
python tools\worktree_report.py          # 文件分类与 worktree 结论（交付物 W）
python tools\verify_integrity.py         # 完整性门禁 80 项，复检以上全部报告
```

历史保留、**不作为门禁**，各自变红的原因都是确定的：

| 套件 | 状态 | 精确原因 |
|---|---|---|
| `validate_rules.py`（P1） | 15/16，退出码 1 | 唯一失败项是 ORI-04 探针（`SR-09` 前身），**按设计 FAIL** |
| `validate_rules_v2.py`（P2） | `SC-01`、`SC-02` REGRESSION | ① `SR-09` 按设计 FAIL；② **Schema 已升到 3.0**，该套件内嵌夹具仍写 `"schema_version": "2.0"`，两个 Schema 契约探针因此不再成立 —— 这是契约演进的必然结果，不是内核回归 |

两份历史报告 `regression_report_v{1,2}.md` 保留为阶段证据，不删改。

## 2. 结果

| 指标 | 值 |
|---|---|
| 探针总数 | **100** |
| PASS | **99** |
| FAIL | **1** = `SR-09`（ORI-04，**按设计**） |
| Expected Failure | **`['SR-09']`**（严格等于，由 `EF-01` 守护） |
| Regressions | **0** |
| STATUS | **CLEAN** |
| Python↔Web | 24/24 MATCH |
| Web UI | 37/37 CLEAN |
| 完整性 | PASS，UNEXPECTED 文件 0 |

## 3. 本任务新增的强制守护（任务 §24）

| ID | 断言 | 为什么重要 |
|---|---|---|
| **CT-V2-01** | 每个附表 Certification Cell = 主表单 SKU 数量 × SKU 数，**逐格** | 明令禁止只验证合计 |
| **CT-V2-02** | 附表只用于验证，不重复计入总量 | 项目总量里 Certification 只有一份 |
| **CT-V2-03** | 单一 SKU 时 Certification 输出单值 | 取消"永远区间"的旧行为 |
| **CT-V2-04** | 4–5 SKU 时，范围分别来自 4 SKU 与 5 SKU 的真实计算 | 范围必须可追溯 |
| **CT-V2-05** | 范围原因是 `SKU_NOT_ESTABLISHED`，不是竞争模型 | 禁止旧范围归因回潮 |
| **CT-V2-06** | FVT 与 SIT 各用各自源费率 | 两 Phase 数字不同是事实 |
| **CT-V2-07** | 引擎中不存在任何全局 Phase 比例 | Schema `phase_ratio_used: null` 双保险 |
| **CT-V2-08** | J33 不在主表结果上再次叠加 | 防重复计入（风险 HIGH） |
| **CT-V2-09** | 验证一致时不生成 `COMPETING_CERTIFICATION_MODELS` | 旧标签只存在于"禁止"元组与文档 |
| **CT-V2-10** | Certification 在项目总量中只计入一次 | `total = cert + non-cert` 每档成立 |
| **CT-V2-11** | 任一附表 Cell 不一致 → `SOURCE_VALIDATION_MISMATCH`，原值保留 | 不改源数据；差异进 Register |
| **CT-V2-12** | 显示精度不改变底层 Certification 结果 | `9.6` 不是把 `9.599999…` 四舍五入来的 |

## 4. 本任务新增的其他守护

| ID | 断言 |
|---|---|
| `RT-02` | 修正后每档输出**单一**总量（373.0 / 417.0 / 443.8 / 474.0 / 506.6） |
| `QM-07` | MEPA / HW PA 标记 `is_temporary_model`，前端显示「临时采用」 |
| `QM-09` | `DERIVED_TOTAL_VALIDATION` 是证据角色，**不是** Quantity Model |
| `JG-01..05` | J33 = 说明性证据、只适用于 RF Certification 与其自述的 2+2 组合、只产生 ADVISORY 条目 |
| `LG-01..04` | Phase 2 竞争模型行为无法从 live 代码/模型中回来；四条附表禁令写在 policy 里 |
| `WV-12` | 界面「未特别指定」→ `NO_EXPLICIT_ASSIGNMENT`，**不**当 UNKNOWN 展开 |
| `WV-13` | 被排除的 Spec 有名字，页面能解释差异 |
| `OR-01..05` | Review Item 不阻断分析；`BLOCKS_FORMALIZATION` 不阻塞 MVP；`BLOCKS_EXECUTION` 只停受影响情景并解释；重复问题折叠 |
| `D01-08` | `65.49999999999999` 不会被写回成 `65.5` |
| `D01-09` | 导出声明"显示精度不修改数值"且"不把区间折叠成单值" |
| `PR-05b` | 每个导出的 Certification 格同时保留系统值 / 用户值 / 采用来源 |
| `SC-05` | `appendix_counted_in_project_total_times = 1` 被 Schema 直接拒绝 |
| `SC-09` | `single_value = true` 而总量为 null 被拒绝 |
| `SC-10` | 附表被改标成 Quantity Model 被拒绝 |
| `EF-01` | Expected Failure 集合恒等于批准值 `['SR-09']`；`SR-09` 意外转绿也是 REGRESSION |

## 5. Phase 2 探针的处置

- **原样继续执行**：`RT-01`、`QM-01..06/08`、`PL-01..04`、`SR-01..SR-10`、
  `WV-01..11`、`RS-01..08`、`D01-01..07`、`PR-01..04`、`SC-01..04/06/07`。
- **退役并被接替**：`CT-01 CT-02 CT-03 CT-04 CT-07 CT-08`（映射见 `docs/25_owner_decision_log_v3.md §3`）。
  `verify_integrity.py §6` 反向确认这四个 ID 确实已不在当前套件中——
  既没有被偷偷留下"碰巧变绿"，也没有无声消失。
- **保留并加强**：`CT-05`（手工覆盖）→ `CT-V2-11` + `SC-08` + `PR-05b`；
  `CT-06`（非全局比例）→ `CT-V2-06/07`。

## 6. Web 端到端探针（37 项，映射任务 §25）

驱动方式：`tools/check_web_ui.py` → 无头 Edge（禁用 DNS）加载 `web/ui_test.html`，
后者在 **iframe 里加载真实的三页**，像用户一样填值、点「运行分析」、等页面跳转、
再读用户实际看到的内容。断言的是页面文本，不是内部数据结构。

| §25 要求 | 探针 |
|---|---|
| 1 单一 SKU 结果 | `UI-01` |
| 2 4–5 SKU 范围 | `UI-02` ×3（页面文案 + 不预选 + 实时预览） |
| 3 Key Factor 缺失 | `W-03`（parity）+ 页面 `请补充` 提示 |
| 4 未设置任何 Wave | `W-04`（parity） |
| 5 存在明确 LATER_WAVE | `UI-07` |
| 6 Current = Full | `UI-06` ×2 |
| 7 Current ≠ Full | `UI-07`、`UI-15` |
| 8 主附表验证通过 | `UI-08` |
| 9 附表不重复计入 | `UI-09` |
| 10 范围只由 SKU 产生 | `UI-10` |
| 11 Certification 用户临时覆盖 | `W-11`/`W-23`（parity） |
| 12 J33 不重复叠加 | `UI-12`、`UI-12b`、`UI-12c` |
| 13 MEPA / HW PA 固定量 | `UI-13` |
| 14/15 Reuse 扣减 / 未扣减 | `W-14`/`W-15`/`W-24`（parity） |
| 16 `single_value=false` 时单值字段为 null | `UI-16` ×2 + `SC-09` |
| 17 显示精度不改底层值 | `UI-17` ×3 |
| 18 历史保存 | `UI-18` ×3（含点按钮后落盘） |
| 19 历史打开 | `UI-19` ×2 |
| 20 历史复制 | `UI-20` |
| 21 Register 收集新问题 | `UI-21` ×2 |
| 22 Review Item 不阻断 | `UI-22` ×2 |
| 23 `BLOCKS_FORMALIZATION` 不阻塞 MVP | `UI-23` |
| 24 `BLOCKS_EXECUTION` 停止并解释 | `UI-24` ×2 |

`UI-21` 曾经因为断言本身写错（把字符串和布尔值混在一起比较）而误判，已改为读取
`#r-open-count` 的实际数值 —— **修的是探针，不是被测代码**。同理 `UI-06` 原先写成
恒真表达式，已换成对页面文案的真实断言。

## 7. 构建期/移植期的真实缺陷（全部已修，留此备查）

| 缺陷 | 发现方式 | 影响 |
|---|---|---|
| `new.html` 缺 `#add-reuse` / `#add-extra` 两个按钮 → `bindNew()` 提前抛异常，「运行分析」没绑上 | `UI-18` 报 `nav=false` | 点按钮无反应（严重） |
| `store.js` 一处对象字面量收尾多了一个分号 → 整个文件语法错误 | 专用加载探针抓到 `SyntaxError @ store.js:132` | 所有页面脚本失效（致命） |
| 无头浏览器 profile 落在含非 ASCII 的用户目录 → Edge 静默不输出 | 逐变量排查启动参数 | 检查器无法运行（工具侧） |
| `--host-resolver-rules` 含空格被 Start-Process 拆成 3 个参数 | 同上 | 同上（工具侧） |

## 8. Expected Failure 政策

`SR-09` 是**唯一**被批准的 Expected Failure，代表 ORI-04（5 SKU 结构上不可达）。

- 它**永远不会**被删除、软化、改标签或调权重转绿；
- 它**意外转绿同样算 REGRESSION**（`EF-01` + `verify_integrity` 双向检查
  `expected_failures == ['SR-09']` 且 `SR-09 in probes_failing`）；
- 只有 Owner 提供真实 4 SKU / 5 SKU 样本并给出正式分界条件后，才允许按新口径重写；
- 本任务未新增任何未经批准的 Expected Failure。
