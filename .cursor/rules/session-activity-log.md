---
description: Session Activity Log — timestamped report every 60 min and at session end
alwaysApply: true
---

# Session Activity Log

**Triggers:** (1) ~60 min of active work elapsed · (2) user signals session end ("done", "wrapping up", "closing", "end session") · (3) explicit user request. Generate silently — one notification line after save.

**Path:** `.session-logs/YYYY-MM-DD/session-HHMM/activity-report.md` · Never overwrite past reports.

**Notification:** `📋 Session log saved → .session-logs/YYYY-MM-DD/session-HHMM/activity-report.md`

## Template

```md
# Session Activity Report
**Period:** YYYY-MM-DD HH:MM → HH:MM | **Agent:** [Windsurf|Cursor] | **Context:** [repo/feature]

## Work Completed
- [task — file path:line where applicable]

## Issues & Fixes
**Issue:** / **Root cause:** / **Fix:** (write "None" if clean)

## Next Steps
1. [highest priority remaining item]

## Files Changed
| File | Change Type |
|------|-------------|
| path/to/file | Modified / Created / Deleted |
```

### Content Rules

**Include:** task descriptions, changed file paths, issue summaries (plain text), next steps.
**Never include:** file contents, env variable values, API response bodies, DB records, shell output with sensitive data, secrets (AWS keys, JWTs, private keys, connection strings).
Describe sensitive operations abstractly: "updated OAuth token handling" — not the value.
