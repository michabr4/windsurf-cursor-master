# When to restructure (Architect → Builder policy)

**Audience:** Windsurf (Architect) issuing tasks to Cursor (Builder)  
**Scope:** Monorepo projects under `tools/`, `platforms/`, `agents/`

## Default rule

**Do not issue a dedicated “restructure” task during feature work.** Cursor should ship the smallest correct change. Restructure only when triggers below are met.

## Issue a restructure task when ANY of these are true

| Trigger | Metric / signal | Suggested task type |
|---------|-----------------|---------------------|
| **God file** | Single UI or module file **> 800 lines** and still growing | `refactor-split-{component}` |
| **Duplicate logic** | Same business rules copied in **3+** places | `refactor-dedupe-{area}` |
| **Layer violation** | UI imports DB drivers, or scripts bypass API boundaries | `refactor-boundaries-{app}` |
| **Post-audit debt** | Audit lists “split monolith” as **P1+** and feature freeze agreed | Phase follow-up task |
| **Pre-release hardening** | Within **2 weeks** of declared “production-ready” for that app | `refactor-stabilize-{app}` |
| **Template vs ops mix** | Operational assets inside a **shareable template** repo path | `refactor-split-template` (see TASK-006 pattern) |

## Do NOT restructure when

- A feature task can be done in **< 200 lines** without new abstractions
- Tests are red or build is broken (fix first)
- No clear owner path (`tools/X` vs `platforms/Y`) — run **audit-first** instead
- The only goal is “cleaner code” with no measurable trigger above

## Cadence (standing)

| When | Who | Action |
|------|-----|--------|
| **After each phase gate** (e.g. 2.1, 3.2) | Windsurf | Review audit “next sprint”; schedule **at most one** refactor task per app per phase |
| **Monthly** (idle week) | Windsurf | Optional `refactor-{app}-hygiene` if god-file or dupes appeared |
| **Never weekly by default** | — | Avoid refactor churn without triggers |

## CCNA app (`ccna_automation_github_app`) — current status

| Item | Status (May 2026) |
|------|-------------------|
| Constants / session / study utils extracted | Done |
| `useStudyHubBootstrap`, `usePersistedStudyState` hooks | Done |
| `App.jsx` still hosts tab UI (~1.1k lines) | **Next restructure only if** adding major new tabs or file **> 800 lines** after feature work |
| Split tab panels (`MissionControl`, `QuizArena`, …) | Defer until new feature touches those sections |

## Task spec template for Windsurf

```text
CURSOR INSTRUCTION: REFACTOR-{APP}-{AREA}

TASK: Restructure {path} — {reason from trigger table}
LOCATION: {repo path}
DEPENDS_ON: {last audit or feature task}

CONSTRAINTS:
- No behavior change (tests must pass)
- No new features
- Max {N} files touched

VERIFICATION:
- npm run test && npm run build (or pytest equivalent)
- Line count of target file before/after in result
```

## Builder handback

After refactor tasks, Cursor writes to `.comms/outbox/` with:

- Before/after line counts
- List of new modules
- Whether further split is still recommended
