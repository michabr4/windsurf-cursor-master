# Delivery Workbench

Structured local workspace for service delivery work.

This is a **standalone** project: playbooks, templates, and a small local home page. It does not require Jira, Confluence, email APIs, or any cloud keys to get started.

## What you get

- **Playbooks** — step-by-step guides for your weekly rhythm, meetings, status, RAID, and stakeholder updates
- **Templates** — copy-ready markdown starters
- **Projects** — one folder per engagement (names and cadence only; no secrets in config)
- **Local home page** — optional browser UI at `http://127.0.0.1:8840/` (server binds to localhost only)
- **Cursor rules** — security and human-approval guardrails for AI-assisted work

## Quick start

1. Open this folder in **Cursor** (File → Open Folder).
2. Read [GETTING_STARTED.md](GETTING_STARTED.md) once.
3. Copy `.env.example` to `.env` if you use the local server or CLI.
4. Start the server (optional):

   ```bash
   python3 python/server/workbench_server.py
   ```

   Then open `http://127.0.0.1:8840/` in your browser.

5. Pick a playbook under `playbooks/` and ask Cursor to walk you through it for a project.

Scaffold a draft: `./scripts/workbench.sh new-status-draft --project _example`

## Daily use

- **Structure:** Follow a playbook; save drafts under `data/` or `projects/<name>/outputs/`.
- **AI:** Ask the agent to help fill templates—never to post externally without your explicit approval.
- **Integrations:** Optional later via `python/connectors/` (see [docs/CONNECTORS.md](docs/CONNECTORS.md)).

## Email assistant (work M365)

Primary mailbox only, agent-orchestrated workflows:

- [docs/email/OVERVIEW.md](docs/email/OVERVIEW.md)
- [docs/email/IT_ADMIN_REQUEST.md](docs/email/IT_ADMIN_REQUEST.md) — send to IT for Graph consent
- Orchestration: `orchestration/email-inbox-review.yaml`, `orchestration/email-morning-digest.yaml`

**Minimal IT (live inbox):** use Microsoft Graph PowerShell — see [docs/email/MINIMAL_IT.md](docs/email/MINIMAL_IT.md) and `./scripts/email_fetch.sh`.

Without any login, use **sample mode**: `./scripts/email_fetch.sh --sample`

## Security

See [SECURITY.md](SECURITY.md). Summary: secrets in `.env` only; nothing sensitive in git; local server on `127.0.0.1` only; you review before any external publish.
