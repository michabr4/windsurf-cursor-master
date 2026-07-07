# Salesforce MCP Server (Phase 3)

**Status:** Planned — disabled in `~/.cursor/mcp.json` until implemented.

## Purpose

Query Salesforce data from Cursor: accounts, cases, opportunities, and SDC console metrics.

## Capabilities (planned)

- `query_soql` — Execute SOQL and return results
- `get_account` — Account details by name or ID
- `list_cases` — Open cases for an account
- `list_opportunities` — Opportunities for an account
- `get_report` — Run a Salesforce report

## Auth

OAuth 2.0 / connected app via `SF_*` variables in `~/.env.cursor`

## Stack

- Protocol: MCP stdio (Python)
- Dependencies: `simple-salesforce`, `mcp`

Built when ROADMAP Phase 3 begins per `CURSOR_SETUP_PLAN.md`.
