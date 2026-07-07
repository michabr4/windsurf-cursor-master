---
description: Comms Bridge — Windsurf outbox monitor and task dispatch
alwaysApply: true
---

## Comms Bridge — Windsurf

**Session start:** Silently call `check_outbox`. If results waiting → surface with brief summary (task ID, status, one line). If empty → say nothing.

**Pipeline status:** If user asks "pipeline status" → call `get_pipeline_status`, show inbox/active/outbox/completed counts.

**Send task:** Call `send_task` with: `title` (short imperative), `spec` (exact file paths), `priority` (critical/high/medium/low), `phase`, `files_to_read`, `depends_on`. Confirm task ID to user.

### Auto-dispatch (SMART AUTO-CHAIN mode)

**Fast-path (`requires_review: false`):** Auto-archive → check inbox for next eligible task (`depends_on` satisfied) → dispatch immediately. Announce: `"Auto-dispatching → [task-id] — [title]"`. No user permission needed.

**Review-path (`requires_review: true`):** Surface to user → wait for "approve / revise / reject". On approval: archive + dispatch next.

**Failed result:** Stop all auto-dispatch. Surface: `"Task [ID] failed — [reason]. Pausing pipeline."` Wait for explicit instruction.

### MCP Fallback
If MCP tools fail: read `.comms/outbox/` via filesystem, write tasks to `.comms/inbox/` as JSON. Log: `"MCP unavailable — using filesystem fallback"`. Do not stall pipeline.
