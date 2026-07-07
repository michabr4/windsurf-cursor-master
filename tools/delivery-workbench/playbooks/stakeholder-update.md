# Playbook: Stakeholder update

Short, audience-appropriate updates for sponsors and partners who do not need full status depth.

## When

- Ad hoc requests, pre-steering summaries, or monthly sponsor notes.

## Inputs

- Latest status draft or `templates/status-report.md` sections 1, 4, 6
- `projects/<slug>/project.yaml` stakeholder list

## Steps

1. **Audience** — Pick one primary reader (sponsor vs. technical lead vs. vendor).

2. **One message, three blocks**
   - **Headline** — RAG + one sentence why.
   - **What changed** — max 3 bullets.
   - **Ask** — zero or one clear request with deadline.

3. **Tone** — Direct, no blame; facts before interpretation.

4. **Review**
   - Remove internal names or sensitive metrics if the channel is broad.
   - You send manually after review.

## Done when

- The update fits on one screen and the ask (if any) is actionable in under five minutes.

## AI prompt (Cursor)

> Draft a stakeholder update for `<slug>` aimed at the executive sponsor. Use my status notes below. Under 200 words. Do not send email or post anywhere.
