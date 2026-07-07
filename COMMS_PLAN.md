# Automated Communications Plan: Windsurf ↔ Cursor

**Issued by:** Windsurf (Architect)  
**Date:** May 26, 2026  
**Purpose:** Eliminate manual relay between IDEs — let Windsurf and Cursor communicate through structured, file-based protocols with optional real-time notification

---

## Problem Statement

Today, every handoff between Windsurf (Architect) and Cursor (Builder) requires you to:
1. Read Windsurf's output
2. Copy the instruction packet
3. Paste it into Cursor
4. Wait for Cursor to finish
5. Read Cursor's output
6. Return to Windsurf and summarize

**Goal:** Reduce this to a single trigger — or fully automate it.

---

## Recommended Architecture

### Option A: File-Based Message Queue (Recommended — Build First)

Both IDEs already share the master folder. Add a structured `.comms/` directory that acts as a message bus.

```
~/New Master Folder - Windsurf and Cursor/
├── .comms/
│   ├── inbox/           ← Windsurf writes tasks here for Cursor
│   ├── outbox/          ← Cursor writes results here for Windsurf
│   ├── active/          ← Currently executing task (moved from inbox)
│   ├── completed/       ← Archived completed tasks
│   └── schema.md        ← Message format spec
```

**How it works:**

1. Windsurf creates a task file in `.comms/inbox/` with a structured JSON format
2. Cursor watches for new files (or you tell Cursor to "check inbox")
3. Cursor moves the task to `.comms/active/`, executes it, writes results to `.comms/outbox/`
4. Windsurf reads the outbox, reviews, and issues next task

**Message Format:**

```json
{
  "id": "TASK-2026-0526-001",
  "from": "windsurf",
  "to": "cursor",
  "priority": "high",
  "type": "instruction",
  "phase": "0.5",
  "title": "Verify Cursor extensions installed",
  "spec": "Run: cursor --list-extensions | wc -l. Expected 16+. Report exact count and list.",
  "depends_on": null,
  "created_at": "2026-05-26T12:20:00-04:00",
  "status": "pending"
}
```

**Response Format:**

```json
{
  "id": "TASK-2026-0526-001",
  "from": "cursor",
  "to": "windsurf",
  "type": "result",
  "status": "success",
  "summary": "16 extensions installed. Full list attached.",
  "details": "...",
  "issues": [],
  "completed_at": "2026-05-26T12:25:00-04:00",
  "next_recommended": "TASK-2026-0526-002"
}
```

**Pros:** Simple, no infrastructure, both IDEs can read/write files natively, full audit trail  
**Cons:** Not real-time — requires manual "check inbox" trigger or a file watcher

---

### Option B: Shared MCP Server (Recommended — Build Second)

Build a custom MCP server that both Windsurf and Cursor connect to. This is the bridge that makes Option A real-time.

```
tools/agentic-starter-kit/mcp-servers/comms-bridge-mcp/
├── server.py          ← MCP server (Python, stdio)
├── requirements.txt   ← mcp-sdk, watchdog
├── README.md
└── .env.example
```

**MCP Tools exposed:**

| Tool | Used By | Purpose |
|------|---------|---------|
| `send_task` | Windsurf | Write a task to the inbox |
| `check_inbox` | Cursor | Read pending tasks |
| `claim_task` | Cursor | Move task to active |
| `submit_result` | Cursor | Write result to outbox |
| `check_outbox` | Windsurf | Read completed results |
| `get_status` | Both | Get current pipeline status |
| `list_history` | Both | View completed task history |

**How it works:**

1. Windsurf calls `send_task(title, spec, priority)` → writes to `.comms/inbox/`
2. Cursor calls `check_inbox()` → sees pending task
3. Cursor calls `claim_task(id)` → moves to active
4. Cursor executes the task normally
5. Cursor calls `submit_result(id, status, summary, details)` → writes to `.comms/outbox/`
6. Windsurf calls `check_outbox()` → reads result, issues next task

**MCP Config Addition (both IDEs):**

```json
{
  "comms-bridge": {
    "command": "python3",
    "args": ["-m", "comms_bridge_mcp.server"],
    "env": {
      "COMMS_DIR": "~/New Master Folder - Windsurf and Cursor/.comms"
    }
  }
}
```

