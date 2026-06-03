# Strategic Roadmap

**Owner:** Windsurf (Architect)  
**Last Updated:** May 27, 2026  
**Purpose:** Prioritized plan for what to work on next, with Cursor-ready instruction packets

---

## Operating Model Reminder

- **Windsurf** writes specs and instructions in this folder
- **You** hand instruction packets to **Cursor** for execution
- **Cursor** reports back; **Windsurf** reviews and issues next instructions

---

## Phase 0: Migration (FIRST — Do This Before Anything Else)

**Goal:** Move all projects into the master folder with structured layout.

**Cursor workflow:** Open **CURSOR_INSTRUCTIONS_MIGRATION.md** and execute Sections 1–12 in order.

| Step | Section | Est. Time | Depends On |
| --- | --- | --- | --- |
| 0.1 | Create directory structure (Section 1) | 2 min | — |
| 0.2 | Migrate platforms (Section 2) | 10 min | 0.1 |
| 0.3 | Migrate agents (Section 3) | 10 min | 0.1 |
| 0.4 | Migrate bots (Section 4) | 5 min | 0.1 |
| 0.5 | Migrate tools (Section 5) | 10 min | 0.1 |
| 0.6 | Migrate content (Section 6) | 2 min | 0.1 |
| 0.7 | Migrate data (Section 7) | 2 min | 0.1 |
| 0.8 | Migrate SDM utilities (Section 8) | 5 min | 0.1 |
| 0.9 | Archive stale items (Section 9) | 5 min | 0.1 |
| 0.10 | Post-migration fixups (Section 10) | 15 min | 0.2–0.9 |
| 0.11 | Create master README (Section 11) | 5 min | 0.10 |
| 0.12 | Verify full migration (Section 12) | 5 min | 0.11 |

**After Phase 0:** Return to Windsurf for review before cleanup of originals.

---

## Phase 0.5: Cursor Builder Setup (Can Run in Parallel with Phase 0)

**Goal:** Configure Cursor as a fully equipped Builder IDE.

**Cursor workflow:** Open **CURSOR_SETUP_PLAN.md** and execute Parts 1–6 in order.

| Step | Part | Est. Time | Depends On |
| --- | --- | --- | --- |
| 0.5.1 | Port CodeGuard rules (Part 1A) | 20 min | — |
| 0.5.2 | Create Builder role rules (Part 1B) | 10 min | — |
| 0.5.3 | Install extensions (Part 3) | 10 min | — |
| 0.5.4 | Optimize settings (Part 4) | 5 min | — |
| 0.5.5 | Create MCP config + credentials (Part 2C) | 10 min | — |
| 0.5.6 | Verify existing MCP servers (Part 2A) | 15 min | 0.5.5 |
| 0.5.7 | Install new MCP servers (Part 2B) | 20 min | 0.5.5 |
| 0.5.8 | Configure AI models (Part 6) | 5 min | — |
| 0.5.9 | Run verification (Post-Setup) | 10 min | All above |

**After Phase 0.5:** Cursor is fully equipped. Custom MCP servers (Webex, Salesforce, ServiceNow) will be built in Phase 3.

---

## Phase 1: Consolidate & Refine (Post-Migration)

**Goal:** Merge overlapping projects within the new structure.

| Step | Instruction Packet | Est. Time | Depends On |
| --- | --- | --- | --- |
| 1.1 | STARTER-WORKBENCH-SPLIT (CONSOLIDATION_PLAN.md) | 15 min | Phase 0 |
| 1.2 | EMAIL-CONSOLIDATE (CONSOLIDATION_PLAN.md) | 30 min | Phase 0 |
| 1.3 | Security audit (rotate Airtable PAT, scan for secrets) | 15 min | Phase 0 |

**Note:** ARCHIVE-STALE, AGENT-EXTRACTION, and PLATFORM-CONSOLIDATE from the original plan are now handled by the migration itself.

**Cursor workflow:** Open CONSOLIDATION_PLAN.md, execute remaining packets. Use NEW paths under the master folder.

---

## Phase 2: Strengthen Core Assets (Weeks 1–2 of June)

**Goal:** Make the top 3 projects production-ready.

### 2.1 Helix / ServiceFlow SDM ✅ COMPLETE (May 26, 2026)

**Priority:** HIGH — this is your flagship

**Status:** Production-hardened via TASK-012 (audit), TASK-013 (P0+P1), TASK-014 (P2)

**Completed:**

