# 03 — D. Simplified User Input Model ＋ E. File Auto-reading & Manual Selection Logic

设计红线（任务第三节）：用户**不输入 SKU 数量**；Key Factor 缺失时**保持"请补充"**，绝不默认 0/1/不适用。
本章每条逻辑均在 `prototype/rules_v1.py` 中可执行，并由 `tools/validate_rules.py` 断言（见 §E.8）。

---

## D. 输入模型

## D.1 输入分层

```
AnalysisInput
├── Key Factors（5 项，用户可见、可改）          ← 唯一驱动 SKU 推荐
│     cpu   : CPU 组合数量
│     gpu   : GPU 组合数量
│     panel : Panel Spec 数量
│     ssd   : SSD Spec 数量
│     mem   : Memory Spec 数量
├── 上下文（可选，MVP 仅记录不驱动）
│     odm            : LCFC | HQ | Compal | (空)
│     product_series : 自由文本（仅展示，不参与判定 → ORI-13）
│     wave_scope     : CURRENT | FULL_PROJECT（影响 ssd/mem 的解释）
├── 额外需求（按需展开，默认折叠）
│     conditional_increment      : 小数，来自用户勾选的 Option 项
│     confirmed_reuse            : 小数，已确认可复用台数
│     potential_reuse            : 小数，仅展示
└── 对照（可选）
      existing_plan              : 上传/粘贴的 ODM 或 TPM Build Plan 明细
```

## D.2 Key Factor 值对象（每个字段都带完整溯源）

```jsonc
{
  "name": "cpu",
  "file_value": 3,          // 文件自动读取值，读取失败 = null
  "file_confidence": 0.92,  // 读取置信度，见 E.3
  "user_value": 4,          // 用户在页面上的最终选择
  "user_edited": true,      // 是否发生修改（MVP 不要求填写原因）
  "effective": 4,           // 本次分析实际采用值（派生）
  "source": "USER",         // USER | FILE | UNKNOWN（派生）
  "status_user": "用户已修改" // 面向用户的中文状态（派生）
}
```

四条不变量（已由测试断言）：

1. `effective = user_value if user_edited else (file_value ?? user_value)`；
2. `file_value` 一旦读入即**只读留痕**，用户修改不会覆盖它；
3. `file_value == null && !user_edited` → `effective = null` → 状态 `请补充`；
   **不存在**任何 `default 0` / `default 1` / `default N/A` 路径；
4. `effective == null` 的维度在 SKU 评分中被**完全剔除**（不参与分母），而不是按 0 匹配。

## D.3 面向用户的状态词表（内部码 → UI 文案）

| 内部码 | 用户可见 | 触发条件 |
|---|---|---|
| `READ_FROM_FILE` | **已读取** | `file_value != null && !user_edited` |
| `USER_MODIFIED` | **用户已修改** | `user_edited && user_value != null`（并展示"原读取值 X"） |
| `NEED_CONFIRM` | **请确认** | `file_value != null` 但 `file_confidence < 0.85`，或该字段与规则冲突（ORI-01 类） |
| `NEED_INPUT` | **请补充** | `effective == null` |
| `COMPUTED` | **已计算** | 该行由规则成功算出 |
| `NOT_COMPUTABLE` | **暂无法计算** | 依赖缺失、规则冲突未关闭、或超出定义域 |

## D.4 输入示例

```yaml
# 示例 A：从需求表自动读取，用户未修改
cpu:   {file_value: 3, user_edited: false}   # → 已读取
gpu:   {file_value: 2, user_edited: false}   # → 已读取
panel: {file_value: 2, user_edited: false}   # → 已读取
ssd:   {file_value: 2, user_edited: false}
mem:   {file_value: 2, user_edited: false}
odm: LCFC
# → Recommended SKU = 4（SINGLE），详见 10_examples §1.2

# 示例 B：Panel 没读到，用户手工选择 2
cpu:   {file_value: 3}
gpu:   {file_value: 2}
panel: {file_value: null, user_value: 2, user_edited: true}   # → 用户已修改（原读取值：未读取）
ssd:   {file_value: 2}
mem:   {file_value: 2}
# → 与示例 A 结果相同，但输入溯源为 USER

# 示例 C：Panel 既没读到、用户也没选
panel: {file_value: null, user_edited: false}   # → 请补充；SKU 结果降级为范围
```

