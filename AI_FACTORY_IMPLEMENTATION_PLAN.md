# AI Factory — Master Implementation Plan

> **Version:** 1.0 | **Created:** May 27, 2026  
> **Scope:** 32 agents across 8 CX roles — Cisco CX "People AI Factory"  
> **Source framework:** `content/ai-factory/js/data.js`

---

## 1. Executive Summary

### What Gets Built

| Phase | Timeline | Agents | Key Outcome |
|-------|----------|--------|-------------|
| **0 — Foundation** | Weeks 1–4 | 0 | Standards, infra, baselines, governance |
| **1 — SDM Pilots** | Weeks 5–12 | 3 | Proof of model |
| **2 — CXM + PM** | Months 4–6 | 7 | Customer health, plan management |
| **3 — CE + CDA** | Months 7–9 | 8 | Config, diagnostics, architecture |
| **4 — HTOM + SDM** | Months 10–12 | 8 | SLA, resource, entitlement |
| **5 — CPM + CXL** | Year 2 Q1 | 8 | Program intelligence, executive reporting |
| **6 — Orchestration** | Year 2 Q2+ | Chains | Agent-of-agents end-to-end workflows |

**End state:** 32 agents, 8 roles transformed, 40–80% cycle-time reduction per workflow.

---

## 2. Existing Assets

### Platforms (Production-Ready — Extend, Don't Replace)

| Asset | Location | AI Factory Role |
|-------|----------|-----------------|
| Helix / ServiceFlow SDM | `platforms/serviceflow-sdm/` | Core data platform for all agents |
| Delivery Workbench | `tools/delivery-workbench/` | Orchestration layer (YAML workflows, agent bridge) |
| Agentic Starter Kit | `tools/agentic-starter-kit/` | Standards: CodeGuard, agent card template, guardrails |

### Existing Agents (Extend, Don't Rebuild)

| Agent | Location | Status | Maps To |
|-------|----------|--------|---------|
| Flerken | `agents/flerken/` | 🔒 Blocked (Azure AD) | CXM: Proactive Outreach Drafter |
| Communication Agent | `agents/communication-agent/` | ⚠️ Token expired | CE: Context Keeper |
| Status Report Agent | `agents/status-report-agent/` | ✅ Working | SDM: Delivery Comms Drafter |
| MGM/DD Status Bots | `bots/` | ⚠️ Token expired | SDM: Delivery Tracker baseline |

### Design Documents (Read Before Building)

| Document | Key Content |
|----------|-------------|
| `content/ai-factory/js/data.js` | All 8 roles, 32 agents: KPIs, pain points, agent descriptions |
| `sdm-files/sdm-agentic-framework/docs/SDM_AGENT_ANALYSIS.md` | 10 SDM agents with priority matrix |
| `tools/agentic-starter-kit/docs/AGENT_FACTORY_REQUIREMENTS.md` | FR1–FR8, three-tier trust model |
| `tools/agentic-starter-kit/docs/templates/AGENT_CARD_TEMPLATE.md` | Agent spec template |

---

## 3. Implementation Philosophy

1. **Audit before you build** — Measure current cycle time. No baseline = no ROI proof.
2. **Draft-first** — Every agent starts in read/draft mode. 45-day HITL before autonomous action.
3. **Extend what exists** — Helix, Delivery Workbench, existing agents are the foundation.
4. **One chain, one measurable outcome** — Every agent chain = one cycle-time metric.
5. **Security inherits the highest tier** — Chain's trust tier = highest tier of any member.

### Three-Tier Trust Model

| Tier | Actions | Approval | When |
|------|---------|----------|------|
| **T1** | Read, fetch, summarize, display | Domain owner (standard) | Day 0 |
| **T2** | Draft + HITL gate — human approves before external action | Security + business owner | After agent card sign-off |
| **T3** | Autonomous — send, write, trigger | Security/GRC + 45-day HITL evidence | After governance gate |

---

## 4. Technology Stack

| Layer | Decision | Rationale |
|-------|----------|-----------|
| Agent runtime | Python 3.11+ | Matches flerken, comm-agent pattern |
| LLM | LiteLLM (Ollama local / hosted via env) | Flexible, no hardcoded endpoints |
| Orchestration | Delivery Workbench YAML + agent_bridge.py | Already built |
| API | FastAPI per agent service | Consistent with NetPilot pattern |
| Data | PostgreSQL (Helix) + Airtable + `data/runs/` | Existing data layer |
| Communication | Webex + Outlook/Graph (Flerken) | Existing patterns |
| Deployment | Docker multi-stage + GitHub Actions | Helix production pattern |
| Secrets | `.env` per agent, gitignored | CodeGuard: no hardcoded credentials |

