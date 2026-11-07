# 13 — B. Open Review Item 状态（Phase 2 更新）

本文件是 **ORI 状态的当前权威视图**。（Phase 3 更新：当前权威状态请看 `docs/26_owner_review_register_v3.md` 与 `docs/27_owner_confirmation_checklist_v3.md`。ORI-02 已推进为 `PARTIALLY_RESOLVED`，并新增 ORI-02a / 02b / 15 / 16 / 17；仍然没有任何一项阻塞手工输入 MVP。）
`docs/08_owner_review_items.md` 保留 Phase 1 的完整证据与提问原文，不删改；
两者冲突时以本文件的状态列与临时处置为准。

**状态口径**

| 状态 | 含义 |
|---|---|
| `OPEN` | Owner 尚未回答，Agent 未采用任何临时口径 |
| `INTERIM_TREATMENT_ADOPTED` | Owner 已下达临时处置指令，已写入模型并有探针守护；**最终业务结论仍未确认** |
| `ANSWERED_AWAITING_SAMPLE` | 处置方式已定，但落地需要 Owner 提供样本/上游文件 |
| `CLOSED` / `WAIVED` | 已关闭 / Owner 明确豁免 |

**阻塞口径**（关键区分，避免"所有问题都挡路"）

| 阻塞对象 | 含义 |
|---|---|
| `CONFIRMED_RULE_PACK` | 规则包不能升级为 CONFIRMED；结果持续显示 `DRAFT_UNCONFIRMED_BY_OWNER` |
| `AUTO_SKU_SINGLE_ANSWER` | 该维度上系统只能给范围，不能给单一 SKU |
| `CERTIFICATION_TOTALS` | Certification 数量只能给区间，不能给单一数 |
| `AUTO_FILE_READING` | 自动读取需求表功能不能上线 |
| `BUILD_PLAN_COMPARISON` | 与既有 Build Plan 的差异比较不能上线 |

> **MVP 手工输入主链路目前不被任何 ORI 阻塞。** DEC-08 已把 ORI-09 / ORI-11 从主链路解耦；
> 其余 ORI 的后果是"输出范围 + 持续显示 Review Item"，而不是"功能不可用"。

---

## 状态总表

| ID | 主题 | 严重度 | Phase 1 状态 | **Phase 2 状态** | 决策 | 阻塞对象 | 阻塞 MVP 手工主链路 |
|---|---|---|---|---|---|---|---|
| ORI-01 | Panel 语义冲突（定义 vs `D2:H2` 批注） | MAJOR | OPEN | `INTERIM_TREATMENT_ADOPTED` | DEC-02 | `CONFIRMED_RULE_PACK` | 否 |
| ORI-02 | Certification 三套竞争模型 | MAJOR | OPEN | `INTERIM_TREATMENT_ADOPTED` | DEC-03 | `CONFIRMED_RULE_PACK`, `CERTIFICATION_TOTALS` | 否（给区间） |
| ORI-03 | 第二波无判据 | MAJOR | OPEN | `INTERIM_TREATMENT_ADOPTED` | DEC-04 | `CONFIRMED_RULE_PACK`（波次部分已可用） | 否 |
| ORI-04 | **5 SKU 永不可被单独推荐**（SKU5 ⊂ SKU4） | MAJOR | OPEN | **`OPEN`** | DEC-01（仅临时口径） | `CONFIRMED_RULE_PACK`, `AUTO_SKU_SINGLE_ANSWER` | 否（给 `4–5 SKU` 范围） |
| ORI-05 | ODM 无结构化规则 + 3 处 Status 未关闭 | MAJOR | OPEN | `OPEN` | — | `CONFIRMED_RULE_PACK` | 否（ODM 仅记录） |
| ORI-06 | Option 项是否启用 / PCBA 单位 | MINOR | OPEN | `OPEN` | — | `CONFIRMED_RULE_PACK` | 否（不预置） |
| ORI-07 | Risk Reserve 无来源 | MINOR | OPEN | `OPEN` | — | `CONFIRMED_RULE_PACK` | 否（默认 0%） |
| ORI-08 | 匹配权重/阈值属 Agent 设定 | MINOR | OPEN | `OPEN`（权重已被探针冻结） | DEC-01 限制其用途 | `CONFIRMED_RULE_PACK` | 否 |
| ORI-09 | **无真实需求表样本** | MAJOR | OPEN | `ANSWERED_AWAITING_SAMPLE` | DEC-08 | `AUTO_FILE_READING` | **否**（已解耦） |
| ORI-10 | MEPA / HW PA 实为绝对量，回推不一致 | MAJOR | OPEN | `INTERIM_TREATMENT_ADOPTED` | DEC-05 | `CONFIRMED_RULE_PACK` | 否 |
| ORI-11 | G10/G12/SP/PPA sample standard 1.0 未提供 | MAJOR | OPEN | `ANSWERED_AWAITING_SAMPLE` | DEC-08 | `BUILD_PLAN_COMPARISON` | **否**（已解耦） |
| ORI-12 | 疑似"统一假设"费率（6 个 Function 共用同一组值） | MINOR | OPEN | `OPEN` → 已扩为 **6 条 model questions** | DEC-05 拒绝按形状升级 | `CONFIRMED_RULE_PACK` | 否 |
| ORI-13 | 定义域空洞（超出 2–6 SKU 支持域无规则） | MAJOR | OPEN | `INTERIM_TREATMENT_ADOPTED` | 引擎新增 `OUT_OF_DOMAIN` 拒绝态 | `CONFIRMED_RULE_PACK` | 否（拒绝而非外推） |
| ORI-14 | 缩写与 Green FVT 自相矛盾 | MINOR | OPEN | `OPEN` | — | `CONFIRMED_RULE_PACK` | 否 |

