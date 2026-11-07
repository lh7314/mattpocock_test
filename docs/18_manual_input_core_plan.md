# 18 — H. 手工输入 MVP 计算内核实施方案

> 状态：内核已可运行（`prototype/rules_v2.py`），70 条探针 69 通过、1 条按设计失败。
> 本文描述**把它变成 MVP 内核**的具体方案：模块边界、契约、执行顺序、错误处理、不做的事。

---

## 0. 已完成 vs 待做

| 项 | 状态 |
|---|---|
| 输入契约 + `from_document()` | ✅ 已实现并被 `SC-06/07` 守护 |
| Wave 场景生成 | ✅ |
| SKU 匹配与状态机 | ✅（ORI-04 缺口按设计保留） |
| Quantity Model 直读 | ✅ |
| Certification 多模型计价 + 手工覆盖 | ✅ |
| Reuse 账本 | ✅ |
| Risk Reserve | ✅（比例默认 0，等 ORI-07） |
| 序列化到 output schema | ✅（`serialise()`，`SC-01` 守护） |
| 浏览器内运行封装（打包 rule pack、IndexedDB、CSV/JSON 导出） | ❌ 下一步 |
| 三页 UI | ❌ 下一步 |
| 自动读取需求表 | ❌ 等 ORI-09 |
| Build Plan 差异比较 | ❌ 等 ORI-11 |

---

## 1. 模块边界

```
Web MVP（浏览器，无后端）
├── ui/home              最近分析列表、新建
├── ui/new-analysis      表单 → 构造 input document
├── ui/result            渲染 output payload
├── contract
│   ├── input.schema.json      ← 前端提交前校验（唯一入口校验）
│   └── output.schema.json     ← 渲染前校验（防止内核/前端漂移）
├── core/rules_v2.js           ← rules_v2.py 的 1:1 移植（下方 §3 移植清单）
└── data/rule_pack_v2.json     ← baseline_v1 + quantity_model_v2 打包，只读，带版本与来源 SHA
```

**单一事实来源**：`rule_pack_v2.json` 由 `tools/build_baseline_dataset.py` +
`tools/derive_quantity_model.py` 生成，前端**不携带任何业务数字**。
打包时写入 `source.sha256`，结果页显示规则版本与来源指纹。

---

## 2. 执行顺序（固定，不得重排）

```
1  校验 input document（input.schema.json）
     ↳ 失败：定位到具体字段路径并阻止提交，不做"善意纠正"
2  AnalysisInput.from_document()
     ↳ 保留 file_value / user_value / user_edited 三件套，永不合并
3  normalise_specs()           Wave 正规化（未标注 → NOT_PROVIDED，不推断）
4  wave_scenarios()            FULL_PROJECT + CURRENT_WAVE（含 UNKNOWN 扇出，上限 32）
5  对每个 scenario：
     5.1 match_sku(counts)     维度判定 → 状态机
     5.2 candidates_to_price   RANGE → 平局集合全体计价
     5.3 对每个候选 SKU：finalise()
           a. demand_rows()    逐 cell 读 Quantity Model（绝对量直读）
           b. certification_override 应用（如有）
           c. totals_by_model() 每套证据源各算一遍完整总量 + band
           d. summarise()      FVT / SIT / category / function
           e. reuse_ledger()   四态判定，仅 proven ADDITIONAL_CONFIRMED_REUSE 扣减
           f. risk_reserve     (TOTAL + reuse) × percent
           g. recommended_total / band
6  Owner Review Items 汇总去重（按 kind + 主题，折叠 scenario_ids）
7  serialise() → output.schema.json 校验 → 渲染 / 导出
```

任何一步产生 `UNRESOLVED` / `RANGE` / `UNKNOWN` 都**继续往下算**，
用范围和 Review Item 表达，不中断、不猜测。

---

## 3. Python → JS 移植清单（必须逐条对齐）

| Python | JS | 风险点与对策 |
|---|---|---|
| `float` 四则 | `number` | **JS 无十进制精确性**。`443.8 * 0.05` 在 JS 里是 `22.189999999999998`。对策：全链路保持 float，导出与比较统一用 `1e-9` 容差；显示用 `toFixed`；**不做**"四舍五入到 1 位"式的业务修正（D-01）。回归里断言 `abs(x-443.8)<1e-9` 而不是 `x===443.8` |
| `dict` 键序 | `Map` 或普通对象 | `scores` 等映射在 JSON 里键会变字符串。导出时显式排序，保证 diff 稳定 |
| `dataclass` | 工厂函数 + `Object.freeze` | 冻结避免 UI 误改内核返回值 |
| `json.dumps(sort_keys=True)` 去重键 | 手写稳定序列化 | 场景去重、ORI 去重都依赖它，必须稳定 |
| `round(x, 9)` | `Math.round(x*1e9)/1e9` | 只用于证据里的 delta 展示，不用于业务值 |