### Standard Agent Directory Structure
```
agents/<agent-name>/
├── src/
│   ├── main.py        # CLI entry: --dry-run, --account, --date
│   ├── config.py      # python-dotenv env loading
│   ├── agent.py       # Core orchestration logic
│   ├── tools/         # One file per integration
│   └── prompts/       # LLM prompt templates (.md)
├── tests/
├── .env.example
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 5. Phase 0 — Foundation (Weeks 1–4)

### 5.1 Finalize Agent Card Template
Every agent needs a completed card before development. Required fields:
- Role alignment | Trust tier | Maturity target
- Trigger | Inputs | Processing steps | Outputs
- Human gate | Integrations | Baseline metric | Target metric
- Security approval tier | Escalation path

**Action:** Review `tools/agentic-starter-kit/docs/templates/AGENT_CARD_TEMPLATE.md`

### 5.2 Measure Baselines (5 SDM Workflows)
Track manually for 2 weeks before first agent:

| Workflow | Measure |
|----------|---------|
| Weekly status report | Hours per report |
| Risk identification | Days from risk emergence to detection |
| QBR prep | Hours per QBR |
| Entitlement tracking | How often under/overrun found late |
| Customer comms draft | Minutes per communication |

**File:** `tools/delivery-workbench/data/baselines/CYCLE_TIME_BASELINES.md`

### 5.3 Rotate Webex Tokens (Ops — no code)
1. Regenerate `WEBEX_BOT_TOKEN` at developer.webex.com
2. Update GitHub secrets on both bot repos
3. Refresh `WEBEX_ACCESS_TOKEN` (dd-status-bot)
4. Build Webex interactive card template (approve/dismiss) for HITL use

### 5.4 Register Azure AD App (Ops — no code)
1. Register in Microsoft Entra admin center
2. Permissions: `Mail.Read`, `Mail.Send`, `User.Read`, `Calendars.Read`
3. Save `AZURE_CLIENT_ID` + `AZURE_TENANT_ID` to `agents/flerken/.env`
4. Verify MSAL device code flow

### 5.5 Integration Scaffold

| Integration | Agents Using | Action |
|-------------|-------------|--------|
| Salesforce | 6 agents | Map: Cases, Accounts, Opportunities, CSAT |
| ServiceNow | 4 agents | Map: Incidents, Problems, Change Requests |
| Webex | 8 agents | Fix tokens, test HITL card delivery |
| Outlook/Graph | 8 agents | Azure AD → test MSAL flow |
| Helix REST API | 10 agents | Document all endpoints agents will use |

**Deliverable:** `tools/agentic-starter-kit/docs/INTEGRATION_READINESS.md`

### 5.6 Initialize Governance
- Create `AI_FACTORY_AGENT_REGISTRY.md` (all 32 agents, phase, status, location)
- Create `AI_FACTORY_GOVERNANCE_LOG.md` (HITL decisions, tier promotions, go/no-go gates)
- Phase gate criteria: previous phase stable + KPI targets met → proceed

### Phase 0 Exit Criteria
- [ ] Agent card template finalized
- [ ] Baselines documented (5 workflows, 2-week data)
- [ ] Webex tokens rotated and HITL card tested
- [ ] Azure AD registered or timeline confirmed
- [ ] Integration readiness matrix complete
- [ ] Agent registry + governance log initialized

---

## 6. Phase 1 — SDM Pilot Wave (Weeks 5–12)

**Why SDM first:** Helix is production-ready, SDM analysis pre-exists (`SDM_AGENT_ANALYSIS.md`), status bots provide communication pattern.

### Pilot Agents

| # | Agent | T-Tier | KPI Target |
|---|-------|--------|------------|
| 1 | Delivery Tracker | T1 | 2–3 hr weekly check → 5 min review |
| 2 | Risk & Escalation Sentinel | T2 | Reactive → 5–10 days predictive |
| 3 | Business Review Generator | T2 | 8–12 hr QBR prep → 30 min review |

---

### Agent 1: Delivery Tracker
**Location:** `agents/delivery-tracker/` | **Trigger:** Daily 7am

**Inputs:** Helix API (milestones, entitlements) + Salesforce (cases) + ServiceNow (incidents)

**Processing:**
1. Authenticate to Helix via service JWT
2. Fetch all active accounts + delivery state
3. Per account: open cases, milestone status, entitlement balance
4. Calculate health score: `(on_time_milestones / total) × (days_to_breach > 5 ? 1.0 : 0.5)`
5. Rank by health score (lowest = highest risk)
6. Emit: `data/runs/delivery-tracker/YYYY-MM-DD.md` + `.json` (consumed by downstream agents)
7. Push Webex summary card (informational, T1 — no approval needed)

**Sprint plan:**
```
Week 5: Agent card + scaffold + Helix API client
Week 6: Health scoring + report generation
Week 7: Webex card + cron scheduling + tests
Week 8: Live pilot, monitor, tune thresholds
```

---

### Agent 2: Risk & Escalation Sentinel
**Location:** `agents/risk-escalation-sentinel/` | **Trigger:** Daily 8am (after Delivery Tracker)

**Risk rules:**
```
P1/P2 open > 48h                         → HIGH
SLA breach predicted within 5 days       → HIGH
Health score dropped > 15 pts in 7 days  → HIGH
Milestone slipped > 2 weeks              → MEDIUM
Entitlement < 20% with renewal < 60 days → MEDIUM
```

**Processing:**
1. Load Delivery Tracker JSON
2. Apply risk rules per account, compute tier (HIGH/MEDIUM/LOW)
3. For HIGH/MEDIUM: LLM generates risk summary + recommended action
4. Save: `data/runs/risk-sentinel/YYYY-MM-DD.json`
5. Push Webex interactive card per HIGH risk with buttons:
   - [Escalate Now] → generates draft escalation (human sends)
   - [Schedule Call] → generates draft calendar invite language
   - [Snooze 48h] → defers with reason logging
   - [Dismiss] → logs decision + reason

**HITL window:** 45 days logged. Track: cards sent, decisions, dismiss reasons, false positive rate.  
**Promotion gate:** false positive rate < 20%, SDM satisfaction confirmed → T3 eligible for defined patterns.

---

### Agent 3: Business Review Generator
**Location:** `agents/business-review-generator/` | **Trigger:** On-demand CLI

```bash
python run.py --account "Acme Corp" --quarter Q2-2026 [--format pptx]
```

**Processing:**
1. Pull period data: Salesforce (cases, CSAT), ServiceNow (incidents), Delivery Tracker (milestones), Helix (entitlements)
2. Compute metrics: case velocity, SLA compliance %, milestone on-time %, utilization %
3. Four LLM passes (chain-of-thought, grounded in data):
   - Executive summary (3–5 sentences, business language)
   - Delivery performance narrative
   - Risk & issues section
   - Next quarter priorities + recommendations
4. Populate `templates/business-review-template.md`
5. Save draft: `data/runs/business-review/YYYY-MM-DD-{account}.md`
6. Webex notification: "Draft QBR for [Account] ready — ~30 min review"

**Human gate:** SDM reviews all sections, edits relationship context, delivers to customer. Agent never sends autonomously.

**Quality check:** Every LLM-generated metric is validated against source data before inclusion. No hallucinated numbers.

### Phase 1 Governance Timeline

| Week | Gate |
|------|------|
| 5 | Agent cards signed by domain owners |
| 8 | Delivery Tracker live, 100% portfolio |
| 9 | Risk Sentinel HITL window opens |
| 10 | QBR Generator HITL window opens |
| 16–17 | 45-day windows close |
| 18 | **Governance review: T3 promotion decisions** |

### Phase 1 Exit Criteria
- [ ] Delivery Tracker: stable 4 weeks, 100% portfolio coverage daily
- [ ] Risk Sentinel: 45-day log complete, false positive < 20%
- [ ] QBR Generator: ≥ 3 real QBRs delivered to customers
- [ ] All 3 cycle-time targets met or exceeded
- [ ] Governance review logged in `AI_FACTORY_GOVERNANCE_LOG.md`

---

## 7. Phase 2 — CXM + PM Layer (Months 4–6)

**Prerequisites:** Phase 1 stable, Webex active, Azure AD registered

### Agents (7)

| # | Agent | Role | T-Tier | Key Dependency |
|---|-------|------|--------|----------------|
| 4 | Customer Health Pulse | CXM | T1 | Delivery Tracker + Salesforce |
| 5 | Proactive Outreach Drafter | CXM | T2 | Health Pulse + Flerken |
| 6 | Cross-Functional Coordinator | CXM | T1 | Helix API multi-lane |
| 7 | Living Plan Agent | PM | T2 | Helix milestones |
| 8 | Stakeholder Communicator | PM | T2 | Living Plan output |
| 9 | Schedule Risk Predictor | PM | T1→T2 | Historical Helix data |
| 10 | Lessons Learned Harvester | PM | T1 | Project close events |

### Agent 4: Customer Health Pulse
**Location:** `agents/customer-health-pulse/` | **Trigger:** Daily (after Delivery Tracker)

**Health score formula:**
```
Score = 0.25×(sla_compliance_pct)
      + 0.20×(case_trend: improving=1.0, steady=0.7, worsening=0.3)
      + 0.20×(engagement_recency: <7d=1.0, 7-14d=0.7, >14d=0.3)
      + 0.20×(milestone_performance from Delivery Tracker)
      + 0.15×(renewal_risk: >180d=1.0, 90-180d=0.8, <90d+risk=0.4)
