---
description: Session Warm-Up — load minimal context at session start; never re-read full session logs or completed comms
alwaysApply: true
---

# Session Warm-Up Protocol

## Problem

Full session activity logs are 500–2,000 tokens each. Reading them at session start
to "catch up" is expensive — the information is already encoded in the files changed.
The `.comms/completed/` directory (51+ files) must never be scanned for context.

## What to Read at Session Start

**Read only:**

1. `.session-logs/LAST_SESSION_BRIEF.md` if it exists — max 200 tokens (see format below)
2. Any file in `.comms/active/` — to resume in-progress work only
3. Files explicitly listed in the active task's `files_to_read`

**Never read at session start:**

- Full `activity-report-*.md` files from `.session-logs/`
- The `.comms/completed/` directory
- `PROJECT_PROGRESS.md` unless the active task explicitly requires it
- Any file not referenced by the current task

## LAST_SESSION_BRIEF.md Format

At session end, before generating the full activity report, write this file:

```markdown
# Last Session Brief
**Date:** YYYY-MM-DD  **Agent:** [Windsurf|Cursor]
**Files changed:** path/a.py, path/b.ts (+ N more if over 5)
**Key decisions:** one sentence max per decision, max 3 total
**Active task:** TASK-ID or "none"
**Next priority:** one sentence
```

Cap this file at 200 tokens. It replaces reading the full activity report.

## Savings

- Full session log ~1,000 tokens → brief ~200 tokens = **800 tokens saved per session start**
- Over 20 sessions/month = **16,000 tokens/month** saved