---

# E. File Auto-reading and Manual Selection Logic

## E.1 前置事实：当前**不存在**可解析的需求表

`original_documents` 内**只有费率基线表**，没有任何"样机需求表"实例。
因此 E.2–E.5 的读取规则属于**设计提案**，其命中率无法在本阶段实测 → **ORI-09（阻塞 E 功能验收）**。
Agent 不假设表头拼写、不假设语言（文件本身中英混排 + 繁简混用 + 多处拼写错误），采用**归一化 + 别名 + 置信度**三段式。

## E.2 归一化（对表头与单元格文本）

```
NFC → 去首尾与连续空白 → 转小写 → 去标点(*/-_/():：，,。) → 折叠数字两侧空白
```
`CPU 数量*` / `CPU数量` / `cpu qty` / `CPU Qty` 归一后同为 `cpu数量` / `cpuqty`。

## E.3 候选别名与置信度

| 维度 | 高置信别名（0.95） | 中置信别名（0.75） | 需人工确认（0.5） |
|---|---|---|---|
| `cpu` | `cpu数量`,`cpu组合数量`,`cpu spec`,`cpu source数量`,`# of cpu` | `cpu`,`cpu 配置` | `cpu platform`（platform ≠ 数量） |
| `gpu` | `gpu数量`,`gpu组合数量`,`gpu spec`,`gpu source数量` | `gpu`,`gfx` | `dGPU`/`iGPU` 单列（是否计数未定义） |
| `panel` | `panel数量`,`panel spec数量`,`panel source数量`,`面板规格数量` | `panel`,`屏规格数量` | **`panel 分辨率数量`/`尺寸数量`**（口径不同 → ORI-01） |
| `ssd` | `ssd数量`,`ssd spec数量`,`ssd source数量` | `ssd`,`storage数量` | `storage 类型数量` |
| `mem` | `memory数量`,`memory spec数量`,`mem spec数量`,`内存规格数量` | `memory`,`dram数量` | `容量档位数量`（容量 ≠ source） |

**多命中处理**：取最高分；若最高分并列且值不同 → 该字段状态置 `请确认`，把两个候选值都展示给用户，**不自动取舍**（同 §E.5 示例 D）。

## E.4 值解析

- 直接整数 `3` → 3。
- 文本内数字：`2 CPU`、`2种`、`2款`、`2 sources`、`2家` → 2（取第一个数字；出现多个不同数字 → `请确认`）。
- 区间 `2-3` → `请确认`（要求用户选一个；**不取中点、不取上界**）。
- 勾选式 `☑`/`Y`/`O` → **不推断数量** → `请确认`。
- 空白 / `-` / `N/A` / `TBD` / `/` → `请补充`（**不映射为 0 或不适用**）。
- 小数（如 `2.5` 个 Spec）→ 保留小数并在 UI 标注异常（Key Factor 语义应为整数）。

## E.5 手动选择与优先级

```
用户最终确认值  >  文件自动读取值  >  未确认状态(请补充)
```

- UI 每个 Key Factor 一行：`读取值` 灰显 + 可编辑数字框（初始 = 读取值或空）+ 状态徽章。
- 数字框留空 = **不覆盖**；若要"故意置 0"必须显式点 `设为0` 按钮（避免误清空 → 变成"请补充"）。
- 任何 `user_edited` 只记录"改了什么"，**MVP 不采集修改原因**（任务 §三）。
- 修改即失效重算：任何 Key Factor 变更后，结果页标记"结果已过期，请重新运行"。

**示例 D（多命中冲突）**

```
需求表出现： "Panel 尺寸: 2" 与 "Panel Source: 3"
→ panel.file_value = null, file_confidence = 0.5
→ UI: 请确认 —— 候选 2（Panel 尺寸）/ 3（Panel Source）；用户选定后 source=USER
→ 结果页在"待确认项"保留一行：Panel 口径未确认（ORI-01 相关）
```

