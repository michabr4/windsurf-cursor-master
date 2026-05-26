# Cursor Builder Setup Plan

**Issued by:** Windsurf (Architect)  
**Date:** May 26, 2026  
**Purpose:** Configure Cursor as a world-class Builder IDE — security-hardened, API-connected, and optimized for your tech stack

---

## Current State (Baseline)

| Setting | Current Value |
| --- | --- |
| Theme | Default High Contrast Light |
| Font Size | 14 |
| Auto Save | afterDelay |
| Cursor Rules | None |
| MCP Servers | None in global config (ad-hoc per session) |
| Extensions | Minimal |
| Security Rules | None (22 CodeGuard rules exist in Windsurf only) |

---

## Part 1: Cursor Rules — The Builder's Playbook

Cursor rules define how the AI agent behaves. These go in `.cursor/rules/` at the project root or globally.

### 1A: Port CodeGuard Security Rules from Windsurf

Your Windsurf workspace has 22 CodeGuard rules. These MUST also govern Cursor since it's doing the actual coding.

```text
CURSOR INSTRUCTION: SETUP-CODEGUARD-RULES

TASK: Port all 22 CodeGuard security rules to Cursor format
LOCATION: ~/New Master Folder - Windsurf and Cursor/.cursor/rules/

STEPS:
1. Create directory: mkdir -p "~/New Master Folder - Windsurf and Cursor/.cursor/rules/"

2. Copy all Windsurf rules and convert format:
   For each file in .windsurf/rules/codeguard-*.md:
   - Copy to .cursor/rules/ with the same filename
   - Change the frontmatter from Windsurf format to Cursor format:

   WINDSURF FORMAT:
   ---
   trigger: glob
   globs: **/*.js,**/*.ts
   title: Rule Title
   version: 1.0.1
   ---

   CURSOR FORMAT:
   ---
   description: Rule Title
   globs: **/*.js,**/*.ts
   alwaysApply: false
   ---

   - Keep the rule body (everything after frontmatter) identical

3. Files to convert (all 22):
   - codeguard-0-additional-cryptography.md
   - codeguard-0-api-web-services.md
   - codeguard-0-authentication-mfa.md
   - codeguard-0-authorization-access-control.md
   - codeguard-0-client-side-web-security.md
   - codeguard-0-cloud-orchestration-kubernetes.md
   - codeguard-0-data-storage.md
   - codeguard-0-devops-ci-cd-containers.md
   - codeguard-0-file-handling-and-uploads.md
   - codeguard-0-framework-and-languages.md
   - codeguard-0-iac-security.md
   - codeguard-0-input-validation-injection.md
   - codeguard-0-logging.md
   - codeguard-0-mobile-apps.md
   - codeguard-0-privacy-data-protection.md
   - codeguard-0-safe-c-functions.md
   - codeguard-0-session-management-and-cookies.md
   - codeguard-0-supply-chain-security.md
   - codeguard-0-xml-and-serialization.md
   - codeguard-1-crypto-algorithms.md
   - codeguard-1-digital-certificates.md
   - codeguard-1-hardcoded-credentials.md

4. Verify: ls .cursor/rules/ | wc -l  (should be 22+)

REPORT BACK: List all converted rules with filename and description.
```

### 1B: Create Builder-Specific Rules

These rules define Cursor's behavior as the Builder in the Architect/Builder model.

