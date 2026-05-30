---
description: Read Deduplication — never re-read a file that was already read earlier in the same session
alwaysApply: true
---

# Read Deduplication Protocol

## Core Rule

**Within a single session, each file is read at most once.** If you have already read
a file, reference its contents from memory — do not call the read tool again unless
the file was explicitly modified since the last read.

## When a Re-Read IS Allowed

A re-read is permitted only if:

1. The file was written or edited after the last read in this session, OR
2. The task explicitly states "re-read [filename]", OR
3. The read occurred more than 120 minutes ago in the same session

## What to Do Instead of Re-Reading

- Reference the specific lines or sections recalled from the earlier read
- Cite as `@filepath:line-line` so the user can verify
- If uncertain whether content changed, check the edit diff rather than re-reading the full file

## High-Risk Re-Read Patterns to Avoid

These are common unnecessary re-reads that waste tokens:

- Reading `context-budget.md` after already reading it to "confirm" the file cap rules
- Reading `session-activity-log.md` to "check the template" before writing a report
- Reading a Python file to understand a function, then re-reading it before editing
- Reading `PROJECT_PROGRESS.md` at session start AND again when asked to update it

## Token Impact

Average file read: 500–2,000 tokens (depending on file size).
Eliminating 3 unnecessary re-reads/session × 800 avg = **2,400 tokens/session**.
Over 20 sessions/month = **48,000 tokens/month** saved.

This is the **single highest-impact behavioral rule** in this ruleset.
