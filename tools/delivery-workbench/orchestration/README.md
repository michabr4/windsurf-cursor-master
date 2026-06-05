# Delivery Workbench — orchestration

Workflow YAML files describe how the workbench chains **repo-root agents** (`agents/forge`, `agents/status-report-agent`, `agents/communication-agent`) and local scripts. They are consumed by `python/orchestration/` and `scripts/morning-briefing.py`.

## Audit (TASK-015 baseline)

| Asset | Role |
|-------|------|
| `email-morning-digest.yaml`, `email-inbox-review.yaml` | **Workbench-native** Graph + specialist agents under `agents/specialists/email/` |
| `email-digest.yaml` | **Forge** triage (`agents/forge`) — executive summary + categories |
| `status-report.yaml` | **status-report-agent** — weekly metrics narrative |
| `communication-scan.yaml` | **communication-agent** — Webex/email attention scan |
| `python/integrations/agt001/` | Outlook “chief of staff” (separate from morning briefing) |
| `playbooks/`, `templates/` | Human + Cursor workflows; not auto-run |

Morning briefing (`scripts/morning-briefing.py`) runs **Forge → calendar placeholder → combined markdown**. Status and communication workflows are optional follow-ons (see script flags).

## Workflow file format

```yaml
name: workflow-id
version: 1
description: Human-readable summary

agent:
  path: agents/<agent-dir>    # relative to repo root
  entry: module.Callable

inputs:
  key: value

output:
  format: markdown | json
  section: "## Section title in combined brief"

error_handling:
  retry:
    max_attempts: 2
    backoff_seconds: 5
  fallback: placeholder_markdown | skip_section_with_todo
  notify: false                 # requires SMTP_* in .env
```

## Examples

**Dry-run morning brief (no API keys):**

```bash
cd tools/delivery-workbench
python3 scripts/morning-briefing.py --dry-run
```

Output: `data/runs/morning-briefing/YYYY-MM-DD.md` (gitignored).

**Include communication scan (needs Webex token):**

```bash
python3 scripts/morning-briefing.py --communication-scan
```

## Webex in morning briefing

Live Webex fetch is **not** wired into the default briefing sequence yet. `communication-scan.yaml` documents the agent contract; configure `agents/communication-agent/.env` and pass `--communication-scan` when ready.

## Security

- Secrets only in `.env` (never committed).
- `data/runs/**` is gitignored — briefings may contain inbox snippets.
- No outbound email/API without explicit flags and configured credentials.
