# Agent Factory Activity Log

This is the detailed running log of work for the Service Delivery Agent Factory initiative.

## Purpose

- Keep a clear, readable history of decisions, outputs, and next steps.
- Provide continuity for collaborators joining mid-stream.
- Capture assumptions and unresolved items for fast follow-up.

## How to Use This Log

- Add new entries at the top under **Activity Entries**.
- Keep each entry concise but complete enough for someone outside the thread.
- Link to artifacts, diagrams, and requirements updates where possible.

## Activity Entries

### 2026-05-20 — Session 2 (Collateral expansion for broad readability)

#### 1) Audience strategy decision

- User confirmed collateral should be optimized for both executive and delivery audiences in parallel.

#### 2) New collateral planning artifact created

- Created `docs/AGENT_FACTORY_COLLATERAL_PLAN.md`.
- Added complete collateral inventory (`C1` to `C10`) with purpose, owner role, audience, and status.
- Added 90-day collateral milestones and update protocol.

#### 3) Cross-document linkage update

- Updated `docs/AGENT_FACTORY_REQUIREMENTS.md` to reference `docs/AGENT_FACTORY_COLLATERAL_PLAN.md`.

#### 4) Working-mode confirmation

- Model recommendation label will be included in each response moving forward.
- Ongoing prompts for artifacts, integrations, and context remain active.

#### 5) Creative pilot decisions confirmed (email agent)

- Platform selected: Outlook.
- Scope selected: personal mailbox and team mailbox.
- Outbound controls selected: draft-first with human review before send.
- Governance decision: initial 45-day HITL review period to allow broader stakeholder validation before autonomy expansion.

#### 6) Tiger Team catalog approach added

- Created `docs/TIGER_TEAM_AGENT_CATALOG_APPROACH.md`.
- Defined standard agent-card fields for purpose, integrations, human input, expected results, and ROI.
- Added stage-gate review model and KPI/ROI formula framework.
- Linked Tiger Team approach into requirements and collateral plan artifacts.

#### 7) Executive-share and execution guardrail artifacts added

- Created living executive brief: `docs/TIGER_TEAM_EXECUTIVE_BRIEF.md`.
- Exported Word version for leadership sharing: `docs/TIGER_TEAM_EXECUTIVE_BRIEF.docx`.
- Created scope-discipline tracker: `docs/AGENT_FACTORY_EXECUTION_GUARDRAILS.md`.
- Linked these artifacts in `docs/AGENT_FACTORY_REQUIREMENTS.md` for discoverability.

#### 8) Reusable agent card template added

- Created `docs/templates/AGENT_CARD_TEMPLATE.md` for standardized catalog intake.
- Included required sections for purpose, integrations, human controls, expected results, KPI/ROI, and stage-gate evidence.
- Linked template into collateral and requirements references.

#### 9) Plain-language security approval guidance added

- Added `Security Approval Protocol (Plain Language)` to `docs/AGENT_FACTORY_EXECUTION_GUARDRAILS.md`.
- Clarified routine vs elevated approvals and why elevated approvals are required.
- Added non-developer quick rule for classifying approval level.
- Added `FR-7` to requirements to formalize security approval tiers and rationale.

#### 10) Security approval cheat sheet added

- Created `docs/SECURITY_APPROVAL_CHEAT_SHEET.md` with Green/Yellow/Red approval model.
- Added straightforward non-developer guidance and decision-log requirements.
- Linked cheat sheet into core planning references.

#### 11) Airtable MCP execution workspace initialized

- Connected to Airtable base: `appWta0Gt4fZRjxB6`.
- Created core tables:
  - `Agent Catalog`
  - `Tasks`
  - `Milestones`
  - `Approvals`
  - `ROI Metrics`
  - `Risks`
  - `Integrations`
- Created dashboard-style views for leaders and delivery operations, including:
  - `Executive Value Dashboard`
  - `Agent Pipeline`
  - `Delivery Control Tower`
  - `This Week Priorities`
  - `Approval Queue`
  - `Elevated Security Reviews`
  - `ROI Dashboard`
  - `Risk Watchlist`
  - `Integration Readiness`
  - `45-Day HITL Timeline`
- Added key fields for cataloging value and controls (purpose, integrations, expected human input, expected results, approval level, ROI estimate, pilot dates).
- Seeded initial pilot records for:
  - Outlook email agent catalog entry
  - Initial delivery task
  - Day-45 milestone
  - Draft-send control approval record
- Adjusted implementation approach when Airtable field/template validation returned errors (moved to sequential field creation and stable field types).
- Attempted MCP-driven linked-record field creation; received `INVALID_REQUEST`.
- Implemented relational fallback with `Agent Catalog Key` fields across all core tables and documented one-click UI steps for true Airtable links.

### 2026-05-19 / 2026-05-20 — Session 1 (Strategy and initial operating model framing)

#### 1) Strategic direction established

- Service Delivery role updated to focus on building agents and agents-of-agents.
- Vision language framed as an **Agent Factory** to simplify customer experience at Cisco and internal work execution.

#### 2) Collaboration method agreed

- Iterative, deep-thinking workshop format requested.
- Assistant should continuously ask probing questions.
- Assistant should recommend best-fit LLM profile per objective as work progresses.

#### 3) Initial structure defined

- Three concurrent tracks established:
  - Operating model design
  - Targeted starter agent portfolio
  - Compounding architecture (agents of agents)

