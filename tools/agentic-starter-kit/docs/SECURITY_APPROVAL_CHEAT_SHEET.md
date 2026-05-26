# Security Approval Cheat Sheet (Green/Yellow/Red)

Use this quick guide to decide what approvals are required before enabling an agent capability.

## Why Approvals Exist

Approvals are needed to prevent:

- Data exposure
- Compliance violations
- Customer-impacting errors
- Fast, large-scale mistakes from automation

## Green: Routine Approval (Workflow Owner)

Use Green when the agent is limited to low-risk support behavior.

Typical actions:

- Read data
- Summarize information
- Draft suggestions for human review
- Create internal notes

Approval needed:

- Workflow owner or designated manager

Why this is lower risk:

- No irreversible action is taken
- Human remains final decision-maker

## Yellow: Elevated Approval (Workflow Owner + Security/GRC)

Use Yellow when the agent can change internal systems or touch sensitive data.

Typical actions:

- Write updates to internal tools
- Trigger workflow actions automatically
- Use sensitive or customer-protected data

Approval needed:

- Workflow owner
- Security/GRC reviewer

Required checks:

- Least-privilege access
- Audit logging enabled
- Rollback/fallback defined
- Escalation path documented

## Red: Restricted / Executive Gate (Workflow Owner + Security/GRC + Leadership)

Use Red when mistakes could cause major external or compliance impact.

Typical actions:

- External autonomous sends
- High-impact production changes
- Broad cross-system autonomous actions

Approval needed:

- Workflow owner
- Security/GRC reviewer
- Leadership/governance authority

Required checks:

- Formal risk assessment completed
- Control validation from pilot evidence
- Incident response playbook approved
- Explicit go/no-go decision recorded

## Quick Non-Developer Rule

- If the agent only reads and drafts, it is usually Green.
- If the agent writes internally or uses sensitive data, it is Yellow.
- If the agent acts externally or at high scale autonomously, it is Red.

## Example: Outlook Email Chief-of-Staff Agent

Current mode:

- Draft-only with human approval before send
- Scope: personal + team mailbox
- 45-day HITL review period

Current approval color:

- Green for summary/draft behavior
- Yellow/Red review required before any autonomous sending

## Decision Log Requirement

Every approval must capture:

- Agent name and capability approved
- Approval color (`Green`, `Yellow`, `Red`)
- Approver names and date
- Conditions and expiry/review date
