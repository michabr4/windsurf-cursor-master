# Windsurf Architect Plan — Version 2

> **Supersedes:** `WINDSURF_ARCHITECT_PLAN.md` (V1, May 26, 2026)  
> **Issued:** May 27, 2026  
> **Status:** Active — governing document  
> **What changed from V1:** Mission updated to AI Factory + customer automation. Claude Reasoning Framework added. Design Studio workflow added. Comms Bridge integrated. Domain design docs introduced. Cursor model routing strategy defined.

---

## What's Different from V1

| V1 | V2 |
|---|---|
| Mission: consolidate 17 projects | Mission: operate an AI delivery intelligence platform |
| Two-tier: Windsurf → Cursor | Three-tier: Windsurf → Claude Reasoning → Cursor |
| Specs written ad-hoc | Design Studio workflow (structured 6-step process) |
| ADRs created reactively | ADRs created proactively before spec writing |
| Monolithic master plan | Domain design docs per workstream |
| Comms Bridge not in operating model | Comms Bridge is the nervous system of the pipeline |
| Generic AI model references | Explicit Claude routing: Opus (reasoning), Sonnet (build) |
| Session bootstrap: manual | Session bootstrap: structured prompt + context synthesis |
| AI Factory not in scope | AI Factory (34 agents) is the primary build pipeline |
| Customer automation not addressed | Customer automation (MGM, DD) is a first-class workstream |

---

## Part 1: Mission

**Transform a Cisco CX SDM operation into an AI-powered delivery intelligence platform** — governed by disciplined Architect/Builder collaboration, informed by Claude's reasoning, built by Cursor, and continuously learning from real customer work.

### Three Pillars

| Pillar | What It Means |
|--------|---------------|
| **AI Factory** | 34 agents across 8 CX roles, built in 6 phases — automating SDM workflows at scale |
| **Customer Automation** | Customer-specific agents and tools (MGM, DD, future) that deliver immediate ROI |
| **Platform & Infrastructure** | Helix, shared integrations, MCP servers, governance framework |

### North Star (12-Month View)

```
TODAY (May 2026):
  Automation backlog defined, AI Factory in design, customer tools broken/manual

6 MONTHS (Nov 2026):
  AI Factory Phase 1-2 live (10 agents), MGM status report automated,
  Firewall migration tracked, shared integration layer deployed

12 MONTHS (May 2027):
  AI Factory Phase 3-4 live (26 agents), all P0/P1 customer automations active,
  Helix with live data, multi-customer platform, NetPilot deployed
```

---

## Part 2: The Three-Tier Operating Model

This is the core upgrade from V1. Every non-trivial piece of work flows through three tiers:

```
┌─────────────────────────────────────────────────────────┐
│  TIER 1: STRATEGY (Windsurf)                            │
│  • Backlog prioritization                               │
│  • Domain design docs                                   │
│  • ADR creation                                         │
│  • Design session initiation                            │
│  • Quality gate reviews                                 │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  TIER 2: REASONING (Claude Extended Thinking)           │
│  • Architectural trade-off analysis                     │
│  • Spec completeness validation                         │
│  • Security pre-flight review                           │
│  • Edge case and failure mode enumeration               │
│  • Design option generation (2-3 approaches)            │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  TIER 3: IMPLEMENTATION (Cursor + Claude)               │
│  • Code generation (Claude Sonnet 4.5)                  │
│  • Test-first implementation                            │
│  • Build reporting via Comms Bridge                     │
│  • Claude Opus for complex reasoning within builds      │
└─────────────────────────────────────────────────────────┘
```

### The Comms Bridge as Nervous System

The Comms Bridge (`.comms/`) is the coordination layer between all three tiers:

| Direction | Content |
|-----------|---------|
| Windsurf → Cursor | Structured task specs (TASK-*.json) |
| Cursor → Windsurf | Build results (RESULT-*.json) |
| Windsurf → Windsurf | Session context synthesis (session-start prompt) |

