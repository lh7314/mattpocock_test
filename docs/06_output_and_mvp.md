# 06 — I. Simplified User Output Model ＋ J. Lightweight Web MVP Design

原则：默认结果页**精简**；Rule ID / Rule Version / 公式 / 证据来源 / 详细计算过程留在后台数据或可展开详情中。

---

# I. Simplified User Output Model

## I.1 主页面输出（默认可见，一屏内）

| 区块 | 内容 | 用户可见字段 |
|---|---|---|
| ① SKU 结论 | `Recommended SKU`：`4 SKU` 或 `4–5 SKU` 或 `暂无法建议` | 状态徽章 + 一句话依据 |
| ② 判断依据 | 每个维度 `CPU 3 → 命中 4SKU(2–4)` 式的 5 行迷你表；`MATCH/PARTIAL/MISMATCH/请补充` 用中文 | 已读取 / 用户已修改 / 请确认 / 请补充 |
| ③ 建议样机总数 | **总量**、**FVT 合计**、**SIT 合计**（SKU 为范围时给范围） | 小数，注明"未取整" |
| ④ Function/Phase 明细 | 21 行 ×（Function、Phase、建议数量、主要原因、状态） | 默认折叠到 Category 汇总，点击展开 |
| ⑤ 待确认/待补充 | 缺失维度、冲突项、未勾选 Option、Status 未关闭的 Function | 可复制清单 |
| ⑥ Existing Plan 差异 | 若有上传：Top 10 差异 | Δ、Δ%、备注 |
| ⑦ 导出 | CSV / JSON | — |

## I.2 面向用户的措辞规范

| 内部 | 用户可见 |
|---|---|
| `MATCH / PARTIAL_MATCH / MISMATCH / UNKNOWN` | 命中 / 接近 / 不匹配 / 请补充 |
| `SINGLE_WITH_RESERVATION` | 建议 **4 SKU**（存在待确认项） |
| `UNDETERMINED` | 暂无法计算 |
| `base_demand` | 基础需求 |
| `conditional_increment` | 额外需求 |
| `confirmed_reuse_adj` | 已确认复用 |
| `potential_reuse` | 可复用机会（未扣减） |
| `risk_reserve` | 风险预留 |
| `NOT_COMPUTABLE` | 暂无法计算 |
| Rule ID `BASELINE-CS-ODM-001:F_SWPA:FVT@v1.0-draft` + 单元格 `F21` | **不显示**，置于"详情"抽屉 |

## I.3 输出示例（4 SKU，含 1 项额外需求 + 0.5 已确认复用 + 5% 风险）

```
推荐 SKU：4 SKU
判断依据：GPU 2 → 命中 4SKU(2–3) ｜ CPU 3 → 命中(2–4) ｜ Panel 2 → 命中 ｜ SSD 2 → 命中 ｜ Mem 2 → 命中

建议样机需求（按小数计算，未取整）
  总计 466.5 台      FVT 211.4 台      SIT 232.4 台
  = 基础需求 443.8 + 额外需求 1.0 − 已确认复用 0.5 + 风险预留 22.215
  另有可复用机会 10.0 台（仅提示，未扣减）

明细（默认折叠）   RD 132.8 ｜ PA 240.0 ｜ Certification 41.0 ｜ 3rd Party 28.0 ｜ MFG 2.0

待确认（3）
  · Panel Spec 数量：文件中未读取到，请补充
  · EMC Test 基线：待LCFC update（该 Function 数量可能变化）
  · RF Certification 存在两套口径（主表恒定 15 vs 副表 8–10），本次采用主表，请 Owner 确认
```

---

# J. Lightweight Web MVP Design

## J.1 明确不建设（任务 §七）

团队管理 ✗ ｜ 用户目录 ✗ ｜ 组织映射 ✗ ｜ 内置 RBAC ✗ ｜ 复杂权限 ✗ ｜ 管理后台 ✗ ｜ 复杂审批流 ✗ ｜ 企业级多系统集成 ✗

