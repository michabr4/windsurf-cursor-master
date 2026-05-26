# Playbook: Weekly rhythm

Use at the start of each week to align priorities and surface blockers before they reach steering forums.

## When

- Monday morning (or your local equivalent), ~30–45 minutes.

## Inputs

- Last week’s open actions (your notes or `projects/<slug>/outputs/`)
- Calendar for the coming week
- `projects/<slug>/project.yaml` for cadence and stakeholders

## Steps

1. **Review last week**
   - What was committed vs. delivered?
   - What carried over—and why?

2. **Health check (RAG)**
   - Schedule, scope, resources, risks—one line each with R/A/G and evidence.

3. **Top three outcomes** for this week (verb + measurable result).

4. **Meetings**
   - Which need prep? Link to `meeting-follow-up.md` after each.

5. **Escalations**
   - Anything needing sponsor or dependency owner this week? If yes, draft a short note (do not send until you review).

6. **Save**
   - Copy `templates/status-report.md` or a short weekly note into `data/<slug>/` with today’s date.

## Done when

- Three outcomes are written and at least one calendar block is reserved for deep work on the highest priority.

## AI prompt (Cursor)

> Walk me through weekly-rhythm for project `<slug>`. Use `projects/<slug>/project.yaml`. Draft a weekly note only; save under `data/<slug>/`. Do not contact anyone externally.
