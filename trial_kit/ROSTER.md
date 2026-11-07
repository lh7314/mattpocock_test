# 试用案例清单（Trial roster，S1 用）

- 规则包：`RP-V4.0`（仍是 DRAFT_PENDING_OWNER，本清单不改状态）
- 生成时间：2026-11-06T08:36:38+00:00
- 回收关联方式：按 **Project** 列逐字对应（`project_name`）
- 推荐用法：双击 `web\index.html` →「参加团队试用」，选案例即自动载入本清单里的项目名、Key Factors 与 Wave（案例配置锁定，不让试用者改）；本文件同时是给不使用网页的同事的备用清单。

## 1. 案例清单

| 案例 | 项目名（必须逐字使用） | Key Factors（在 web\new.html 输入） | 配置画像 | 覆盖的差异格 | 依据 |
|---|---|---|---|---|---|
| C1 | `TRIAL-C1-SKU2` | cpu=2 / gpu=1 / panel=1 / ssd=1 / mem=1 | 简单配置（低配项目） | RF Certification / SIT @ SKU2 | C79 (2SKU: 1-2*CPU +1*GPU +1-2*Panel +SSD*1 +Mem*1) |
| C2 | `TRIAL-C2-SKU3` | cpu=3 / gpu=2 / panel=1 / ssd=1 / mem=1 | Green / SIT 差异取证（必须 3 SKU） | Green / SIT @ SKU3；RF Certification / SIT @ SKU3 | C80 (3SKU: 2-3*CPU +2*GPU +1*Panel +SSD*1 +Mem*1) |
| C3 | `TRIAL-C3-SKU4` | cpu=2 / gpu=2 / panel=2 / ssd=2 / mem=2 | 中等配置（4 SKU 单值） | RF Certification / SIT @ SKU4 | C81 (4SKU: 2-4*CPU +2-3*GPU +2*Panel +SSD*2 +Mem*2) |
| C4 | `TRIAL-C4-RANGE45` | cpu=3 / gpu=3 / panel=2 / ssd=2 / mem=2 | 4-5 SKU 范围项目（SR-09 现场） | RF Certification / SIT @ SKU4；RF Certification / SIT @ SKU5 | C81 与 C82 的交集（同时满足 4SKU 与 5SKU 定义） |
| C5 | `TRIAL-C5-SKU6-WAVE` | cpu=5 / gpu=3 / panel=3 / ssd=2 / mem=2 | 复杂配置 + LATER_WAVE（必须 6 SKU） | RF Certification / SIT @ SKU4；RF Certification / SIT @ SKU5；RF Certification / SIT @ SKU6；Safety / FVT @ SKU6 | C83 (6SKU: 4-5*CPU +3*GPU +2-3*Panel +SSD*2 +Mem*2-3)；全表唯一的波次提法是 C80 括号里的「(or SSD/Mem spec *2, arrange 2nd wave)」，它只提到 SSD / Memory，没有判据，也没有提到 CPU / Panel（ORI-03） |

## 2. 每个案例的预期结果（由 prototype/rules_v3.py 实算，不是手写）

