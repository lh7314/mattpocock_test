# Phase-1 rule design validation

Validation of `prototype/rules_v1.py` against the extracted baseline. All numbers derive from the Owner workbook; nothing hand-typed.


## 1. SKU recommendation scenarios

### T-01 positive / clean 4-SKU profile
- input: {'cpu': (3, 'FILE'), 'gpu': (2, 'FILE'), 'panel': (2, 'FILE'), 'ssd': (2, 'FILE'), 'mem': (2, 'FILE')}
- state: **SINGLE** | recommended: 4 | range: [4, 4]
- candidate scores: SKU4=1.00, SKU5=0.85, SKU6=0.76, SKU3=0.64, SKU2=0.49
  - SKU5 not recommended (norm=0.85): lower weighted match
  - SKU6 not recommended (norm=0.76): lower weighted match

### T-02 positive / small project 2-SKU profile
- input: {'cpu': (1, 'FILE'), 'gpu': (1, 'FILE'), 'panel': (1, 'FILE'), 'ssd': (1, 'FILE'), 'mem': (1, 'FILE')}
- state: **SINGLE** | recommended: 2 | range: [2, 2]
- candidate scores: SKU2=1.00, SKU3=0.76, SKU4=0.40, SKU5=0.24, SKU6=0.24
  - SKU3 not recommended (norm=0.76): lower weighted match
  - SKU4 not recommended (norm=0.40): lower weighted match

### T-03 positive / mid 3-SKU profile
- input: {'cpu': (2, 'FILE'), 'gpu': (2, 'FILE'), 'panel': (1, 'FILE'), 'ssd': (1, 'FILE'), 'mem': (1, 'FILE')}
- state: **SINGLE** | recommended: 3 | range: [3, 3]
- candidate scores: SKU3=1.00, SKU2=0.85, SKU4=0.64, SKU5=0.40, SKU6=0.34
  - SKU2 not recommended (norm=0.85): lower weighted match
  - SKU4 not recommended (norm=0.64): lower weighted match

### T-04 positive / large 6-SKU profile
- input: {'cpu': (5, 'FILE'), 'gpu': (3, 'FILE'), 'panel': (3, 'FILE'), 'ssd': (2, 'FILE'), 'mem': (3, 'FILE')}
- state: **SINGLE** | recommended: 6 | range: [6, 6]
- candidate scores: SKU6=1.00, SKU4=0.68, SKU5=0.68, SKU3=0.19, SKU2=0.15
  - SKU4 not recommended (norm=0.68): lower weighted match
  - SKU5 not recommended (norm=0.68): lower weighted match

### T-05 boundary / CPU at 4-SKU upper bound
- input: {'cpu': (4, 'FILE'), 'gpu': (2, 'FILE'), 'panel': (2, 'FILE'), 'ssd': (2, 'FILE'), 'mem': (2, 'FILE')}
- state: **SINGLE** | recommended: 4 | range: [4, 4]
- candidate scores: SKU4=1.00, SKU5=0.85, SKU6=0.85, SKU3=0.55, SKU2=0.43
  - SKU5 not recommended (norm=0.85): lower weighted match
  - SKU6 not recommended (norm=0.85): lower weighted match

### T-06 boundary / GPU=1 but 4 spec dims high
- input: {'cpu': (4, 'FILE'), 'gpu': (1, 'FILE'), 'panel': (2, 'FILE'), 'ssd': (2, 'FILE'), 'mem': (2, 'FILE')}
- state: **SINGLE_WITH_RESERVATION** | recommended: 4 | range: [4, 4]
- candidate scores: SKU4=0.85, SKU5=0.75, SKU6=0.75, SKU2=0.58, SKU3=0.40
  - SKU5 not recommended (norm=0.75): hard mismatch on gpu
  - SKU6 not recommended (norm=0.75): hard mismatch on gpu

### T-07 boundary / Panel=2 blocks the 3-SKU path
- input: {'cpu': (2, 'FILE'), 'gpu': (2, 'FILE'), 'panel': (2, 'FILE'), 'ssd': (1, 'FILE'), 'mem': (1, 'FILE')}
- state: **SINGLE_WITH_RESERVATION** | recommended: 3 | range: [3, 3]
- candidate scores: SKU3=0.91, SKU2=0.85, SKU4=0.74, SKU5=0.49, SKU6=0.43
  - SKU2 not recommended (norm=0.85): lower weighted match
  - SKU4 not recommended (norm=0.74): lower weighted match

### T-08 boundary / everything maxed
- input: {'cpu': (6, 'FILE'), 'gpu': (5, 'FILE'), 'panel': (4, 'FILE'), 'ssd': (4, 'FILE'), 'mem': (4, 'FILE')}
- state: **SINGLE_WITH_RESERVATION** | recommended: 6 | range: [6, 6]
- candidate scores: SKU6=0.21, SKU2=0.00, SKU3=0.00, SKU4=0.00, SKU5=0.00
  - SKU2 not recommended (norm=0.00): hard mismatch on cpu/gpu/panel/ssd/mem
  - SKU3 not recommended (norm=0.00): hard mismatch on cpu/gpu/panel/ssd/mem

