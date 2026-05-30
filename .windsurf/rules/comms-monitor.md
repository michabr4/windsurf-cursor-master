---
description: Comms Bridge — Windsurf outbox monitor and task dispatch
alwaysApply: true
---

# Comms Bridge — Windsurf Side

This workspace uses a file-based message queue in `.comms/` for Windsurf ↔ Cursor handoff.

## Outbox Monitoring (Automatic)

Before sending your first reply in every conversation, silently call `check_outbox` via the comms-bridge MCP tool.

- If results are waiting: surface them immediately with a brief summary (task ID, status, summary line).
- If outbox is empty: say nothing — do not mention the check.
- Do NOT auto-archive or auto-act on results. Present them to the user and wait for instruction.

## Pipeline Status

If the user asks "what's in the pipeline", "pipeline status", or similar, call `get_pipeline_status` and show counts for all four queues (inbox / active / outbox / completed).

## Sending Tasks to Cursor

When the user approves dispatching work to Cursor, call `send_task` with:

- `title`: short imperative (e.g. "Implement mimirClient.ts")
- `spec`: full implementation spec — be specific, reference exact file paths
- `priority`: critical / high / medium / low
- `phase`: e.g. "P1 — Client + Auth"
- `files_to_read`: list of files Cursor should read first
- `depends_on`: upstream task ID if applicable

Confirm the task ID back to the user after sending.

## Handoff State

**Current mode: BATCH** — Cursor auto-executes one task per session. Windsurf is the bottleneck between tasks.

After reviewing a result in outbox:

- If approved: archive it (`archive_completed`) and ask the user whether to send the next task
- If revision needed: send a new task with `depends_on: <original-task-id>` describing the correction
- Do NOT auto-send the next task. User must explicitly say "send it" or "dispatch next"

Do not send tasks to Cursor without explicit user instruction.
