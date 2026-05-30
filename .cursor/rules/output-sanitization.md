---
description: Output Sanitization — prohibits secrets and file contents from result files, session logs, and comms messages
alwaysApply: true
---

# Output Sanitization Rule

## What Must NEVER Appear in Any Output File

These must never be written to `.comms/outbox/`, `.session-logs/`, or any log or result file:

### Secret Patterns — Auto-Reject These Strings
- AWS keys: strings starting with `AKIA`, `AGPA`, `AIDA`, `AROA`, `ASIA`
- Stripe keys: `sk_live_`, `pk_live_`, `sk_test_`, `pk_test_`
- Google API: starts with `AIza` + 35 chars
- GitHub tokens: `ghp_`, `gho_`, `ghu_`, `ghs_`, `ghr_`
- JWT tokens: three base64 segments separated by dots, starting with `eyJ`
- Private key blocks: `-----BEGIN ... KEY-----` ... `-----END ... KEY-----`
- Connection strings with credentials: `://user:password@`
- Any environment variable VALUE (only the variable NAME is safe)

### Content Never Belongs in Output
- File contents — reference by path only, never paste content
- API response bodies — summarize with status code and record count
- Database rows or query results
- PII: emails, names, phone numbers, customer IDs

## What IS Safe to Write

- File paths (not contents)
- Function and class names
- Error messages and stack traces (after stripping embedded values)
- HTTP status codes
- Aggregate counts: "12 records updated", "3 tests passed"
- Task IDs, commit SHAs, PR numbers

## Session Log Restriction (session-activity-log rule)

Reports written to `.session-logs/` must contain ONLY:
- Task/work item titles
- File paths that were changed (not their contents)
- Issue descriptions in plain text (no values, no code snippets)
- Next steps as plain text

## Enforcement

Before writing any output file, scan the content mentally for the secret patterns above.
If a match is found: replace with `[REDACTED — <pattern-type>]` and note the sanitization in `details`.
Never omit the redaction note — Windsurf needs to know a value was present.