### T-09 boundary / everything min-flagged
- input: {'cpu': (1, 'FILE'), 'gpu': (1, 'FILE'), 'panel': (1, 'FILE'), 'ssd': (1, 'FILE'), 'mem': (2, 'FILE')}
- state: **SINGLE_WITH_RESERVATION** | recommended: 2 | range: [2, 2]
- candidate scores: SKU2=0.87, SKU3=0.62, SKU4=0.53, SKU5=0.37, SKU6=0.37
  - SKU3 not recommended (norm=0.62): lower weighted match
  - SKU4 not recommended (norm=0.53): lower weighted match

### T-10 missing / Panel not provided
- input: {'cpu': (3, 'FILE'), 'gpu': (2, 'FILE'), 'panel': (None, 'UNKNOWN'), 'ssd': (2, 'FILE'), 'mem': (2, 'FILE')}
- state: **SINGLE_WITH_RESERVATION** | recommended: 4 | range: [4, 4]
- 请补充: panel
- candidate scores: SKU4=1.00, SKU5=0.82, SKU6=0.71, SKU3=0.69, SKU2=0.40
  - SKU5 not recommended (norm=0.82): lower weighted match
  - SKU6 not recommended (norm=0.71): lower weighted match

### T-11 missing / only CPU known
- input: {'cpu': (3, 'FILE'), 'gpu': (None, 'UNKNOWN'), 'panel': (None, 'UNKNOWN'), 'ssd': (None, 'UNKNOWN'), 'mem': (None, 'UNKNOWN')}
- state: **RANGE** | recommended: None | range: [3, 5]
- 请补充: gpu, panel, ssd, mem
- candidate scores: SKU3=1.00, SKU4=1.00, SKU5=1.00, SKU2=0.40, SKU6=0.40
  - SKU2 not recommended (norm=0.40): lower weighted match
  - SKU6 not recommended (norm=0.40): lower weighted match

### T-12 missing / nothing known
- input: {'cpu': (None, 'UNKNOWN'), 'gpu': (None, 'UNKNOWN'), 'panel': (None, 'UNKNOWN'), 'ssd': (None, 'UNKNOWN'), 'mem': (None, 'UNKNOWN')}
- state: **UNDETERMINED** | recommended: None | range: None
- reason: no key factor supplied
- candidate scores: 

### T-13 conflict / SSD-Mem=2 but GPU=1
- input: {'cpu': (2, 'FILE'), 'gpu': (1, 'FILE'), 'panel': (1, 'FILE'), 'ssd': (2, 'FILE'), 'mem': (2, 'FILE')}
- state: **SINGLE_WITH_RESERVATION** | recommended: 4 | range: [4, 4]
- candidate scores: SKU4=0.76, SKU2=0.74, SKU3=0.59, SKU5=0.56, SKU6=0.50
  - SKU2 not recommended (norm=0.74): lower weighted match
  - SKU3 not recommended (norm=0.59): lower weighted match

### T-14 conflict / 2nd-wave SSD/Mem on 3-SKU base
- input: {'cpu': (2, 'FILE'), 'gpu': (2, 'FILE'), 'panel': (1, 'FILE'), 'ssd': (2, 'FILE'), 'mem': (2, 'FILE')}
- state: **SINGLE_WITH_RESERVATION** | recommended: 4 | range: [4, 4]
- candidate scores: SKU4=0.91, SKU3=0.74, SKU5=0.66, SKU6=0.60, SKU2=0.59
  - SKU3 not recommended (norm=0.74): lower weighted match
  - SKU5 not recommended (norm=0.66): lower weighted match

### T-15 conflict / CPU=2 fits 2,3 and 4-SKU
- input: {'cpu': (2, 'FILE'), 'gpu': (2, 'FILE'), 'panel': (1, 'FILE'), 'ssd': (1, 'FILE'), 'mem': (1, 'FILE')}
- state: **SINGLE** | recommended: 3 | range: [3, 3]
- candidate scores: SKU3=1.00, SKU2=0.85, SKU4=0.64, SKU5=0.40, SKU6=0.34
  - SKU2 not recommended (norm=0.85): lower weighted match
  - SKU4 not recommended (norm=0.64): lower weighted match


## 2. Sample-demand output (D-01: decimals, no rounding)

