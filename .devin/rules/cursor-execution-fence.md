---
description: Cursor Execution Fence — reference for Windsurf when writing task specs; defines what Cursor may and may not run
alwaysApply: true
---

# Cursor Execution Fence (Windsurf Reference)

This rule documents what Cursor is and is not permitted to run autonomously. Use this when writing task specs to avoid requesting forbidden operations.

## Pre-Approved (Cursor runs without asking)

- Test runners, formatters, linters
- `pip install -r requirements.txt`, `npm install` (no net-new packages)
- Read-only git operations
- `git add <file>` + `git commit` (no force flags)
- Filesystem reads (`find`, `grep`, `cat`, `ls`)

## Requires User Approval (do not include in fast-path tasks)

- `git push` in any form
- File deletions (`rm`, `rmdir`)
- Adding net-new pip/npm packages
- Database migrations
- `.env` write operations

## Forbidden (never put these in a task spec)

- `git push --force` or `git reset --hard` on remote branches
- SQL without `WHERE` clauses (`DROP TABLE`, `DELETE FROM`)
- `curl <url> | bash`
- Global package installs
- Disabling security tooling

## Spec Writing Rule

If a task requires an approval-needed command, set `requires_review: true` and `fast_path: false` in the task JSON — Cursor will stop and surface it for review before executing that step.
