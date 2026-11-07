-- Optional SQLite landing for review / archival / BI cross-check.
-- The MVP itself runs on packed rule JSON + browser IndexedDB; this schema exists so the
-- team can open the same data in Excel/BI without a server database.
-- All quantity columns are REAL and are NEVER rounded (approved decision D-01).
PRAGMA foreign_keys = ON;

CREATE TABLE source_file (
  sha256        TEXT PRIMARY KEY,
  file_name     TEXT NOT NULL,
  relative_path TEXT NOT NULL,
  size_bytes    INTEGER,
  mtime_local   TEXT,
  role          TEXT CHECK (role IN ('FORMAL_BUSINESS_INPUT','SUPPLEMENT','HISTORICAL_REFERENCE',
                                     'DUPLICATE','TEMP','UNREADABLE','UNKNOWN')),
  notes         TEXT
);

CREATE TABLE evidence (
  evidence_id  TEXT PRIMARY KEY,
  file_sha256  TEXT NOT NULL REFERENCES source_file(sha256),
  sheet        TEXT,
  cell_ref     TEXT,
  kind         TEXT CHECK (kind IN ('CELL','MERGED_RANGE','COMMENT','DOC_PROPERTY')),
  raw_value    TEXT,          -- verbatim, original spelling kept
  formula      TEXT,
  cached_value REAL,          -- stored as-is (float artefacts kept, D-01)
  author       TEXT,
  authored_at  TEXT
);

CREATE TABLE rule_pack (
  baseline_id      TEXT,
  version          TEXT,
  status           TEXT CHECK (status IN ('DRAFT_UNCONFIRMED_BY_OWNER','CONFIRMED','SUPERSEDED')),
  derived_from_sha TEXT NOT NULL REFERENCES source_file(sha256),
  generator        TEXT,
  PRIMARY KEY (baseline_id, version)
);

CREATE TABLE rule (
  rule_id       TEXT NOT NULL,
  rule_version  TEXT NOT NULL,
  baseline_id   TEXT NOT NULL,
  rule_type     TEXT CHECK (rule_type IN ('RATE_PER_SKU','ABSOLUTE_PER_PHASE','FIXED_PER_PHASE',
                        'SKU_DEFINITION','CONDITIONAL_INCREMENT','ODM_MODIFIER','DISPLAY_NOTE')),
  function_id   TEXT,
  category      TEXT CHECK (category IN ('RD','PA','CERT','VENDOR','MFG')),
  phase         TEXT CHECK (phase IN ('FVT','SIT')),
  unit          TEXT NOT NULL DEFAULT 'UNIT' CHECK (unit IN ('UNIT','PCBA')),
  payload_json  TEXT NOT NULL,
  status        TEXT NOT NULL CHECK (status IN ('CONFIRMED','DRAFT','CONFLICTED','DISABLED',
                        'NON_NORMATIVE','HISTORICAL_REFERENCE','NOT_A_RULE')),
  confidence    TEXT CHECK (confidence IN ('HIGH','MEDIUM','LOW')),
  applies_json  TEXT,
  superseded_by TEXT,
  PRIMARY KEY (rule_id, rule_version),
  FOREIGN KEY (baseline_id, rule_version) REFERENCES rule_pack(baseline_id, version)
);

-- Rules never carry evidence inline; they reference immutable evidence rows.
CREATE TABLE rule_evidence (
  rule_id     TEXT NOT NULL,
  rule_version TEXT NOT NULL,
  evidence_id TEXT NOT NULL REFERENCES evidence(evidence_id),
  PRIMARY KEY (rule_id, rule_version, evidence_id)
);

CREATE TABLE sku_definition (
  baseline_id  TEXT NOT NULL,
  version      TEXT NOT NULL,
  sku          INTEGER NOT NULL CHECK (sku BETWEEN 2 AND 6),
  cpu_low INTEGER, cpu_high INTEGER,
  gpu_low INTEGER, gpu_high INTEGER,
  panel_low INTEGER, panel_high INTEGER,
  ssd_low INTEGER, ssd_high INTEGER,
  mem_low INTEGER, mem_high INTEGER,
  context_note TEXT,               -- display only; never a rule
  second_wave_option INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL,
  PRIMARY KEY (baseline_id, version, sku),
  FOREIGN KEY (baseline_id, version) REFERENCES rule_pack(baseline_id, version)
);

CREATE TABLE owner_review_item (
  ori_id      TEXT PRIMARY KEY,
  title       TEXT NOT NULL,
  type        TEXT,
  severity    TEXT CHECK (severity IN ('MAJOR','MINOR')),
  blocking    INTEGER NOT NULL DEFAULT 0,
  finding     TEXT NOT NULL,
  impact      TEXT,
  options_json TEXT,
  agent_default TEXT NOT NULL,      -- interim, explicitly not a rule
  owner_decision TEXT,
  decided_at   TEXT
);

