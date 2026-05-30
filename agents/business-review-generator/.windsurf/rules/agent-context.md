---
description: Business Review Generator Agent — local context rules
alwaysApply: true
---

# Business Review Generator — Local Rules

## Agent Identity

- **Trust Tier:** T2 (Draft-first HITL — SDM/CXM reviews and approves every draft before customer delivery)
- **Phase:** 1 (SDM Pilots, Agent #3)
- **Trigger:** On-demand CLI — never scheduled, never autonomous
- **Primary Users:** Service Delivery Manager (SDM), Customer Experience Manager (CXM)
- **Output:** Structured QBR/EBR draft `.md` file; Webex notification to reviewer

## Module Layout

All imports within this agent are local (no package prefix):

```python
from config import get_settings, Settings
from models import AccountPeriodData, CaseMetrics, MilestoneMetrics, EntitlementMetrics, QBRSection, QBRDraft
from data_collector import DataCollector
from metrics_calculator import MetricsCalculator
from llm_writer import LLMWriter
from reviewer import BusinessReviewGenerator
```

Entry point: `main.py` — CLI with `--account`, `--quarter`, `--format`, `--dry-run` flags.

## CLI Usage

```bash
python main.py --account "Acme Corp" --quarter Q2-2026 [--dry-run] [--format md]
```

## Key Data Models (`models.py`)

- `AccountPeriodData` — aggregate of all data pulled for one account + quarter: helix data, salesforce data (may be empty stub), delivery tracker JSON supplement
- `CaseMetrics` — `case_velocity`, `sla_compliance_pct`, `open_count`, `critical_high_count`, `source_fields: List[str]`
- `MilestoneMetrics` — `on_time_pct`, `total_milestones`, `overdue_count`, `source_fields: List[str]`
- `EntitlementMetrics` — `utilization_pct`, `renewal_days_remaining`, `source_fields: List[str]`
- `QBRSection` — `title`, `content`, `source_data_present: bool`, `llm_generated: bool`
- `QBRDraft` — `account`, `quarter`, `generated_at`, `sections: List[QBRSection]`, `missing_data_flags: List[str]`, `draft_path`

## Data Sources

| Source | Status | Behavior when unavailable |
| --- | --- | --- |
| Helix REST API | ✅ Ready | Raise `ValueError` — required |
| Salesforce MCP | 🟡 Pending ops | Return empty `SalesforceData(source="stub")` — log warning, continue |
| Delivery Tracker JSON | Optional | Load latest from `data/runs/delivery-tracker/` if present |

**Salesforce stub rule:** If `SALESFORCE_MCP_TOKEN` is unset, `DataCollector.fetch_salesforce_data()` returns a stub without raising. Never crash on missing Salesforce data.

## AI Factory Standard Methods (`reviewer.py`)

- `trust_tier: str = "T2"` — class attribute
- `validate_inputs(account, quarter)` — raises `ValueError` if `account` is empty string or `HELIX_API_TOKEN` is missing
- `handle_error(exc)` — logs and re-raises
- `run(account, quarter)` — calls `validate_inputs()`, collects data, computes metrics, runs 4 LLM passes, saves draft, sends Webex notification, prints `[METRICS]` on all exit paths

## Four LLM Passes (`llm_writer.py`)

| Pass | Section | Content |
| --- | --- | --- |
| 1 | Executive Summary | 3–5 sentences, business language, grounded in data |
| 2 | Delivery Performance | Narrative on case velocity, SLA, milestones |
| 3 | Risk & Issues | Open issues, overdue items, escalation flags |
| 4 | Next Quarter Priorities | Recommended actions + priorities |

**LLM fallback:** If `LLM_MODEL` unset or `--dry-run`, each pass returns a clearly marked placeholder:

```text
[DRAFT — REVIEW REQUIRED]
<Section Title>: Data collected for {account} ({quarter}).
[LLM generation skipped — set LLM_MODEL in .env to enable]
```

**Metric validation rule:** Every metric value appearing in LLM output must trace to a `source_fields` citation. If source data was absent, section is flagged in `missing_data_flags`.

## Settings Defaults (`config.py` / `.env.example`)

| Variable | Default |
| --- | --- |
| `HELIX_API_TOKEN` | *(required)* |
| `HELIX_BASE_URL` | *(required)* |
| `SALESFORCE_MCP_TOKEN` | *(optional — stub used when unset)* |
| `WEBEX_BOT_TOKEN` | *(optional — notification skipped when unset)* |
| `WEBEX_ROOM_ID` | *(optional)* |
| `DATA_DIR` | `./data/runs` |
| `LLM_MODEL` | *(optional — placeholder text used when unset)* |
| `LLM_BASE_URL` | *(optional)* |
| `LOG_LEVEL` | `INFO` |

## Draft Output

- Saved to: `data/runs/business-review/YYYY-MM-DD-{account_slug}.md`
- Template: `templates/business-review-template.md`
- Human gate: SDM/CXM must review, edit if needed, and explicitly approve before any version is shared with customer — **agent never sends autonomously**

## Testing Conventions

- All tests in `tests/`; shared fixtures in `tests/conftest.py`
- Patch targets: `reviewer.DataCollector`, `reviewer.LLMWriter`, `reviewer.MetricsCalculator`
- `test_reviewer.py` — covers `trust_tier`, `validate_inputs`, `handle_error`, `run()` happy path, run with Salesforce stub (must not crash), `[METRICS]` printed on all exits
- `test_metrics.py` — one test per metric function; assert `source_fields` list is non-empty in output
- Never hit real Helix, Salesforce, Webex, or LLM APIs in tests

## Security Rules (Non-Negotiable)

- `HELIX_API_TOKEN`, `SALESFORCE_MCP_TOKEN`, `WEBEX_BOT_TOKEN` must NEVER appear in source code
- All credentials via `.env` only; `.env` is in `.gitignore`
- HTTPS enforced for all external API calls; `timeout=15` on all HTTP requests
- Draft files saved locally only — no customer-facing delivery by the agent