#### 4) Candidate operating model skeleton proposed

- Intake
- Triage
- Build
- Deploy
- Govern
- Scale

#### 5) Agent selection rubric proposed

Weighted scoring framework proposed with hard gates:

- Business impact (25%)
- Workload frequency (15%)
- Time-to-value (15%)
- Data readiness (15%)
- Process stability (10%)
- Risk/compliance fit (10%)
- Adoption readiness (10%)

Priority bands:

- 80+: build now
- 65–79: design/unblock
- <65: park/redesign

Hard gates:

- Named business owner
- Baseline KPI exists
- Human escalation path exists
- Logging/audit defined

#### 6) Initial starter portfolio proposed

Wave 1 candidates:

- Case Intake & Routing Agent
- Case Summary + Next-Best-Action Agent
- Knowledge Retrieval & Citation Agent
- Customer Update Drafting Agent

Wave 2 candidates:

- Incident Commander Agent (orchestrator)
- Knowledge Gap Miner Agent

#### 7) KPI priority decision captured

- Primary Q1 KPI selected: **cycle time**.

#### 8) Early autonomy split proposed

Proposed for first 60 days:

- Autonomous: tagging, routing, duplicate detection, SLA reminders
- Human-approved: customer communications, case closure, escalation overrides

Status: pending user confirmation/refinement.

#### 9) AI Playbooks source introduced

- Source link provided for Confluence AI Playbooks page.
- Access attempt failed due to Atlassian authentication wall.
- Constraint documented: source cannot be fetched directly from this session without authenticated access.

#### 10) Role-based mapping draft (assumption-based pending source extracts)

PMO-aligned agent lanes drafted:

- Portfolio PMO Agent
- RAID Governance Agent
- Status Narrative Agent
- Milestone Integrity Agent

Architecture/Engineering lanes drafted:

- Architecture Decision Agent
- Integration Design Agent
- Engineering Work Breakdown Agent
- Quality & Release Guard Agent

#### 11) Integration stack (initial)

Priority integration surfaces identified:

- Jira
- Confluence
- ServiceNow (or equivalent)
- GitHub/GitLab
- CI/CD
- Observability platform
- Identity/SSO and RBAC

Cross-agent platform primitives identified:

- Event/webhook backbone
- Shared memory/context store
- Policy/guardrail engine
- End-to-end audit logging

#### 12) Artifact request pattern established

User requested proactive prompts for:

- Additional artifacts
- Integration details
- Missing operating context

This pattern is now part of the working cadence.

## Decisions Register (Current)

- Direction: Agent Factory (agents + agents-of-agents)
- KPI focus: cycle time (Q1)
- Work mode: iterative, question-driven, deep-think
- Documentation mode: living docs for activity + requirements

#### 18) Agent-of-agents orchestration architecture designed

Three-tier model confirmed:

- **Tier 1 (Read Chain)**: Design now, sandbox test. Green approval. 3 chains designed: Case Insight, Governance Pulse, Weekly Readout.
- **Tier 2 (Draft Chain)**: Pilot during 45-day HITL. Yellow approval. 2 chains designed: Case Lifecycle, Meeting-to-Action.
- **Tier 3 (Autonomous Chain)**: Post-governance aspiration only.

#### 19) Orchestration design decisions locked

All design questions resolved:

- **First prototype**: CHAIN-004 (Case Lifecycle Chain). CHAIN-001 (Case Insight) runs in parallel as Tier 1 stepping stone.
- **HITL gate**: Single mid-chain gate after classification, before writes. Mechanism: Airtable Approval Queue.
- **Failure handling**: Retry with fallback (1 retry + 1 fallback agent, then stop and alert).
- **Scope guard**: Max 6 agents/chain + one KPI per chain + no new chains until first prototype has 2 weeks of evidence.
- **Orchestrator identity**: Capability layer, not a catalog agent. No ORCH-001.
- **Latency**: < 2 min required, < 30s aspiration for Tier 1. SLAs set at day-45 from pilot data.
- **HITL mechanism**: Airtable for both approval and dashboarding during pilot. Jira migration is post-pilot.
- **Observability**: Chain execution logs feed weekly readouts and day-45 governance package.

#### 20) Airtable Orchestration Chains table created

New table `Orchestration Chains` with fields: Tier, Member Agents, Cycle-Time Target, Approval Level, HITL Gate Position, Failure Mode, Target Due. Five chain records seeded. Kanban and Gallery views added.

## Constraints and Assumptions

- Confluence playbook details currently unavailable via direct tool fetch due to auth.
- Role mapping and integration model are currently assumption-based until artifacts are provided.
- Human-in-the-loop is assumed by default for externally visible or high-risk actions.

## Immediate Next Actions

1. Ingest user-provided playbook extracts and role documents.
2. Convert role-mapping draft into validated RACI model by function.
3. Finalize 90-day operating model with cycle-time milestones.
4. Define wave-1 integration sequence and dependency map.
5. Attach measurable baseline and target cycle-time deltas per agent.

## Update Checklist for Future Sessions

When updating this file each session:

- Add date/time and session ID.
- Record decisions made and why.
- Note what changed vs previous assumptions.
- Record unresolved questions and required inputs.
- Add links to requirement changes in `docs/AGENT_FACTORY_REQUIREMENTS.md`.
