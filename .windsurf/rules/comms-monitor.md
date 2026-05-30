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

**Current mode: SMART AUTO-CHAIN** — Windsurf auto-dispatches the next eligible task after reviewing a fast-path result. User intervention is only required for `requires_review: true` results.

### After reviewing a result in outbox

**Fast-path result (`requires_review: false`):**
1. Auto-archive it (`archive_completed`)
2. Check inbox for the next eligible task: `depends_on` satisfied AND `requires_review: false`
3. If found → dispatch it immediately. Announce: `"Auto-dispatching → [task-id] — [title]"`
4. If inbox is empty → announce: `"Pipeline clear. No tasks queued."`
5. Do NOT ask the user for permission on fast-path dispatch.

**Review-path result (`requires_review: true`):**
1. Surface the result to the user with a clear summary
2. Wait for explicit user instruction: "approve", "revise", or "reject"
3. On approval: archive + dispatch next eligible task (fast-path auto, review-path waits again)
4. On revision: send a new task with `depends_on: <original-task-id>`

**Failed result (any path):**
1. Stop all auto-dispatch immediately
2. Surface to user: "Task [ID] failed — [reason]. Pausing pipeline. Review before continuing."
3. Wait for explicit user instruction before resuming

### Sending Tasks

When the user instructs a new task, call `send_task` with full spec. For queued batches, dispatch all fast-path tasks immediately in priority order without waiting for user confirmation between each.

### MCP Fallback

If `check_outbox` or `send_task` MCP tools fail with transport error:
1. Read `.comms/outbox/` directly via filesystem
2. Write new tasks directly to `.comms/inbox/` as JSON files
3. Log: `"MCP unavailable — using filesystem fallback"`
4. Do NOT stall the pipeline waiting for MCP to recover
