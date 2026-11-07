# 09 — N. MVP Acceptance Criteria ＋ O. Recommended Implementation Sequence ＋ P. Minimum Prototype Scope

---

# N. MVP Acceptance Criteria

约定：**AC-1 ~ AC-8 必须全部通过**才算 MVP 可交付；标注 `[ORI]` 的条款以 Owner 关闭对应 Review Item 为前提，
未关闭时以"降级行为正确"作为通过标准（降级行为见 §N.2）。

## N.1 功能验收

| # | 验收条款 | 判定方法（可自动化） |
|---|---|---|
| **AC-1** 输入完整性 | 5 个 Key Factor 中任一未读取且未选择时，其状态必须为 `请补充`，且**绝不出现 0/1/不适用默认值** | 断言 `effective is None`（已 PASS） |
| **AC-2** 输入优先级 | `用户最终值 > 文件读取值 > 未确认`；且文件读取值在用户修改后仍完整留痕 | 3 条断言已 PASS |
| **AC-3** SKU 非单一字段 | 任一 Key Factor 单独输入时，结果**不得**是 `SINGLE`（必须 `RANGE` 或 `UNDETERMINED`） | 遍历 5 维单值输入（已 PASS，见扫描表） |
| **AC-4** SKU 输出完整性 | 每次推荐必须同时给出：推荐 SKU（值或范围）/ 逐维匹配判定 / 判断依据 / 相邻候选 / 相邻候选未推荐原因 / 缺失或竞争条件 / 输入来源 | 校验输出对象字段非空 |
| **AC-5** 范围不伪精确 | SKU 为范围时，样机总数必须为**同名范围**（`FVT a–b`、`SIT c–d`、`Total e–f`），禁止输出中点/均值 | 断言 `state=RANGE → recommended_sku is None` |
| **AC-6** 小数不取整（D-01） | 全链路 float；443.8 显示为 `443.8`（非 444）；风险预留 `22.19` 等小数完整保留 | 4 条断言已 PASS |
| **AC-7** 基线可复算 | Agent 输出的 5 档总量必须等于 `365 / 417 / 443.8 / 474 / 507` | 已 PASS |
| **AC-8** 复用语义 | `Potential Reuse` 永不改变总数；`Confirmed Reuse` 必须落到 Function×Phase 且不得超过该行需求 | 已 PASS（越界校验待实现） |
| AC-9 `[ORI-01/04]` 单一推荐 | 完全匹配场景（T-01/02/03/04）输出单一 SKU 且与人工判断一致 | 已 PASS（5 SKU 见 §N.2） |
| AC-10 `[ORI-09]` 自动读取 | 用真实需求表样本读取 5 个 Key Factor，命中率 ≥ 阈值（阈值待样本测定） | **当前不可测**（无样本） |
| AC-11 `[ORI-02]` 认证口径 | Certification 数量符合 Owner 选定口径（主表 / 副表 / source 公式） | 降级：双口径并列展示 |
| AC-12 `[ORI-03]` 波次 | 可分别输出 `Current Wave` 与 `Full Project` 两套 SKU 与需求 | 已实现并通过断言（W-01: 3 vs 4 SKU） |
| AC-13 `[ORI-11]` 差异比较 | 与上传 Build Plan 按 Function×Phase 对比，输出 Δ 与 Δ%，Plan=0 时显示 `N/A` | 需用户数据 |
| AC-14 可追溯 | 结果页"详情"内每条明细可回溯到 **源文件名 + SHA-256 + Sheet + 单元格坐标 + 原文** | 结构已具备（`DemandLine.evidence`） |
| AC-15 证据边界 | UI 明示当前规则版本、未关闭冲突条数；历史参考/产品名不出现在判定依据中 | 检查 `basis` 不含产品名 |
| AC-16 导出 | CSV 含全精度原值 + display 列；JSON 含全量证据与 ORI 引用 | 导出文件字段核对 |
| AC-17 只读保证 | 全流程**不得**向 `original_documents/` 写入任何内容 | 解析器写盘前断言（已实现）+ 结束 SHA 复验 |
| AC-18 范围收敛 | 无团队管理 / 无登录 / 无权限 / 无审批流 / 无管理后台 | 代码走查 |

## N.2 未关闭 ORI 时的**降级行为**（这部分现在就要能验收）

| 未关闭项 | 期望降级行为 |
|---|---|
| ORI-01 Panel 口径 | 按行 79–83 计算，同时在结果页固定显示"Panel 口径待确认（批注口径为 N*panel）" |
| ORI-02 认证口径 | 按主表计算，详情内并列展示副表口径数值与差值 |
| ORI-03 波次 | 输出单一波次 + 提示"波次为人工声明，非系统判定" |
| ORI-04 5 SKU | 输出 `4–5 SKU` **范围**，绝不给单值；总数同步给范围 |
| ORI-09 无样本 | 自动读取入口显示"当前仅支持手工输入（读取规则未经真实样本验证）" |
| ORI-13 越界 | `暂无法计算` + 指出越界维度，不做外推 |

## N.3 非功能验收

| # | 条款 |
|---|---|
| NF-1 | 纯本地运行，**零网络请求**（含字体/CDN）；断网可用 |
| NF-2 | 单次分析 < 1s（21×2=42 行计算 + 5 档查表） |
| NF-3 | 输入 200 行 xlsx 解析 < 3s |
| NF-4 | 分析记录本地持久化，刷新/重开可恢复最近 20 条 |
| NF-5 | 规则版本与源文件 SHA 在 UI 可见 |
| NF-6 | Chrome/Edge 最新版；1366×768 可用 |
| NF-7 | 中英混排显示正常（源表即混排），中文不乱码 |

## N.4 回归测试基线（已建立，可立即执行）

