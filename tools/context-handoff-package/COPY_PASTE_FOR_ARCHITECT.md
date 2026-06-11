# Copy-paste this entire block to your architect

Select everything inside the box below and send it (Slack, email, Cursor chat, VS Code chat — anywhere).

---

**Subject: Install Context Handoff (5 minutes, mostly automated)**

Hi — please set up our **context handoff** protocol so long AI sessions don’t lose work when context compacts or chats restart.

### Fastest path (recommended)

1. Open **[PROMPT.md](tools/context-handoff-package/PROMPT.md)** in the repo.
2. Copy **everything below the `---` line** in that file.
3. Paste into your AI tool (Cursor, VS Code Copilot, Windsurf, or Devin) and send.
4. Let the agent run the installer and report the checklist back to you.

### Or run two commands yourself (repo root)

```bash
bash tools/context-handoff-package/install.sh --all
bash tools/context-handoff-package/verify.sh
```

### Pick one tool only

```bash
bash tools/context-handoff-package/install.sh --cursor
bash tools/context-handoff-package/install.sh --vscode
bash tools/context-handoff-package/install.sh --windsurf
bash tools/context-handoff-package/install.sh --devin
```

### What you’re installing

| Tool | Handoff file | How it triggers |
|------|--------------|-----------------|
| Cursor | `.cursor/handoff/STATE.md` | Hooks in `.cursor/hooks.json` |
| VS Code | `.github/handoff/STATE.md` | Copilot hooks in `.github/hooks/context-handoff.json` |
| Windsurf | `.windsurf/handoff/STATE.md` | Rule — you write on tier thresholds |
| Devin | `.devin/handoff/STATE.md` | Rule — you write on tier thresholds |

All tools also use **`.session-logs/LAST_SESSION_BRIEF.md`** (shared brief, ≤400 tokens total with STATE).

### Reference docs (if anything fails)

- **[CONTEXT_HANDOFF_INSTRUCTIONS.pdf](tools/context-handoff-package/CONTEXT_HANDOFF_INSTRUCTIONS.pdf)** — printable PDF (send this if they won't open the repo)
- **[README.md](tools/context-handoff-package/README.md)** — full docs + troubleshooting
- **[install.sh](tools/context-handoff-package/install.sh)** — installer script
- **[verify.sh](tools/context-handoff-package/verify.sh)** — post-install checks
- **[PROMPT.md](tools/context-handoff-package/PROMPT.md)** — AI agent install prompt

### VS Code only — one extra check

Agent hooks are preview. In VS Code: Settings → search **hook** → confirm `.github/hooks` is in `chat.hookFilesLocations`. Your org must allow hooks.

### Done when

- `verify.sh` prints **“All checks passed.”**
- You do **not** commit `STATE.md`, `LAST_SESSION_BRIEF.md`, or `.triggered-*` files (already in `.gitignore`).

Reply with the checklist from PROMPT Step 5 when finished.

---