**Operating rule:** No work starts in Cursor without a task in the inbox. No task moves to "active" without Windsurf's ADR and spec complete.

---

## Part 3: Claude Reasoning Framework

This is the most significant addition from V1. Claude is used not just as a code generator but as a structured reasoning engine at multiple stages.

### 3.1 When to Use Claude Reasoning (Windsurf Side)

| Trigger | Reasoning Task | Prompt Pattern |
|---------|---------------|----------------|
| New agent design | Generate 2-3 architectural approaches with trade-offs | "Design Options" template |
| Complex spec writing | Stress-test the spec before sending to Cursor | "Spec Validation" template |
| Integration decision | Analyze coupling, dependency risk, auth patterns | "Integration Analysis" template |
| Risk assessment | Enumerate failure modes and mitigations | "Failure Mode Analysis" template |
| ADR decision | Think through consequences before committing | "Decision Consequences" template |

### 3.2 Prompt Templates for Claude Reasoning

Use these in Windsurf before writing specs. They are structured thinking activators.

#### Template A: Design Options
```
Context: [2-3 sentences on what we're building and why]
Constraints: [tech stack, security requirements, existing integrations]
Task: Generate exactly 3 architectural approaches for [problem].
For each approach, cover:
  1. How it works (3-5 sentences)
  2. Dependencies required
  3. Key trade-offs (2-3 bullet points)
  4. Security considerations
  5. Estimated dev complexity (Easy/Medium/Complex)
End with: your recommended approach and primary reason.
```

#### Template B: Spec Validation
```
Below is a Cursor instruction packet for [task].
Act as a skeptical senior engineer reviewing it before execution.
Check for:
  1. Ambiguities that would cause Cursor to make wrong assumptions
  2. Missing error scenarios or edge cases
  3. Security gaps (CodeGuard violations, missing auth checks)
  4. Missing test criteria — what should Cursor verify?
  5. Dependencies that aren't called out
Output: list of gaps with severity (BLOCK / WARN / NOTE), then a revised spec if needed.
[paste spec here]
```

#### Template C: Failure Mode Analysis
```
We are building: [system description]
Context: [customer, stakes, integrations]
Task: Enumerate the top 10 failure modes for this system.
For each failure mode:
  - Trigger condition
  - Impact (user-facing / data / security)
  - Probability (High/Medium/Low)
  - Mitigation strategy
Format as a table.
```

#### Template D: Integration Analysis
```
We need to integrate [System A] with [System B] in [context].
Existing auth pattern: [current approach]
Task: Analyze this integration for:
  1. Auth and token management risks
  2. Rate limit and resilience considerations
  3. Data sensitivity and PII exposure points
  4. Failure isolation — if [B] is down, what breaks?
  5. Recommended implementation pattern with rationale
```

### 3.3 Claude Model Routing (Both IDEs)

| Task Type | Model | Reason |
|-----------|-------|--------|
| Architectural design, trade-off analysis | Claude Opus 4 | Best reasoning depth |
| Standard code generation, spec writing | Claude Sonnet 4.5 | Best speed/quality balance |
| Quick lookups, formatting, summaries | Claude Haiku 3.5 | Fast, low cost |
| Complex agent logic implementation | Claude Sonnet + thinking mode | Needs reasoning + code quality |
| Security review, spec validation | Claude Opus 4 | Cannot afford gaps |

**In Windsurf:** Switch to Opus when using Design Options or Spec Validation templates. Use Sonnet for day-to-day planning and spec writing.

**In Cursor:** See `CURSOR_UPGRADES_V2.md` for model routing rules and the Anthropic MCP server setup.

---

## Part 4: Design Studio Workflow

Every non-trivial backlog item (anything above P2 complexity or requiring a new integration) passes through this workflow before a Cursor task is created.

### The 6-Step Design Studio

