---
description: Risk & Escalation Sentinel Agent — local context rules
alwaysApply: true
---

# Risk & Escalation Sentinel — Local Rules

## Agent Identity

- **Trust Tier:** T2 (HITL — Webex card sent; human must approve before SDM acts)
- **Phase:** 1 (SDM Pilots, Agent #2)
- **Trigger:** Daily 8am scheduler, runs after Delivery Tracker completes
- **Input:** Latest Delivery Tracker JSON from `data/runs/delivery-tracker/`
- **Output:** `SentinelReport` JSON to `data/runs/risk-sentinel/`; Webex HITL card per HIGH risk

## Module Layout

All imports within this agent are local (no package prefix):

```python
from config import get_settings, Settings
from models import RiskTier, AccountRisk, SentinelReport, DeliveryTrackerRun
from risk_rules import RiskEvaluator
from webex_notifier import WebexNotifier
from sentinel import RiskEscalationSentinel
```

Entry point: `main.py` — accepts `--date YYYY-MM-DD` and `--dry-run` flags.

## Key Data Models (`models.py`)

### Enums

- `RiskTier` — `HIGH`, `MEDIUM`, `LOW`

### Core Models

- `AccountRisk` — `account_id`, `account_name`, `tier: RiskTier`, `triggered_rules: List[str]`, `summary`, `recommended_action`
- `SentinelReport` — `run_date`, `source_file`, `accounts_evaluated`, `high_risk: List[AccountRisk]`, `medium_risk: List[AccountRisk]`, `low_risk_count`, `webex_cards_sent`, `errors: List[str]`; computed: `has_errors`
- `DeliveryTrackerRun` — mirrors Delivery Tracker JSON output; `accounts: List[AccountSummary]`

### AccountSummary (input shape from Delivery Tracker)

Fields: `account_id`, `account_name`, `total_open`, `critical_high`, `overdue`, `escalated`, `avg_age_days`, `sla_status`, `sla_actual_pct`, `sla_target_pct`, `milestone_completion_pct`, `milestones_overdue`

## Risk Rules (`risk_rules.py`)

Five rules applied in order — first match sets tier (rules are not cumulative):

| Rule | Condition | Tier |
| --- | --- | --- |
| 1 | `critical_high > 0` and `avg_age_days > 48h` | HIGH |
| 2 | SLA breach predicted within 5 days (`sla_actual_pct` trending below `sla_target_pct`) | HIGH |
| 3 | Health score dropped > 15 pts in 7 days | HIGH |
| 4 | `milestones_overdue > 0` and slip > 2 weeks | MEDIUM |
| 5 | Entitlement utilization < 20% and renewal < 60 days | MEDIUM |

Accounts matching no rule → `LOW`.

## AI Factory Standard Methods (`sentinel.py`)

- `trust_tier: str = "T2"` — class attribute
- `validate_inputs()` — raises `ValueError` if `DATA_DIR` doesn't exist on disk OR `WEBEX_BOT_TOKEN` is empty (unless `dry_run=True`)
- `handle_error(exc)` — logs and re-raises
- `run(run_date)` — calls `validate_inputs()`, loads delivery-tracker JSON, evaluates risks, sends Webex cards for HIGH risks, writes report JSON, prints `[METRICS]` before returning

## Settings Defaults (`config.py` / `.env.example`)

| Variable | Default |
| --- | --- |
| `DATA_DIR` | `./data/runs` |
| `WEBEX_BOT_TOKEN` | *(required unless dry_run)* |
| `WEBEX_ROOM_ID` | *(required unless dry_run)* |
| `HELIX_API_TOKEN` | *(optional — reserved for future enrichment)* |
| `LOOKBACK_DAYS` | `7` |
| `LOG_LEVEL` | `INFO` |
| `DRY_RUN` | `False` |

## Webex HITL Card

Each HIGH risk account generates one card with 4 buttons:

- **[Escalate Now]** → generates draft escalation text (human sends)
- **[Schedule Call]** → generates draft calendar invite language
- **[Snooze 48h]** → defers with reason logging
- **[Dismiss]** → logs decision + reason

## Testing Conventions

- All tests in `tests/`; shared fixtures in `tests/conftest.py`
- Patch targets: `sentinel.RiskEvaluator`, `sentinel.WebexNotifier`
- `test_sentinel.py` — covers `trust_tier`, `validate_inputs`, `handle_error`, `run()` paths (happy, missing file, validation failure)
- `test_risk_rules.py` — one test per rule, happy path + edge case (exactly at threshold, below threshold)
- Never hit real Webex API in tests — always mock `WebexNotifier.send_high_risk_card`

## Security Rules (Non-Negotiable)

- `WEBEX_BOT_TOKEN` must NEVER appear in source code
- All credentials via `.env` only; `.env` is in `.gitignore`
- HTTPS enforced for all Webex API calls
- Bearer token passed only via `Authorization` header — never in URL query parameters
- Dry-run mode MUST skip all Webex network calls entirely
