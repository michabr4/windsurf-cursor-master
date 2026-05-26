# Cursor Instructions: Full Project Migration

**Issued by:** Windsurf (Architect)  
**Date:** May 26, 2026  
**Purpose:** Migrate all projects into `~/New Master Folder - Windsurf and Cursor/` with a structured mono-repo layout

---

## Important: Read Before Executing

### Your Role

You are the **Builder**. Windsurf is the **Architect**. You execute these instructions section by section. You do NOT proceed to the next section until Windsurf has reviewed and approved your work.

### Rules (Follow Without Exception)

1. Execute steps **in order** — later steps depend on earlier ones
2. **After completing each section**, create a documentation entry in `MIGRATION_LOG.md` (in this folder) recording:
   - Section number and name
   - Timestamp
   - Every action taken (commands run, files copied, errors encountered)
   - Final status: SUCCESS / PARTIAL / FAILED
   - Any items that need Windsurf review
3. **STOP after each section** — do NOT proceed to the next section until the user confirms that Windsurf has reviewed and approved. The user will say "Windsurf approved, proceed" or similar.
4. **Never delete originals** until migration is fully verified and Windsurf approves cleanup
5. If a step fails, **stop and report** — do not attempt to fix without consulting
6. If you are uncertain about anything, **ask before acting**

### Migration Log Format

After Section 1, create `MIGRATION_LOG.md` in this folder with this structure:

```markdown
# Migration Log

**Migration started:** [timestamp]
**Architect:** Windsurf
**Builder:** Cursor

---

## Section 1: Create Directory Structure
**Completed:** [timestamp]
**Status:** [SUCCESS/PARTIAL/FAILED]

### Actions Taken
- [list every command run and its result]

### Issues Found
- [list any issues, or "None"]

### Awaiting Windsurf Review
- [list items needing review, or "None"]

---
```

Append a new section entry after completing each subsequent section.

---

## Target Structure

```text
~/New Master Folder - Windsurf and Cursor/
├── README.md                          # Repo overview + navigation
├── MASTER_INDEX.md                    # Project registry (Windsurf maintains)
├── CONSOLIDATION_PLAN.md              # Consolidation specs
├── ROADMAP.md                         # Strategic roadmap
├── CURSOR_INSTRUCTIONS_MIGRATION.md   # This file
├── Windsurf_Work_Analysis_Report.md   # Windsurf history
├── CURSOR-WORK-HISTORY-FULL-ANALYSIS.md  # Cursor history
├── cursor-work-history-report.md      # Cursor summary
│
├── platforms/
│   └── serviceflow-sdm/               # Helix — flagship platform
│
├── agents/
│   ├── status-report-agent/            # Salesforce/ServiceNow weekly reports
│   ├── communication-agent/            # Webex/Email action item extraction
│   ├── flerken/                        # Personal email triage + digest
│   └── email-summary-agent/            # CLI email summary (archive candidate)
│
├── bots/
│   ├── mgm-status-bot/                 # MGM daily Webex status bot
│   └── dd-status-bot/                  # Digitized Delivery daily status bot
│
├── tools/
│   ├── netpilot/                       # Network automation platform
│   ├── firewall-implementation-planning/  # MGM Palo→Cisco migration
│   ├── delivery-workbench/             # SDM daily-driver workspace
│   ├── agentic-starter-kit/            # Reusable templates + CodeGuard
│   └── personal-automation/            # Legacy email digest (archive candidate)
│
├── content/
│   └── ai-factory/                     # CX Transformation Playbook + tutorials
│
├── data/
│   ├── digitized-delivery-ges/         # NaC/SaC Excel consolidation + Airtable
│   └── blue-shield/                    # SHI payment analysis
│
├── sdm-files/                          # Remaining SDM utility scripts + framework docs
│   ├── webex_bot.py
│   ├── webex_bot_server.py
│   ├── webex_bot_scheduler.py
│   ├── send_subscription_card.py
│   ├── generate_mgm_pptx.py
│   ├── setup_daily_schedule.sh
│   └── sdm-agentic-framework/         # Framework README + docs
│
├── _archived/                          # Superseded / stale projects
│   ├── ServiceFlow-SDC/                # Original HTML mockup (superseded)
│   ├── ServiceFlow-SDC-Windsurf/       # Windsurf SDC iteration (superseded)
│   ├── outlook-agent/                  # Cursor-only exploration
│   ├── python-empty/                   # Empty Python/Email App/Asana dirs
│   └── ARCHIVE_LOG.md                  # What was archived and when
│
└── .windsurf/                          # Windsurf config (already exists)
    └── rules/                          # CodeGuard security rules
```