**Pros:** Both IDEs use native MCP calls, no copy-paste, structured data, audit trail  
**Cons:** Requires building the MCP server (1-2 hours for Cursor)

---

### Option C: File Watcher + Notification (Enhancement)

Add a background process that watches `.comms/inbox/` and `.comms/outbox/` and sends notifications.

**Implementation:**

```python
# comms_watcher.py — runs as a background daemon
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

class CommsHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith('.json'):
            path = event.src_path
            if '/inbox/' in path:
                notify("Cursor", "New task from Windsurf", path)
            elif '/outbox/' in path:
                notify("Windsurf", "Result from Cursor", path)

def notify(target, title, path):
    # macOS native notification
    subprocess.run([
        'osascript', '-e',
        f'display notification "{title}" with title "{target} Comms"'
    ])
```

**Pros:** Real-time desktop notifications when tasks arrive  
**Cons:** Requires a background daemon

---

### Option D: Git-Based Workflow (Future Enhancement)

Use branches and commits as the communication mechanism:

- Windsurf commits specs to `architect/` branch
- Cursor pulls, executes, commits results to `builder/` branch
- Merge = handoff complete

**Pros:** Full version control, diff-based review  
**Cons:** Heaviest setup, overkill for current scale

---

## Recommended Build Order

| Priority | What | Est. Time | Who Builds |
|----------|------|-----------|-----------|
| **1** | Option A: `.comms/` directory + schema | 15 min | Windsurf designs, Cursor creates |
| **2** | Option B: `comms-bridge-mcp` server | 1.5 hours | Cursor builds to Windsurf spec |
| **3** | Option C: File watcher daemon | 30 min | Cursor builds |
| **4** | Cursor rule: auto-check inbox | 5 min | Windsurf writes |
| **5** | Option D: Git workflow | Future | After validating A+B |

---

## Phase 1 Implementation: Comms Directory + Schema

### Cursor Instruction Packet

```text
CURSOR INSTRUCTION: BUILD-COMMS-SYSTEM

TASK: Create the file-based communications system between Windsurf and Cursor
LOCATION: ~/New Master Folder - Windsurf and Cursor/

STEP 1: Create directory structure
mkdir -p .comms/inbox .comms/outbox .comms/active .comms/completed

STEP 2: Create .comms/schema.md with this content:

# Comms Protocol Schema

## Task Message (Windsurf → Cursor)
File: .comms/inbox/TASK-{YYYY}-{MMDD}-{NNN}.json

Fields:
- id: string — unique task ID matching filename
- from: "windsurf"
- to: "cursor"
- priority: "critical" | "high" | "medium" | "low"
- type: "instruction" | "review-request" | "question"
- phase: string — roadmap phase reference
- title: string — short description
- spec: string — full instruction text (can be multi-line)
- depends_on: string | null — ID of prerequisite task
- files_to_read: string[] — files Cursor should read before starting
- created_at: ISO 8601 timestamp
- status: "pending"

## Result Message (Cursor → Windsurf)
File: .comms/outbox/RESULT-{task-id}.json

Fields:
- id: string — matches the task ID
- from: "cursor"
- to: "windsurf"
- type: "result" | "question" | "blocker"
- status: "success" | "partial" | "failed" | "blocked"
- summary: string — one-line result
- details: string — full report
- files_changed: string[] — list of files modified
- issues: string[] — any issues found
- completed_at: ISO 8601 timestamp
- next_recommended: string | null — suggested next task

## Lifecycle
1. Windsurf creates TASK-*.json in inbox/ (status: pending)
2. Cursor reads inbox/, moves task to active/ (status: in_progress)
3. Cursor executes, writes RESULT-*.json to outbox/
4. Windsurf reads outbox/, moves both to completed/
5. Windsurf issues next task

STEP 3: Add to .gitignore
# Comms queue (transient)
.comms/inbox/
.comms/outbox/
.comms/active/
# Keep completed for audit
# .comms/completed/

STEP 4: Create a Cursor rule for inbox awareness
Create .cursor/rules/comms-protocol.md:

---
description: Comms Protocol — Check for Windsurf tasks
alwaysApply: true
---

# Comms Protocol

When the user asks you to "check inbox" or "check for tasks":
1. Read all .json files in .comms/inbox/
2. Display them sorted by priority (critical > high > medium > low)
3. Ask the user which task to execute
4. Move the selected task to .comms/active/
5. Execute the spec in the task
6. Write a RESULT-{task-id}.json to .comms/outbox/
7. Move the task from .comms/active/ to .comms/completed/

When you complete ANY task (even if not from inbox):
- If .comms/ exists, write a result file to .comms/outbox/ summarizing what was done


REPORT BACK: Confirm directory structure, schema, gitignore update, and rule created.
```

