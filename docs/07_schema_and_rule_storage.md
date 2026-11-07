# 07 — K. Proposed Data Schema ＋ L. Rule and Evidence Storage Proposal

设计约束：MVP 是**单文件本地小工具**。Schema 要能表达"证据 + 状态 + 版本 + 冲突"，
但不能长成数据平台。落地形态：**打包 JSON（规则/基线）+ 浏览器 IndexedDB（分析记录）**，
SQLite 仅作为可选导出格式（便于团队用 Excel/BI 复核）。

机器可读定义（可直接使用）：

| 文件 | 内容 |
|---|---|
| `schema/input.schema.json` | 分析输入（Key Factor 值对象 + 额外需求 + 复用） |
| `schema/output.schema.json` | 分析结果（SKU 结论 + 需求明细 + 待确认项） |
| `schema/rule.schema.json` | 规则/基线条目（含证据、状态、冲突引用） |
| `schema/ddl_sqlite.sql` | 可选 SQLite 落地（复核/归档用） |
| `artifacts/model/baseline_v1.json` | **已生成**的基线实例（21 Function × 2 Phase × 5 SKU + SKU Definition + 冲突清单） |

---

# K. Proposed Data Schema

## K.1 实体总览

```
Evidence（源文件/单元格级证据）──┐
                                 ├─◄── Rule（费率规则 / SKU 定义规则 / 候选规则）
RuleVersion（基线版本） ─────────┘            │ 冲突引用
                                              ▼
Analysis ──► AnalysisInput（KeyFactor ×5 + 额外 + 复用）        OwnerReviewItem
   │                                             ▲
   ├──► SkuRecommendation（state/recommended/range/candidates）│ 被引用
   ├──► DemandLine（21 Function × 2 Phase）◄── 规则引用 + 证据引用
   ├──► ReuseItem（confirmed / potential）
   ├──► OptionalRequirementDecision（Option 勾选结果）
   └──► PlanComparison（Existing Plan 差异）
```

## K.2 关键表/对象（字段级）

### Evidence（不可变）
| 字段 | 类型 | 说明 |
|---|---|---|
| `evidence_id` | text | `EV-<sha8>-<sheet>-<ref>` |
| `file_sha256` | text | 源文件哈希（当前 `48A360FF…`） |
| `file_path` | text | 相对路径，**只读引用** |
| `sheet` / `cell_ref` | text | `CS ODM sample ` / `F21` |
| `raw_value` | text | 原始文本（含中文、错别字，原样保存） |
| `formula` | text? | 若为公式单元格 |
| `cached_value` | real? | Excel 缓存值（保留 `65.49999999999999` 原样） |
| `kind` | enum | `CELL` / `MERGED_RANGE` / `COMMENT` / `DOC_PROPERTY` |
| `author` / `authored_at` | text? | 批注用（如 Lingyu LY3 Rong / 2026-06-24） |

### Rule
| 字段 | 类型 | 说明 |
|---|---|---|
| `rule_id` | text | `BASELINE-CS-ODM-001:F_SWPA:FVT` |
| `rule_version` | text | `v1.0-draft` |
| `rule_type` | enum | `RATE_PER_SKU` / `ABSOLUTE_PER_PHASE` / `SKU_DEFINITION` / `OPTION_CANDIDATE` / `ODM_CANDIDATE` |
| `payload` | json | `{"per_sku_rate": {SKU2..SKU6}, "phase": "FVT"}` 或 SKU 区间 |
| `unit` | enum | `UNIT` / `PCBA`（**严禁混合相加**，H.7） |
| `status` | enum | `CONFIRMED` / `DRAFT` / `CONFLICTED` / `DISABLED` / `NON_NORMATIVE` |
| `evidence_refs[]` | text[] | 指向 Evidence |
| `conflict_refs[]` | text[] | 指向 OwnerReviewItem（如 `ORI-02`） |
| `applies_to` | json | `{odm:[], phase:[], sku:[], series_note:"Pro/LOQ /Y5"}`；`series_note` **不参与判定** |

### KeyFactorValue
`{name, file_value, file_confidence, user_value, user_edited, effective, source, status_user}` — 见 §D.2。
**三值并存**是硬性要求：文件读取值、用户最终值、本次采用值。

### DemandLine
`{analysis_id, function_id, category, phase, per_sku_rate, sku_qty, base_demand, conditional_increment, confirmed_reuse_adj, risk_reserve, recommended, unit, status, rule_id, rule_version, evidence_ref, note}`
`recommended` 为 **REAL，不取整**；导出时另附 `display` 字符串列。

### SkuRecommendation
`{analysis_id, state, recommended_sku, range_low, range_high, wave_scope, top_score, candidates_json, runner_up_json, missing_dims_json, unresolved_conflicts_json}`
`state ∈ SINGLE | SINGLE_WITH_RESERVATION | RANGE | UNDETERMINED`。
**范围态时 `recommended_sku` 必须为 NULL**（防止下游误用单值）。

### OwnerReviewItem
`{ori_id, title, type, finding, evidence_refs[], impact, options[], default_applied, blocking, owner_decision, decided_at}`
MVP 只做**只读展示 + 导出**，不做审批工作流；`owner_decision` 由人工回填到规则版本中。

## K.3 版本与不可变性