- ✅ Backend: Real JWT auth with startup secret validation, rate limiting (10/15min auth, 100/15min writes), Zod validation on all write endpoints
- ✅ Frontend: 5 of 7 pages functional, builds clean (Dashboard placeholder documented)
- ✅ Mobile: Expo SDK 52, most screens API-driven, asset config cleaned (Expo defaults)
- ✅ Docker: Multi-stage production builds (backend + nginx frontend), compose uses .env, migration documented
- ✅ Docs: README current, CHANGELOG.md added with Phase 2.1 entries, legacy docs indexed
- ✅ Security: No hardcoded secrets, JWT guard, rate limits, input validation

**Deferred (P3 - not blockers):**

- Dashboard page wiring to live KPIs (currently placeholder)
- Mobile settings persistence (AsyncStorage)
- Docker build verification (requires Docker CLI)

**Audit findings:** Backend NEEDS-WORK → **PRODUCTION-READY** after P0+P1+P2 fixes. Mockup hub (19 HTML views) is primary UX, React SPA is optional shell.

### 2.2 MGM Status Bot + DD Status Bot

**Priority:** HIGH — these run daily in production

**Audit findings (TASK-011):**

- **mgm-status-bot:** BROKEN — 6 consecutive GHA failures (May 19–26), `WEBEX_BOT_TOKEN` returns 401
- **dd-status-bot:** BROKEN — Failed May 26, both access token and bot token returning 401
- **Root cause:** Expired Webex tokens in GitHub secrets (ops issue, not code)
- **Code/security:** Clean — no hardcoded tokens, proper env var usage, subscribers.json valid

**Required fixes (ops, not Cursor):**

1. Regenerate `WEBEX_BOT_TOKEN` at developer.webex.com → update GitHub secrets on both repos
2. Refresh `WEBEX_ACCESS_TOKEN` on dd-status-bot
3. Trigger `workflow_dispatch` to verify

**Deferred improvements:**

- Add `--dry-run` mode for local testing
- Update dd-status-bot GHA actions to v5/v6 (currently v4/v5 with Node 20 deprecation warnings)
- Fix `continue-on-error` masking analysis failures

### 2.3 Flerken (Post-Email Consolidation)

**Priority:** MEDIUM — after Phase 1 email consolidation

```text
CURSOR INSTRUCTION: FLERKEN-UPGRADE

TASK: Upgrade Flerken after email consolidation
LOCATION: ~/Desktop/Flerken - Personal AI Assistant/

STEPS:
1. Verify base functionality:
   - python run.py works with valid .env
   - Device-code auth flow completes
   - Digest generates and saves to out/

2. If email-summary-agent logic was merged (Phase 1):
   - Verify new modules integrate without errors
   - Add CLI flags for any new capabilities

3. Plan Phase 2 features from README:
   - Web dashboard for reviewing drafts
   - Calendar integration
   - Assess which is highest value and create a spec

REPORT BACK: Current working state + recommended next feature to build.
```

---

## AI Factory: Phase 0 — Foundation (Active — May 27, 2026)

**Goal:** Governance infrastructure, baseline measurement, integration readiness, and agent cards signed before any code is written.

**Status:** 🟡 Week 1 In Progress

### Week 1 Deliverables (2026-05-27) — ✅ Complete

| Artifact | Location | Status |
| --- | --- | --- |
| Agent Registry (34 agents) | `AI_FACTORY_AGENT_REGISTRY.md` | ✅ Done |
| Governance Log | `AI_FACTORY_GOVERNANCE_LOG.md` | ✅ Done |
| Cycle Time Baselines tracker | `AI_FACTORY_CYCLE_TIME_BASELINES.md` | ✅ Done |
| Integration Readiness matrix | `AI_FACTORY_INTEGRATION_READINESS.md` | ✅ Done |
| Agent Card: Delivery Tracker (T1) | `agents/delivery-tracker/AGENT_CARD.md` | ✅ Done |
| Agent Card: Risk Sentinel (T2) | `agents/risk-escalation-sentinel/AGENT_CARD.md` | ✅ Done |
| Agent Card: Business Review Generator (T2) | `agents/business-review-generator/AGENT_CARD.md` | ✅ Done |

### Remaining Phase 0 Actions (Ops — You Must Do These)

1. **👤 Rotate Webex bot token** — `WEBEX_BOT_TOKEN` is expired (also blocks Phase 2 bots). Update at developer.webex.com → GitHub secrets.
2. **👤 Confirm Salesforce MCP delegated read access** — needed before Business Review Generator HITL pilot.
3. **👤 Confirm ServiceNow MCP access** — needed before Risk Sentinel HITL pilot.
4. **👤 Fill in `AI_FACTORY_CYCLE_TIME_BASELINES.md`** — measure the 5 workflows over the next 2 weeks before Sprint 1 starts.