| 案例 | 场景 | SKU 判定 | 推荐 SKU | 范围 | 总量 | Certification | 登记的待确认项 |
|---|---|---|---|---|---|---|---|
| C1 | FULL_PROJECT | SINGLE | 2 | 2-2 | SKU2=366.0 | SKU2=32.0 | CERTIFICATION_APPENDIX_VALIDATION_INCOMPLETE、CERTIFICATION_BREAKDOWN_EVIDENCE_NOT_GENERALIZED、CERTIFICATION_SOURCE_VALIDATION_MISMATCH、WAVE_ASSIGNMENT_NOT_PROVIDED |
| C1 | CURRENT_WAVE | SINGLE | 2 | 2-2 | SKU2=366.0 | SKU2=32.0 |  |
| C2 | FULL_PROJECT | SINGLE | 3 | 3-3 | SKU3=408.0 | SKU3=33.0 | CERTIFICATION_APPENDIX_VALIDATION_INCOMPLETE、CERTIFICATION_BREAKDOWN_EVIDENCE_NOT_GENERALIZED、CERTIFICATION_SOURCE_VALIDATION_MISMATCH、WAVE_ASSIGNMENT_NOT_PROVIDED |
| C2 | CURRENT_WAVE | SINGLE | 3 | 3-3 | SKU3=408.0 | SKU3=33.0 |  |
| C3 | FULL_PROJECT | SINGLE | 4 | 4-4 | SKU4=438.8 | SKU4=36.0 | CERTIFICATION_APPENDIX_VALIDATION_INCOMPLETE、CERTIFICATION_BREAKDOWN_EVIDENCE_NOT_GENERALIZED、CERTIFICATION_SOURCE_VALIDATION_MISMATCH、WAVE_ASSIGNMENT_NOT_PROVIDED |
| C3 | CURRENT_WAVE | SINGLE | 4 | 4-4 | SKU4=438.8 | SKU4=36.0 |  |
| C4 | FULL_PROJECT | RANGE | （不给单值） | 4-5 | SKU4=438.8; SKU5=469.0 | SKU4=36.0; SKU5=37.0 | CERTIFICATION_APPENDIX_VALIDATION_INCOMPLETE、CERTIFICATION_BREAKDOWN_EVIDENCE_NOT_GENERALIZED、CERTIFICATION_SOURCE_VALIDATION_MISMATCH、SKU_TIE_NOT_RESOLVABLE、WAVE_ASSIGNMENT_NOT_PROVIDED |
| C4 | CURRENT_WAVE | RANGE | （不给单值） | 4-5 | SKU4=438.8; SKU5=469.0 | SKU4=36.0; SKU5=37.0 |  |
| C5 | FULL_PROJECT | SINGLE | 6 | 6-6 | SKU6=502.0 | SKU6=38.0 | CERTIFICATION_APPENDIX_VALIDATION_INCOMPLETE、CERTIFICATION_BREAKDOWN_EVIDENCE_NOT_GENERALIZED、CERTIFICATION_SOURCE_VALIDATION_MISMATCH、SKU_TIE_NOT_RESOLVABLE、WAVE_ASSIGNMENT_NOT_PROVIDED |
| C5 | CURRENT_WAVE | RANGE | （不给单值） | 4-6 | SKU4=438.8; SKU5=469.0; SKU6=502.0 | SKU4=36.0; SKU5=37.0; SKU6=38.0 |  |

## 3. 每个案例只问它自己涉及的问题

试用者不需要回答全部 19 条 Owner 问题：案例没跑到的东西，问了只能换来猜测。
本清单合计把 10/19 条问题列为必答（按案例），其余 9 条作为可选题仍会出现在每个人的反馈页里，可答可不答；本清单保证 19/19 条问题至少被问到一次。