---

## Section 1: Create Directory Structure

```text
TASK: Create the target directory structure inside the master folder.

STEPS:
1. Navigate to: ~/New Master Folder - Windsurf and Cursor/

2. Create these directories (mkdir -p):
   - platforms/
   - agents/
   - bots/
   - tools/
   - content/
   - data/
   - sdm-files/
   - _archived/

3. Verify all directories exist with: ls -la

REPORT BACK: Confirm all directories were created.

THEN:
1. Create MIGRATION_LOG.md with Section 1 entry (see format above)
2. STOP — wait for user to confirm Windsurf has reviewed before proceeding to Section 2
```

---

## Section 2: Migrate Platforms

```text
TASK: Move the ServiceFlow SDM platform into platforms/

STEPS:
1. Move the canonical platform:
   cp -R ~/Desktop/serviceflow-sdm/ "~/New Master Folder - Windsurf and Cursor/platforms/serviceflow-sdm/"

   IMPORTANT: Use cp -R first (copy, not move). We verify before removing originals.

2. EXCLUDE from the copy (delete after copy to save space):
   - platforms/serviceflow-sdm/node_modules/  (can be reinstalled)
   - platforms/serviceflow-sdm/frontend/node_modules/
   - platforms/serviceflow-sdm/backend/node_modules/
   - platforms/serviceflow-sdm/mobile/node_modules/

   Run: find "platforms/serviceflow-sdm" -name "node_modules" -type d -exec rm -rf {} +

3. Verify the copy:
   - Check that README.md, docker-compose.yml, package.json exist
   - Check that frontend/, backend/, mobile/, docs/ directories exist
   - Run: diff -rq ~/Desktop/serviceflow-sdm/ platforms/serviceflow-sdm/ --exclude=node_modules --exclude=.git

4. Archive the legacy SDC variants:
   cp -R ~/Desktop/SDM\ Files/ServiceFlow\ SDC/ "_archived/ServiceFlow-SDC/"
   cp -R ~/Desktop/SDM\ Files/ServiceFlow\ SDC_Windsurf/ "_archived/ServiceFlow-SDC-Windsurf/"

REPORT BACK: List files in platforms/serviceflow-sdm/ (top level) and confirm SDC variants are archived.

THEN:
1. Append Section 2 entry to MIGRATION_LOG.md
2. STOP — wait for Windsurf review before proceeding to Section 3
```

---

## Section 3: Migrate Agents

```text
TASK: Copy all agent projects into agents/

STEPS:
1. Status Report Agent:
   cp -R ~/Desktop/SDM\ Files/status-report-agent/ agents/status-report-agent/

2. Communication Agent:
   cp -R ~/Desktop/SDM\ Files/communication-agent/ agents/communication-agent/

3. Flerken:
   cp -R ~/Desktop/Flerken\ -\ Personal\ AI\ Assistant/ agents/flerken/

4. Email Summary Agent:
   cp -R ~/Desktop/email-summary-agent/ agents/email-summary-agent/

5. For each agent directory, remove virtual environments to save space:
   find agents/ -name "venv" -type d -exec rm -rf {} +
   find agents/ -name ".venv" -type d -exec rm -rf {} +
   find agents/ -name "__pycache__" -type d -exec rm -rf {} +

6. Verify each has its README.md and requirements.txt:
   for d in agents/*/; do echo "=== $d ==="; ls "$d"README.md "$d"requirements.txt 2>/dev/null || echo "MISSING"; done

REPORT BACK: List each agent directory with file count and confirm key files present.

THEN:
1. Append Section 3 entry to MIGRATION_LOG.md
2. STOP — wait for Windsurf review before proceeding to Section 4
```

---

## Section 4: Migrate Bots

```text
TASK: Copy bot projects into bots/

STEPS:
1. MGM Status Bot:
   cp -R ~/Desktop/SDM\ Files/mgm-status-bot/ bots/mgm-status-bot/

2. DD Status Bot:
   cp -R ~/Desktop/Digitized\ Delivery/dd-status-bot/ bots/dd-status-bot/

3. Clean up:
   find bots/ -name "venv" -type d -exec rm -rf {} +
   find bots/ -name "__pycache__" -type d -exec rm -rf {} +

4. CRITICAL: These bots have GitHub Actions. Verify .github/workflows/ exists in each:
   ls bots/mgm-status-bot/.github/workflows/
   ls bots/dd-status-bot/.github/workflows/

5. Note: The GitHub remote origin still points to the original repo paths.
   These will continue to work since git remotes are URL-based, not path-based.
   But verify: cd bots/mgm-status-bot && git remote -v && cd ../..

REPORT BACK: Confirm both bots copied with workflows intact. Show git remote -v output for each.

THEN:
1. Append Section 4 entry to MIGRATION_LOG.md
2. STOP — wait for Windsurf review before proceeding to Section 5
```

