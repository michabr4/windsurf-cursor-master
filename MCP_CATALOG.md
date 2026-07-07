# MCP Server Catalog
## AI IDE Tooling — Windsurf + Cursor

> **Last updated:** 2026-05-29  
> **Env file (Cursor):** `~/.env.cursor`  
> **Windsurf config:** `~/.codeium/windsurf/mcp_config.json`  
> **Cursor config:** `~/.cursor/mcp.json`

---

## Status Legend
| Symbol | Meaning |
|---|---|
| ✅ | Active in both IDEs |
| 🟡 | Active in one IDE only (see note) |
| 🔴 | Configured but disabled (needs credentials) |
| ⬜ | Planned / not yet installed |

---

## 1. Active Servers

| Server | Package / URL | Auth | Cursor | Windsurf | Notes |
|---|---|---|---|---|---|
| **airtable-user-mcp** | local `~/.airtable-user-mcp/start.mjs` | Chrome session | ✅ | ✅ | Custom headless automation |
| **airtable** | `@airtable/mcp-server` | AIRTABLE_API_KEY | 🟡 Cursor | — | Official Airtable REST API |
| **atlassian** | `@anthropic/mcp-atlassian` / remote SSE | ATLASSIAN_URL + TOKEN | ✅ | ✅ | Jira + Confluence |
| **github** | `@modelcontextprotocol/server-github` / remote Copilot | GITHUB_PAT | ✅ | ✅ | PR, issues, code search |
| **deepwiki** | `https://mcp.deepwiki.com/mcp` | None | 🟡 Windsurf | 🟡 Windsurf | AI wiki for GitHub repos |
| **filesystem** | `@modelcontextprotocol/server-filesystem` | None | 🟡 Cursor | — | Local workspace file access |
| **postgres** | `@modelcontextprotocol/server-postgres` | POSTGRES_CONNECTION_STRING | 🟡 Cursor | — | Helix DB direct access |
| **docker** | `@modelcontextprotocol/server-docker` | None | 🟡 Cursor | — | Container management |
| **memory** | `@modelcontextprotocol/server-memory` | None | 🟡 Cursor | — | Persistent KV memory store |
| **playwright** | `@playwright/mcp@latest` | None | 🟡 Windsurf | ✅ | Browser automation |
| **puppeteer** | `@modelcontextprotocol/server-puppeteer` | None | — | 🟡 Windsurf | Browser automation (alt) |
| **fetch** | Docker `mcp/fetch` | None | — | 🟡 Windsurf | HTTP fetch + web scraping |
| **sqlite** | `@modelcontextprotocol/server-sqlite` | None | — | 🟡 Windsurf | Local SQLite DB access |
| **context7** | `@upstash/context7-mcp@latest` | None | 🟡 Windsurf | ✅ | Up-to-date library docs |
| **asana** | `https://mcp.asana.com/sse` | OAuth (Windsurf handles) | — | 🟡 Windsurf | Task + project management |
| **postman** | `@anthropic/mcp-postman` | POSTMAN_API_KEY | 🟡 Cursor | — | API collection runner |
| **comms-bridge** | local Python `server.py` | None | ✅ | ✅ | Windsurf ↔ Cursor task relay |
| **outlook** | local `~/.local/bin/outlook-mcp` | None | 🟡 Cursor | — | Email read/send |
| **webex** | `python3 -m webex_mcp_server` | WEBEX_BOT_TOKEN | 🔴 disabled | — | Re-enable when needed |
| **salesforce** | `python3 -m salesforce_mcp_server` | SF creds | 🔴 disabled | — | Re-enable when needed |

---

## 2. Cross-Sync Fixes (missing from one IDE)

### Add to Cursor
These already work in Windsurf — add to `~/.cursor/mcp.json`:

| Server | Action |
|---|---|
| `context7` | Add via npx — no credentials needed |
| `playwright` | Add via npx — no credentials needed |
| `fetch` | Add via Docker — no credentials needed |
| `sqlite` | Add via npx — no credentials needed |
| `asana` | Add remote URL — Windsurf OAuth handles auth; Cursor needs ASANA_ACCESS_TOKEN stub |
| `deepwiki` | Add remote URL — no credentials needed |

### Add to Windsurf
These already work in Cursor — add to `~/.codeium/windsurf/mcp_config.json`:

| Server | Action |
|---|---|
| `filesystem` | Add via npx pointing to workspace root |
| `postgres` | Add via npx with `.env.cursor` envFile |
| `docker` | Add via npx — no credentials needed |
| `memory` | Add via npx — no credentials needed |
| `postman` | Add via npx with `.env.cursor` envFile |

---

## 3. New Servers — Expansion

