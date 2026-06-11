# Token Optimization — AI Agent Install Prompt

**Copy everything below the line into your AI coding tool (Cursor, VS Code, Windsurf, Devin, Claude Code, etc.) and send it as a single message.**

---

You are installing the **Token Optimization** rules from `TOKEN_OPTIMIZATION_PLAN.md`. Follow these steps exactly. Do not skip steps. Do not improvise alternate designs.

## What you are installing

Rules that cut context overhead from ~72% toward **~88%** by:

1. **P0 (glob-gate heavy rules)** — `alwaysApply: false` + file globs on effectiveness-signals and two codeguard rules (Cursor)
2. **P1 (new protocols)** — model routing, spec length cap, session warm-up, comms retention
3. **Shared dirs** — `.comms/archive/`, `.session-logs/`

## Step 0 — Ask the user (if not already stated)

Which AI tools should this repo support?

- `cursor` — 7 rules in `.cursor/rules/` (includes P0 codeguard fixes)
- `vscode` — 7 instructions in `.github/instructions/`
- `windsurf` — 5 rules in `.windsurf/rules/`
- `devin` — 5 rules in `.devin/rules/`
- `all` — install everything (default if user is unsure)

## Step 1 — Locate the package

```
tools/token-optimization-package/
```

If missing, ask the user to add it from the source repo. Read `TOKEN_OPTIMIZATION_PLAN.md` for rationale — do not invent different limits.

## Step 2A — Run the installer (preferred)

From the **repository root**:

```bash
bash tools/token-optimization-package/install.sh --all
bash tools/token-optimization-package/verify.sh
```

Or per tool:

```bash
bash tools/token-optimization-package/install.sh --cursor
bash tools/token-optimization-package/install.sh --vscode
bash tools/token-optimization-package/install.sh --windsurf
bash tools/token-optimization-package/install.sh --devin
```

## Step 2B — Manual install (only if script fails)

| Source | Destination |
|--------|-------------|
| `templates/cursor/rules/*.md` (7 files) | `.cursor/rules/` |
| `templates/vscode/instructions/*.instructions.md` (7 files) | `.github/instructions/` |
| `templates/windsurf/rules/*.md` (5 files) | `.windsurf/rules/` |
| `templates/devin/rules/*.md` (5 files) | `.devin/rules/` |
| `templates/shared/comms/archive/.gitkeep` | `.comms/archive/.gitkeep` |
| `templates/shared/session-logs/.gitkeep` | `.session-logs/.gitkeep` |

Regenerate VS Code instructions if needed:

```bash
python3 tools/token-optimization-package/scripts/convert_to_vscode_instructions.py
```

## Step 3 — P0 verification (Cursor + Windsurf)

Confirm these files have **`alwaysApply: false`** and **`globs:`** set (not always-on):

- `.cursor/rules/effectiveness-signals.md`
- `.cursor/rules/codeguard-1-crypto-algorithms.md`
- `.cursor/rules/codeguard-1-digital-certificates.md`
- `.windsurf/rules/effectiveness-signals.md` (if Windsurf installed)

Do **not** revert them to `alwaysApply: true`.

## Step 4 — P1 behavior smoke check

After install, confirm agents will:

1. Emit `[ROUTING]` telemetry per `model-routing.md`
2. Cap task specs at 300 tokens / 5 `files_to_read` per `spec-length-cap.md`
3. Read only `LAST_SESSION_BRIEF.md` + `.comms/active/` at session start per `session-warm-up.md`
4. Cap `.comms/completed/` at 20 files per `comms-retention.md`

## Step 5 — Report to the user

| Check | Status |
|-------|--------|
| Installer ran (or manual copy completed) | ✅ / ❌ |
| `verify.sh` passed | ✅ / ❌ |
| Cursor rules (7 files, if requested) | ✅ / N/A |
| VS Code instructions (7 files, if requested) | ✅ / N/A |
| Windsurf rules (5 files, if requested) | ✅ / N/A |
| Devin rules (5 files, if requested) | ✅ / N/A |
| P0 glob-gate confirmed | ✅ / N/A |
| `.comms/archive/` created | ✅ / ❌ |

Summarize expected savings in 3–5 sentences (reference plan: ~88% overhead reduction target).

## P2 — Do NOT implement unless asked

The plan lists P2/P3 backlog (rule compression, dedupe windsurf/cursor codeguard, progress tracker cap). Skip unless the user explicitly requests P2 work.

## Rules you must NOT break

- Do not change token caps (300 spec, 200 brief, 20 completed comms) unless user asks
- Do not set P0 rules back to `alwaysApply: true`
- Do not delete unrelated rules in `.cursor/rules/` or `.github/instructions/`

## Reference

- Plan: `TOKEN_OPTIMIZATION_PLAN.md`
- Human docs: `tools/token-optimization-package/README.md`
- PDF: `tools/token-optimization-package/TOKEN_OPTIMIZATION_INSTRUCTIONS.pdf`