**统计**：14 项 → `INTERIM_TREATMENT_ADOPTED` 5 项、`ANSWERED_AWAITING_SAMPLE` 2 项、`OPEN` 7 项、`CLOSED` 0 项。
**仍可阻塞 `CONFIRMED_RULE_PACK` 的：全部 14 项。阻塞手工输入 MVP 主链路的：0 项。**

---

## 各项 Phase 2 处置说明

### ORI-01 · Panel 语义 → `INTERIM_TREATMENT_ADOPTED`（DEC-02）

- 已做：Panel 按 **Panel Spec Count** 匹配；`D2:H2` 批注整体降级 `UNRESOLVED_COMMENT`，
  在输出 `unresolved_comments_excluded` 中原样回显；Panel 独立输入维度保留。
- 探针：`PL-01`–`PL-04`。`PL-04` 是反证：`panel=1` 仍判 3 SKU，若批注在计算路径上这不可能成立。
- **还需要 Owner 回答**：`D2:H2` 的 `N*panel` 到底指什么（显示口径？历史口径？还是
  "每个 SKU 都要一套 panel 治具"这类非样机数量语义？）。同一批注在 6 SKU 处写 `3*CPU`
  而定义是 `4-5*CPU`，也要一并澄清。
- 关闭条件：Owner 给出批注语义 + 确认 Panel 定义维持行 79–83。

### ORI-02 · Certification → `INTERIM_TREATMENT_ADOPTED`（DEC-03）

- 已做：8 个 cell 全 `UNRESOLVED`；按证据源分别完整计价并给区间；
  `J33_FORMULA` 保留为"声明但不可评估"（缺 antenna / WLAN 卡数量）；提供逐项手工覆盖入口；
  FVT/SIT 逐 cell 查表（探针 `CT-06` 证明各档 FVT 占比 0.4712–0.4769 互不相同，不存在全局比例）。
- 当前区间（`artifacts/model/model_delta.md`）：

  | SKU | Main Table | Secondary Table | 发布区间 |
  |---:|---:|---:|---|
  | 2 | 373.0 | 366.0 | `366–373` |
  | 3 | 417.0 | 408.0 | `408–417` |
  | 4 | 443.8 | 438.8 | `438.8–443.8` |
  | 5 | 474.0 | 469.0 | `469–474` |
  | 6 | 506.6 | 502.0 | `502–506.6` |

- **还需要 Owner**：在"主表 / 副表 / 按 J33 天线×WLAN 卡源驱动 / 混合规则"中选定一种，
  并提供 antenna source 与 WLAN card 数量是否进入输入模型。
- 注意：两套模型恰好一致的 cell（EMC、Green FVT 等）**仍保持 UNRESOLVED**，只标注
  `models_agree = true`。一致是信息，不是把模型升为 CONFIRMED 的理由。

### ORI-03 · 第二波 → `INTERIM_TREATMENT_ADOPTED`（DEC-04）

- 已做：Wave 挂在单颗 Spec 上并记录来源；只排除**明确** `LATER_WAVE`；
  未标注 → 计入 Current Wave + `WAVE_ASSIGNMENT_NOT_PROVIDED` ORI；
  显式 `UNKNOWN` → 扇出 + `WAVE_ASSIGNMENT_UNKNOWN` ORI；无任何按波次的比例或固定折减。
- 探针 `WV-10` 确认声明波次确实会改变 SKU 答案（CW=3 / FP=4），契约有承载力。
- **还需要 Owner**：正式需求表里用哪一列/哪个标记表达 Wave；`IMPLICIT_SINGLE_SPEC`
  这条唯一允许的推断是否接受；3 SKU 的第二波条款是否也适用于其他 SKU 档。

### ORI-04 · 5 SKU 不可达 → **`OPEN`（唯一保留的失败探针）**

