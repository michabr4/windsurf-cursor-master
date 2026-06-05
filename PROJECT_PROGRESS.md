# Project Progress Tracker

**Maintained by:** Windsurf (Architect) + auto-updated per `project-progress-tracker.md` rule  
**Last Updated:** 2026-05-29  
**Dashboard:** `tools/project-dashboard/` (build spec → `CURSOR_TASK_PROJECT_DASHBOARD.md`)

---

## Summary

| Metric | Count |
| ------ | ----- |
| Total active projects | 14 |
| On track | 8 |
| Blocked (ops) | 3 |
| Stable / Maintenance | 3 |
| Planned (not started) | 31 agents |

---

## Platform Projects

---

### Helix / ServiceFlow SDM

| Field | Value |
| ----- | ----- |
| **Location** | `platforms/serviceflow-sdm/` |
| **Status** | Stable |
| **Phase** | Phase 2.1 — Complete |
| **Progress** | 85% |
| **Last Updated** | 2026-05-26 |
| **ETA** | Ongoing — Phase 4 publish to GitHub Pages (July+) |
| **Blockers** | None — P3 deferred items (dashboard wiring, AsyncStorage, Docker verification) not blockers |

**Completed:**
- Production-hardened: JWT auth, rate limiting, Zod validation
- 5 of 7 frontend pages functional (build clean)
- Mobile: Expo SDK 52, API-driven screens
- Docker: multi-stage production builds
- Docs: README + CHANGELOG current
- Security: no hardcoded secrets, input validation

**Remaining:**
- Dashboard page wiring to live KPIs (currently placeholder)
- Mobile AsyncStorage settings persistence
- Docker build CLI verification
- GitHub Pages publish (Phase 4)
- Live Salesforce/ServiceNow data integration (Phase 4)

**Expected Outcome:**
Full-stack SDM platform serving as data backbone for all AI Factory agents, with live Salesforce/ServiceNow integration and stakeholder-accessible demo URL.

---

## AI Factory — Agent Pipeline

---

### Agent 1: Delivery Tracker

| Field | Value |
| ----- | ----- |
| **Location** | `agents/delivery-tracker/` |
| **Status** | In Development |
| **Phase** | Phase 1 — SDM Pilot Wave (Week 5–8) |
| **Progress** | 60% |
| **Last Updated** | 2026-05-27 |
| **ETA** | Week 8 (~2026-07-08) live pilot |
| **Blockers** | Webex bot token expired (ops — rotate at developer.webex.com) |

**Completed:**
- Agent card written and signed
- Directory scaffold: `main.py`, `config.py`, `tracker.py`, `models.py`, `helix_client.py`, `report_formatter.py`
- Dockerfile present
- Requirements defined
- Tests directory created

**Remaining:**
- Helix API client integration (live endpoint wiring)
- Health scoring implementation and validation
- Webex card push (blocked by expired token)
- Cron scheduling via GitHub Actions
- Live pilot: 100% portfolio coverage for 4 consecutive weeks

**Expected Outcome:**
Daily automated delivery health report covering 100% of accounts, reducing weekly check from 2–3 hours to a 5-minute review.

---

### Agent 2: Risk & Escalation Sentinel

| Field | Value |
| ----- | ----- |
| **Location** | `agents/risk-escalation-sentinel/` |
| **Status** | In Development |
| **Phase** | Phase 1 — SDM Pilot Wave (Week 9) |
| **Progress** | 25% |
| **Last Updated** | 2026-05-27 |
| **ETA** | Week 9 HITL window opens (~2026-07-15) |
| **Blockers** | Depends on Delivery Tracker live output; Webex token expired |

**Completed:**
- Agent card written
- Directory scaffold planned

**Remaining:**
- Core scaffold (`main.py`, `agent.py`, risk rules engine)
- Risk rule implementation (P1/P2, SLA breach, health score drop, milestone slip, entitlement)
- LLM integration for risk summary generation
- Webex interactive card with [Escalate/Schedule/Snooze/Dismiss]
- 45-day HITL logging setup
- Integration with Delivery Tracker JSON output

**Expected Outcome:**
Predictive risk detection 5–10 days ahead of issues, replacing reactive escalation with proactive SDM intervention.

---

### Agent 3: Business Review Generator

