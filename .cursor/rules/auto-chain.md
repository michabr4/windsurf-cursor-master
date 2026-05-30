---
description: Auto-Chain — Cursor automatically executes the next queued task when requires_review is false
alwaysApply: true
---

# Auto-Chain Protocol

## Decision Logic After Any Task Completes

```text
IF completed.status IN ["success", "partial"]
  AND inbox has task T where:
    T.depends_on == completed.id OR T.depends_on == null
    AND T.requires_review == false
    AND T.fast_path == true
THEN
  Auto-claim T → announce "Auto-chaining → [T.id] — [T.title]" → execute

ELSE IF T.requires_review == true (or field absent)
  Stop. Tell user: "Task [T.id] requires Windsurf review. Result submitted to outbox."

ELSE IF completed.status == "failed"
  Stop all auto-chaining. Alert user. Wait for instruction.

ELSE IF completed.status == "blocked"
  Check for other independent tasks with requires_review: false
  If found → auto-chain to those (skip blocked task, note it)
  If none → stop and alert user
```

## Auto-Chain Rules

- Treat `requires_review` absent or null as `true` — safe default is to pause
- Never skip an unsatisfied `depends_on` dependency (prerequisite must be in `completed/`)
- Multiple independent fast-path tasks: execute in priority order (critical → high → medium → low)
- Session depth cap: **10 tasks per session** — then stop and surface a batch summary

## Announcing Auto-Chain

One line only per task pickup:

> `Auto-chaining → TASK-2026-MMDD-NNN — [title]`

No preamble. Do not re-explain the auto-chain rule. Do not ask for permission.

## Session Summary When Chain Ends

When inbox is empty or only review-path tasks remain:

> `Auto-chain complete. [N] tasks executed. [M] task(s) awaiting Windsurf review. [Inbox clear | X review-path tasks remain in inbox.]`
