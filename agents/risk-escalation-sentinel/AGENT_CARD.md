# Agent Card: Risk & Escalation Sentinel

## Document Metadata

- Agent name: Risk & Escalation Sentinel
- Version: 0.1 (Design)
- Date: 2026-05-27
- Owner: SDM domain expert
- Reviewer(s): Windsurf (Architect), SDM lead
- Status: `Pilot Ready (ops actions pending)`

---

## 1) Purpose

- Problem statement: Risk signals (overdue milestones, SLA breach approaching, stalled cases) are discovered days late because SDMs check Helix manually on an ad-hoc basis. Escalation drafts are written from scratch each time, adding 30–60 min per incident to response lag.
- Why now: Phase 1 pilot window gives us a 45-day HITL period to validate signal accuracy before any autonomous escalation. Risk is contained — every output requires human approval before sending.
- Primary user personas: Service Delivery Manager (SDM)
- Workflow scope boundaries:
  - **In scope:** Scan Helix cases + milestones + SLA data daily. Classify risk signals. Draft escalation message for human review. Post to Webex only after explicit SDM approval.
  - **Out of scope:** Autonomous sending of any escalation. Contacting the customer directly. Modifying Helix records. Any financial or contractual decisions.

---

## 2) Integrations

- Required systems: Helix REST API, ServiceNow MCP, Webex MCP
- Integration mode per system:
  - Helix REST API: `Read`
  - ServiceNow MCP: `Read`
  - Webex MCP: `Write` (draft + human-approved post only)
- API readiness status:
  - Helix: ✅ Ready
  - ServiceNow: 🟡 MCP exists — confirm access (see `AI_FACTORY_INTEGRATION_READINESS.md`)
  - Webex: ⚠️ Token rotation required before use
- Access/security dependencies: `HELIX_API_TOKEN`, `SERVICENOW_TOKEN`, `WEBEX_BOT_TOKEN` in `.env`
- Blockers and owner:
  - ServiceNow access confirmation → 👤 Ops
  - Webex token rotation → 👤 You

---

## 3) Expected Human Input and Controls

- Human roles involved: SDM (sole approver)
- Required approval points: **Every escalation draft** requires explicit SDM approval before the Webex message is sent. No exceptions during HITL window.
- HITL control mode: Draft-first. Agent produces draft + risk classification. SDM chooses: `Approve & Send` | `Edit & Send` | `Dismiss`.
- Escalation path for exceptions: If agent produces a false positive or misclassified risk → SDM dismisses + logs feedback. Feedback reviewed weekly to retrain/tune thresholds.
- Fallback behavior if agent fails: SDM notified of scan failure. Manual Helix check initiated. No silent failures.

---

## 4) Expected Results

### Operational Outcomes

- Expected cycle-time impact: Reduce risk detection lag from ~3–5 days (manual) to < 24 hours (daily automated scan)
- Handoff reduction target: Eliminate manual data-gathering step per escalation (estimated 30 min per incident)
- Throughput impact: SDM can monitor more accounts simultaneously without increasing workload

### Quality Outcomes

- Accuracy target: < 20% false positive rate by end of 45-day HITL window
- Compliance/policy conformance target: Zero autonomous sends — all Webex messages human-approved
- Error/rework reduction target: Eliminate missed escalations due to manual oversight gaps

### Adoption Outcomes

- Expected adoption rate: SDM reviews all daily scan outputs within 45-day window
- Trust/satisfaction target: SDM rates draft quality ≥ 4/5 by Day 30

---

## 5) KPI and ROI Metrics

### KPI Baseline and Targets

- Baseline cycle time: ___ days (fill from `AI_FACTORY_CYCLE_TIME_BASELINES.md` Workflow 2)
- Target cycle time: < 1 day (daily scan)
- Time saved per incident: ~30 min manual data gathering + draft writing
- Draft acceptance rate target: ≥ 70% (approve or edit-then-send) by Day 45
- Action extraction accuracy target: ≥ 80% risk signal accuracy by Day 45

### ROI Inputs

- Volume per period: ___ escalations/month (fill from baseline)
- Periods per year: 12
- Loaded hourly rate: $___/hr
- Operating cost estimate: LLM inference cost ~$0.10/scan/day

### ROI Outputs

- `Annualized Hours Saved = Volume/month × 0.5 hr × 12`
- `Estimated Cost Savings = Annualized Hours Saved × Loaded Hourly Rate`
- `Net Value = Estimated Cost Savings - (365 × $0.10 LLM cost)`
- Benefit confidence: `Medium` (depends on signal volume — confirmed at Day 45 review)

---

## 6) Stage-Gate Evidence Checklist

### Gate 1: Concept Readiness

- [x] Purpose and scope complete
- [x] Integration feasibility documented (Helix ready; SN + Webex pending ops)
- [x] Initial KPI and ROI assumptions documented

### Gate 2: Pilot Readiness

- [ ] Webex token rotated and confirmed
- [ ] ServiceNow access confirmed (ops action)
- [x] HITL approval workflow built and tested with dummy data — verified 2026-06-03 (adaptive card with Escalate/Schedule/Snooze/Dismiss buttons built in webex_notifier.py; 17/17 tests pass)
- [ ] Baseline from `AI_FACTORY_CYCLE_TIME_BASELINES.md` Workflow 2 complete
- [x] Security review: confirm no autonomous sends possible in code path — verified 2026-06-03 (send_high_risk_card blocked in dry_run; no Webex POST occurs without explicit orchestrator call; code reviewed)

### Gate 3: Scale Readiness (Day 45 Review)

- [ ] False positive rate ≤ 20%
- [ ] Draft acceptance rate ≥ 70%
- [ ] Zero unauthorized sends during HITL window
- [ ] SDM satisfaction ≥ 4/5
- [ ] ROI evidence package complete

---

## 7) Pilot Plan Snapshot

- Pilot start date: Day 21 of Phase 0 (Sprint 1 delivery)
- Pilot end date: Day 66 (45-day HITL window)
- Review cadence: Weekly 15-min HITL log review; Day 30 mid-point check
- Decision date: Day 67
- Expansion recommendation options: `Scale to T3` | `Continue HITL` | `Hold/Redesign`

---

## 8) Decision Summary

- Current recommendation: Build in Sprint 1 alongside Delivery Tracker
- Decision owner: SDM lead
- Decision date: Pending Gate 1 sign-off + Ops actions complete
- Notes: Do not start HITL pilot until Webex token rotated and ServiceNow access confirmed. Gate 2 blocks on ops.

---

## 9) Linked Artifacts

- Requirements reference: `tools/agentic-starter-kit/docs/AGENT_FACTORY_REQUIREMENTS.md` (FR-6, FR-7)
- Collateral reference: `sdm-files/sdm-agentic-framework/docs/SDM_AGENT_ANALYSIS.md` (Agent P1-2)
- Implementation plan reference: `AI_FACTORY_IMPLEMENTATION_PLAN.md` Section 6
- Registry entry: `AI_FACTORY_AGENT_REGISTRY.md` Row #2
- Governance log: `AI_FACTORY_GOVERNANCE_LOG.md` (HITL window to be logged at pilot start)
- Baseline reference: `AI_FACTORY_CYCLE_TIME_BASELINES.md` Workflow 2
