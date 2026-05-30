---
description: Project Progress Tracker — maintain PROJECT_PROGRESS.md at session start and after any project milestone
globs: "PROJECT_PROGRESS.md,ROADMAP.md,AI_FACTORY_IMPLEMENTATION_PLAN.md"
alwaysApply: false
---

# Project Progress Tracker Protocol

## Purpose

Keep a single authoritative file — `PROJECT_PROGRESS.md` in the workspace root — that reflects the current progress state of every active project. This file is the source of truth for the project dashboard and for cross-session continuity.

## When to Update PROJECT_PROGRESS.md

Update the file when **any** of these events occur:

1. **Session start** — read the file, verify it reflects reality, fix stale entries silently.
2. **Milestone completed** — a feature, phase, or agent ships.
3. **Status changes** — a project moves from one phase to another, or a blocker is resolved or added.
4. **New project created** — a new agent, tool, or platform folder is scaffolded.
5. **Manual trigger** — user asks "update progress" or "show project status".

## File Location

```text
PROJECT_PROGRESS.md  (workspace root)
```

Never rename or move this file.

## Project Entry Schema

Each project entry in `PROJECT_PROGRESS.md` follows this exact structure:

```markdown
### [Project Name]

| Field | Value |
|-------|-------|
| **Location** | `path/to/project/` |
| **Status** | [Planned / In Design / In Development / HITL Active / Stable / Blocked / Complete] |
| **Phase** | [Phase number and name from ROADMAP.md] |
| **Progress** | [0–100%] |
| **Last Updated** | YYYY-MM-DD |
| **ETA** | [Target date or sprint week, e.g., "Week 8 (2026-07-15)"] |
| **Blockers** | [None — or brief description] |

**Completed:**
- [bullet list of done items, most recent first]

**Remaining:**
- [bullet list of next required steps, priority order]

**Expected Outcome:**
[One sentence: what does "done" look like and what value does it deliver?]

---
```

## Completion Percentage Guide

Use these anchors consistently:

| % | Meaning |
|---|---------|
| 0% | Planned, not started |
| 10% | Agent card / spec written |
| 25% | Scaffold + directory structure created |
| 40% | Core logic implemented, not yet tested |
| 60% | Tests pass, integration pending |
| 75% | Integration complete, in pilot/HITL |
| 90% | HITL window active, governance log open |
| 100% | Governance gate passed, promoted |

## ETA Estimation Rules

- For **In Development** agents: estimate remaining weeks based on implementation plan sprint schedule.
- For **Planned** agents: use the phase timeline from `AI_FACTORY_IMPLEMENTATION_PLAN.md` as the baseline.
- For **Blocked** items: ETA is "TBD — blocked by [blocker]".
- Always flag if an ETA has slipped more than 2 weeks.

## Security

- `PROJECT_PROGRESS.md` must NEVER contain secrets, tokens, passwords, or connection strings.
- Status entries may reference `.env` files by name only — never by content.
- Blocker descriptions may name external services (Webex, Salesforce) but not credentials.

## Notification

After updating `PROJECT_PROGRESS.md`, emit exactly one line to the user:

> `📊 PROJECT_PROGRESS.md updated — [N] projects tracked, [N] blocked, [N] on track`

No further explanation unless the user asks.
