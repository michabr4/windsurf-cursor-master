# Part 6: AI Model Configuration (Manual UI Steps)

These settings are controlled in **Cursor Settings** (Cmd+,) and cannot be fully automated from the CLI. Apply after Parts 1–5.

## Models (Settings → Models)

- **Primary model:** Claude Sonnet 4 (or latest Sonnet available)
- **Long context:** Enable for large file / multi-file edits
- **Auto-apply:** Enable for Agent mode code changes (also set `cursor.agent.enableAutoApply` in settings.json)

## Features (Settings → Features / Beta)

- **Agent mode:** Default interaction mode where possible
- **Iterate on lints:** Enable — auto-fix lint issues after edits
- **Search the web:** Enable for API documentation lookups
- **MCP:** Enable — required for all servers in `~/.cursor/mcp.json`

## Privacy (Settings → Privacy)

- Review **Privacy mode** per Cisco policy
- If required, enable privacy mode to limit code retention on Cursor servers

## After changing

1. **Restart Cursor** (Cmd+Shift+P → “Developer: Reload Window”)
2. Open Agent chat → confirm MCP tools appear
3. Test: “List available MCP tools” or invoke a filesystem/github tool
