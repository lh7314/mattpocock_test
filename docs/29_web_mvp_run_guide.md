# 29 — Web MVP 运行说明（交付物 M、N）
> **状态（DEC-10 之后）**：本文描述的是 Phase 3a 的 Certification 口径
> （采用主表派生值）。Owner 已决定在 MVP 与团队试用阶段**采用附表总量**，
> 最新口径见 `docs/36_certification_adoption_v4.md`、`docs/37_owner_decision_log_v4.md`、
> `docs/39_totals_v4_and_6sku_review.md`、`docs/40_web_mvp_v4_changes.md`。
> 本文按原文保留，作为阶段记录。


## 1. 运行方式（零依赖、零构建、零服务器）

```
双击  D:\GAMING_NRE_AGENT\web\index.html
```

或用本地静态服务器（可选，仅为便于分享）：

```
cd D:\GAMING_NRE_AGENT\web
python -m http.server 8765
浏览器打开 http://127.0.0.1:8765/index.html
```

支持 Edge / Chrome（Chromium 系）。**不需要** Node、npm、Python 运行时、数据库、网络。
`file://` 下即可完整工作：业务数值通过 `assets/rulepack.js`（`window.RULEPACK`）注入，
因为浏览器在 `file://` 下会拦截 `fetch()` 本地 JSON。

## 2. 三个页面

| 页面 | 文件 | 作用 |
|---|---|---|
| 首页 | `index.html` | 工具名称与一句话用途；新建分析；最近分析列表（Project Name / 分析时间 / SKU 结果或范围 / 需求值或范围 / 状态 / 打开·复制·删除） |
| 新建分析 | `new.html` | 基本信息 + 五个 Key Factor + 逐 Spec 波次 + 三个折叠高级选项 + 当前判断（实时预览） |
| 分析结果 | `result.html?id=…` | SKU 结果或范围、Current Wave、Full Project、需求值或范围、FVT/SIT 拆分、Function 明细、Certification 验证、待确认问题、导出 |

## 3. 文件构成

```
web/
  index.html  new.html  result.html
  assets/
    rulepack.js          生成的业务数值（唯一来源，勿手改）
    core.js              rules_v3.py 的等价移植（不含任何业务数字）
    store.js             localStorage 历史 + JSON/CSV 导出 + 显示格式化
    app.js               三个页面的渲染逻辑（不含业务判断）
    app.css              样式
  parity.html            人工可跑的 Python/Web 对照页
  ui_test.html           端到端 UI 探针（被 tools/check_web_ui.py 驱动）
  assets/parity_runner.js 对照页运行器
```

## 4. 数据来源与不可漂移性

- 前端**不含**任何业务数字。所有 42 个 Quantity Model 单元格、SKU Definition、
  Certification 逐格验证结果、J33 结论、权重、容差，全部来自 `assets/rulepack.js`，
  而该文件由 `tools/build_rule_pack_v3.py` 从已验证产物生成。
- 计算逻辑是 `prototype/rules_v3.py` 的移植，由 `tools/check_python_web_parity.py`
  在**禁用 DNS** 的无头浏览器里逐字段比对（当前 **24/24 完全一致**）。
- 任何不一致都会让完整性门禁失败，属于交付阻塞项。

## 5. 本地存储

`localStorage` 键 `gaming-nre.sample-analyses.v1`。每条记录保存 **完整输入快照 + 完整引擎输出**：

- 打开历史记录 = 查看**当时**的结果，不会用新规则包重算；
- 复制 = 带着原输入跳到新建页，另存为新记录，原记录不变；
- 删除 = 只删本机记录。

存储不可用时页面会显示提示，分析仍可运行、仍可导出。清空浏览器站点数据会清空历史。
**没有**服务器端用户、团队、权限、审批、Rule Registry 编辑或自学习页面（任务 §10 明确排除）。

## 6. 导出

- **JSON**：完整底层精度 + 输入快照 + 系统值/用户值/采用来源 + Certification 逐格验证 +
  J33 状态 + Reuse 账本 + Review Items + 被排除的 Panel 批注 + 引擎/规则包/Schema 版本 + 生成时间。
  区间在导出中**仍然是区间**。
- **CSV（Excel 可直接打开，带 BOM）**：7 个区块的团队 Review 摘要。
  详见 `docs/33_export_contract_v3.md`。

显示层可统一 1 位小数（例如 443.8、9.6），但**导出与存储保留原值**（例如 65.49999999999999）。

## 7. 自测

```
python tools\check_python_web_parity.py   # Python vs Web 逐字段一致性（24 例）
python tools\check_web_ui.py              # 端到端 UI 探针（37 项，真实驱动三个页面）
python tools\verify_integrity.py          # 完整性门禁（含上面两份报告的复检）
```

两者都以无头 Edge 运行，均带 `--host-resolver-rules="MAP * ~NOTFOUND"`（禁用 DNS），
因此这些检查本身也无法访问互联网。

## 8. 若要在别的机器上跑

把整个 `web/` 目录拷过去即可（`rulepack.js` 已内嵌全部数值）。
要重跑 Python 侧校验则需要 Python 3.11+ 与一台 Chromium 系浏览器；
`verify_integrity.py` 还依赖 `jsonschema`（`pip install jsonschema`），缺失时相关探针会明确跳过而不是假装通过。
