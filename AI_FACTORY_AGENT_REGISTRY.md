# AI Factory — Agent Registry

> **Maintained by:** Windsurf (Architect)  
> **Update cadence:** Start of every sprint  
> **Source of truth for:** Agent status, location, trust tier, phase assignment

---

## Registry

| # | Agent Name | Role | Phase | Status | Trust Tier | Location |
|---|-----------|------|-------|--------|------------|---------|
| 1 | Delivery Tracker | SDM | 1 | 🟡 In Design | T1 | `agents/delivery-tracker/` |
| 2 | Risk & Escalation Sentinel | SDM | 1 | 🟡 In Design | T2 | `agents/risk-escalation-sentinel/` |
| 3 | Business Review Generator | SDM/CXM | 1 | 🟡 In Design | T2 | `agents/business-review-generator/` |
| 4 | Customer Health Pulse | CXM | 2 | ⬜ Planned | T1 | `agents/customer-health-pulse/` |
| 5 | Proactive Outreach Drafter | CXM | 2 | ⬜ Planned | T2 | `agents/proactive-outreach-drafter/` |
| 6 | Cross-Functional Coordinator | CXM | 2 | ⬜ Planned | T1 | `agents/cross-functional-coordinator/` |
| 7 | Living Plan Agent | PM | 2 | ⬜ Planned | T2 | `agents/living-plan-agent/` |
| 8 | Stakeholder Communicator | PM | 2 | ⬜ Planned | T2 | `agents/stakeholder-communicator/` |
| 9 | Schedule Risk Predictor | PM | 2 | ⬜ Planned | T1→T2 | `agents/schedule-risk-predictor/` |
| 10 | Lessons Learned Harvester | PM | 2 | ⬜ Planned | T1 | `agents/lessons-learned-harvester/` |
| 11 | Config Accelerator | CE | 3 | ⬜ Planned | T2 | `agents/config-accelerator/` |
| 12 | Diagnostic Accelerator | CE | 3 | ⬜ Planned | T2 | `agents/diagnostic-accelerator/` |
| 13 | Engagement Context Keeper | CE | 3 | ⬜ Planned | T1 | `agents/engagement-context-keeper/` |
| 14 | Implementation Pattern Miner | CE | 3 | ⬜ Planned | T1 | `agents/implementation-pattern-miner/` |
| 15 | Architecture Pattern Matcher | CDA | 3 | ⬜ Planned | T1 | `agents/architecture-pattern-matcher/` |
| 16 | Compatibility Validator | CDA | 3 | ⬜ Planned | T1 | `agents/compatibility-validator/` |
| 17 | Design Doc Generator | CDA | 3 | ⬜ Planned | T2 | `agents/design-doc-generator/` |
| 18 | Product Intelligence Feed | CDA | 3 | ⬜ Planned | T1 | `agents/product-intelligence-feed/` |
| 19 | SLA Sentinel | HTOM | 4 | ⬜ Planned | T2 | `agents/sla-sentinel/` |
| 20 | Resource Optimizer | HTOM | 4 | ⬜ Planned | T2 | `agents/resource-optimizer/` |
| 21 | Ops Status Generator | HTOM | 4 | ⬜ Planned | T2 | `agents/ops-status-generator/` |
| 22 | Delivery Risk Radar | HTOM | 4 | ⬜ Planned | T1 | `agents/delivery-risk-radar/` |
| 23 | Entitlement Monitor | SDM | 4 | ⬜ Planned | T1 | `agents/entitlement-monitor/` |
| 24 | Service Gap Predictor | SDM | 4 | ⬜ Planned | T2 | `agents/service-gap-predictor/` |
| 25 | Delivery Comms Drafter | SDM | 4 | ⬜ Planned | T2 | `agents/delivery-comms-drafter/` |
| 26 | Financial Health Agent | SDM | 4 | ⬜ Planned | T1 | `agents/financial-health-agent/` |
| 27 | Program Pulse Dashboard | CPM | 5 | ⬜ Planned | T1 | `agents/program-pulse-dashboard/` |
| 28 | Dependency Tracker | CPM | 5 | ⬜ Planned | T2 | `agents/dependency-tracker/` |
| 29 | Executive Report Generator | CPM | 5 | ⬜ Planned | T2 | `agents/executive-report-generator/` |
| 30 | Portfolio Impact Measurer | CPM | 5 | ⬜ Planned | T1 | `agents/portfolio-impact-measurer/` |
| 31 | Org Performance Dashboard | CXL | 5 | ⬜ Planned | T1 | `agents/org-performance-dashboard/` |
| 32 | Strategic Signal Aggregator | CXL | 5 | ⬜ Planned | T1 | `agents/strategic-signal-aggregator/` |
| 33 | Investment Recommender | CXL | 5 | ⬜ Planned | T2 | `agents/investment-recommender/` |
| 34 | Innovation Pipeline Monitor | CXL | 5 | ⬜ Planned | T1 | `agents/innovation-pipeline-monitor/` |

---

## Status Key

| Symbol | Meaning |
|--------|---------|
| ⬜ Planned | In backlog — not yet started |
| 🟡 In Design | Agent card being written, not yet in dev |
| 🔵 In Development | Active sprint, code being written |
| 🟢 HITL Active | Deployed, in 45-day human-in-the-loop window |
| ✅ T3 Promoted | Passed governance gate, autonomous capable |
| 🔴 On Hold | Blocked or paused |

---

## Phase Summary

| Phase | Agents | Status |
|-------|--------|--------|
| 0 — Foundation | 0 | ✅ Infrastructure work |
| 1 — SDM Pilots | #1–3 | 🟡 Week 1: In Design |
| 2 — CXM + PM | #4–10 | ⬜ Planned (Months 4–6) |
| 3 — CE + CDA | #11–18 | ⬜ Planned (Months 7–9) |
| 4 — HTOM + SDM Ops | #19–26 | ⬜ Planned (Months 10–12) |
| 5 — CPM + CXL | #27–34 | ⬜ Planned (Year 2 Q1) |
| 6 — Orchestration | Chains | ⬜ Planned (Year 2 Q2+) |

---

*Reference: `AI_FACTORY_IMPLEMENTATION_PLAN.md` Section 12*  
*Last updated: 2026-05-27*
