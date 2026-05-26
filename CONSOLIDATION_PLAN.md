# Consolidation Plan

**Owner:** Windsurf (Architect)  
**Last Updated:** May 26, 2026  
**Purpose:** Reduce project sprawl by merging overlapping work into clean, purposeful repos

---

## Guiding Principles

1. **One project, one purpose** — eliminate duplicate scaffolds
2. **Preserve all working code** — archive, don't delete
3. **Cursor executes** — each consolidation below includes a Cursor instruction packet
4. **Security first** — consolidation is a chance to audit secrets

---

## Consolidation 1: Email Automation Cluster

### Problem

Five separate projects do variations of "read my email and extract value":

| Project | What it does | Status |
| --- | --- | --- |
| Flerken | Full triage + digest via GPT-4o + Graph API | STABLE, most complete |
| email-summary-agent | CLI email summary | STALE, subset of Flerken |
| Personal Automation | Apple Mail parser + regex priority | STALE, offline only |
| delivery-workbench (email) | M365 email orchestration YAML | ACTIVE, partial |
| Outlook Agent (.cursor) | Cursor-only exploration | STALE |

### Decision

**Winner: Flerken** — it has the most complete architecture (Graph API, GPT-4o, HTML digest, device-code auth).

### Cursor Instruction Packet: EMAIL-CONSOLIDATE

```text
TASK: Consolidate email automation into Flerken
CONTEXT: Flerken at ~/Desktop/Flerken - Personal AI Assistant/ is the surviving email agent.

STEPS:
1. From ~/Desktop/email-summary-agent/:
   - Review summarizer.py and email_reader.py for any logic not in Flerken
   - If unique logic exists, port it into Flerken's src/ as optional modules
   - Copy nothing if Flerken already covers the functionality

2. From ~/Desktop/Personal Automation/:
   - Review email_digest.py regex priority patterns
   - If Flerken lacks offline/Apple Mail support and we want it, add as src/offline_parser.py
   - Otherwise skip — this is a legacy approach

3. From ~/Desktop/delivery-workbench/docs/email/:
   - Review orchestration YAML (email-inbox-review.yaml, email-morning-digest.yaml)
   - If these add orchestration patterns Flerken lacks, port the YAML concept
   - Do NOT move delivery-workbench's core structure — only email-specific assets

4. Archive completed sources:
   - Create ~/Desktop/_archived/
   - Move email-summary-agent/ and Personal Automation/ into _archived/
   - Leave delivery-workbench intact (it has non-email purposes)

5. Update Flerken's README.md to reflect any new capabilities added

CONSTRAINTS:
- Do NOT modify .env files or create new API keys
- Do NOT delete anything — only move to _archived/
- Commit message format: "consolidate: merge [source] email logic into Flerken"
```

---

## Consolidation 2: ServiceFlow Platform Cluster

### Problem: Platform Fragmentation

Three folders represent different generations of the same platform:

| Project | What it is | Status |
| --- | --- | --- |
| `~/Desktop/SDM Files/ServiceFlow SDC/` | Original HTML+CSS+JS mockup | STALE, superseded |
| `~/Desktop/SDM Files/ServiceFlow SDC_Windsurf/` | Windsurf iteration of SDC | STALE, superseded |
| `~/Desktop/serviceflow-sdm/` | Full-stack (Express/React/Expo/Docker) | ACTIVE, canonical |

### Decision: Canonical Repo

**Winner: serviceflow-sdm** — it has the full-stack architecture, Docker deployment, and mobile app.

### Cursor Instruction Packet: PLATFORM-CONSOLIDATE

```text
TASK: Consolidate ServiceFlow variants into serviceflow-sdm
CONTEXT: ~/Desktop/serviceflow-sdm/ is the canonical platform repo.

STEPS:
1. Inventory unique assets in ServiceFlow SDC/:
   - Check mockup HTML/CSS/JS files for any UI views NOT already in serviceflow-sdm
   - Check CISCO_DATA_SOURCES.md, MVP_SCOPE_FREEZE.md for content not in serviceflow-sdm/docs/
   - List findings before making changes (report back to user)

2. Inventory unique assets in ServiceFlow SDC_Windsurf/:
   - Same check as above
   - This is likely a subset of serviceflow-sdm — confirm

3. Port any unique assets:
   - Copy unique docs to serviceflow-sdm/docs/legacy/
   - Copy unique mockup HTML to serviceflow-sdm/frontend/public/legacy-mockup/

4. Archive:
   - Move ~/Desktop/SDM Files/ServiceFlow SDC/ to ~/Desktop/_archived/ServiceFlow SDC/
   - Move ~/Desktop/SDM Files/ServiceFlow SDC_Windsurf/ to ~/Desktop/_archived/ServiceFlow SDC_Windsurf/

5. Update serviceflow-sdm/README.md with a note about legacy mockup assets

CONSTRAINTS:
- Do NOT modify serviceflow-sdm's working code
- Archive only — never delete
- Commit message: "consolidate: archive legacy SDC variants, port unique assets"
```

---

## Consolidation 3: Starter Kit vs Delivery Workbench

