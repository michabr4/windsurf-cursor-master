# AI Factory — Integration Readiness Matrix

> **Purpose:** Track authentication, access, and API readiness for every external integration  
> the AI Factory agents depend on. Must be complete before Phase 1 Week 5 gate.
>
> **Owner:** AI Factory architect  
> **Reference:** `AI_FACTORY_IMPLEMENTATION_PLAN.md` Section 5.5

---

## Integration Status Legend

| Symbol | Meaning |
| ------ | ------- |
| ✅ Ready | Token/credentials confirmed working in dev |
| 🟡 In Progress | Setup underway, not yet confirmed |
| 🔴 Blocked | Access or approval blocked |
| ⬜ Not Started | Not yet attempted |

---

## Integration Matrix

| Integration | Agents Using | Phase 1 Needed | Auth Method | Key Objects | Status | Owner | Notes |
| ----------- | ------------ | -------------- | ----------- | ----------- | ------ | ----- | ----- |
| Helix REST API | #1, #2, #3 + 7 others (10 total) | ✅ Yes | Bearer token (`HELIX_API_TOKEN`) | Cases, Milestones, SLA Records, Entitlements, Accounts | 🟡 In Progress | SDM lead | Delivery Tracker client built; bearer token needed per agent `.env` |
| Salesforce MCP | #3 + 5 others (6 total) | Stub only in Phase 1 | MCP token (`SALESFORCE_MCP_TOKEN`) | Cases, Accounts, Opportunities, CSAT | ⬜ Not Started | Ops | BRG uses empty stub when token unset — not blocking Phase 1 |
| Webex Bot API | #2, #3 + 6 others (8 total) | ✅ Yes | Bot token (`WEBEX_BOT_TOKEN`) | Messages, Adaptive Cards, Rooms | 🟡 In Progress | SDM lead | HITL cards required for Risk Sentinel (T2); token rotation per Phase 0 Section 5.3 |
| Outlook / Graph API | #5 + 7 others (8 total) | ❌ Not needed in Phase 1 | MSAL device code flow (`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`) | Mail.Read, Mail.Send, Calendars.Read | 🔴 Blocked | IT/Azure | Azure AD app registration required; Forge blocked until registered |
| ServiceNow | #3 + 3 others (4 total) | Stub only in Phase 1 | API key or OAuth | Incidents, Problems, Change Requests | ⬜ Not Started | Ops | Not required until Phase 2+ agents; BRG stub acceptable for Phase 1 |

---

## Phase 1 Blocking Integrations

The following must be resolved before Phase 1 Week 5 gate:

| Integration | Blocking What | Action Required | Target Date |
| ----------- | ------------- | --------------- | ----------- |
| Helix REST API | Delivery Tracker go-live | Provision `HELIX_API_TOKEN` for dev + test environments | Before Week 5 |
| Webex Bot API | Risk Sentinel HITL cards | Rotate bot token; confirm HITL card delivery to test room | Before Week 9 |

---

## Non-Blocking (Phase 2+) Integrations

| Integration | First Needed | Prerequisite |
| ----------- | ------------ | ------------ |
| Salesforce MCP | Phase 2 (proper) — stub used in Phase 1 BRG | Ops provisioning of MCP token |
| Outlook / Graph | Phase 2 — Proactive Outreach Drafter | Azure AD app registration |
| ServiceNow | Phase 2 — Cross-Functional Coordinator | ServiceNow instance access + API key |

---

## Webex Token Rotation Checklist (Phase 0 Section 5.3)

- [ ] Regenerate `WEBEX_BOT_TOKEN` at developer.webex.com
- [ ] Update token in all agent `.env` files (locally) and CI/CD secrets
- [ ] Refresh `WEBEX_ACCESS_TOKEN` for dd-status-bot (expires ~14 days from issue)
- [ ] Test adaptive card delivery to SDM Webex test room
- [ ] Confirm approve/dismiss button callbacks are reachable

---

## Azure AD App Registration Checklist (Phase 0 Section 5.4)

- [ ] Register app in Microsoft Entra admin center
- [ ] Request permissions: `Mail.Read`, `Mail.Send`, `User.Read`, `Calendars.Read`
- [ ] Save `AZURE_CLIENT_ID` and `AZURE_TENANT_ID` to `agents/forge/.env`
- [ ] Verify MSAL device code flow works end-to-end
- [ ] Document consent grant process for production

---

_Last updated: 2026-05-29 | Reference: `AI_FACTORY_IMPLEMENTATION_PLAN.md` Section 5.5_