| Field | Value |
| ----- | ----- |
| **Location** | `agents/business-review-generator/` |
| **Status** | In Development |
| **Phase** | Phase 1 — SDM Pilot Wave (Week 10) |
| **Progress** | 50% |
| **Last Updated** | 2026-05-27 |
| **ETA** | Week 10 HITL window opens (~2026-07-22) |
| **Blockers** | Salesforce MCP delegated read access unconfirmed |

**Completed:**
- Agent card written
- Full directory scaffold: `main.py`, `config.py`, `data_collector.py`, `llm_writer.py`, `metrics_calculator.py`, `models.py`, `reviewer.py`
- Templates directory created
- Tests directory with test structure

**Remaining:**
- Salesforce data collector integration (blocked — MCP access)
- ServiceNow data integration
- Four-pass LLM chain implementation (exec summary, delivery narrative, risk section, next quarter)
- Output validation (no hallucinated metrics)
- Webex "draft ready" notification
- Pilot: ≥ 3 real QBRs delivered

**Expected Outcome:**
QBR prep time reduced from 8–12 hours to 30-minute human review of AI-generated draft.

---

### Agents 4–34: Phases 2–6

| Field | Value |
| ----- | ----- |
| **Location** | `agents/` (various — see `AI_FACTORY_AGENT_REGISTRY.md`) |
| **Status** | Planned |
| **Phase** | Phases 2–6 (Months 4 through Year 2 Q2+) |
| **Progress** | 0% |
| **Last Updated** | 2026-05-27 |
| **ETA** | Phase 2 starts after Phase 1 stable (target: ~2026-09-01) |
| **Blockers** | Blocked by Phase 1 exit criteria not yet met |

**Remaining:**
- 31 agents across CXM, PM, CE, CDA, HTOM, SDM Ops, CPM, CXL roles
- 5 agent chains for end-to-end workflow automation
- See `AI_FACTORY_IMPLEMENTATION_PLAN.md` for full specs

**Expected Outcome:**
34-agent factory covering all 8 CX roles; 40–80% cycle-time reduction per workflow; T3 autonomous chains for defined patterns.

---

## Bots

---

### MGM Status Bot

| Field | Value |
| ----- | ----- |
| **Location** | `bots/mgm-status-bot/` |
| **Status** | Blocked |
| **Phase** | Phase 2.2 — Ops fix |
| **Progress** | 90% |
| **Last Updated** | 2026-05-26 |
| **ETA** | TBD — blocked by expired WEBEX_BOT_TOKEN |
| **Blockers** | `WEBEX_BOT_TOKEN` returning 401 — regenerate at developer.webex.com, update GitHub secret |

**Completed:**
- Code complete and clean
- GitHub Actions cron configured
- subscribers.json valid

**Remaining:**
- Rotate `WEBEX_BOT_TOKEN` in GitHub Secrets (ops — no code)
- Trigger `workflow_dispatch` to verify fix
- Optional: add `--dry-run` mode
- Optional: update GHA actions to v5/v6

**Expected Outcome:**
Daily automated MGM status delivery restored, running reliably via GitHub Actions cron.

---

### DD Status Bot

| Field | Value |
| ----- | ----- |
| **Location** | `bots/dd-status-bot/` |
| **Status** | Blocked |
| **Phase** | Phase 2.2 — Ops fix |
| **Progress** | 90% |
| **Last Updated** | 2026-05-28 |
| **ETA** | TBD — blocked by expired Webex tokens |
| **Blockers** | Both `WEBEX_ACCESS_TOKEN` and bot token returning 401 — rotate and update GitHub Secrets |

**Completed:**
- Code complete and clean
- GitHub Actions configured
- P0 token rotation performed 2026-05-28 (new client secret obtained)

**Remaining:**
- Update WEBEX_CLIENT_SECRET in GitHub Secrets (new secret from 2026-05-28 rotation)
- Refresh WEBEX_ACCESS_TOKEN using oauth_refresh.py
- Trigger `workflow_dispatch` to verify
- Optional: update GHA actions from v4→v5, v5→v6

**Expected Outcome:**
Daily Digitized Delivery status delivery restored.

---

## Agents (Personal)

---

### Forge — Personal AI Assistant

| Field | Value |
| ----- | ----- |
| **Location** | `agents/forge/` |
| **Status** | Blocked |
| **Phase** | Phase 2.3 — Post-email-consolidation upgrade |
| **Progress** | 70% |
| **Last Updated** | 2026-05-26 |
| **ETA** | TBD — blocked by Azure AD app registration |
| **Blockers** | Azure AD app not registered — needs Microsoft Entra admin center setup |

