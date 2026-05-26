# Airtable Implementation Status (Agent Factory)

## Base

- Base ID: `appWta0Gt4fZRjxB6`

## Tables Created

- `Agent Catalog` (`tbleBsZCUAQFDyke2`)
- `Tasks` (`tblpbt0OwF8eDmZQy`)
- `Milestones` (`tbl5OAYfP4JYTQeTT`)
- `Approvals` (`tblonF7X0yc2Z1IFE`)
- `ROI Metrics` (`tblTbWC5RMFqUATEL`)
- `Risks` (`tblmCsEzmLk1a40xq`)
- `Integrations` (`tblGryTapzwscFaZS`)

## Views Created

### Agent Catalog

- `Executive Value Dashboard` (`viw6vmPXpT9CZJ94y`)
- `Agent Pipeline` (`viwnChS71bylZWixy`)

### Tasks

- `Delivery Control Tower` (`viwxdaY8PEdk1Rwg0`)
- `This Week Priorities` (`viwHqn4aEEB2DqdOG`)
- `Blocked Work` (`viwbbRVg4Lr8G2b67`)

### Approvals

- `Approval Queue` (`viw3YyBAiRXoyid43`)
- `Elevated Security Reviews` (`viwYsnOdcXFQBJv9P`)

### ROI / Risks / Integrations / Milestones

- `ROI Dashboard` (`viwlfg1ZHS7sTfxSR`)
- `Risk Watchlist` (`viwfeBqOFDKQHnTHV`)
- `Integration Readiness` (`viwbx6DLB9AaBPNCn`)
- `45-Day HITL Timeline` (`viwoapzbTOqBXAEWA`)

## Seeded Records

- Agent catalog record for `P1 Outlook Email Chief-of-Staff Agent`
- Initial task for Outlook permissions and reviewer roster
- Initial milestone for Day-45 HITL review
- Initial approval record for draft-only send control

## Current Constraints

- Some advanced field payloads returned Airtable validation errors when using richer options.
- Stable implementation path used: sequential field creation with core field types.
- Date values in template prefill were partially rejected; dates can be set directly in rows via UI if needed.
- Linked-record field creation via MCP returned `INVALID_REQUEST` in this base/profile.

## Relational Fallback Implemented

- Added `Agent Catalog Key` field in:
  - `Agent Catalog`
  - `Tasks`
  - `Milestones`
  - `Approvals`
  - `ROI Metrics`
  - `Risks`
  - `Integrations`

This allows immediate cross-table joins by shared key value while preserving progress.

## One-Click Manual Completion (Airtable UI)

To enable true linked records in the UI:

1. In each execution table (`Tasks`, `Milestones`, `Approvals`, `ROI Metrics`, `Risks`, `Integrations`), add a new field of type `Link to another record`.
2. Set the target table to `Agent Catalog`.
3. Name the field `Agent Link`.
4. Optionally migrate values from `Agent Catalog Key` and keep key fields as backup.

## Next Recommended Airtable Steps

1. Complete UI-linked record setup (`Agent Link`) using the 4-step guide above.
2. Add formula/rollup fields for executive scorecards (open tasks, pending approvals, ROI totals).
3. Add grouped views by `Status` and `Approval Level`.
4. Add monthly executive review view filters.
5. Add submission templates for new agent intake based on `AGENT_CARD_TEMPLATE.md`.
