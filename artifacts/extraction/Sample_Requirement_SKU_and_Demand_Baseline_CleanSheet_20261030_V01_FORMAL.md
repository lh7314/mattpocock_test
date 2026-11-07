# Workbook dump — `original_documents\Sample_Requirement_SKU_and_Demand_Baseline_CleanSheet_20261030_V01_FORMAL.xlsx`

- SHA-256: `48a360ff2ffd086e41d6b90a916f64fe52d9bc13efba07b8377b2945c846ab5a`
- creator: William HC | last_modified_by: Lingyu LY3 Rong
- created: 2015-06-05T18:19:34+00:00 | modified: 2026-10-30T08:51:32+00:00
- defined names: []

## Sheet `CS ODM sample `  (state=visible, dims=A1:L95, nonempty cells=515)
- autofilter: A2:K49 | freeze: C35
- hidden rows: [] | hidden cols: []
- merged (91): I35:I44=None, B43:B44='MFG', J9:J10='MIC effect tuning*  1 \n Audio Nahimic *1\nScenic tuning* 1 \nResonance Test  /Sound Quality Test * 1-->2\nfianl : LCFC/HQ/Compal 都可按照4-5unit/phase.\nOption：\nSmart AMP: add 1 unit\n', B61:B62='TTL SUM/phase', J11:J12='天线调试+RD 自测+TDMS issue*1\nnoise测试，conductive*1（RD 和3nd 实验室common）\nnoise测试，air tput*1（RD 和3nd 实验室common）\nPre-SAR/RSE(x1)*1\nfianl : LCFC/HQ/Compal 都可按照4-5unit/phase. \n', B29:B30='Green', B23:B24='MEPA', K27:K28=None, B13:B14='EMC Test', I3:I4='OK', I17:I18='LCFC BIOS and SA 建议根据复杂度，4-6unit /phase.\nHQ 数量偏少', B37:B38='ITE', B15:B16='SED', K43:K44='Total one phase on unit', J31:J32='FVT:CB 5台(battery source +1 自测)，UL4200A（纽扣电池） 1台-->0 (现在基本内置Batt)， BIS 1 台.\nCommon charge 2 台，\nSIT:CCC 2 (1+CPU 核心数*1pcs)+ 韩国 1 + 内测 1\nNOM 1  + EAC 1(哈萨克斯坦1pcs maybe)', A27:A34='Certification', K9:K10='跟着platform 走，leading的样机相对多，\n其后项目适当减少,common driver.', C81:J81='4SKU:2-4*CPU +2-3*GPU+ 2*Panel spec  +SSD SPEC*2 +Mem spec *2                                                                                                                Pro/LOQ /Y5', J21:J26='follow PPA sample standard 1.0.\nSW PA 样机数量包含了HLK*1/sku +EE noise test*1/sku.\n比如HQ EE noise是pwr RD 测试,Compal HLK是pre-load 测试，需要对应的function做相应的扣除和添加。', B25:B26='HW PA', K37:K38='if no lighting feature,no need', K15:K16='具体到Win Hello cer.跟着camera走，如果已经有其他项目送样了，可以不用再次送样。\n现在都是Panel HDR的.Dolby vision 是否一定需要了?跟team 去check? If no, 那么Dolby FVT 可以减少。--PM confirm delete it from G12.', K29:K30='FVT for RD 内测,leverage safety.', B35:B36='BIOS', I28:I34=None, B27:B28='EMC', A35:A42='3rd Party Vendor', A3:A20='RD', B3:B4='HW', B17:B18='SS', B11:B12='RF Test', C79:J79='2SKU: 1-2*CPU +1*GPU+ 1-2*Panel +SSD SPEC*1 +Mem spec *1     VRAM match MB1 1-2 Source/X9/X11.                                                  N1x/Y9 source少，Volume 少', J27:J28='认证*1/sku+全套的KP(只要SIT)', J35:J36=None, K17:K18='各家ODM 数据gap挺大的，跟TPM gap也有，需要重点沟通。\nPre-load  BIOS Driver \n都跟KP 强相关，理论上会要求sku*1.\n可以根据平台成熟度协商.或者是否可以rework方式节省样机?\nODM BIOS *10 \n           driver *10\n        OS*2\n         EC*5\n     ', A21:A26='PA', I19:I20=None, K19:K20='LNV+ODM PD total 1 unit', B45:B46='SUM/sku', A43:A44='MFG', I9:I10=None, K3:K4='HDMI 样机是根据connector source定的.\n一般是3家source. Compal 样机是2unit/phase.\nremark option 的部分，还没加到样机data里面。\nPCIE*1 PCBA\nUSB3/2*1 PCBA\nCrystal*1 PCBA\naudio*1 PCBA\nHW EE debug *4 PCBA\nHW EA team test *1 PCBA\nITE KB debug *1 PCBA\nVRAM tuning*7', B7:B8='THM', I11:I12=None, J39:J40='台北，印度，美国各2台  TTL 6pcs ', K5:K6=None, B31:B32='Safety', A1:K1='CleanSheet Project By Senario/By SKU Qty Breakdown', K11:K12=None, K31:K32='BIS: India catelog name *1pcs/SIT PHASE/BATTERY SPEC/ADP SPEC.\nadapter rating label* battery rating label.', B68:B69='SWPA', B9:B10='Audio', B33:B34='RF Certification', J3:J4='Power测试*1/phase; (HQ:EE noise 是Power RD 自己测试，1unit/sku,)\nEE breakdown+issue debug*1by sku, 最高配sku*2unit,\nHDMI认证*3/phase (FVT 开始送测，如果FVT PASS(一般都能pass),SIT 无需再送测, base QS GPU）（HQ 是放在认证RD）\nTBT*2/Phase，FVT 测EV +SIT 测试FV.(HQ FV 是在sw team 做)\nBattery life  1 unit/ sku, Compal 是 3 units/phase.\nOption:\nBattery team 1*vendor*sku*phase for Q test for new source；\nFor old source，Compal/HQ不需要样机。(LCFC SIT 1source *1units)\nCPU OC *2 &GPU OC ：\n    LCFC:   CPU OC *2 &GPU OC *2  /phase .\nCompal:  CPU OC *2 &GPU OC *2  /phase .\n        HQ: Leverage EE unit.\n', I23:I24='LCFC:Confirmed ok as left data. \nHQ /Compal :to be clarify. ', J43:J44='红丹test', C82:J82='5SKU :3-4*CPU +3*GPU+ 2*Panel spec  +SSD SPEC*2 +Mem spec *2                                                                                                                   Pro/LOQ /Y5            ', J5:J6='for debug*1 or 0台 to common with ME PA.', J33:J34='this data for 2 antenna source +2 wlan source refrence:\n1.SRRC *2(PRC 型号核准);如果网卡数量大于天线数量，整机需求基于WLAN卡型号数量；\n2.CE *4 =antenna *wlan（欧盟）,如果网卡数量大于天线数量，需额外提供网卡单体送测；\n3.FCC(intel WLAN 数量*天线数量)*4（如果是C1PC ,就不需要整机）,其他wlan source(Non-intel) combine with CE.;\n4.印尼* 2  .\n5.Mexico *1.\n6.资安*2（欧盟网络安全）\n', J29:J30='越南DN1 + 韩国DN 1台+ CEL*CPU value(EEcofirm)*2 + BCS 2台\nOption:\nEPEAT: 5unit. （主要做跌落测试，L/T2-3WK,HQ LOQ 是share 其他function 样机）\n Gaming pro系列项目不符合EPEAT2025的要求,还未做过。\nE-Star9.0 *1；\nUL golden*1 (Gaming performance and comfort)跟GPU5080以上\neyesafe/LBL/HGPD Golden* N台 ,如果Panel数量为N，则样机数量为N\n', B72:B73='HW PA', B21:B22='SWPA', J13:J14='Compal ：EMI/ESD/EMS測試機台6台，for 6 sku, 1unit/sku.\nHQ: 1 unit/sku;\nshengfei suggest: 1unit/sku, Add 2 additional backup units,and for leading,2-3 unit/sku.', C83:J83='6SKU::4-5*CPU +3*GPU+ 2-3*Panel spec  +SSD SPEC*2 +Mem spec *2-3                                                                                                            ID./ME*2 ，Pro上', K33:K34=None, K21:K22=None, B70:B71='MEPA', J37:J38='Total one phase on unit', J15:J16='base sku 搭配不同的panel.\nx-rite FVT *source,normal 1 /sku\nHDR cer.SIT*source,normal 1 /sku, \nPanel debug*2/phase （common with camera debug）\nOption:\nCamera win Hello cer. unit(for IR feature)\nOEM exception: 需要送测MS,  source *2-3 /FVT phase。(normal only FVT) vendor*1/FVT.此范畴适用于leading的项目，第一个送测的.\nPQL:大部分属于此范畴，只需要提供报告，无需送样机给MS, vendor*1 units/FVT phase.\nDolby vision FVT *Cable 线，follow design（一般OLED 和IPS Cable不同，SDC和EDO OLED cable不同）,remove from G12.\nPanel related  new feature tuning: case by case.\nESI test: LCFC need for source leading project need 2 unit.\nTP FW Tuning*3/ FVT. SIT no need.(for new source,MP source no need);\nX-rite-HDR 校色to 印度： source *1 unit/FVT Phase.sit no need.', K35:K36='the data is for leading CS project. \nOthers less than this, case by case.', B39:B40='NV', B48:B49='TTL SUM/phase', I25:I26='HQ gap比较大', I21:I22=None, J7:J8='LCFC:component  *1；skin*1；Acountic 1unit,thm capacity test*1\nthm module vendor debug*1.Fan vendor*1\nDust shipment*1（L/T 1wk,can leverage vendor unit）\nCompal total 6unit for 1unit test in Acoustic team.\nHQ: total 6unit.', C80:J80='3SKU:2-3*CPU +2*GPU+ 1*Panel spec  +SSD SPEC*1 +Mem spec *1(or SSD/Mem spec *2, arrange  2nd wave)                                             Y7  DIS ', B19:B20='PD', A2:B2='Function', K23:K24='CS: 1 phase 36 units\nPCB refresh: 1 phase 12-16units.', B74:B75='TTL SUM/phase', I13:I14='待LCFC update', K39:K42='the data is for leading CS project. \nOthers less than this, case by case.', K13:K14='一台EMI,一台EMS.一台backup. 加PCBA*SKU*1PCS？', J41:J42='6PCS', K7:K8='其他配置给PCBA', B5:B6='ME', J52:J62='Flicker Free，TUV EyeSafe，Low Blue Light  can leverage sample unit,1panel*1 unit;\nHigh gaming performance*1panel*1 unit. \nrefer to G10 G12 LCFC data: WW certification including promition: range 34--36 units.\n Certification 每个场景下的样机不一样，主要差异在EMC, 因为EMC 的样机是by sku的，需要cover所有KP.\nFor PRC only project: need xx units for CCC. X units For SRRC.', J17:J18='BIOS*4/phase\nEC*1-- 2/Phase\nSA HLK*1/SKU\nSA *5/phase \ndebug*2(compal 无此team和需求,but MS*4 &jump start*2 in SIT PHASE)\nPreload*1/SKU\nOS*1/phase \n', K25:K26='TTL3- 4unit one phase\ntest EE/THM', B41:B42='INTEL', J19:J20='1unit for debug'

