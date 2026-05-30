# Architecture Decision Records

**Owner:** Windsurf (Architect)  
**Started:** May 26, 2026

---

## ADR-001: Windsurf as Architect, Cursor as Builder

- **Date:** 2026-05-26
- **Status:** Accepted
- **Context:** Work is spread across two IDEs (Windsurf and Cursor) with no coordination. Projects overlap, naming is inconsistent, and there is no design authority.
- **Decision:** Windsurf owns all design, planning, specifications, and review. Cursor owns all implementation, coding, and execution. The operator (michabr4) is final authority.
- **Consequences:** All implementation work requires a written spec. Cursor must document all work in logs. No architectural decisions are made in Cursor without Windsurf approval.

---

## ADR-002: Master Folder as Single Source of Truth

- **Date:** 2026-05-26
- **Status:** Accepted
- **Context:** 17 projects scattered across Desktop, home directory, and projects folder. No central index. Difficult to track status and dependencies.
- **Decision:** Migrate all projects into `~/New Master Folder - Windsurf and Cursor/` with a structured mono-repo layout (platforms/, agents/, bots/, tools/, content/, data/, _archived/).
- **Consequences:** All future project paths change. Git remotes must be verified. Hardcoded paths must be updated. IDE workspace configurations may need updating.

---

## ADR-003: Flerken as Canonical Email Agent

- **Date:** 2026-05-26
- **Status:** Accepted
- **Context:** Five separate projects implement email automation (Flerken, email-summary-agent, Personal Automation, delivery-workbench email, Outlook Agent). Maintenance burden and confusion.
- **Decision:** Flerken is the surviving email agent. Others are archived or have unique logic ported into Flerken.
- **Consequences:** email-summary-agent and Personal Automation will be archived. delivery-workbench keeps non-email features. Outlook Agent workspace archived.

---

## ADR-004: serviceflow-sdm as Canonical Platform

- **Date:** 2026-05-26
- **Status:** Accepted
- **Context:** Three folders represent the ServiceFlow/Helix platform (ServiceFlow SDC, SDC_Windsurf, serviceflow-sdm). The full-stack version (serviceflow-sdm) has Docker, mobile, and real backend.
- **Decision:** serviceflow-sdm is the canonical platform repo. SDC variants are archived with unique assets ported.
- **Consequences:** Legacy HTML mockups preserved in _archived/ for reference. serviceflow-sdm README updated to note legacy assets.

---

## ADR-005: AgenticStarterKit and delivery-workbench Remain Separate

- **Date:** 2026-05-26
- **Status:** Accepted
- **Context:** Both projects were created from similar prompts on May 26, 2026. Risk of duplicate scaffolding.
- **Decision:** Keep both with distinct purposes. AgenticStarterKit = reusable template library. delivery-workbench = personal SDM operational workspace.
- **Consequences:** READMEs updated to clarify relationship. CodeGuard rules sourced from AgenticStarterKit. No structural merge.

---

## ADR-006: Copy-First Migration Strategy

- **Date:** 2026-05-26
- **Status:** Accepted
- **Context:** Moving 17 projects risks data loss if something goes wrong.
- **Decision:** All migrations use cp -R (copy), not mv (move). Originals are preserved until Windsurf reviews and operator approves cleanup.
- **Consequences:** Temporary disk space doubling. Explicit cleanup phase required after verification. No data loss risk.

---

## ADR-007: Shared Integration Layer Architecture

- **Date:** 2026-05-26
- **Status:** Proposed (Phase 3)
- **Context:** Multiple projects independently implement Salesforce, ServiceNow, Webex, and Microsoft Graph clients. Code duplication, inconsistent auth patterns, and maintenance burden.
- **Decision:** Build a shared integration layer with reusable API client modules that all projects consume.
- **Consequences:** Requires refactoring existing projects to use shared modules. Reduces duplication but introduces coupling. Must be versioned carefully.

---

## ADR-008: Sanitize Cursor History JSON Files Before Any Git Tracking

- **Date:** 2026-05-26
- **Status:** Accepted
- **Context:** Windsurf Architect review of `cursor-work-history-queries-appendix.json` and `cursor-work-history-analysis.json` revealed three plaintext credentials embedded in user prompts: an Airtable PAT, a Webex bot token fragment, and Microsoft Entra tenant/client IDs. These files are in the master folder and would be exposed if the folder is ever git-tracked or shared.
- **Decision:** (1) Both JSON files must be sanitized — replace credential values with `[REDACTED]` before any git init or sharing. (2) The Airtable PAT and Webex token must be rotated immediately regardless of sanitization. (3) Add both filenames to .gitignore as a safety net. (4) Future Cursor history exports should be reviewed by Windsurf before being placed in shared locations.
- **Consequences:** Loss of exact credential strings in the historical record (acceptable — they should never have been there). Rotation may temporarily break Airtable tracking and Webex bot delivery until new tokens are configured.

---

## ADR-009: Three-Tier Operating Model (Windsurf → Claude Reasoning → Cursor)

- **Date:** 2026-05-27
- **Status:** Accepted
- **Context:** V1 operating model was two-tier (Windsurf designs, Cursor builds). As the scope expanded to 34 AI Factory agents and customer automation, specs were being written without sufficient depth of reasoning. Complex integration decisions and agent logic need a structured reasoning pass before becoming Cursor instruction packets.
- **Decision:** Adopt a three-tier model: Tier 1 (Windsurf strategy), Tier 2 (Claude extended reasoning — trade-off analysis, spec validation, failure mode analysis), Tier 3 (Cursor implementation). Every P0/P1 backlog item runs through the 6-step Design Studio workflow before a Cursor task is created.
- **Consequences:** Windsurf sessions take slightly longer per item (30-45 min instead of 15-20 min for complex specs). Cursor tasks become more precise — fewer revision loops. Comms Bridge tasks are richer and include ADR references. V1 plan superseded by WINDSURF_ARCHITECT_PLAN_V2.md.

---

## ADR-010: Claude Model Routing Strategy

- **Date:** 2026-05-27
- **Status:** Accepted
- **Context:** Both IDEs defaulted to Claude Sonnet for all tasks. As AI agent complexity increased (orchestration loops, multi-API integrations, auth flows), the need for deeper reasoning on complex tasks was identified. Haiku is faster and cheaper for simple tasks.
- **Decision:** Route by task complexity: Claude Opus 4 for architectural reasoning, security review, and complex agent logic; Claude Sonnet 4.5 for standard implementation; Claude Haiku 3.5 for formatting, small edits, quick lookups. Cursor rule `claude-reasoning.md` enforces this.
- **Consequences:** Increased API cost for Opus-routed tasks (offset by fewer revision loops). All new Cursor sessions must declare task complexity before starting. Extended thinking activated for HIGH complexity tasks.

---

## ADR-011: Test-First Protocol for AI Factory Agent Builds

- **Date:** 2026-05-27
- **Status:** Accepted
- **Context:** V1 Cursor builds had no consistent testing discipline. Agents were submitted as working without verifiable test criteria. As the AI Factory scales to 34 agents, untested code creates compounding risk — especially for agents with trust tier T1 (full autonomy).
- **Decision:** All new agent functions, classes, and components require tests written before implementation. Minimum coverage: happy path, error path, auth failure, edge case. Cursor rule `test-first.md` enforces this. Skipping requires explicit Windsurf permission in the task spec.
- **Consequences:** Cursor build time per agent increases by ~20-30%. Quality gates now verifiable, not self-reported. Comms Bridge results must include test results section.

---

*New ADRs are appended as decisions are made. Each ADR is immutable once accepted — superseding decisions create new ADRs.*