```text
CURSOR INSTRUCTION: SETUP-BUILDER-RULES

TASK: Create custom Cursor rules for the Builder role
LOCATION: ~/New Master Folder - Windsurf and Cursor/.cursor/rules/

STEPS:
1. Create file: .cursor/rules/builder-role.md
   Content:

---
description: Builder Role — Operating Model
alwaysApply: true
---

# Builder Role

You are the **Builder**. Windsurf is the **Architect**.

## Operating Rules
- You execute implementation tasks based on specs from Windsurf
- Always document your work in the designated log file (MIGRATION_LOG.md or project-specific log)
- Never make architectural decisions independently — if a design choice is unclear, ask
- Always report back after completing each task with: what was done, issues found, and what needs review
- Follow all CodeGuard security rules without exception
- Never hardcode secrets, API keys, or credentials — always use .env files or OS keychain
- Commit messages follow conventional format: type(scope): description
- When creating files, include appropriate headers and documentation

## Before Making Changes
1. Read the relevant instruction packet or spec
2. Understand the full scope before starting
3. If the spec is ambiguous, ask for clarification
4. Check for existing tests — run them before and after changes

## After Making Changes
1. Run linters and formatters
2. Run existing tests
3. Document what was changed in the log
4. Report status: SUCCESS / PARTIAL / FAILED


2. Create file: .cursor/rules/project-conventions.md
   Content:

---
description: Project Conventions — Code Standards
alwaysApply: true
---

# Project Conventions

## File Organization
- Python projects: src/ for source, tests/ for tests, docs/ for documentation
- Node/TS projects: src/ for source, __tests__/ or tests/, docs/
- Always include: README.md, .env.example, .gitignore, requirements.txt or package.json

## Python Standards
- Use type hints on all function signatures
- Use Pydantic for data models where applicable
- Use virtual environments (venv or .venv) — never install globally
- Format with black, lint with ruff
- Minimum Python 3.11

## TypeScript/Node Standards
- Strict TypeScript — no `any` types without justification
- Use ESM imports
- Format with prettier, lint with eslint
- Minimum Node 22 (avoid deprecated Node 20)

## Git Conventions
- Branch naming: feature/short-description, fix/short-description, chore/short-description
- Commit format: type(scope): description
- Types: feat, fix, docs, chore, refactor, test, style, ci
- Never commit .env, node_modules, venv, __pycache__, .DS_Store

## Security (Non-Negotiable)
- All secrets in .env files only
- .env must be in .gitignore
- No API keys, tokens, or passwords in source code
- Use HTTPS for all external API calls
- Validate all user input
- Use parameterized queries for database access


3. Create file: .cursor/rules/api-integration.md
   Content:

---
description: API Integration Patterns
globs: **/*.py,**/*.ts,**/*.js
alwaysApply: false
---

# API Integration Patterns

## Authentication Patterns
- Microsoft Graph: Use device-code flow or PKCE for user-delegated auth
- Salesforce: Use OAuth 2.0 JWT bearer or connected app flow
- ServiceNow: Use OAuth 2.0 or basic auth with instance credentials
- Webex: Use bot tokens for automation, integration tokens for user actions
- Cisco APIs (DNA/FMC/ISE/OpenVuln): Use API key or token auth per service docs

## Error Handling
- Always implement retry with exponential backoff for API calls
- Log the HTTP status code, response body (redacted), and request ID
- Distinguish between retriable (429, 500, 502, 503) and non-retriable (400, 401, 403, 404) errors
- Set reasonable timeouts: 30s for standard, 120s for report generation

## Rate Limiting
- Track rate limit headers (X-RateLimit-Remaining, Retry-After)
- Implement client-side throttling before hitting limits
- Use async/await for concurrent API calls with semaphore limiting

## Data Handling
- Never log full API responses in production — redact sensitive fields
- Cache API responses where appropriate (TTL based on data freshness needs)
- Validate API response schemas before processing


REPORT BACK: Confirm all three rule files created with correct frontmatter.
```

---

## Part 2: MCP Servers — Cursor's Integration Layer

MCP (Model Context Protocol) servers give Cursor direct access to external tools and APIs. Based on your project needs, here's the full MCP server plan.

### 2A: Currently Used (Reinstall/Verify)

These were observed in your Cursor history but may not be persistently configured.

