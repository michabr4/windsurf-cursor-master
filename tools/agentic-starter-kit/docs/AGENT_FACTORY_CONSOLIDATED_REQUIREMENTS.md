# Agent Factory — Consolidated Requirements Document

## Document Control

- Version: `v1.0`
- Status: `Active`
- Date: `2026-05-20`
- Owner: Service Delivery Agent Factory
- Primary KPI: `Cycle Time`

This is the single source of truth for all requirements — completed and forward-looking — for the Agent Factory initiative including individual agents, agent-of-agents orchestration, governance, tooling, and collateral.

---

## 1. Business Objective

Design and operationalize an Agent Factory that builds role-aligned agents and orchestrated agent chains (agents-of-agents) to:

- Simplify Cisco customer experiences.
- Simplify internal service delivery workflows.
- Reduce end-to-end cycle time across delivery activities.
- Compound individual agent value through multi-agent orchestration.

---

## 2. Scope

### 2.1 In Scope

- Practical operating model: intake → build → govern → scale.
- PMO role-mapped agent design.
- Architecture and Engineering role-mapped agent design.
- Agent-of-agents orchestration (three-tier trust model).
- Integration mapping across Jira, Confluence, ServiceNow, Outlook, GitHub/GitLab.
- AI playbook-to-agent composition.
- 90-day wave-1 rollout plan.
- Airtable-based execution tracking and HITL gate workflow.
- Leadership collateral and evidence packaging.

### 2.2 Out of Scope (Current)

- Full autonomous production actions without guardrails.
- Finalized platform implementation details per tool.
- Detailed budget and staffing model.
- Jira-based HITL gate (post-pilot maturity step).

---

## 3. Stakeholders and Roles

### 3.1 Core Groups

- **Service Delivery leadership** — strategic direction, scale decisions.
- **PMO leadership and program teams** — portfolio prioritization, delivery cadence.
- **Architecture leadership and architects** — standards, design governance.
- **Engineering managers and delivery teams** — implementation, release execution.
- **Security, compliance, and governance partners** — risk controls, policy exceptions.

### 3.2 Decision Authority (RACI — to validate)

| Function | Responsibility |
| --- | --- |
| PMO | Portfolio and delivery prioritization |
| Architecture | Standards and design-governance approvals |
| Engineering | Implementation sequencing and release execution |
| Governance | Risk controls and policy exceptions |

---

## 4. Functional Requirements

### FR-1: Intake and Triage

The operating model must support standardized intake and triage of agent opportunities.

| Acceptance Signal | Status |
| --- | --- |
| Each proposal has a named business owner | Defined |
| Each proposal is scored against a shared rubric | Defined |
| Each proposal is assigned to a delivery wave | Defined |

### FR-2: Role-Mapped Agent Design

Agents must map to PMO and Architecture/Engineering workflows with clear human decision points.

| Acceptance Signal | Status |
| --- | --- |
| Each agent has role alignment, inputs, outputs, escalation path | Designed |
| Human approval gates defined for high-impact actions | Designed |

### FR-3: Playbook Composition

AI playbooks must be reusable as composable modules for agent behavior.

| Acceptance Signal | Status |
| --- | --- |
| Each module includes trigger, inputs, outputs, policy gates | Defined |
| Orchestrator can invoke multiple approved modules | Designed |

### FR-4: Integration Layer

The platform must integrate with delivery systems to read, recommend, and track.

| Acceptance Signal | Status |
| --- | --- |
| Priority integrations sequenced by value and feasibility | Pending — API access not yet confirmed |
| Identity, permissions, auditability enforced | Defined in guardrails |

### FR-5: Measurement and Governance

Baseline and ongoing measurement of cycle-time improvements with governance controls.

| Acceptance Signal | Status |
| --- | --- |
| Baseline cycle-time metric per targeted workflow | Pending — next execution step |
| Target cycle-time reduction per wave | Designed per chain |
| Audit logs for recommendations and actions | Designed in execution log schema |

### FR-6: Tiger Team Agent Catalog Framework

Standardized documentation of each agent's purpose, integrations, human input, results, and ROI.

| Acceptance Signal | Status |
| --- | --- |
| Every agent has a Tiger Team agent card | Template created |
| Cards include purpose, integrations, human input, outcomes, ROI | Template complete |
| Stage-gate evidence for concept, pilot, scale | Gates defined |
| Consistent KPI/ROI terms across catalog | ROI formula framework defined |

### FR-7: Security Approval Tiers

Plain-language security approval tiers (Green/Yellow/Red) for technical and non-technical users.

