# Agent Factory Requirements (Living Document)

This is the ongoing requirements document for the Service Delivery Agent Factory initiative.

> **Note**: A consolidated requirements document combining all living docs into a single source of truth is available at `docs/AGENT_FACTORY_CONSOLIDATED_REQUIREMENTS.md`. This file remains active for incremental updates.

## Document Status

- Version: `v0.1`
- Status: `Draft / In Progress`
- Primary KPI Focus: `Cycle Time`
- Last Updated: `2026-05-20`

## Objective

Design and operationalize an Agent Factory that builds role-aligned agents and orchestrated agents-of-agents to:

- Simplify Cisco customer experiences.
- Simplify internal service delivery workflows.
- Reduce end-to-end cycle time across delivery activities.

## Scope

### In Scope (Current)

- Practical operating model for intake-to-scale lifecycle.
- PMO role-mapped agent design.
- Architecture and Engineering role-mapped agent design.
- Integration point mapping across systems and toolchains.
- AI playbook-to-agent composition approach.
- 90-day rollout planning for wave 1.

### Out of Scope (Current)

- Full autonomous production actions without guardrails.
- Finalized platform implementation details per tool.
- Detailed budget and staffing model.

## Stakeholders and Roles

### Core Stakeholder Groups

- Service Delivery leadership
- PMO leadership and program teams
- Architecture leadership and architects
- Engineering managers and delivery teams
- Security, compliance, and governance partners

### Role-Decision Expectations (to validate)

- PMO owns portfolio and delivery prioritization decisions.
- Architecture owns standards and design-governance approvals.
- Engineering owns implementation sequencing and release execution.
- Governance functions own risk controls and policy exceptions.

## Functional Requirements

### FR-1: Intake and Triage

The operating model must support standardized intake and triage of agent opportunities with explicit scoring criteria and ownership.

Acceptance signals:

- Each proposal has a named business owner.
- Each proposal is scored against a shared rubric.
- Each proposal is assigned to a delivery wave.

### FR-2: Role-Mapped Agent Design

The framework must map agents to PMO and Architecture/Engineering workflows with clear human decision points.

Acceptance signals:

- Each agent has role alignment, inputs, outputs, and escalation path.
- Human approval gates are defined for high-impact actions.

### FR-3: Playbook Composition

AI playbooks must be reusable as composable modules for agent behavior.

Acceptance signals:

- Each playbook module includes trigger, required inputs, outputs, and policy gates.
- Orchestrator agents can invoke multiple approved modules.

### FR-4: Integration Layer

The platform must integrate with delivery systems to read status, generate recommendations, and track outcomes.

Acceptance signals:

- Priority integrations are sequenced by value and feasibility.
- Identity, permissions, and auditability are enforced across actions.

### FR-5: Measurement and Governance

The operating model must include baseline and ongoing measurement of cycle-time improvements with governance controls.

Acceptance signals:

- Baseline cycle-time metric exists for each targeted workflow.
- Target cycle-time reduction is defined per wave.
- Audit logs exist for recommendations and actions.

### FR-6: Tiger Team Agent Catalog Framework

The operating model must include a separate Tiger Team framework that standardizes how each agent's purpose, integrations, human input expectations, expected results, and ROI are documented and reviewed.

Acceptance signals:

- Every catalog agent has a completed Tiger Team agent card.
- Each agent card includes purpose, integrations, required human input, expected outcomes, and ROI assumptions.
- Stage-gate evidence exists for concept, pilot, and scale decisions.
- Agent value is communicated in consistent KPI and ROI terms across the catalog.

### FR-7: Security Approval Tiers and Rationale

The operating model must define clear security approval tiers in plain language so non-developers can understand when standard approvals are sufficient and when elevated approvals are mandatory.

Acceptance signals:

- Routine actions (read/draft/internal suggestions) are documented with standard approval path.
- Elevated-risk actions (send/write/sensitive-data/cross-system automation) require explicit Security/GRC and business-owner approval.
- Rationale for elevated approvals is documented in business terms (risk of data exposure, compliance issues, and customer impact).
- A simple quick-rule exists for non-technical users to classify approval level.

### FR-8: Agent-of-Agents Orchestration

The operating model must support orchestrated agent chains (agent-of-agents) using a three-tier trust model.

Acceptance signals:

- Tier 1 (read-only chains) are designed and testable in sandbox immediately.
- Tier 2 (draft chains with HITL gate) are piloted during the 45-day HITL window.
- Tier 3 (autonomous chains) require day-45 governance approval before activation.
- Every chain maps to a single measurable cycle-time reduction.
- Chain approval level inherits the highest approval level of any member agent.
- Maximum chain length is 6 agents during pilot; longer chains require architecture review.
- Every chain execution produces an observability log (agents fired, outputs, human interventions, elapsed time).
- Orchestration architecture reference: `docs/AGENT_OF_AGENTS_ARCHITECTURE.md`

