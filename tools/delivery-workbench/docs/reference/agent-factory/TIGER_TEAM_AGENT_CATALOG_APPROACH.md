# Tiger Team Agent Catalog Approach

This document defines a separate Tiger Team approach for designing, validating, and communicating value for each agent in the catalog.

## Purpose

- Create clear, repeatable agent definitions that non-technical and technical stakeholders can understand.
- Show measurable value through expected outcomes and ROI metrics.
- Speed up governance decisions by standardizing what evidence each agent must provide.

## Tiger Team Mandate

The Tiger Team is responsible for:

- Defining each agent card using a common template.
- Verifying integration feasibility and dependency readiness.
- Defining required human inputs and control points.
- Estimating expected cycle-time impact and financial value.
- Packaging evidence for review boards and leadership.

## Team Composition (Recommended)

- Tiger Team Lead (program-level owner)
- PMO representative
- Architecture representative
- Engineering representative
- Security/GRC representative
- Analytics/finance representative
- Business workflow owner

## Agent Card Standard (Required Fields)

Each candidate agent must include the following sections.

### 1) Agent purpose

- Business problem statement
- Workflow scope boundaries
- Primary user personas

### 2) Integrations

- Required systems (e.g., Outlook, Jira, Confluence, ServiceNow)
- Integration type (read, write, event-trigger, bi-directional)
- API readiness and access status
- Known dependency blockers

### 3) Expected human input

- Reviewer roles and approval points
- Human-in-the-loop controls (where, when, why)
- Escalation owner for failures and exceptions

### 4) Expected results

- Operational outcomes (faster triage, fewer handoffs, fewer missed actions)
- Quality outcomes (accuracy, consistency, compliance)
- Adoption outcomes (usage rate, user trust indicators)

### 5) ROI metrics

- Cycle-time baseline (current)
- Cycle-time target (expected)
- Volume assumptions (cases/emails/tasks per period)
- Time saved per transaction
- Annualized hours saved
- Cost savings estimate
- Benefit realization confidence level (`High`, `Medium`, `Low`)

## ROI Formula Framework

Use this simple, explainable model:

- `Annualized Hours Saved = Volume per Period x Time Saved per Transaction x Periods per Year`
- `Estimated Cost Savings = Annualized Hours Saved x Loaded Hourly Rate`
- `Net Value = Estimated Cost Savings - Operating Cost`

Add non-financial value indicators alongside ROI:

- Decision latency reduction
- SLA adherence improvement
- Error/rework reduction
- Stakeholder satisfaction trend

## Stage-Gate Review Model

### Gate 1: Concept readiness

Required evidence:

- Complete agent card
- Problem-value fit
- Initial integration feasibility

### Gate 2: Pilot readiness

Required evidence:

- Control model defined (HITL/autonomy)
- Security and compliance checks complete
- KPI baseline and measurement method approved

### Gate 3: Scale readiness

Required evidence:

- Pilot outcomes vs target
- Quality and trust thresholds met
- ROI evidence reviewed

## Output Artifacts

The Tiger Team should produce:

- Agent card packets (one per agent)
- Integration dependency matrix
- Human-control design matrix
- Pilot scorecard and ROI pack
- Executive value narrative (quarterly)

## Initial KPI Pack for Agent Catalog Value

- `Cycle Time Delta (%)`
- `Time Saved per Workflow (hours)`
- `Human Review Load (minutes per item)`
- `Draft Acceptance Rate (%)`
- `Action Extraction Accuracy (%)`
- `SLA Breach Reduction (%)`
- `Estimated Annualized Savings ($)`

## Cadence

- Weekly Tiger Team review for candidate agents
- Bi-weekly governance checkpoint
- Monthly executive value readout

## Initial Application: Outlook Email Chief-of-Staff Agent

Use this approach immediately for the Outlook pilot:

- Scope: personal + team mailbox
- Control mode: draft-only, human review before send
- Governance marker: 45-day HITL review period
- Day-45 decision package: quality metrics, user trust signals, and ROI estimate

## Update Protocol

When updating this document:

1. Keep formulas and KPI definitions consistent across agents.
2. Add new metrics only when they map to a decision gate.
3. Link agent-specific updates to:
   - `docs/AGENT_FACTORY_REQUIREMENTS.md`
   - `docs/AGENT_FACTORY_COLLATERAL_PLAN.md`
   - `docs/AGENT_FACTORY_ACTIVITY_LOG.md`