也不做：SSO、多租户、通知、评论协作、规则在线编辑器（规则只由文件+人工维护版本）。

## J.2 三个页面

### 页面 1 — 首页 `/`
- `上传需求表`（拖拽 .xlsx/.csv）
- `新建分析`（跳过上传，直接手工输入）
- `最近分析记录`（本地列表：项目名、Key Factor 摘要、推荐 SKU、总数、时间）
- 页脚固定：`基线版本 BASELINE-CS-ODM-001 v1.0-draft ｜ 状态：待 Owner 确认 ｜ 共 14 项待确认规则`

### 页面 2 — 新建分析 `/analysis/new`
```
① 上传区        文件读取结果摘要（成功/失败/部分识别）
② Key Factor    5 行：CPU / GPU / Panel / SSD / Memory
                每行：读取值(灰) | 数字框 | 状态徽章(已读取/用户已修改/请补充/请确认)
                底部：ODM 下拉(LCFC/HQ/Compal/未指定) —— 标注"当前仅记录，不参与计算"
③ 高级(折叠)    额外需求(Option 勾选) ｜ 已确认复用 ｜ 可复用机会 ｜ 波次(Current/Full Project)
④ [运行分析]
```
校验：5 个 Key Factor 全空 → 按钮禁用并提示"请至少补充 1 项"；有缺失但非全空 → 允许运行，结果降级为范围/带保留。

### 页面 3 — 分析结果 `/analysis/{id}`
即 I.1 的七个区块。
- 默认视图 = ①②③⑤ + 折叠的④；⑥ 仅在上传过 Plan 时出现。
- `详情` 抽屉（默认关闭）：逐行 Rule ID / Rule Version / 公式 / 源文件单元格 / SHA-256 / 原始文本。
- `导出`：CSV（明细）、JSON（含全量证据与 ORI 引用）。

## J.3 技术形态（小工具，非平台）

| 项 | 选择 | 理由 |
|---|---|---|
| 前端 | 单页静态站点（Vite + 原生或轻量框架），可 `file://` 或内网静态托管 | 无后端也能跑，分发 = 发文件夹 |
| 计算 | **浏览器内**执行（规则 JSON + JS），或本地 `python -m http.server` | 数据不出机器；符合"默认禁用互联网" |
| 解析 | SheetJS(xlsx) 浏览器解析；解析逻辑与已验证 Python 逻辑一一对应 | 双实现可用同一 `baseline_v1.json` 做黄金对照 |
| 存储 | 浏览器 `IndexedDB`（最近分析、输入留痕）；导出即归档 | 不需要数据库服务 |
| 规则版本 | 随应用打包 `baseline_v*.json`，文件名带版本与源 SHA | 可追溯，杜绝"口径悄悄变了" |
| 部署 | 内网共享一个静态 URL，或每人本地打开 | 无需账号体系 |

## J.4 数据流

```
上传 xlsx ─┐
           ├─► KeyFactor[5]（file_value / user_value / edited）
手工输入 ──┘        │
                    ▼
            SKU Definition 匹配（v1） ──► state / recommended / range / basis / neighbors
                    │                                   │
                    ▼                                   ▼
            baseline_v1.json 查表 ──► demand_rows(21×2) ──► 汇总 + FVT/SIT
                    │
                    ├─ + 额外需求(已确认) − 已确认复用 × (1+risk%)
                    ▼
              Recommended（小数，未取整） ──► 页面 / 导出 / 差异比较
```

## J.5 状态与空态

| 场景 | 表现 |
|---|---|
| 上传解析失败 | 明确错误 + "改用手工输入"入口，不产生幽灵"已读取" |
| 某 Key Factor 未读到 | 该行 `请补充`（黄），结果区顶部横幅提示结果可能为范围 |
| SKU 结果为范围 | 总数并列显示区间两个端点值，**不显示平均值** |
| 规则冲突未关闭（ORI-01/02） | 结果区固定横幅"当前使用主表口径，存在 1 项待确认冲突"，链接到详情 |
| 输入超出定义域 | `暂无法计算` + 列出越界维度 |