| Acceptance Signal | Status |
| --- | --- |
| Routine actions documented with standard path | Complete |
| Elevated-risk actions require Security/GRC + business owner | Complete |
| Rationale documented in business terms | Complete |
| Quick-rule for non-technical users | Complete |

### FR-8: Agent-of-Agents Orchestration

Orchestrated agent chains using a three-tier trust model.

| Acceptance Signal | Status |
| --- | --- |
| Tier 1 (read-only chains) designed and sandbox-testable | Complete — 3 chains designed |
| Tier 2 (draft + HITL gate) piloted during 45-day window | Complete — 2 chains designed |
| Tier 3 (autonomous) requires governance approval | Defined — 3 concepts sketched |
| Every chain maps to one cycle-time reduction | Complete |
| Chain approval inherits highest member agent level | Complete |
| Max 6 agents per chain during pilot | Complete |
| Observability log per chain execution | Designed — Airtable schema pending |
| All design questions resolved | Complete — 8 of 8 resolved |

---

## 5. Non-Functional Requirements

### NFR-1: Security and Access

- Role-based access control for tools and actions.
- Least-privilege principle for agent permissions.
- Traceable action logs for review and compliance.

### NFR-2: Reliability

- Agent failures degrade safely (retry with fallback, then stop and alert).
- Every workflow defines fallback behavior.
- Escalation to human owner is always available.
- Chain failure handling: 1 retry → 1 fallback agent → stop and alert. Never loop indefinitely.

### NFR-3: Transparency

- Recommendations include rationale and source references.
- Action provenance is inspectable.
- Chain execution logs capture: agents fired, outputs, human interventions, elapsed time, outcome.

### NFR-4: Extensibility

- New playbooks are pluggable without redesigning core orchestration.
- Reusable capabilities are modular (classification, retrieval, planning, policy checks).
- Orchestrator is a capability layer, not a catalog agent — no standalone ORCH-001.

### NFR-5: Performance

- All chains must complete automated segments in < 2 minutes.
- Tier 1 read-only chains have a < 30 second aspiration.
- Actual SLAs set at day-45 based on pilot measurement data.

---

## 6. Agent Catalog

### 6.1 Priority Pilot

| Agent ID | Name | Lane | Status |
| --- | --- | --- | --- |
| AGT-001 | Outlook Email Chief-of-Staff | Cross-functional | **Scaffolded** — `python/src/agt001_email_chief_of_staff.py` |

- Platform: Outlook (personal + team mailbox)
- Outputs: daily synopsis, decisions needed, action items, draft responses
- Control: draft-only with human approval before send
- Governance: 45-day HITL review, then formal readiness review

### 6.2 PMO Lane

| Agent ID | Name | Status |
| --- | --- | --- |
| AGT-005 | RAID Governance Agent | Designed |
| AGT-007 | Portfolio PMO Agent | Cataloged |
| AGT-008 | Status Narrative Agent | Cataloged |
| AGT-009 | Milestone Integrity Agent | Cataloged |

### 6.3 Architecture and Engineering Lane

| Agent ID | Name | Status |
| --- | --- | --- |
| AGT-002 | Case Intake & Routing Agent | Designed |
| AGT-003 | Case Summary + Next-Best-Action Agent | Designed |
| AGT-004 | Knowledge Retrieval & Citation Agent | Designed |
| AGT-006 | Meeting-to-Execution Agent | Designed |
| AGT-010 | Architecture Decision Agent | Cataloged |
| AGT-011 | Integration Design Agent | Cataloged |
| AGT-012 | Engineering Work Breakdown Agent | Cataloged |
| AGT-013 | Quality and Release Guard Agent | Cataloged |

---

## 7. Orchestration Chains

### 7.1 Tier 1 — Read Chains (Active Now)

| Chain ID | Name | Agents | Cycle-Time Target | Approval |
| --- | --- | --- | --- | --- |
| CHAIN-001 | Case Insight | AGT-001, AGT-004, AGT-003 | Save 15–30 min/case | Green |
| CHAIN-002 | Governance Pulse | AGT-005, AGT-001, AGT-006 | Save 1–2 hrs/week | Green |
| CHAIN-003 | Weekly Readout | AGT-003, AGT-005, AGT-001 | Save 2–3 hrs/week | Green |

### 7.2 Tier 2 — Draft Chains (45-Day HITL Pilot)

| Chain ID | Name | Agents | Cycle-Time Target | Approval |
| --- | --- | --- | --- | --- |
| CHAIN-004 | Case Lifecycle | AGT-001, AGT-002, AGT-004, AGT-003 | Hours → minutes per case | Yellow |
| CHAIN-005 | Meeting-to-Action | AGT-006, AGT-005, AGT-001 | Eliminate manual transcription | Yellow |

