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

1. `.windsurf/handoff/STATE.md` if it exists — max 400 tokens
2. `.session-logs/LAST_SESSION_BRIEF.md` if it exists — max 200 tokens
3. Any file in `.comms/active/` — to resume in-progress work only
4. Files explicitly listed in the active task's `files_to_read`

**Never read at session start:**

- Full `activity-report-*.md` files from `.session-logs/`
- The `.comms/completed/` directory
- `PROJECT_PROGRESS.md` unless the active task explicitly requires it
- Any file not referenced by the current task

## LAST_SESSION_BRIEF.md Format

At session end (or when writing the context handoff), write this file:

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

## Specialized Rule Catalog

Glob-gated rules auto-load only when matching file types are in context. You do NOT need to load them manually.

| Category | Auto-loads when editing |
| -------- | ----------------------- |
| Safe C functions | `*.c *.cc *.cpp *.h *.hpp` |
| Crypto algorithms | `*.c *.go *.h *.java *.js *.py *.ts` + others |
| Digital certificates | Above + `*.pem *.crt *.cer *.der` |
| Hardcoded credentials | `*.py *.ts *.js *.go *.sh *.json *.yml *.env*` |
| Framework security | `*.java *.js *.py *.rb *.ts *.php *.xml *.yml` |
| Effectiveness signals | `*.py *.ts *.js *.mjs` (agents & platforms) |
| Input validation / injection | `*.c *.go *.py *.ts *.js *.php *.sql *.sh` |
| API integration | `*.py *.ts *.js` |
| AI factory standards | `agents/**` and `platforms/**` |

For sessions with no code files open, none of these load.