### 3a. No credentials required — add enabled immediately

| Server | Package | Use case |
|---|---|---|
| **sequential-thinking** | `@modelcontextprotocol/server-sequential-thinking` | Multi-step reasoning chains; planning tasks for agents and Helix work |
| **redis** | `@modelcontextprotocol/server-redis` | Helix uses Redis cache; inspect/flush keys during dev without needing redis-cli |

### 3b. Requires credential setup — add disabled stubs

| Server | Package | Required Env Var(s) | Use case |
|---|---|---|---|
| **brave-search** | `@modelcontextprotocol/server-brave-search` | `BRAVE_API_KEY` | Web search for research agents; better than fetch for search queries |
| **exa** | `exa-mcp-server` | `EXA_API_KEY` | Semantic/neural web search; better than keyword search for technical docs |
| **slack** | `@modelcontextprotocol/server-slack` | `SLACK_BOT_TOKEN`, `SLACK_TEAM_ID` | Cross-org messaging alongside Webex/Outlook |
| **notion** | `notion-mcp-server` | `NOTION_API_TOKEN` | Knowledge base read/write for documentation workflows |
| **sentry** | `@sentry/mcp-server` | `SENTRY_AUTH_TOKEN`, `SENTRY_ORG` | Error monitoring for deployed bots (dd-status-bot, mgm-status-bot) |
| **linear** | `@linear/mcp-server` | `LINEAR_API_KEY` | Issue tracking alternative if Asana/Jira not available |
| **tavily** | `tavily-mcp` | `TAVILY_API_KEY` | Research-grade web search for AI agents |
| **aws** | `@modelcontextprotocol/server-aws-kb-retrieval` | AWS creds | Cloud infra queries relevant to Cisco deployment |
| **sharepoint** | local venv `tools/sharepoint-mcp-venv/bin/sharepoint-mcp` | `SHP_TENANT_ID`, `SHP_ID_APP`, `SHP_ID_APP_SECRET`, `SHP_SITE_URL` | PyPI `sharepoint-mcp` 1.1.1 — Docker `ravikant1918/sharepoint-mcp:latest` not published; use stdio not podman unless you build the image |

### 3c. Consideration only (evaluate before adding)

| Server | Notes |
|---|---|
| **vercel** | Only if Helix frontend gets deployed to Vercel |
| **stripe** | Not currently relevant to any active project |
| **google-maps** | Not currently relevant |
| **figma** | Add if design workflow integration becomes needed |

---

## 4. Credential Setup Checklist

New servers marked `disabled: true` will be ready to enable once you add the credential to `~/.env.cursor`:

```bash
# Add to ~/.env.cursor when ready:
BRAVE_API_KEY=             # https://brave.com/search/api/
EXA_API_KEY=               # https://exa.ai/
SLACK_BOT_TOKEN=           # https://api.slack.com/apps
SLACK_TEAM_ID=             # Slack workspace ID
NOTION_API_TOKEN=          # https://www.notion.so/my-integrations
SENTRY_AUTH_TOKEN=         # https://sentry.io/settings/account/api/auth-tokens/
SENTRY_ORG=                # Your Sentry org slug
LINEAR_API_KEY=            # https://linear.app/settings/api
TAVILY_API_KEY=            # https://tavily.com/
ASANA_ACCESS_TOKEN=        # https://app.asana.com/0/my-apps (Personal Access Token)
REDIS_URL=redis://localhost:6379
SHP_TENANT_ID=               # Azure AD tenant (Cisco) — not AZURE_TENANT_ID
SHP_ID_APP=                  # App registration client ID
SHP_ID_APP_SECRET=           # App registration secret (never commit)
SHP_SITE_URL=                # e.g. https://cisco.sharepoint.com/sites/CXMGM
SHP_API_TYPE=graph           # graph | office365 | graphql
TRANSPORT=stdio              # required for Cursor MCP (not http)
```

---

## 5. Project → MCP Mapping

Which servers are most valuable per active project:

| Project | Primary MCPs |
|---|---|
| **Helix / ServiceFlow SDM** | postgres, redis, filesystem, docker, github, sequential-thinking |
| **Delivery Tracker agent** | asana, sequential-thinking, github, filesystem |
| **Communication agent** | webex (enable), slack, outlook |
| **DD/MGM Status Bots** | github, sentry, slack, webex |
| **Firewall Dashboard** | filesystem, postgres, github, sequential-thinking |
| **Mimir integration (Wave 18)** | fetch, filesystem, postgres, sequential-thinking |
| **AI Factory / general** | context7, brave-search, exa, tavily, notion, sequential-thinking |
| **MGM CX / Digitized Delivery research** | sharepoint, fetch, context7, sequential-thinking |