```
Status: GREEN (80+), YELLOW (60–79), RED (<60)  
Triggers Proactive Outreach Drafter when score drops > 10 pts.  
**KPI:** Proactive/reactive ratio: 20/80 → 70/30

### Agent 5: Proactive Outreach Drafter
**Location:** `agents/proactive-outreach-drafter/` | **Trigger:** Event (Health Pulse score drop)

Trigger conditions: score drop > 10 pts, score < 60, or renewal < 90d with score < 80.

Processing: pull account context + last 3 emails (Flerken) → LLM generates personalized outreach referencing specific milestone, acknowledging open issues, with clear ask.

**Human gate:** Webex card [Send as-is] [Edit then send] [Dismiss] — agent never sends autonomously.

### Agent 6: Cross-Functional Coordinator
**Location:** `agents/cross-functional-coordinator/` | **Trigger:** Daily | **T1**

Synthesizes CE, PM, CDA workstream status per account. Flags gaps: CE work with no linked PM milestone, CDA design pending CE start, commitments with no resource assigned.

### Agent 7: Living Plan Agent
**Location:** `agents/living-plan-agent/` | **Trigger:** Daily | **T2**

Pulls Helix milestone/task status, compares to plan, detects slippages (>3 days late), recalculates completion dates via rolling velocity.

Human gate: PM reviews daily diff → approves updated dates → approved plan consumed by Stakeholder Communicator.

### Agent 8: Stakeholder Communicator
**Location:** `agents/stakeholder-communicator/` | **Trigger:** After Living Plan approval or weekly | **T2**

Two-pass LLM: executive version (3–5 bullets, business impact) + technical version (milestone dates, risk details).  
Human gate: PM reviews both drafts before delivering to stakeholders.

### Agent 9: Schedule Risk Predictor
**Location:** `agents/schedule-risk-predictor/` | **Trigger:** Daily | **T1 → T2 after 30-day validation**

Analyzes 12+ months of historical Helix delivery data. Flags milestones with >30% slip probability based on team velocity, technology complexity, and dependency count. Starts as T1 analysis, upgrades to T2 HITL recommendations once accuracy validated.

### Agent 10: Lessons Learned Harvester
**Location:** `agents/lessons-learned-harvester/` | **Trigger:** Project close event | **T1**

LLM extracts: what worked, what failed, customer preferences, reusable technical patterns.  
Saves to `data/knowledge-base/lessons/` indexed by technology, vertical, project type.  
Powers Config Accelerator and Architecture Pattern Matcher in Phase 3.

---

## 8. Phase 3 — CE + CDA Technical Layer (Months 7–9)

### Agents (8)

| # | Agent | Role | T-Tier |
|---|-------|------|--------|
| 11 | Config Accelerator | CE | T2 |
| 12 | Diagnostic Accelerator | CE | T2 |
| 13 | Engagement Context Keeper | CE | T1 |
| 14 | Implementation Pattern Miner | CE | T1 |
| 15 | Architecture Pattern Matcher | CDA | T1 |
| 16 | Compatibility Validator | CDA | T1 |
| 17 | Design Doc Generator | CDA | T2 |
| 18 | Product Intelligence Feed | CDA | T1 |

### Agent 11: Config Accelerator
**Trigger:** On-demand `python run.py --device ISR4451 --use-case "WAN segmentation"`

Pulls Cisco validated design patterns from knowledge base + customer constraints from Salesforce → LLM generates config template → validates against known IOS version syntax rules → CE reviews before applying.

**Human gate:** CE reviews, tests in lab, applies to production. Never autonomous.  
**KPI:** Routine config time: hours → minutes

### Agent 12: Diagnostic Accelerator
**Trigger:** On-demand (input: log files, show output, symptom description)

Classifies problem domain → searches knowledge base for similar symptoms → LLM generates ranked probable causes + diagnostic commands + resolution steps. Cross-references Cisco Bug Search Tool patterns.

**Human gate:** CE runs diagnostic steps, applies resolution.  
**KPI:** Troubleshooting: from scratch → contextual head start

### Agent 13: Engagement Context Keeper
**Trigger:** New CE assigned to account, or engagement close | **T1**

Maintains running technical narrative: config decisions + rationale, issues resolved, customer preferences. On new CE assignment: generates briefing doc. On close: feeds Lessons Learned Harvester.

### Agent 14: Implementation Pattern Miner
**Trigger:** Weekly batch | **T1**

Scans completed engagement data. Extracts reusable patterns and successful config templates. Feeds `data/knowledge-base/patterns/` used by Config Accelerator and Architecture Pattern Matcher.

### Agent 15: Architecture Pattern Matcher
**Trigger:** On-demand | **T1**

Matches customer requirements against proven designs in knowledge base. Returns top 3 matching patterns with fit score, gaps, and adaptation notes.

### Agent 16: Compatibility Validator
**Trigger:** On-demand (input: proposed BOM or design doc) | **T1**

Checks proposed hardware/software versions against Cisco compatibility matrix. Flags incompatibilities, EOL risks, known bugs. Output: validation report (BLOCK / WARN / INFO severity).  
**KPI:** Design rework rate: 30% → < 10%

### Agent 17: Design Doc Generator
**Trigger:** After Pattern Matcher + Compatibility Validator complete | **T2**

Multi-pass LLM generates HLD + LLD from matched pattern, validated BOM, and customer context.  
**Human gate:** CDA reviews all technical content before customer delivery.  
**KPI:** Architecture design time: 2–4 weeks → 2–3 days

### Agent 18: Product Intelligence Feed
**Trigger:** Daily scan | **T1**

Monitors Cisco product updates, release notes, bugs relevant to active CDA designs and known customer environments. Filters to only surface relevant changes. Daily Webex digest.  
**KPI:** Product knowledge: quarterly refresh → real-time

---

## 9. Phase 4 — HTOM + SDM Operations Layer (Months 10–12)

### Agents (8)

| # | Agent | Role | T-Tier | Key Function |
|---|-------|------|--------|--------------|
| 19 | SLA Sentinel | HTOM | T2 | Real-time SLA monitoring + draft escalations |
| 20 | Resource Optimizer | HTOM | T2 | Workload balancing recommendations |
| 21 | Ops Status Generator | HTOM | T2 | Auto-compile operational reports |
| 22 | Delivery Risk Radar | HTOM | T1 | Pattern scan for delivery risks |
| 23 | Entitlement Monitor | SDM | T1 | Contracted vs. consumed tracking |
| 24 | Service Gap Predictor | SDM | T2 | Predict delivery gaps weeks ahead |
| 25 | Delivery Comms Drafter | SDM | T2 | Customer-facing status drafts |
| 26 | Financial Health Agent | SDM | T1 | Account P&L visibility |

**Agent 19 — SLA Sentinel:** Runs every 4 hours. Tiered alerts at 20%/10%/breach-imminent SLA remaining. Draft escalation to HTOM at each threshold. Human approves before sending.

**Agent 20 — Resource Optimizer:** Weekly + on-demand. Matches upcoming project demand to available CE/CDA/PM capacity by skill, time zone, utilization. HITL: HTOM approves reallocation.

**Agent 21 — Ops Status Generator:** Weekly Monday 6am. Three output formats: executive (1 page), detailed (5+ pages), exception (blockers only). Human reviews before distribution.

**Agent 22 — Delivery Risk Radar:** Daily T1 scan. Flags engagement risk patterns. Feeds SLA Sentinel, Resource Optimizer, Ops Status Generator.

**Agent 23 — Entitlement Monitor:** Daily. Flags: utilization < 30% with renewal < 90 days, utilization > 90% with contract end < 30 days, unstarted services with deadline in 60 days.

**Agent 24 — Service Gap Predictor:** Weekly. Combines Delivery Tracker + Entitlement Monitor + Resource Optimizer output to predict service gaps and generate corrective action recommendations.

**Agent 25 — Delivery Comms Drafter:** Extends existing `status-report-agent`. Weekly + event-driven (milestone complete, SLA alert). Executive + operational formats. Human approves before send.

**Agent 26 — Financial Health Agent:** Weekly. Monitors account P&L, margin performance, cost overrun alerts, entitlement revenue forecasting. T1 informational output.

---

## 10. Phase 5 — CPM + CXL Program Intelligence (Year 2, Q1)

### Agents (8)

| # | Agent | Role | T-Tier | Key Function |
|---|-------|------|--------|--------------|
| 27 | Program Pulse Dashboard | CPM | T1 | Real-time program status from all workstreams |
| 28 | Dependency Tracker | CPM | T2 | Cross-team dependency mapping + risk flags |
| 29 | Executive Report Generator | CPM | T2 | Auto-compile executive program reports |
| 30 | Portfolio Impact Measurer | CPM | T1 | Continuous ROI tracking across agent portfolio |
| 31 | Org Performance Dashboard | CXL | T1 | Real-time KPIs across all 8 CX functions |
| 32 | Strategic Signal Aggregator | CXL | T1 | Customer sentiment + market + internal signals |
| 33 | Investment Recommender | CXL | T2 | Agent ROI analysis → investment recommendations |
| 34 | Innovation Pipeline Monitor | CXL | T1 | Agent ideas → deployment progress tracking |

**Agent 27 — Program Pulse Dashboard:** Daily aggregation from all Phase 1–4 agents. Surfaces: active workstreams status, milestones due this week, risks flagged across all agents, resource constraints.

**Agent 28 — Dependency Tracker:** Maps cross-team dependencies (CXM ↔ CE, PM ↔ CDA, SDM ↔ HTOM). Automatic risk flag when a dependency owner changes or a deadline slips upstream.

**Agent 29 — Executive Report Generator:** Weekly. Compiles all agent outputs into exec-ready report: KPI summary, risk heat map, investment performance, recommendations. Human reviews before distribution.

**Agent 30 — Portfolio Impact Measurer:** Continuously tracks: cycle-time reductions per agent, throughput gains, FTE hour savings, business outcomes tied to agent actions. Powers Agent 33.

**Agent 31 — Org Performance Dashboard:** Real-time KPIs across all 8 CX functions powered by all Phase 1–4 agent outputs. The "factory floor view" for CX leadership.

**Agent 32 — Strategic Signal Aggregator:** Synthesizes customer sentiment (CSAT trends, QBR themes), market signals, product changes (from Product Intelligence Feed), and internal operational metrics into strategic insights.

**Agent 33 — Investment Recommender:** Analyzes Portfolio Impact Measurer data. Recommends: which agents to scale, which to sunset, where to invest next based on ROI evidence.

**Agent 34 — Innovation Pipeline Monitor:** Tracks agent ideas from Identify stage through Scale. Surfaces stalled ideas, reports innovation throughput (ideas per month → pilots per month → deployed per month).

---

## 11. Phase 6 — Agent-of-Agents Orchestration (Year 2, Q2+)

**Goal:** Chain individual agents into end-to-end workflows that span roles.

### Three-Tier Chain Model (from FR-8)

| Tier | Chain Type | Approval | Max Length |
|------|-----------|----------|------------|
| T1 | Read-only chains | Standard | Unlimited |
| T2 | Draft chains with HITL gate | Security + business owner | 6 agents (pilot) |
| T3 | Autonomous chains | GRC + 45-day HITL evidence | Architecture review required |

### Planned Agent Chains

#### Chain 1: Account Risk-to-Action (SDM + CXM)
```
Customer Health Pulse → Risk Sentinel → Proactive Outreach Drafter
T1 health scoring  →  T2 risk flag  →  T2 draft comms (human approves send)
Cycle time: customer-risk-to-outreach: weeks → 24 hours
```

#### Chain 2: Project Delivery Loop (PM + CE)
```
Living Plan Agent → Schedule Risk Predictor → Stakeholder Communicator
T2 plan update   →  T1/T2 risk analysis   →  T2 draft stakeholder update
Cycle time: plan-change-to-stakeholder-update: days → same-day automated draft
```

#### Chain 3: Technical Delivery Accelerator (CE + CDA)
```
Architecture Pattern Matcher → Compatibility Validator → Design Doc Generator → Config Accelerator
T1 pattern match           →  T1 validation          →  T2 HLD/LLD draft    →  T2 config template
Cycle time: design to ready-for-CE: 2–4 weeks → 2–3 days
```

#### Chain 4: QBR Factory (SDM + CXM + CPM)
```
Delivery Tracker → Entitlement Monitor → Business Review Generator → Executive Report Generator
T1 delivery data → T1 entitlement data → T2 QBR draft            → T2 exec report
Cycle time: end-to-end QBR: 1–2 days → 30 min review
```

#### Chain 5: Operations Intelligence Loop (HTOM + SDM + CXL)
```
Delivery Risk Radar → SLA Sentinel → Resource Optimizer → Org Performance Dashboard
T1 risk patterns   → T2 SLA alerts → T2 reallocation   → T1 executive view
Continuous operations intelligence: reactive weekly → proactive real-time
```

### Orchestration Infrastructure

All chains are defined as YAML workflows in `tools/delivery-workbench/orchestration/` using the pattern established in Phase 3.1:

```yaml
# Example: account-risk-to-action.yaml
name: account-risk-to-action
trigger: event
event_source: customer-health-pulse
event_condition: score_delta_7d < -10 OR score < 60
steps:
  - agent: risk-escalation-sentinel
    tier: T2
    input: "{{ event.account_name }}"
  - agent: proactive-outreach-drafter
    tier: T2
    depends_on: risk-escalation-sentinel
    hitl_gate: webex_approval
    input: "{{ steps.risk-escalation-sentinel.output }}"
