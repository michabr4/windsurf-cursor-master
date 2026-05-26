# Master Project Index

**Owner:** Windsurf (Architect)  
**Last Updated:** May 26, 2026  
**Purpose:** Single source of truth for all projects across Windsurf and Cursor

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
| **Location** | `~/Desktop/serviceflow-sdm/` |
| **Status** | ACTIVE |
| **Primary IDE** | Both (Cursor: mockup/UI, Windsurf: full-stack architecture) |
| **Stack** | Express/TypeScript, React/Vite, React Native/Expo, PostgreSQL |
| **Key Assets** | 22+ UI views, Docker deploy, SSO, Salesforce/ServiceNow/Cisco API integrations |
| **Related Folders** | `~/Desktop/SDM Files/ServiceFlow SDC/`, `~/Desktop/SDM Files/ServiceFlow SDC_Windsurf/` |
| **Overlap Risk** | HIGH — ServiceFlow SDC, SDC_Windsurf, and serviceflow-sdm are 3 variants of the same concept |
| **Next Action** | Consolidate into single repo; see CONSOLIDATION_PLAN.md |

### 2. SDM Files — Workspace & Agent Hub

| Field | Value |
| --- | --- |
| **Location** | `~/Desktop/SDM Files/` |
| **Status** | ACTIVE |
| **Primary IDE** | Both |
| **Contents** | status-report-agent, communication-agent, mgm-status-bot, SDM Agentic Framework, ServiceFlow SDC variants, Webex bot scripts, PPTX generator |
| **Key Concern** | Sprawling folder with mixed agents, scripts, and platform variants |
| **Next Action** | Extract agents to standalone repos; archive SDC variants |

### 3. Status Report Agent

| Field | Value |
| --- | --- |
| **Location** | `~/Desktop/SDM Files/status-report-agent/` |
| **Status** | STABLE |
| **Primary IDE** | Windsurf |
| **Stack** | Python, Pydantic, Azure OpenAI, Salesforce, ServiceNow |
| **Delivery** | GitHub Actions weekly cron |
| **Next Action** | Promote to standalone repo |

### 4. Communication Intelligence Agent

| Field | Value |
| --- | --- |
| **Location** | `~/Desktop/SDM Files/communication-agent/` |
| **Status** | STABLE |
| **Primary IDE** | Windsurf |
| **Stack** | Python, Pydantic, OpenAI/Anthropic, Webex API, Microsoft Graph |
| **Next Action** | Promote to standalone repo |

### 5. MGM Status Bot

| Field | Value |
| --- | --- |
| **Location** | `~/Desktop/SDM Files/mgm-status-bot/` |
| **Status** | ACTIVE (runs daily via GitHub Actions) |
| **Primary IDE** | Both (Cursor for debugging, Windsurf for core build) |
| **Stack** | Python, Webex Bot API, OpenAI, GitHub Actions |
| **Next Action** | Keep as standalone; verify GitHub Actions health |

### 6. Digitized Delivery Status Bot

| Field | Value |
| --- | --- |
| **Location** | `~/Desktop/Digitized Delivery/dd-status-bot/` |
| **Status** | ACTIVE (runs daily via GitHub Actions) |
| **Primary IDE** | Windsurf |
| **Stack** | Python, Webex SpaceLift, OpenAI, GitHub Actions |
| **Next Action** | Keep as standalone |

### 7. Flerken — Personal AI Assistant

| Field | Value |
| --- | --- |
| **Location** | `~/Desktop/Flerken - Personal AI Assistant/` |
| **Status** | STABLE |
| **Primary IDE** | Windsurf |
| **Stack** | Python, OpenAI GPT-4o, Microsoft Graph (device-code flow) |
| **Next Action** | Evaluate merge with delivery-workbench email capabilities |

### 8. Email Summary Agent

| Field | Value |
| --- | --- |
| **Location** | `~/Desktop/email-summary-agent/` |
| **Status** | STALE |
| **Primary IDE** | Windsurf |
| **Stack** | Python, OpenAI, Microsoft Graph |
| **Overlap Risk** | Overlaps with Flerken and delivery-workbench email assistant |
| **Next Action** | Archive or merge into Flerken |

### 9. Personal Automation — Email Digest

