# WebEx_Email_Comm_Intelligence Agent Runbook

## 1) Daily Run Command

Use this for a one-time manual run:

```bash
python main.py --days 7 --output-all
```

Use this for continuous runtime (recommended):

```bash
python scheduler.py
```

Daily operator checks:

- Confirm new files are generated in `output/`
- Review high-priority and overdue actions first
- Verify Webex and Microsoft Graph authentication is still valid

## 2) Weekly Review Process

Every week, perform this sequence:

1. Quality review

- Sample 20 extracted actions
- Validate customer/internal classification accuracy
- Check due-date inference quality

1. Priority tuning

- Update `.env` keyword lists:

  - `HIGH_PRIORITY_KEYWORDS`
  - `MEDIUM_PRIORITY_KEYWORDS`

- Re-run agent and compare changes in high-priority counts

1. Source coverage review

- Confirm all key Webex spaces are represented
- Confirm meeting transcripts are still being pulled
- Confirm email volume is in expected range

1. Reporting handoff

- Share `report_*.md` with stakeholders
- Import `actions_*.csv` into task tracker if needed

## 3) Escalation Workflow (High Priority)

Trigger escalation when any of these occur:

- High-priority actions increase sharply week-over-week
- Any customer action is overdue
- Repeated extraction failures from one or more sources

Escalation steps:

1. Immediate triage (within same business day)

- Open latest report and isolate high-priority items
- Identify customer-facing overdue actions
- Assign a named owner for each critical action

1. Communication

- Notify stakeholders with:

  - Count of high-priority actions
  - List of overdue customer actions
  - ETA for mitigation

1. Corrective actions

- Fix auth/API issues first (Webex token, Graph app permissions)
- Re-run `python main.py --days 7 --output-all`
- If LLM is degraded, run fallback: `python main.py --no-llm`

1. Close-out criteria

- No overdue customer-critical actions
- Continuous scheduler healthy
- Latest report generated successfully

## Runtime Configuration (Continuous)

Set these in `.env`:

```env
RUNTIME_MODE=continuous
CONTINUOUS_BACKOFF_SECONDS=5
```

Then start continuous runtime:

```bash
python scheduler.py
```

Stop runtime with `Ctrl+C`.