```text
CURSOR INSTRUCTION: SETUP-MCP-EXISTING

TASK: Install and configure MCP servers you've previously used
METHOD: Cursor Settings → MCP → Add Server (or edit ~/.cursor/mcp.json)

MCP SERVERS TO CONFIGURE:

1. AIRTABLE
   Name: airtable
   Type: stdio
   Command: npx
   Args: ["-y", "@airtable/mcp-server"]
   Env:
     AIRTABLE_API_KEY: (from .env — DO NOT paste in chat)
   Purpose: Query and update Airtable bases for GES tracking

2. ATLASSIAN (Jira/Confluence)
   Name: atlassian
   Type: stdio
   Command: npx
   Args: ["-y", "@anthropic/mcp-atlassian"]
   Env:
     ATLASSIAN_URL: (your Jira instance URL)
     ATLASSIAN_EMAIL: michabr4@cisco.com
     ATLASSIAN_API_TOKEN: (from .env)
   Purpose: Read/write Jira tickets, Confluence docs

3. POSTMAN
   Name: postman
   Type: stdio
   Command: npx
   Args: ["-y", "@anthropic/mcp-postman"]
   Env:
     POSTMAN_API_KEY: (from .env)
   Purpose: Run Postman collections, test API endpoints

STEPS:
1. Create or edit ~/.cursor/mcp.json with the server configs above
2. Store all API keys in ~/.env.cursor (new file) and reference via env
3. Add ~/.env.cursor to global gitignore
4. Restart Cursor to load MCP servers
5. Test each: open a chat, type "list airtable bases" / "list jira projects" to verify

REPORT BACK: Which MCP servers connected successfully and which failed (with error).
```

### 2B: New MCP Servers — Strategic Additions

These new MCP servers align with your project needs and will significantly boost Cursor's capabilities.

```text
CURSOR INSTRUCTION: SETUP-MCP-NEW

TASK: Install new MCP servers to expand Cursor's Builder capabilities

NEW MCP SERVERS:

4. GITHUB
   Name: github
   Type: stdio
   Command: npx
   Args: ["-y", "@modelcontextprotocol/server-github"]
   Env:
     GITHUB_PERSONAL_ACCESS_TOKEN: (from .env — create at github.com/settings/tokens)
   Purpose: Create repos, manage PRs, trigger workflows, read repo contents
   Critical for: mgm-status-bot, dd-status-bot GitHub Actions management

5. FILESYSTEM
   Name: filesystem
   Type: stdio
   Command: npx
   Args: ["-y", "@modelcontextprotocol/server-filesystem",
          "/Users/michabr4/New Master Folder - Windsurf and Cursor"]
   Purpose: Safe file operations within the master folder
   Critical for: Migration, project organization, bulk operations

6. POSTGRES
   Name: postgres
   Type: stdio
   Command: npx
   Args: ["-y", "@modelcontextprotocol/server-postgres"]
   Env:
     POSTGRES_CONNECTION_STRING: (from .env — your local serviceflow-sdm DB)
   Purpose: Query, inspect, and manage the Helix/ServiceFlow database
   Critical for: Helix platform development

7. DOCKER
   Name: docker
   Type: stdio
   Command: npx
   Args: ["-y", "@modelcontextprotocol/server-docker"]
   Purpose: Manage Docker containers, images, and compose stacks
   Critical for: Helix deployment, local development environments

8. MEMORY / KNOWLEDGE GRAPH
   Name: memory
   Type: stdio
   Command: npx
   Args: ["-y", "@modelcontextprotocol/server-memory"]
   Purpose: Persistent memory across Cursor sessions — remembers context, decisions, and project state
   Critical for: Long multi-session builds where Cursor loses context

9. WEBEX (Custom)
   Name: webex
   Type: stdio
   Command: python
   Args: ["-m", "webex_mcp_server"]
   Env:
     WEBEX_BOT_TOKEN: (from .env)
   Purpose: Send messages, read spaces, manage bot actions directly from Cursor
   Critical for: mgm-status-bot, dd-status-bot testing and management
   NOTE: This may require building a custom MCP server — see Part 5

10. SALESFORCE (Custom)
    Name: salesforce
    Type: stdio
    Command: python
    Args: ["-m", "salesforce_mcp_server"]
    Env:
      SF_INSTANCE_URL: (from .env)
      SF_USERNAME: (from .env)
      SF_PASSWORD: (from .env)
      SF_SECURITY_TOKEN: (from .env)
    Purpose: Query accounts, cases, opportunities directly from Cursor
    Critical for: Helix platform, status-report-agent
    NOTE: Requires custom MCP server build — see Part 5

STEPS:
1. Install servers 4-8 (these are pre-built):
   For each, add to ~/.cursor/mcp.json
   Store credentials in ~/.env.cursor

2. For servers 9-10 (custom):
   Create placeholder entries in mcp.json with enabled: false
   We will build these in Phase 3 of the ROADMAP

3. Restart Cursor and test each active server

REPORT BACK: Connection status for each server. List any that need API key setup.
```