---

## Phase 2 Implementation: Comms Bridge MCP Server

### Windsurf Specification

```text
SPECIFICATION (Windsurf Architect): COMMS-BRIDGE-MCP

Purpose: MCP server that both Windsurf and Cursor connect to for structured
task handoff without manual copy-paste.

Location: tools/agentic-starter-kit/mcp-servers/comms-bridge-mcp/

Tech Stack:
- Python 3.11+
- mcp SDK (pip install mcp)
- Protocol: stdio

Tools to implement:

1. send_task(title, spec, priority, phase, depends_on, files_to_read)
   → Creates TASK-*.json in .comms/inbox/
   → Returns task ID

2. check_inbox()
   → Lists all pending tasks in .comms/inbox/
   → Returns array of task summaries

3. claim_task(task_id)
   → Moves task from inbox/ to active/
   → Updates status to in_progress
   → Returns full task spec

4. submit_result(task_id, status, summary, details, files_changed, issues)
   → Creates RESULT-*.json in .comms/outbox/
   → Returns confirmation

5. check_outbox()
   → Lists all results in .comms/outbox/
   → Returns array of result summaries

6. get_task(task_id)
   → Reads a specific task from any folder (inbox/active/completed)
   → Returns full task

7. archive_completed()
   → Moves all outbox results + their tasks to completed/
   → Returns count archived

8. get_pipeline_status()
   → Returns counts: inbox pending, active, outbox awaiting review, completed

Security:
- No credentials needed (local filesystem only)
- COMMS_DIR env var points to .comms/ directory
- Validate all JSON before writing
- Never execute task specs — only relay them

Testing:
- Unit test each tool with sample JSON
- Integration test: send_task → check_inbox → claim → submit → check_outbox

Cursor will build this to spec. Windsurf will review before deployment.
```

---

## Usage After Build

### Windsurf's Workflow (Architect)
```
1. "Send a task to Cursor: Verify all extensions are installed" 
   → Windsurf calls send_task() via MCP
   → Task appears in .comms/inbox/

2. Tell user: "Task sent. Tell Cursor to check inbox."

3. Later: "Check outbox for Cursor's results"
   → Windsurf calls check_outbox() via MCP
   → Reads Cursor's result
   → Issues next task or provides review
```

### Cursor's Workflow (Builder)
```
1. User says: "Check inbox" (or Cursor auto-checks per rule)
   → Cursor calls check_inbox() via MCP
   → Shows pending tasks

2. "Execute task TASK-2026-0526-001"
   → Cursor calls claim_task() → reads spec → executes
   → Calls submit_result() with outcome

3. "Any more tasks?" → check_inbox() again
```

### You (User) — Minimal Involvement
```
1. Tell Windsurf what you want done
2. Windsurf creates the task
3. Switch to Cursor, say "check inbox"
4. Cursor executes
5. Switch to Windsurf, say "check outbox"
6. Windsurf reviews and queues next task
```

---

## Future Enhancements

- **Auto-polling:** Cursor checks inbox on session start
- **Task chaining:** Windsurf pre-loads a queue of dependent tasks
- **Priority interrupts:** Critical tasks trigger macOS notifications
- **Dashboard:** Simple HTML page showing pipeline status (inbox/active/outbox/completed counts)
- **Bi-directional questions:** Cursor can send "question" type messages back to Windsurf when blocked

---

*This communications plan is maintained by Windsurf (Architect). Phase 1 can be built immediately by Cursor.*
