# 19 — I + J. 回归测试（v2）与预期 PASS/FAIL 清单

> 执行：`python -X utf8 tools\validate_rules_v2.py`
> 产物：`artifacts/validation/regression_report_v2.md`、`regression_results_v2.json`
> 用例样本：`artifacts/validation/worked_examples_v2.md` / `.json`（11 例，由引擎实时生成）
> 基线复现锚点仍由 `tools/validate_rules.py`（Phase 1 套件）与 `RT-01` 双重守护。

---

## 1. 这套测试怎么解释

每条探针带一个 **Owner 批准的期望值**，因此报告区分两件事：

| 概念 | 含义 |
|---|---|
| **probe result** | 不变量当下成立还是不成立 |
| **verdict** | 探针结果与期望一致 → `OK`；不一致 → `REGRESSION` |

所以 **`SR-09` 显示 `[FAIL]` 是正确状态**，它期望就是 `FAIL`。
套件整体 `STATUS: CLEAN` 的含义是"没有出现非预期偏差"，**不是**"全绿"。

**退出码**：有 REGRESSION 时返回 1，否则 0。`SR-09` 失败**不会**让 CI 变红，
但如果哪天它意外变绿，`SR-09` 会立刻报 REGRESSION —— 这是防止后人"顺手修绿"的机关。

当前实际结果：**70 条探针，69 条成立，1 条按设计失败，0 条回归，`STATUS: CLEAN`。**

---

## 2. J · 预期 PASS / FAIL 清单

### 2.1 设计缺口（唯一预期失败项）

| ID | 不变量 | 期望 | 失败原因与关闭条件 |
|---|---|---|---|
| `SR-09` | every SKU definition is reachable as a unique recommendation | **FAIL** | 5 SKU 定义是 4 SKU 定义的严格子集，在 405 组现实输入中作为唯一答案出现 **0 次**。关闭需要 Owner 提供：① 真实 4 SKU 项目样本 ② 真实 5 SKU 项目样本 ③ 正式分界条件。**禁止**通过改权重、加惩罚项或改断言使其转绿。 |

> 这一条**不得删除、不得弱化、不得改写断言、不得改成 `xfail(strict=False)` 之类**。
> 它在 `validate_rules_v2.py` 里以 `expected="FAIL"` 显式标注，注释中写明 ORI-04。

### 2.2 预期 PASS（69 条），按主题分组

| 组 | ID | 守护的决策 |
|---|---|---|
| 基线复现 | `RT-01` | 提取链完整（365 / 417 / 443.8 / 474 / 507） |
| Quantity Model | `QM-01`…`QM-08` | DEC-05：伪费率取消、MEPA/HW PA 绝对量、平坦不升级、来源可追 |
| Certification | `CT-01`…`CT-08` | DEC-03：三模型并存、不选不合并、区间不平均、手工覆盖、无全局比例、一致也不升级、自动出 ORI |
| Panel 语义 | `PL-01`…`PL-04` | DEC-02：按 Spec Count 匹配、批注排除、维度保留、反证批注不在计算路径 |
| SKU 推荐 | `SR-01`…`SR-08`、`SR-10` | DEC-01：平局报范围、`NOT_ESTABLISHED`、全员计价、不填充、空输入、越域拒绝、权重冻结 |
| Wave | `WV-01`…`WV-11`（含 `WV-07b`） | DEC-04：只排除明确 LATER_WAVE、两口径可不同答案、不改费率、无折减常量、不推断第二波、UNKNOWN 扇出、来源记录、ORI、波次有承载力 |
| Reuse 保护 | `RS-01`…`RS-08` | DEC-06：四态、仅 proven 扣减、账本可审计、嵌入式共享标记、PCBA 隔离 |
| D-01 小数 | `D01-01`…`D01-07` | DEC-07：不取整、容差不改值、PCBA/UNIT 分开、预留不因额外需求放大 |
| 红线与溯源 | `PR-01`…`PR-05` | 产品名不进判断、逐行溯源、缺失不默认、用户值优先且保留文件值 |
| Schema 契约 | `SC-01`…`SC-07` | 输出过 Schema、输入过 Schema、拒文本哨兵、拒未知 Reuse 状态、**区间禁止显示为单值**、`from_document` 契约精确、声明的 Wave 真能传到底层 |

完整逐条表格由 `regression_report_v2.md` 自动产出（Expected / Actual / Verdict 三列），
避免本文与实际结果脱节。

---

## 3. 契约级测试（不是数值测试）

| ID | 断言的性质 |
|---|---|
| `QM-02` | 对 `rules_v2.py` **源码**断言不含 `per_sku_rate` / `ttl_per_phase` —— 伪费率不是"没用"，是"不存在" |
| `SR-10` | 权重常量字面量必须等于 Phase 1 值 —— 任何"为了变绿的微调"立刻暴露 |
| `CT-03` | 序列化结果里不得出现 `avg`；`recommended_total` 必须为 `null` |
| `WV-04` | 模块命名空间里不得出现含 RATIO / DEDUCTION 的波次常量 |
| `SC-05` | 用 Schema 的 `if/then` 反证：把区间伪装成单值会**校验失败** |
| `PL-04` | 反证：`panel=1` 仍判 3 SKU；若 E2 批注在计算路径上此结果不可能成立 |