### 2C: MCP Configuration File

```text
CURSOR INSTRUCTION: CREATE-MCP-CONFIG

TASK: Create the complete MCP configuration file

STEPS:
1. Create ~/.cursor/mcp.json with this structure:

{
  "mcpServers": {
    "airtable": {
      "command": "npx",
      "args": ["-y", "@airtable/mcp-server"],
      "env": {
        "AIRTABLE_API_KEY": "${AIRTABLE_API_KEY}"
      }
    },
    "atlassian": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-atlassian"],
      "env": {
        "ATLASSIAN_URL": "${ATLASSIAN_URL}",
        "ATLASSIAN_EMAIL": "michabr4@cisco.com",
        "ATLASSIAN_API_TOKEN": "${ATLASSIAN_API_TOKEN}"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/michabr4/New Master Folder - Windsurf and Cursor"
      ]
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "${POSTGRES_URL}"
      }
    },
    "docker": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-docker"]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}

2. Create ~/.env.cursor with placeholder values:
   (User will fill in real values — NEVER paste real keys)

# Cursor MCP Server Credentials
# WARNING: Keep this file secure. Never commit to git.

# Airtable
AIRTABLE_API_KEY=pat_ROTATE_ME

# Atlassian
ATLASSIAN_URL=https://your-instance.atlassian.net
ATLASSIAN_API_TOKEN=your_token_here

# GitHub
GITHUB_TOKEN=ghp_your_token_here

# PostgreSQL (Helix/ServiceFlow)
POSTGRES_URL=postgresql://user:pass@localhost:5432/serviceflow

# Webex (for future custom MCP)
WEBEX_BOT_TOKEN=your_bot_token_here

# Salesforce (for future custom MCP)
SF_INSTANCE_URL=https://your-instance.salesforce.com
SF_USERNAME=your_username
SF_PASSWORD=your_password
SF_SECURITY_TOKEN=your_token

3. Add to global gitignore:
   echo ".env.cursor" >> ~/.gitignore_global
   git config --global core.excludesfile ~/.gitignore_global

REPORT BACK: Confirm mcp.json created, .env.cursor created (with placeholders), global gitignore updated.
```

---

## Part 3: VS Code / Cursor Extensions

### 3A: Essential Extensions

```text
CURSOR INSTRUCTION: INSTALL-EXTENSIONS

TASK: Install critical extensions for your tech stack

STEPS:
Install each via Cursor's extension panel or command line:

PYTHON:
  cursor --install-extension ms-python.python
  cursor --install-extension ms-python.vscode-pylance
  cursor --install-extension charliermarsh.ruff
  cursor --install-extension ms-python.debugpy

TYPESCRIPT / JAVASCRIPT:
  cursor --install-extension dbaeumer.vscode-eslint
  cursor --install-extension esbenp.prettier-vscode

REACT / FRONTEND:
  cursor --install-extension dsznajder.es7-react-js-snippets
  cursor --install-extension bradlc.vscode-tailwindcss

DOCKER:
  cursor --install-extension ms-azuretools.vscode-docker

DATABASE:
  cursor --install-extension mtxr.sqltools
  cursor --install-extension mtxr.sqltools-driver-pg

GIT:
  cursor --install-extension eamodio.gitlens
  cursor --install-extension mhutchie.git-graph

MARKDOWN:
  cursor --install-extension DavidAnson.vscode-markdownlint
  cursor --install-extension yzhang.markdown-all-in-one

API DEVELOPMENT:
  cursor --install-extension humao.rest-client

SECURITY:
  cursor --install-extension streetsidesoftware.code-spell-checker

YAML:
  cursor --install-extension redhat.vscode-yaml

REPORT BACK: List installed extensions (cursor --list-extensions) and note any that failed.
```