| Ref | Raw / Formula | Cached | Fmt | State |
|---|---|---|---|---|
| A1 | CleanSheet Project By Senario/By SKU Qty Breakdown | CleanSheet Project By Senario/By SKU Qty Breakdown | General |  |
| A2 | Function | Function | General |  |
| C2 | Phase | Phase | General |  |
| D2 |  SKU*2 |  SKU*2 | General |  |
| E2 |  SKU*3 |  SKU*3 | General |  |
| F2 |  SKU*4 |  SKU*4 | General |  |
| G2 |  SKU*5  |  SKU*5  | General |  |
| H2 |  SKU*6 |  SKU*6 | General |  |
| I2 | Status | Status | General |  |
| J2 | Purpose and Explanation | Purpose and Explanation | General |  |
| K2 | Remark | Remark | General |  |
| A3 | RD | RD | General |  |
| B3 | HW | HW | General |  |
| C3 | FVT | FVT | General |  |
| D3 | 6 | 6 | General |  |
| E3 | 4.3 | 4.3 | General |  |
| F3 | 3.5 | 3.5 | General |  |
| G3 | 3 | 3 | General |  |
| H3 | 2.7 | 2.7 | General |  |
| I3 | OK | OK | General |  |
| J3 | Power测试*1/phase; (HQ:EE noise 是Power RD 自己测试，1unit/sku,) ⏎ EE breakdown+issue debug*1by sku, 最高配sku*2unit, ⏎ HDMI认证*3/phase (FVT 开始送测，如果FVT PASS(一般都能pass),SIT 无需再送测, base QS GPU）（HQ 是放在认证RD） ⏎ TBT*2/Phase，FVT 测EV +SIT 测试FV.(HQ FV 是在sw team 做) ⏎ Battery life  1 unit/ sku, Compal 是 3 units/phase. ⏎ Option: ⏎ Battery team 1*vendor*sku*phase for Q test for new source； ⏎ For old source，Compal/HQ不需要样机。(LCFC SIT 1source *1units) ⏎ CPU OC *2 &GPU OC ： ⏎     LCFC:   CPU OC *2 &GPU OC *2  /phase . ⏎ Compal:  CPU OC *2 &GPU OC *2  /phase . ⏎         HQ: Leverage EE unit. ⏎  | Power测试*1/phase; (HQ:EE noise 是Power RD 自己测试，1unit/sku,) ⏎ EE breakdown+issue debug*1by sku, 最高配sku*2unit, ⏎ HDMI认证*3/phase (FVT 开始送测，如果FVT PASS(一般都能pass),SIT 无需再送测, base QS GPU）（HQ 是放在认证RD） ⏎ TBT*2/Phase，FVT 测EV +SIT 测试FV.(HQ FV 是在sw team 做) ⏎ Battery life  1 unit/ sku, Compal 是 3 units/phase. ⏎ Option: ⏎ Battery team 1*vendor*sku*phase for Q test for new source； ⏎ For old source，Compal/HQ不需要样机。(LCFC SIT 1source *1units) ⏎ CPU OC *2 &GPU OC ： ⏎     LCFC:   CPU OC *2 &GPU OC *2  /phase . ⏎ Compal:  CPU OC *2 &GPU OC *2  /phase . ⏎         HQ: Leverage EE unit. ⏎  | General |  |
| K3 | HDMI 样机是根据connector source定的. ⏎ 一般是3家source. Compal 样机是2unit/phase. ⏎ remark option 的部分，还没加到样机data里面。 ⏎ PCIE*1 PCBA ⏎ USB3/2*1 PCBA ⏎ Crystal*1 PCBA ⏎ audio*1 PCBA ⏎ HW EE debug *4 PCBA ⏎ HW EA team test *1 PCBA ⏎ ITE KB debug *1 PCBA ⏎ VRAM tuning*7 | HDMI 样机是根据connector source定的. ⏎ 一般是3家source. Compal 样机是2unit/phase. ⏎ remark option 的部分，还没加到样机data里面。 ⏎ PCIE*1 PCBA ⏎ USB3/2*1 PCBA ⏎ Crystal*1 PCBA ⏎ audio*1 PCBA ⏎ HW EE debug *4 PCBA ⏎ HW EA team test *1 PCBA ⏎ ITE KB debug *1 PCBA ⏎ VRAM tuning*7 | General |  |
| C4 | SIT | SIT | General |  |
| D4 | 6 | 6 | General |  |
| E4 | 4.3 | 4.3 | General |  |
| F4 | 3.5 | 3.5 | General |  |
| G4 | 3 | 3 | General |  |
| H4 | 2.7 | 2.7 | General |  |
| B5 | ME | ME | General |  |
| C5 | FVT | FVT | General |  |
| D5 | 0.5 | 0.5 | General |  |
| E5 | 0.3 | 0.3 | General |  |
| F5 | 0.25 | 0.25 | General |  |
| G5 | 0.2 | 0.2 | General |  |
| H5 | 0.2 | 0.2 | General |  |
| J5 | for debug*1 or 0台 to common with ME PA. | for debug*1 or 0台 to common with ME PA. | General |  |
| C6 | SIT | SIT | General |  |
| D6 | 0.5 | 0.5 | General |  |
| E6 | 0.3 | 0.3 | General |  |
| F6 | 0.25 | 0.25 | General |  |
| G6 | 0.2 | 0.2 | General |  |
| H6 | 0.2 | 0.2 | General |  |
| B7 | THM | THM | General |  |
| C7 | FVT | FVT | General |  |
| D7 | 3.5 | 3.5 | General |  |
| E7 | 2.3 | 2.3 | General |  |
| F7 | 1.8 | 1.8 | General |  |
| G7 | 1.4 | 1.4 | General |  |
| H7 | 1.2 | 1.2 | General |  |
| J7 | LCFC:component  *1；skin*1；Acountic 1unit,thm capacity test*1 ⏎ thm module vendor debug*1.Fan vendor*1 ⏎ Dust shipment*1（L/T 1wk,can leverage vendor unit） ⏎ Compal total 6unit for 1unit test in Acoustic team. ⏎ HQ: total 6unit. | LCFC:component  *1；skin*1；Acountic 1unit,thm capacity test*1 ⏎ thm module vendor debug*1.Fan vendor*1 ⏎ Dust shipment*1（L/T 1wk,can leverage vendor unit） ⏎ Compal total 6unit for 1unit test in Acoustic team. ⏎ HQ: total 6unit. | General |  |
| K7 | 其他配置给PCBA | 其他配置给PCBA | General |  |
| C8 | SIT | SIT | General |  |
| D8 | 3.5 | 3.5 | General |  |
| E8 | 2.3 | 2.3 | General |  |
| F8 | 1.8 | 1.8 | General |  |
| G8 | 1.4 | 1.4 | General |  |
| H8 | 1.2 | 1.2 | General |  |
| I8 | ok | ok | General |  |
| B9 | Audio | Audio | General |  |
| C9 | FVT | FVT | General |  |
| D9 | 2 | 2 | General |  |
| E9 | 1 | 1 | General |  |
| F9 | 1 | 1 | General |  |
| G9 | 0.8 | 0.8 | General |  |
| H9 | 0.6 | 0.6 | General |  |
| J9 | MIC effect tuning*  1  ⏎  Audio Nahimic *1 ⏎ Scenic tuning* 1  ⏎ Resonance Test  /Sound Quality Test * 1-->2 ⏎ fianl : LCFC/HQ/Compal 都可按照4-5unit/phase. ⏎ Option： ⏎ Smart AMP: add 1 unit ⏎  | MIC effect tuning*  1  ⏎  Audio Nahimic *1 ⏎ Scenic tuning* 1  ⏎ Resonance Test  /Sound Quality Test * 1-->2 ⏎ fianl : LCFC/HQ/Compal 都可按照4-5unit/phase. ⏎ Option： ⏎ Smart AMP: add 1 unit ⏎  | General |  |
| K9 | 跟着platform 走，leading的样机相对多， ⏎ 其后项目适当减少,common driver. | 跟着platform 走，leading的样机相对多， ⏎ 其后项目适当减少,common driver. | General |  |
| C10 | SIT | SIT | General |  |
| D10 | 2 | 2 | General |  |
| E10 | 1 | 1 | General |  |
| F10 | 1 | 1 | General |  |
| G10 | 0.8 | 0.8 | General |  |
| H10 | 0.6 | 0.6 | General |  |
| B11 | RF Test | RF Test | General |  |
| C11 | FVT | FVT | General |  |
| D11 | 2.5 | 2.5 | General |  |
| E11 | 1.7 | 1.7 | General |  |
| F11 | 1.3 | 1.3 | General |  |
| G11 | 1 | 1 | General |  |
| H11 | 0.8 | 0.8 | General |  |
| J11 | 天线调试+RD 自测+TDMS issue*1 ⏎ noise测试，conductive*1（RD 和3nd 实验室common） ⏎ noise测试，air tput*1（RD 和3nd 实验室common） ⏎ Pre-SAR/RSE(x1)*1 ⏎ fianl : LCFC/HQ/Compal 都可按照4-5unit/phase.  ⏎  | 天线调试+RD 自测+TDMS issue*1 ⏎ noise测试，conductive*1（RD 和3nd 实验室common） ⏎ noise测试，air tput*1（RD 和3nd 实验室common） ⏎ Pre-SAR/RSE(x1)*1 ⏎ fianl : LCFC/HQ/Compal 都可按照4-5unit/phase.  ⏎  | General |  |
| C12 | SIT | SIT | General |  |
| D12 | 2.5 | 2.5 | General |  |
| E12 | 1.7 | 1.7 | General |  |
| F12 | 1.3 | 1.3 | General |  |
| G12 | 1 | 1 | General |  |
| H12 | 0.8 | 0.8 | General |  |
| B13 | EMC Test | EMC Test | General |  |
| C13 | FVT | FVT | General |  |
| D13 | 3 | 3 | General |  |
| E13 | 2 | 2 | General |  |
| F13 | 1.5 | 1.5 | General |  |
| G13 | 1.2 | 1.2 | General |  |
| H13 | 1 | 1 | General |  |
| I13 | 待LCFC update | 待LCFC update | General |  |
| J13 | Compal ：EMI/ESD/EMS測試機台6台，for 6 sku, 1unit/sku. ⏎ HQ: 1 unit/sku; ⏎ shengfei suggest: 1unit/sku, Add 2 additional backup units,and for leading,2-3 unit/sku. | Compal ：EMI/ESD/EMS測試機台6台，for 6 sku, 1unit/sku. ⏎ HQ: 1 unit/sku; ⏎ shengfei suggest: 1unit/sku, Add 2 additional backup units,and for leading,2-3 unit/sku. | General |  |
| K13 | 一台EMI,一台EMS.一台backup. 加PCBA*SKU*1PCS？ | 一台EMI,一台EMS.一台backup. 加PCBA*SKU*1PCS？ | General |  |
| C14 | SIT | SIT | General |  |
| D14 | 3 | 3 | General |  |
| E14 | 2 | 2 | General |  |
| F14 | 1.5 | 1.5 | General |  |
| G14 | 1.2 | 1.2 | General |  |
| H14 | 1 | 1 | General |  |
| B15 | SED | SED | General |  |
| C15 | FVT | FVT | General |  |
| D15 | 2 | 2 | General |  |
| E15 | 1.7 | 1.7 | General |  |
| F15 | 1.5 | 1.5 | General |  |
| G15 | 1.4 | 1.4 | General |  |
| H15 | 1.3 | 1.3 | General |  |
| J15 | base sku 搭配不同的panel. ⏎ x-rite FVT *source,normal 1 /sku ⏎ HDR cer.SIT*source,normal 1 /sku,  ⏎ Panel debug*2/phase （common with camera debug） ⏎ Option: ⏎ Camera win Hello cer. unit(for IR feature) ⏎ OEM exception: 需要送测MS,  source *2-3 /FVT phase。(normal only FVT) vendor*1/FVT.此范畴适用于leading的项目，第一个送测的. ⏎ PQL:大部分属于此范畴，只需要提供报告，无需送样机给MS, vendor*1 units/FVT phase. ⏎ Dolby vision FVT *Cable 线，follow design（一般OLED 和IPS Cable不同，SDC和EDO OLED cable不同）,remove from G12. ⏎ Panel related  new feature tuning: case by case. ⏎ ESI test: LCFC need for source leading project need 2 unit. ⏎ TP FW Tuning*3/ FVT. SIT no need.(for new source,MP source no need); ⏎ X-rite-HDR 校色to 印度： source *1 unit/FVT Phase.sit no need. | base sku 搭配不同的panel. ⏎ x-rite FVT *source,normal 1 /sku ⏎ HDR cer.SIT*source,normal 1 /sku,  ⏎ Panel debug*2/phase （common with camera debug） ⏎ Option: ⏎ Camera win Hello cer. unit(for IR feature) ⏎ OEM exception: 需要送测MS,  source *2-3 /FVT phase。(normal only FVT) vendor*1/FVT.此范畴适用于leading的项目，第一个送测的. ⏎ PQL:大部分属于此范畴，只需要提供报告，无需送样机给MS, vendor*1 units/FVT phase. ⏎ Dolby vision FVT *Cable 线，follow design（一般OLED 和IPS Cable不同，SDC和EDO OLED cable不同）,remove from G12. ⏎ Panel related  new feature tuning: case by case. ⏎ ESI test: LCFC need for source leading project need 2 unit. ⏎ TP FW Tuning*3/ FVT. SIT no need.(for new source,MP source no need); ⏎ X-rite-HDR 校色to 印度： source *1 unit/FVT Phase.sit no need. | General |  |
| K15 | 具体到Win Hello cer.跟着camera走，如果已经有其他项目送样了，可以不用再次送样。 ⏎ 现在都是Panel HDR的.Dolby vision 是否一定需要了?跟team 去check? If no, 那么Dolby FVT 可以减少。--PM confirm delete it from G12. | 具体到Win Hello cer.跟着camera走，如果已经有其他项目送样了，可以不用再次送样。 ⏎ 现在都是Panel HDR的.Dolby vision 是否一定需要了?跟team 去check? If no, 那么Dolby FVT 可以减少。--PM confirm delete it from G12. | General |  |
| C16 | SIT | SIT | General |  |
| D16 | 2 | 2 | General |  |
| E16 | 1.7 | 1.7 | General |  |
| F16 | 1.5 | 1.5 | General |  |
| G16 | 1.4 | 1.4 | General |  |
| H16 | 1.3 | 1.3 | General |  |
| B17 | SS | SS | General |  |
| C17 | FVT | FVT | General |  |
| D17 | 9 | 9 | General |  |
| E17 | 7 | 7 | General |  |
| F17 | 5.5 | 5.5 | General |  |
| G17 | 5 | 5 | General |  |
| H17 | 4.4 | 4.4 | General |  |
| I17 | LCFC BIOS and SA 建议根据复杂度，4-6unit /phase. ⏎ HQ 数量偏少 | LCFC BIOS and SA 建议根据复杂度，4-6unit /phase. ⏎ HQ 数量偏少 | General |  |
| J17 | BIOS*4/phase ⏎ EC*1-- 2/Phase ⏎ SA HLK*1/SKU ⏎ SA *5/phase  ⏎ debug*2(compal 无此team和需求,but MS*4 &jump start*2 in SIT PHASE) ⏎ Preload*1/SKU ⏎ OS*1/phase  ⏎  | BIOS*4/phase ⏎ EC*1-- 2/Phase ⏎ SA HLK*1/SKU ⏎ SA *5/phase  ⏎ debug*2(compal 无此team和需求,but MS*4 &jump start*2 in SIT PHASE) ⏎ Preload*1/SKU ⏎ OS*1/phase  ⏎  | General |  |
| K17 | 各家ODM 数据gap挺大的，跟TPM gap也有，需要重点沟通。 ⏎ Pre-load  BIOS Driver  ⏎ 都跟KP 强相关，理论上会要求sku*1. ⏎ 可以根据平台成熟度协商.或者是否可以rework方式节省样机? ⏎ ODM BIOS *10  ⏎            driver *10 ⏎         OS*2 ⏎          EC*5 ⏎       | 各家ODM 数据gap挺大的，跟TPM gap也有，需要重点沟通。 ⏎ Pre-load  BIOS Driver  ⏎ 都跟KP 强相关，理论上会要求sku*1. ⏎ 可以根据平台成熟度协商.或者是否可以rework方式节省样机? ⏎ ODM BIOS *10  ⏎            driver *10 ⏎         OS*2 ⏎          EC*5 ⏎       | General |  |
| L17 | Inhouse只要10台样机 | Inhouse只要10台样机 | General |  |
| C18 | SIT | SIT | General |  |
| D18 | 9 | 9 | General |  |
| E18 | 7 | 7 | General |  |
| F18 | 5.5 | 5.5 | General |  |
| G18 | 5 | 5 | General |  |
| H18 | 4.4 | 4.4 | General |  |
| B19 | PD | PD | General |  |
| C19 | FVT | FVT | General |  |
| D19 | 0.5 | 0.5 | General |  |
| E19 | 0.3 | 0.3 | General |  |
| F19 | 0.25 | 0.25 | General |  |
| G19 | 0.2 | 0.2 | General |  |
| H19 | 0.2 | 0.2 | General |  |
| J19 | 1unit for debug | 1unit for debug | General |  |
| K19 | LNV+ODM PD total 1 unit | LNV+ODM PD total 1 unit | General |  |
| C20 | SIT | SIT | General |  |
| D20 | 0.5 | 0.5 | General |  |
| E20 | 0.3 | 0.3 | General |  |
| F20 | 0.25 | 0.25 | General |  |
| G20 | 0.2 | 0.2 | General |  |
| H20 | 0.2 | 0.2 | General |  |
| A21 | PA | PA | General |  |
| B21 | SWPA | SWPA | General |  |
| C21 | FVT | FVT | General |  |
| D21 | 28 | 28 | General |  |
| E21 | 24 | 24 | General |  |
| F21 | 20 | 20 | General |  |
| G21 | 18 | 18 | General |  |
| H21 | 17 | 17 | General |  |
| J21 | follow PPA sample standard 1.0. ⏎ SW PA 样机数量包含了HLK*1/sku +EE noise test*1/sku. ⏎ 比如HQ EE noise是pwr RD 测试,Compal HLK是pre-load 测试，需要对应的function做相应的扣除和添加。 | follow PPA sample standard 1.0. ⏎ SW PA 样机数量包含了HLK*1/sku +EE noise test*1/sku. ⏎ 比如HQ EE noise是pwr RD 测试,Compal HLK是pre-load 测试，需要对应的function做相应的扣除和添加。 | General |  |
| C22 | SIT | SIT | General |  |
| D22 | 28 | 28 | General |  |
| E22 | 24 | 24 | General |  |
| F22 | 20 | 20 | General |  |
| G22 | 18 | 18 | General |  |
| H22 | 17 | 17 | General |  |
| B23 | MEPA | MEPA | General |  |
| C23 | FVT | FVT | General |  |
| D23 | 16 | 16 | General |  |
| E23 | 12 | 12 | General |  |
| F23 | 9 | 9 | General |  |
| G23 | 7.2 | 7.2 | General |  |
| H23 | 6 | 6 | General |  |
| I23 | LCFC:Confirmed ok as left data.  ⏎ HQ /Compal :to be clarify.  | LCFC:Confirmed ok as left data.  ⏎ HQ /Compal :to be clarify.  | General |  |
| K23 | CS: 1 phase 36 units ⏎ PCB refresh: 1 phase 12-16units. | CS: 1 phase 36 units ⏎ PCB refresh: 1 phase 12-16units. | General |  |
| C24 | SIT | SIT | General |  |
| D24 | 16 | 16 | General |  |
| E24 | 12 | 12 | General |  |
| F24 | 9 | 9 | General |  |
| G24 | 7.2 | 7.2 | General |  |
| H24 | 6 | 6 | General |  |
| B25 | HW PA | HW PA | General |  |
| C25 | FVT | FVT | General |  |
| D25 | 1 | 1 | General |  |
| E25 | 1 | 1 | General |  |
| F25 | 1 | 1 | General |  |
| G25 | 0.8 | 0.8 | General |  |
| H25 | 0.7 | 0.7 | General |  |
| I25 | HQ gap比较大 | HQ gap比较大 | General |  |
| K25 | TTL3- 4unit one phase ⏎ test EE/THM | TTL3- 4unit one phase ⏎ test EE/THM | General |  |
| C26 | SIT | SIT | General |  |
| D26 | 1 | 1 | General |  |
| E26 | 1 | 1 | General |  |
| F26 | 1 | 1 | General |  |
| G26 | 0.8 | 0.8 | General |  |
| H26 | 0.7 | 0.7 | General |  |
| A27 | Certification | Certification | General |  |
| B27 | EMC | EMC | General |  |
| C27 | FVT | FVT | General |  |
| D27 | 0 | 0 | General |  |
| E27 | 0 | 0 | General |  |
| F27 | 0 | 0 | General |  |
| G27 | 0 | 0 | General |  |
| H27 | 0 | 0 | General |  |
| J27 | 认证*1/sku+全套的KP(只要SIT) | 认证*1/sku+全套的KP(只要SIT) | General |  |
| C28 | SIT | SIT | General |  |
| D28 | 1 | 1 | General |  |
| E28 | 1 | 1 | General |  |
| F28 | 1 | 1 | General |  |
| G28 | 1 | 1 | General |  |
| H28 | 1 | 1 | General |  |
| B29 | Green | Green | General |  |
| C29 | FVT | FVT | General |  |
| D29 | 0 | 0 | General |  |
| E29 | 0 | 0 | General |  |
| F29 | 0 | 0 | General |  |
| G29 | 0 | 0 | General |  |
| H29 | 0 | 0 | General |  |
| J29 | 越南DN1 + 韩国DN 1台+ CEL*CPU value(EEcofirm)*2 + BCS 2台 ⏎ Option: ⏎ EPEAT: 5unit. （主要做跌落测试，L/T2-3WK,HQ LOQ 是share 其他function 样机） ⏎  Gaming pro系列项目不符合EPEAT2025的要求,还未做过。 ⏎ E-Star9.0 *1； ⏎ UL golden*1 (Gaming performance and comfort)跟GPU5080以上 ⏎ eyesafe/LBL/HGPD Golden* N台 ,如果Panel数量为N，则样机数量为N ⏎  | 越南DN1 + 韩国DN 1台+ CEL*CPU value(EEcofirm)*2 + BCS 2台 ⏎ Option: ⏎ EPEAT: 5unit. （主要做跌落测试，L/T2-3WK,HQ LOQ 是share 其他function 样机） ⏎  Gaming pro系列项目不符合EPEAT2025的要求,还未做过。 ⏎ E-Star9.0 *1； ⏎ UL golden*1 (Gaming performance and comfort)跟GPU5080以上 ⏎ eyesafe/LBL/HGPD Golden* N台 ,如果Panel数量为N，则样机数量为N ⏎  | General |  |
| K29 | FVT for RD 内测,leverage safety. | FVT for RD 内测,leverage safety. | General |  |
| C30 | SIT | SIT | General |  |
| D30 | 3 | 3 | General |  |
| E30 | 3 | 3 | General |  |
| F30 | 1.5 | 1.5 | General |  |
| G30 | 1.2 | 1.2 | General |  |
| H30 | 1 | 1 | General |  |
| B31 | Safety | Safety | General |  |
| C31 | FVT | FVT | General |  |
| D31 | 5 | 5 | General |  |
| E31 | 3 | 3 | General |  |
| F31 | 2.5 | 2.5 | General |  |
| G31 | 2 | 2 | General |  |
| H31 | 1.6 | 1.6 | General |  |
| J31 | FVT:CB 5台(battery source +1 自测)，UL4200A（纽扣电池） 1台-->0 (现在基本内置Batt)， BIS 1 台. ⏎ Common charge 2 台， ⏎ SIT:CCC 2 (1+CPU 核心数*1pcs)+ 韩国 1 + 内测 1 ⏎ NOM 1  + EAC 1(哈萨克斯坦1pcs maybe) | FVT:CB 5台(battery source +1 自测)，UL4200A（纽扣电池） 1台-->0 (现在基本内置Batt)， BIS 1 台. ⏎ Common charge 2 台， ⏎ SIT:CCC 2 (1+CPU 核心数*1pcs)+ 韩国 1 + 内测 1 ⏎ NOM 1  + EAC 1(哈萨克斯坦1pcs maybe) | General |  |
| K31 | BIS: India catelog name *1pcs/SIT PHASE/BATTERY SPEC/ADP SPEC. ⏎ adapter rating label* battery rating label. | BIS: India catelog name *1pcs/SIT PHASE/BATTERY SPEC/ADP SPEC. ⏎ adapter rating label* battery rating label. | General |  |
| C32 | SIT | SIT | General |  |
| D32 | 3 | 3 | General |  |
| E32 | 2 | 2 | General |  |
| F32 | 1.5 | 1.5 | General |  |
| G32 | 1.2 | 1.2 | General |  |
| H32 | 1 | 1 | General |  |
| B33 | RF Certification | RF Certification | General |  |
| C33 | FVT | FVT | General |  |
| D33 | 0 | 0 | General |  |
| E33 | 0 | 0 | General |  |
| F33 | 0 | 0 | General |  |
| G33 | 0 | 0 | General |  |
| H33 | 0 | 0 | General |  |
| J33 | this data for 2 antenna source +2 wlan source refrence: ⏎ 1.SRRC *2(PRC 型号核准);如果网卡数量大于天线数量，整机需求基于WLAN卡型号数量； ⏎ 2.CE *4 =antenna *wlan（欧盟）,如果网卡数量大于天线数量，需额外提供网卡单体送测； ⏎ 3.FCC(intel WLAN 数量*天线数量)*4（如果是C1PC ,就不需要整机）,其他wlan source(Non-intel) combine with CE.; ⏎ 4.印尼* 2  . ⏎ 5.Mexico *1. ⏎ 6.资安*2（欧盟网络安全） ⏎  | this data for 2 antenna source +2 wlan source refrence: ⏎ 1.SRRC *2(PRC 型号核准);如果网卡数量大于天线数量，整机需求基于WLAN卡型号数量； ⏎ 2.CE *4 =antenna *wlan（欧盟）,如果网卡数量大于天线数量，需额外提供网卡单体送测； ⏎ 3.FCC(intel WLAN 数量*天线数量)*4（如果是C1PC ,就不需要整机）,其他wlan source(Non-intel) combine with CE.; ⏎ 4.印尼* 2  . ⏎ 5.Mexico *1. ⏎ 6.资安*2（欧盟网络安全） ⏎  | General |  |
| C34 | SIT | SIT | General |  |
| D34 | 7.5 | 7.5 | General |  |
| E34 | 5 | 5 | General |  |
| F34 | 3.75 | 3.75 | General |  |
| G34 | 3 | 3 | General |  |
| H34 | 2.5 | 2.5 | General |  |
| L34 | 比G12 9台多 | 比G12 9台多 | General |  |
| A35 | 3rd Party Vendor | 3rd Party Vendor | General |  |
| B35 | BIOS | BIOS | General |  |
| C35 | FVT | FVT | General |  |
| D35 | 0.5 | 0.5 | General |  |
| E35 | 0.3 | 0.3 | General |  |
| F35 | 0.25 | 0.25 | General |  |
| G35 | 0.2 | 0.2 | General |  |
| H35 | 0.2 | 0.2 | General |  |
| K35 | the data is for leading CS project.  ⏎ Others less than this, case by case. | the data is for leading CS project.  ⏎ Others less than this, case by case. | General |  |
| C36 | SIT | SIT | General |  |
| D36 | 0.5 | 0.5 | General |  |
| E36 | 0.3 | 0.3 | General |  |
| F36 | 0.25 | 0.25 | General |  |
| G36 | 0.2 | 0.2 | General |  |
| H36 | 0.2 | 0.2 | General |  |
| B37 | ITE | ITE | General |  |
| C37 | FVT | FVT | General |  |
| D37 | 0.5 | 0.5 | General |  |
| E37 | 0.3 | 0.3 | General |  |
| F37 | 0.25 | 0.25 | General |  |
| G37 | 0.2 | 0.2 | General |  |
| H37 | 0.2 | 0.2 | General |  |
| J37 | Total one phase on unit | Total one phase on unit | General |  |
| K37 | if no lighting feature,no need | if no lighting feature,no need | General |  |
| C38 | SIT | SIT | General |  |
| D38 | 0.5 | 0.5 | General |  |
| E38 | 0.3 | 0.3 | General |  |
| F38 | 0.25 | 0.25 | General |  |
| G38 | 0.2 | 0.2 | General |  |
| H38 | 0.2 | 0.2 | General |  |
| B39 | NV | NV | General |  |
| C39 | FVT | FVT | General |  |
| D39 | 3 | 3 | General |  |
| E39 | 2 | 2 | General |  |
| F39 | 1.5 | 1.5 | General |  |
| G39 | 1.2 | 1.2 | General |  |
| H39 | 1 | 1 | General |  |
| J39 | 台北，印度，美国各2台  TTL 6pcs  | 台北，印度，美国各2台  TTL 6pcs  | General |  |
| K39 | the data is for leading CS project.  ⏎ Others less than this, case by case. | the data is for leading CS project.  ⏎ Others less than this, case by case. | General |  |
| C40 | SIT | SIT | General |  |
| D40 | 3 | 3 | General |  |
| E40 | 2 | 2 | General |  |
| F40 | 1.5 | 1.5 | General |  |
| G40 | 1.2 | 1.2 | General |  |
| H40 | 1 | 1 | General |  |
| B41 | INTEL | INTEL | General |  |
| C41 | FVT | FVT | General |  |
| D41 | 3 | 3 | General |  |
| E41 | 2 | 2 | General |  |
| F41 | 1.5 | 1.5 | General |  |
| G41 | 1.2 | 1.2 | General |  |
| H41 | 1 | 1 | General |  |
| J41 | 6PCS | 6PCS | General |  |
| C42 | SIT | SIT | General |  |
| D42 | 3 | 3 | General |  |
| E42 | 2 | 2 | General |  |
| F42 | 1.5 | 1.5 | General |  |
| G42 | 1.2 | 1.2 | General |  |
| H42 | 1 | 1 | General |  |
| A43 | MFG | MFG | General |  |
| B43 | MFG | MFG | General |  |
| C43 | FVT | FVT | General |  |
| D43 | 0.5 | 0.5 | General |  |
| E43 | 0.3 | 0.3 | General |  |
| F43 | 0.25 | 0.25 | General |  |
| G43 | 0.2 | 0.2 | General |  |
| H43 | 0.2 | 0.2 | General |  |
| J43 | 红丹test | 红丹test | General |  |
| K43 | Total one phase on unit | Total one phase on unit | General |  |
| C44 | SIT | SIT | General |  |
| D44 | 0.5 | 0.5 | General |  |
| E44 | 0.3 | 0.3 | General |  |
| F44 | 0.25 | 0.25 | General |  |
| G44 | 0.2 | 0.2 | General |  |
| H44 | 0.2 | 0.2 | General |  |
| B45 | SUM/sku | SUM/sku | General |  |
| C45 | FVT | FVT | General |  |
| D45 | =SUM(D3+D5+D7+D9+D11+D13+D15+D17+D19+D21+D23+D25+D27+D29+D31+D33+D35+D37+D39+D41+D43) | 86.5 | General | FORMULA |
| E45 | =SUM(E3+E5+E7+E9+E11+E13+E15+E17+E19+E21+E23+E25+E27+E29+E31+E33+E35+E37+E39+E41+E43) | 65.49999999999999 | General | FORMULA |
| F45 | =SUM(F3+F5+F7+F9+F11+F13+F15+F17+F19+F21+F23+F25+F27+F29+F31+F33+F35+F37+F39+F41+F43) | 52.85 | General | FORMULA |
| G45 | =SUM(G3+G5+G7+G9+G11+G13+G15+G17+G19+G21+G23+G25+G27+G29+G31+G33+G35+G37+G39+G41+G43) | 45.20000000000002 | General | FORMULA |
| H45 | =SUM(H3+H5+H7+H9+H11+H13+H15+H17+H19+H21+H23+H25+H27+H29+H31+H33+H35+H37+H39+H41+H43) | 40.30000000000001 | General | FORMULA |
| C46 | SIT | SIT | General |  |
| D46 | =SUM(D4+D6+D8+D10+D12+D14+D16+D18+D20+D22+D24+D26+D28+D30+D32+D34+D36+D38+D40+D42+D44) | 96 | General | FORMULA |
| E46 | =SUM(E4+E6+E8+E10+E12+E14+E16+E18+E20+E22+E24+E26+E28+E30+E32+E34+E36+E38+E40+E42+E44) | 73.49999999999999 | General | FORMULA |
| F46 | =SUM(F4+F6+F8+F10+F12+F14+F16+F18+F20+F22+F24+F26+F28+F30+F32+F34+F36+F38+F40+F42+F44) | 58.1 | General | FORMULA |
| G46 | =SUM(G4+G6+G8+G10+G12+G14+G16+G18+G20+G22+G24+G26+G28+G30+G32+G34+G36+G38+G40+G42+G44) | 49.60000000000002 | General | FORMULA |
| H46 | =SUM(H4+H6+H8+H10+H12+H14+H16+H18+H20+H22+H24+H26+H28+H30+H32+H34+H36+H38+H40+H42+H44) | 44.20000000000001 | General | FORMULA |
| C47 | Sku Qty | Sku Qty | General |  |
| D47 | 2 | 2 | General |  |
| E47 | 3 | 3 | General |  |
| F47 | 4 | 4 | General |  |
| G47 | 5 | 5 | General |  |
| H47 | 6 | 6 | General |  |
| B48 | TTL SUM/phase | TTL SUM/phase | General |  |
| C48 | FVT | FVT | General |  |
| D48 | =D45*D47 | 173 | General | FORMULA |
| E48 | =E45*E47 | 196.49999999999994 | General | FORMULA |
| F48 | =F45*F47 | 211.4 | General | FORMULA |
| G48 | =G45*G47 | 226.00000000000009 | General | FORMULA |
| H48 | =H45*H47 | 241.80000000000007 | General | FORMULA |
| C49 | SIT | SIT | General |  |
| D49 | =D46*D47 | 192 | General | FORMULA |
| E49 | =E46*E47 | 220.49999999999994 | General | FORMULA |
| F49 | =F46*F47 | 232.4 | General | FORMULA |
| G49 | =G46*G47 | 248.0000000000001 | General | FORMULA |
| H49 | =H46*H47 | 265.20000000000005 | General | FORMULA |
| B51 | Certification | Certification | General |  |
| B52 | SUM/sku | SUM/sku | General |  |
| C52 | Sku Qty | Sku Qty | General |  |
| D52 | 2 | 2 | General |  |
| E52 | 3 | 3 | General |  |
| F52 | 4 | 4 | General |  |
| G52 | 5 | 5 | General |  |
| H52 | 6 | 6 | General |  |
| J52 | Flicker Free，TUV EyeSafe，Low Blue Light  can leverage sample unit,1panel*1 unit; ⏎ High gaming performance*1panel*1 unit.  ⏎ refer to G10 G12 LCFC data: WW certification including promition: range 34--36 units. ⏎  Certification 每个场景下的样机不一样，主要差异在EMC, 因为EMC 的样机是by sku的，需要cover所有KP. ⏎ For PRC only project: need xx units for CCC. X units For SRRC. | Flicker Free，TUV EyeSafe，Low Blue Light  can leverage sample unit,1panel*1 unit; ⏎ High gaming performance*1panel*1 unit.  ⏎ refer to G10 G12 LCFC data: WW certification including promition: range 34--36 units. ⏎  Certification 每个场景下的样机不一样，主要差异在EMC, 因为EMC 的样机是by sku的，需要cover所有KP. ⏎ For PRC only project: need xx units for CCC. X units For SRRC. | General |  |
| B53 | EMC | EMC | General |  |
| C53 | FVT | FVT | General |  |
| D53 | 0 | 0 | General |  |
| E53 | 0 | 0 | General |  |
| F53 | 0 | 0 | General |  |
| G53 | 0 | 0 | General |  |
| H53 | 0 | 0 | General |  |
| C54 | SIT | SIT | General |  |
| D54 | 2 | 2 | General |  |
| E54 | 3 | 3 | General |  |
| F54 | 4 | 4 | General |  |
| G54 | 5 | 5 | General |  |
| H54 | 6 | 6 | General |  |
| B55 | Green | Green | General |  |
| C55 | FVT | FVT | General |  |
| D55 | 0 | 0 | General |  |
| E55 | 0 | 0 | General |  |
| F55 | 0 | 0 | General |  |
| G55 | 0 | 0 | General |  |
| H55 | 0 | 0 | General |  |
| C56 | SIT | SIT | General |  |
| D56 | 6 | 6 | General |  |
| E56 | 6 | 6 | General |  |
| F56 | 6 | 6 | General |  |
| G56 | 6 | 6 | General |  |
| H56 | 6 | 6 | General |  |
| B57 | Safety | Safety | General |  |
| C57 | FVT | FVT | General |  |
| D57 | 10 | 10 | General |  |
| E57 | 9 | 9 | General |  |
| F57 | 10 | 10 | General |  |
| G57 | 10 | 10 | General |  |
| H57 | 10 | 10 | General |  |
| C58 | SIT | SIT | General |  |
| D58 | 6 | 6 | General |  |
| E58 | 6 | 6 | General |  |
| F58 | 6 | 6 | General |  |
| G58 | 6 | 6 | General |  |
| H58 | 6 | 6 | General |  |
| B59 | RF Certification | RF Certification | General |  |
| C59 | FVT | FVT | General |  |
| D59 | 0 | 0 | General |  |
| E59 | 0 | 0 | General |  |
| F59 | 0 | 0 | General |  |
| G59 | 0 | 0 | General |  |
| H59 | 0 | 0 | General |  |
| C60 | SIT | SIT | General |  |
| D60 | 8 | 8 | General |  |
| E60 | 9 | 9 | General |  |
| F60 | 10 | 10 | General |  |
| G60 | 10 | 10 | General |  |
| H60 | 10 | 10 | General |  |
| B61 | TTL SUM/phase | TTL SUM/phase | General |  |
| C61 | FVT | FVT | General |  |
| D61 | =SUM(D53+D55+D57+D59) | 10 | General | FORMULA |
| E61 | =SUM(E53+E55+E57+E59) | 9 | General | FORMULA |
| F61 | =SUM(F53+F55+F57+F59) | 10 | General | FORMULA |
| G61 | =SUM(G53+G55+G57+G59) | 10 | General | FORMULA |
| H61 | =SUM(H53+H55+H57+H59) | 10 | General | FORMULA |
| C62 | SIT | SIT | General |  |
| D62 | =SUM(D54+D56+D58+D60) | 22 | General | FORMULA |
| E62 | =SUM(E54+E56+E58+E60) | 24 | General | FORMULA |
| F62 | =SUM(F54+F56+F58+F60) | 26 | General | FORMULA |
| G62 | =SUM(G54+G56+G58+G60) | 27 | General | FORMULA |
| H62 | =SUM(H54+H56+H58+H60) | 28 | General | FORMULA |
| B66 | PA  | PA  | General |  |
| B67 | SUM/sku | SUM/sku | General |  |
| C67 | Sku Qty | Sku Qty | General |  |
| D67 | 2 | 2 | General |  |
| E67 | 3 | 3 | General |  |
| F67 | 4 | 4 | General |  |
| G67 | 5 | 5 | General |  |
| H67 | 6 | 6 | General |  |
| B68 | SWPA | SWPA | General |  |
| C68 | FVT | FVT | General |  |
| D68 | 56 | 56 | General |  |
| E68 | 72 | 72 | General |  |
| F68 | 80 | 80 | General |  |
| G68 | 90 | 90 | General |  |
| H68 | 102 | 102 | General |  |
| C69 | SIT | SIT | General |  |
| D69 | 56 | 56 | General |  |
| E69 | 72 | 72 | General |  |
| F69 | 80 | 80 | General |  |
| G69 | 90 | 90 | General |  |
| H69 | 102 | 102 | General |  |
| B70 | MEPA | MEPA | General |  |
| C70 | FVT | FVT | General |  |
| D70 | 36 | 36 | General |  |
| E70 | 36 | 36 | General |  |
| F70 | 36 | 36 | General |  |
| G70 | 36 | 36 | General |  |
| H70 | 36 | 36 | General |  |
| C71 | SIT | SIT | General |  |
| D71 | 36 | 36 | General |  |
| E71 | 36 | 36 | General |  |
| F71 | 36 | 36 | General |  |
| G71 | 36 | 36 | General |  |
| H71 | 36 | 36 | General |  |
| B72 | HW PA | HW PA | General |  |
| C72 | FVT | FVT | General |  |
| D72 | 2 | 2 | General |  |
| E72 | 3 | 3 | General |  |
| F72 | 4 | 4 | General |  |
| G72 | 4 | 4 | General |  |
| H72 | 4 | 4 | General |  |
| C73 | SIT | SIT | General |  |
| D73 | 2 | 2 | General |  |
| E73 | 3 | 3 | General |  |
| F73 | 4 | 4 | General |  |
| G73 | 4 | 4 | General |  |
| H73 | 4 | 4 | General |  |
| B74 | TTL SUM/phase | TTL SUM/phase | General |  |
| C74 | FVT | FVT | General |  |
| D74 | =SUM(D68+D70+D72) | 94 | General | FORMULA |
| E74 | =SUM(E68+E70+E72) | 111 | General | FORMULA |
| F74 | =SUM(F68+F70+F72) | 120 | General | FORMULA |
| G74 | =SUM(G68+G70+G72) | 130 | General | FORMULA |
| H74 | =SUM(H68+H70+H72) | 142 | General | FORMULA |
| C75 | SIT | SIT | General |  |
| D75 | =SUM(D69+D71+D73) | 94 | General | FORMULA |
| E75 | =SUM(E69+E71+E73) | 111 | General | FORMULA |
| F75 | =SUM(F69+F71+F73) | 120 | General | FORMULA |
| G75 | =SUM(G69+G71+G73) | 130 | General | FORMULA |
| H75 | =SUM(H69+H71+H73) | 142 | General | FORMULA |
| B78 | 备注： | 备注： | General |  |
| C78 | SKU Definition | SKU Definition | General |  |
| C79 | 2SKU: 1-2*CPU +1*GPU+ 1-2*Panel +SSD SPEC*1 +Mem spec *1     VRAM match MB1 1-2 Source/X9/X11.                                                  N1x/Y9 source少，Volume 少 | 2SKU: 1-2*CPU +1*GPU+ 1-2*Panel +SSD SPEC*1 +Mem spec *1     VRAM match MB1 1-2 Source/X9/X11.                                                  N1x/Y9 source少，Volume 少 | General |  |
| C80 | 3SKU:2-3*CPU +2*GPU+ 1*Panel spec  +SSD SPEC*1 +Mem spec *1(or SSD/Mem spec *2, arrange  2nd wave)                                             Y7  DIS  | 3SKU:2-3*CPU +2*GPU+ 1*Panel spec  +SSD SPEC*1 +Mem spec *1(or SSD/Mem spec *2, arrange  2nd wave)                                             Y7  DIS  | General |  |
| C81 | 4SKU:2-4*CPU +2-3*GPU+ 2*Panel spec  +SSD SPEC*2 +Mem spec *2                                                                                                                Pro/LOQ /Y5 | 4SKU:2-4*CPU +2-3*GPU+ 2*Panel spec  +SSD SPEC*2 +Mem spec *2                                                                                                                Pro/LOQ /Y5 | General |  |
| C82 | 5SKU :3-4*CPU +3*GPU+ 2*Panel spec  +SSD SPEC*2 +Mem spec *2                                                                                                                   Pro/LOQ /Y5             | 5SKU :3-4*CPU +3*GPU+ 2*Panel spec  +SSD SPEC*2 +Mem spec *2                                                                                                                   Pro/LOQ /Y5             | General |  |
| C83 | 6SKU::4-5*CPU +3*GPU+ 2-3*Panel spec  +SSD SPEC*2 +Mem spec *2-3                                                                                                            ID./ME*2 ，Pro上 | 6SKU::4-5*CPU +3*GPU+ 2-3*Panel spec  +SSD SPEC*2 +Mem spec *2-3                                                                                                            ID./ME*2 ，Pro上 | General |  |
| C86 | source复杂度/ODM 是哪家--SKU数量->Function units 数量-->ODM UNIT | source复杂度/ODM 是哪家--SKU数量->Function units 数量-->ODM UNIT | General |  |
| C88 | source的复杂度到sku的数量，当前是基于经验值判断的。 | source的复杂度到sku的数量，当前是基于经验值判断的。 | General |  |
| G88 | G12 build plan 和SP 作为经验值的数据支撑 | G12 build plan 和SP 作为经验值的数据支撑 | General |  |
| C91 | Input | Input | General |  |
| E91 | output | output | General |  |
| C92 | key source数量 | key source数量 | General |  |
| E92 | Sku 数量 | Sku 数量 | General |  |
| C93 | CPU GPU PANEL  SSD memory | CPU GPU PANEL  SSD memory | General |  |
| E93 | 推荐Build plan | 推荐Build plan | General |  |
| C94 | ODM | ODM | General |  |
| E94 | 各个function 数量 | 各个function 数量 | General |  |
| E95 | total的数量 | total的数量 | General |  |

## Comments

| Ref | Kind | Text |
|---|---|---|
| D2 | legacy_comment | <t>[线程批注] ⏎  ⏎ 你的Excel版本可读取此线程批注; 但如果在更新版本的Excel中打开文件，则对批注所作的任何改动都将被删除。了解详细信息: https://go.microsoft.com/fwlink/?linkid=870924 ⏎  ⏎ 注释: ⏎     2*panel+1*CPU+1*GPU |
| E2 | legacy_comment | <t>[线程批注] ⏎  ⏎ 你的Excel版本可读取此线程批注; 但如果在更新版本的Excel中打开文件，则对批注所作的任何改动都将被删除。了解详细信息: https://go.microsoft.com/fwlink/?linkid=870924 ⏎  ⏎ 注释: ⏎     3*panel+2*CPU+2*GPU |
| F2 | legacy_comment | <t>[线程批注] ⏎  ⏎ 你的Excel版本可读取此线程批注; 但如果在更新版本的Excel中打开文件，则对批注所作的任何改动都将被删除。了解详细信息: https://go.microsoft.com/fwlink/?linkid=870924 ⏎  ⏎ 注释: ⏎     4*panel+2*CPU+2*GPU |
| G2 | legacy_comment | <t>[线程批注] ⏎  ⏎ 你的Excel版本可读取此线程批注; 但如果在更新版本的Excel中打开文件，则对批注所作的任何改动都将被删除。了解详细信息: https://go.microsoft.com/fwlink/?linkid=870924 ⏎  ⏎ 注释: ⏎     5*panel+3*CPU+3*GPU |
| H2 | legacy_comment | <t>[线程批注] ⏎  ⏎ 你的Excel版本可读取此线程批注; 但如果在更新版本的Excel中打开文件，则对批注所作的任何改动都将被删除。了解详细信息: https://go.microsoft.com/fwlink/?linkid=870924 ⏎  ⏎ 注释: ⏎     6*panel+3*CPU+3*GPU |
| D2 | threaded_comment | 2*panel+1*CPU+1*GPU |
| E2 | threaded_comment | 3*panel+2*CPU+2*GPU |
| F2 | threaded_comment | 4*panel+2*CPU+2*GPU |
| G2 | threaded_comment | 5*panel+3*CPU+3*GPU |
| H2 | threaded_comment | 6*panel+3*CPU+3*GPU |