| 案例 | 必答问题 | 由该案例引出的 Owner 问题 | 可选（其余 ORI） |
|---|---|---|---|
| C1 | · RF Certification / SIT @ SKU2：本工具采用附表 8.0，主表推算为 15.0（差 -7.0）。在你的项目里哪一个才是业务上正确的数量？只能选：附表正确 / 主表正确 / 按条件区分 / 无法判断。<br>· 你们项目里「当前波次 / 后续波次」实际按什么条件划分？（本工具只认「Spec 被明确标为后续波次」这一条判据）<br>· 本次 Certification 给出了「与主表不一致 / 附表校验未全部通过 / J33 只适用特定组合」的提示。这些提示你看得懂吗？会影响你使用这个结果吗？<br>· 结果里的 MEPA 每 Phase 恒为 36、HW PA 恒为 4：在你的真实项目里成立吗？<br>· 本工具默认 Risk Reserve = 0%（源表没有已确认比例）。你的项目实际会另加预留吗？比例按什么算？<br>· 这次的输出看得懂吗？字段够你判断吗？（缺什么直接写在下面 Comment） | ORI-02、ORI-02b、ORI-03、ORI-07、ORI-10 | ORI-01、ORI-02a、ORI-04、ORI-05、ORI-06、ORI-08、ORI-09、ORI-11、ORI-12、ORI-13、ORI-14、ORI-15、ORI-16、ORI-17 |
| C2 | · Green / SIT @ SKU3：本工具采用附表 6.0，主表推算为 9.0（差 -3.0）。在你的项目里哪一个才是业务上正确的数量？只能选：附表正确 / 主表正确 / 按条件区分 / 无法判断。<br>· RF Certification / SIT @ SKU3：本工具采用附表 9.0，主表推算为 15.0（差 -6.0）。在你的项目里哪一个才是业务上正确的数量？只能选：附表正确 / 主表正确 / 按条件区分 / 无法判断。<br>· 你们项目里「当前波次 / 后续波次」实际按什么条件划分？（本工具只认「Spec 被明确标为后续波次」这一条判据）<br>· 本次 Certification 给出了「与主表不一致 / 附表校验未全部通过 / J33 只适用特定组合」的提示。这些提示你看得懂吗？会影响你使用这个结果吗？<br>· 结果里的 MEPA 每 Phase 恒为 36、HW PA 恒为 4：在你的真实项目里成立吗？<br>· 本工具默认 Risk Reserve = 0%（源表没有已确认比例）。你的项目实际会另加预留吗？比例按什么算？<br>· 这次的输出看得懂吗？字段够你判断吗？（缺什么直接写在下面 Comment） | ORI-02、ORI-02b、ORI-03、ORI-07、ORI-10、ORI-15 | ORI-01、ORI-02a、ORI-04、ORI-05、ORI-06、ORI-08、ORI-09、ORI-11、ORI-12、ORI-13、ORI-14、ORI-16、ORI-17 |
| C3 | · RF Certification / SIT @ SKU4：本工具采用附表 10.0，主表推算为 15.0（差 -5.0）。在你的项目里哪一个才是业务上正确的数量？只能选：附表正确 / 主表正确 / 按条件区分 / 无法判断。<br>· 你们项目里「当前波次 / 后续波次」实际按什么条件划分？（本工具只认「Spec 被明确标为后续波次」这一条判据）<br>· 本次 Certification 给出了「与主表不一致 / 附表校验未全部通过 / J33 只适用特定组合」的提示。这些提示你看得懂吗？会影响你使用这个结果吗？<br>· 本项目有多个 Panel Spec。源表 D2:H2 上的「N*panel」批注，在你的业务里到底指什么？（本工具不猜，只做记录）<br>· 结果里的 MEPA 每 Phase 恒为 36、HW PA 恒为 4：在你的真实项目里成立吗？<br>· 本工具默认 Risk Reserve = 0%（源表没有已确认比例）。你的项目实际会另加预留吗？比例按什么算？<br>· 这次的输出看得懂吗？字段够你判断吗？（缺什么直接写在下面 Comment） | ORI-01、ORI-02、ORI-02b、ORI-03、ORI-07、ORI-10 | ORI-02a、ORI-04、ORI-05、ORI-06、ORI-08、ORI-09、ORI-11、ORI-12、ORI-13、ORI-14、ORI-15、ORI-16、ORI-17 |
| C4 | · RF Certification / SIT @ SKU4：本工具采用附表 10.0，主表推算为 15.0（差 -5.0）。在你的项目里哪一个才是业务上正确的数量？只能选：附表正确 / 主表正确 / 按条件区分 / 无法判断。<br>· RF Certification / SIT @ SKU5：本工具采用附表 10.0，主表推算为 15.0（差 -5.0）。在你的项目里哪一个才是业务上正确的数量？只能选：附表正确 / 主表正确 / 按条件区分 / 无法判断。<br>· 工具给出了 4-5 SKU 的范围、没有替你选一档。这个范围在你的真实项目里能接受吗？如果不能，你实际靠什么条件判定它是 4 还是 5？<br>· 你们项目里「当前波次 / 后续波次」实际按什么条件划分？（本工具只认「Spec 被明确标为后续波次」这一条判据）<br>· 本次 Certification 给出了「与主表不一致 / 附表校验未全部通过 / J33 只适用特定组合」的提示。这些提示你看得懂吗？会影响你使用这个结果吗？<br>· 本项目有多个 Panel Spec。源表 D2:H2 上的「N*panel」批注，在你的业务里到底指什么？（本工具不猜，只做记录）<br>· 结果里的 MEPA 每 Phase 恒为 36、HW PA 恒为 4：在你的真实项目里成立吗？<br>· 本工具默认 Risk Reserve = 0%（源表没有已确认比例）。你的项目实际会另加预留吗？比例按什么算？<br>· 这次的输出看得懂吗？字段够你判断吗？（缺什么直接写在下面 Comment） | ORI-01、ORI-02、ORI-02b、ORI-03、ORI-04、ORI-07、ORI-08、ORI-10 | ORI-02a、ORI-05、ORI-06、ORI-09、ORI-11、ORI-12、ORI-13、ORI-14、ORI-15、ORI-16、ORI-17 |
| C5 | · RF Certification / SIT @ SKU4：本工具采用附表 10.0，主表推算为 15.0（差 -5.0）。在你的项目里哪一个才是业务上正确的数量？只能选：附表正确 / 主表正确 / 按条件区分 / 无法判断。<br>· RF Certification / SIT @ SKU5：本工具采用附表 10.0，主表推算为 15.0（差 -5.0）。在你的项目里哪一个才是业务上正确的数量？只能选：附表正确 / 主表正确 / 按条件区分 / 无法判断。<br>· RF Certification / SIT @ SKU6：本工具采用附表 10.0，主表推算为 15.0（差 -5.0）。在你的项目里哪一个才是业务上正确的数量？只能选：附表正确 / 主表正确 / 按条件区分 / 无法判断。<br>· Safety / FVT @ SKU6：本工具采用附表 10.0，主表推算为 9.6（差 0.4）。在你的项目里哪一个才是业务上正确的数量？只能选：附表正确 / 主表正确 / 按条件区分 / 无法判断。<br>· 工具给出了 4-5 SKU 的范围、没有替你选一档。这个范围在你的真实项目里能接受吗？如果不能，你实际靠什么条件判定它是 4 还是 5？<br>· 你们项目里「当前波次 / 后续波次」实际按什么条件划分？（本工具只认「Spec 被明确标为后续波次」这一条判据）<br>· 本次 Certification 给出了「与主表不一致 / 附表校验未全部通过 / J33 只适用特定组合」的提示。这些提示你看得懂吗？会影响你使用这个结果吗？<br>· 本项目有多个 Panel Spec。源表 D2:H2 上的「N*panel」批注，在你的业务里到底指什么？（本工具不猜，只做记录）<br>· 结果里的 MEPA 每 Phase 恒为 36、HW PA 恒为 4：在你的真实项目里成立吗？<br>· 本工具默认 Risk Reserve = 0%（源表没有已确认比例）。你的项目实际会另加预留吗？比例按什么算？<br>· 这次的输出看得懂吗？字段够你判断吗？（缺什么直接写在下面 Comment） | ORI-01、ORI-02、ORI-02b、ORI-03、ORI-04、ORI-07、ORI-08、ORI-10、ORI-16 | ORI-02a、ORI-05、ORI-06、ORI-09、ORI-11、ORI-12、ORI-13、ORI-14、ORI-15、ORI-17 |

