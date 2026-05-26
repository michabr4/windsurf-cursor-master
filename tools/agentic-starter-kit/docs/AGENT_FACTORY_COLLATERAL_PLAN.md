# Agent Factory Collateral Plan (Executive + Delivery)

This plan tracks all collateral needed to run the Agent Factory program with clear communication for both executive and delivery audiences.

## Document Status

- Version: `v0.1`
- Status: `Active`
- Last Updated: `2026-05-20`
- Primary KPI Anchor: `Cycle Time`

## Audience Strategy

We will build collateral for both groups in parallel:

- **Executive audience**: strategy clarity, business value, governance confidence, investment narrative.
- **Delivery audience**: operational clarity, role expectations, implementation details, day-to-day execution playbooks.

## Collateral Inventory

- `C1` Executive one-page strategy brief
  - Audience: Executive
  - Owner role: Service Delivery Lead
  - Purpose: Define why Agent Factory, outcomes, KPI commitments
  - Status: Draft
- `C2` Leadership deck (10–12 slides)
  - Audience: Executive
  - Owner role: PMO + Strategy
  - Purpose: Align target state, 90-day milestones, decisions needed
  - Status: Draft
- `C3` Operating model handbook
  - Audience: Both
  - Owner role: PMO
  - Purpose: Define intake, triage, build, deploy, govern, scale
  - Status: Draft
- `C4` RACI and decision rights matrix
  - Audience: Both
  - Owner role: PMO + Governance
  - Purpose: Clarify who decides what and when
  - Status: Draft
- `C5` Agent portfolio charter pack
  - Audience: Delivery
  - Owner role: Product/Program Owners
  - Purpose: Scope each wave-1 and wave-2 agent
  - Status: Draft
- `C6` AI playbook-to-agent mapping catalog
  - Audience: Delivery
  - Owner role: Architecture
  - Purpose: Translate concept playbooks into executable modules
  - Status: Pending input
- `C7` Integration architecture and dependency map
  - Audience: Delivery
  - Owner role: Architecture + Engineering
  - Purpose: Define system touchpoints and sequencing
  - Status: Draft
- `C8` Security, risk, and guardrails policy
  - Audience: Both
  - Owner role: Security/GRC
  - Purpose: Set autonomy controls and escalation requirements
  - Status: Draft
- `C9` KPI baseline and benefits scorecard
  - Audience: Both
  - Owner role: PMO + Analytics
  - Purpose: Track cycle-time impact by workflow and wave
  - Status: Pending baseline
- `C10` Adoption and enablement kit
  - Audience: Delivery
  - Owner role: PMO + Change Lead
  - Purpose: Onboard teams and improve adoption quality
  - Status: Draft
- `C11` Tiger Team agent catalog approach
  - Audience: Both
  - Owner role: Tiger Team Lead + PMO + Architecture
  - Purpose: Standardize purpose, integrations, human input, expected results, and ROI proof for each catalog agent
  - Status: Draft

## Priority Creative Pilot Charter (Initial)

### P1: Outlook Email Chief-of-Staff Agent

- Platform: Outlook
- Scope: personal mailbox and team mailbox
- Primary outcomes:
  - Daily summary of key emails
  - Action items and unresolved steps
  - Decisions required from owner
  - Response drafts for review
- Control mode (initial): draft-only with human approval required before send
- Governance marker: 45-day mandatory HITL review window for quality, trust, and policy validation
- Expansion gate: no send autonomy before formal review signoff after day 45

## Required Contents by Collateral

### C1: Executive one-page strategy brief

- Current-state pain and cost of delay
- Agent Factory vision and principles
- 12-month business outcomes
- Quarter-by-quarter KPI targets
- Risks and mitigation

### C2: Leadership deck

- Why now
- Current state to target state
- Role model (PMO + Architecture/Engineering)
- Wave roadmap and gating decisions
- Investment and dependency asks

### C3: Operating model handbook

- Lifecycle stages and entry/exit criteria
- Intake scoring rubric and hard gates
- Governance cadence and review forums
- Exception handling and escalation paths

### C4: RACI and decision rights matrix

- Decision categories (priority, design, release, autonomy)
- Accountable/Responsible by function
- SLA for decision turnaround

### C5: Agent portfolio charter pack

Per-agent templates:

- Problem statement
- Workflow scope boundaries
- Inputs/outputs and system dependencies
- KPI baseline and target
- Human-in-the-loop controls
- Pilot governance marker (for P1: 45-day HITL review)

### C6: AI playbook-to-agent mapping catalog

Per playbook module:

- Trigger conditions
- Required context and data
- Output artifact format
- Policy checks and approval requirements
- Reusability tags

### C7: Integration map

- Integration sequence (wave by wave)
- API readiness and ownership
- Eventing patterns (webhook/bus)
- Failure handling and retry strategy

### C8: Security and guardrails policy

- Permission tiers by action type
- Restricted actions requiring approval
- Audit and retention standards
- Incident response process for agent errors

### C9: KPI and benefits scorecard

- Baseline cycle-time by workflow
- Leading indicators (handoffs, waiting time)
- Lagging indicators (end-to-end cycle-time)
- Weekly and monthly reporting cadence

### C10: Adoption kit

- Role-based quick-start guides
- FAQ and objection handling
- Office-hours and support workflow
- Adoption measurement plan

### C11: Tiger Team agent catalog approach

- Standard agent card fields (purpose, integrations, human input, expected results, ROI)
- Stage-gate evidence model for concept, pilot, and scale readiness
- KPI and ROI formulas aligned across catalog entries
- Decision-pack template for governance and executive review
- Working template: `docs/templates/AGENT_CARD_TEMPLATE.md`

## 90-Day Collateral Milestones

### Days 0–30

- Publish C1, C2 draft, C3 v0.1, C4 v0.1, C5 templates
- Confirm wave-1 workflows and KPI baseline measurement method

### Days 31–60

- Publish C6 v0.1 and C7 v0.1 with integration dependencies
- Publish C8 v0.1 guardrail policy
- Start C9 baseline tracking and weekly reporting
- Execute P1 45-day HITL evaluation and readiness review package

### Days 61–90

- Finalize C2, C3, C4 with real pilot outcomes
- Publish C10 enablement kit
- Publish C9 with first cycle-time impact results

## Source and Reference Notes

- Primary source reference for AI playbooks: Confluence URL shared by stakeholder.
- Current limitation: direct fetch blocked in this session by Atlassian authentication.
- Action: ingest stakeholder-provided excerpts/exports continuously and map into C6, C7, and C8.
- Tiger Team approach reference: `docs/TIGER_TEAM_AGENT_CATALOG_APPROACH.md`.
- Agent card template reference: `docs/templates/AGENT_CARD_TEMPLATE.md`.

## Working Update Protocol

When updating this file:

1. Update `Last Updated` date.
2. Change status fields for each collateral item.
3. Record blockers in Source and Reference Notes.
4. Link updates back to:
   - `docs/AGENT_FACTORY_ACTIVITY_LOG.md`
   - `docs/AGENT_FACTORY_REQUIREMENTS.md`
