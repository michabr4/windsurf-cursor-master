# Comms Hub Architecture — Multi-Channel Task Router

**Issued by:** Windsurf (Architect)
**Date:** May 26, 2026
**Status:** DESIGN — awaiting approval before build
**ADR:** Will create ADR-009 upon approval

---

## Vision

Turn the Windsurf ↔ Cursor comms bridge into a **multi-channel communications hub** that can send and receive tasks/notifications across:

- **IDE channels:** Windsurf, Cursor (filesystem JSON — already working)
- **Messaging:** Webex Teams (bot messages, adaptive cards)
- **Email:** MS Outlook via Microsoft Graph API
- **Future:** Slack, Jira, ServiceNow, webhooks

```text
                    ┌──────────────────────────────┐
                    │       COMMS HUB (MCP)        │
                    │                              │
                    │  ┌────────────────────────┐  │
                    │  │    Core Task Engine     │  │
                    │  │  (JSON task protocol)   │  │
                    │  └──────────┬─────────────┘  │
                    │             │                 │
                    │  ┌──────┬──┴──┬───────┬───┐  │
                    │  │      │     │       │   │  │
                    └──┼──────┼─────┼───────┼───┼──┘
                       │      │     │       │   │
                    ┌──┴──┐┌──┴──┐┌─┴──┐┌───┴┐┌─┴──┐
                    │ IDE ││Webex││Email││Jira││Slack│
                    │File ││ Bot ││Graph││API ││ API │
                    └─────┘└─────┘└─────┘└────┘└─────┘
```

## Architecture

### Layer 1: Core Task Engine (Already Built)

The JSON task protocol in `.comms/` — unchanged. Every message in the system is a task or result in the same schema:

```json
{
  "id": "TASK-2026-0526-003",
  "from": "windsurf",
  "to": "cursor",
  "priority": "high",
  "channels": ["ide", "webex"],
  "title": "Build feature X",
  "spec": "..."
}
```

**New field: `channels`** — array of delivery channels. A task can be delivered to multiple channels simultaneously.

### Layer 2: Channel Adapters

Each external system gets a channel adapter — a Python module that implements a standard interface:

```python
class ChannelAdapter:
    """Base class for all channel adapters."""

    async def send(self, message: dict) -> bool:
        """Send a task/result/notification to this channel."""
        raise NotImplementedError

    async def receive(self) -> list[dict]:
        """Check for incoming messages from this channel."""
        raise NotImplementedError

    async def health_check(self) -> bool:
        """Verify the channel is connected and working."""
        raise NotImplementedError
```

### Layer 3: MCP Server (Expanded)

The comms-bridge-mcp server gains channel-aware tools:

#### Original Tools (unchanged)

| Tool | Purpose |
| --- | --- |
| `send_task` | Create a task in inbox |
| `check_inbox` | List pending tasks |
| `claim_task` | Move task to active |
| `submit_result` | Write result to outbox |
| `check_outbox` | List completed results |
| `get_task` | Read a specific task |
| `archive_completed` | Move to completed |
| `get_pipeline_status` | Count tasks per stage |

#### New Channel Tools

| Tool | Purpose |
| --- | --- |
| `notify_webex(task_id, space_id)` | Send task summary to a Webex space |
| `notify_email(task_id, recipients)` | Send task summary via Outlook |
| `check_webex_replies(space_id)` | Read replies from a Webex space |
| `check_email_replies(folder)` | Read replies from an Outlook folder |
| `broadcast(task_id, channels)` | Send to multiple channels at once |
| `list_channels()` | Show available channels and their status |

---

## Channel Specifications

### Channel 1: IDE Filesystem (Already Working)

- **Direction:** Bidirectional
- **Mechanism:** JSON files in `.comms/inbox/`, `.comms/outbox/`
- **Auth:** None (local filesystem)
- **Latency:** Instant (file write)
- **Used by:** Windsurf, Cursor

