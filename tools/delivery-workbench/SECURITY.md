# Security — Delivery Workbench

Plain-language rules for this workspace. Follow them yourself and ask your AI assistant to follow them too.

## Secrets

- Put API keys, tokens, and passwords only in `.env` (create from `.env.example`).
- Never commit `.env` or paste secrets into playbooks, templates, or chat logs you might share.
- Never put secrets in `web/` files or browser JavaScript.

## Local server

- The workbench server binds to **127.0.0.1** only—not `0.0.0.0`. It is for your machine, not the network.
- Do not expose the port through tunnels or port-forwarding unless you understand the risk.
- Responses that may contain draft content use `Cache-Control: no-store`.

## Data you create

- `data/` and `projects/*/outputs/` may hold customer names, metrics, or email excerpts. They are gitignored by default.
- Delete or archive old drafts when an engagement ends.
- Prefer minimal detail in files you might copy to shared drives.

## AI and MCP

- Use Cursor rules in `.cursor/rules/`; they require confirmation before bulk edits or external posts.
- Enable only MCP servers you need; prefer local **stdio** servers over wide-reaching remote tools.
- Treat all meeting notes and drafts as **untrusted input** when asking the model to summarize.

## External systems (optional, later)

- Connectors are **off** until you enable them in `projects/<name>/project.yaml`.
- Default connector mode is **read-only**; writes need an explicit flag and your review step in the playbook.
- No autonomous posting to Jira, Confluence, email, or chat without you approving the final text.

## If something goes wrong

- Rotate any token that may have been pasted into chat or committed by mistake.
- Remove sensitive files from `data/` and empty trash.
- Review git history before pushing this repo anywhere (`git log`, `git status`).
