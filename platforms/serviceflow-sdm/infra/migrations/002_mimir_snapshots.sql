-- Wave 18 P3 — Cisco Mimir snapshot tables (append-only per sync)

CREATE TABLE IF NOT EXISTS cisco.mimir_inventory_snapshot (
  id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  synced_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  company_id   TEXT NOT NULL,
  device_name  TEXT,
  ip_address   TEXT,
  product_id   TEXT,
  sw_version   TEXT,
  device_role  TEXT,
  hw_eol_date  DATE,
  sw_eos_date  DATE,
  raw_json     JSONB
);

CREATE TABLE IF NOT EXISTS cisco.mimir_psirt_snapshot (
  id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  synced_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  company_id   TEXT NOT NULL,
  total_count  INT,
  critical     INT,
  high         INT,
  medium       INT,
  low          INT,
  raw_json     JSONB
);

CREATE TABLE IF NOT EXISTS cisco.mimir_fn_snapshot (
  id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  synced_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  company_id        TEXT NOT NULL,
  total_count       INT,
  affected_devices  INT,
  raw_json          JSONB
);

CREATE TABLE IF NOT EXISTS cisco.mimir_qbr_snapshot (
  id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  synced_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  company_id          TEXT NOT NULL,
  risk_composite      NUMERIC,
  psirt_score         NUMERIC,
  fn_score            NUMERIC,
  hw_lifecycle_score  NUMERIC,
  sw_lifecycle_score  NUMERIC,
  raw_json            JSONB
);

CREATE INDEX IF NOT EXISTS idx_mimir_inventory_company_synced
  ON cisco.mimir_inventory_snapshot (company_id, synced_at DESC);

CREATE INDEX IF NOT EXISTS idx_mimir_psirt_company_synced
  ON cisco.mimir_psirt_snapshot (company_id, synced_at DESC);

CREATE INDEX IF NOT EXISTS idx_mimir_fn_company_synced
  ON cisco.mimir_fn_snapshot (company_id, synced_at DESC);

CREATE INDEX IF NOT EXISTS idx_mimir_qbr_company_synced
  ON cisco.mimir_qbr_snapshot (company_id, synced_at DESC);
