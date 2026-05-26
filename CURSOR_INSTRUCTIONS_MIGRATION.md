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

## Section 13: Post-Migration Fixes (Windsurf Reviewed)

```text
CURSOR INSTRUCTION: POST-MIGRATION-FIXES

CONTEXT: Windsurf has reviewed ALL migration sections (3–12). The following
fixes are approved. Execute them in order.

TASK 13.1: Fix netpilot .gitignore
- File: tools/netpilot/.gitignore
- If the file exists, append these lines (if not already present):
    .env
    .env.*
    !.env.example
- If the file does not exist, create it with:
    .env
    .env.*
    !.env.example
    node_modules/
    .venv/
    __pycache__/
    .DS_Store

TASK 13.2: Remove bundled virtual environments (scan noise reduction)
- Remove these directories if they exist:
    rm -rf data/digitized-delivery-ges/.xlsx_venv
    rm -rf data/digitized-delivery-ges/Airtable\ Tracking/.venv
- Verify removal:
    find data/ -name ".xlsx_venv" -o -name ".venv" | head -5
    (should return nothing)

TASK 13.3: Verify all .env files are gitignored
- Run this check for each .env file in the workspace:
    find . -name ".env" -not -path "./.git/*" -not -path "*node_modules*" | while read f; do
      dir=$(dirname "$f")
      if [ -f "$dir/.gitignore" ]; then
        grep -q "^\.env" "$dir/.gitignore" && echo "OK: $f" || echo "WARN: $f NOT in $dir/.gitignore"
      else
        echo "WARN: $f has no local .gitignore"
      fi
    done
- For any WARN results in active (non-archived) directories, add .env to the local .gitignore

TASK 13.4: Close open issues in MIGRATION_LOG.md
- Append a new section to MIGRATION_LOG.md:

## Section 13: Post-Migration Fixes
**Completed:** [timestamp]
**Status:** [SUCCESS or PARTIAL]

### Decisions from Windsurf Review
- email-summary-agent missing README: ACCEPTED — will be absorbed into Flerken (Phase 1)
- personal-automation missing README: ACCEPTED — will be absorbed into Flerken (Phase 1)
- data/blue-shield empty: ACCEPTED — empty repo placeholder, content expected later
- serviceflow-sdm no .git: ACCEPTED — intentional exclude during rsync, remote is michabr4/helix
- Archived backend .env unprotected: ACCEPTED — not active code
- Airtable PAT rotation: PENDING — requires manual action by user at airtable.com

### Actions Taken
- [list each fix performed with file paths]

### Issues Found
- [list any new issues or "None"]

THEN: STOP and report back to Windsurf.
```

---

## Section 14: Cleanup Original Locations (APPROVED by Windsurf)

