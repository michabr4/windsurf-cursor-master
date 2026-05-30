# Comms Protocol Schema

## Overview

This directory is the message bus between Windsurf (Architect) and Cursor (Builder).
Both IDEs read and write JSON files here using their native filesystem capabilities.

## Directory Structure

```text
.comms/
├── inbox/       ← Windsurf writes tasks here for Cursor
├── outbox/      ← Cursor writes results here for Windsurf
├── active/      ← Task currently being executed (moved from inbox)
├── completed/   ← Archived task+result pairs
└── schema.md    ← This file
```

## Task Message (Windsurf → Cursor)

**Filename:** `TASK-{YYYY}-{MMDD}-{NNN}.json`
**Location:** `.comms/inbox/`

```json
{
  "id": "TASK-2026-0526-001",
  "from": "windsurf",
  "to": "cursor",
  "priority": "high",
  "type": "instruction",
  "phase": "0.5",
  "title": "Short task description",
  "spec": "Full instruction text. Can be multi-line.",
  "depends_on": null,
  "files_to_read": [],
  "out_of_scope": [],
  "model": "sonnet",
  "complexity": "MEDIUM",
  "created_at": "2026-05-26T12:30:00-04:00",
  "status": "pending"
}
```

**Fields:**

- `id` — Unique task ID, matches filename
- `from` — Always "windsurf"
- `to` — Always "cursor"
- `priority` — "critical" | "high" | "medium" | "low"
- `type` — "instruction" | "review-request" | "question"
- `phase` — Roadmap phase reference (e.g., "0.5", "1", "2.1")
- `title` — Short human-readable description
- `spec` — Full instruction text. Must include: exact files to touch, expected output, and what "done" looks like.
- `depends_on` — ID of prerequisite task, or null
- `files_to_read` — Array of file paths Cursor must read before starting (be precise — do not omit or over-include)
- `out_of_scope` — Array of files or concerns explicitly excluded from this task
- `model` — Target model: `"haiku"` | `"sonnet"` | `"opus"` — see routing table below
- `complexity` — `"LOW"` | `"MEDIUM"` | `"HIGH"` — HIGH triggers reasoning-first protocol
- `created_at` — ISO 8601 timestamp
- `status` — "pending" (set by Windsurf)

**Model Routing Table:**

| Task type | `model` | `complexity` |
|-----------|---------|-------------|
| Simple edits, config changes, rename, log adds, formatting | `haiku` | `LOW` |
| Standard implementation, APIs, scripts, tests | `sonnet` | `MEDIUM` |
| Complex agent logic, auth flows, orchestration, data schema | `opus` | `HIGH` |
| Security review, debugging unclear root causes | `opus` | `HIGH` |

## Result Message (Cursor → Windsurf)

**Filename:** `RESULT-{task-id}.json`
**Location:** `.comms/outbox/`

```json
{
  "id": "TASK-2026-0526-001",
  "from": "cursor",
  "to": "windsurf",
  "type": "result",
  "status": "success",
  "summary": "One-line result description",
  "details": "Full report of what was done",
  "files_changed": [],
  "issues": [],
  "completed_at": "2026-05-26T12:45:00-04:00",
  "next_recommended": null
}
```

**Fields:**

- `id` — Matches the task ID
- `from` — Always "cursor"
- `to` — Always "windsurf"
- `type` — "result" | "question" | "blocker"
- `status` — "success" | "partial" | "failed" | "blocked"
- `summary` — One-line result
- `details` — Full report
- `files_changed` — Array of files modified during execution
- `issues` — Array of issues encountered
- `completed_at` — ISO 8601 timestamp
- `next_recommended` — Suggested next task ID, or null

## Lifecycle

1. Windsurf creates `TASK-*.json` in `inbox/` (status: pending)
2. User tells Cursor to "check inbox"
3. Cursor reads task, moves it to `active/`, updates status to "in_progress"
4. Cursor executes the spec
5. Cursor writes `RESULT-*.json` to `outbox/`
6. User tells Windsurf to "check outbox"
7. Windsurf reads result, reviews, archives both to `completed/`
8. Windsurf issues next task

## Priority Levels

- **critical** — Security issue or blocker. Execute immediately.
- **high** — Current phase work. Execute next.
- **medium** — Important but not blocking.
- **low** — Nice to have. Execute when idle.
