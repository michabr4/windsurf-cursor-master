# Agent-of-Agents Orchestration Architecture

This document defines the compounding architecture for chaining individual agents into orchestrated workflows (agent-of-agents).

## Document Status

- Version: `v0.1`
- Status: `Design / Active`
- Date: `2026-05-20`
- Governing doc: `docs/AGENT_FACTORY_EXECUTION_GUARDRAILS.md`

## Orchestration Tier Model

### Tier 1 — Read Chain (Design Now)

- **Trust level**: Green (routine approval)
- **Capability**: Read-only. No writes, no sends, no state changes.
- **Human checkpoint**: End of chain only (review final output).
- **When**: Available immediately for design and sandbox testing.

### Tier 2 — Draft Chain (Pilot During 45-Day HITL)

- **Trust level**: Yellow (elevated approval)
- **Capability**: Chain produces a draft artifact; human approves before any write or send.
- **Human checkpoint**: Single defined gate before any write action.
- **When**: Piloted during the 45-day HITL window alongside individual agent pilots.

### Tier 3 — Autonomous Chain (Post-Governance Aspiration)

- **Trust level**: Red (restricted approval)
- **Capability**: End-to-end execution with audit trail and rollback.
- **Human checkpoint**: Exception-only (alert on anomaly, low confidence, or policy trigger).
- **When**: Only after day-45 governance decision = "scale" and Security/GRC signoff.

## Tier 1 Chain Designs (Active)

### Chain 1: Case Insight Chain

**Purpose**: Reduce time-to-understanding for incoming cases.
**Cycle-time target**: Eliminate 15–30 min of manual triage per case.

| Step | Agent | Action | Output |
|------|-------|--------|--------|
| 1 | AGT-001 Email Chief-of-Staff | Read and summarize incoming case email | Structured summary with urgency flag |
| 2 | AGT-004 Knowledge Retrieval | Search KB for matching resolutions | Top 3 cited articles with confidence scores |
| 3 | AGT-003 Case Summary | Combine email context + KB results into recommendation | One-page case brief with recommended next action |

**Human checkpoint**: Engineer reviews the case brief before acting.
**Failure mode**: If AGT-004 returns zero matches, chain skips KB step and flags "no prior resolution found" in the brief.

### Chain 2: Governance Pulse Chain

**Purpose**: Surface risks and blockers before they become escalations.
**Cycle-time target**: Replace 1–2 hours of weekly manual RAID scanning.

| Step | Agent | Action | Output |
|------|-------|--------|--------|
| 1 | AGT-005 RAID Governance | Scan Jira/Confluence for new risks, assumptions, issues, dependencies | RAID item list with severity |
| 2 | AGT-001 Email Chief-of-Staff | Summarize RAID items into a digest | Formatted risk digest |
| 3 | AGT-006 Meeting-to-Execution | Cross-reference open RAID items against upcoming meetings | Meeting prep brief with flagged RAID items per agenda |

**Human checkpoint**: PMO reviews digest before distribution.
**Failure mode**: If AGT-005 returns no new items, chain outputs "No new RAID items detected — prior items unchanged" and skips steps 2–3.

### Chain 3: Weekly Readout Chain

**Purpose**: Auto-assemble the weekly executive readout package.
**Cycle-time target**: Reduce 2–3 hours of manual slide assembly to 15 min review.

| Step | Agent | Action | Output |
|------|-------|--------|--------|
| 1 | AGT-003 Case Summary | Pull cycle-time deltas from pilot data | KPI snapshot section |
| 2 | AGT-005 RAID Governance | Pull open risk count and top blockers | Risk section |
| 3 | AGT-001 Email Chief-of-Staff | Combine into narrative executive summary | Draft readout document |

**Human checkpoint**: Lead reviews and approves before sending to leadership.
**Failure mode**: If any agent returns incomplete data, chain marks that section as "Data pending — manual input required" rather than hallucinating.

## Tier 2 Chain Designs (Pilot During HITL)

### Chain 4: Case Lifecycle Chain (Draft Mode)

**Purpose**: Handle a case from intake through response draft.
**Cycle-time target**: Reduce end-to-end case handling from hours to minutes.

| Step | Agent | Action | Output |
|------|-------|--------|--------|
| 1 | AGT-001 Email Chief-of-Staff | Summarize incoming case | Structured summary |
| 2 | AGT-002 Case Intake & Routing | Classify and recommend queue assignment | Routing recommendation |
| 3 | AGT-004 Knowledge Retrieval | Retrieve resolution guidance | Cited KB articles |
| 4 | AGT-003 Case Summary | Synthesize into recommended response | Draft response |
| **HITL GATE** | Human reviewer | Approve routing + response before write/send | Go / Revise / Reject |
| 5 | AGT-002 Case Intake & Routing | Execute approved routing | Case routed |
| 6 | AGT-001 Email Chief-of-Staff | Place approved response in Outlook drafts | Draft ready for send |

**Security level**: Yellow — write actions gated behind human approval.
**Failure mode**: If HITL gate returns "Reject," chain stops and logs rejection reason for prompt tuning.

### Chain 5: Meeting-to-Action Chain (Draft Mode)

**Purpose**: Convert meeting outcomes into tracked actions without manual transcription.