```text
CURSOR INSTRUCTION: CLEANUP-ORIGINALS

STATUS: APPROVED by Windsurf Architect on 2026-05-26
VERIFICATION: Migration verified — all 14 projects confirmed in master folder.
METHOD: Move to Trash (recoverable). NOT permanent deletion.

TASK 14.1: Move all original project folders to Trash
Execute each command. If any command fails, log the error and continue.

mv ~/Desktop/serviceflow-sdm ~/.Trash/serviceflow-sdm
mv ~/Desktop/"SDM Files" ~/.Trash/"SDM Files"
mv ~/Desktop/"Flerken - Personal AI Assistant" ~/.Trash/"Flerken - Personal AI Assistant"
mv ~/Desktop/email-summary-agent ~/.Trash/email-summary-agent
mv ~/Desktop/"Personal Automation" ~/.Trash/"Personal Automation"
mv ~/Desktop/NetPilot ~/.Trash/NetPilot
mv ~/firewall-implementation-planning ~/.Trash/firewall-implementation-planning
mv ~/Desktop/delivery-workbench ~/.Trash/delivery-workbench
mv ~/Desktop/AgenticStarterKitv1_0 ~/.Trash/AgenticStarterKitv1_0
mv ~/Desktop/"AI Factory" ~/.Trash/"AI Factory"
mv ~/Desktop/"Digitized Delivery - GES" ~/.Trash/"Digitized Delivery - GES"
mv ~/Desktop/"Digitized Delivery" ~/.Trash/"Digitized Delivery"
mv ~/projects/Blue-Shield ~/.Trash/Blue-Shield
mv ~/Desktop/Python ~/.Trash/Python

NOTE: If a Trash name collision occurs (folder already in Trash),
append a timestamp: mv ~/Desktop/[folder] ~/.Trash/[folder]-$(date +%s)

TASK 14.2: Verify cleanup
Run this check — all should say GONE:

for d in ~/Desktop/serviceflow-sdm ~/Desktop/"SDM Files" \
  ~/Desktop/"Flerken - Personal AI Assistant" ~/Desktop/email-summary-agent \
  ~/Desktop/"Personal Automation" ~/Desktop/NetPilot \
  ~/firewall-implementation-planning ~/Desktop/delivery-workbench \
  ~/Desktop/AgenticStarterKitv1_0 ~/Desktop/"AI Factory" \
  ~/Desktop/"Digitized Delivery - GES" ~/Desktop/"Digitized Delivery" \
  ~/projects/Blue-Shield ~/Desktop/Python; do
  test -d "$d" && echo "STILL EXISTS: $d" || echo "GONE: $d"
done

TASK 14.3: Log cleanup in MIGRATION_LOG.md
Append:

## Section 14: Cleanup Original Locations
**Completed:** [timestamp]
**Status:** [SUCCESS or PARTIAL]
**Approved by:** Windsurf Architect

### Actions Taken
- Moved 14 original project folders to ~/.Trash/
- [list any that failed with error]

### Recovery
- All originals are in macOS Trash and can be restored if needed.
- Recommend emptying Trash only after 7 days of working with the master folder.

### Issues Found
- [list any or "None"]

THEN: STOP and report back to Windsurf.
```

---

## Section 15: Restore Originals from Master Folder (URGENT)

