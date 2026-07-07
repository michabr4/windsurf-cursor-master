# Context Handoff — AI Agent Install Prompt

**Copy everything below the line into your AI coding tool (Cursor, VS Code, Windsurf, Devin, Claude Code, etc.) and send it as a single message.**

---

You are installing the **Context Handoff** protocol for this repository. Follow these steps exactly. Do not skip steps. Do not improvise alternate designs.

## What you are installing

A complexity-adaptive session handoff system that preserves active task context across long sessions and compaction. It writes two small files (≤400 tokens total):

- **Cursor:** `.cursor/handoff/STATE.md` + `.session-logs/LAST_SESSION_BRIEF.md` (hooks automate triggers; you enrich content)
- **VS Code:** `.github/handoff/STATE.md` + `.session-logs/LAST_SESSION_BRIEF.md` (Copilot agent hooks + `.github/instructions/` rule)
- **Windsurf:** `.windsurf/handoff/STATE.md` + `.session-logs/LAST_SESSION_BRIEF.md` (you write on tier thresholds)
- **Devin:** `.devin/handoff/STATE.md` + `.session-logs/LAST_SESSION_BRIEF.md` (you write on tier thresholds)

## Step 0 — Ask the user (if not already stated)

Which AI tools should this repo support?

- `cursor` — automated hooks + rule
- `vscode` — GitHub Copilot instructions + agent hooks (`.github/hooks/`)
- `windsurf` — rule only (agent writes handoff)
- `devin` — rule only (agent writes handoff)
- `all` — install everything (default if user is unsure)

## Step 1 — Locate the package

Look for this directory in the repo:

```
tools/context-handoff-package/
```

If it exists, use the installer script (Step 2A).  
If it does **not** exist, copy the package from the source repo or ask the user to add `tools/context-handoff-package/` first. Do not invent a different handoff design.

## Step 2A — Run the installer (preferred)

From the **repository root**, run:

```bash
bash tools/context-handoff-package/install.sh --all
```

Or for a single tool:

```bash
bash tools/context-handoff-package/install.sh --cursor
bash tools/context-handoff-package/install.sh --vscode
bash tools/context-handoff-package/install.sh --windsurf
bash tools/context-handoff-package/install.sh --devin
```

## Step 2B — Manual install (only if the script fails)

Copy files from `tools/context-handoff-package/templates/`:

| Source | Destination |
|--------|-------------|
| `templates/cursor/rules/context-handoff.md` | `.cursor/rules/context-handoff.md` |
| `templates/cursor/hooks/context-handoff.py` | `.cursor/hooks/context-handoff.py` |
| `templates/cursor/hooks/session-start-handoff.py` | `.cursor/hooks/session-start-handoff.py` |
| `templates/cursor/handoff/.gitkeep` | `.cursor/handoff/.gitkeep` |
| `templates/windsurf/rules/context-handoff.md` | `.windsurf/rules/context-handoff.md` |
| `templates/windsurf/handoff/.gitkeep` | `.windsurf/handoff/.gitkeep` |
| `templates/devin/rules/context-handoff.md` | `.devin/rules/context-handoff.md` |
| `templates/devin/handoff/.gitkeep` | `.devin/handoff/.gitkeep` |
| `templates/vscode/instructions/context-handoff.instructions.md` | `.github/instructions/context-handoff.instructions.md` |
| `templates/vscode/hooks/context-handoff.py` | `.github/hooks/context-handoff.py` |
| `templates/vscode/hooks/session-start-handoff.py` | `.github/hooks/session-start-handoff.py` |
| `templates/vscode/handoff/.gitkeep` | `.github/handoff/.gitkeep` |
| `templates/shared/session-logs/.gitkeep` | `.session-logs/.gitkeep` |

For Cursor hooks, merge `templates/cursor/hooks.json.fragment` into `.cursor/hooks.json` without removing existing hooks:

```bash
python3 tools/context-handoff-package/scripts/merge_hooks.py \
  .cursor/hooks.json \
  tools/context-handoff-package/templates/cursor/hooks.json.fragment
```

Make hook scripts executable:

```bash
chmod +x .cursor/hooks/context-handoff.py .cursor/hooks/session-start-handoff.py
```

For VS Code hooks, merge `templates/vscode/hooks/context-handoff.json` into `.github/hooks/context-handoff.json`:

```bash
python3 tools/context-handoff-package/scripts/merge_vscode_hooks.py \
  .github/hooks/context-handoff.json \
  tools/context-handoff-package/templates/vscode/hooks/context-handoff.json
chmod +x .github/hooks/context-handoff.py .github/hooks/session-start-handoff.py
```

Append to `.gitignore` (skip lines already present):

```
# context-handoff-package — runtime handoff artifacts (do not commit)
.cursor/handoff/STATE.md
.cursor/handoff/.triggered-*
.github/handoff/STATE.md
.github/handoff/.triggered-*
.windsurf/handoff/STATE.md
.devin/handoff/STATE.md
.session-logs/LAST_SESSION_BRIEF.md
```

## Step 3 — Verify

```bash
bash tools/context-handoff-package/verify.sh
```

Fix any missing files and re-run until all checks pass.

## Step 4 — Smoke test

**Cursor** — confirm hooks are wired:

1. `.cursor/hooks.json` lists `context-handoff.py` on: `afterAgentResponse`, `stop`, `preCompact`, `subagentStop`
2. `.cursor/hooks.json` lists `session-start-handoff.py` on: `sessionStart`
3. Hook scripts are executable

```bash
echo '{}' | .cursor/hooks/session-start-handoff.py   # should print {} and exit 0
```

**VS Code** — confirm Copilot hooks are wired:

1. `.github/hooks/context-handoff.json` lists hooks on: `SessionStart`, `PreCompact`, `Stop`, `SubagentStop`, `PostToolUse`
2. Hook `env` sets `CONTEXT_HANDOFF_DIR` to `.github/handoff`
3. `.github/instructions/context-handoff.instructions.md` exists with `applyTo: "**"`
4. Hooks are enabled in VS Code (Settings → search "hook"; org policy may gate this)

```bash
echo '{"hookEventName":"SessionStart"}' | .github/hooks/session-start-handoff.py
```

## Step 5 — Report to the user

Reply with this checklist filled in:

| Check | Status |
|-------|--------|
| Installer ran (or manual copy completed) | ✅ / ❌ |
| `verify.sh` passed | ✅ / ❌ |
| Cursor rule + hooks (if requested) | ✅ / N/A |
| VS Code instructions + hooks (if requested) | ✅ / N/A |
| Windsurf rule (if requested) | ✅ / N/A |
| Devin rule (if requested) | ✅ / N/A |
| `.gitignore` updated | ✅ / ❌ |
| `.session-logs/` created | ✅ / ❌ |

Then explain in 3–5 sentences:

1. What triggers a handoff (tier thresholds: low 65%, medium 60%, high 52%, critical 45%)
2. Which files the agent must enrich when notified
3. That the next session should read handoff files before broad exploration

## Rules you must NOT break

- Do not change tier thresholds, token budgets, or file paths unless the user explicitly asks
- Do not commit `STATE.md`, `LAST_SESSION_BRIEF.md`, or `.triggered-*` marker files
- Do not put secrets, tokens, or code dumps in handoff files
- Do not remove unrelated entries from an existing `.cursor/hooks.json` or `.github/hooks/*.json`

## Reference

Full human docs: `tools/context-handoff-package/README.md`
