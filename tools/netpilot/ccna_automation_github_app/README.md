# Automation Study Hub (+ GitHub App hooks)

Monorepo for a **DEVASC-oriented automation study app** with optional **GitHub App** webhooks and a separate **MGM Webex daily report** script.

| Area | Purpose |
|------|---------|
| `frontend/` | React (Vite) study UI |
| `backend/` | FastAPI API, SQLite persistence, GitHub webhooks |
| `data_model/` | SQL schema, seed JSON, domain map |
| `send_reports.py` | Webex status bot (scheduled via GitHub Actions) |

## Requirements

- **Python 3.10–3.13** (3.14 may fail to install `pydantic-core`; CI uses 3.11)
- **Node.js 20+**

## Quick start

```bash
cp .env.example .env
# Edit .env (VITE_API_BASE, optional GitHub App vars)

make install   # venv + npm
make dev       # API :8000, UI :5173
```

Or separately:

```bash
cd backend && python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. python -m app

cd frontend && npm install && npm run dev
```

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness |
| GET | `/docs` | OpenAPI (Swagger) |
| POST | `/api/plan` | Study plan from profile |
| GET | `/api/flashcards` | Flashcards (`?domain=`) |
| GET | `/api/practice-questions` | Practice questions |
| POST | `/api/weak-areas` | Weak-area detection |
| GET | `/api/source-package` | Optional HTML-derived content |
| GET | `/api/domains` | Domain titles from DB |
| POST | `/webhooks/github` | GitHub App webhooks |
| GET | `/api/github/status` | GitHub App config status |
| GET | `/api/github/installations` | Known installations |
| GET | `/api/github/events` | Recent webhook events |
| POST | `/api/github/installations/{id}/token` | Installation access token |

## Data

SQLite file defaults to `data/ccna_study.db` (gitignored). On startup the API applies `data_model/schema.sql` and seeds from `seed.json`, `domain_map.yaml`, and built-in question banks.

## GitHub App setup

1. Create a GitHub App with webhook URL `https://<your-host>/webhooks/github`.
2. Set webhook secret and note **App ID** + generate a **private key**.
3. Configure `.env`: `GITHUB_APP_ID`, `GITHUB_WEBHOOK_SECRET`, `GITHUB_APP_PRIVATE_KEY` or `GITHUB_APP_PRIVATE_KEY_PATH`.
4. Install the app on a repo; verify with `GET /api/github/events`.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## MGM daily status (Webex)

Workflow: [.github/workflows/mgm-daily-status-report.yml](.github/workflows/mgm-daily-status-report.yml)

Secrets: `WEBEX_BOT_TOKEN` (required), `WEBEX_ACCESS_TOKEN`, `OPENAI_API_KEY` (optional).

```bash
WEBEX_BOT_TOKEN=... python send_reports.py
# or DRY_RUN=true python send_reports.py
```

## Commands

- `make test` — pytest + vitest
- `make lint` / `make fmt` — ruff + eslint/prettier

## Security

- Secrets only in `.env` (see `.env.example`).
- Do not commit `data/*.db` or private keys.
