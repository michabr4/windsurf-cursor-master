# Context Handoff Package

Spoon-fed installer for the **complexity-adaptive context handoff** protocol. Gives your architect (or any teammate) a copy-paste AI prompt and a one-command shell installer — no tribal knowledge required.

## What it does

Long AI sessions lose context when the window compacts or you start a new chat. This package installs rules and (for Cursor) hooks that:

1. **Detect** when context usage crosses a tier-specific threshold (low 65% → critical 45%)
2. **Write** skeleton handoff files with session metadata
3. **Prompt** the agent to enrich those files (≤400 tokens total)
4. **Resume** the next session from handoff state instead of re-discovering work

## Quick start (for humans)

### Option 0 — Send the PDF

Attach or share **[CONTEXT_HANDOFF_INSTRUCTIONS.pdf](CONTEXT_HANDOFF_INSTRUCTIONS.pdf)** with your architect. Regenerate anytime:

```bash
bash tools/context-handoff-package/generate-pdf.sh
```

### Option A — Let your AI tool do it (easiest)

1. Open `PROMPT.md`
2. Copy everything **below the `---` line**
3. Paste into Cursor / VS Code / Windsurf / Devin / Claude Code
4. Send. The agent runs the installer and reports back.

### Option B — Run the script yourself

From your **repo root**:

```bash
bash tools/context-handoff-package/install.sh --all
bash tools/context-handoff-package/verify.sh
```

Pick a single tool:

```bash
bash tools/context-handoff-package/install.sh --cursor    # hooks + rule
bash tools/context-handoff-package/install.sh --vscode    # Copilot instructions + hooks
bash tools/context-handoff-package/install.sh --windsurf  # rule only
bash tools/context-handoff-package/install.sh --devin     # rule only
```

Install into another repo:

```bash
bash tools/context-handoff-package/install.sh --all /path/to/other-repo
```

## What gets installed

| Tool | Rule | Hooks | Handoff dir | Brief file |
|------|------|-------|-------------|------------|
| **Cursor** | `.cursor/rules/context-handoff.md` | 5 events in `.cursor/hooks.json` | `.cursor/handoff/` | `.session-logs/LAST_SESSION_BRIEF.md` |
| **VS Code** | `.github/instructions/context-handoff.instructions.md` | 5 events in `.github/hooks/context-handoff.json` | `.github/handoff/` | `.session-logs/LAST_SESSION_BRIEF.md` |
| **Windsurf** | `.windsurf/rules/context-handoff.md` | — (agent writes) | `.windsurf/handoff/` | `.session-logs/LAST_SESSION_BRIEF.md` |
| **Devin** | `.devin/rules/context-handoff.md` | — (agent writes) | `.devin/handoff/` | `.session-logs/LAST_SESSION_BRIEF.md` |

### Cursor hooks (automated)

| Event | Script | Behavior |
|-------|--------|----------|
| `afterAgentResponse` | `context-handoff.py` | Writes/refreshes handoff when threshold crossed |
| `stop` | `context-handoff.py` | Same on agent stop |
| `preCompact` | `context-handoff.py` | Always writes before compaction |
| `subagentStop` | `context-handoff.py` | Refreshes at critical tier after subagents |
| `sessionStart` | `session-start-handoff.py` | Injects saved handoff into new session |

Existing `.cursor/hooks.json` entries are **preserved** — the installer only appends missing handoff hooks.

### VS Code hooks (GitHub Copilot agent, automated)

| Event | Script | Behavior |
|-------|--------|----------|
| `SessionStart` | `session-start-handoff.py` | Injects saved handoff into new session |
| `PreCompact` | `context-handoff.py` | Always writes before compaction |
| `Stop` | `context-handoff.py` | Writes/refreshes handoff when threshold crossed |
| `SubagentStop` | `context-handoff.py` | Refreshes at critical tier after subagents |
| `PostToolUse` | `context-handoff.py` | Checks threshold after each tool (VS Code has no `afterAgentResponse`) |

Hooks use the same Python scripts as Cursor, with `CONTEXT_HANDOFF_DIR=.github/handoff` and VS Code JSON output format (`hookSpecificOutput.additionalContext`).

**Prerequisites:** VS Code agent hooks are preview; your org must allow hooks. Confirm `chat.hookFilesLocations` includes `.github/hooks`. For monorepo subfolders, enable `chat.useCustomizationsInParentRepositories`.

## Complexity tiers

| Tier | Signals | Trigger | Refresh |
|------|---------|---------|---------|
| Low | ≤5 tools, ≤2 paths, no subagents, ≤3 turns | 65% | preCompact only |
| Medium | Default | 60% | preCompact + scope change |
| High | ≥15 tools, ≥5 paths, or multi-file keywords | 52% | +12% context or scope change |
| Critical | Subagents and/or ≥25 tools | 45% | +10% context, subagent done, or scope change |

## Handoff content (agent enriches)

Both files combined must stay under **400 tokens**:

- Active task (one sentence)
- Progress (done vs open)
- Files touched (paths only)
- Next step (single action)
- Blockers (if any)

**Never include:** secrets, tokens, env values, API responses, code dumps.

## Package layout

```
tools/context-handoff-package/
├── PROMPT.md              ← paste into AI tool
├── README.md              ← you are here
├── install.sh             ← one-command installer
├── verify.sh              ← post-install checks
├── scripts/
│   ├── merge_hooks.py        ← Cursor hooks.json merge
│   └── merge_vscode_hooks.py ← VS Code hooks merge
└── templates/
    ├── cursor/            ← rules, hooks, hooks fragment
    ├── vscode/            ← instructions, hooks json, hook scripts
    ├── windsurf/
    ├── devin/
    └── shared/session-logs/
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `verify.sh` fails | Re-run `install.sh --all` |
| Hooks not firing (Cursor) | Confirm hooks enabled in Cursor Settings → Hooks; scripts must be executable |
| Hooks not firing (VS Code) | Check org policy allows hooks; open **GitHub Copilot Chat Hooks** output channel; confirm `chat.hookFilesLocations` |
| Duplicate hook entries | Safe to re-run installer — merge scripts skip duplicates |
| Wrong repo path | Pass target dir: `install.sh --all /path/to/repo` |

## Copying to another repo

Copy the entire `tools/context-handoff-package/` folder into the target repo, then run Option A or B above.

## Updating

When the canonical handoff spec changes in the main repo, refresh templates:

```bash
cp .cursor/rules/context-handoff.md tools/context-handoff-package/templates/cursor/rules/
cp .cursor/hooks/context-handoff.py tools/context-handoff-package/templates/cursor/hooks/
cp .cursor/hooks/session-start-handoff.py tools/context-handoff-package/templates/cursor/hooks/
cp .devin/rules/context-handoff.md tools/context-handoff-package/templates/devin/rules/
cp tools/context-handoff-package/templates/cursor/hooks/*.py tools/context-handoff-package/templates/vscode/hooks/
```

Then bump Windsurf / VS Code instructions if `.devin/rules/context-handoff.md` changed (paths: `.windsurf/handoff/`, `.github/handoff/`).
