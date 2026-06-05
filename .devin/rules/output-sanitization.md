---
description: Output Sanitization — prohibits secrets and file contents from task specs, result files, and session logs
alwaysApply: true
---

# Output Sanitization Rule (Windsurf)

## Task Specs Must Never Contain

When writing task specs to send to Cursor, NEVER include:

- Actual secret values — use variable names only (e.g., `WEBEX_CLIENT_SECRET`, not the value)
- File contents pasted inline — use `files_to_read` + file path instead
- JWT tokens, API keys, private keys, or connection strings with passwords
- PII: customer names, emails, account IDs

## Session Log Restriction

Reports written to `.session-logs/` must contain ONLY:
- Task/work item titles
- File paths changed (not file contents)
- Issue descriptions in plain text (no values, no code snippets)
- Next steps as plain text

## Comms Message Sanitization

Before sending any task to Cursor via `.comms/inbox/`, verify the `spec` field contains no secrets.
If a spec requires referencing a secret, write: "Use the value of `ENV_VAR_NAME` from `.env`" — never the value itself.

## Secret Pattern Reference

Never put any string matching these in a spec or log:
- `AKIA*`, `sk_live_*`, `pk_live_*`, `AIza*`, `ghp_*`, `eyJ*.eyJ*.*`
- `-----BEGIN ... KEY-----` blocks
- `://user:password@host` connection strings