## 4. 为什么是这五个案例

7 个主表/附表仍然不一致的格子分布在特定 SKU 数上，试用项目没跑到的 SKU 数，就永远拿不到那格的证据：

| 差异格 | 需要的 SKU 数 | 由哪个案例覆盖 |
|---|---|---|
| Green / SIT @ SKU3 | 3 | C2 |
| RF Certification / SIT @ SKU2 | 2 | C1 |
| RF Certification / SIT @ SKU3 | 3 | C2 |
| RF Certification / SIT @ SKU4 | 4 | C3、C4、C5 |
| RF Certification / SIT @ SKU5 | 5 | C4、C5 |
| RF Certification / SIT @ SKU6 | 6 | C5 |
| Safety / FVT @ SKU6 | 6 | C5 |

- 本清单覆盖 7/7 格。

## 5. 怎么用

**推荐（网页内置试用模式）**：
1. 双击 `web\index.html` →「参加团队试用」；
2. 选一个案例 → 载入（项目名、Key Factors、Wave 自动填好并锁定）；
3. 运行分析 → 看结果 → 只回答本案例涉及的问题 → 填姓名与日期；
4. 点「导出试用提交件」，得到 `trial-submission-<项目>-<时间>.json`；
5. 把这个文件放进 `feedback_inbox\`，然后 `python tools\collect_trial_feedback.py`。

**备用（不用网页）**：
1. 新建分析，Project Name 逐字复制上表，Key Factors 按上表输入；C5 另外把 cpu 第 5 条、panel 第 3 条的 Wave 选「后续波次」；
2. 运行分析 → 导出 JSON + 试用反馈表；
3. 填好反馈表的署名、日期与每一行答复，把反馈表和分析 JSON 一起复制到 `feedback_inbox\`（`trial_kit\forms\` 里的空白表不要就地填写）。

> 案例配置来自 CleanSheet 自己的 SKU 定义（C79:C83）。如果试用者手上有同类型的真实项目，请用真实项目的 Key Factors 跑同一条案例，并在 Comment 里写真实项目名——本清单只保证覆盖面，不替代真实项目。
