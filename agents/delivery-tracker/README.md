# Delivery Tracker — Agent #1 (T1)

**Purpose:** Reduce weekly Helix case-review prep time from ~45 min to ~5 min review.
**Trust tier:** T1 — read-only, no HITL gate, no write-back to Helix.

## What it does

Pulls open cases, milestone completion %, SLA adherence, and overdue items from
the Helix REST API for all accounts the SDM owns, then renders a structured
weekly summary as a rich console table and/or a markdown file.

## Quick start

```bash
cd agents/delivery-tracker

# 1. Create virtual env and install dependencies
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure credentials
cp .env.example .env
# Edit .env — set HELIX_BASE_URL and HELIX_API_TOKEN

# 3. Validate config (no API calls)
python main.py --dry-run

# 4. Run
python main.py                    # console table
python main.py --output both      # console + markdown file in ./output/
python main.py --accounts "ACME"  # filter to accounts containing "ACME"
python main.py --lookback 14      # 14-day window instead of 7
```

## Environment variables

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `HELIX_BASE_URL` | Yes | — | Helix API base URL, e.g. `https://helix.example.com/api/v1` |
| `HELIX_API_TOKEN` | Yes | — | Bearer token from Helix admin portal |
| `HELIX_TIMEOUT` | No | `30` | HTTP timeout (seconds) |
| `LOOKBACK_DAYS` | No | `7` | Case update lookback window |
| `ACCOUNT_FILTER` | No | all | Substring filter on account name |
| `OUTPUT_DIR` | No | `./output` | Directory for markdown reports |
| `LOG_LEVEL` | No | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

## Project structure

```text
agents/delivery-tracker/
├── AGENT_CARD.md          # design & governance document
├── README.md              # this file
├── .env.example           # environment variable template
├── requirements.txt       # Python dependencies
├── config.py              # pydantic-settings configuration
├── models.py              # Pydantic data models
├── helix_client.py        # Helix REST API client (read-only)
├── tracker.py             # agent orchestrator
├── report_formatter.py    # console + markdown rendering
├── main.py                # CLI entry point
└── tests/
    ├── conftest.py
    ├── test_helix_client.py
    └── test_tracker.py
```

## Running tests

```bash
pytest tests/ -v
```

## Helix API mapping

| Agent data need | Helix endpoint |
| --- | --- |
| Account list | `GET /accounts` |
| Open cases | `GET /cases?account_id=&status=open,in_progress,pending_customer` |
| Overdue cases | `GET /cases?account_id=&overdue=true` |
| Milestones | `GET /milestones?account_id=` |
| SLA metrics | `GET /sla/metrics?account_id=&period_start=&period_end=` |

> **Note:** These endpoint paths follow a conventional REST pattern. Adjust
> `helix_client.py` if your Helix instance uses different paths or response shapes.

## Governance

- T1: no data is written back; output is display-only for SDM review.
- Token stored in `.env` only — never committed to source control.
- All HTTP calls are GET; retry logic handles transient 5xx and 429.
- Per-account errors are logged as warnings and surfaced in the summary
  `errors` field — the agent continues processing remaining accounts.
