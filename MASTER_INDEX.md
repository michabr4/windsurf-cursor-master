# Master Project Index

**Owner:** Windsurf (Architect)  
**Last Updated:** May 27, 2026  
**Purpose:** Single source of truth for all projects across Windsurf and Cursor

**Governing Documents (V2):**
- `WINDSURF_ARCHITECT_PLAN_V2.md` — Active operating model (supersedes V1)
- `CURSOR_UPGRADES_V2.md` — Cursor model routing, new rules, Anthropic MCP (additive to V1 setup)
- `AUTOMATION_BACKLOG.md` — Prioritized backlog (A: Customer, B: Platform, C: Internal, D: Infra)
- `AI_FACTORY_IMPLEMENTATION_PLAN.md` — 34-agent build pipeline
- `ADR_LOG.md` — Architecture decisions (ADR-001 through ADR-011)

---

## Operating Model

| Role | IDE | Responsibility |
| --- | --- | --- |
| **Architect** | Windsurf | Design, plan, organize, write specs, create Cursor instructions |
| **Builder** | Cursor | Code, execute, implement based on Windsurf specs |
| **Command Center** | This folder | `~/New Master Folder - Windsurf and Cursor/` |

---

## Project Registry

### Legend

| Status | Meaning |
| --- | --- |
| ACTIVE | Under active development |
| STABLE | Functional, not currently being iterated |
| STALE | Incomplete or abandoned — needs decision |
| ARCHIVE | Should be archived or folded into another project |

---

### 1. ServiceFlow SDM / Helix — Flagship Platform

| Field | Value |
| --- | --- |
| **Location** | `platforms/serviceflow-sdm/` (also `~/Desktop/serviceflow-sdm/`) |
| **Status** | ACTIVE — **canonical platform** |
| **Primary IDE** | Both |
| **Stack** | Express/TypeScript, React/Vite, React Native/Expo, PostgreSQL, Docker |
| **Key Assets** | Mockup hub, SSO, Salesforce/ServiceNow/Cisco integrations, legacy docs in `docs/legacy/` |
| **Archived variants** | `_archived/ServiceFlow-SDC/`, `_archived/ServiceFlow-SDC-Windsurf/` |
| **Overlap Risk** | LOW — consolidation complete (May 26 PLATFORM-CONSOLIDATE) |

### 2. SDM Files — Workspace & Agent Hub

| Field | Value |
| --- | --- |
| **Location** | `~/Desktop/SDM Files/` |
| **Status** | ACTIVE |
| **Primary IDE** | Both |
| **Contents** | status-report-agent, communication-agent, mgm-status-bot, SDM Agentic Framework, ServiceFlow SDC variants, Webex bot scripts, PPTX generator |
| **Key Concern** | Sprawling folder with mixed agents, scripts, and platform variants |
| **Next Action** | Utilities remain here; canonical agents live under `agents/` and `bots/` |

### 3. Status Report Agent

| Field | Value |
| --- | --- |
| **Location** | `agents/status-report-agent/` (also `~/Desktop/SDM Files/status-report-agent/`) |
| **Status** | STABLE |
| **Primary IDE** | Windsurf |
| **Stack** | Python, Pydantic, Azure OpenAI, Salesforce, ServiceNow |
| **Delivery** | GitHub Actions weekly cron |
| **Self-contained** | README, `requirements.txt`, `main.py` — verified May 26 |

### 4. Communication Intelligence Agent

| Field | Value |
| --- | --- |
| **Location** | `agents/communication-agent/` (also `~/Desktop/SDM Files/communication-agent/`) |
| **Status** | STABLE |
| **Primary IDE** | Windsurf |
| **Stack** | Python, Pydantic, OpenAI/Anthropic, Webex API, Microsoft Graph |
| **Self-contained** | README, `requirements.txt`, `main.py` — verified May 26 |

### 5. MGM Status Bot

| Field | Value |
| --- | --- |
| **Location** | `bots/mgm-status-bot/` (also `~/Desktop/SDM Files/mgm-status-bot/`) |
| **Status** | ACTIVE (runs daily via GitHub Actions) |
| **Primary IDE** | Both |
| **Stack** | Python, Webex Bot API, OpenAI, GitHub Actions |
| **Self-contained** | README, `requirements.txt`, `send_reports.py` — verified May 26 |