---

## Section 5: Migrate Tools

```text
TASK: Copy tool projects into tools/

STEPS:
1. NetPilot:
   cp -R ~/Desktop/NetPilot/ tools/netpilot/
   find tools/netpilot -name "node_modules" -type d -exec rm -rf {} +
   find tools/netpilot -name ".venv" -type d -exec rm -rf {} +

2. Firewall Implementation Planning:
   cp -R ~/firewall-implementation-planning/ tools/firewall-implementation-planning/

3. Delivery Workbench:
   cp -R ~/Desktop/delivery-workbench/ tools/delivery-workbench/
   find tools/delivery-workbench -name "venv" -type d -exec rm -rf {} +

4. Agentic Starter Kit:
   cp -R ~/Desktop/AgenticStarterKitv1_0/ tools/agentic-starter-kit/
   find tools/agentic-starter-kit -name "node_modules" -type d -exec rm -rf {} +
   find tools/agentic-starter-kit -name "venv" -type d -exec rm -rf {} +

5. Personal Automation (archive candidate but still moving):
   cp -R ~/Desktop/Personal\ Automation/ tools/personal-automation/

6. Verify each:
   for d in tools/*/; do echo "=== $d ==="; ls "$d"README.md 2>/dev/null || echo "NO README"; done

REPORT BACK: List each tool directory and confirm README present.

THEN:
1. Append Section 5 entry to MIGRATION_LOG.md
2. STOP — wait for Windsurf review before proceeding to Section 6
```

---

## Section 6: Migrate Content

```text
TASK: Copy content projects into content/

STEPS:
1. AI Factory:
   cp -R ~/Desktop/AI\ Factory/ content/ai-factory/

2. Verify key files:
   ls content/ai-factory/index.html
   ls content/ai-factory/vibe-coding-101.html
   ls content/ai-factory/tutorial-email-agent.html

REPORT BACK: Confirm all HTML files present.

THEN:
1. Append Section 6 entry to MIGRATION_LOG.md
2. STOP — wait for Windsurf review before proceeding to Section 7
```

---

## Section 7: Migrate Data Projects

```text
TASK: Copy data/analysis projects into data/

STEPS:
1. Digitized Delivery GES:
   cp -R ~/Desktop/Digitized\ Delivery\ -\ GES/ data/digitized-delivery-ges/

2. Blue Shield:
   cp -R ~/projects/Blue-Shield/ data/blue-shield/

3. Verify:
   ls data/digitized-delivery-ges/
   ls data/blue-shield/

REPORT BACK: Confirm both data directories populated.

THEN:
1. Append Section 7 entry to MIGRATION_LOG.md
2. STOP — wait for Windsurf review before proceeding to Section 8
```

---

## Section 8: Migrate SDM Utility Scripts

```text
TASK: Copy remaining SDM Files utility scripts into sdm-files/

STEPS:
1. Copy individual utility files (not subdirectories already migrated):
   cp ~/Desktop/SDM\ Files/webex_bot.py sdm-files/
   cp ~/Desktop/SDM\ Files/webex_bot_server.py sdm-files/
   cp ~/Desktop/SDM\ Files/webex_bot_scheduler.py sdm-files/
   cp ~/Desktop/SDM\ Files/send_subscription_card.py sdm-files/
   cp ~/Desktop/SDM\ Files/generate_mgm_pptx.py sdm-files/
   cp ~/Desktop/SDM\ Files/setup_daily_schedule.sh sdm-files/

2. Copy the SDM Agentic Framework:
   cp -R ~/Desktop/SDM\ Files/Service\ Delivery\ Manager\ Agentic\ Framework/ sdm-files/sdm-agentic-framework/

3. Check for any other files in SDM Files root we missed:
   ls ~/Desktop/SDM\ Files/*.py ~/Desktop/SDM\ Files/*.sh ~/Desktop/SDM\ Files/*.md 2>/dev/null

   If there are files not already copied, copy them to sdm-files/

REPORT BACK: List all files in sdm-files/ and flag anything we missed from the source.

THEN:
1. Append Section 8 entry to MIGRATION_LOG.md
2. STOP — wait for Windsurf review before proceeding to Section 9
```

