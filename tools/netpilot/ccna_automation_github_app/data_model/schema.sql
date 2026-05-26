CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  exam_date DATE,
  hours_per_week INTEGER NOT NULL,
  current_level TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS domains (
  id INTEGER PRIMARY KEY,
  code TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS flashcards (
  id INTEGER PRIMARY KEY,
  domain_id INTEGER NOT NULL,
  question TEXT NOT NULL,
  answer TEXT NOT NULL,
  FOREIGN KEY (domain_id) REFERENCES domains(id)
);

CREATE TABLE IF NOT EXISTS quiz_results (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  domain_id INTEGER NOT NULL,
  score_percent REAL NOT NULL,
  attempts INTEGER NOT NULL DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (domain_id) REFERENCES domains(id)
);

CREATE TABLE IF NOT EXISTS study_plan_weeks (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  week_number INTEGER NOT NULL,
  focus_domains TEXT NOT NULL,
  goals TEXT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS practice_questions (
  id INTEGER PRIMARY KEY,
  prompt TEXT NOT NULL,
  options_json TEXT NOT NULL,
  correct_option_index INTEGER NOT NULL,
  explanation TEXT NOT NULL,
  distractor_rationales_json TEXT NOT NULL DEFAULT '[]',
  references_json TEXT NOT NULL DEFAULT '[]',
  domain TEXT NOT NULL,
  source TEXT NOT NULL DEFAULT 'Original',
  policy_note TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS github_installations (
  id INTEGER PRIMARY KEY,
  installation_id INTEGER UNIQUE NOT NULL,
  account_login TEXT,
  account_type TEXT,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS github_webhook_events (
  id INTEGER PRIMARY KEY,
  delivery_id TEXT,
  event_type TEXT NOT NULL,
  action TEXT,
  installation_id INTEGER,
  payload_json TEXT NOT NULL,
  received_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS app_meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);
