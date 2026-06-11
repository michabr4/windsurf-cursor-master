# Copy-paste this entire block to your architect

Select everything inside the box below and send it.

---

**Subject: Install Token Optimization rules (~5 minutes)**

Hi — please install our **token optimization** rules so AI sessions stop loading unnecessary context. Target: **~88% overhead reduction** (up from ~72% baseline).

### Fastest path (recommended)

1. Open **[PROMPT.md](tools/token-optimization-package/PROMPT.md)** in the repo.
2. Copy **everything below the `---` line**.
3. Paste into your AI tool (Cursor, VS Code Copilot, Windsurf, or Devin) and send.
4. Let the agent run the installer and return the Step 5 checklist.

### Or run two commands (repo root)

```bash
bash tools/token-optimization-package/install.sh --all
bash tools/token-optimization-package/verify.sh
```

### Printable PDF

Send **[TOKEN_OPTIMIZATION_INSTRUCTIONS.pdf](tools/token-optimization-package/TOKEN_OPTIMIZATION_INSTRUCTIONS.pdf)** if they will not open the repo.

### What gets installed

| Package | Rules | Key protocols |
|---------|-------|----------------|
| **Cursor** (7 rules) | `.cursor/rules/` | P0 glob-gate + model routing, spec cap, warm-up, comms retention |
| **VS Code** (7 instructions) | `.github/instructions/` | Same protocols as Copilot instructions |
| **Windsurf** (5 rules) | `.windsurf/rules/` | P1 protocols + effectiveness glob-gate |
| **Devin** (5 rules) | `.devin/rules/` | P1 protocols |

Also creates `.comms/archive/` (for comms retention) and `.session-logs/`.

### Done when

- `verify.sh` prints **"All checks passed."**
- P0 rules show `alwaysApply: false` with `globs:` (not loaded on markdown-only sessions)

### Full plan

**[TOKEN_OPTIMIZATION_PLAN.md](TOKEN_OPTIMIZATION_PLAN.md)** — findings, savings table, P2 backlog

Reply with the PROMPT Step 5 checklist when finished.

---
