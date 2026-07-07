# Playbook: Status report

Produce a consistent status artifact for steering, leadership, or your own record.

## When

- Per `project.yaml` cadence (e.g. weekly) or 48 hours before a steering meeting.

## Inputs

- `templates/status-report.md`
- RAID log excerpts if risks changed
- Metrics or milestones you track (paste or summarize—no live API required)

## Steps

1. **Executive summary** — 3–5 sentences: overall RAG, headline win, headline concern, ask (if any).

2. **Progress since last report** — outcomes, not activity lists.

3. **Plan next period** — dated milestones.

4. **Risks and issues** — link to RAID ids; include mitigation and owner.

5. **Dependencies** — external teams, vendors, approvals.

6. **Decisions needed** — specific options, recommendation, impact of delay.

7. **Review**
   - Read aloud once; remove jargon and duplicate bullets.
   - Save to `data/<slug>/` or `projects/<slug>/outputs/`.

## Done when

- An executive can skim section 1 only and know whether to intervene.

## AI prompt (Cursor)

> Draft a status report from `templates/status-report.md` for `<slug>`. I will paste facts below. RAG must be justified. Do not publish anywhere.