## E.6 ODM 字段的处置（重要限制）

Owner 行 94 把 `ODM` 列为 Input，但工作簿**没有任何 ODM→数量 的结构化映射**。ODM 差异全部在 J/K 自由文本中（25 行），例如：

| Function | ODM 差异原文 | 可否结构化 |
|---|---|---|
| HW | `Battery life 1 unit/sku, Compal 是 3 units/phase.` | 部分（Compal 用固定量替代 per-SKU） |
| HW | `For old source，Compal/HQ不需要样机。(LCFC SIT 1source *1units)` | 否（依赖 old/new source 概念，未定义） |
| HW | `CPU OC：LCFC/Compal *2 & *2 /phase；HQ: Leverage EE unit.` | 是（选项型，HQ 归 0） |
| THM | `Compal total 6unit for 1unit test…；HQ: total 6unit.` | 是（绝对量 6） |
| EMC Test | `Compal：機台6台，for 6 sku, 1unit/sku；HQ: 1 unit/sku` | 是（=1/sku，与主表 3/2/1.5/1.2/1 冲突） |
| SS | `LCFC 建议 4-6unit/phase；HQ 数量偏少` | 否（未定量） |
| MEPA | `LCFC:Confirmed ok…；HQ/Compal :to be clarify.` | 否（未决） |
| SWPA | `HQ EE noise 是 pwr RD 测试, Compal HLK 是 pre-load 测试，需要对应的 function 做相应的扣除和添加` | 否（跨 Function 转移规则未量化） |

**MVP 决定**：`odm` 作为**记录 + 展示**字段，用于
①结果页标注"本表基准未区分 ODM，以下为 ODM 已知差异提示"；
②把上表可结构化的 3 条（THM 绝对量 6、EMC Test HQ=1/sku、HW CPU OC）作为**候选规则**置于 `rule_candidate` 表，默认 `disabled`。
**不**在 MVP 内做 ODM 自动改算 → **ORI-05**。

## E.7 额外需求与复用输入

| 输入 | 类型 | 校验 | 进入计算 |
|---|---|---|---|
| Option 勾选项（来自 J 列 4 个 `Option:` 块） | 逐项开关 + 可改数量 | 数量 ≥ 0 | ✅ 计入 `conditional_increment`，来源标注 `OPTION+原文` |
| 自定义额外需求 | 自由文本 + 小数数量 | 数量 > 0 | ✅ 计入，标注 `USER_ADHOC` |
| 已确认复用 | 小数 | 0 ≤ 复用 ≤ 计算前需求 | ✅ 负向调整 |
| 潜在复用 | 小数 | ≥ 0 | ❌ **仅展示** |

未勾选的 Option 项在结果页"待确认项"列出，附原文与"未纳入计算"。

## E.8 输入逻辑可执行验收（当前全部通过）

```
[PASS] missing field never defaults to 0/1
[PASS] user value overrides file value
[PASS] file value retained alongside user value
[PASS] potential reuse does not reduce demand
[PASS] confirmed reuse does reduce demand
[PASS] empty input -> UNDETERMINED (no pseudo-precision)
```

## E.9 输入侧边界

| 情形 | 行为 |
|---|---|
| 上传文件解析失败/非表格 | 明确报错，转纯手工输入模式，不产生任何"已读取"状态 |
| 上传文件含多 Sheet | MVP：取第一个可见 Sheet，其余列出让用户选（本次基线表只有 1 个 Sheet） |
| 同一维度出现两列都高置信 | `请确认`，不自动取舍 |
| 用户上传的正是**基线费率表**本身 | 检测到 21×5 费率矩阵特征 → 提示"这是 SKU/需求基线表，不是项目需求表，无法读取 Key Factor" |
| Key Factor 超出定义域（CPU>5, GPU>3, Panel>3, SSD>2, Mem>3） | 进入 SKU 推荐但结果必然 `SINGLE_WITH_RESERVATION` 或 `UNDETERMINED`；UI 提示"超出 SKU Definition 已定义范围" → ORI-13 |
