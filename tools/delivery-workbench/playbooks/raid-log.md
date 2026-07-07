# Playbook: RAID log

Maintain risks, assumptions, issues, and dependencies in one place.

## When

- When a new risk appears, an assumption is challenged, an issue is opened, or a dependency slips.
- Weekly: 10-minute scan during `weekly-rhythm.md`.

## Inputs

- `templates/raid-entry.md`
- Prior RAID entries in `projects/<slug>/outputs/`

## Steps

1. **Classify** — Risk, Assumption, Issue, or Dependency (one primary type).

2. **Describe** — What could happen / what is blocked / what we assume.

3. **Impact and probability** — Plain language; use numbers only if you have them.

4. **Owner and date** — Who drives mitigation; when is the next review.

5. **Mitigation** — Concrete steps, not “monitor closely.”

6. **Status** — Open, monitoring, closed (with closure note).

7. **Save** — Append or update a master `raid-log.md` under `projects/<slug>/outputs/`.

## Done when

- Every open item has an owner and next review date within 14 days.

## AI prompt (Cursor)

> Add this item to the RAID log for `<slug>` using `templates/raid-entry.md`. Merge with existing `projects/<slug>/outputs/raid-log.md` if present. Draft only.
