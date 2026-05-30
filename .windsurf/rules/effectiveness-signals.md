---
description: Effectiveness Signals — monitor and surface project health, quality, and velocity signals across all active projects
alwaysApply: true
---

# Effectiveness Signals Protocol

## Purpose

Surface measurable signals that indicate whether each project is producing real value — not just activity. Track quality, velocity, health, and approval rates per project category. Flag degradation early.

This rule operates alongside `project-progress-tracker.md` (which tracks status) and `session-activity-log.md` (which tracks work done). This rule tracks **whether the work is working**.

---

## When to Run a Signal Audit

Run a signal audit when **any** of these occur:

1. **Session start** — silently check signal state and flag any degraded project (red/amber)
2. **Cursor result reviewed** — after reading a `RESULT-*.json` from outbox, score the result
3. **Milestone claimed** — any project moves to 75%+ progress
4. **Manual trigger** — user asks "signal check", "effectiveness review", or "health check"

---

## Signal Categories by Project Type

### 1. AI Agents (`agents/`)
Track in each agent's `AGENT_CARD.md` under a `## Effectiveness Signals` section.

| Signal | Definition | Green | Amber | Red |
|--------|-----------|-------|-------|-----|
| **Run success rate** | Successful runs ÷ total runs (last 10) | ≥ 90% | 70–89% | < 70% |
| **HITL approval rate** | Human-approved outputs ÷ presented (last 10) | ≥ 80% | 60–79% | < 60% |
| **Cycle time** | Trigger → output delivery (median) | < 5 min | 5–15 min | > 15 min |
| **Error rate** | Exceptions ÷ total runs (last 10) | < 5% | 5–15% | > 15% |
| **LLM fallback rate** | Fallback responses ÷ total LLM calls | < 10% | 10–25% | > 25% |
| **Output coverage** | Required fields present in output | 100% | 90–99% | < 90% |

### 2. Bots (`bots/`)
Track in each bot's `README.md` and in `PROJECT_PROGRESS.md`.

| Signal | Definition | Green | Amber | Red |
|--------|-----------|-------|-------|-----|
| **Uptime %** | Successful scheduled runs ÷ total scheduled (last 30 days) | ≥ 95% | 85–94% | < 85% |
| **Token validity** | Auth token passes pre-run check | Valid | Expiring soon (< 7 days) | Expired / 401 |
| **Consecutive failures** | Count of uninterrupted run failures | 0 | 1–2 | ≥ 3 |
| **Message delivery rate** | Messages delivered ÷ attempted | ≥ 99% | 95–98% | < 95% |
| **Alert lag** | Time from failure to human awareness (minutes) | < 30 min | 30–120 min | > 120 min |

### 3. Platforms (`platforms/`)
Track in platform `CHANGELOG.md` and `PROJECT_PROGRESS.md`.

| Signal | Definition | Green | Amber | Red |
|--------|-----------|-------|-------|-----|
| **Build success rate** | CI/CD passing runs ÷ total runs (last 14 days) | ≥ 95% | 85–94% | < 85% |
| **Test coverage** | Lines covered ÷ total lines | ≥ 70% | 50–69% | < 50% |
| **Deploy frequency** | Successful deploys per week | ≥ 2/week | 1/week | < 1/week or stalled |
| **API health** | p95 response time (ms) | < 500 ms | 500–2000 ms | > 2000 ms |
| **Open P0/P1 issues** | Count of critical unresolved issues | 0 | 1 | ≥ 2 |

### 4. Tools (`tools/`)
Track in tool `README.md` and `PROJECT_PROGRESS.md`.

| Signal | Definition | Green | Amber | Red |
|--------|-----------|-------|-------|-----|
| **Build clean** | `npm run build` exits 0 with no TS errors | Yes | Warnings only | Errors |
| **Data freshness** | Age of primary data source | < 24 h | 1–7 days | > 7 days |
| **Dev server stability** | `npm run dev` starts without crashes | Yes | Starts with warnings | Crashes |

### 5. AI Factory Pipeline (cross-cutting)
Track in `PROJECT_PROGRESS.md` under `## AI Factory Effectiveness`.

| Signal | Definition | Green | Amber | Red |
|--------|-----------|-------|-------|-----|
| **Agent promotion rate** | Agents at 75%+ ÷ total In Development | ≥ 50% | 25–49% | < 25% |
| **Phase 0 ops completion** | Resolved ops blockers ÷ total | 100% | 60–99% | < 60% |
| **Cursor task success rate** | `success` results ÷ total results (last 10) | ≥ 80% | 60–79% | < 60% |
| **Rework rate** | Tasks requiring follow-up fix ÷ total tasks | < 10% | 10–25% | > 25% |
| **Cycle time per agent** | Scaffold → HITL ready (weeks) | < 6 wk | 6–10 wk | > 10 wk |

---

## Signal Audit Output Format

When running a signal audit, emit this block (do not write a new file — append inline to session or include in PROJECT_PROGRESS.md update):

```
## Effectiveness Signal Audit — YYYY-MM-DD HH:MM

| Project | Category | Signal | Value | Status |
|---------|----------|--------|-------|--------|
| mgm-status-bot | Bot | Uptime % | ~0% (BROKEN) | 🔴 Red |
| dd-status-bot | Bot | Token validity | Expired | 🔴 Red |
| delivery-tracker | AI Agent | Run success rate | No runs yet | ⚪ No data |
| serviceflow-sdm | Platform | Build success rate | ~95% | 🟢 Green |
| firewall-dashboard | Tool | Build clean | Clean | 🟢 Green |
| AI Factory pipeline | Cross-cutting | Phase 0 ops completion | 2/6 (33%) | 🔴 Red |

**Summary:** 2 🔴 Red · 0 🟡 Amber · 1 🟢 Green · N ⚪ No data
**Recommended action:** Rotate Webex tokens (unblocks 2 Red → Green immediately)
```

---

## Degradation Alerts

If any signal is Red, emit this notice **once** at session start (do not repeat during session):

```
⚠️  SIGNAL ALERT: [N] project(s) have degraded effectiveness signals.
    Red: [project names] — [one-line reason]
    See PROJECT_PROGRESS.md § Ops Blockers for remediation steps.
```

Do not alert on Amber signals at session start — only mention them when discussing that project directly.

---

## Signal Instrumentation Requirements

When Cursor builds or modifies any agent, bot, or platform component, the following signals **must be instrumentable** (the code must produce the data):

- **Agents:** `[METRICS]` line printed at every `run()` exit (see `ai-factory-standards.md`)
- **Bots:** Token pre-validation function runs before any API call; logs `[TOKEN_CHECK] valid=True/False expires_in=Nd`
- **Platforms:** CI/CD workflow must report build time and test count in workflow summary
- **Tools:** `npm run build` must be clean before any Cursor task is marked complete

These are **acceptance criteria** — a Cursor result that does not include them is **partial**, not complete.

---

## Security

- Signal values logged in AGENT_CARD.md or PROJECT_PROGRESS.md must never include token values, credentials, or PII.
- Log only counts, percentages, durations, and boolean pass/fail — not raw API responses.
- If a signal value would expose sensitive data (e.g., error message with token), replace with `[redacted]`.
