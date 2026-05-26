# ServiceNow MCP Server (Phase 3)

**Status:** Planned — not yet in `~/.cursor/mcp.json`.

## Purpose

Query ServiceNow incidents, changes, and CMDB data for status-report-agent and Helix.

## Capabilities (planned)

- `query_table` — Query any ServiceNow table with filters
- `get_incident` — Incident details by number
- `list_changes` — Recent change requests
- `get_cmdb_ci` — Configuration item details

## Auth

OAuth 2.0 or basic auth (`SNOW_INSTANCE`, `SNOW_USERNAME`, `SNOW_PASSWORD`)

## Stack

- Protocol: MCP stdio (Python)
- Dependencies: `pysnow`, `mcp`

Built when ROADMAP Phase 3 begins per `CURSOR_SETUP_PLAN.md`.
