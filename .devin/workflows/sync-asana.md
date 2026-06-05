---
description: Sync Asana project tasks to the firewall dashboard (Asana MCP Server)
---

# Sync Asana → Firewall Dashboard

## One-time: Add Asana MCP Server to Windsurf

Open `~/.codeium/windsurf/mcp_config.json` and add the `asana` block (create the file if it does not exist):

```json
{
  "mcpServers": {
    "asana": {
      "command": "npx",
      "args": ["-y", "@asana/mcp-server-asana"],
      "env": {
        "ASANA_ACCESS_TOKEN": "<your-personal-access-token>"
      }
    }
  }
}
```

Generate a PAT at [app.asana.com/0/my-apps](https://app.asana.com/0/my-apps)

Restart Windsurf after saving.

---

## Network constraints

> **Cisco corporate network:** PATs and direct Asana REST API calls are blocked.
> Use Option A (MCP OAuth) or Option C (CSV export) while on-network.

---

## Option A — AI-driven sync via Asana MCP Server *(on or off network)*

The MCP server at `mcp.asana.com/sse` uses browser-based OAuth, not a PAT.
It is already configured in `~/.codeium/windsurf/mcp_config.json`.

Ask Cascade:

> "Sync my Asana firewall project tasks to the dashboard"

Cascade will:

1. Call the Asana MCP tools to fetch tasks from the project
2. Map each task to the `FirewallTask` schema (`id`, `name`, `section`, `assignee`, `status`, `startDate`, `dueDate`, `completed`)
3. Write the result to `tools/firewall-dashboard/public/data/tasks.json`

---

## Option B — CLI sync via REST API *(off Cisco network only)*

Requires `ASANA_PAT` and `ASANA_PROJECT_GID` in `tools/firewall-dashboard/.env`.

```bash
cd tools/firewall-dashboard
npm run fetch:api
```

---

## Option C — CSV export *(on Cisco network, always works)*

1. In Asana: open project → `···` menu → **Export** → **CSV** → save to `tools/firewall-dashboard/data/asana-export.csv`
2. Run:

```bash
cd tools/firewall-dashboard
npm run fetch
```

This runs `scripts/parse-asana-csv.js` using `ASANA_CSV_PATH` from `.env`.

---

## After syncing

```bash
npm run dev
```