| Step | Agent | Action | Output |
|------|-------|--------|--------|
| 1 | AGT-006 Meeting-to-Execution | Extract action items from meeting notes | Action list with owners and dates |
| 2 | AGT-005 RAID Governance | Flag any actions that overlap existing RAID items | Conflict alerts |
| 3 | AGT-001 Email Chief-of-Staff | Draft follow-up email to attendees | Draft email |
| **HITL GATE** | Meeting owner | Review actions + email draft | Go / Revise / Reject |
| 4 | AGT-006 Meeting-to-Execution | Publish actions to Jira | Tasks created |
| 5 | AGT-001 Email Chief-of-Staff | Place email in Outlook drafts | Draft ready for send |

**Security level**: Yellow — Jira writes and email drafts gated behind human approval.

## Tier 3 Chain Vision (Post-Governance)

These chains are **design concepts only** until governance approves autonomy expansion.

- **Full Case Autopilot**: Case Lifecycle Chain without HITL gate. Auto-route, auto-respond, auto-close with audit trail. Requires: >95% draft acceptance rate during Tier 2 pilot, Security/GRC signoff, rollback mechanism.
- **Proactive Risk Autopilot**: Governance Pulse Chain that auto-escalates high-severity RAID items and auto-schedules mitigation meetings. Requires: PMO trust threshold met, false-positive rate <5%.
- **Self-Healing Workflow**: Orchestrator detects stalled cases, auto-reassigns, and auto-follows-up. Requires: full integration readiness across ServiceNow + Jira + Outlook.

## Orchestration Design Principles

1. **Chain length limit**: Maximum 6 agents per chain during pilot. Longer chains require architecture review.
2. **Single KPI per chain**: Every chain must map to one measurable cycle-time reduction.
3. **Failure handling — Retry with fallback**: On agent failure or low confidence, retry once with an alternate prompt strategy. If retry fails, invoke a simpler fallback agent. If fallback also fails, stop the chain and alert the human. Never loop indefinitely. Never hallucinate missing data.
4. **Observability**: Every chain execution produces a log: which agents fired, what each returned, where human intervened, total elapsed time, and outcome (accepted/revised/rejected). Logs feed into the weekly executive readout and day-45 governance package.
5. **Security inheritance**: The chain's approval level = the highest approval level of any individual agent in the chain. A chain containing one Yellow agent is a Yellow chain.
6. **Scope guard**: No new chains may be designed until the first prototype chain (CHAIN-004) has at least 2 weeks of execution evidence.
7. **Prototype priority**: CHAIN-004 (Case Lifecycle) is the confirmed first prototype. CHAIN-001 (Case Insight, Tier 1) runs as a parallel stepping stone while CHAIN-004 member agents mature.

## Resolved Design Decisions

1. **First prototype**: CHAIN-004 (Case Lifecycle) confirmed. CHAIN-001 (Case Insight) runs in parallel as Tier 1 stepping stone.
2. **HITL gate position**: Single mid-chain gate — after classification, before any write/send action.
3. **Failure handling**: Retry with fallback (1 retry + 1 fallback agent, then stop and alert).
4. **Scope guard**: Max 6 agents/chain + one KPI per chain + no new chains until first has 2 weeks of evidence.
5. **Observability**: Chain execution logs feed into weekly readouts and day-45 package automatically.
6. **Orchestrator identity**: The orchestrator is a capability layer, not a catalog agent. It does not get its own agent card (no ORCH-001). Chains are tracked in the Orchestration Chains table. If a general-purpose orchestration engine is built later for team self-service, revisit this decision.
7. **Latency targets**: All chains must complete automated segments in < 2 minutes. Tier 1 read-only chains have a < 30 second aspiration. Actual SLAs will be set at day-45 based on pilot measurement data. Chain elapsed time is captured in the execution log.
8. **HITL gate mechanism**: Airtable is used for both approval and dashboarding during pilot. Reviewers use the Approval Queue (kanban) to approve/revise/reject chain outputs. All decision data stays in one place for the day-45 evidence package. Jira migration is a post-pilot maturity step once API access is confirmed.

## All Design Questions Resolved

No open design questions remain. Next decisions will emerge from pilot execution data.

## Related Documents

- `docs/AGENT_FACTORY_CONSOLIDATED_REQUIREMENTS.md` — Single source of truth (sections 4, 7, 8)
- `docs/AGENT_FACTORY_REQUIREMENTS.md` — FR-3 (Playbook Composition), FR-8 (Orchestration)
- `docs/AGENT_FACTORY_EXECUTION_GUARDRAILS.md` — Tier gates and security protocol
- `docs/SECURITY_APPROVAL_CHEAT_SHEET.md` — Green/Yellow/Red model
- `docs/TIGER_TEAM_AGENT_CATALOG_APPROACH.md` — Agent card standard

## Change Log

### 2026-05-20

- Created initial orchestration architecture with three-tier model.
- Designed three Tier 1 chains: Case Insight, Governance Pulse, Weekly Readout.
- Designed two Tier 2 chains: Case Lifecycle, Meeting-to-Action.
- Sketched three Tier 3 aspirational chains.
- Defined orchestration design principles and open questions.
- Confirmed CHAIN-004 as first prototype with single mid-chain HITL gate.
- Confirmed retry-with-fallback failure handling (1 retry + 1 fallback then stop).
- Added scope guard: no new chains until first prototype has 2 weeks of evidence.
- Resolved 3 of 5 open design questions; 3 remained open.
- Resolved all remaining questions: orchestrator as capability layer, <2 min latency (<30s aspiration for Tier 1), Airtable for both HITL gate and dashboarding.
