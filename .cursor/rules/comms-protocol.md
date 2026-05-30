---
description: Comms Protocol — full task lifecycle, file move steps, result schema, and batch/chain execution rules
alwaysApply: true
---

# Comms Protocol

This workspace uses a file-based message queue in `.comms/` for task handoff between Windsurf (Architect) and Cursor (Builder).

## Automatic Inbox Check (Session Start)

Before sending your first reply in every conversation, silently check `.comms/inbox/` for pending tasks using the `check_inbox` MCP tool. If MCP is unavailable, read `.comms/inbox/*.json` directly from the filesystem.

**Current mode: SMART AUTO-CHAIN** — execute all consecutive eligible fast-path tasks without stopping. Only pause for `requires_review: true` or `status: failed`.

If tasks are waiting:

1. Claim the highest-priority eligible task immediately (no user prompt required)
2. Announce: `"Picked up [ID] — [title]. Executing now."`
3. Execute fully per the spec
4. Submit result to outbox
5. Apply auto-chain decision logic (see `auto-chain.md`):
   - If next task exists with `requires_review: false` and `fast_path: true` → auto-claim and execute immediately
   - If next task has `requires_review: true` → stop and announce: `"Task [ID] queued — requires Windsurf review before proceeding."`
   - If result was `failed` → stop all chaining, alert user
6. When chain is exhausted: `"Auto-chain complete. [N] tasks executed. Inbox clear."`

If inbox is empty at session start: say nothing.

## Checking for Tasks (Manual)

When the user says "check inbox", "check for tasks", or "any tasks from Windsurf":

1. Read all `.json` files in `.comms/inbox/`
2. Display them sorted by priority (critical > high > medium > low)
3. For each task, show: ID, priority, title, and phase
4. Claim and execute the top task immediately

## Executing a Task

1. Move the task file from `.comms/inbox/` to `.comms/active/`
2. Update the task's `status` field to `"in_progress"`
3. Read any files listed in `files_to_read`
4. Execute the instructions in the `spec` field
5. Follow all CodeGuard security rules during execution

## Reporting Results

After completing a task:

1. Create a result file: `.comms/outbox/RESULT-{task-id}.json`
2. Include: task ID, status (success/partial/failed/blocked), summary, details, files changed, issues found
3. Move the task from `.comms/active/` to `.comms/completed/`
4. Tell the user: "Result submitted to outbox. Tell Windsurf to check outbox."

## When Completing Any Work (Even Without an Inbox Task)

If `.comms/` exists and you complete a significant piece of work:

- Write a result file to `.comms/outbox/` summarizing what was done
- Use ID format: `ADHOC-{YYYY}-{MMDD}-{NNN}`

## Message Formats

See `.comms/schema.md` for full JSON schema definitions.

## Restructure policy (Architect)

Before scheduling refactor/restructure tasks, read:

`tools/netpilot/ccna_automation_github_app/docs/RESTRUCTURE_GUIDANCE.md`

Do not issue weekly refactors by default; use the trigger table in that doc (god file >800 lines, duplicate logic, phase-gate audit P1+, etc.).
