# Token Optimization Package

Spoon-fed installer for the rules in **[TOKEN_OPTIMIZATION_PLAN.md](../../TOKEN_OPTIMIZATION_PLAN.md)**. Same pattern as `context-handoff-package`: copy-paste prompt, shell installer, verify script, architect email blurb, and PDF.

## What it does

Reduces per-session context overhead toward **~88%** by:

| Phase | What | Savings |
|-------|------|---------|
| **P0** | Glob-gate `effectiveness-signals` + 2 codeguard rules (Cursor/Windsurf) | ~4,000 tokens/session on non-code work |
| **P1** | `model-routing`, `spec-length-cap`, `session-warm-up`, `comms-retention` | ~17,500 tokens/session combined |
| **Dirs** | `.comms/archive/` for retention moves | Bounds completed-dir listing noise |

P2/P3 items in the plan (rule compression, dedupe, telemetry) are **not** installed by this package — implement only when explicitly requested.

## Quick start

### Option 0 — Send the PDF

**[TOKEN_OPTIMIZATION_INSTRUCTIONS.pdf](TOKEN_OPTIMIZATION_INSTRUCTIONS.pdf)**

Regenerate:

```bash
bash tools/token-optimization-package/generate-pdf.sh
```

### Option A — AI tool installs it

1. Open `PROMPT.md`
2. Copy below the `---` line
3. Paste into Cursor / VS Code / Windsurf / Devin

### Option B — Shell installer

```bash
bash tools/token-optimization-package/install.sh --all
bash tools/token-optimization-package/verify.sh
```

## What gets installed

| Tool | Count | Location |
|------|-------|----------|
| Cursor | 7 rules | `.cursor/rules/` |
| VS Code | 7 instructions | `.github/instructions/` |
| Windsurf | 5 rules | `.windsurf/rules/` |
| Devin | 5 rules | `.devin/rules/` |

**Cursor-only P0:** `codeguard-1-crypto-algorithms.md`, `codeguard-1-digital-certificates.md` (glob-gated, not always-on).

**All tools P1:** model routing, spec cap, session warm-up, comms retention.

**Windsurf/Devin P0:** `effectiveness-signals.md` glob-gated.

## Package layout

```
tools/token-optimization-package/
├── TOKEN_OPTIMIZATION_PLAN.md      # canonical plan (copy)
├── TOKEN_OPTIMIZATION_INSTRUCTIONS.pdf
├── PROMPT.md                       # paste into AI tool
├── COPY_PASTE_FOR_ARCHITECT.md     # email/Slack blurb
├── README.md
├── install.sh
├── verify.sh
├── generate-pdf.sh
├── scripts/
│   ├── convert_to_vscode_instructions.py
│   └── generate_pdf.py
└── templates/
    ├── cursor/rules/
    ├── vscode/instructions/
    ├── windsurf/rules/
    ├── devin/rules/
    └── shared/comms/archive/
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `verify.sh` fails | Re-run `install.sh --all` |
| VS Code instructions missing | Run `python3 scripts/convert_to_vscode_instructions.py` then `install.sh --vscode` |
| Rules still always-on | Confirm P0 files have `alwaysApply: false` and `globs:` |
| `.comms/completed/` still huge | Agent must run comms-retention at session end; archive dir must exist |

## Works with context-handoff

Install both packages for full coverage:

```bash
bash tools/context-handoff-package/install.sh --all
bash tools/token-optimization-package/install.sh --all
```

`session-warm-up` reads `LAST_SESSION_BRIEF.md`; context-handoff writes it. No conflict.

## Updating templates

After editing rules in `.cursor/rules/`:

```bash
cp .cursor/rules/{model-routing,spec-length-cap,session-warm-up,comms-retention,effectiveness-signals,codeguard-1-crypto-algorithms,codeguard-1-digital-certificates}.md \
  tools/token-optimization-package/templates/cursor/rules/
python3 tools/token-optimization-package/scripts/convert_to_vscode_instructions.py
bash tools/token-optimization-package/generate-pdf.sh
```