```
Step 1: FRAME (5 min)
  → What problem does this solve?
  → What's the measurable success criterion?
  → Which backlog item ID does this map to?

Step 2: DEPEND (5 min)
  → What existing systems does this read from?
  → What does this write to or trigger?
  → What must exist before this can run?
  → What will break if this fails?

Step 3: REASON (10-20 min) ← Claude Tier 2 engagement
  → Run Template A (Design Options) in Claude
  → Select approach; document rationale
  → Run Template C (Failure Mode Analysis) if high-stakes

Step 4: RECORD (5 min)
  → Create or update ADR in ADR_LOG.md
  → ADR number assigned sequentially
  → Status: Proposed → Accepted when decision is final

Step 5: SPECIFY (10-20 min)
  → Write the Cursor Instruction Packet (see spec template below)
  → Run Template B (Spec Validation) in Claude
  → Resolve all BLOCK-level gaps before proceeding

Step 6: DISPATCH (2 min)
  → Create task via Comms Bridge (mcp3_send_task)
  → Link to: ADR number, backlog item ID, domain design doc
  → Set priority and phase correctly
```

### Spec Template (V2 — Improved from V1)

Every Cursor Instruction Packet must include these sections:

```markdown
## TASK: [ID] — [Title]

**Backlog Item:** [e.g. MGM-02]
**ADR Reference:** ADR-[NNN]
**Priority:** P0/P1/P2
**Phase:** [AI Factory phase or Customer sprint]
**Trust Tier (agents only):** T1/T2/T3

### Context
[2-3 sentences: why this task exists, what problem it solves]

### Location
[Exact path in master folder]

### Prerequisites
[What must exist/be done before this task starts]

### Inputs
[Data sources, APIs, files, environment variables required]

### Steps
1. [Specific, numbered, unambiguous]
2. ...

### Outputs
[Files created, APIs called, messages sent, state changed]

### Test Criteria (REQUIRED)
- [ ] [Specific, verifiable pass/fail check 1]
- [ ] [Specific, verifiable pass/fail check 2]
- [ ] No hardcoded credentials (CodeGuard check)
- [ ] .env.example updated if new vars added
- [ ] Existing tests still pass

### Error Scenarios
| Scenario | Expected Behavior |
|----------|------------------|
| [e.g. API unreachable] | [e.g. Log error, do not crash, alert via console] |

### Security Checklist
- [ ] No secrets in source
- [ ] Auth via .env only
- [ ] Input validated before processing
- [ ] Outputs sanitized (no PII in logs)

### Report Back Format
Status: [SUCCESS / PARTIAL / FAILED]
What was done: [bullet list]
Issues found: [bullet list or "None"]
Files changed: [list]
Needs Windsurf review: [specific items]
```

---

## Part 5: Domain Design Documents

V1 had a single monolithic plan. V2 introduces domain-specific design docs — one per major workstream. Each is maintained by Windsurf and referenced by Cursor tasks.

| Domain | Document | Status |
|--------|----------|--------|
| AI Factory (all 34 agents) | `AI_FACTORY_IMPLEMENTATION_PLAN.md` | ✅ Active |
| Automation Backlog (all items) | `AUTOMATION_BACKLOG.md` | ✅ Active |
| Customer: MGM Resorts | `domains/mgm-resorts/DESIGN.md` | ⬜ To create |
| Customer: DD | `domains/dd/DESIGN.md` | ⬜ To create |
| Shared Integration Layer | `domains/integrations/DESIGN.md` | ⬜ To create — Phase 3 |
| Platform (Helix / ServiceFlow) | `platforms/serviceflow-sdm/docs/ARCHITECTURE.md` | ⬜ To create |

Domain design docs capture the "why" and "how" for each workstream — decisions that span multiple specs and ADRs. Cursor reads them as context before executing tasks in that domain.

---

## Part 6: Architectural Principles (Updated)

Original V1 principles retained. Three new principles added:

