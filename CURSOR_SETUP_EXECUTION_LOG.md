# Cursor Setup Plan — Execution Log

**Executed:** 2026-05-26  
**Source:** `CURSOR_SETUP_PLAN.md` Parts 1–6

## Part 1: Cursor Rules — SUCCESS

### 1A: CodeGuard (22 rules)
Ported from `.windsurf/rules/codeguard-*.md` → `.cursor/rules/` with Cursor frontmatter (`description`, `globs`, `alwaysApply`).

| File | alwaysApply |
|------|-------------|
| codeguard-1-hardcoded-credentials.md | true |
| codeguard-1-digital-certificates.md | true |
| codeguard-1-crypto-algorithms.md | true |
| codeguard-0-* (19 rules) | false (glob-scoped) |

### 1B: Builder rules (3 files)
- `builder-role.md` — alwaysApply: true
- `project-conventions.md` — alwaysApply: true
- `api-integration.md` — glob-scoped

**Total:** 25 rule files in `.cursor/rules/`

---

## Part 2: MCP Servers — PARTIAL (config ready; restart + credentials required)

### Created / updated
- `~/.cursor/mcp.json` — merged existing `airtable-user-mcp` + new servers
- `~/.env.cursor` — placeholder credentials (fill locally, never commit)
- `~/.gitignore_global` — added `.env.cursor` (did **not** run `git config` per safety policy)

### Servers in mcp.json

| Server | Status |
|--------|--------|
| airtable-user-mcp | Preserved (existing node MCP) |
| airtable | Configured (npx + envFile) |
| atlassian | Configured |
| postman | Configured |
| github-copilot | Preserved (HTTP MCP; update Bearer in mcp.json) |
| github | Configured (stdio) |
| filesystem | Configured |
| postgres | Configured |
| docker | Configured |
| memory | Configured |
| webex | **disabled** — Phase 3 |
| salesforce | **disabled** — Phase 3 |

**Your action:** Edit `~/.env.cursor` with real tokens, update `github-copilot` Authorization header, then **restart Cursor**.

---

## Part 3: Extensions — SUCCESS

Installed via `/Applications/Cursor.app/Contents/Resources/app/bin/cursor --install-extension` (individual installs; batch failed once).

**Count:** 21 extensions (includes Cursor-bundled `anysphere.*` plus plan extensions).

Key additions: `charliermarsh.ruff`, `esbenp.prettier-vscode`, `dbaeumer.vscode-eslint`, `eamodio.gitlens`, `redhat.vscode-yaml`, `mtxr.sqltools`, `mtxr.sqltools-driver-pg`, `bradlc.vscode-tailwindcss`, `dsznajder.es7-react-js-snippets`, `mhutchie.git-graph`, `davidanson.vscode-markdownlint`, `yzhang.markdown-all-in-one`, `humao.rest-client`, `streetsidesoftware.code-spell-checker`.

---

## Part 4: Settings — SUCCESS

Merged into `~/Library/Application Support/Cursor/User/settings.json`:

- Format on save, Ruff for Python, Prettier for TS
- File/search excludes for venv, node_modules
- Terminal zsh, 10k scrollback
- Git autofetch / smart commit
- **Preserved:** `workbench.colorTheme`, `claudeCode.preferredLocation`

---

## Part 5: Custom MCP Builds — DOCUMENTED (future)

Phase 3 README stubs created:

- `tools/agentic-starter-kit/mcp-servers/webex-mcp/README.md`
- `tools/agentic-starter-kit/mcp-servers/salesforce-mcp/README.md`
- `tools/agentic-starter-kit/mcp-servers/servicenow-mcp/README.md`

---

## Part 6: AI Models — MANUAL

UI steps documented in `CURSOR_SETUP_PART6_MANUAL.md`.

Settings.json hints added: `cursor.agent.enableAutoApply` (remove if Cursor flags unknown key).

---

## Next steps

1. Fill `~/.env.cursor` and restart Cursor
2. Complete Part 6 in Settings UI
3. Install extensions (Part 3) if batch install failed
4. Verify: `ls .cursor/rules | wc -l` → 25
5. Chat test: “List available MCP tools”