### 7.3 Tier 3 — Autonomous Chains (Post-Governance)

| Concept | Based On | Prerequisite |
| --- | --- | --- |
| Full Case Autopilot | CHAIN-004 | >95% draft acceptance, Security/GRC signoff |
| Proactive Risk Autopilot | CHAIN-002 | PMO trust met, <5% false-positive rate |
| Self-Healing Workflow | New | Full integration across ServiceNow + Jira + Outlook |

### 7.4 Confirmed Orchestration Decisions

| Decision | Resolution |
| --- | --- |
| First prototype | CHAIN-004 (Case Lifecycle). CHAIN-001 runs in parallel as Tier 1 stepping stone. |
| HITL gate position | Single mid-chain gate — after classification, before writes. |
| Failure handling | Retry with fallback (1 retry + 1 fallback agent → stop and alert). |
| Scope guard | Max 6 agents/chain + 1 KPI/chain + no new chains until 2 weeks of evidence. |
| Orchestrator identity | Capability layer, not a catalog agent. |
| Latency | < 2 min required, < 30s aspiration for Tier 1. SLAs from pilot data. |
| HITL mechanism | Airtable for both approval and dashboarding. Jira migration is post-pilot. |
| Observability | Chain execution logs feed weekly readouts and day-45 package. |

---

## 8. Governance Requirements

### 8.1 Core Governance Controls

- Human-in-the-loop default for high-risk and customer-facing actions.
- Risk and compliance review before expanded autonomy.
- Standard go/no-go gates for wave progression.
- Minimum 45-day HITL review period for Outlook pilot before autonomy review.

### 8.2 Security Approval Model (Green/Yellow/Red)

| Level | When | Approvers |
| --- | --- | --- |
| Green | Read and draft only | Workflow owner |
| Yellow | Write to internal systems or use sensitive data | Workflow owner + Security/GRC |
| Red | External autonomous sends or high-scale automation | Workflow owner + Security/GRC + Leadership |

Reference: `docs/SECURITY_APPROVAL_CHEAT_SHEET.md`

### 8.3 Do-Not-Skip Gates

- Do not enable autonomous send before day-45 review package is approved.
- Do not add new pilot scope until baseline metrics are captured.
- Do not claim ROI until volume and time-saved assumptions are validated.
- Do not activate Tier 2 chains until individual member agents pass their own pilot gates.
- Do not activate Tier 3 chains until Tier 2 evidence package is reviewed by governance.
- Do not design new chains until the first prototype has 2 weeks of evidence.

### 8.4 Day-45 Decision Package

- Pilot scorecard: quality, trust, cycle-time, reviewer effort.
- ROI estimate with assumptions.
- Governance recommendation: continue HITL / limited autonomy / hold / redesign.

---

## 9. Integration Requirements

### 9.1 Priority Systems

| System | Purpose | API Status |
| --- | --- | --- |
| Outlook | Email read/draft/send | Pending — permissions to confirm |
| Jira | Task/case management | Pending — API readiness check |
| Confluence | Knowledge base, playbooks | Pending — auth blocked in current session |
| ServiceNow | Ticketing (or equivalent) | Pending |
| GitHub/GitLab | Code and release management | Pending |
| CI/CD tooling | Pipeline integration | Pending |
| Identity provider | SSO/RBAC enforcement | Pending |

### 9.2 Platform Primitives Required

- Event and webhook backbone.
- Shared context and memory store.
- Policy and guardrail engine.
- End-to-end audit log.

---

## 10. Execution Tracking (Airtable)

### 10.1 Base

- Base ID: `appWta0Gt4fZRjxB6`

### 10.2 Tables

| Table | Purpose |
| --- | --- |
| Agent Catalog | Individual agent registry and status |
| Tasks | Execution tasks with dependencies |
| Milestones | Key milestone tracking (45-day HITL, wave gates) |
| Approvals | HITL gate decisions and security approvals |
| Risks | Risk watchlist and mitigation |
| Integrations | System integration readiness |
| ROI Metrics | Value measurement and evidence |
| Orchestration Chains | Agent-of-agents chain tracking |

### 10.3 Dashboard Views

| View | Table | Type |
| --- | --- | --- |
| Executive Value Dashboard | Agent Catalog | Gallery |
| Agent Pipeline | Agent Catalog | Kanban |
| Delivery Control Tower | Tasks | Levels |
| This Week Priorities | Tasks | Kanban |
| Blocked Work | Tasks | Kanban |
| Approval Queue | Approvals | Kanban |
| Elevated Security Reviews | Approvals | Kanban |
| ROI Dashboard | ROI Metrics | Gallery |
| Risk Watchlist | Risks | Gallery |
| Integration Readiness | Integrations | Gallery |
| 45-Day HITL Timeline | Milestones | Gallery |
| Orchestration Pipeline | Orchestration Chains | Kanban |
| Chain Architecture | Orchestration Chains | Gallery |

