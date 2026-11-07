# 37 — Owner 决定记录 v4（交付物：更新后的 Owner Decision 记录）

## DEC-10（本轮新决定）

> 「当前 MVP 和团队试用阶段，Certification 以附表中对应 SKU、Function 和 Phase 的总量为准。」

编码位置：`artifacts/model/quantity_model_v4.json → owner_decision`、
`artifacts/model/rule_pack_v4.json → owner_decision / certification_adoption`、
`prototype/rules_v3.py`（常量 `ADOPTED_SOURCE / ADOPTED / AUDIT`）。

| 项 | 内容 |
|---|---|
| decision | `DEC-10` |
| adopted_value_source | `APPENDIX_TABLE_TOTAL` |
| audit_only_source | `MAIN_TABLE_PER_SKU_RATE_TIMES_SKU` |
| appendix_counted_in_project_total_times | **1** |
| main_derived_counted_in_project_total_times | **0** |
| j33_counted_in_project_total_times | **0** |
| phase_ratio_used | `null`（FVT / SIT 各自读自己的附表行） |
| user_override_scope | `THIS_ANALYSIS_ONLY` |
| scope | MVP + 团队试用；**不关闭 ORI-02**（两列为何不仍一致仍需 Owner 回答） |

### DEC-10 的边界（Agent 明确不做的事）

1. 不把主表派生值与附表值相加，也不把两者做成区间或上下界。
2. 不把附表值"还原"成每 SKU 费率（不做除再乘的伪费率还原）。
3. 不因为采用附表就把 ORI-02 标为 RESOLVED：采用 ≠ 解释。
4. 不把 Rule Package 从 `DRAFT_PENDING_OWNER` 升级为 CONFIRMED。
5. 不把用户本次覆盖写回规则包（覆盖只存在于该条 Analysis 的快照里）。

---

## 保持不变的既有决定

| 决定 | 内容 | 本轮 |
|---|---|---|
| DEC-01 (ORI-04) | 4 SKU 与 5 SKU 无法区分 → 输出 `RANGE`，`recommended_sku = null`，`preferred_sku = NOT_ESTABLISHED`，两档都完整计价 | **不变**（探针 SR-01…SR-05、DA-07） |
| DEC-02 (ORI-01) | Panel = Panel Spec Count；D2:H2 批注 `UNRESOLVED_COMMENT` 不参与计算 | **不变**（PL-01…PL-05） |
| DEC-03 | 三套竞争模型（Phase 2）→ 已由 DEC-09 废止 | 继续废止，`competing_candidates` 禁止复现 |
| DEC-04 (ORI-03) | 波次只能显式指定；UI「未特别指定」= `NO_EXPLICIT_ASSIGNMENT`，不是 `UNKNOWN`；波次永不产生固定量或比例 | **不变**（WV-01…WV-13） |
| DEC-05 | 五个 Quantity Model；绝对值直读；无伪费率 | **不变**（QM-01…QM-09、DA-09） |
| DEC-06 | 只有已证明的 `ADDITIONAL_CONFIRMED_REUSE` 才可抵扣 | **不变**（RS-01…RS-10） |
| DEC-07 / D-01 | 全程十进制底层值，显示精度永不回写 | **不变**（D01-01…D01-09、EX-04） |
| DEC-08 | 手动输入 MVP 范围；ORI-09 / ORI-11 与 MVP 解耦 | **不变** |
| DEC-09 (ORI-02) | Certification 只有一套规则；FVT / SIT 各行独立；区间只能来自 SKU 档位；J33 为解释证据 | **部分被 DEC-10 取代**：「采用哪一列」改为附表；其余约束全部保留 |

## DEC-09 与 DEC-10 的关系（避免误解）

- DEC-09 说的是：**不要**把主表与附表当成两套互相竞争的规则，不要区间，不要叠加 J33。
- DEC-10 说的是：在这个前提下，**采用**附表那一列的数字。
- 两者不冲突：DEC-10 只替换了「采用哪一列」，没有恢复任何竞争模型行为。
  因此 `COMPETING_CERTIFICATION_MODELS`、`CERTIFICATION_MODEL_UNRESOLVED`
  仍然只存在于"被禁止"名单里，永不作为 `kind` 输出（探针 DA-08 / CT-V2-09）。
