# Automation Backlog

> **Owner:** Windsurf (Architect)  
> **Last Updated:** May 27, 2026  
> **Purpose:** Master backlog of automation opportunities, prioritized by impact × ease of development, organized by customer and category.

---

## Priority Scoring Rubric

Priority is scored on **Impact × Ease**. Impact = business value, time savings, risk reduction. Ease = development complexity and dependency readiness.

| | **Easy** (≤1 wk) | **Medium** (1–3 wks) | **Complex** (3+ wks) |
|---|---|---|---|
| **High Impact** | 🔴 **P0** — Do now | 🟠 **P1** — Plan next | 🟡 **P2** — Schedule |
| **Medium Impact** | 🟠 **P1** — Plan next | 🟡 **P2** — Schedule | 🟢 **P3** — Backlog |
| **Low Impact** | 🟡 **P2** — Schedule | 🟢 **P3** — Backlog | 🟢 **P3** — Backlog |

---

## Category Taxonomy

| Code | Category | Description |
|------|----------|-------------|
| **A1** | Customer: MGM Resorts | Automations scoped to MGM Resorts engagement |
| **A2** | Customer: DD | Automations scoped to Digitized Delivery customer |
| **A3** | Customer: [Future] | Placeholder for new customer-specific work |
| **B1** | Platform: Delivery & PM | Cross-customer delivery tracking, plan management, risk |
| **B2** | Platform: Customer Health & Risk | Health scoring, proactive outreach, escalation |
| **B3** | Platform: Technical Delivery | Config acceleration, diagnostics, architecture |
| **B4** | Platform: Operations & SLA | SLA monitoring, resource optimization, ops reporting |
| **B5** | Platform: BI & Executive Reporting | QBR generation, executive reports, portfolio intelligence |
| **B6** | Platform: Orchestration Chains | Agent-of-agents end-to-end workflows |
| **C1** | Internal: Communications & Email | Email digest, Webex monitoring, personal productivity |
| **C2** | Internal: Daily Driver Tooling | Morning briefing, orchestration layer |
| **C3** | Internal: Network Automation | CCNA automation, NetPilot |
| **D1** | Infra: Integration Layer | MCP servers for Salesforce, ServiceNow, Webex, Outlook |
| **D2** | Infra: Platform Health | Monitoring, token rotation, bot health |
| **D3** | Infra: Governance & Compliance | Audit logs, HITL tracking, promotion gates |

---

## A1 — Customer: MGM Resorts