---

## Part 4: Cursor Settings Optimization

```text
CURSOR INSTRUCTION: OPTIMIZE-SETTINGS

TASK: Configure Cursor settings for optimal Builder performance

STEPS:
1. Open Cursor Settings (Cmd+,) or edit settings.json directly
2. Merge these settings with existing:

{
  "files.autoSave": "afterDelay",
  "editor.fontSize": 14,
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.rulers": [100],
  "editor.wordWrap": "on",
  "editor.bracketPairColorization.enabled": true,
  "editor.guides.bracketPairs": true,
  "editor.minimap.enabled": false,
  "editor.stickyScroll.enabled": true,

  "terminal.integrated.fontSize": 13,
  "terminal.integrated.defaultProfile.osx": "zsh",
  "terminal.integrated.scrollback": 10000,

  "files.exclude": {
    "**/.git": true,
    "**/.DS_Store": true,
    "**/node_modules": true,
    "**/__pycache__": true,
    "**/.venv": true,
    "**/venv": true
  },

  "search.exclude": {
    "**/node_modules": true,
    "**/venv": true,
    "**/.venv": true,
    "**/__pycache__": true,
    "**/dist": true,
    "**/build": true
  },

  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll.ruff": "explicit",
      "source.organizeImports.ruff": "explicit"
    }
  },

  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },

  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },

  "[markdown]": {
    "editor.defaultFormatter": "DavidAnson.vscode-markdownlint"
  },

  "python.analysis.typeCheckingMode": "basic",
  "python-envs.defaultEnvManager": "ms-python.python:system",

  "containers.containerClient": "com.microsoft.visualstudio.containers.docker",
  "containers.orchestratorClient": "com.microsoft.visualstudio.orchestrators.dockercompose",

  "chat.subagents.allowInvocationsFromSubagents": true,
  "workbench.editor.empty.hint": "hidden",

  "git.autofetch": true,
  "git.confirmSync": false,
  "git.enableSmartCommit": true
}

3. Do NOT change colorTheme (user preference)
4. Do NOT change claudeCode settings

REPORT BACK: Confirm settings updated. List any conflicts with existing settings.
```

---

## Part 5: Custom MCP Server Builds (Future — Phase 3)

These are strategic additions Cursor should build once the migration and consolidation are complete.

### 5A: Webex MCP Server

```text
SPECIFICATION (Windsurf Architect):

Purpose: Allow Cursor to interact with Webex directly — send messages, read spaces,
manage bot subscriptions, and test status report delivery.

Location: tools/agentic-starter-kit/mcp-servers/webex-mcp/

Capabilities:
- list_spaces: List Webex spaces the bot is in
- send_message: Send a message to a space (text or adaptive card)
- read_messages: Read recent messages from a space (last N)
- list_members: List members of a space
- create_space: Create a new Webex space
- add_member: Add a person to a space

Auth: WEBEX_BOT_TOKEN from environment
Protocol: MCP stdio server (Python)
Dependencies: webexteamssdk, mcp-sdk

Cursor will build this when ROADMAP Phase 3 begins.
```

### 5B: Salesforce MCP Server

```text
SPECIFICATION (Windsurf Architect):

Purpose: Allow Cursor to query Salesforce data directly — accounts, cases,
opportunities, and SDC console metrics.

Location: tools/agentic-starter-kit/mcp-servers/salesforce-mcp/

Capabilities:
- query_soql: Execute a SOQL query and return results
- get_account: Get account details by name or ID
- list_cases: List open cases for an account
- list_opportunities: List opportunities for an account
- get_report: Run a Salesforce report and return data

Auth: OAuth 2.0 JWT bearer (SF_INSTANCE_URL, SF_USERNAME, SF_PASSWORD, SF_SECURITY_TOKEN)
Protocol: MCP stdio server (Python)
Dependencies: simple-salesforce, mcp-sdk

Cursor will build this when ROADMAP Phase 3 begins.
```