移植完成后，用 `artifacts/validation/worked_examples_v2.json` 里的 **11 个用例**
作为跨语言黄金对照：JS 与 Python 的每个数字必须在 `1e-9` 内一致。

> 这条对照测试是 P4 的验收门槛之一（见 `docs/09` 的 AC 系列）。

---

## 4. 内核绝不做的事

| 禁止 | 守护方式 |
|---|---|
| 询问或接受 SKU 数量输入 | 输入 Schema 无该字段 |
| 把缺失值默认成 0 / 1 / N-A | `SC-03`；`file_value` 为 `number\|null` |
| 用权重打破 4/5 SKU 平局 | `SR-10` 冻结权重 + `SR-09` 保持失败 |
| 由第二颗 SSD/Mem Spec 推断第二波 | `WV-05` |
| 自动选择或平均 Certification 模型 | `CT-02` `CT-03`；Schema `if/then` 禁单值 |
| 用全局 FVT/SIT 比例 | `CT-06`（各档占比互异） |
| 除以 SKU 再乘回的伪费率 | `QM-02` 对源码断言 |
| 扣减未证明的复用 | `RS-01`…`RS-05` |
| PCBA 与 unit 混算 | `D01-04` `RS-08` |
| 业务取整 | `rounding` 为 Schema const；`D01-01`…`D01-03` |
| 用产品系列名做判断 | `PR-01` |
| 联网取数 | 内核为纯函数 + 本地静态规则包，无网络调用点 |

---

## 5. 错误与边界处理

| 情形 | 行为 |
|---|---|
| 五维全空 | `UNDETERMINED`，不计价，只出提示 |
| 部分维度空 | `SINGLE_WITH_RESERVATION` 或 `RANGE`，reasons 里点名未回答维度 |
| 超出支持域 | `OUT_OF_DOMAIN`，不计价，`OUT_OF_DOMAIN_INPUT` ORI（ORI-13 未定前的安全默认） |
| 全部 Spec 被标 LATER_WAVE | 该维度 Current Wave = 0 → 落入 `OUT_OF_DOMAIN`，作为矛盾暴露而非隐藏 |
| UNKNOWN 扇出 > 32 | 折叠为两极值 + `truncated = true` |
| Certification 手工值与两套模型都不同 | 采用手工值，`value_source = USER_MANUAL_OVERRIDE`，其余 cell 不受影响 |
| Reuse 依据为空但勾了"已证明" | Schema 要求 `basis` 非空；前端表单同样必填 |
| 规则包来源 SHA 与预期不符 | 启动时告警并在结果页标注（防止把未确认规则当已确认） |

---

## 6. 打包与运行形态

- **静态站点或本地单文件 HTML**，无后端、无登录、无网络请求。
- 历史分析存浏览器 IndexedDB（本地），键为 `analysis_id`，值含完整 input document +
  output payload + 规则版本，可复现。
- 导出：CSV（Function × Phase × SKU 明细，含 rule_id 与来源行号）、JSON（完整 payload）。
  两者都带 `rounding: "NONE (D-01)"` 与规则版本；CSV 提供全精度列与显示精度列两栏。
- 规则包 `rule_pack_v2.json` 随包发布，状态字段显示 `DRAFT_UNCONFIRMED_BY_OWNER`。

---

## 7. 实施顺序（建议 3 个 PR）

| PR | 内容 | 验收 |
|---|---|---|
| **P3-1** 内核移植 | `rules_v2.js` + 跨语言黄金对照（11 用例） | 所有数字 `1e-9` 内一致；`SR-09` 在 JS 侧同样失败 |
| **P3-2** 规则包与契约 | 打包脚本产出 `rule_pack_v2.json`（含来源 SHA）；前端 import 两个 Schema | 结果页显示规则版本 + 来源指纹；Schema 校验在前后各跑一次 |
| **P3-3** 三页 UI + 导出 | 见 `docs/20` | 手工输入闭环可跑通；能导出含证据的 CSV；断网可用 |

不在本阶段做：自动读取、Build Plan 比较、任何账号/权限/审批/后台。
