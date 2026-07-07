# AI Factory — Integration Readiness Matrix

> **Purpose:** Track authentication, access, and readiness status for every system the AI Factory agents need to call.  
> **Gate:** All Phase 1 agents require their listed integrations to be in ✅ Ready before HITL pilot starts.  
> **Maintained by:** Windsurf (Architect). Ops actions flagged with 👤.

---

## Integration Status

| Integration | Auth Method | Current Status | Scope Needed | Phase 1 Required | Owner | Notes |
|-------------|------------|----------------|-------------|------------------|-------|-------|
| Helix / ServiceFlow REST API | Bearer token (`.env`) | ✅ Ready | Read: accounts, cases, milestones | Yes (T1 read) | Dev | Already used in delivery-workbench |
| Salesforce MCP | OAuth 2.0 / MCP server | 🟡 MCP exists, access TBC | Read: CRM accounts, entitlements, health | Yes (T1 read) | 👤 Ops | Confirm delegated read permissions |
| ServiceNow MCP | OAuth 2.0 / MCP server | 🟡 MCP exists, access TBC | Read: cases, SLAs, incidents | Yes (T1 read) | 👤 Ops | Confirm ServiceNow instance URL + credentials |
| Webex MCP / Bot | Bot token (`.env`) | ✅ Ready | Post messages, DM, SpaceLift read | Yes (T2 notifications) | Dev | Rotated 2026-05-28: WEBEX_BOT_TOKEN + WEBEX_ACCESS_TOKEN + WEBEX_REFRESH_TOKEN all set |
| Outlook / MS Graph API | Azure AD OAuth 2.0 | 🔴 Not registered | Read: calendar, email drafting | Phase 2 | 👤 Ops/IT | Register Azure AD app, configure delegated perms |
| Airtable | API key (`.env`) | ✅ Ready (MCP + direct) | Read/Write: agent registry, tracking | Yes (agent registry) | Dev | airtable-user-mcp available |

---

## Readiness Criteria per Integration

### ✅ Ready
- Credentials in `.env` (not hardcoded)
- At least one successful API test call documented
- Scope confirmed (what the agent can read/write)
- No open security/access blockers

### 🟡 In Progress
- MCP or API client exists but access not yet confirmed
- Permissions/scope not fully validated
- Needs a test call to confirm

### ⚠️ Action Required
- Known issue (e.g., token expiry)
- Specific ops action needed before integration can be used

### 🔴 Not Started
- No credentials or app registration yet
- Needs ops/IT action to initiate

---

## Action Items (Ops — Human-Required)

| Priority | Action | Integration | Who | Due |
|----------|--------|------------|-----|-----|
| ✅ Done | Rotate Webex bot token | Webex MCP | 👤 You | Completed 2026-05-28 |
| 🟡 P2 | Confirm Salesforce delegated read access | Salesforce MCP | 👤 Ops/Admin | Before Phase 1 HITL start |
| 🟡 P2 | Confirm ServiceNow instance URL + read credentials | ServiceNow MCP | 👤 Ops/Admin | Before Phase 1 HITL start |
| ⬜ P3 | Register Azure AD app for Graph API | Outlook/Graph | 👤 IT | Before Phase 2 |
| ⬜ P3 | Configure Calendar + Mail.ReadWrite delegated perms | Outlook/Graph | 👤 IT | Before Phase 2 |

---

## Integration Test Checklist (Dev Tasks)

Run these once Ops confirms access is ready.

### Helix REST API

- [ ] `GET /accounts` — returns account list
- [ ] `GET /accounts/{id}/cases` — returns cases with status
- [ ] `GET /accounts/{id}/milestones` — returns milestone dates

### Salesforce MCP

- [ ] List accounts query succeeds
- [ ] Account health score field accessible
- [ ] Entitlement records readable

### ServiceNow MCP

- [ ] List open cases query succeeds
- [ ] SLA breach flag field accessible
- [ ] Incident priority field readable

### Webex MCP

- [ ] Send DM to test user succeeds
- [ ] Post to test room succeeds
- [ ] Bot identity confirmed in Webex Developer portal

### Airtable

- [ ] Read from `AI_FACTORY_AGENT_REGISTRY` base
- [ ] Write test record to governance log base
- [ ] airtable-user-mcp confirmed working

---

## Security Notes

- All credentials must be stored in `.env` only — never in code or this document
- Webex bot tokens: rotate every 90 days minimum; log rotation date in governance log
- Azure AD app: use delegated permissions (user-level scope), not application-level, for Outlook access
- MCP servers: confirm each MCP server is running with scoped read permissions before connecting agents

---

*Last updated: 2026-05-28 | Reference: `AI_FACTORY_IMPLEMENTATION_PLAN.md` Section 13*
