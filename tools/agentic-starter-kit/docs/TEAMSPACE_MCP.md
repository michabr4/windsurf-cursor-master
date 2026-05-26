# Teamspace MCP (Cursor)

Connect Cursor to Cisco Team Space via the internal `teamspace-mcp` server.

## Prerequisites

- [uv](https://github.com/astral-sh/uv) (`~/.local/bin/uv`)
- Internal **git clone URL** for `teamspace-mcp` (not on public GitHub)
- Your Cisco email in MCP config (`CISCO_AUTH_EMAIL`)

## One-time setup

1. Add your internal clone URL to `.env` (not committed if `.env` stays local):

   ```env
   TEAMSPACE_MCP_REPO_URL=git@YOUR-INTERNAL-HOST/YOUR-ORG/teamspace-mcp.git
   ```

2. Clone and verify:

   ```bash
   ./scripts/setup_teamspace_mcp.sh
   ```

   Or pass the URL once on the command line:

   ```bash
   ./scripts/setup_teamspace_mcp.sh 'git@YOUR-INTERNAL-HOST/YOUR-ORG/teamspace-mcp.git'
   ```

3. Confirm `~/.cursor/mcp.json` includes `teamspace-mcp` pointing at `~/teamspace-mcp` (or your clone path).

4. **Cursor → Settings → MCP** → refresh or restart Cursor.

## MCP config shape

```json
"teamspace-mcp": {
  "command": "/Users/YOU/.local/bin/uv",
  "args": ["run", "--project", "/Users/YOU/teamspace-mcp", "teamspace-mcp"],
  "env": {
    "CISCO_AUTH_EMAIL": "you@cisco.com"
  }
}
```

## Troubleshooting

- **Red / failed in MCP list:** Project path wrong or repo not cloned — run the setup script again.
- **Auth errors:** Confirm `CISCO_AUTH_EMAIL` matches your Cisco account; complete any browser login the server requests on first run.
