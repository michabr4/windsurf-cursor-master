# Connectors (optional, Phase 3)

Connectors are **add-ons**. The workbench works fully without them using playbooks, templates, and local drafts.

## Design principles

1. **Opt-in** — Listed in `projects/<slug>/project.yaml` under `connectors.enabled`.
2. **Read-only by default** — Writes require `connectors.<id>.allow_writes: true` and a human review step in the playbook.
3. **Secrets in `.env` only** — Connector code reads env vars; never hardcode tokens.
4. **One at a time** — Add and test a single connector before starting another.

## Layout (when you add one)

```
python/connectors/
└── <connector_id>/
    ├── README.md          # What it does, env vars, limits
    ├── client.py          # API calls (server-side only)
    └── __init__.py
```

## project.yaml example

```yaml
connectors:
  enabled:
    - example_vendor
  example_vendor:
    read_only: true
    allow_writes: false
```

## Suggested first steps to add a connector

1. Create `python/connectors/<id>/README.md` documenting required `.env` keys.
2. Implement read-only methods (e.g. fetch issue summary).
3. Add a playbook section marked **Optional connector** with explicit review before write.
4. Never call write APIs from the local web UI; use CLI or Cursor with user confirmation.

## Examples you might add later

| Connector | Typical use | Notes |
|-----------|-------------|--------|
| Atlassian | Issues, pages | OAuth or PAT in `.env`; respect rate limits |
| Outlook / Graph | Mail action items | Device or delegated auth; minimal scopes |
| Airtable | Tracker sync | Personal access token; table allow-list |

None of these ship with the greenfield workbench. Copy patterns from your own prior projects if needed—do not couple this repo to another template repository.

## Security checklist

- [ ] Token only in `.env`
- [ ] `read_only: true` until you need writes
- [ ] Playbook includes “draft → user reviews → publish”
- [ ] No customer PII in server logs
- [ ] MCP servers scoped to this project, not whole-disk access