### 10.4 Pending Airtable Work

- Build chain execution log table (per-run observability).
- Complete UI linked-record setup (`Agent Link` fields).
- Add formula/rollup fields for executive scorecards.

---

## 11. Collateral Plan

| ID | Collateral | Audience | Status |
| --- | --- | --- | --- |
| C1 | Executive brief | Leadership | Complete |
| C2 | Tiger Team approach | Delivery + governance | Complete |
| C3 | Agent card template | Tiger Team | Complete |
| C4 | Security cheat sheet | All stakeholders | Complete |
| C5 | Execution guardrails | All stakeholders | Complete |
| C6 | Orchestration architecture | Architecture + engineering | Complete |
| C7 | Airtable implementation status | Delivery | Complete |
| C8 | Weekly pilot status | Leadership | Template defined |
| C9 | Day-45 decision package | Governance | Template defined |
| C10 | Monthly executive readout | Leadership | Template defined |
| C11 | ROI evidence pack | Finance + governance | Template defined |

---

## 12. Current Phase and Next Steps

### Phase: Foundation + Pilot Readiness

### Completed

- Strategy direction documented.
- Living requirements, activity log, and collateral plan created.
- Outlook email pilot controls defined (draft-first, 45-day HITL).
- Tiger Team catalog approach and executive brief created.
- Security approval tiers (Green/Yellow/Red) documented.
- Agent-of-agents orchestration architecture designed (3 tiers, 5 chains, 8 design decisions resolved).
- Airtable execution workspace seeded (8 tables, 13+ views, starter records).

### Next Steps (In Order)

1. Capture baseline cycle-time metrics for CHAIN-004 member agents (AGT-001, AGT-002, AGT-003, AGT-004).
2. Build Airtable chain execution log table for per-run observability.
3. Define day-45 readiness scorecard thresholds.
4. Confirm Outlook integration permissions and mailbox access model.
5. Finalize reviewer roster for HITL period.
6. Run pilot and collect weekly evidence.
7. Produce day-45 recommendation (scale / hold / redesign).

---

## 13. Dependencies and Risks

### Dependencies

- Access to AI Playbooks source content (Confluence auth currently blocked).
- Confirmed system API readiness by integration target.
- Baseline cycle-time values for top workflows.
- Final role owners and decision authority model (RACI).

### Open Questions

1. Which workflows are approved for autonomous action in first 60–90 days?
2. Which PMO and Architecture/Engineering roles are in first-wave scope?
3. Which integrations are already approved by security and platform teams?
4. What is the current baseline cycle time for each wave-1 workflow?
5. What are the target cycle-time reduction goals by quarter?

---

## 14. Related Artifacts

| Document | Path |
| --- | --- |
| Requirements (original living doc) | `docs/AGENT_FACTORY_REQUIREMENTS.md` |
| Execution Guardrails | `docs/AGENT_FACTORY_EXECUTION_GUARDRAILS.md` |
| Orchestration Architecture | `docs/AGENT_OF_AGENTS_ARCHITECTURE.md` |
| Tiger Team Approach | `docs/TIGER_TEAM_AGENT_CATALOG_APPROACH.md` |
| Executive Brief | `docs/TIGER_TEAM_EXECUTIVE_BRIEF.md` |
| Collateral Plan | `docs/AGENT_FACTORY_COLLATERAL_PLAN.md` |
| Agent Card Template | `docs/templates/AGENT_CARD_TEMPLATE.md` |
| Security Cheat Sheet | `docs/SECURITY_APPROVAL_CHEAT_SHEET.md` |
| Airtable Status | `docs/AIRTABLE_IMPLEMENTATION_STATUS.md` |
| Outlook API Access Guide | `docs/OUTLOOK_API_ACCESS_GUIDE.md` |
| Activity Log | `docs/AGENT_FACTORY_ACTIVITY_LOG.md` |

---

## 15. Change Log

### 2026-05-20 — v1.0

- Created consolidated requirements document from all living docs.
- Merged FR-1 through FR-8 with completion status tracking.
- Added full agent catalog with IDs and lane assignments.
- Added orchestration chain inventory with all 8 resolved design decisions.
- Added Airtable execution workspace inventory (tables, views, pending work).
- Added collateral plan status tracker.
- Added integration requirements with API readiness status.
- Added governance model with do-not-skip gates and day-45 package definition.
- Added phase status with completed items and ordered next steps.
- Added dependencies, open questions, and artifact cross-references.
