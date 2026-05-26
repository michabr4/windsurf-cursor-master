CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  exam_date DATE,
  hours_per_week INTEGER NOT NULL,
  current_level TEXT NOT NULL
);

CREATE TABLE domains (
  id INTEGER PRIMARY KEY,
  code TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL
);

CREATE TABLE flashcards (
  id INTEGER PRIMARY KEY,
  domain_id INTEGER NOT NULL,
  question TEXT NOT NULL,
  answer TEXT NOT NULL,
  FOREIGN KEY (domain_id) REFERENCES domains(id)
);

CREATE TABLE quiz_results (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  domain_id INTEGER NOT NULL,
  score_percent REAL NOT NULL,
  attempts INTEGER NOT NULL DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (domain_id) REFERENCES domains(id)
);

CREATE TABLE study_plan_weeks (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  week_number INTEGER NOT NULL,
  focus_domains TEXT NOT NULL,
  goals TEXT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