### 6. Digitized Delivery Status Bot

| Field | Value |
| --- | --- |
| **Location** | `bots/dd-status-bot/` (also `~/Desktop/Digitized Delivery/dd-status-bot/`) |
| **Status** | ACTIVE (runs daily via GitHub Actions) |
| **Primary IDE** | Windsurf |
| **Stack** | Python, Webex SpaceLift, OpenAI, GitHub Actions |
| **Self-contained** | README, `requirements.txt` (added May 26), `send_reports.py` |

### 7. Forge — Personal AI Assistant

| Field | Value |
| --- | --- |
| **Location** | `agents/forge/` (also `~/Desktop/Forge - Personal AI Assistant/`) |
| **Status** | ACTIVE — canonical email agent |
| **Primary IDE** | Both |
| **Stack** | Python, LLM (OpenAI/Ollama), Microsoft Graph (device-code flow), HTML digest |
| **Consolidated** | email-summary-agent, personal-automation (offline digest); workbench YAML reference in `docs/orchestration_reference/` |
| **Next Action** | Optional: wire morning-readonly mode from orchestration reference |

### 8. Email Summary Agent

| Field | Value |
| --- | --- |
| **Location** | `_archived/email-summary-agent/` |
| **Status** | ARCHIVE |
| **Primary IDE** | — |
| **Stack** | Python, OpenAI, Microsoft Graph |
| **Next Action** | None — superseded by Forge (May 26 EMAIL-CONSOLIDATE) |

### 9. Personal Automation — Email Digest

| Field | Value |
| --- | --- |
| **Location** | `_archived/personal-automation/` |
| **Status** | ARCHIVE |
| **Primary IDE** | — |
| **Stack** | Python, Apple Mail export parsing |
| **Next Action** | Use Forge `run.py --offline-mail` for offline digest |

### 10. NetPilot — Network Automation Platform

| Field | Value |
| --- | --- |
| **Location** | `~/Desktop/NetPilot/` |
| **Status** | ACTIVE |
| **Primary IDE** | Windsurf |
| **Stack** | Python, React/JSX, FastAPI, YAML, SQL |
| **Key Assets** | CCNA Automation App, ALE Lab Module, AREX Remediation, PTE Model, architecture docs through v5.0 |
| **Next Action** | Continue development; standalone repo |

### 11. AI Factory — CX Transformation Playbook

| Field | Value |
| --- | --- |
| **Location** | `~/Desktop/AI Factory/` |
| **Status** | STABLE |
| **Primary IDE** | Windsurf |
| **Stack** | HTML, Tailwind CSS, Alpine.js |
| **Key Assets** | Framework page, Vibe Coding 101 tutorial, Email Agent tutorial |
| **Next Action** | Keep as presentation asset; no consolidation needed |

### 12. Agentic Starter Kit v1.0

| Field | Value |
| --- | --- |
| **Location** | `tools/agentic-starter-kit/` (also `~/Desktop/AgenticStarterKitv1_0/`) |
| **Status** | ACTIVE |
| **Primary IDE** | Both |
| **Stack** | Python, Node.js, HTML, multi-editor support |
| **Purpose** | **Shareable template** — samples, CodeGuard rules, docs, comms-bridge MCP scaffold |
| **Key Assets** | Starter templates, Webex/CIRCUIT/Asana samples, CodeGuard rules, `mcp-servers/comms-bridge-mcp/` |
| **Overlap Risk** | LOW — boundaries clarified with delivery-workbench (May 26 split) |
| **Next Action** | Keep generic; avoid project-specific data in this tree |

### 13. Delivery Workbench

| Field | Value |
| --- | --- |
| **Location** | `tools/delivery-workbench/` (also `~/Desktop/delivery-workbench/`) |
| **Status** | ACTIVE |
| **Primary IDE** | Both |
| **Stack** | Python, HTML, YAML orchestration |
| **Purpose** | **Operational daily-driver** — playbooks, email assistant, AGT-001 integrations, project outputs |
| **Key Assets** | Playbooks, templates, email orchestration, `python/integrations/agt001/`, `docs/reference/` |
| **Overlap Risk** | LOW — uses starter kit as template source, not duplicate scaffold |
| **Next Action** | Continue SDM workflows; operational data stays under `data/` |