| Principle | What It Means In Practice |
|-----------|--------------------------|
| **Single source of truth** | One master folder. One index. One roadmap. No orphan projects. |
| **Separation of concerns** | Windsurf designs, Claude reasons, Cursor builds. |
| **Security by default** | 22 CodeGuard rules enforced in both IDEs. No secrets in source. |
| **Build for reuse** | Every agent, bot, and integration is modular. |
| **Document as you go** | Every architectural decision logged. Every spec versioned. |
| **Progressive complexity** | Start with what works. Add integrations incrementally. |
| **Observable outcomes** | Every project has measurable success criteria. |
| **Reason before you spec** *(NEW)* | No spec is written without a Claude reasoning pass for complex items. |
| **Customer-first prioritization** *(NEW)* | P0 customer items (MGM, DD) take precedence over platform work. |
| **Agent-first design** *(NEW)* | All new tools are designed as agents first — with trust tiers, HITL gates, and measurable KPIs — even if T1 only. |

---

## Part 7: Governance Framework (Updated)

### Quality Gates (Upgraded V2)

| Gate | Check | V1 | V2 Change |
|------|-------|----|-----------|
| **G0: Design** | ADR created, Claude reasoning pass done | Not in V1 | **New** — required for P0/P1 items |
| **G1: Completeness** | All spec sections filled (including test criteria) | Partial | Now mandatory — spec template enforced |
| **G2: Security** | No hardcoded secrets, CodeGuard checklist in spec | Yes | Security checklist added to spec template |
| **G3: Documentation** | Files changed logged, ADR updated | Yes | Unchanged |
| **G4: Testing** | Test criteria verified, smoke tests passing | Yes | Test criteria now in spec template |
| **G5: Standards** | Linters pass | Yes | Unchanged |
| **G6: Integration** | No broken dependencies | Yes | Unchanged |

### ADR Cadence (Upgraded)

**V1:** ADRs written reactively when decisions are made.

**V2:** ADRs are created in Step 4 of Design Studio, *before* the spec is written. Format:

```markdown
## ADR-[NNN]: [Title]
- **Date:** YYYY-MM-DD
- **Status:** Proposed | Accepted | Superseded | Rejected
- **Backlog Item:** [e.g. MGM-02]
- **Context:** [Why this decision is needed]
- **Options Considered:** [2-3 from Claude Design Options pass]
- **Decision:** [What was chosen]
- **Rationale:** [Why this option over others]
- **Consequences:** [What this commits us to, what it rules out]
- **Security Impact:** [None / describe]
- **Supersedes:** [ADR-NNN if applicable]
```

### Review Cadence

| Review | Frequency | Windsurf Action |
|--------|-----------|-----------------|
| Task review | After each Cursor result | Read RESULT-*.json, update backlog item status |
| Domain review | Weekly per active domain | Review domain design doc, update open questions |
| Phase gate | Per AI Factory phase | Full governance review per `AI_FACTORY_GOVERNANCE_LOG.md` |
| Architecture review | Before any new integration | Design Options + Integration Analysis Claude passes |

---

## Part 8: Session Bootstrap Protocol (Upgraded)

### Session Start Sequence

Every new Windsurf session begins with this protocol to restore full context:

**Step 1 — Auto-read these files (in order):**
1. `AUTOMATION_BACKLOG.md` — what's prioritized
2. `ROADMAP.md` — where we are
3. `AI_FACTORY_AGENT_REGISTRY.md` — agent status
4. `ADR_LOG.md` — recent decisions
5. Check `.comms/` for any pending results from Cursor

**Step 2 — Context Synthesis Prompt (paste at session start):**

