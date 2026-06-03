# Agent Card: Delivery Tracker

## Document Metadata

- Agent name: Delivery Tracker
- Version: 0.1 (Design)
- Date: 2026-05-27
- Owner: SDM domain expert
- Reviewer(s): Windsurf (Architect), SDM lead
- Status: `Pilot Ready (baseline pending)`

---

## 1) Purpose

- Problem statement: SDMs spend 30–60 min per week manually pulling delivery status from Helix across all active accounts to compile the weekly status report. Data is fragmented across cases, milestones, and notes.
- Why now: Helix REST API is already integrated into delivery-workbench. This is the lowest-friction agent to build — read-only, no customer-facing output, direct measurable time saving.
- Primary user personas: Service Delivery Manager (SDM)
- Workflow scope boundaries:
  - **In scope:** Pull open cases, milestone completion %, SLA adherence, overdue items per account from Helix API. Generate structured weekly summary.
  - **Out of scope:** Writing customer-facing reports (that's the Business Review Generator). Updating Helix data. Any action in external systems.

---

## 2) Integrations

- Required systems: Helix REST API
- Integration mode per system: `Read` only
- API readiness status: ✅ Ready — Helix connector exists in `tools/delivery-workbench/python/connectors/`
- Access/security dependencies: Bearer token in `.env` (`HELIX_API_TOKEN`)
- Blockers and owner: None — clear to build

---

## 3) Expected Human Input and Controls

- Human roles involved: SDM (sole consumer of output)
- Required approval points: None — T1 read-only output. SDM reviews displayed dashboard/report before acting.
- HITL control mode: Display-only. Agent surfaces data; SDM decides what to do.
- Escalation path for exceptions: If API call fails → log error, notify SDM via console/log. No automated notification.
- Fallback behavior if agent fails: SDM falls back to manual Helix review. Alert logged.

---

## 4) Expected Results

### Operational Outcomes

- Expected cycle-time impact: Reduce weekly status prep from ~45 min to ~5 min review
- Handoff reduction target: 0 (no handoffs — internal SDM tool)
- Throughput impact: SDM can cover more accounts in same time budget

### Quality Outcomes

- Accuracy target: 100% match with Helix data (it's a direct read — no transformation)
- Compliance/policy conformance target: No PII in output, no customer-facing use
- Error/rework reduction target: Eliminate manual copy-paste errors from Helix

### Adoption Outcomes

- Expected adoption rate: 100% of SDM weekly status tasks within 4 weeks of pilot
- Trust/satisfaction target: SDM actively uses weekly — confirmed in sprint review

---

## 5) KPI and ROI Metrics

### KPI Baseline and Targets

- Baseline cycle time: ___ min (fill from `AI_FACTORY_CYCLE_TIME_BASELINES.md` Workflow 1)
- Target cycle time: 5 min (review of auto-generated summary)
- Time saved per transaction: ___  min (baseline - 5)
- Draft acceptance rate target: N/A (read-only)
- Action extraction accuracy target: N/A

### ROI Inputs

- Volume per period: 1 report per week
- Periods per year: 52
- Loaded hourly rate: $___/hr (fill in)
- Operating cost estimate: $0 (no API costs for Helix reads)

### ROI Outputs

- `Annualized Hours Saved = 1 × (Baseline min - 5 min) / 60 × 52`
- `Estimated Cost Savings = Annualized Hours Saved × Loaded Hourly Rate`
- `Net Value = Estimated Cost Savings - $0 operating cost`
- Benefit confidence: `High` (direct read, no inference)

---

## 6) Stage-Gate Evidence Checklist

### Gate 1: Concept Readiness

- [x] Purpose and scope complete
- [x] Initial integration feasibility validated (Helix connector exists)
- [x] Initial KPI and ROI assumptions documented

### Gate 2: Pilot Readiness

- [x] HITL/autonomy controls approved (T1 — display only, no approval needed)
- [x] Security check: read-only scope confirmed, no PII in output — verified 2026-06-03 (all Helix calls are GET; WeeklySummary model contains no PII; token stored in .env only)
- [ ] Baseline measurement from `AI_FACTORY_CYCLE_TIME_BASELINES.md` Workflow 1 complete

### Gate 3: Scale Readiness

- [ ] Pilot outcomes reviewed vs targets
- [ ] SDM actively using weekly (usage log reviewed)
- [ ] ROI evidence package reviewed

---

## 7) Pilot Plan Snapshot

- Pilot start date: Day 21 of Phase 0 (after baselines measured)
- Pilot end date: Day 65 (45 days of use)
- Review cadence: Weekly 15-min check-in
- Decision date: Day 66
- Expansion recommendation options: `Scale` | `Continue as-is` | `Hold/Redesign`

---

## 8) Decision Summary

- Current recommendation: Build — lowest risk, highest immediate value, no governance overhead
- Decision owner: SDM lead
- Decision date: Pending Gate 1 sign-off
- Notes: T1 = no HITL window required. Can go straight to use after build. Metrics tracked passively.

---

## 9) Linked Artifacts

- Requirements reference: `tools/agentic-starter-kit/docs/AGENT_FACTORY_REQUIREMENTS.md`
- Collateral reference: `sdm-files/sdm-agentic-framework/docs/SDM_AGENT_ANALYSIS.md` (Agent P1-1)
- Implementation plan reference: `AI_FACTORY_IMPLEMENTATION_PLAN.md` Section 6
- Registry entry: `AI_FACTORY_AGENT_REGISTRY.md` Row #1
- Baseline reference: `AI_FACTORY_CYCLE_TIME_BASELINES.md` Workflow 1