---

## Section 9: Archive Stale Items

```text
TASK: Archive superseded and empty projects

STEPS:
1. ServiceFlow SDC variants (already done in Section 2 — verify):
   ls _archived/ServiceFlow-SDC/
   ls _archived/ServiceFlow-SDC-Windsurf/

2. Empty Python directories:
   mkdir -p _archived/python-empty/
   cp -R ~/Desktop/Python/ _archived/python-empty/ 2>/dev/null || echo "Already empty"

3. Outlook Agent (if exists):
   if [ -d ~/.cursor/Outlook\ Agent ]; then
     cp -R ~/.cursor/Outlook\ Agent/ _archived/outlook-agent/
   fi

4. Create archive log:
   Create file: _archived/ARCHIVE_LOG.md with content:

   # Archive Log
   **Date:** May 26, 2026

   | Item | Original Location | Reason |
   | --- | --- | --- |
   | ServiceFlow-SDC | ~/Desktop/SDM Files/ServiceFlow SDC/ | Superseded by serviceflow-sdm |
   | ServiceFlow-SDC-Windsurf | ~/Desktop/SDM Files/ServiceFlow SDC_Windsurf/ | Superseded by serviceflow-sdm |
   | python-empty | ~/Desktop/Python/ | Empty placeholder directories |
   | outlook-agent | ~/.cursor/Outlook Agent/ | Cursor-only exploration, superseded by Flerken |

REPORT BACK: Confirm archive log created and all items present.

THEN:
1. Append Section 9 entry to MIGRATION_LOG.md
2. STOP — wait for Windsurf review before proceeding to Section 10
```

---

## Section 10: Post-Migration Fixups

```text
TASK: Fix paths, verify git remotes, and scan for security issues

STEPS:
1. FIX HARDCODED PATHS:
   Search all migrated files for old absolute paths:
   grep -r "/Users/michabr4/Desktop/" . --include="*.py" --include="*.sh" --include="*.md" --include="*.yml" --include="*.yaml" -l

   For each file found:
   - If it's a README/doc, update the path references
   - If it's a script, update the path
   - If it's a git workflow (GitHub Actions), leave it alone (runs on GitHub, not local)

2. FIX FIREWALL PLANNING SCRIPT:
   The file tools/firewall-implementation-planning/setup-git.sh has hardcoded:
     cd /Users/michabr4/firewall-implementation-planning
   Update to use relative paths or $(dirname "$0")

3. VERIFY GIT REMOTES (for projects with GitHub repos):
   for d in bots/mgm-status-bot bots/dd-status-bot platforms/serviceflow-sdm; do
     echo "=== $d ==="
     cd "$d" && git remote -v && cd ../../..
   done

   Git remotes are URL-based so they should still work. Confirm.

4. SECURITY SCAN:
   grep -r "AKIA\|sk_live\|ghp_\|gho_\|pat[A-Z]\|-----BEGIN" . \
     --include="*.py" --include="*.js" --include="*.ts" --include="*.md" \
     --include="*.json" --include="*.yml" --include="*.yaml" \
     --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=venv -l

   Report ANY files found — these may contain leaked secrets.

5. VERIFY .env FILES ARE NOT TRACKED:
   find . -name ".env" -not -path "./.git/*" | while read f; do
     dir=$(dirname "$f")
     if [ -f "$dir/.gitignore" ]; then
       grep -q ".env" "$dir/.gitignore" && echo "OK: $f (gitignored)" || echo "WARNING: $f NOT gitignored"
     else
       echo "WARNING: $f has no .gitignore in parent"
     fi
   done

6. ROTATE AIRTABLE PAT:
   - Check if data/digitized-delivery-ges/Airtable Tracking/.env exists
   - If it contains an Airtable PAT, note it for rotation (DO NOT print the token)
   - Remind user to generate a new PAT at https://airtable.com/create/tokens

REPORT BACK:
- List of files with hardcoded paths (and whether fixed)
- Git remote status for each repo
- Security scan results
- .env gitignore status
- Airtable PAT rotation status

THEN:
1. Append Section 10 entry to MIGRATION_LOG.md (include ALL findings above)
2. STOP — wait for Windsurf review before proceeding to Section 11
```

---

## Section 11: Create Master README

