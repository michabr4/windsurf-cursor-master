# AI Factory — Governance Log

> **Purpose:** Permanent record of all trust tier decisions, HITL windows, go/no-go gates, and promotion decisions.  
> **Maintained by:** Windsurf (Architect) after each governance event.  
> **Rule:** Every T2→T3 promotion requires an entry here before the promotion takes effect.

---

## Phase Gate Log

| Date | Gate | Decision | Notes |
| ---- | ---- | -------- | ----- |
| 2026-05-27 | Phase 0 → Phase 1 | 🟡 Pending | Criteria: baselines measured, integration readiness confirmed, 3 agent cards signed |

---

## HITL Window Log

Track each T2 agent's 45-day human-in-the-loop window here.

| Agent | HITL Start | HITL End (Day 45) | Cards Sent | Approve | Edit | Dismiss | False+ Rate | Decision |
| ----- | ---------- | ----------------- | ---------- | ------- | ---- | ------- | ----------- | -------- |
| Risk & Escalation Sentinel | — | — | — | — | — | — | — | Pending |
| Business Review Generator | — | — | — | — | — | — | — | Pending |

---

## Trust Tier Promotion Log

| Date | Agent | From | To | Approver | Evidence | Notes |
| ---- | ----- | ---- | -- | -------- | -------- | ----- |
| — | — | — | — | — | — | First promotion pending Phase 1 |

---

## Governance Decisions (Rolling)

### 2026-06-03 — Phase 1 Code Complete + Security Verification

- **Test results:** All three Phase 1 agents fully tested and green — 56/56 tests pass (Delivery Tracker 26, Risk Sentinel 17, Business Review Generator 13)
- **Code-verifiable Gate 2 items confirmed:**
  - Delivery Tracker: HITL controls approved (T1, display-only); security check passed (all GET, no PII in WeeklySummary)
  - Risk Sentinel: HITL workflow confirmed (4-button adaptive card built + tested); no autonomous sends possible (dry_run guard + explicit call required)
  - Business Review Generator: HITL workflow confirmed (draft always persisted before any notification, no customer path); no customer data cached outside `data/runs/business-review/`
- **AGENT_CARD statuses updated:** Delivery Tracker → `Pilot Ready (baseline pending)`; Sentinel → `Pilot Ready (ops actions pending)`; BRG → `Pilot Ready (ops actions pending)`
- **Outstanding blockers for Phase 0 gate (human/ops actions — cannot be resolved by code):**
  1. `AI_FACTORY_CYCLE_TIME_BASELINES.md` — all 5 workflows empty; SDM must time-log 5 instances per workflow
  2. Webex bot token rotation → 👤 You (required before Sentinel pilot start)
  3. ServiceNow access confirmation → 👤 Ops (required before Sentinel pilot start)
  4. Salesforce delegated read access → 👤 Ops/Admin (required before BRG pilot start)
  5. QBR template structure sign-off → 👤 SDM/CXM lead (required before BRG pilot start)
- **Next gate:** Phase 0 → Phase 1 formal sign-off pending baseline measurements + ops actions above

---

### 2026-05-29 — Phase 1 Development Start

- **Decision:** Phase 1 Agent #1 (Delivery Tracker, T1) and Agent #2 (Risk & Escalation Sentinel, T2) moved to 🔵 In Development; Agent #3 (Business Review Generator, T2) scaffolded and in development
- **AI Factory compliance verified:** `trust_tier`, `validate_inputs()`, `handle_error()`, `[METRICS]` print confirmed in `delivery-tracker/tracker.py` and `risk-escalation-sentinel/sentinel.py`
- **Rule inheritance:** `.windsurf/rules/agent-context.md` and `.cursor/rules/agent-context.md` created for all three Phase 1 agents
- **Data directories provisioned:** `data/runs/delivery-tracker/`, `data/runs/risk-sentinel/`, `data/runs/business-review/`
- **Next gate:** Phase 0 exit review criteria — baselines measured, Salesforce access confirmed, all 3 agent cards signed

---

### 2026-05-27 — Phase 0 Kickoff

- **Decision:** AI Factory Phase 0 initiated per `AI_FACTORY_IMPLEMENTATION_PLAN.md`
- **Scope confirmed:** 34 agents across 8 CX roles
- **Phase 1 pilot agents selected:** Delivery Tracker (T1), Risk Sentinel (T2), Business Review Generator (T2)
- **Domain owner sign-off pending:** Agent cards in progress (Week 1 task)
- **Next gate:** Phase 0 exit review — criteria documented in plan Section 5.7

---

## Governance Review Cadence

| Cadence | Activity |
| ------- | -------- |
| Weekly (15 min) | Review HITL logs, surface any issues |
| Monthly | Phase gate assessment, KPI review |
| Per T3 promotion | Full governance review + written sign-off |
| Per chain deployment | Architecture review + T3 chain approval |

---

## Agent Escalation Log

Record any incidents where an agent produced unexpected output or required emergency intervention.

| Date | Agent | Incident | Impact | Action Taken | Resolved |
| ---- | ----- | -------- | ------ | ------------ | -------- |
| — | — | No incidents yet | — | — | — |

---

*Last updated: 2026-06-03 | Reference: `AI_FACTORY_IMPLEMENTATION_PLAN.md` Section 14*
