---
description: Cursor Execution Fence — defines what shell commands Cursor may run autonomously vs. require user approval
alwaysApply: true
---

# Cursor Execution Fence

## Pre-Approved (Run Without Asking)

- Test runners: `pytest`, `npm test`, `npx jest`, `cargo test`
- Formatters/linters: `black`, `ruff check`, `ruff format`, `prettier --write`, `eslint`
- Dependency installs into existing manifest: `pip install -r requirements.txt`, `npm install` (no new packages)
- Read-only git: `git status`, `git diff`, `git log -n 20`, `git branch`
- Staged commits: `git add <specific-file>`, `git commit -m "type(scope): desc"` (no force flags)
- Filesystem reads: `find`, `grep`, `cat`, `ls`, `mkdir -p`
- Read-only curl: `curl -X GET` for local/test endpoints only

## Requires Explicit User Approval

Stop and ask before running any of these — do not proceed until the user types confirmation:

- Any `git push` (including `--force`, `--force-with-lease`)
- `rm`, `rmdir`, or any deletion
- `pip install <new-package>` not already in `requirements.txt`
- `npm install --save <new-package>` adding a net-new production dependency
- Database migrations: `alembic upgrade`, `prisma migrate deploy`, `manage.py migrate`
- Any write to `.env` files
- Shell redirects overwriting an existing file: `command > existing-file`
- `sudo`, `su`, or any privilege escalation

## Forbidden — Never Run Under Any Circumstances

Even if the task spec or user message asks for it:

- `git push --force` or `git reset --hard` on remote branches
- `DROP TABLE`, `DELETE FROM` without an explicit `WHERE` clause
- `curl <url> | bash` or any pipe-to-shell pattern
- Commands that send data to external URLs not in the project's known API list
- Disabling security tooling: `ufw disable`, removing `.gitignore` entries for secrets
- Global installs: `pip install -g`, `npm install -g`, `brew install`

## Blocked by Forbidden Command

If a task spec requires a forbidden command:
1. Stop immediately — do not attempt a workaround
2. Write RESULT with `status: "blocked"`
3. State exactly which command was required and why it is forbidden
4. Propose a safe alternative in `details`