- SKU4: base=443.8 FVT=211.4 SIT=232.4 cond=1.0 reuse=-0.5 risk=22.215000 -> **recommended=466.515000**
  by_category: {"RD": 132.8, "PA": 240.0, "CERT": 41.0, "VENDOR": 28.0, "MFG": 2.0}
  potential_reuse shown but NOT applied: 0.0

  Top function lines for the recommended SKU:
  - SWPA            FVT  20.0 x 4 SKU = 80      rule=BASELINE-CS-ODM-001:F_SWPA:FVT@v1.0-draft cell=F21
  - SWPA            SIT  20.0 x 4 SKU = 80      rule=BASELINE-CS-ODM-001:F_SWPA:SIT@v1.0-draft cell=F22
  - MEPA            FVT  9.0 x 4 SKU = 36      rule=BASELINE-CS-ODM-001:F_MEPA:FVT@v1.0-draft cell=F23
  - MEPA            SIT  9.0 x 4 SKU = 36      rule=BASELINE-CS-ODM-001:F_MEPA:SIT@v1.0-draft cell=F24
  - SS              FVT  5.5 x 4 SKU = 22      rule=BASELINE-CS-ODM-001:F_SS:FVT@v1.0-draft cell=F17
  - SS              SIT  5.5 x 4 SKU = 22      rule=BASELINE-CS-ODM-001:F_SS:SIT@v1.0-draft cell=F18
  - RF CertificationSIT  3.75 x 4 SKU = 15      rule=BASELINE-CS-ODM-001:F_RF_CERTIFICATION:SIT@v1.0-draft cell=F34
  - HW              FVT  3.5 x 4 SKU = 14      rule=BASELINE-CS-ODM-001:F_HW:FVT@v1.0-draft cell=F3

## 3. SKU Definition ambiguity scan

- combinations scanned: 2800 (cpu1-7, gpu1-5, panel1-5, ssd1-4, mem1-4)
- SINGLE_WITH_RESERVATION: 2398 (85.6%)  e.g. {'cpu': 1, 'gpu': 1, 'panel': 1, 'ssd': 1, 'mem': 2}
- RANGE: 385 (13.8%)  e.g. {'cpu': 1, 'gpu': 2, 'panel': 4, 'ssd': 1, 'mem': 2}
- SINGLE: 17 (0.6%)  e.g. {'cpu': 1, 'gpu': 1, 'panel': 1, 'ssd': 1, 'mem': 1}
- outcome distribution: 2-3=77, 2-4=12, 2-6=6, 3-4=30, 3-5=5, 3-6=9, 4-5=93, 4-6=153, single 2=457, single 3=216, single 4=543, single 6=1199

### Discriminative power of each key factor (single-factor only)
- cpu   : {'SINGLE_WITH_RESERVATION': 3, 'RANGE': 3, 'UNDETERMINED': 1}
- gpu   : {'SINGLE_WITH_RESERVATION': 1, 'RANGE': 3, 'UNDETERMINED': 1}
- panel : {'RANGE': 2, 'SINGLE_WITH_RESERVATION': 2, 'UNDETERMINED': 1}
- ssd   : {'RANGE': 3, 'UNDETERMINED': 1}
- mem   : {'RANGE': 2, 'SINGLE_WITH_RESERVATION': 2}

## 4. Design invariants / regression checks

- [PASS] workbook grand totals reproduce (SKU2..6) {'SKU2': 365.0, 'SKU3': 417.0, 'SKU4': 443.8, 'SKU5': 474.0, 'SKU6': 507.0}
- [PASS] recommended total grows with SKU count 365.0 -> 507.0
- [PASS] D-01: decimals preserved, never rounded to int SKU4 base=443.8 (not 444), SKU5 base=474.0
- [PASS] D-01: fractional risk reserve not rounded reserve=22.19
- [PASS] missing field never defaults to 0/1 
- [PASS] user value overrides file value 
- [PASS] file value retained alongside user value 
- [PASS] potential reuse does not reduce demand base=443.8 rec=443.8
- [PASS] confirmed reuse does reduce demand 
- [PASS] empty input -> UNDETERMINED (no pseudo-precision) no key factor supplied
- [PASS] tie -> RANGE, not a fake single number [3, 5] tie=[3, 4, 5]

### SKU reachability (can each definition ever be the unique winner?)
- realistic space scanned: 405 (cpu1-5, gpu1-3, panel1-3, ssd1-3, mem1-3)
- states: {'SINGLE': 17, 'SINGLE_WITH_RESERVATION': 357, 'RANGE': 31}
- SKU2: unique-winner count = 83 | appearable-in-range = 2
- SKU3: unique-winner count = 39 | appearable-in-range = 5
- SKU4: unique-winner count = 147 | appearable-in-range = 31
- SKU5: unique-winner count = 0 | appearable-in-range = 29   <<< NOT REACHABLE AS A UNIQUE RECOMMENDATION
- SKU6: unique-winner count = 105 | appearable-in-range = 19

### Second wave (row 80 clause) input cpu2/gpu2/panel1/ssd2/mem2, 2nd SSD+Mem deferred
- Current Wave : SINGLE -> 3
- Full Project : SINGLE_WITH_RESERVATION -> 4
- [PASS] second wave splits into two SKU views current=3 full=4
- [PASS] second wave does not change base rates (only the SKU count fed in) 

### Unit isolation (workbook K3: PCBA items not in sample data)
- [PASS] PCBA rules are excluded from UNIT totals 

### Product names must never appear in SKU judgement
- [PASS] no product series token in judgement basis carries ranges only
- [FAIL] every SKU definition is reachable as a unique recommendation UNRESOLVED DESIGN GAP -> see Owner Review Item ORI-04