## Non-Functional Requirements

### NFR-1: Security and Access

- Role-based access control for tools and actions.
- Least-privilege principle for agent permissions.
- Traceable action logs for review and compliance.

### NFR-2: Reliability

- Agent failures must degrade safely.
- Every workflow must define fallback behavior.
- Escalation to human owner must be available.

### NFR-3: Transparency

- Recommendations must include rationale and source references.
- Action provenance must be inspectable.

### NFR-4: Extensibility

- New playbooks should be pluggable without redesigning core orchestration.
- Reusable capabilities should be modular (classification, retrieval, planning, policy checks).

## Initial Candidate Agent Requirements

### Priority Creative Pilot: Outlook Email Chief-of-Staff Agent

- Platform: Outlook
- Scope: personal mailbox and team mailbox
- Core outputs: daily synopsis, decisions needed, action items, and suggested response drafts
- Outbound behavior: draft-only with human approval before any send action
- Governance marker: maintain human-in-the-loop review for first 45 days, then perform formal readiness review before any autonomy expansion
- Review objective: ensure quality, trust, policy adherence, and stakeholder comfort before changing controls

### PMO Lane

- Portfolio PMO Agent
- RAID Governance Agent
- Status Narrative Agent
- Milestone Integrity Agent

### Architecture and Engineering Lane

- Architecture Decision Agent
- Integration Design Agent
- Engineering Work Breakdown Agent
- Quality and Release Guard Agent

## Integration Requirements (Initial)

### Priority Systems

- Jira
- Confluence
- ServiceNow (or equivalent ticketing)
- GitHub/GitLab
- CI/CD pipeline tooling
- Observability tooling
- Identity provider / SSO / RBAC

### Platform Primitives

- Event and webhook backbone
- Shared context and memory store
- Policy and guardrail engine
- End-to-end audit log

## Governance Requirements

- Human-in-the-loop default for high-risk and customer-facing actions.
- Risk and compliance review before expanded autonomy.
- Standard go/no-go gates for wave progression.
- For the Outlook email pilot, enforce a minimum 45-day HITL review period before autonomy review.
- Security approval protocol reference: `docs/AGENT_FACTORY_EXECUTION_GUARDRAILS.md`.

## Dependencies and Unknowns

- Access to AI Playbooks source content (currently blocked by Atlassian authentication from this session).
- Confirmed system API readiness and access model by integration target.
- Baseline cycle-time values for top workflows.
- Final role owners and decision authority model (RACI).

## Open Questions (Rolling)

1. Which workflows are approved for autonomous action in first 60–90 days?
2. Which PMO and Architecture/Engineering roles are in first-wave scope?
3. Which integrations are already approved by security and platform teams?
4. What is the current baseline cycle time for each wave-1 workflow?
5. What are the target cycle-time reduction goals by quarter?

## Artifacts Requested (Rolling)

Please provide as available:

- AI playbook excerpts or exports
- SOPs and runbooks
- Case taxonomy and SLA definitions
- Existing KPI dashboards
- Escalation matrix and governance process docs
- Integration inventory and API readiness notes

Related planning artifact:

- `docs/AGENT_FACTORY_COLLATERAL_PLAN.md`
- `docs/TIGER_TEAM_AGENT_CATALOG_APPROACH.md`
- `docs/TIGER_TEAM_EXECUTIVE_BRIEF.md`
- `docs/AGENT_FACTORY_EXECUTION_GUARDRAILS.md`
- `docs/templates/AGENT_CARD_TEMPLATE.md`
- `docs/SECURITY_APPROVAL_CHEAT_SHEET.md`
- `docs/AGENT_OF_AGENTS_ARCHITECTURE.md`

## Change Log

### 2026-05-20

- Created initial living requirements structure.
- Captured current objectives, scope, agent lanes, integration assumptions, and open questions.
- Marked key dependencies pending source artifacts.
- Added reference to collateral planning document for executive and delivery audiences.
- Added concrete Outlook email pilot requirements with personal/team mailbox scope and 45-day HITL governance marker.
- Added FR-6 for Tiger Team agent catalog framework and linked approach document.
- Added references to executive brief and execution guardrails artifacts.
- Added Tiger Team agent card template reference.
- Added FR-7 for plain-language security approval tiers and rationale.
- Added security approval cheat sheet reference.
- Added FR-8 for agent-of-agents orchestration with three-tier trust model.
- Added reference to orchestration architecture document.