```text
TASK: Create a top-level README.md for the master folder

STEPS:
1. Create README.md at the root of ~/New Master Folder - Windsurf and Cursor/
   with the following content:

# Master Workspace — Windsurf & Cursor

**Operating Model:** Windsurf = Architect | Cursor = Builder

## Navigation

| Directory | Contents |
| --- | --- |
| platforms/ | Helix / ServiceFlow SDM — flagship operations platform |
| agents/ | AI agents: status reports, communication intel, email triage |
| bots/ | Webex bots: MGM daily status, Digitized Delivery status |
| tools/ | NetPilot, firewall planning, delivery workbench, starter kit |
| content/ | AI Factory CX Transformation Playbook + tutorials |
| data/ | GES delivery data, Blue Shield analysis |
| sdm-files/ | Utility scripts, Webex bots, PPTX generator |
| _archived/ | Superseded projects (do not modify) |

## Key Documents

- **MASTER_INDEX.md** — Full project registry with status and ownership
- **CONSOLIDATION_PLAN.md** — Merge/archive decisions
- **ROADMAP.md** — Strategic plan with Cursor instruction packets
- **CURSOR_INSTRUCTIONS_MIGRATION.md** — Migration steps (this migration)

## Reports

- **Windsurf_Work_Analysis_Report.md** — All Windsurf work analyzed
- **CURSOR-WORK-HISTORY-FULL-ANALYSIS.md** — All Cursor work (1,159 lines, 22 sessions)
- **cursor-work-history-report.md** — Cursor work summary

REPORT BACK: Confirm README.md created.

THEN:
1. Append Section 11 entry to MIGRATION_LOG.md
2. STOP — wait for Windsurf review before proceeding to Section 12
```

---

## Section 12: Verify Full Migration

```text
TASK: Final verification that all projects are present and functional

STEPS:
1. Count directories:
   echo "Platforms: $(ls platforms/ | wc -l)"
   echo "Agents: $(ls agents/ | wc -l)"
   echo "Bots: $(ls bots/ | wc -l)"
   echo "Tools: $(ls tools/ | wc -l)"
   echo "Content: $(ls content/ | wc -l)"
   echo "Data: $(ls data/ | wc -l)"
   echo "Archived: $(ls _archived/ | wc -l)"

   Expected: Platforms=1, Agents=4, Bots=2, Tools=5, Content=1, Data=2, Archived=4+

2. Spot check key files:
   test -f platforms/serviceflow-sdm/README.md && echo "OK: Helix" || echo "MISSING: Helix"
   test -f agents/flerken/run.py && echo "OK: Flerken" || echo "MISSING: Flerken"
   test -f bots/mgm-status-bot/send_reports.py && echo "OK: MGM Bot" || echo "MISSING: MGM Bot"
   test -f tools/netpilot/README.md && echo "OK: NetPilot" || echo "MISSING: NetPilot"
   test -f content/ai-factory/index.html && echo "OK: AI Factory" || echo "MISSING: AI Factory"

3. Total size:
   du -sh . --exclude=.git

4. Full tree (top 2 levels):
   find . -maxdepth 2 -type d | sort

REPORT BACK: Full verification results. If all pass, migration is COMPLETE.

THEN:
1. Append Section 12 entry to MIGRATION_LOG.md with final summary
2. Add a "Migration Complete" header with total files migrated, total size, and any open issues
3. STOP — DO NOT proceed to cleanup. Wait for Windsurf review of the entire migration.
   The user will return from Windsurf with approval before ANY originals are touched.
```

---

## After Migration: Cleanup Original Locations

**DO NOT execute this section until ALL verifications pass and user explicitly approves.**

```text
TASK: Remove original project folders after verified migration
WARNING: DESTRUCTIVE — requires explicit user approval for EACH deletion

After user confirms migration is verified:
1. Ask user to confirm deletion of EACH original folder individually
2. Move (not delete) originals to Trash: mv ~/Desktop/[project] ~/.Trash/
3. This allows recovery from Trash if anything was missed

FOLDERS TO CLEAN (only after user approval per folder):
- ~/Desktop/serviceflow-sdm/
- ~/Desktop/SDM Files/ (after confirming all contents migrated)
- ~/Desktop/Flerken - Personal AI Assistant/
- ~/Desktop/email-summary-agent/
- ~/Desktop/Personal Automation/
- ~/Desktop/NetPilot/
- ~/firewall-implementation-planning/
- ~/Desktop/delivery-workbench/
- ~/Desktop/AgenticStarterKitv1_0/
- ~/Desktop/AI Factory/
- ~/Desktop/Digitized Delivery - GES/
- ~/Desktop/Digitized Delivery/ (dd-status-bot)
- ~/projects/Blue-Shield/
- ~/Desktop/Python/
```

---

*Migration instructions issued by Windsurf (Architect). Hand this entire file to Cursor and execute section by section.*