### Problem: Duplicate Scaffolds

Both projects were born on May 26 from the same prompt ("build a local IDE for SDM with security guardrails"):

| Project | What it is | Status |
| --- | --- | --- |
| AgenticStarterKitv1_0 | Multi-editor template with samples, docs, CodeGuard | ACTIVE |
| delivery-workbench | Playbook-driven SDM workspace with email assistant | ACTIVE |

### Decision: Keep Both with Clear Boundaries

**Keep both, but with distinct purposes:**

- **AgenticStarterKit** = **Template library** (reusable starters, samples, CodeGuard rules for any project)
- **delivery-workbench** = **Operational workspace** (your personal daily-driver for SDM work)

### Cursor Instruction Packet: STARTER-WORKBENCH-SPLIT

```text
TASK: Clarify boundaries between AgenticStarterKit and delivery-workbench
CONTEXT: Both exist and should remain, but with distinct roles.

STEPS:
1. In AgenticStarterKitv1_0/README.md:
   - Add a section "Relationship to delivery-workbench" explaining:
     "This kit provides reusable templates and security rules.
      For your personal SDM operational workspace, see delivery-workbench."

2. In delivery-workbench/README.md:
   - Add a section "Relationship to AgenticStarterKit" explaining:
     "This workbench is your daily-driver SDM workspace.
      For reusable starter templates and CodeGuard rules, see AgenticStarterKitv1_0."

3. Ensure CodeGuard rules are symlinked or copied consistently:
   - AgenticStarterKit should be the SOURCE of CodeGuard rules
   - delivery-workbench should reference or copy from AgenticStarterKit

4. Do NOT merge the repos — they serve different audiences

CONSTRAINTS:
- README edits only — no structural changes
- Commit messages: "docs: clarify relationship with [other project]"
```

---

## Consolidation 4: Agent Extraction from SDM Files

### Problem: Sprawling Folder

`~/Desktop/SDM Files/` is a sprawling folder mixing agents, bots, scripts, and platform variants.

### Decision: Promote to Standalone

Agents that are functional should become standalone repos. Scripts and one-offs stay.

### Cursor Instruction Packet: AGENT-EXTRACTION

```text
TASK: Promote agents from SDM Files to standalone project folders
CONTEXT: ~/Desktop/SDM Files/ contains multiple agents mixed with other files.

STEPS:
1. Verify these are already self-contained with their own README, requirements.txt, etc.:
   - status-report-agent/
   - communication-agent/
   - mgm-status-bot/

2. If self-contained, COPY (not move) each to ~/Desktop/:
   - ~/Desktop/status-report-agent/
   - ~/Desktop/communication-agent/
   - Keep mgm-status-bot in SDM Files (it's already a GitHub repo)

3. Leave originals in SDM Files for now (we'll clean up after verifying copies work)

4. For remaining SDM Files items:
   - Service Delivery Manager Agentic Framework/ — keep as parent framework doc
   - webex_bot.py, webex_bot_server.py, etc. — keep as utility scripts
   - generate_mgm_pptx.py — keep as utility

CONSTRAINTS:
- COPY, don't move (preserve originals until verified)
- No code changes — just file organization
- Report back: list what was copied and what stayed
```

---

## Consolidation 5: Archive Stale Projects

### Cursor Instruction Packet: ARCHIVE-STALE

```text
TASK: Archive stale and superseded projects
CONTEXT: Several projects are no longer active and have been superseded.

STEPS:
1. Create ~/Desktop/_archived/ if it doesn't exist

2. Move the following into _archived/:
   - ~/Desktop/Python/Email App/ (empty directory)
   - ~/Desktop/Python/Asana/ (empty directory)
   - ~/.cursor/Outlook Agent/ (if any files exist; Cursor-only exploration)

3. Do NOT archive:
   - Blue Shield (keep for reference — has SHI analysis)
   - Digitized Delivery - GES (active data, Airtable tracking)

4. For ~/Desktop/Python/ — if only empty subdirs remain after archiving, archive the whole folder

CONSTRAINTS:
- Move only — never delete
- Create a file ~/Desktop/_archived/ARCHIVE_LOG.md listing what was archived and when
```

---

## Execution Order

| Priority | Consolidation | Risk | Effort |
| --- | --- | --- | --- |
| 1 | Archive Stale (C5) | LOW | 10 min |
| 2 | Starter/Workbench Split (C3) | LOW | 15 min |
| 3 | Agent Extraction (C4) | LOW | 20 min |
| 4 | Email Consolidation (C1) | MEDIUM | 30 min |
| 5 | Platform Consolidation (C2) | MEDIUM | 45 min |

---

## Security Audit (During Consolidation)

During each consolidation, Cursor should also:

1. Verify `.gitignore` includes `.env`, `*.pem`, `*.key`, `token*`
2. Run `grep -r "AKIA\|sk_live\|ghp_\|pat[A-Z]" .` in each repo to check for leaked secrets
3. Confirm no `.env` files are git-tracked
4. Report any findings before committing

---

*This plan is maintained by Windsurf (Architect). Hand each Cursor Instruction Packet to Cursor for execution.*