CREATE TABLE rule_conflict (
  conflict_id  INTEGER PRIMARY KEY AUTOINCREMENT,
  rule_id      TEXT,
  ori_id       TEXT REFERENCES owner_review_item(ori_id),
  description  TEXT NOT NULL,
  severity     TEXT CHECK (severity IN ('MAJOR','MINOR','OPEN')),
  sku          INTEGER,
  phase        TEXT,
  value_a      REAL,   -- REAL, not rounded (D-01)
  value_b      REAL,
  delta        REAL
);

-- ---------------- analysis records (append-only) ----------------

CREATE TABLE analysis (
  analysis_id   TEXT PRIMARY KEY,
  created_at    TEXT NOT NULL,
  project_name  TEXT NOT NULL,
  odm           TEXT CHECK (odm IN ('LCFC','HQ','Compal')),   -- recorded, not a driver (ORI-05)
  product_series TEXT,                                        -- display only
  wave_scope    TEXT CHECK (wave_scope IN ('CURRENT','FULL_PROJECT','BOTH')),
  baseline_id   TEXT, baseline_version TEXT,
  input_json    TEXT NOT NULL,     -- full snapshot incl. file/user/adopted values
  sku_state     TEXT CHECK (sku_state IN ('SINGLE','SINGLE_WITH_RESERVATION','RANGE','UNDETERMINED')),
  recommended_sku INTEGER,         -- NULL when RANGE/UNDETERMINED (no pseudo-precision)
  range_low INTEGER, range_high INTEGER,
  total REAL, fvt_total REAL, sit_total REAL,   -- REAL, never rounded (D-01)
  open_conflicts TEXT
);

CREATE TABLE key_factor (
  analysis_id TEXT NOT NULL REFERENCES analysis(analysis_id) ON DELETE CASCADE,
  name        TEXT NOT NULL CHECK (name IN ('cpu','gpu','panel','ssd','mem')),
  file_value  REAL,               -- NULL = not read; never defaulted to 0/1
  file_confidence REAL,
  user_value  REAL,
  user_edited INTEGER NOT NULL DEFAULT 0,
  effective   REAL,               -- NULL allowed -> 请补充
  source      TEXT CHECK (source IN ('USER','FILE','UNKNOWN')),
  status_user TEXT CHECK (status_user IN ('已读取','用户已修改','请确认','请补充')),
  PRIMARY KEY (analysis_id, name)
);

CREATE TABLE demand_line (
  analysis_id TEXT NOT NULL REFERENCES analysis(analysis_id) ON DELETE CASCADE,
  line_no     INTEGER NOT NULL,
  function_id TEXT NOT NULL,
  category    TEXT,
  phase       TEXT CHECK (phase IN ('FVT','SIT')),
  per_sku_rate REAL, sku_qty INTEGER,
  base_demand REAL NOT NULL,
  conditional_increment REAL NOT NULL DEFAULT 0,
  confirmed_reuse_adjustment REAL NOT NULL DEFAULT 0,
  risk_reserve REAL NOT NULL DEFAULT 0,
  recommended REAL NOT NULL,       -- REAL, never rounded (D-01)
  display     TEXT,                -- formatting only; never fed back into computation
  unit        TEXT NOT NULL DEFAULT 'UNIT' CHECK (unit IN ('UNIT','PCBA')),
  status      TEXT CHECK (status IN ('COMPUTED','NEED_INPUT','NEED_CONFIRM','NOT_COMPUTABLE')),
  status_user TEXT CHECK (status_user IN ('已计算','请补充','请确认','暂无法计算')),
  main_reason TEXT,
  rule_id TEXT, rule_version TEXT,
  evidence_cell TEXT,
  PRIMARY KEY (analysis_id, line_no)
);

CREATE TABLE reuse_item (
  reuse_id    INTEGER PRIMARY KEY AUTOINCREMENT,
  analysis_id TEXT NOT NULL REFERENCES analysis(analysis_id) ON DELETE CASCADE,
  kind        TEXT NOT NULL CHECK (kind IN ('CONFIRMED','POTENTIAL')),  -- POTENTIAL never subtracted
  function_id TEXT, phase TEXT, quantity REAL NOT NULL
);

CREATE TABLE plan_comparison (
  analysis_id TEXT NOT NULL REFERENCES analysis(analysis_id) ON DELETE CASCADE,
  function_id TEXT NOT NULL, phase TEXT NOT NULL,
  agent REAL, plan REAL, delta REAL, delta_percent REAL,   -- NULL delta_percent => UI shows N/A
  baseline_caveat TEXT,
  PRIMARY KEY (analysis_id, function_id, phase)
);

CREATE INDEX idx_demand_function ON demand_line(function_id, phase);
CREATE INDEX idx_rule_status     ON rule(status, rule_type);
CREATE INDEX idx_conflict_ori    ON rule_conflict(ori_id);

-- Golden check: the agent must reproduce the workbook's own totals.
CREATE VIEW v_golden_totals AS
SELECT sku_qty,
       SUM(CASE WHEN phase='FVT' THEN base_demand END) AS fvt_total,
       SUM(CASE WHEN phase='SIT' THEN base_demand END) AS sit_total,
       SUM(base_demand)                                AS total
FROM demand_line
GROUP BY sku_qty;
-- Expected (SKU2..6): 365 / 417 / 443.8 / 474 / 507
