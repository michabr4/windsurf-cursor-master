# Email assistant (work M365)

Personal productivity agent for **one primary mailbox** via Microsoft Graph. Designed for orchestration, not single-project playbooks.

## Scope (v1)

| In scope | Out of scope (v1) |
|----------|-------------------|
| Primary work mailbox (UPN in `.env`) | Shared mailboxes |
| Read: triage, summarize, actions, follow-ups | Auto-send / auto-reply |
| Draft replies (you send in Outlook) | Unattended folder moves |
| Morning digest ~7:00 (after Graph works) | |
| Cursor interactive + scheduled job | |

## Modes

- **Interactive:** `orchestration/email-inbox-review.yaml` — full six capabilities; organize only after you approve.
- **Scheduled:** `orchestration/email-morning-digest.yaml` — read/analyze only; no moves, no mass drafting.

## Outputs

All runs write under `data/runs/email/<run-id>/` (gitignored). Nothing is sent externally without you.

## Blocked on IT

Admin must register an Azure AD app and grant consent. See [IT_ADMIN_REQUEST.md](IT_ADMIN_REQUEST.md).

Until then, use `--sample` runs with pasted content or fixture files.

## Specialists

See `agents/specialists/email/` and the orchestration YAML files.
