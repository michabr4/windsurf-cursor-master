# Agent Factory Execution Guardrails (Keep Us Honest)

This document keeps sequencing disciplined so requests do not jump ahead of required foundations.

## Current Phase

- Phase: `Foundation + Pilot Readiness`
- Date: `2026-05-20`
- Priority KPI: `Cycle Time`

## What Is Already Done

- Agent Factory strategy direction documented.
- Living requirements doc created and maintained.
- Living activity log created and maintained.
- Collateral plan for executive + delivery audiences created.
- Outlook email pilot controls defined:
  - personal + team mailbox scope
  - draft-first send control
  - 45-day HITL governance marker
- Tiger Team catalog approach documented.
- Executive brief created from Tiger Team approach.
- Agent-of-agents orchestration architecture designed (3 tiers, 5 chains).
- CHAIN-004 (Case Lifecycle) confirmed as first prototype.
- Retry-with-fallback failure handling confirmed.
- Scope guard: no new chains until first prototype has 2 weeks of evidence.

## What Must Be Done Next (In Order)

1. Confirm baseline cycle-time metrics for pilot workflows.
2. Define day-45 readiness scorecard thresholds.
3. Confirm Outlook integration permissions and mailbox access model.
4. Finalize reviewer roster for HITL period.
5. Run pilot and collect weekly evidence.
6. Produce day-45 recommendation (scale / hold / redesign).

## Agent-of-Agents Orchestration Gates

- **Tier 1 (read-only chains)**: Design and sandbox test now. Green approval only.
- **Tier 2 (draft chains)**: Pilot during 45-day HITL window. Yellow approval required. Single mid-chain human gate before any write/send. Gate mechanism: Airtable Approval Queue (kanban). Jira migration is post-pilot.
- **Tier 3 (autonomous chains)**: Blocked until day-45 governance decision = "scale" + Security/GRC signoff.
- Chain approval level = highest approval level of any member agent.
- Maximum 6 agents per chain during pilot.
- Architecture reference: `docs/AGENT_OF_AGENTS_ARCHITECTURE.md`

## Do Not Skip Gates

- Do not enable autonomous send before day-45 review package is approved.
- Do not add new pilot scope until baseline metrics are captured.
- Do not claim ROI until volume and time-saved assumptions are validated.
- Do not activate Tier 2 chains until individual member agents have passed their own pilot gates.
- Do not activate Tier 3 chains until Tier 2 evidence package is reviewed by governance.

## Security Approval Protocol (Plain Language)

This section explains when normal approvals are enough and when extra approvals are required.

### Routine approvals (common case)

These actions are usually low risk and can use normal workflow-owner approval:

- Reading data to generate summaries
- Drafting recommendations for human review
- Creating internal notes or suggested task lists

Why this level is usually enough:

- The agent is not taking irreversible actions.
- A human still confirms outcomes before external impact.

### Elevated approvals (security-risk cases)

These actions require Security/GRC plus business-owner approval before enablement:

- Sending external communications automatically
- Writing to production systems (status changes, closures, escalations)
- Accessing sensitive data classes (confidential, regulated, customer-sensitive)
- Cross-system automation that could spread incorrect actions quickly

Why elevated approvals are needed:

- Mistakes can cause data exposure, compliance violations, or customer harm.
- Automated writes can create large-scale errors faster than humans can stop.
- Security teams must confirm controls are in place before risk increases.

### Required evidence before elevated approval

- Access control review (least privilege)
- Audit logging confirmation (who did what, when)
- Fallback and rollback plan
- Human escalation path
- Pilot quality metrics meeting agreed thresholds

### Non-developer quick rule

If the agent can only read and draft, normal approvals are usually fine.
If the agent can send, write, or touch sensitive data, elevated approvals are mandatory.

Supporting reference:

- `docs/SECURITY_APPROVAL_CHEAT_SHEET.md`
- `docs/AGENT_FACTORY_CONSOLIDATED_REQUIREMENTS.md`

## Output Preview (What Leaders Will Receive)

### Weekly Outputs

- Pilot status summary
- KPI trend snapshot
- Risk and blocker log
- Decision requests

### Day-45 Output Package

- Pilot scorecard (quality, trust, cycle-time, reviewer effort)
- ROI estimate with assumptions
- Governance recommendation:
  - Continue HITL
  - Limited autonomy expansion
  - Hold/redesign

### Monthly Executive Output

- Agent catalog value readout
- Top 3 wins and top 3 risks
- Next-quarter scale decisions

## Owner Checkpoints

- PMO: cadence and decision governance
- Architecture/Engineering: integration and delivery readiness
- Security/GRC: control and policy readiness
- Workflow owner: business outcome accountability

## Update Protocol

When scope expands, this file must be updated first:

1. Add new requested scope item.
2. Tag as `Now`, `Next`, or `Later`.
3. Attach required gate(s) before execution.
4. Link expected output artifact.
