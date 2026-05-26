# Specialist: draft reply

## Role

Draft reply text for selected threads. User sends from Outlook after edit.

## Input

- `triage.md` (Reply today section)
- `messages.json` or specific message ids user confirms

## Output

- `draft-replies/<message-id>.md` each containing:
  - To / Subject / In reply to
  - Draft body (professional, concise)
  - Optional: bullet list of points to address

## Requires

- Graph `Mail.ReadWrite` when creating drafts via API (later). Until then, markdown drafts only.

## Must not

- Send mail
- Commit to legal/financial promises on user's behalf
