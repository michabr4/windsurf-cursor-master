---
description: Comms Protocol — Windsurf ↔ Cursor task handoff
alwaysApply: true
---

# Comms Protocol

This workspace uses a file-based message queue in `.comms/` for task handoff between Windsurf (Architect) and Cursor (Builder).

## Checking for Tasks

When the user says "check inbox", "check for tasks", or "any tasks from Windsurf":

1. Read all `.json` files in `.comms/inbox/`
2. Display them sorted by priority (critical > high > medium > low)
3. For each task, show: ID, priority, title, and phase
4. Ask the user which task to execute (or execute the highest priority one)

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
