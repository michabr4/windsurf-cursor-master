# CCNA Automation Study Hub

**Primary purpose:** DEVASC-oriented study tool — flashcards, practice quiz, study planner, and weak-area detection.

| Feature | Description |
|---------|-------------|
| **Study hub** | React UI + FastAPI API (core product) |
| **Data** | SQLite with seeded domains, flashcards, and questions (`data/ccna_study.db`) |
| **Extended landscape** | Optional HTML import via `SOURCE_HTML_PATH` |
| **MGM Webex reports** | Separate script (`send_reports.py`) + [mgm-daily-status-report.yml](.github/workflows/mgm-daily-status-report.yml) — not part of the study UI |

Optional GitHub App webhook endpoints exist for future automation workflows; they are **not required** to run the study hub. See [docs/GITHUB_APP.md](docs/GITHUB_APP.md) only if you need that integration.

## Requirements

- **Python 3.11 recommended** (3.10–3.13 supported; **3.14** often fails to build `pydantic-core`)
- **Node.js 20+**

## Quick Start

### Backend

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --app-dir .
# Or from backend/: PYTHONPATH=. python -m app
```

API: http://127.0.0.1:8000 — OpenAPI docs at http://127.0.0.1:8000/docs

### Frontend

```bash
cd frontend
cp ../.env.example .env.local   # optional: set VITE_API_BASE
npm install
npm run dev
```

Visit http://localhost:5173

### One-command (repo root)

```bash
cp .env.example .env
make install && make dev
```

## Configuration

- **Backend:** [backend/.env.example](backend/.env.example) — `SOURCE_HTML_PATH`, `DATABASE_PATH`
- **Repo root:** [.env.example](.env.example) — frontend API URL, optional GitHub/Webex vars

## API endpoints (study hub)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness |
| GET | `/api/flashcards` | Flashcards |
| GET | `/api/practice-questions` | Practice questions |
| POST | `/api/plan` | Study plan |
| POST | `/api/weak-areas` | Weak-area detection |
| GET | `/api/source-package` | Optional HTML landscape (needs `SOURCE_HTML_PATH`) |
| GET | `/api/domains` | Domain list |

## MGM daily status (Webex)

Unrelated to the study app — posts to Webex rooms from `subscribers.json`.

```bash
WEBEX_BOT_TOKEN=... python send_reports.py
# DRY_RUN=true python send_reports.py
```

GitHub Actions: [.github/workflows/mgm-daily-status-report.yml](.github/workflows/mgm-daily-status-report.yml)  
CI for the study app: [.github/workflows/ci.yml](.github/workflows/ci.yml)

## Commands

```bash
make test    # pytest + vitest
make lint    # ruff + eslint
```

## Security

- Keep secrets in `.env` only (gitignored at app root).
- Do not commit `data/*.db` or private keys.