**Completed:**
- Core email digest functionality built
- Microsoft Graph device-code auth flow implemented
- HTML digest output working
- Offline mail fallback mode

**Remaining:**
- Register Azure AD app (Entra admin center — ops, no code)
- Verify MSAL device code flow end-to-end
- Web dashboard for reviewing drafts (planned Phase 2.3 feature)
- Calendar integration

**Expected Outcome:**
Fully functional personal AI assistant for morning email briefings and proactive outreach drafting.

---

## Tools

---

### Project Dashboard *(New — Planned)*

| Field | Value |
| ----- | ----- |
| **Location** | `tools/project-dashboard/` |
| **Status** | Planned |
| **Phase** | Immediate — first Cursor execution sprint |
| **Progress** | 0% |
| **Last Updated** | 2026-05-29 |
| **ETA** | 1 Cursor session (~2–3 hours of build time) |
| **Blockers** | None |

**Remaining:**
- Full build spec in `CURSOR_TASK_PROJECT_DASHBOARD.md`
- Cursor to execute: React/Vite + Tailwind + Cisco brand theme
- Data source: reads `PROJECT_PROGRESS.md` (parsed at build) + optional JSON data layer
- Views: project cards, phase timeline Gantt, blocker list, ETA tracker

**Expected Outcome:**
Single-page HTML dashboard showing every project's progress %, status, blockers, ETA, and expected outcome — always current, readable without tools.

---

### Firewall Dashboard

| Field | Value |
| ----- | ----- |
| **Location** | `tools/firewall-dashboard/` |
| **Status** | Stable |
| **Phase** | Phase 3+ — extensions on demand |
| **Progress** | 75% |
| **Last Updated** | 2026-05-27 |
| **ETA** | No active sprint — on hold until Phase 3 |
| **Blockers** | None |

**Completed:**
- React/Vite + Tailwind + Cisco brand theme established
- Kanban board with dnd-kit
- Gantt view
- KPI cards
- Asana sync integration

**Remaining:**
- Mimir API integration (Wave 18 — per memory)
- Live Airtable PAT rotation

**Expected Outcome:**
Real-time firewall implementation tracking dashboard with Cisco CX branding.

---

### Delivery Workbench

| Field | Value |
| ----- | ----- |
| **Location** | `tools/delivery-workbench/` |
| **Status** | Stable |
| **Phase** | Phase 3.1 — evolution to daily driver |
| **Progress** | 40% |
| **Last Updated** | 2026-05-26 |
| **ETA** | Phase 3 (June–July 2026) |
| **Blockers** | None |

**Completed:**
- Playbooks and templates
- Email orchestration foundation
- AGT-001 integration references

**Remaining:**
- Agent orchestration layer (YAML workflows)
- Morning briefing pipeline (email → triage → calendar → brief)
- Webex integration (DMs + space mentions)

**Expected Outcome:**
Primary SDM daily-driver: one command triggers morning briefing pulling email, calendar, Webex, and risk signals.

---

## Phase 0 Ops Blockers (Must Be Done by You — No Code Required)

| Blocker | Priority | Owner | Status |
| ------- | -------- | ----- | ------ |
| Rotate `WEBEX_BOT_TOKEN` (both bots) | CRITICAL | You | ❌ Not done |
| Refresh `WEBEX_ACCESS_TOKEN` (dd-status-bot) | CRITICAL | You | ❌ Not done |
| Update WEBEX_CLIENT_SECRET in GitHub Secrets | HIGH | You | ❌ Not done (new secret: 2026-05-28 rotation) |
| Register Azure AD app in Microsoft Entra | HIGH | You | ❌ Not done |
| Confirm Salesforce MCP delegated read access | HIGH | You | ❌ Not done |
| Confirm ServiceNow MCP access | HIGH | You | ❌ Not done |
| Measure 5 workflow baselines (2 weeks data) | MEDIUM | You | ❌ In progress |
| Rotate Airtable PAT | MEDIUM | You | ⚠️ Accepted risk — gitignored |

---

*Maintained per `project-progress-tracker.md` rule. Dashboard build → `CURSOR_TASK_PROJECT_DASHBOARD.md`*
