# AI Factory — Cycle Time Baselines

> **Purpose:** Establish pre-agent baselines for 5 SDM workflows. These are the "before" numbers  
> against which Phase 1 KPI targets will be measured. Fill in actual values from 2-week manual  
> tracking before first agent goes live (Phase 0 exit criterion).
>
> **Measurement period:** Fill in actual start/end dates below  
> **Measured by:** SDM domain expert  
> **Reference:** `AI_FACTORY_IMPLEMENTATION_PLAN.md` Section 5.2

---

## Measurement Instructions

1. Track each workflow manually for **2 weeks** before any agent is enabled.
2. Record each instance individually in the per-workflow tables below.
3. Calculate the average — that is the baseline.
4. "Target" values are set from Phase 1 agent KPI targets in the implementation plan.

---

## Workflow 1: Weekly Status Report

**Trigger:** SDM compiles weekly delivery status across all active accounts  
**Measure:** Total wall-clock time per report (hours)  
**Target:** 2–3 hr weekly check → **≤ 5 min review** (Delivery Tracker T1)

| Date | Accounts Covered | Time Taken (hrs) | Notes |
| ---- | ---------------- | ---------------- | ----- |
| — | — | — | Baseline measurement pending |

**Baseline average:** _____ hrs/report  
**Measured by:** _____  
**Measurement period:** _____ to _____

---

## Workflow 2: Risk Identification

**Trigger:** SDM discovers a risk signal (overdue milestone, SLA breach approaching, stalled case)  
**Measure:** Days elapsed from when risk emerged (Helix data event) to when SDM detected it  
**Target:** Reactive (avg detection days) → **5–10 days predictive** (Risk Sentinel T2)

| Date Detected | Account | Risk Type | Risk Emerged (est.) | Days to Detection | Notes |
| ------------- | ------- | --------- | ------------------- | ----------------- | ----- |
| — | — | — | — | — | Baseline measurement pending |

**Baseline average detection lag:** _____ days  
**Measured by:** _____  
**Measurement period:** _____ to _____

---

## Workflow 3: QBR / EBR Preparation

**Trigger:** Quarterly or executive business review due for an account  
**Measure:** Total SDM/CXM prep time per review (hours), from data gathering to draft-ready  
**Target:** 8–12 hr QBR prep → **≤ 30 min review** (Business Review Generator T2)

| Date | Account | Review Type | Data Gathering (hrs) | Writing (hrs) | Total (hrs) | Notes |
| ---- | ------- | ----------- | -------------------- | ------------- | ----------- | ----- |
| — | — | — | — | — | — | Baseline measurement pending |

**Baseline average:** _____ hrs/QBR  
**Measured by:** _____  
**Measurement period:** _____ to _____

---

## Workflow 4: Entitlement Tracking

**Trigger:** SDM checks whether an account's entitlement usage is on track  
**Measure:** Frequency at which under-run or over-run is discovered late (within 30 days of expiry)  
**Target:** Reduce late discoveries to near zero (Phase 4: Entitlement Monitor T1)

| Month | Accounts Reviewed | Late Discoveries (< 30d) | Discovery Method | Notes |
| ----- | ----------------- | ------------------------ | ---------------- | ----- |
| — | — | — | — | Baseline measurement pending |

**Baseline late discovery rate:** _____ % of accounts/quarter  
**Measured by:** _____  
**Measurement period:** _____ to _____

---

## Workflow 5: Customer Communications Draft

**Trigger:** SDM needs to draft a proactive or reactive customer communication  
**Measure:** Time from "decision to communicate" to "draft ready for review" (minutes)  
**Target:** Manual drafting time → **≤ 2 min HITL approval** (Phase 4: Delivery Comms Drafter T2)

| Date | Account | Communication Type | Time to Draft (min) | Notes |
| ---- | ------- | ------------------ | ------------------- | ----- |
| — | — | — | — | Baseline measurement pending |

**Baseline average:** _____ min/communication  
**Measured by:** _____  
**Measurement period:** _____ to _____

---

## Summary Table (Fill in After 2-Week Measurement)

| Workflow | Baseline Value | Unit | Target | Reduction |
| -------- | -------------- | ---- | ------ | --------- |
| Weekly status report | _(pending)_ | hrs/report | ≤ 5 min review | — |
| Risk identification | _(pending)_ | days to detect | Predictive (5–10d) | — |
| QBR prep | _(pending)_ | hrs/QBR | ≤ 30 min review | — |
| Entitlement tracking | _(pending)_ | % late discoveries | Near zero | — |
| Customer comms draft | _(pending)_ | min/draft | ≤ 2 min HITL | — |

---

_Phase 0 exit criterion: all 5 baselines populated before Phase 1 Week 5 gate._  
_Reference: `AI_FACTORY_IMPLEMENTATION_PLAN.md` Section 5.2 and Section 6 (Phase 1 KPI targets)_
