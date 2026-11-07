# Free-text signal inventory (Purpose/Explanation, Remark, Status)

Total non-empty text lines mined from columns I/J/K of rows 3-44: **126**


## HW

- `[Status]` OK
- `[Purpose]` Power测试*1/phase; (HQ:EE noise 是Power RD 自己测试，1unit/sku,)
- `[Purpose]` EE breakdown+issue debug*1by sku, 最高配sku*2unit,
- `[Purpose]` HDMI认证*3/phase (FVT 开始送测，如果FVT PASS(一般都能pass),SIT 无需再送测, base QS GPU）（HQ 是放在认证RD）
- `[Purpose]` TBT*2/Phase，FVT 测EV +SIT 测试FV.(HQ FV 是在sw team 做)
- `[Purpose]` Battery life  1 unit/ sku, Compal 是 3 units/phase.
- `[Purpose]` Option:
- `[Purpose]` Battery team 1*vendor*sku*phase for Q test for new source；
- `[Purpose]` For old source，Compal/HQ不需要样机。(LCFC SIT 1source *1units)
- `[Purpose]` CPU OC *2 &GPU OC ：
- `[Purpose]` LCFC:   CPU OC *2 &GPU OC *2  /phase .
- `[Purpose]` Compal:  CPU OC *2 &GPU OC *2  /phase .
- `[Purpose]` HQ: Leverage EE unit.
- `[Remark]` HDMI 样机是根据connector source定的.
- `[Remark]` 一般是3家source. Compal 样机是2unit/phase.
- `[Remark]` remark option 的部分，还没加到样机data里面。
- `[Remark]` PCIE*1 PCBA
- `[Remark]` USB3/2*1 PCBA
- `[Remark]` Crystal*1 PCBA
- `[Remark]` audio*1 PCBA
- `[Remark]` HW EE debug *4 PCBA
- `[Remark]` HW EA team test *1 PCBA
- `[Remark]` ITE KB debug *1 PCBA
- `[Remark]` VRAM tuning*7

## ME

- `[Purpose]` for debug*1 or 0台 to common with ME PA.

## THM

- `[Purpose]` LCFC:component  *1；skin*1；Acountic 1unit,thm capacity test*1
- `[Purpose]` thm module vendor debug*1.Fan vendor*1
- `[Purpose]` Dust shipment*1（L/T 1wk,can leverage vendor unit）
- `[Purpose]` Compal total 6unit for 1unit test in Acoustic team.
- `[Purpose]` HQ: total 6unit.
- `[Remark]` 其他配置给PCBA

## Audio

- `[Purpose]` MIC effect tuning*  1
- `[Purpose]` Audio Nahimic *1
- `[Purpose]` Scenic tuning* 1
- `[Purpose]` Resonance Test  /Sound Quality Test * 1-->2
- `[Purpose]` fianl : LCFC/HQ/Compal 都可按照4-5unit/phase.
- `[Purpose]` Option：
- `[Purpose]` Smart AMP: add 1 unit
- `[Remark]` 跟着platform 走，leading的样机相对多，
- `[Remark]` 其后项目适当减少,common driver.

## RF Test

- `[Purpose]` 天线调试+RD 自测+TDMS issue*1
- `[Purpose]` noise测试，conductive*1（RD 和3nd 实验室common）
- `[Purpose]` noise测试，air tput*1（RD 和3nd 实验室common）
- `[Purpose]` Pre-SAR/RSE(x1)*1
- `[Purpose]` fianl : LCFC/HQ/Compal 都可按照4-5unit/phase.

## EMC Test

- `[Status]` 待LCFC update
- `[Purpose]` Compal ：EMI/ESD/EMS測試機台6台，for 6 sku, 1unit/sku.
- `[Purpose]` HQ: 1 unit/sku;
- `[Purpose]` shengfei suggest: 1unit/sku, Add 2 additional backup units,and for leading,2-3 unit/sku.
- `[Remark]` 一台EMI,一台EMS.一台backup. 加PCBA*SKU*1PCS？

## SED

- `[Purpose]` base sku 搭配不同的panel.
- `[Purpose]` x-rite FVT *source,normal 1 /sku
- `[Purpose]` HDR cer.SIT*source,normal 1 /sku,
- `[Purpose]` Panel debug*2/phase （common with camera debug）
- `[Purpose]` Option:
- `[Purpose]` Camera win Hello cer. unit(for IR feature)
- `[Purpose]` OEM exception: 需要送测MS,  source *2-3 /FVT phase。(normal only FVT) vendor*1/FVT.此范畴适用于leading的项目，第一个送测的.
- `[Purpose]` PQL:大部分属于此范畴，只需要提供报告，无需送样机给MS, vendor*1 units/FVT phase.
- `[Purpose]` Dolby vision FVT *Cable 线，follow design（一般OLED 和IPS Cable不同，SDC和EDO OLED cable不同）,remove from G12.
- `[Purpose]` Panel related  new feature tuning: case by case.
- `[Purpose]` ESI test: LCFC need for source leading project need 2 unit.
- `[Purpose]` TP FW Tuning*3/ FVT. SIT no need.(for new source,MP source no need);
- `[Purpose]` X-rite-HDR 校色to 印度： source *1 unit/FVT Phase.sit no need.
- `[Remark]` 具体到Win Hello cer.跟着camera走，如果已经有其他项目送样了，可以不用再次送样。
- `[Remark]` 现在都是Panel HDR的.Dolby vision 是否一定需要了?跟team 去check? If no, 那么Dolby FVT 可以减少。--PM confirm delete it from G12.

## SS

- `[Status]` LCFC BIOS and SA 建议根据复杂度，4-6unit /phase.
- `[Status]` HQ 数量偏少
- `[Purpose]` BIOS*4/phase
- `[Purpose]` EC*1-- 2/Phase
- `[Purpose]` SA HLK*1/SKU
- `[Purpose]` SA *5/phase
- `[Purpose]` debug*2(compal 无此team和需求,but MS*4 &jump start*2 in SIT PHASE)
- `[Purpose]` Preload*1/SKU
- `[Purpose]` OS*1/phase
- `[Remark]` 各家ODM 数据gap挺大的，跟TPM gap也有，需要重点沟通。
- `[Remark]` Pre-load  BIOS Driver
- `[Remark]` 都跟KP 强相关，理论上会要求sku*1.
- `[Remark]` 可以根据平台成熟度协商.或者是否可以rework方式节省样机?
- `[Remark]` ODM BIOS *10
- `[Remark]` driver *10
- `[Remark]` OS*2
- `[Remark]` EC*5

## PD

- `[Purpose]` 1unit for debug
- `[Remark]` LNV+ODM PD total 1 unit

## SWPA

- `[Purpose]` follow PPA sample standard 1.0.
- `[Purpose]` SW PA 样机数量包含了HLK*1/sku +EE noise test*1/sku.
- `[Purpose]` 比如HQ EE noise是pwr RD 测试,Compal HLK是pre-load 测试，需要对应的function做相应的扣除和添加。

## MEPA

- `[Status]` LCFC:Confirmed ok as left data.
- `[Status]` HQ /Compal :to be clarify.
- `[Remark]` CS: 1 phase 36 units
- `[Remark]` PCB refresh: 1 phase 12-16units.

## HW PA

- `[Status]` HQ gap比较大
- `[Remark]` TTL3- 4unit one phase
- `[Remark]` test EE/THM

## EMC

- `[Purpose]` 认证*1/sku+全套的KP(只要SIT)

## Green

- `[Purpose]` 越南DN1 + 韩国DN 1台+ CEL*CPU value(EEcofirm)*2 + BCS 2台
- `[Purpose]` Option:
- `[Purpose]` EPEAT: 5unit. （主要做跌落测试，L/T2-3WK,HQ LOQ 是share 其他function 样机）
- `[Purpose]` Gaming pro系列项目不符合EPEAT2025的要求,还未做过。
- `[Purpose]` E-Star9.0 *1；
- `[Purpose]` UL golden*1 (Gaming performance and comfort)跟GPU5080以上
- `[Purpose]` eyesafe/LBL/HGPD Golden* N台 ,如果Panel数量为N，则样机数量为N
- `[Remark]` FVT for RD 内测,leverage safety.

## Safety

- `[Purpose]` FVT:CB 5台(battery source +1 自测)，UL4200A（纽扣电池） 1台-->0 (现在基本内置Batt)， BIS 1 台.
- `[Purpose]` Common charge 2 台，
- `[Purpose]` SIT:CCC 2 (1+CPU 核心数*1pcs)+ 韩国 1 + 内测 1
- `[Purpose]` NOM 1  + EAC 1(哈萨克斯坦1pcs maybe)
- `[Remark]` BIS: India catelog name *1pcs/SIT PHASE/BATTERY SPEC/ADP SPEC.
- `[Remark]` adapter rating label* battery rating label.

## RF Certification

- `[Purpose]` this data for 2 antenna source +2 wlan source refrence:
- `[Purpose]` 1.SRRC *2(PRC 型号核准);如果网卡数量大于天线数量，整机需求基于WLAN卡型号数量；
- `[Purpose]` 2.CE *4 =antenna *wlan（欧盟）,如果网卡数量大于天线数量，需额外提供网卡单体送测；
- `[Purpose]` 3.FCC(intel WLAN 数量*天线数量)*4（如果是C1PC ,就不需要整机）,其他wlan source(Non-intel) combine with CE.;
- `[Purpose]` 4.印尼* 2  .
- `[Purpose]` 5.Mexico *1.
- `[Purpose]` 6.资安*2（欧盟网络安全）

## BIOS

- `[Remark]` the data is for leading CS project.
- `[Remark]` Others less than this, case by case.

## ITE

- `[Purpose]` Total one phase on unit
- `[Remark]` if no lighting feature,no need

## NV

- `[Purpose]` 台北，印度，美国各2台  TTL 6pcs
- `[Remark]` the data is for leading CS project.
- `[Remark]` Others less than this, case by case.

## INTEL

- `[Purpose]` 6PCS

## MFG

- `[Purpose]` 红丹test
- `[Remark]` Total one phase on unit


---

# A. CONDITIONAL / OPTIONAL increments (non-normative by rule)  — 4 lines

- **HW** `[Purpose]` Option:
- **Audio** `[Purpose]` Option：
- **SED** `[Purpose]` Option:
- **Green** `[Purpose]` Option:


---

# B. ODM-differentiated statements (LCFC / HQ / Compal)  — 25 lines

- **HW** `[Purpose]` Power测试*1/phase; (HQ:EE noise 是Power RD 自己测试，1unit/sku,)
- **HW** `[Purpose]` HDMI认证*3/phase (FVT 开始送测，如果FVT PASS(一般都能pass),SIT 无需再送测, base QS GPU）（HQ 是放在认证RD）
- **HW** `[Purpose]` TBT*2/Phase，FVT 测EV +SIT 测试FV.(HQ FV 是在sw team 做)
- **HW** `[Purpose]` Battery life  1 unit/ sku, Compal 是 3 units/phase.
- **HW** `[Purpose]` For old source，Compal/HQ不需要样机。(LCFC SIT 1source *1units)
- **HW** `[Purpose]` LCFC:   CPU OC *2 &GPU OC *2  /phase .
- **HW** `[Purpose]` Compal:  CPU OC *2 &GPU OC *2  /phase .
- **HW** `[Purpose]` HQ: Leverage EE unit.
- **HW** `[Remark]` 一般是3家source. Compal 样机是2unit/phase.
- **THM** `[Purpose]` LCFC:component  *1；skin*1；Acountic 1unit,thm capacity test*1
- **THM** `[Purpose]` Compal total 6unit for 1unit test in Acoustic team.
- **THM** `[Purpose]` HQ: total 6unit.
- **Audio** `[Purpose]` fianl : LCFC/HQ/Compal 都可按照4-5unit/phase.
- **RF Test** `[Purpose]` fianl : LCFC/HQ/Compal 都可按照4-5unit/phase.
- **EMC Test** `[Status]` 待LCFC update
- **EMC Test** `[Purpose]` Compal ：EMI/ESD/EMS測試機台6台，for 6 sku, 1unit/sku.
- **EMC Test** `[Purpose]` HQ: 1 unit/sku;
- **SED** `[Purpose]` ESI test: LCFC need for source leading project need 2 unit.
- **SS** `[Status]` LCFC BIOS and SA 建议根据复杂度，4-6unit /phase.
- **SS** `[Status]` HQ 数量偏少
- **SWPA** `[Purpose]` 比如HQ EE noise是pwr RD 测试,Compal HLK是pre-load 测试，需要对应的function做相应的扣除和添加。
- **MEPA** `[Status]` LCFC:Confirmed ok as left data.
- **MEPA** `[Status]` HQ /Compal :to be clarify.
- **HW PA** `[Status]` HQ gap比较大
- **Green** `[Purpose]` EPEAT: 5unit. （主要做跌落测试，L/T2-3WK,HQ LOQ 是share 其他function 样机）


---

# C. UNCERTAINTY / case-by-case / leverage lexicon  — 19 lines

- **HW** `[Purpose]` Option:
- **HW** `[Purpose]` HQ: Leverage EE unit.
- **HW** `[Remark]` remark option 的部分，还没加到样机data里面。
- **THM** `[Purpose]` Dust shipment*1（L/T 1wk,can leverage vendor unit）
- **Audio** `[Purpose]` Option：
- **EMC Test** `[Status]` 待LCFC update
- **EMC Test** `[Purpose]` shengfei suggest: 1unit/sku, Add 2 additional backup units,and for leading,2-3 unit/sku.
- **SED** `[Purpose]` Option:
- **SED** `[Purpose]` Panel related  new feature tuning: case by case.
- **SED** `[Remark]` 现在都是Panel HDR的.Dolby vision 是否一定需要了?跟team 去check? If no, 那么Dolby FVT 可以减少。--PM confirm delete it from G12.
- **SS** `[Remark]` 各家ODM 数据gap挺大的，跟TPM gap也有，需要重点沟通。
- **SS** `[Remark]` 可以根据平台成熟度协商.或者是否可以rework方式节省样机?
- **MEPA** `[Status]` HQ /Compal :to be clarify.
- **HW PA** `[Status]` HQ gap比较大
- **Green** `[Purpose]` Option:
- **Green** `[Remark]` FVT for RD 内测,leverage safety.
- **Safety** `[Purpose]` NOM 1  + EAC 1(哈萨克斯坦1pcs maybe)
- **BIOS** `[Remark]` Others less than this, case by case.
- **NV** `[Remark]` Others less than this, case by case.


---

# D. Source-count driven demand statements (key-factor linkage)  — 26 lines

- **HW** `[Purpose]` HDMI认证*3/phase (FVT 开始送测，如果FVT PASS(一般都能pass),SIT 无需再送测, base QS GPU）（HQ 是放在认证RD）
- **HW** `[Purpose]` Battery team 1*vendor*sku*phase for Q test for new source；
- **HW** `[Purpose]` For old source，Compal/HQ不需要样机。(LCFC SIT 1source *1units)
- **HW** `[Purpose]` CPU OC *2 &GPU OC ：
- **HW** `[Purpose]` LCFC:   CPU OC *2 &GPU OC *2  /phase .
- **HW** `[Purpose]` Compal:  CPU OC *2 &GPU OC *2  /phase .
- **HW** `[Remark]` 一般是3家source. Compal 样机是2unit/phase.
- **THM** `[Purpose]` thm module vendor debug*1.Fan vendor*1
- **THM** `[Purpose]` Dust shipment*1（L/T 1wk,can leverage vendor unit）
- **SED** `[Purpose]` x-rite FVT *source,normal 1 /sku
- **SED** `[Purpose]` HDR cer.SIT*source,normal 1 /sku,
- **SED** `[Purpose]` Panel debug*2/phase （common with camera debug）
- **SED** `[Purpose]` OEM exception: 需要送测MS,  source *2-3 /FVT phase。(normal only FVT) vendor*1/FVT.此范畴适用于leading的项目，第一个送测的.
- **SED** `[Purpose]` PQL:大部分属于此范畴，只需要提供报告，无需送样机给MS, vendor*1 units/FVT phase.
- **SED** `[Purpose]` ESI test: LCFC need for source leading project need 2 unit.
- **SED** `[Purpose]` TP FW Tuning*3/ FVT. SIT no need.(for new source,MP source no need);
- **SED** `[Purpose]` X-rite-HDR 校色to 印度： source *1 unit/FVT Phase.sit no need.
- **SED** `[Remark]` 现在都是Panel HDR的.Dolby vision 是否一定需要了?跟team 去check? If no, 那么Dolby FVT 可以减少。--PM confirm delete it from G12.
- **Green** `[Purpose]` 越南DN1 + 韩国DN 1台+ CEL*CPU value(EEcofirm)*2 + BCS 2台
- **Green** `[Purpose]` UL golden*1 (Gaming performance and comfort)跟GPU5080以上
- **Safety** `[Purpose]` FVT:CB 5台(battery source +1 自测)，UL4200A（纽扣电池） 1台-->0 (现在基本内置Batt)， BIS 1 台.
- **Safety** `[Purpose]` SIT:CCC 2 (1+CPU 核心数*1pcs)+ 韩国 1 + 内测 1
- **RF Certification** `[Purpose]` this data for 2 antenna source +2 wlan source refrence:
- **RF Certification** `[Purpose]` 1.SRRC *2(PRC 型号核准);如果网卡数量大于天线数量，整机需求基于WLAN卡型号数量；
- **RF Certification** `[Purpose]` 2.CE *4 =antenna *wlan（欧盟）,如果网卡数量大于天线数量，需额外提供网卡单体送测；
- **RF Certification** `[Purpose]` 3.FCC(intel WLAN 数量*天线数量)*4（如果是C1PC ,就不需要整机）,其他wlan source(Non-intel) combine with CE.;


---

# E. Key-factor mention frequency across all mined text

- CPU: 5
- GPU: 5
- Panel/panel: 5
- SSD: 0
- Mem/memory: 0
- source: 13
- antenna: 2
- wlan: 3
- camera: 2
- vendor: 5
- battery: 2


# F. PCBA / non-unit demand units observed

- PCBA, phase, unit, units, 台