```

### Chain Promotion Criteria

Before any chain is promoted to T3 (autonomous):
1. T2 pilot run for minimum 45 days
2. Human intervention rate < 10% of runs
3. Zero customer-impact incidents attributable to chain
4. Security/GRC review sign-off
5. Documented in `AI_FACTORY_GOVERNANCE_LOG.md`

---

## 12. Complete Agent Catalog

All 32 agents mapped to roles, phases, trust tiers, and locations:

| # | Agent Name | Role | Phase | T-Tier | Location |
|---|-----------|------|-------|--------|----------|
| 1 | Delivery Tracker | SDM | 1 | T1 | `agents/delivery-tracker/` |
| 2 | Risk & Escalation Sentinel | SDM | 1 | T2 | `agents/risk-escalation-sentinel/` |
| 3 | Business Review Generator | SDM/CXM | 1 | T2 | `agents/business-review-generator/` |
| 4 | Customer Health Pulse | CXM | 2 | T1 | `agents/customer-health-pulse/` |
| 5 | Proactive Outreach Drafter | CXM | 2 | T2 | `agents/proactive-outreach-drafter/` |
| 6 | Cross-Functional Coordinator | CXM | 2 | T1 | `agents/cross-functional-coordinator/` |
| 7 | Living Plan Agent | PM | 2 | T2 | `agents/living-plan-agent/` |
| 8 | Stakeholder Communicator | PM | 2 | T2 | `agents/stakeholder-communicator/` |
| 9 | Schedule Risk Predictor | PM | 2 | T1→T2 | `agents/schedule-risk-predictor/` |
| 10 | Lessons Learned Harvester | PM | 2 | T1 | `agents/lessons-learned-harvester/` |
| 11 | Config Accelerator | CE | 3 | T2 | `agents/config-accelerator/` |
| 12 | Diagnostic Accelerator | CE | 3 | T2 | `agents/diagnostic-accelerator/` |
| 13 | Engagement Context Keeper | CE | 3 | T1 | `agents/engagement-context-keeper/` |
| 14 | Implementation Pattern Miner | CE | 3 | T1 | `agents/implementation-pattern-miner/` |
| 15 | Architecture Pattern Matcher | CDA | 3 | T1 | `agents/architecture-pattern-matcher/` |
| 16 | Compatibility Validator | CDA | 3 | T1 | `agents/compatibility-validator/` |
| 17 | Design Doc Generator | CDA | 3 | T2 | `agents/design-doc-generator/` |
| 18 | Product Intelligence Feed | CDA | 3 | T1 | `agents/product-intelligence-feed/` |
| 19 | SLA Sentinel | HTOM | 4 | T2 | `agents/sla-sentinel/` |
| 20 | Resource Optimizer | HTOM | 4 | T2 | `agents/resource-optimizer/` |
| 21 | Ops Status Generator | HTOM | 4 | T2 | `agents/ops-status-generator/` |
| 22 | Delivery Risk Radar | HTOM | 4 | T1 | `agents/delivery-risk-radar/` |
| 23 | Entitlement Monitor | SDM | 4 | T1 | `agents/entitlement-monitor/` |
| 24 | Service Gap Predictor | SDM | 4 | T2 | `agents/service-gap-predictor/` |
| 25 | Delivery Comms Drafter | SDM | 4 | T2 | `agents/delivery-comms-drafter/` |
| 26 | Financial Health Agent | SDM | 4 | T1 | `agents/financial-health-agent/` |
| 27 | Program Pulse Dashboard | CPM | 5 | T1 | `agents/program-pulse-dashboard/` |
| 28 | Dependency Tracker | CPM | 5 | T2 | `agents/dependency-tracker/` |
| 29 | Executive Report Generator | CPM | 5 | T2 | `agents/executive-report-generator/` |
| 30 | Portfolio Impact Measurer | CPM | 5 | T1 | `agents/portfolio-impact-measurer/` |
| 31 | Org Performance Dashboard | CXL | 5 | T1 | `agents/org-performance-dashboard/` |
| 32 | Strategic Signal Aggregator | CXL | 5 | T1 | `agents/strategic-signal-aggregator/` |
| 33 | Investment Recommender | CXL | 5 | T2 | `agents/investment-recommender/` |
| 34 | Innovation Pipeline Monitor | CXL | 5 | T1 | `agents/innovation-pipeline-monitor/` |

*Note: 34 agents total (framework specifies 32 + 2 additional CPM/CXL agents needed for completeness)*

---

## 13. Integration Architecture

### Integration → Agent Dependency Map

| Integration | Agents Using | Auth Method | Key Data |
|-------------|-------------|-------------|----------|
| **Helix REST API** | 10 agents | JWT (service account) | Milestones, entitlements, cases |
| **Salesforce** | 6 agents | OAuth2 via MCP | Cases, accounts, CSAT, opportunities |
| **ServiceNow** | 4 agents | API key via MCP | Incidents, problems, change requests |
| **Webex** | 8 agents | Bot token | Cards, messages, HITL approvals |
| **Outlook/Graph** | 8 agents | MSAL device code (Flerken) | Email, calendar, stakeholder context |
| **Airtable** | 4 agents | PAT (gitignored) | Reference data, baselines |
| **Cisco Bug Search** | 2 agents | CCO credentials | Known bugs, EOS/EOL data |

### Data Flow Architecture

```
External Systems          Agent Layer              Orchestration Layer
─────────────────         ───────────              ───────────────────
Salesforce ──────────→   Delivery Tracker  ──→    Delivery Workbench
ServiceNow ──────────→   Health Pulse      ──→    YAML Workflows
Helix API  ──────────→   Risk Sentinel     ──→    agent_bridge.py
Webex      ←──────────   All T2 agents     ──→    Morning Briefing
Outlook    ←──────────   Outreach Drafter  
                              ↓
                    data/runs/{agent}/{date}.json
                    data/knowledge-base/
