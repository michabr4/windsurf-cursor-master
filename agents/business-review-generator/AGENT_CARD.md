# Agent Card: Business Review Generator

## Document Metadata

- Agent name: Business Review Generator
- Version: 0.1 (Design)
- Date: 2026-05-27
- Owner: SDM / CXM domain expert
- Reviewer(s): Windsurf (Architect), SDM lead, CXM lead
- Status: `Concept`

---

## 1) Purpose

- Problem statement: Preparing a quarterly or executive business review (QBR/EBR) takes 4–8 hours per account. The process is largely data gathering and formatting from Helix and Salesforce — the same sources every time. SDMs and CXMs spend most of this time on mechanical assembly, leaving limited time for strategic narrative.
- Why now: Helix and Salesforce MCP integrations are in scope for Phase 1. A draft-first T2 approach means the agent does the mechanical work; the SDM/CXM adds strategy and approves before delivery. No customer ever sees the raw agent output.
- Primary user personas: Service Delivery Manager (SDM), Customer Experience Manager (CXM)
- Workflow scope boundaries:
  - **In scope:** Pull delivery metrics, case history, milestone completion, health scores, and account context. Generate a structured QBR draft (narrative + data sections). Surface to SDM/CXM for review, editing, and approval.
  - **Out of scope:** Sending the QBR directly to the customer. Making strategic recommendations autonomously. Updating Salesforce or Helix records. Any financial commitments.

---

## 2) Integrations

- Required systems: Helix REST API, Salesforce MCP
- Integration mode per system:
  - Helix REST API: `Read`
  - Salesforce MCP: `Read`
- API readiness status:
  - Helix: ✅ Ready
  - Salesforce: 🟡 MCP exists — confirm delegated read access (see `AI_FACTORY_INTEGRATION_READINESS.md`)
- Access/security dependencies: `HELIX_API_TOKEN`, `SALESFORCE_MCP_TOKEN` in `.env`
- Blockers and owner:
  - Salesforce delegated read access confirmation → 👤 Ops/Admin

---

## 3) Expected Human Input and Controls

- Human roles involved: SDM or CXM (author and approver), customer (recipient — never sees agent draft directly)
- Required approval points: **Every QBR draft** must be reviewed, edited if needed, and explicitly approved by SDM/CXM before any version is shared with the customer.
- HITL control mode: Draft-first. Agent generates full draft. User reviews section by section. Choices: `Accept` | `Edit` | `Regenerate section` | `Discard`.
- Escalation path for exceptions: If data pull returns incomplete data → agent flags missing sections clearly. SDM fills gaps manually before approval.
- Fallback behavior if agent fails: SDM notified of failure. Falls back to manual QBR process. No partial drafts sent.

---

## 4) Expected Results

### Operational Outcomes

- Expected cycle-time impact: Reduce QBR prep from 4–8 hrs to 30–60 min review and edit
- Handoff reduction target: Eliminate manual data-gathering step across both Helix and Salesforce (estimated 2–3 hrs per QBR)
- Throughput impact: SDM/CXM can prepare more QBRs per quarter without increasing headcount

### Quality Outcomes

- Accuracy target: 100% data accuracy (direct API reads — no inference on facts)
- Compliance/policy conformance target: Zero unapproved QBRs delivered to customers
- Error/rework reduction target: Eliminate missing-data errors that currently delay QBR delivery

### Adoption Outcomes

- Expected adoption rate: SDM/CXM uses for ≥ 80% of QBRs after 45-day pilot
- Trust/satisfaction target: Draft rated ≥ 4/5 quality by Day 30; ≥ 60% accepted as-is or with minor edits

---

## 5) KPI and ROI Metrics

### KPI Baseline and Targets

- Baseline cycle time: ___ hrs (fill from `AI_FACTORY_CYCLE_TIME_BASELINES.md` Workflow 3)
- Target cycle time: 45 min (review + edit of auto-generated draft)
- Time saved per QBR: (Baseline hrs × 60 - 45) min
- Draft acceptance rate target: ≥ 60% accepted or lightly edited by Day 45
- Action extraction accuracy target: N/A (structured data pull, not inference)

### ROI Inputs

- Volume per period: ___ QBRs/quarter (fill from baseline)
- Periods per year: 4
- Loaded hourly rate: $___/hr
- Operating cost estimate: ~$0.50–$2.00 LLM inference per QBR

### ROI Outputs

- `Annualized Hours Saved = Volume/quarter × (Baseline hrs - 0.75 hr) × 4`
- `Estimated Cost Savings = Annualized Hours Saved × Loaded Hourly Rate`
- `Net Value = Estimated Cost Savings - (Volume/year × $2.00 LLM cost)`
- Benefit confidence: `High` (data retrieval is deterministic; savings are large)

---

## 6) Stage-Gate Evidence Checklist

### Gate 1: Concept Readiness

- [x] Purpose and scope complete
- [x] Integration feasibility documented (Helix ready; Salesforce pending ops)
- [x] Initial KPI and ROI assumptions documented

### Gate 2: Pilot Readiness

- [ ] Salesforce delegated read access confirmed (ops action)
- [ ] QBR template structure approved by SDM/CXM lead
- [ ] HITL review workflow built — human cannot skip approval step
- [ ] Baseline from `AI_FACTORY_CYCLE_TIME_BASELINES.md` Workflow 3 complete
- [ ] Security review: no customer data cached outside approved storage

### Gate 3: Scale Readiness (Day 45 Review)

- [ ] Draft acceptance rate ≥ 60%
- [ ] Zero unapproved QBRs sent to customers
- [ ] SDM/CXM satisfaction ≥ 4/5
- [ ] ROI evidence package complete
- [ ] Salesforce read access stable (no auth failures during pilot)

---

## 7) Pilot Plan Snapshot

- Pilot start date: Sprint 2 (Day 35 of Phase 0, after Delivery Tracker + Risk Sentinel pilot start)
- Pilot end date: Day 80 (45 days from Sprint 2 delivery)
- Review cadence: Per-QBR review log; weekly 15-min check-in; Day 60 mid-point review
- Decision date: Day 81
- Expansion recommendation options: `Scale to T3` | `Continue HITL` | `Hold/Redesign`

---

## 8) Decision Summary

- Current recommendation: Build in Sprint 2 — sequenced after Sprint 1 agents to allow Salesforce access confirmation
- Decision owner: SDM lead + CXM lead (joint sign-off required — two roles use this agent)
- Decision date: Pending Gate 1 sign-off + Salesforce ops action complete
- Notes: This agent has the highest ROI of the Phase 1 set. It is also the most visible — QBR quality reflects directly on the SDM/CXM. Ensure draft quality bar is high before starting pilot.

---

## 9) Linked Artifacts

- Requirements reference: `tools/agentic-starter-kit/docs/AGENT_FACTORY_REQUIREMENTS.md` (FR-4, FR-6)
- Collateral reference: `sdm-files/sdm-agentic-framework/docs/SDM_AGENT_ANALYSIS.md` (Agent P1-3)
- Implementation plan reference: `AI_FACTORY_IMPLEMENTATION_PLAN.md` Section 6
- Registry entry: `AI_FACTORY_AGENT_REGISTRY.md` Row #3
- Governance log: `AI_FACTORY_GOVERNANCE_LOG.md` (HITL window to be logged at Sprint 2 pilot start)
- Baseline reference: `AI_FACTORY_CYCLE_TIME_BASELINES.md` Workflow 3
