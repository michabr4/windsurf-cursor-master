-- ServiceFlow SDM backend MVP schema (PostgreSQL mode)

CREATE TABLE IF NOT EXISTS users (
  user_id UUID PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  role TEXT NOT NULL,
  password_hash TEXT NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS properties (
  property_id UUID PRIMARY KEY,
  property_code TEXT NOT NULL,
  property_name TEXT NOT NULL,
  city TEXT,
  state TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS devices (
  device_id UUID PRIMARY KEY,
  property_id UUID NOT NULL REFERENCES properties(property_id),
  hostname TEXT NOT NULL,
  serial_number TEXT,
  model TEXT,
  status TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS incidents (
  incident_id UUID PRIMARY KEY,
  incident_number TEXT UNIQUE NOT NULL,
  property_id UUID REFERENCES properties(property_id),
  device_id UUID REFERENCES devices(device_id),
  title TEXT NOT NULL,
  description TEXT,
  priority TEXT NOT NULL,
  status TEXT NOT NULL,
  reported_by UUID NOT NULL REFERENCES users(user_id),
  assigned_to UUID,
  tac_case_number TEXT,
  tac_severity TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS incident_updates (
  update_id UUID PRIMARY KEY,
  incident_id UUID NOT NULL REFERENCES incidents(incident_id),
  user_id UUID NOT NULL REFERENCES users(user_id),
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tac_cases (
  tac_case_id UUID PRIMARY KEY,
  case_number TEXT UNIQUE NOT NULL,
  incident_id UUID REFERENCES incidents(incident_id),
  severity TEXT NOT NULL,
  title TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_events (
  event_id UUID PRIMARY KEY,
  action_type TEXT NOT NULL,
  action TEXT NOT NULL,
  entity_type TEXT,
  entity_id TEXT,
  user_id TEXT,
  request_id TEXT NOT NULL,
  success BOOLEAN NOT NULL,
  detail TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