| Field | Value |
| --- | --- |
| **Location** | `~/Desktop/Personal Automation/` |
| **Status** | STALE |
| **Primary IDE** | Cursor (created in Apr 2026 session) |
| **Stack** | Python, Apple Mail parsing |
| **Overlap Risk** | Overlaps with Flerken, email-summary-agent |
| **Next Action** | Archive — superseded by Flerken |

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
| **Location** | `~/Desktop/AgenticStarterKitv1_0/` |
| **Status** | ACTIVE |
| **Primary IDE** | Both |
| **Stack** | Python, Node.js, HTML, multi-editor support |
| **Key Assets** | Starter templates, Webex/CIRCUIT/Asana samples, CodeGuard rules, docs |
| **Overlap Risk** | MEDIUM — overlaps with delivery-workbench in purpose |
| **Next Action** | See CONSOLIDATION_PLAN.md — pick north star |

### 13. Delivery Workbench

| Field | Value |
| --- | --- |
| **Location** | `~/Desktop/delivery-workbench/` |
| **Status** | ACTIVE (greenfield, May 26) |
| **Primary IDE** | Both (started in Cursor, continued in Windsurf) |
| **Stack** | Python, HTML, YAML orchestration |
| **Key Assets** | Playbooks, templates, email assistant, orchestration YAML |
| **Overlap Risk** | HIGH — overlaps AgenticStarterKit in intent |
| **Next Action** | See CONSOLIDATION_PLAN.md — pick north star |

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
| **Location** | `~/projects/Blue-Shield/` |
| **Status** | STALE |
| **Primary IDE** | Cursor only |
| **Stack** | Analysis/investigation (SpaceLift export parsing) |
| **Key Assets** | SHI payment reconciliation analysis, accountability trace |
| **Next Action** | Evaluate — archive or keep for reference |

### 16. Digitized Delivery — GES (Data)

| Field | Value |
| --- | --- |
| **Location** | `~/Desktop/Digitized Delivery - GES/` |
| **Status** | STABLE |
| **Primary IDE** | Cursor |
| **Stack** | Python (openpyxl), Excel, Airtable |
| **Key Assets** | `merge_parity_into_readiness.py`, merged workbook, Airtable Tracking subfolder |
| **Next Action** | Keep; ensure Airtable PAT is rotated |

### 17. Outlook Agent (Cursor)

| Field | Value |
| --- | --- |
| **Location** | `~/.cursor/Outlook Agent/` |
| **Status** | STALE |
| **Primary IDE** | Cursor only |
| **Next Action** | Evaluate — merge into Flerken or delivery-workbench |

---

## Overlap Map

```text
Email Automation Cluster:
  Flerken ←→ email-summary-agent ←→ Personal Automation ←→ delivery-workbench (email) ←→ Outlook Agent
  RECOMMENDATION: Consolidate into Flerken as the single email agent

Platform Cluster:
  serviceflow-sdm ←→ ServiceFlow SDC ←→ ServiceFlow SDC_Windsurf
  RECOMMENDATION: Consolidate into serviceflow-sdm; archive SDC variants

Starter/Workbench Cluster:
  AgenticStarterKitv1_0 ←→ delivery-workbench
  RECOMMENDATION: Pick one as north star; the other becomes a template library
```

---

## Security Action Items

| Item | Priority | Status |
| --- | --- | --- |
| Rotate Airtable PAT (exposed in Cursor chat May 8) | CRITICAL | PENDING |
| Sanitize cursor-work-history-queries-appendix.json (contains Airtable PAT, Webex token, Entra IDs in plaintext) | CRITICAL | PENDING |
| Sanitize cursor-work-history-analysis.json (contains Airtable PAT in session query) | CRITICAL | PENDING |
| Verify no secrets in any git-tracked files | HIGH | PENDING |
| Confirm .env files are gitignored across all repos | MEDIUM | PENDING |
| Review ~/Documents/GitHub/index workspace (untracked, found in Cursor metadata) | LOW | PENDING |
| Check ~/Desktop/Python/Test for content before archiving | LOW | PENDING |

---

*This document is maintained by Windsurf (Architect). All implementation instructions are issued via ROADMAP.md as Cursor-ready instruction packets.*
