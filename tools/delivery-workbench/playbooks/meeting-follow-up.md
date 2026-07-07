# Playbook: Meeting follow-up

Turn meeting notes into clear actions and communication—without losing ownership.

## When

- Within 24 hours of any working session, steering prep, or vendor call.

## Inputs

- Raw notes (bullets are fine)
- `templates/meeting-notes.md`

## Steps

1. **Capture facts**
   - Decisions made (who agreed, what, by when).
   - Open questions (owner to resolve, due date).

2. **Action items**
   - Each action: owner, due date, dependency, definition of done.
   - Avoid passive voice (“monitoring will occur” → “Alex monitors metric X by Friday”).

3. **Risks or RAID**
   - New or changed items → `playbooks/raid-log.md` and `templates/raid-entry.md`.

4. **Communications**
   - Who must be informed but was not in the room? One paragraph max.

5. **Save and review**
   - Save filled template to `projects/<slug>/outputs/` or `data/<slug>/`.
   - You approve before any email or chat is sent.

## Done when

- Every action has one owner and one due date; decisions are quoted accurately.

## AI prompt (Cursor)

> From my notes below, fill `templates/meeting-notes.md` for project `<slug>`. List actions in a table. Draft a follow-up email in the template but do not send it.