> **Reference Hub:** [MGM CX SharePoint Site](https://cisco.sharepoint.com/sites/CXMGM/SitePages/Home.aspx) — primary source for project docs, plans, stakeholder info, and workstream materials.

| # | Item | Category | Priority | Impact | Ease | Status | Linked Artifacts |
|---|------|----------|----------|--------|------|--------|-----------------|
| MGM-01 | **Fix Webex bot token** — Rotate expired `WEBEX_BOT_TOKEN`, restore live MGM bot delivery | A1, D2 | 🔴 P0 | High | Easy | ⚠️ Blocked (expired token) | `bots/mgm-status-bot/`, `ROADMAP.md §2.2` |
| MGM-02 | **Weekly Customer Status Report Agent** — AI-driven weekly report auto-generated from Webex space export + Helix data; structured output matching current manual report format | A1 | 🔴 P0 | High | Easy | ⬜ New — framework exists | `bots/mgm-status-bot/`, `sdm-files/MGM_Status_Report_20260410.md` |
| MGM-03 | **Firewall Migration Progress Tracker** — Automated daily tracking of Palo Alto → Cisco Firepower migration wave completion, milestone status, open action items; push to Webex | A1 | 🟠 P1 | High | Medium | ⬜ New — planning docs exist | `tools/firewall-implementation-planning/` |
| MGM-04 | **Firewall Config Generation Assistant** — AI-assisted translation of Palo Alto baseline configs to Cisco Firepower; outputs config templates for CE review (never applies autonomously) | A1 | 🟠 P1 | High | Medium | ⬜ New | `tools/firewall-implementation-planning/docs/`, `agents/config-accelerator/` (Phase 3) |
| MGM-05 | **ISE ISAAC Automation Expansion** — Automate cert renewal execution across all PSN nodes; extend to ISE Patch upgrade workflow; daily health check push | A1 | 🟡 P2 | Medium | Medium | ⬜ New — partial ISAAC work exists | `sdm-files/MGM_Status_Report_20260410.md §2` |
| MGM-06 | **LCS Syslog Alert Automation** — Daily automated PSIRT/syslog/field notice digest for MGM network estate; Webex push with severity classification | A1 | 🟡 P2 | Medium | Medium | ⬜ New | `sdm-files/MGM_Status_Report_20260410.md §3` |
| MGM-07 | **Migration Wave Execution Checklist Bot** — Tracks per-device, per-wave firewall migration checklist completion; alerts on blockers and percentage complete | A1 | 🟡 P2 | Medium | Complex | ⬜ New | `tools/firewall-implementation-planning/project/` |

### MGM Resorts — Notes

- **MGM-01 is an ops prerequisite** for MGM-02 and all Webex-push items. Do this first — 5 min token rotation.
- **MGM-02** builds on the `mgm-status-bot/webex_recordings.py` which already extracts Webex space data and the manual template in `MGM_Status_Report_20260410.md`. Add LLM pass for structured report generation.
- **MGM-03 / MGM-04** are directly tied to the active $10M Firepower migration deal. MGM-03 (tracker) is faster to ship; MGM-04 (config generation) is higher complexity but higher strategic value.

---

## A2 — Customer: DD (Digitized Delivery)

| # | Item | Category | Priority | Impact | Ease | Status | Linked Artifacts |
|---|------|----------|----------|--------|------|--------|-----------------|
| DD-01 | **Fix DD Status Bot token** — Rotate expired `WEBEX_BOT_TOKEN` + `WEBEX_ACCESS_TOKEN`; restore live DD bot delivery | A2, D2 | 🔴 P0 | High | Easy | ⚠️ Blocked (expired token) | `bots/dd-status-bot/`, `ROADMAP.md §2.2` |
| DD-02 | **Weekly DD Customer Status Report Agent** — Auto-generate weekly status report for DD account using same framework as MGM-02 | A2 | 🟠 P1 | High | Easy | ⬜ New — reuse MGM-02 framework | `bots/dd-status-bot/`, `data/digitized-delivery-ges/` |
| DD-03 | **GES Regional Parity Status Automation** — Automate tracking of SD-WAN CatC / GES regional parity across customer base; generate weekly summary dashboard | A2 | 🟡 P2 | Medium | Medium | ⬜ New | `data/digitized-delivery-ges/` |
| DD-04 | **Customer NaC Parity Tracking Agent** — Monitor parity database changes; flag new parity gaps; weekly digest push | A2 | 🟢 P3 | Low | Medium | ⬜ Backlog | `data/digitized-delivery-ges/Customer NaC Parity Database.xlsx` |

---

## B1 — Platform: Delivery & Project Management

*These are cross-customer agents in the AI Factory pipeline. See `AI_FACTORY_IMPLEMENTATION_PLAN.md` for full specs.*

| # | Item | AI Factory Agent | Priority | Phase | Status |
|---|------|-----------------|----------|-------|--------|
| B1-01 | **Delivery Tracker** — Daily automated pull of milestone/case/SLA status across all accounts | Agent #1 | 🔴 P0 | Phase 1 | 🟡 In Design |
| B1-02 | **Living Plan Agent** — Detects milestone slippages, recalculates completion dates | Agent #7 | 🟠 P1 | Phase 2 | ⬜ Planned |
| B1-03 | **Schedule Risk Predictor** — Predicts milestone slip probability from historical patterns | Agent #9 | 🟠 P1 | Phase 2 | ⬜ Planned |
| B1-04 | **Stakeholder Communicator** — Drafts executive + technical stakeholder updates from plan changes | Agent #8 | 🟡 P2 | Phase 2 | ⬜ Planned |
| B1-05 | **Lessons Learned Harvester** — Extracts reusable patterns at project close | Agent #10 | 🟡 P2 | Phase 2 | ⬜ Planned |

---

## B2 — Platform: Customer Health & Risk

| # | Item | AI Factory Agent | Priority | Phase | Status |
|---|------|-----------------|----------|-------|--------|
| B2-01 | **Risk & Escalation Sentinel** — Rule-based risk detection (SLA breach, health score drop, entitlement gap); HITL Webex cards | Agent #2 | 🔴 P0 | Phase 1 | 🟡 In Design |
| B2-02 | **Customer Health Pulse** — Composite health score from SLA, cases, engagement, milestones | Agent #4 | 🟠 P1 | Phase 2 | ⬜ Planned |
| B2-03 | **Proactive Outreach Drafter** — Drafts personalized customer outreach on health score drop | Agent #5 | 🟠 P1 | Phase 2 | ⬜ Planned |
| B2-04 | **Cross-Functional Coordinator** — Synthesizes CE/PM/CDA workstream status per account; flags gaps | Agent #6 | 🟡 P2 | Phase 2 | ⬜ Planned |
| B2-05 | **Service Gap Predictor** — Predicts delivery service gaps weeks ahead | Agent #24 | 🟡 P2 | Phase 4 | ⬜ Planned |

---

## B3 — Platform: Technical Delivery

| # | Item | AI Factory Agent | Priority | Phase | Status |
|---|------|-----------------|----------|-------|--------|
| B3-01 | **Config Accelerator** — AI-generates device config templates from validated design patterns + customer constraints | Agent #11 | 🟠 P1 | Phase 3 | ⬜ Planned |
| B3-02 | **Diagnostic Accelerator** — Classifies problems, surfaces probable causes + resolution steps from logs | Agent #12 | 🟠 P1 | Phase 3 | ⬜ Planned |
| B3-03 | **Architecture Pattern Matcher** — Matches requirements against proven design patterns | Agent #15 | 🟡 P2 | Phase 3 | ⬜ Planned |
| B3-04 | **Compatibility Validator** — Validates proposed BOM/design against Cisco compatibility matrix | Agent #16 | 🟡 P2 | Phase 3 | ⬜ Planned |
| B3-05 | **Engagement Context Keeper** — Maintains running technical narrative per account; generates CE handoff briefing | Agent #13 | 🟡 P2 | Phase 3 | ⬜ Planned |
| B3-06 | **Design Doc Generator** — Multi-pass LLM generation of HLD + LLD from matched pattern + validated BOM | Agent #17 | 🟢 P3 | Phase 3 | ⬜ Planned |

---

## B4 — Platform: Operations & SLA

| # | Item | AI Factory Agent | Priority | Phase | Status |
|---|------|-----------------|----------|-------|--------|
| B4-01 | **SLA Sentinel** — Real-time SLA monitoring with tiered alerts + draft escalations at 20%/10%/breach | Agent #19 | 🟠 P1 | Phase 4 | ⬜ Planned |
| B4-02 | **Entitlement Monitor** — Tracks contracted vs consumed; flags overrun and under-utilization risks | Agent #23 | 🟠 P1 | Phase 4 | ⬜ Planned |
| B4-03 | **Ops Status Generator** — Weekly auto-compiled operational report (exec/detailed/exception formats) | Agent #21 | 🟡 P2 | Phase 4 | ⬜ Planned |
| B4-04 | **Resource Optimizer** — Matches upcoming project demand to available CE/CDA/PM capacity | Agent #20 | 🟡 P2 | Phase 4 | ⬜ Planned |
| B4-05 | **Delivery Risk Radar** — Daily T1 scan for engagement risk patterns; feeds SLA Sentinel | Agent #22 | 🟡 P2 | Phase 4 | ⬜ Planned |
| B4-06 | **Financial Health Agent** — Monitors account P&L, margin, cost overruns, entitlement revenue forecast | Agent #26 | 🟢 P3 | Phase 4 | ⬜ Planned |

---

## B5 — Platform: Business Intelligence & Executive Reporting

| # | Item | AI Factory Agent | Priority | Phase | Status |
|---|------|-----------------|----------|-------|--------|
| B5-01 | **Business Review Generator** — Automated QBR draft from Salesforce + ServiceNow + Helix data; human reviews before delivery | Agent #3 | 🔴 P0 | Phase 1 | 🟡 In Design |
| B5-02 | **Delivery Comms Drafter** — Weekly + event-driven customer-facing status drafts (extends mgm-status-bot) | Agent #25 | 🟠 P1 | Phase 4 | ⬜ Planned |
| B5-03 | **Executive Report Generator** — Compiles all agent outputs into exec-ready weekly program report | Agent #29 | 🟡 P2 | Phase 5 | ⬜ Planned |
| B5-04 | **Portfolio Impact Measurer** — Continuously tracks cycle-time reductions, FTE hour savings per agent | Agent #30 | 🟢 P3 | Phase 5 | ⬜ Planned |

---

## B6 — Platform: Orchestration Chains

| # | Chain | Agents Involved | Priority | Phase | Status |
|---|-------|-----------------|----------|-------|--------|
| B6-01 | **Account Risk-to-Action** — Health Pulse → Risk Sentinel → Outreach Drafter | #4, #2, #5 | 🟠 P1 | Phase 6 | ⬜ Planned |
| B6-02 | **QBR Factory** — Delivery Tracker → Entitlement Monitor → Business Review Generator | #1, #23, #3 | 🟠 P1 | Phase 6 | ⬜ Planned |
| B6-03 | **Project Delivery Loop** — Living Plan → Schedule Risk Predictor → Stakeholder Communicator | #7, #9, #8 | 🟡 P2 | Phase 6 | ⬜ Planned |
| B6-04 | **Technical Delivery Accelerator** — Pattern Matcher → Compatibility Validator → Design Doc → Config Accelerator | #15, #16, #17, #11 | 🟡 P2 | Phase 6 | ⬜ Planned |
| B6-05 | **Operations Intelligence Loop** — Delivery Risk Radar → SLA Sentinel → Resource Optimizer | #22, #19, #20 | 🟢 P3 | Phase 6 | ⬜ Planned |

---

## C1 — Internal: Communications & Email

| # | Item | Priority | Impact | Ease | Status | Linked Artifacts |
|---|------|----------|--------|------|--------|-----------------|
| C1-01 | **Flerken Email Digest** — Daily AI-powered email triage and digest; unblocked after Azure AD registration | 🟠 P1 | High | Medium | 🔒 Blocked (Azure AD) | `agents/flerken/` |
| C1-02 | **Webex Unread Monitor** — Pull unread DMs/mentions, classify action-required vs FYI, include in morning briefing | 🟡 P2 | Medium | Medium | ⬜ Planned | `agents/communication-agent/` |

---

## C2 — Internal: Daily Driver Tooling

| # | Item | Priority | Impact | Ease | Status | Linked Artifacts |
|---|------|----------|--------|------|--------|-----------------|
| C2-01 | **Morning Briefing Pipeline** — Sequence: fetch email → triage → calendar → Webex mentions → briefing doc | 🟡 P2 | High | Complex | ⬜ Planned | `tools/delivery-workbench/` |
| C2-02 | **Agent Orchestration Layer** — YAML-based workflow engine for all agents in Delivery Workbench | 🟡 P2 | High | Complex | ⬜ Planned | `tools/delivery-workbench/orchestration/` |

---

## C3 — Internal: Network Automation

| # | Item | Priority | Impact | Ease | Status | Linked Artifacts |
|---|------|----------|--------|------|--------|-----------------|
| C3-01 | **NetPilot CCNA App** — Complete FastAPI backend + React frontend for CCNA automation | 🟡 P2 | Medium | Complex | ⬜ In progress | `tools/netpilot/` |
| C3-02 | **NetPilot Agent Marketplace** — Architecture for multi-agent network automation marketplace | 🟢 P3 | Medium | Complex | ⬜ Architecture only | `tools/netpilot/` |

---

## D1 — Infrastructure: Integration Layer (MCP Servers)

| # | Item | Priority | Required By | Status |
|---|------|----------|-------------|--------|
| D1-01 | **Salesforce MCP Server** — Delegated read access for Cases, Accounts, CSAT, Opportunities | 🟠 P1 | Agents #2, #3, #4, #5, #15 | ⚠️ Needs confirmation |
| D1-02 | **ServiceNow MCP Server** — API key for Incidents, Problems, Change Requests | 🟠 P1 | Agents #2, #3, #12, #19 | ⚠️ Needs confirmation |
| D1-03 | **Webex HITL Card Infrastructure** — Interactive approve/dismiss card template for all T2 agents | 🟠 P1 | All T2 agents | ⬜ Planned |
| D1-04 | **Azure AD App Registration** — MSAL device code flow for Outlook/Graph (email + calendar) | 🟠 P1 | Flerken, 8 agents | 🔒 Blocked |
| D1-05 | **Helix API Client Library** — Shared connector for 10 agents; exists in delivery-workbench | 🔴 P0 | Agents #1–3 | ✅ Exists — extend |

---

## D2 — Infrastructure: Platform Health & Token Management

| # | Item | Priority | Impact | Ease | Status |
|---|------|----------|--------|------|--------|
| D2-01 | **Webex Token Rotation** — Rotate `WEBEX_BOT_TOKEN` (MGM bot) + `WEBEX_ACCESS_TOKEN` (DD bot); update GitHub secrets | 🔴 P0 | High | Easy | ⚠️ Required now |
| D2-02 | **Token Expiry Monitor** — Automated alert 30 days before any Webex/API token expires | 🟡 P2 | Medium | Easy | ⬜ Planned |
| D2-03 | **Bot Health Checker** — Daily GHA step that validates bot tokens are returning 200 before sending reports | 🟡 P2 | Medium | Easy | ⬜ Planned |

---

## Prioritized Quick Wins (P0 Items — Do These First)

| # | Item | Est. Dev Time | Blocker? | Owner |
|---|------|---------------|----------|-------|
| 1 | **D2-01 / MGM-01 / DD-01** — Rotate all expired Webex tokens | 15 min (ops) | ✅ None | You (ops task) |
| 2 | **MGM-02** — Weekly MGM Status Report Agent (LLM layer on existing bot + Webex data) | ~1 week | MGM-01 first | Cursor |
| 3 | **B1-01** — Delivery Tracker (AI Factory Phase 1) | 4 weeks | Helix API ready ✅ | Cursor |
| 4 | **B2-01** — Risk & Escalation Sentinel (AI Factory Phase 1) | 4 weeks | Delivery Tracker first | Cursor |
| 5 | **B5-01** — Business Review Generator (AI Factory Phase 1) | 4 weeks | Salesforce MCP needed | Cursor |
| 6 | **D1-05** — Extend Helix API client library for agents | 3 days | None | Cursor |

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-27 | MGM-01 (token fix) is prerequisite for all MGM Webex-push items | Cannot test or use any bot-based delivery without a live token |
| 2026-05-27 | MGM-02 scoped as LLM layer on existing `mgm-status-bot` framework | Avoid rebuilding what works; add intelligence on top |
| 2026-05-27 | MGM-03 (migration tracker) prioritized P1 over MGM-04 (config gen) | Tracker is lower risk and faster to ship; config gen has CE safety gate complexity |
| 2026-05-27 | Firewall automation items (MGM-03/04) kept separate from AI Factory agents | Customer-specific scope; may feed into Config Accelerator (Phase 3) later |
| 2026-05-27 | DD items follow MGM template after MGM-02 is stable | Reuse same framework; don't parallelize before first version is validated |
| 2026-05-27 | B3/B4/B5/B6 items preserved from AI Factory plan, not duplicated | `AI_FACTORY_IMPLEMENTATION_PLAN.md` remains source of truth for those |

---

## Open Questions (Resolve Before Building)

| # | Question | Blocks | Target |
|---|----------|--------|--------|
| Q1 | What Webex spaces should MGM-02 pull from? (Beyond the 3 shown in MGM_Status_Report) | MGM-02 | Before sprint |
| Q2 | Should MGM-02 push report to specific Webex space or email or both? | MGM-02 | Before sprint |
| Q3 | What is the Firepower migration wave structure / total device count? | MGM-03, MGM-04 | Before P1 sprint |
| Q4 | Is Salesforce MCP delegated access confirmed for use? | B5-01, D1-01 | Phase 0 exit gate |
| Q5 | What is the DD customer's equivalent of the Webex space export for status reports? | DD-02 | Before DD sprint |

---

*Maintained by Windsurf (Architect). Reference: `AI_FACTORY_AGENT_REGISTRY.md`, `AI_FACTORY_IMPLEMENTATION_PLAN.md`, `ROADMAP.md`*  
*Last updated: 2026-05-27*