### 14. Firewall Implementation Planning

| Field | Value |
| --- | --- |
| **Location** | `~/firewall-implementation-planning/` |
| **Status** | STABLE |
| **Primary IDE** | Both (plan created in Cursor, repo structured in Windsurf) |
| **Stack** | Markdown, MS Project XML, Python, PowerShell |
| **Key Assets** | Executive migration plan, actionable project plan, conversion scripts |
| **Next Action** | Keep as-is; standalone deliverable |

### 15. Blue Shield

| Field | Value |
| --- | --- |
| **Location** | `data/blue-shield/` (reference; also `~/projects/Blue-Shield/` if present) |
| **Status** | STALE |
| **Primary IDE** | Cursor only |
| **Stack** | Analysis/investigation (SpaceLift export parsing) |
| **Key Assets** | SHI payment reconciliation analysis, accountability trace |
| **Next Action** | Evaluate — archive or keep for reference |

### 16. Digitized Delivery — GES (Data)

| Field | Value |
| --- | --- |
| **Location** | `data/digitized-delivery-ges/` (also `~/Desktop/Digitized Delivery - GES/`) |
| **Status** | STABLE |
| **Primary IDE** | Cursor |
| **Stack** | Python (openpyxl), Excel, Airtable |
| **Key Assets** | `merge_parity_into_readiness.py`, merged workbook, Airtable Tracking subfolder |
| **Next Action** | Keep; ensure Airtable PAT is rotated |

### 17. Outlook Agent (Cursor)

| Field | Value |
| --- | --- |
| **Location** | `_archived/outlook-agent/` (empty shell; was `~/.cursor/Outlook Agent/`) |
| **Status** | ARCHIVE |
| **Primary IDE** | — |
| **Next Action** | None — superseded by Forge (May 26 ARCHIVE-STALE) |

---

## Overlap Map

```text
Email Automation Cluster:
  Forge (canonical) ← delivery-workbench (orchestration YAML, kept)
  ARCHIVED: email-summary-agent, personal-automation → _archived/
  ARCHIVED: Outlook Agent → _archived/outlook-agent/

Platform Cluster:
  serviceflow-sdm (canonical) ← archived: ServiceFlow-SDC, ServiceFlow-SDC-Windsurf in _archived/
  RESOLVED (May 26): Legacy docs in platforms/serviceflow-sdm/docs/legacy/

Starter/Workbench Cluster:
  agentic-starter-kit (template) ←→ delivery-workbench (operational)
  RESOLVED (May 26): Starter kit = shareable template; workbench = personal SDM workspace
```

---

## Security Action Items

| Item | Priority | Status | Audited |
| --- | --- | --- | --- |
| Rotate Airtable PAT (exposed in Cursor chat May 8) | CRITICAL | ACCEPTED RISK — live PAT in `data/digitized-delivery-ges/Airtable Tracking/.env`, gitignored | May 26 |
| Sanitize cursor-work-history-queries-appendix.json | CRITICAL | RESOLVED — secrets already redacted by Cursor (`[REDACTED_AIRTABLE_PAT]`, `[REDACTED — Webex bot token]`, `[REDACTED — MS Entra Client ID]`). Remaining UUIDs are public session/app IDs. | May 26 |
| Sanitize cursor-work-history-analysis.json | CRITICAL | RESOLVED — no live secrets found; Airtable mentions are category labels only | May 26 |
| Verify no secrets in any git-tracked files | HIGH | RESOLVED — grep audit clean; .env files not tracked; history files pre-redacted | May 26 |
| Confirm .env files are gitignored across all repos | MEDIUM | RESOLVED — `.gitignore` covers `.env`, `.env.*`, `!.env.example` | May 26 |
| Asana client secret + webhook secret in `tools/agentic-starter-kit/.env` | HIGH | ACCEPTED RISK — live values on disk, gitignored | May 26 |
| Review ~/Documents/GitHub/index workspace (untracked, found in Cursor metadata) | LOW | PENDING | — |
| Check ~/Desktop/Python/Test for content before archiving | LOW | RESOLVED — archived as `_archived/desktop-python-2026/` | May 26 |

---

*This document is maintained by Windsurf (Architect). All implementation instructions are issued via ROADMAP.md as Cursor-ready instruction packets.*