```bat
python tools\validate_rules.py    :: 16 项不变量 + 15 场景 + 3,205 组合扫描
```
当前 **15/16 PASS**，唯一 FAIL 为刻意保留的 ORI-04 探针。Owner 关闭 ORI-04 后该断言应转为 PASS，
在此之前**不得**通过修改断言使其变绿。

> **Phase 2 更新**：Owner Decision 收敛后新增 `tools/validate_rules_v2.py`（69 条探针，
> 68 成立 + `SR-09` 按设计失败，0 回归）。本文件下述 P1~P7 阶段中，**P1 Owner Review 已部分完成**
> （DEC-01…DEC-08 已下达临时口径），**P2 规则定版仍被 14 项 ORI 阻塞**，
> **P3 计算内核已可运行**（`prototype/rules_v2.py`）。当前排期见 `docs/21_next_stage_tasks.md`，
> 三页 UI 的最小字段定稿见 `docs/20_web_mvp_minimal_fields.md`。

---

# O. Recommended Implementation Sequence

阶段划分原则：每阶段都有**独立可验证产出**，且不在 Owner Review 前做不可逆设计承诺。

| 阶段 | 内容 | 前置 | 产出 | 估算 |
|---|---|---|---|---|
| **P0（本任务，已完成）** | 证据盘点、结构解析、冲突发现、模型设计、规则原型 | — | 10 份文档 + `baseline_v1.json` + 原型 + 回归 | ✅ |
| **P1 Owner Review** | 关闭 6 个阻塞项（重点 **ORI-04**、**ORI-01**、**ORI-02**） | P0 | 决策记录；`baseline_v1.0`（去掉 draft） | Owner 侧 |
| **P2 规则固化** | 决策写回 `baseline_v1.0.json`；补 ABSOLUTE_PER_PHASE（ORI-10）；参数化权重（ORI-08） | P1 | 规则库 v1.0 + 回归转全绿 | 0.5 天 |
| **P3 计算内核** | Python 侧完整实现（Function×Phase 复用分摊、越界处理）——波次与单位隔离已有断言 | P2 | CLI：`analyze input.json → out.json/csv` | 1 天 |
| **P4 Web MVP（3 页）** | 首页 / 新建分析 / 结果页 + 手工输入 + 结果展示 + 导出 + IndexedDB | P3 | 可分发的静态小工具 | 1.5 天 |
| **P5 文件自动读取** | xlsx 解析 + 别名/置信度 + 多命中确认 UI | **ORI-09 样本** | 上传→自动填充→确认闭环 | 1 天（含样本标定） |
| **P6 差异比较** | Existing Plan 导入 + 列映射 + Top N 差异 | **ORI-11 Plan 样本** | 差异表 + 导出 | 0.5 天 |
| **P7 校准迭代** | 用 3–5 个真实历史项目回测：Agent vs 实际样机数 | P4–P6 | 偏差报告；基线修订建议 | 视样本 |

**关键路径**：`P1 的 ORI-04 决定 Agent 能否输出单一 SKU`；
`ORI-09 决定 P5 能否开始`；`ORI-11 决定 P6 能否开始`。
P2–P4 **不依赖** ORI-09/11，可先行开工（手工输入闭环即可交付团队试用）。

**建议顺序**：P1 → P2 → P3 → P4（交付试用）→ 并行推进 ORI-09/11 样本收集 → P5 → P6 → P7。

---

# P. Minimum Prototype Scope

## P.1 In Scope（最小闭环）

1. 手工输入 5 个 Key Factor（含"请补充"三态与留痕）；
2. SKU 匹配（MATCH/PARTIAL/MISMATCH/UNKNOWN + 加权 + 状态机）；
3. 基线查表 → 21 Function × 2 Phase 明细 + FVT/SIT/总量；
4. 额外需求（已确认）+ 已确认复用 + 风险预留（默认 0）；
5. 结果页（I.1 的 ①②③⑤ + 折叠明细）+ CSV/JSON 导出；
6. 最近分析记录（IndexedDB）；
7. 规则版本与未关闭冲突展示。

## P.2 Explicitly Out of Scope（MVP 不做）

| 不做 | 原因 |
|---|---|
| 文件自动读取（仅留入口与"暂不可用"提示） | ORI-09 无样本，规则未经校准 |
| Existing Plan 差异比较 | ORI-11 无基准数据 |
| ODM 差异化计算 | ORI-05，ODM 仅记录不生效 |
| 第二波自动判定 | ORI-03，仅手动开关 |
| 规则在线编辑 / 管理后台 | 规则由文件+人工版本化（L 章） |
| 登录 / 权限 / 团队 / 审批 / 通知 | 任务 §七红线 |
| 取整后的"可下单台数" | D-01 明确不取整；如需取整须 Owner 新决策 |
| PCBA 需求计算 | 单位不同（K3 明确未纳入样机 data），仅原文展示 |
| 2–6 SKU 之外外推 | ORI-13 |
| 认证 source 公式引擎 | 等 ORI-02 结论 |

## P.3 已有可运行原型（本阶段产出）

| 文件 | 说明 |
|---|---|
| `prototype/rules_v1.py` | 纯规则内核：`AnalysisInput`/`KeyFactor`/`match_sku()`/`demand_rows()`/`finalise()`，无第三方依赖，**无 UI** |
| `artifacts/model/baseline_v1.json` | 全部业务数值（无手填），含 `conflicts` |
| `tools/validate_rules.py` | 15 场景 + 16 不变量 + 3,205 组合扫描 |

**说明**：该原型用于**验证设计可执行、可测试、可量化**，不是 MVP 实现；
MVP 将按 P4 用 Web 技术重写 UI，但规则内核与本原型保持同一份 `baseline_v1.json` 做黄金对照，避免 Python/JS 双实现口径漂移。
