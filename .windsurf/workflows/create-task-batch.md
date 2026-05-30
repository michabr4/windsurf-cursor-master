---
description: How to create a batch of related tasks for Cursor to minimize session startup overhead
---

# Create Task Batch

Use this workflow whenever you have 2+ related tasks to send to Cursor. Never send 1 task per session if they are logically sequential.

## Step 1 — Decompose

Break the work into 3–5 tasks where:
- Each task has a single, bounded scope (1–3 files max)
- Tasks are ordered so each can start after the previous completes
- Assign `model` and `complexity` per the routing table in `.comms/schema.md`

## Step 2 — Set `depends_on` Chain

Link tasks sequentially using `depends_on`:

```
TASK-A: depends_on: null
TASK-B: depends_on: "TASK-A"
TASK-C: depends_on: "TASK-B"
```

Cursor will execute all three in one session without restarting.

## Step 3 — Write Bounded Specs

Each `spec` must include (see `.windsurf/rules/task-spec-standard.md`):
- Exact file paths to touch
- Function/interface contract for new code
- What "done" looks like (1 sentence)
- `out_of_scope` array

## Step 4 — Send Tasks

Use `mcp3_send_task` for each task. Send them in order (A before B before C) so Cursor sees the dependency chain correctly.

## Step 5 — Tell the User

After sending: "Sent [N]-task batch: TASK-A → TASK-B → TASK-C. Tell Cursor to check inbox — it will execute all in one session."

## Batching Rules

| Scenario | Do This |
|----------|---------|
| 1 simple task (haiku) | Still send — no batching needed |
| 2+ tasks in the same feature area | Batch with depends_on chain |
| Tasks that can run in parallel | Send separately but tell user they can open two Cursor sessions |
| Tasks for different projects | Never batch — separate sessions intentional |

## Anti-Pattern to Avoid

Do NOT send one task, wait for result, then send the next as a new session. This wastes:
- Session startup context (~141 lines × number of sessions)
- Inbox check overhead per session
- Re-establishing task context per session