```

### Security Principles (CodeGuard Compliance)

- All credentials in `.env` per agent — never in source code
- MCP servers as isolated integration adapters — agents never call external APIs directly
- Webex tokens: rotated on schedule, stored in `.env`, never committed
- Azure AD: delegated permissions only, minimum required scopes
- All agent outputs sanitized before Webex delivery (no PII in card previews)
- Audit log for all T2/T3 actions with timestamp, agent, human decision, reason

---

## 14. Governance & Trust Model

### HITL Approval Workflow (T2 Agents)

```
Agent generates draft
        ↓
Webex interactive card sent to domain owner
        ↓
Human reviews (target: < 15 min)
        ↓
[Approve] → Agent takes action (send, save, trigger)
[Edit] → Human modifies, then approves
[Dismiss] → Logged with reason, no action
[Snooze] → Re-queued for N hours
        ↓
All decisions logged in AI_FACTORY_GOVERNANCE_LOG.md
```

### 45-Day HITL Window Tracking

For each T2 agent, log daily during 45-day window:
- Cards sent count
- Approve rate / Edit rate / Dismiss rate
- False positive rate (dismissed because wrong)
- Average review time
- Any adverse outcomes

**Promotion criteria to T3:**
- False positive rate < 20%
- Approve-as-is rate > 60%
- Zero customer-impact incidents
- Security/GRC sign-off documented

### Governance Review Cadence

| Cadence | Activity |
|---------|---------|
| Weekly (15 min) | Review HITL logs, flag any issues |
| Monthly | Phase gate assessment, KPI review |
| Per T3 promotion | Full governance review + sign-off |
| Per chain deployment | Architecture review + T3 chain approval |

---

## 15. Success Metrics

### Phase-Level KPIs

| Phase | Primary KPI | Before | Target |
|-------|-------------|--------|--------|
| 1 | QBR prep time | 8–12 hrs | 30 min review |
| 1 | Risk detection lead time | Reactive | 5–10 days ahead |
| 2 | Customer health visibility | Weekly manual | Real-time daily |
| 2 | Plan accuracy | Degrades weekly | Real-time accurate |
| 3 | Config generation time | Hours per device | Minutes (template) |
| 3 | Architecture design time | 2–4 weeks | 2–3 days |
| 4 | SLA breach detection | Post-breach | Predictive |
| 4 | Resource utilization | 65% | 85%+ |
| 5 | Executive report time | 4–8 hrs | Auto-generated |
| 5 | Innovation throughput | Ad hoc | Systematic pipeline |

### Maturity Progression Targets

| Milestone | Timing | Indicator |
|-----------|--------|-----------|
| L1 → L2 (Assisted) | End of Phase 1 | 3 T1 agents live, baselines tracked |
| L2 → L3 (Augmented) | End of Phase 3 | 5+ T2 agents with HITL, 40%+ cycle-time reduction |
| L3 → L4 (Autonomous) | End of Phase 6 | ≥ 3 agents promoted to T3, agent-of-agents running |

### Portfolio ROI Tracking

Maintained by Portfolio Impact Measurer (Agent 30) from Phase 5:
- Hours saved per week per agent
- FTE equivalent freed per role
- Cycle-time improvement % per workflow
- Agent portfolio ROI vs. development investment

---

## 16. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Webex tokens expire again | HIGH | HIGH | Implement token expiry monitoring + calendar alert 30 days before expiry |
| Azure AD blocked permanently | MEDIUM | HIGH | Identify alternative Outlook path (IMAP/POP3 as degraded fallback); prioritize resolution |
| Salesforce API access denied | MEDIUM | HIGH | Work with admin to provision service account; use read-only sandbox during dev |
| LLM hallucination in QBR | MEDIUM | HIGH | Ground all metrics in source data before LLM pass; human review gate is mandatory |
| False positive rate > 20% on Risk Sentinel | MEDIUM | MEDIUM | Tune thresholds with SDM domain expert in Week 1; adjustable per account tier |
| Helix API changes break agents | LOW | HIGH | Version pin all Helix API calls; add contract tests in CI |
| Domain owner unavailable for HITL | LOW | MEDIUM | Define backup approver per agent; 48-hour auto-escalation if no response |
| Agent chain complexity exceeds governance capacity | LOW | MEDIUM | Hard limit: 6 agents per chain in pilot; architecture review required for longer chains |
| Knowledge base quality degrades over time | MEDIUM | MEDIUM | Monthly quality review of `data/knowledge-base/`; Lessons Learned Harvester continuously feeds it |

---

## Appendix A: First 30 Days Action Plan

| Day | Action | Owner |
|-----|--------|-------|
| 1–3 | Read all existing documents in Section 2 | You |
| 4–5 | Finalize agent card template | You + domain expert |
| 6–10 | Start baseline measurement (5 workflows, 2 weeks) | You + SDM |
| 7 | Rotate Webex tokens | Ops |
| 7–14 | Register Azure AD app | Ops / IT |
| 8–14 | Integration readiness matrix | You |
| 15 | Initialize agent registry + governance log | You |
| 16–20 | Write Phase 1 agent cards (3 cards) | You + SDM domain expert |
| 21 | Phase 0 exit gate review | You |
| 22–30 | Begin Phase 1 Agent 1 (Delivery Tracker) development | Cursor task |

---

*Last updated: May 27, 2026 | Next review: Phase 0 exit gate*
