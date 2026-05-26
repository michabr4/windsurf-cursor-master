# Automation Study Hub App Scaffold

Monorepo scaffold for an automation study app with:

- `frontend/` React (Vite) UI
- `backend/` FastAPI service
- `data_model/` schema and seed data

## One-command startup

From `ccna_automation_github_app/`:

```bash
make dev
```

This will auto-install missing dependencies and start:

- Backend on `http://127.0.0.1:8000`
- Frontend (Vite) on its default local dev port

Additional root commands:

- `make stop` — stop backend/frontend dev processes
- `make fmt` — run `ruff format` (backend) + `prettier` (frontend)
- `make lint` — run `ruff` (backend) + `eslint` (frontend)
- `make test` — run `pytest` (backend) + `vitest` (frontend)

## Frontend

```bash
cd frontend
npm install
npm run dev
```

## Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API Endpoints

- `GET /health`
- `POST /api/plan`
- `GET /api/flashcards?domain=...`
- `POST /api/weak-areas`

## Notes

This is a starter scaffold focused on structure and initial flow for:

1. Learning plan generation
2. Flashcard retrieval
3. Weak-area detection

## MGM Daily Status Report Workflow

This repository includes a GitHub Actions workflow at
`.github/workflows/mgm-daily-status-report.yml`.

Required GitHub repository secrets:

- `WEBEX_BOT_TOKEN` (required)

Optional secrets (used only for recordings analysis step):

- `WEBEX_ACCESS_TOKEN`
- `OPENAI_API_KEY`

Set secrets in GitHub at:

`Settings` -> `Secrets and variables` -> `Actions` -> `New repository secret`