```
You are Windsurf, the Architect in a three-tier system:
  Tier 1: You (Windsurf) — strategy, design, specs, governance
  Tier 2: Claude Reasoning — trade-off analysis, spec validation, design options
  Tier 3: Cursor — implementation, testing, build reporting

Current project: Cisco CX AI Delivery Intelligence Platform
Key documents just read: AUTOMATION_BACKLOG.md, ROADMAP.md, AI_FACTORY_AGENT_REGISTRY.md, ADR_LOG.md

Your mode today: [DESIGN / REVIEW / PLANNING — pick one]

Active workstreams:
  • AI Factory: Phase 0 (foundation), agents 1-3 in design
  • Customer MGM: MGM-01 (token fix) and MGM-02 (status report agent) are P0
  • Customer DD: DD-01 (token fix) is P0
  • Infrastructure: Comms Bridge operational, 17 tasks completed

Resume from the highest-priority incomplete item in the backlog.
Before any spec is written: run the Design Studio workflow (Part 4 of WINDSURF_ARCHITECT_PLAN_V2.md).
```

**Step 3 — Check Comms Bridge:**

```
Check .comms/outbox/ for any Cursor results awaiting Windsurf review.
If results found: review them, update backlog status, archive via mcp3_archive_completed.
Then resume from next priority item.
```

---

## Part 9: Spec Backlog (Updated)

V1 spec backlog had SPEC-001 through SPEC-020. Updated below to reflect current state and new priorities.

### Completed Specs (V1 deliverables done)
| Spec | Title | Status |
|------|-------|--------|
| SPEC-001 | Migration instructions | ✅ Delivered + executed |
| SPEC-002 | Cursor setup plan | ✅ Delivered (V1) |
| SPEC-003 | Consolidation instruction packets | ✅ Delivered |

### Active Specs (Current Sprint)
| Spec | Title | Domain | Priority | ADR Needed |
|------|-------|--------|----------|------------|
| SPEC-021 | Webex token rotation procedure | MGM/DD | P0 | No (ops) |
| SPEC-022 | MGM Weekly Status Report Agent | MGM | P0 | ADR-009 |
| SPEC-023 | AI Factory Delivery Tracker (Agent 1) | AI Factory | P0 | ADR-010 |
| SPEC-024 | MGM Firewall Migration Tracker | MGM | P1 | ADR-011 |
| SPEC-025 | Cursor V2 Upgrades (model routing, new rules) | Infrastructure | P1 | No |

### Queued Specs (Next Sprint)
| Spec | Title | Domain | Priority |
|------|-------|--------|----------|
| SPEC-026 | Risk & Escalation Sentinel (Agent 2) | AI Factory | P1 |
| SPEC-027 | Business Review Generator (Agent 3) | AI Factory | P1 |
| SPEC-028 | DD Weekly Status Report Agent | DD | P1 |
| SPEC-029 | Salesforce MCP Server | Infrastructure | P1 |
| SPEC-030 | ServiceNow MCP Server | Infrastructure | P1 |
| SPEC-031 | Shared Webex bot framework | Infrastructure | P1 |
| SPEC-032 | MGM Domain Design Doc | MGM | P1 |
| SPEC-033 | Helix production hardening | Platform | P2 |
| SPEC-034 | MGM Firewall Config Generation Assistant | MGM | P1 |

### Phase 3+ Specs (Planned — Not Yet Written)
| Spec | Title | Domain | Priority |
|------|-------|--------|----------|
| SPEC-035 | Shared integration layer (Salesforce, SNOW, Webex, Graph) | Infrastructure | P1 |
| SPEC-036 | Agents 4-10 (AI Factory Phase 2: CXM + PM) | AI Factory | P2 |
| SPEC-037 | Agents 11-18 (AI Factory Phase 3: CE + CDA) | AI Factory | P2 |
| SPEC-038 | Azure AD registration for Forge | Infrastructure | P1 |
| SPEC-039 | NetPilot CCNA App completion | Tools | P2 |

---

## Part 10: Risk Register (Updated)

