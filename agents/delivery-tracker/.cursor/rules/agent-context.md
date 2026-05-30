---
description: Delivery Tracker Agent — local context rules
alwaysApply: true
---

# Delivery Tracker Agent — Local Rules

## Agent Identity

- **Trust Tier:** T1 (Read-Only — no human approval gate required)
- **Primary API:** Helix REST API (`HELIX_BASE_URL` env var)
- **Auth:** Bearer token (`HELIX_API_TOKEN` env var)
- **Output:** `WeeklySummary` Pydantic model; formatted by `report_formatter.py`

## Module Layout

All imports within this agent are local (no `agents.delivery-tracker` prefix):

```python
from config import get_settings, Settings
from helix_client import HelixClient, HelixAPIError
from models import (
    HelixAccount, HelixCase, HelixMilestone, HelixSLARecord,
    AccountCaseMetrics, WeeklySummary,
    CaseStatus, Priority, SLAStatus, MilestoneStatus,
)
from tracker import DeliveryTracker
from report_formatter import ReportFormatter
```

Entry point: `main.py` — instantiates `DeliveryTracker`, calls `run()`, passes to `ReportFormatter`.

## Key Data Models (`models.py`)

### Enums

- `CaseStatus` — `open`, `in_progress`, `pending_customer`, `resolved`, `closed`
- `Priority` — `critical`, `high`, `medium`, `low`
- `SLAStatus` — `met`, `at_risk`, `breached`
- `MilestoneStatus` — `not_started`, `in_progress`, `complete`, `overdue`

### Raw Helix Entities

- `HelixAccount` — `id`, `name`, `account_manager`, `segment`, `contract_end_date`
- `HelixCase` — `id`, `case_number`, `title`, `status`, `priority`, `account_id`, `is_escalated`; computed: `age_days`, `is_overdue`
- `HelixMilestone` — `id`, `name`, `account_id`, `status`, `due_date`, `completion_pct`
- `HelixSLARecord` — `account_id`, `target_pct`, `actual_pct`; computed: `status` → `SLAStatus`

### Aggregated Summaries

- `AccountCaseMetrics` — `account_id`, `account_name`, `total_open`, `critical_high`, `overdue`, `escalated`, `avg_age_days`, `sla_status`, `milestone_completion_pct`
- `WeeklySummary` — aggregate root; `accounts: List[AccountCaseMetrics]`, `total_open_cases`, `total_overdue`, `total_escalated`, `accounts_at_risk_sla`, `errors`; computed: `has_errors`

## AI Factory Standard Methods (`tracker.py`)

- `trust_tier: str = "T1"` — class attribute
- `validate_inputs()` — raises `ValueError` if `HELIX_BASE_URL` or `HELIX_API_TOKEN` missing
- `handle_error(exc)` — logs and re-raises
- `run()` — calls `validate_inputs()`, tracks `records`/`errors` counters, prints `[METRICS]` before returning

## Settings Defaults (`config.py` / `.env.example`)

| Variable | Default |
| --- | --- |
| `HELIX_BASE_URL` | *(required, no default)* |
| `HELIX_API_TOKEN` | *(required, no default)* |
| `HELIX_TIMEOUT` | `30` (seconds) |
| `LOOKBACK_DAYS` | `7` |
| `ACCOUNT_FILTER` | `None` (all accounts) |
| `OUTPUT_DIR` | `./output` |
| `LOG_LEVEL` | `INFO` |

## Testing Conventions

- All tests in `tests/`; shared fixtures in `tests/conftest.py`
- Patch targets use full dotted paths: `tracker.HelixClient`, `tracker.HelixAPIError`
- Never hit the real Helix API in tests — always mock `HelixClient` methods
- `test_tracker.py` covers `trust_tier`, `validate_inputs`, `handle_error`, `run()` paths
- `test_helix_client.py` covers `HelixClient` HTTP interactions (mocked with `responses` or `unittest.mock`)

## Security Rules (Non-Negotiable)

- `HELIX_API_TOKEN` value must NEVER appear in source code
- All credentials via `.env` only; `.env` is in `.gitignore`
- HTTPS enforced for all Helix API calls (verify `HELIX_BASE_URL` starts with `https://`)
- Bearer token passed only via `Authorization` header — never in URL query parameters