### Phase 0 Exit Gate (Day 21 target: ~2026-06-17)

- [ ] All 5 baselines measured (≥ 5 data points each)
- [ ] Webex token rotated
- [ ] Salesforce + ServiceNow access confirmed
- [ ] 3 agent cards reviewed and signed by domain expert
- [ ] Governance log entry written confirming Phase 0 complete

---

## Phase 3: Strategic Builds (June–July)

**Goal:** Build the next generation of SDM tools.

### 3.1 Delivery Workbench — Your Daily Driver

```text
CURSOR INSTRUCTION: WORKBENCH-BUILD-V2

TASK: Evolve delivery-workbench into the primary SDM daily-driver
LOCATION: ~/Desktop/delivery-workbench/

STEPS:
1. Implement agent orchestration layer:
   - Create orchestration/ directory with YAML-based workflows
   - Support: email-digest, status-report, communication-scan
   - Each workflow should call the appropriate agent (Flerken, status-report-agent, etc.)

2. Build morning briefing pipeline:
   - Sequence: fetch email → triage → fetch calendar → generate briefing
   - Output: Markdown + optional HTML email to self

3. Add Webex integration:
   - Pull unread DMs and space mentions
   - Classify as action-required vs FYI
   - Include in morning briefing

4. Security:
   - All secrets in .env only
   - No external API calls without explicit user approval
   - CodeGuard rules from AgenticStarterKit applied

CONSTRAINTS:
- Each feature should be independently testable
- Use existing agents as libraries, don't rebuild
- Document each workflow in orchestration/README.md
```

### 3.2 NetPilot — CCNA Automation App

```text
CURSOR INSTRUCTION: NETPILOT-CCNA-APP

TASK: Complete the CCNA Automation GitHub App
LOCATION: ~/Desktop/NetPilot/ccna_automation_github_app/

STEPS:
1. BACKEND (FastAPI):
   - Verify: cd backend && pip install -r requirements.txt && python -m app.main
   - Run tests: pytest tests/
   - Document API endpoints

2. FRONTEND (React):
   - Verify: cd frontend && npm install && npm run dev
   - Check all components render
   - Document which views are functional

3. DATA MODEL:
   - Review schema.sql and seed.json
   - Verify domain_map.yaml is complete

REPORT BACK: What's working, what needs building, recommended next sprint.
```

### 3.3 AI Factory — Add Interactive Workshop

```text
CURSOR INSTRUCTION: AI-FACTORY-WORKSHOP

TASK: Add an interactive workshop module to AI Factory
LOCATION: ~/Desktop/AI Factory/

STEPS:
1. Create workshop.html — a hands-on guided exercise page
2. Link from index.html alongside existing tutorials
3. Content: Walk through building a simple Webex notification bot
4. Style: Match existing Tailwind + Cisco brand theme
5. Include: Step-by-step code snippets, copy buttons, progress tracker

CONSTRAINTS:
- Static HTML only (no backend)
- Must work offline after initial load
- Match existing tutorial page quality
```

---

## Phase 4: Scale & Share (July+)

- Publish Helix to GitHub Pages for stakeholder demos
- Package AgenticStarterKit as a shareable template for other Cisco CX teams
- Build "Agent Marketplace" concept for NetPilot (architecture docs already exist)
- Evaluate Helix for real data integration (move from mock to live Salesforce/ServiceNow)

---

## Decision Log

| Date | Decision | Rationale |
| --- | --- | --- |
| 2026-05-26 | Windsurf = Architect, Cursor = Builder | Clear separation of design vs execution |
| 2026-05-26 | Flerken wins email consolidation | Most complete architecture |
| 2026-05-26 | serviceflow-sdm is canonical platform | Full-stack, Docker, mobile |
| 2026-05-26 | Keep AgenticStarterKit + delivery-workbench separate | Different audiences (template vs operational) |
| 2026-06-03 | Devin Desktop — no upgrade path | Evaluated and ruled out; governance gates limit parallelization value and cost does not justify capability at current scale; not to be reconsidered without explicit decision reversal |

---

## How to Use This Roadmap

1. **Pick a phase and step** from the table above
2. **Open the Cursor Instruction Packet** (the `text` code block)
3. **Paste it into Cursor** as your opening prompt
4. **Cursor executes** and reports back
5. **Return to Windsurf** — update this roadmap with results and get next instructions

---

*This roadmap is maintained by Windsurf (Architect). Updated after each phase completion.*