| Risk | Severity | V1/New | Mitigation |
|------|----------|--------|-----------|
| Session context loss | HIGH | V1 | Session Bootstrap Protocol (Part 8) + memory system |
| Cursor deviates from spec | MEDIUM | V1 | V2 spec template with test criteria + mandatory report-back format |
| Secret exposure | HIGH | V1 | ADR-008 procedure + CodeGuard in both IDEs |
| AI Factory scope overrun | HIGH | NEW | Phase gates with explicit exit criteria per AI_FACTORY_IMPLEMENTATION_PLAN.md |
| MGM token not rotated → blocks P0 items | HIGH | NEW | Escalate immediately — blocks MGM-02, DD-01, DD-02 |
| Claude reasoning pass skipped for speed | MEDIUM | NEW | Design Studio is non-negotiable for P0/P1 items |
| Domain design docs missing → specs lack context | MEDIUM | NEW | Create MGM domain doc as first Windsurf design task |
| Comms Bridge message backlog buildup | LOW | NEW | Archive completed results at session start |
| Salesforce/ServiceNow access not confirmed | MEDIUM | V1 | Track in AI_FACTORY_INTEGRATION_READINESS.md; block dependent agents |

---

## Part 11: 90-Day Execution Plan (Updated)

| Period | Windsurf Delivers | Cursor Builds | Success Looks Like |
|--------|------------------|---------------|-------------------|
| **Week 1 (now)** | SPEC-021/022/023, ADR-009/010, MGM domain doc | Token rotation, MGM status agent, Delivery Tracker scaffold | MGM bot live, Delivery Tracker CLI working |
| **Week 2** | SPEC-024/025/026, ADR-011, Cursor V2 upgrades | Firewall migration tracker, Cursor upgraded, Risk Sentinel scaffold | MGM tracker posting to Webex, Cursor using Opus for complex tasks |
| **Weeks 3-4** | SPEC-027/028/029, Agent cards signed | BRG scaffold, DD report agent, Salesforce MCP | 3 Phase 1 agents in code, DD bot live |
| **Month 2** | Phase 1 exit gate review, Phase 2 specs | Delivery Tracker live, Risk Sentinel HITL window open | Daily delivery status in Webex, weekly baseline measurement |
| **Month 3** | Shared integration layer specs, Phase 2 agents | Integration modules, Customer Health Pulse, Living Plan | Agents #4-7 in design/build, shared SF/SNOW clients |

---

## Appendix: Document Registry (Updated V2)

| Document | Owner | Purpose | Version |
|----------|-------|---------|---------|
| `WINDSURF_ARCHITECT_PLAN_V2.md` | Windsurf | This file — operating model (active) | V2 |
| `WINDSURF_ARCHITECT_PLAN.md` | Windsurf | V1 — historical reference | V1 (archived) |
| `AUTOMATION_BACKLOG.md` | Windsurf | Master backlog with all items, priorities, categories | Active |
| `AI_FACTORY_IMPLEMENTATION_PLAN.md` | Windsurf | Full 34-agent implementation plan | Active |
| `AI_FACTORY_AGENT_REGISTRY.md` | Windsurf | Agent status + phase registry | Active |
| `AI_FACTORY_GOVERNANCE_LOG.md` | Windsurf | HITL decisions, tier promotions, phase gates | Active |
| `AI_FACTORY_CYCLE_TIME_BASELINES.md` | Windsurf | Baseline measurements before agents go live | Active |
| `AI_FACTORY_INTEGRATION_READINESS.md` | Windsurf | Integration access status per system | Active |
| `ROADMAP.md` | Windsurf | Phased execution plan | Active |
| `ADR_LOG.md` | Windsurf | Architecture decision records | Active |
| `CURSOR_SETUP_PLAN.md` | Windsurf | Original Cursor setup (V1) | Reference |
| `CURSOR_UPGRADES_V2.md` | Windsurf | Cursor upgrades — model routing, new rules, Anthropic MCP | Active |
| `.comms/transcript.md` | Both | Live Windsurf ↔ Cursor comms log | Active |
| `domains/mgm-resorts/DESIGN.md` | Windsurf | MGM domain design doc | To create |

---

*Version 2. Windsurf is the Architect. Claude is the Reasoner. Cursor is the Builder.*  
*Last updated: 2026-05-27*