### Channel 2: Webex Teams

- **Direction:** Bidirectional
- **Mechanism:** Webex Bot API (REST)
- **Auth:** `WEBEX_BOT_TOKEN` in `.env`
- **Latency:** ~1-2 seconds
- **Use cases:**
  - Windsurf sends a task → bot posts summary to a "Task Queue" Webex space
  - You reply in Webex → bot creates a task in `.comms/inbox/` for Cursor
  - Cursor completes work → bot posts result summary to Webex
  - You approve/reject from your phone via Webex

**Message Format (Webex Adaptive Card):**

```json
{
  "type": "AdaptiveCard",
  "body": [
    {"type": "TextBlock", "text": "New Task from Windsurf", "weight": "bolder", "size": "medium"},
    {"type": "TextBlock", "text": "TASK-2026-0526-003", "isSubtle": true},
    {"type": "TextBlock", "text": "Build Comms Bridge MCP Server", "wrap": true},
    {"type": "FactSet", "facts": [
      {"title": "Priority", "value": "HIGH"},
      {"title": "Phase", "value": "comms"},
      {"title": "Status", "value": "pending"}
    ]}
  ],
  "actions": [
    {"type": "Action.Submit", "title": "Approve", "data": {"action": "approve", "task_id": "TASK-2026-0526-003"}},
    {"type": "Action.Submit", "title": "Reject", "data": {"action": "reject", "task_id": "TASK-2026-0526-003"}}
  ]
}
```

**Implementation:**

```text
tools/agentic-starter-kit/mcp-servers/comms-bridge-mcp/
├── channels/
│   ├── __init__.py
│   ├── base.py          ← ChannelAdapter base class
│   ├── ide_filesystem.py ← Current file-based channel
│   ├── webex.py          ← Webex Bot API adapter
│   └── outlook.py        ← MS Graph API adapter
```

### Channel 3: MS Outlook (via Microsoft Graph)

- **Direction:** Bidirectional
- **Mechanism:** Microsoft Graph API (REST)
- **Auth:** Device code flow or app registration (Azure AD / Entra)
  - `MS_TENANT_ID`, `MS_CLIENT_ID` in `.env`
- **Latency:** ~2-5 seconds
- **Use cases:**
  - Windsurf sends a task → you get an email with task details
  - You reply to the email → reply is picked up and routed to Cursor
  - Daily digest: all completed tasks summarized in one email
  - Priority alerts: critical tasks sent as high-importance emails

**Email Format:**

```text
Subject: [Windsurf Task] TASK-2026-0526-003 — Build Comms Bridge MCP Server
Priority: High

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK FROM WINDSURF (Architect)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ID:       TASK-2026-0526-003
Phase:    comms
Priority: HIGH
Status:   pending

Build the Comms Bridge MCP Server...
[full spec]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Reply "APPROVE" to send to Cursor.
Reply "REJECT" with reason to cancel.
Reply with any text to add notes.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Configuration

### Single Config File

All channels configured in one place:

```text
tools/agentic-starter-kit/mcp-servers/comms-bridge-mcp/.env.example

# Core
COMMS_DIR=~/New Master Folder - Windsurf and Cursor/.comms

# Channel: Webex
WEBEX_ENABLED=true
WEBEX_BOT_TOKEN=          # From developer.webex.com
WEBEX_TASK_SPACE_ID=      # Webex space for task notifications
WEBEX_RESULT_SPACE_ID=    # Webex space for result notifications (optional, same as above)

# Channel: Outlook
OUTLOOK_ENABLED=true
MS_TENANT_ID=             # Azure AD / Entra tenant
MS_CLIENT_ID=             # App registration client ID
OUTLOOK_TASK_FOLDER=Inbox/Windsurf Tasks   # Mail folder for task emails
OUTLOOK_RECIPIENTS=michabr4@cisco.com      # Who receives task emails