这类"结构断言"比数值断言更难被无意绕过。

---

## 4. worked examples v2（11 例）

| 用例 | 输入（CPU/GPU/Panel/SSD/Mem） | 展示什么 | 场景数 | 结果 |
|---|---|---|---|---|
| EX-A | 1/1/1/1/1 | 干净最小配置 | 2 | 2 SKU，区间 `366–373`（Cert 未定） |
| EX-B | 3/3/2/2/2 | **4/5 SKU 平局** | 2 | `RANGE 4–5`，两档都算：`438.8–443.8` / `469–474` |
| EX-C | 3/–/–/–/– | 只答一维 | 2 | 3/4/5 三档并列计价，不给单值 |
| EX-D | 2/2/1/2/2 + 声明第二波 | Wave 生效 | 2 | **CW → 3 SKU `408–417`；FP → 4 SKU `438.8–443.8`** |
| EX-E | 2/2/1/2/2（不声明 Wave） | **不推断第二波** | 2 | CW = FP = 4 SKU，出 `WAVE_ASSIGNMENT_NOT_PROVIDED` |
| EX-F | 同上 + 第二颗标 UNKNOWN | 显式未知 → 扇出 | 5 | 4 个 CW 场景，答案落在 3 与 4 两种读法 |
| EX-G | 3/3/2/2/2 + RF Cert 手工 10 | 手工覆盖收敛 | 2 | 4 SKU 从区间收敛为**精确 `438.8`** |
| EX-H | 3/2/2/2/2 + 四条 Reuse | 仅 proven 扣减 | 2 | 声称 14.0 → 实扣 **4.0** |
| EX-I | 3/2/2/2/2 + PCBA 12 | 单位隔离 | 2 | unit 总量不变，PCBA 单列 |
| EX-J | 3/2/2/2/2 + 预留 5% | 小数保留 | 2 | `460.74–465.99`，预留 `21.94 / 22.19` 不取整 |
| EX-K | 9/3/2/2/2 | 越域拒绝 | 2 | `OUT_OF_DOMAIN`，**不计价**，出 ORI |

> 注意 EX-A/EX-B 的"场景数 = 2"：无第二波声明时 Current Wave 与 Full Project 数量相同，
> 但两条仍并列输出并标 `identical_to_full_project = true`。
> "区间"来自 Certification 未定（ORI-02），不是四舍五入误差。

---

## 5. Phase 1 套件的关系

`tools/validate_rules.py`（16 条，Phase 1）继续运行，其中：

- `workbook grand totals reproduce`、`D-01 decimals` 等被 `RT-01` / `D01-0x` 覆盖并加强；
- Phase 1 的 `every SKU definition is reachable` 与本套 `SR-09` 是同一缺口的两处记录，
  **两处都保持 FAIL**；
- Phase 1 的 `second wave splits into two SKU views` 已被 v2 的显式 Wave Assignment
  取代（`WV-01`/`WV-02`），旧文件保留以维持设计可追溯性。

两套并存的意义：Phase 1 文件是"当初怎么想的"，Phase 2 文件是"Owner 拍板后必须成立的"。

### 5.1 退出码口径（重要，避免误判）

`tools/validate_rules.py`（Phase 1）只要存在失败不变量就 `exit 1`，
所以它**现在且将继续返回 1** —— 唯一的失败项就是 ORI-04 探针。这不是故障，
但因此**不能**用作 CI 门禁。Phase 1 脚本保持原样不改，作为"当初设计意图"的历史记录。

**CI 门禁 = `tools/validate_rules_v2.py` 退出码（0 = 无回归）+ `tools/verify_integrity.py` 输出 `RESULT: PASS`。**

v2 套件把 `probe result` 与 `verdict` 分开，所以 `SR-09` 的 `FAIL` 不影响退出码；
但它一旦**意外变绿**就会变成 REGRESSION 并让退出码变成 1 ——
即"改绿"比"保持红"更容易被 CI 抓住。`verify_integrity.py`  additionally 断言
`expected_failures == ['SR-09']` 且 `SR-09` 仍在 `probes_failing` 中。

---

## 6. 复跑顺序

```bat
python -X utf8 tools\extract_workbook.py
python -X utf8 tools\build_baseline_dataset.py
python -X utf8 tools\derive_quantity_model.py
python -X utf8 tools\export_model_delta.py
python -X utf8 tools\gen_examples_v2.py
python -X utf8 tools\validate_rules_v2.py      REM 退出码 0 = 无回归
python -X utf8 tools\verify_integrity.py
```

前置脚本全部只读 `original_documents`，写入路径受 `guard_write()` 拦截。
