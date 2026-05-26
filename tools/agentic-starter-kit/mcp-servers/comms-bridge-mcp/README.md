# Comms Bridge MCP Server

MCP server that exposes the Windsurf ↔ Cursor file-based comms protocol (`.comms/`) as named tools. Both IDEs can connect to the same `COMMS_DIR` for structured task handoff without manual file moves.

## What it does

- Reads and writes JSON task/result files under `.comms/inbox`, `active`, `outbox`, and `completed`
- Validates message shape against the protocol schema
- Never executes task `spec` content — storage and relay only
- Uses atomic writes (temp file + rename) for safer concurrent access

## Install

```bash
cd tools/agentic-starter-kit/mcp-servers/comms-bridge-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to your environment or MCP config and set `COMMS_DIR` if your workspace path differs.

## Run locally (stdio)

```bash
export COMMS_DIR="$HOME/New Master Folder - Windsurf and Cursor/.comms"
python server.py
```

The process waits on stdin for MCP messages (Ctrl+C to exit). IDEs spawn this command automatically when configured as an MCP server.

## MCP tools (8)

| Tool | Description |
|------|-------------|
| `send_task` | Create `TASK-{YYYY}-{MMDD}-{NNN}.json` in `inbox/` (from Windsurf) |
| `check_inbox` | List pending tasks sorted by priority |
| `claim_task` | Move task `inbox/` → `active/`, set `in_progress` |
| `submit_result` | Write `RESULT-*.json` to `outbox/`, archive task to `completed/` |
| `check_outbox` | List results awaiting Windsurf review |
| `get_task` | Load full task from `inbox/`, `active/`, or `completed/` |
| `archive_completed` | Move all `RESULT-*.json` from `outbox/` → `completed/` |
| `get_pipeline_status` | Count JSON files in each pipeline folder |

## Cursor configuration

Add to `~/.cursor/mcp.json` (after review):

```json
{
  "mcpServers": {
    "comms-bridge": {
      "command": "python3",
      "args": [
        "/Users/michabr4/New Master Folder - Windsurf and Cursor/tools/agentic-starter-kit/mcp-servers/comms-bridge-mcp/server.py"
      ],
      "env": {
        "COMMS_DIR": "/Users/michabr4/New Master Folder - Windsurf and Cursor/.comms"
      }
    }
  }
}
```

Use your venv Python path if you prefer an isolated environment:

```json
"command": "/path/to/comms-bridge-mcp/.venv/bin/python"
```

## Windsurf configuration

Windsurf MCP config format may differ by version; equivalent stdio entry:

```json
{
  "mcpServers": {
    "comms-bridge": {
      "command": "python3",
      "args": ["tools/agentic-starter-kit/mcp-servers/comms-bridge-mcp/server.py"],
      "env": {
        "COMMS_DIR": "/absolute/path/to/.comms"
      }
    }
  }
}
```

Use absolute paths for `args` and `COMMS_DIR` in production configs.

## Environment

| Variable | Default | Purpose |
|----------|---------|---------|
| `COMMS_DIR` | `~/New Master Folder - Windsurf and Cursor/.comms` | Root comms directory |

## Protocol reference

See `.comms/schema.md` in the workspace root for task/result JSON fields and lifecycle.