# Channel: IDE Filesystem (always enabled)
# No config needed — uses COMMS_DIR
```

### MCP Config (Both IDEs)

```json
{
  "comms-bridge": {
    "command": "python3",
    "args": [
      "/Users/michabr4/New Master Folder - Windsurf and Cursor/tools/agentic-starter-kit/mcp-servers/comms-bridge-mcp/server.py"
    ],
    "envFile": "/Users/michabr4/.env.cursor"
  }
}
```

---

## Build Plan

### Phase A: Core MCP Server (1.5 hours)

Build the 8 original tools with IDE filesystem channel only. No external APIs.

| File | Purpose |
| --- | --- |
| `server.py` | FastMCP server with 8 tools |
| `channels/base.py` | ChannelAdapter base class |
| `channels/ide_filesystem.py` | Current JSON file I/O |
| `requirements.txt` | mcp SDK |
| `README.md` | Docs |
| `.env.example` | Config template |

### Phase B: Webex Channel (1 hour)

Add Webex adapter. Requires your existing Webex bot token.

| File | Purpose |
| --- | --- |
| `channels/webex.py` | Webex Bot API adapter |
| Update `requirements.txt` | Add `webexteamssdk` |
| Update `server.py` | Add `notify_webex`, `check_webex_replies` tools |

### Phase C: Outlook Channel (1.5 hours)

Add Outlook adapter via Microsoft Graph. Requires Entra app registration.

| File | Purpose |
| --- | --- |
| `channels/outlook.py` | MS Graph mail adapter |
| Update `requirements.txt` | Add `msal`, `requests` |
| Update `server.py` | Add `notify_email`, `check_email_replies` tools |

### Phase D: Broadcast + Dashboard (1 hour)

Add multi-channel broadcast and a simple status dashboard.

| File | Purpose |
| --- | --- |
| Update `server.py` | Add `broadcast`, `list_channels` tools |
| `dashboard.html` | Simple static HTML pipeline status page |

---

## Workflow Examples

### Example 1: Windsurf → Cursor + Webex Notification

```text
You: "Send Cursor the Helix hardening task, and ping me on Webex"

Windsurf calls: send_task(title="Helix Hardening", ..., channels=["ide", "webex"])

→ Task JSON written to .comms/inbox/
→ Webex bot posts adaptive card to your Task Queue space
→ You see the notification on your phone
→ In Cursor: "check inbox" → sees the task → executes
→ Result posted to Webex + written to .comms/outbox/
```

### Example 2: Email-Triggered Task

```text
You forward an email to windsurf-tasks@yourapp.com (or reply to a task email)

→ Outlook channel picks up the reply
→ Creates TASK-*.json in .comms/inbox/
→ Cursor: "check inbox" → sees the task
→ After completion, you get a result email
```

### Example 3: Morning Briefing via All Channels

```text
You: "Send me a pipeline status update"

Windsurf calls: broadcast(
  task_id="STATUS-2026-0526",
  channels=["webex", "email"]
)

→ Webex: Card with inbox/active/outbox/completed counts
→ Email: Formatted digest with task summaries
```

---

## Security Considerations

- All secrets in `.env` only — never in MCP config or source
- Webex bot token: rotate quarterly, store in OS keychain if possible
- MS Graph: use device-code flow (no client secret stored)
- Task specs may contain code or paths — never forward full specs to email/Webex by default, only summaries
- Add a `redact_spec` option that strips file paths and code blocks before external channel delivery
- Webhook endpoints (if added later) must use HTTPS + signature verification

---

## Decision Needed

Before Cursor builds this, confirm:

1. **Build Phase A first?** (Core MCP + filesystem only, then add channels later)
2. **Or build A+B together?** (Core + Webex — you already have a bot token)
3. **Outlook priority?** (Need to check if your Entra app registration is ready)

---

*This architecture is maintained by Windsurf (Architect). Cursor builds to this spec.*
