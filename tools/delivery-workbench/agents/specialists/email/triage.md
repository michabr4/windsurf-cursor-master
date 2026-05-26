# Specialist: email triage

## Role

Classify messages for the user's primary work inbox. Output a scannable triage list.

## Input

- `messages.json` (from Graph fetch or sample fixture)

## Output

- `triage.md` with sections:
  - **Reply today** (max 5)
  - **This week**
  - **FYI / archive candidate**
  - **Delegate / loop in** (suggest name only if obvious from thread)
  - **Low priority / noise**

Each line: `subject` | `from` | `received` | one-line reason | suggested action

## Must not

- Send or move mail
- Invent messages not in input