```text
CURSOR INSTRUCTION: RESTORE-ORIGINALS

STATUS: URGENT — User needs original folders restored to their previous locations.
SOURCE: Master folder contains copies of all projects from the migration.
METHOD: cp -R from master folder back to original locations.

TASK 15.1: Restore all original project folders
Execute each command in order. Do NOT use mv — we need to KEEP the master folder copies intact.

cp -R ~/New\ Master\ Folder\ -\ Windsurf\ and\ Cursor/platforms/serviceflow-sdm ~/Desktop/serviceflow-sdm
cp -R ~/New\ Master\ Folder\ -\ Windsurf\ and\ Cursor/sdm-files ~/Desktop/"SDM Files"
cp -R ~/New\ Master\ Folder\ -\ Windsurf\ and\ Cursor/agents/flerken ~/Desktop/"Flerken - Personal AI Assistant"
cp -R ~/New\ Master\ Folder\ -\ Windsurf\ and\ Cursor/agents/email-summary-agent ~/Desktop/email-summary-agent
cp -R ~/New\ Master\ Folder\ -\ Windsurf\ and\ Cursor/tools/personal-automation ~/Desktop/"Personal Automation"
cp -R ~/New\ Master\ Folder\ -\ Windsurf\ and\ Cursor/tools/netpilot ~/Desktop/NetPilot
cp -R ~/New\ Master\ Folder\ -\ Windsurf\ and\ Cursor/tools/firewall-implementation-planning ~/firewall-implementation-planning
cp -R ~/New\ Master\ Folder\ -\ Windsurf\ and\ Cursor/tools/delivery-workbench ~/Desktop/delivery-workbench
cp -R ~/New\ Master\ Folder\ -\ Windsurf\ and\ Cursor/tools/agentic-starter-kit ~/Desktop/AgenticStarterKitv1_0
cp -R ~/New\ Master\ Folder\ -\ Windsurf\ and\ Cursor/content/ai-factory ~/Desktop/"AI Factory"
cp -R ~/New\ Master\ Folder\ -\ Windsurf\ and\ Cursor/data/digitized-delivery-ges ~/Desktop/"Digitized Delivery - GES"
cp -R ~/New\ Master\ Folder\ -\ Windsurf\ and\ Cursor/data/blue-shield ~/projects/Blue-Shield
cp -R ~/New\ Master\ Folder\ -\ Windsurf\ and\ Cursor/_archived/python-empty/Python ~/Desktop/Python

SPECIAL CASES — these need sub-folders restored from SDM Files:
mkdir -p ~/Desktop/"Digitized Delivery"
cp -R ~/New\ Master\ Folder\ -\ Windsurf\ and\ Cursor/bots/dd-status-bot ~/Desktop/"Digitized Delivery"/dd-status-bot

NOTE on SDM Files: The original ~/Desktop/SDM Files/ contained sub-projects that
were split during migration. Restore requires reassembling:
- The sdm-files/ folder has the utility scripts and framework
- agents/status-report-agent was originally under SDM Files/
- agents/communication-agent was originally under SDM Files/
- bots/mgm-status-bot was originally under SDM Files/
- _archived/ServiceFlow-SDC was originally under SDM Files/
- _archived/ServiceFlow-SDC-Windsurf was originally under SDM Files/

To fully restore SDM Files:
cp -R ~/New\ Master\ Folder\ -\ Windsurf\ and\ Cursor/agents/status-report-agent ~/Desktop/"SDM Files"/status-report-agent
cp -R ~/New\ Master\ Folder\ -\ Windsurf\ and\ Cursor/agents/communication-agent ~/Desktop/"SDM Files"/communication-agent
cp -R ~/New\ Master\ Folder\ -\ Windsurf\ and\ Cursor/bots/mgm-status-bot ~/Desktop/"SDM Files"/mgm-status-bot
cp -R ~/New\ Master\ Folder\ -\ Windsurf\ and\ Cursor/_archived/ServiceFlow-SDC ~/Desktop/"SDM Files"/"ServiceFlow SDC"
cp -R ~/New\ Master\ Folder\ -\ Windsurf\ and\ Cursor/_archived/ServiceFlow-SDC-Windsurf ~/Desktop/"SDM Files"/"ServiceFlow SDC_Windsurf"
cp -R ~/New\ Master\ Folder\ -\ Windsurf\ and\ Cursor/sdm-files/sdm-agentic-framework ~/Desktop/"SDM Files"/"Service Delivery Manager Agentic Framework"

TASK 15.2: Verify restoration
for d in ~/Desktop/serviceflow-sdm ~/Desktop/"SDM Files" \
  ~/Desktop/"Flerken - Personal AI Assistant" ~/Desktop/email-summary-agent \
  ~/Desktop/"Personal Automation" ~/Desktop/NetPilot \
  ~/firewall-implementation-planning ~/Desktop/delivery-workbench \
  ~/Desktop/AgenticStarterKitv1_0 ~/Desktop/"AI Factory" \
  ~/Desktop/"Digitized Delivery - GES" ~/Desktop/"Digitized Delivery" \
  ~/projects/Blue-Shield ~/Desktop/Python; do
  test -d "$d" && echo "RESTORED: $d" || echo "FAILED:   $d"
done

TASK 15.3: Log in MIGRATION_LOG.md
Append:

## Section 15: Restore Originals
**Completed:** [timestamp]
**Status:** [SUCCESS or PARTIAL]
**Reason:** User requested originals be restored to original locations.

### Actions Taken
- Copied all 14 project folders from master folder back to original locations
- Master folder copies remain intact (used cp -R, not mv)

### Known Differences from Pre-Migration State
- .git directories were excluded during migration (rsync --exclude .git)
  so restored copies will NOT have git history. Git remotes for bots
  (mgm-status-bot, dd-status-bot) should still work via GitHub.
- venv/node_modules were cleaned during migration — will need reinstall.
- Hardcoded paths in sdm-files/ scripts were updated to relative paths
  during Section 10 fixups — restored copies have the fixed versions.

### Issues Found
- [list any or "None"]

THEN: STOP and report back to Windsurf.
```

---

*Migration instructions issued by Windsurf (Architect). Hand this entire file to Cursor and execute section by section.*