### 5C: ServiceNow MCP Server

```text
SPECIFICATION (Windsurf Architect):

Purpose: Allow Cursor to query ServiceNow incidents, changes, and CMDB data
for the status-report-agent and Helix platform.

Location: tools/agentic-starter-kit/mcp-servers/servicenow-mcp/

Capabilities:
- query_table: Query any ServiceNow table with filters
- get_incident: Get incident details by number
- list_changes: List recent change requests
- get_cmdb_ci: Get configuration item details

Auth: OAuth 2.0 or basic auth (SNOW_INSTANCE, SNOW_USERNAME, SNOW_PASSWORD)
Protocol: MCP stdio server (Python)
Dependencies: pysnow, mcp-sdk

Cursor will build this when ROADMAP Phase 3 begins.
```

---

## Part 6: AI Model Configuration

```text
CURSOR INSTRUCTION: CONFIGURE-AI-MODELS

TASK: Optimize Cursor's AI model settings

STEPS:
1. In Cursor Settings → Models:
   - Primary model: Claude Sonnet 4 (or latest available)
   - Enable "Long context" for large file editing
   - Enable "Auto-apply" for code changes in Agent mode

2. In Cursor Settings → Features:
   - Enable Agent mode as default
   - Enable "Iterate on lints" — auto-fix lint errors after edits
   - Enable "Search the web" — for API documentation lookups
   - Enable "MCP" — for all configured MCP servers

3. In Cursor Settings → Privacy:
   - Review privacy mode settings per your Cisco requirements
   - If required, enable "Privacy mode" to prevent code from being stored

REPORT BACK: Confirm model and feature settings applied.
```

---

## Execution Order

| Priority | Part | Est. Time | Notes |
| --- | --- | --- | --- |
| 1 | Part 1A: Port CodeGuard rules | 20 min | Security foundation — do first |
| 2 | Part 1B: Builder role rules | 10 min | Operating model — do second |
| 3 | Part 3: Extensions | 10 min | Install in parallel while rules are being copied |
| 4 | Part 4: Settings | 5 min | Quick merge |
| 5 | Part 2C: MCP config file | 10 min | Create config + credential placeholders |
| 6 | Part 2A: Existing MCP servers | 15 min | Verify connections |
| 7 | Part 2B: New MCP servers | 20 min | Install pre-built servers |
| 8 | Part 6: AI model config | 5 min | Final tuning |
| — | Part 5: Custom MCP builds | Future | Phase 3 of ROADMAP |

Total immediate setup time: approximately 1.5 hours.

---

## Post-Setup Verification

```text
CURSOR INSTRUCTION: VERIFY-SETUP

TASK: Verify the complete Cursor Builder setup

STEPS:
1. Rules check:
   ls .cursor/rules/ | wc -l  (expect 25: 22 CodeGuard + 3 custom)

2. MCP check:
   Open Cursor chat, run: "List all available MCP tools"
   Verify: github, filesystem, docker, memory, postgres appear

3. Extension check:
   cursor --list-extensions | wc -l  (expect 16+)

4. Settings check:
   Open a .py file — verify Ruff formatting on save
   Open a .ts file — verify Prettier formatting on save
   Open terminal — verify zsh with 10k scrollback

5. Security check:
   Verify .env.cursor is NOT in any git repo
   Verify .cursor/rules/ contains CodeGuard rules
   Run a test: ask Cursor to "write a function that stores a password"
   Cursor should refuse or use environment variables per CodeGuard rules

REPORT BACK: Full verification results.
```

---

*This plan is maintained by Windsurf (Architect). Hand to Cursor for execution after the migration is complete, or run in parallel if Cursor has capacity.*