- `RuleVersion`：`v1.0-draft` →（Owner Review 后）`v1.0` → 修订 `v1.1`。
- 每次分析快照 `rule_version` + `file_sha256`；**历史记录永不因规则升级而重算**（重算必须显式"重新分析"并留新版本）。
- 基线 JSON 与前端一起打包，文件名含版本与源 SHA：`baseline_v1.0-draft__sha48A360FF.json`。

---

# L. Rule and Evidence Storage Proposal

## L.1 三层存储

| 层 | 载体 | 内容 | 可变性 |
|---|---|---|---|
| L1 原始证据 | `original_documents/`（**只读**）+ `artifacts/extraction/` | 源文件、逐格 dump、批注原文 | 源文件不可变；extraction 可重跑复现 |
| L2 规则库 | `artifacts/model/baseline_v*.json` → 打包进前端 `public/rules/` | 费率、SKU 定义、候选规则、冲突引用 | 版本化，改版本=新文件 |
| L3 分析记录 | 浏览器 IndexedDB（+ 可选导出 SQLite） | 每次分析的输入/输出/快照 | 追加式 |

## L.2 为什么不用数据库服务

- 团队规模 = 共享小工具，非并发系统；IndexedDB + 导出文件足够。
- 避免任何"平台化"入口（用户/权限/审批）。
- 规则真相源仍是 **Owner 的文件 + Review 结论**，数据库只会造成第二真相源。

## L.3 规则状态机（治理核心）

```
        ┌──────────────┐  Owner 确认    ┌───────────┐
        │ DRAFT        │───────────────►│ CONFIRMED │
        │ (当前 v1.0)  │                └───────────┘
        └──────┬───────┘                      ▲
   发现冲突     │                              │ 关闭 ORI
        ┌──────▼───────┐  Owner 择一口径       │
        │ CONFLICTED   │──────────────────────┘
        │ ORI-01/02/03 │─── 未关闭 ──► 结果降级为 RANGE / 请确认
        └──────────────┘
        ┌──────────────┐
        │ NON_NORMATIVE│  case by case / Option / suggest / maybe → 永久非规则，仅展示
        └──────────────┘
        ┌──────────────┐
        │ DISABLED     │  ODM 候选规则（E.6）等，保留但不生效
        └──────────────┘
```

**默认状态映射（从当前文件推导，无人工干预）**

| 规则来源 | 初始状态 | 依据 |
|---|---|---|
| 行 3–44 费率矩阵（18/21 Function） | `DRAFT` | 可复算但未经 Owner 确认 |
| 行 13 `EMC Test` | `CONFLICTED` | Status `待LCFC update` |
| 行 23 `MEPA` | `CONFLICTED` | Status `HQ/Compal:to be clarify` + 与 B3 差 +4 |
| 行 25 `HW PA` | `CONFLICTED` | Status `HQ gap比较大` + 与 B3 差 −0.2 |
| 行 27–34 Certification | `CONFLICTED` | 与行 51–62 冲突（ORI-02） |
| 行 51–62 Certification 副表 | `CONFLICTED` | 同上（未选用，保留双口径） |
| 行 79–83 SKU Definition | `CONFLICTED` | 与 D2:H2 批注冲突（ORI-01） |
| D2:H2 批注 | `CONFLICTED` | 同上 |
| J 列 `Option:` 12 项 | `NON_NORMATIVE` | K3 `还没加到样机data里面` |
| `case by case` / `suggest` / `maybe` | `NON_NORMATIVE` | 任务红线 |
| G10/G12、PPA standard 1.0 | `HISTORICAL_REFERENCE` | 文件未随附（ORI-11） |
| E.6 三条 ODM 可结构化项 | `DISABLED` | 未经确认（ORI-05） |
| 产品名称 → SKU 映射 | `NOT_A_RULE` | 任务红线 + 行 88 |

## L.4 冲突登记表（已自动生成 16 条 → `baseline_v1.json.conflicts`）

| # | 类型 | 位置 | 摘要 | 严重度 | ORI |
|---|---|---|---|---|---|
| 1 | 数值 | Green SIT @SKU3 | 主表 9 vs 副表 6 | MAJOR | ORI-02 |
| 2–6 | 数值 | RF Cert SIT @SKU2–6 | 主表恒 15 vs 副表 8/9/10/10/10 | MAJOR×5 | ORI-02 |
| 7 | 数值 | Safety FVT @SKU6 | 9.6 vs 10 | MINOR(精度) | ORI-02 |
| 8 | 数值 | MEPA FVT/SIT @SKU2 | 32 vs 36 | MAJOR | ORI-10 |
| 9 | 数值 | HW PA @SKU6 | 4.2 vs 4 | MINOR(精度) | ORI-10 |
| 10–13 | 定义 | SKU3/4/5/6 Panel | 定义 1/2/2/2-3 vs 批注 3/4/5/6 | MAJOR | ORI-01 |
| 14 | 定义 | SKU6 CPU | 定义 4-5 vs 批注 3 | MAJOR | ORI-01 |
| 15–17 | 状态 | EMC Test / MEPA / HW PA | Status 未关闭 | OPEN | ORI-05 |

## L.5 可复现性要求（验收项）

任何人执行：

```bat
python tools\extract_workbook.py
python tools\build_baseline_dataset.py
```

必须得到与仓库内 `baseline_v1.json` **逐字节一致**的数值部分（时间戳字段除外）。
这是"规则库不是手抄的"的唯一客观证明。