- 已做（仅临时口径，不构成业务结论）：`RANGE [4,5]`、`preferred_sku = NOT_ESTABLISHED`、
  两个候选都完整计价、权重被 `SR-10` 冻结、`SR-09` 保持 `EXPECTED FAIL`。
- 现状证据：405 组现实输入中，**5 SKU 作为唯一答案出现 0 次**；4 SKU 与 5 SKU 得分恒等
  （`{4: 1.0, 5: 1.0}`），因为 5 SKU 定义 `CPU 3–4 · GPU 3 · Panel 2 · SSD 2 · Mem 2`
  是 4 SKU 定义 `CPU 2–4 · GPU 2–3 · Panel 2 · SSD 2 · Mem 2` 的**严格子集**。
- **还需要 Owner**：① 真实的 4 SKU 项目样本；② 真实的 5 SKU 项目样本；③ 正式分界条件
  （例如 CPU source 数、GPU vendor 数、ID/ME 差异、认证范围宽度等可判定的第四个维度）。
- **明确禁止**：为了探针转绿而调权重、加惩罚项或改写断言。
  在 ①②③ 到位前，`SR-09` 必须继续失败。

### ORI-05 / 06 / 07 / 08 / 12 / 14 → 仍 `OPEN`

Phase 2 未获得新证据，也未获得 Owner 指令，因此**没有**任何口径变更：
ODM 仅记录不生效、Option 项不预置、Risk Reserve 默认 0%、匹配权重被冻结且禁止用于打破平局、
平坦费率不因形状升级为 `PER_PHASE_FIXED`、缩写与 Green FVT 矛盾不自行解读。
ORI-12 在 Phase 2 被机器化为 `quantity_model_v2.model_questions` 的 6 条记录
（EMC Test / NV / INTEL 各 FVT+SIT），以便 Owner 逐条回答。

### ORI-09 → `ANSWERED_AWAITING_SAMPLE`（DEC-08）

- 已做：手工输入主链路不再依赖自动读取；输入契约由 `input.schema.json` +
  `AnalysisInput.from_document()` 固定，探针 `SC-06`/`SC-07` 证明契约可实现。
- **还需要 Owner**：2–3 份真实或脱敏需求表（含表头、单位列、Wave 标记位置）。
  在此之前不实现任何别名映射或列位置猜测。

### ORI-10 → `INTERIM_TREATMENT_ADOPTED`（DEC-05）

- 已做：MEPA / HW PA 共 4 个 cell 改为 `PER_PHASE_FIXED`，直读绝对量；
  主表那个"除以 SKU 再乘回来"的伪费率作为竞争证据保留展示；`QM-02` 从源码层面禁止伪费率。
- 影响已量化：仅 4 个 cell 变动 —— MEPA FVT/SIT @2 SKU 各 +4；HW PA FVT/SIT @6 SKU 各 −0.2。
- **还需要 Owner**：确认 MEPA / HW PA 就是每相位绝对量；确认 2 SKU 档 MEPA 是 36 而非 32；
  确认 HW PA 在 6 SKU 档饱和于 4。

### ORI-11 → `ANSWERED_AWAITING_SAMPLE`（DEC-08）

- 已做：Build Plan 差异比较与 SWPA 正式校验移出本次范围；`rule.schema.json` 已为
  `STANDARD` / `BUILD_PLAN` 类型的来源预留 `role` 字段。
- **还需要 Owner**：既有 ODM/TPM Build Plan 样本、`PPA sample standard 1.0`、G10/G12/SP 历史数据。

### ORI-13 → `INTERIM_TREATMENT_ADOPTED`

- 已做：新增 `state = OUT_OF_DOMAIN`。超出支持域（如 CPU 9）时**拒绝**推荐、不计价、
  生成 `OUT_OF_DOMAIN_INPUT` ORI，而不是外推一个 7 SKU 答案。探针 `SR-08`。
- **还需要 Owner**：SSD Spec > 2、GPU Spec > 3、Panel Spec > 3、CPU Spec > 5 的正确行为
  （拒绝 / 封顶 / 升档到 7 SKU），以及是否要支持 7 SKU。

---

## 对使用者的可见后果（当前状态下的真实输出）

1. 结果页长期显示 `DRAFT_UNCONFIRMED_BY_OWNER`，因为 14 项 ORI 全部仍阻塞规则包定版。
2. 同时匹配 4/5 SKU 时给 `4–5 SKU` 范围 + 两套完整数量，不给单一数。
3. 总量长期是区间（Certification 未定），不是单值；区间宽度 4.6–9.0 台。
4. 需求表未标 Wave 时，Current Wave 暂时等于 Full Project，并持续提示待确认。
5. 每一行数量都可展开到"来源文件 + 工作表 + 行号 + 采用的 Quantity Model + 竞争来源"。
