---
description: Complexity-adaptive context handoff — tier-based triggers, 400-token budget (VS Code / GitHub Copilot)
applyTo: "**"
---

# Context Handoff (VS Code / GitHub Copilot)

Agent hooks auto-write `.github/handoff/STATE.md` when context usage crosses a **tier-specific threshold** derived from session complexity. You must enrich both handoff files per the token budget below.

## Complexity tiers and trigger thresholds

| Tier | Signals | Trigger | Refresh |
|------|---------|---------|---------|
| **Low** | ≤5 tools, ≤2 paths, no subagents, ≤3 user turns | **65%** | preCompact only |
| **Medium** | Default | **60%** | preCompact + scope change |
| **High** | ≥15 tools, ≥5 paths, or multi-file keywords | **52%** | +12% context or scope change |
| **Critical** | Subagents and/or ≥25 tools | **45%** | +10% context, subagent completion, or scope change |

## When to update the handoff

Update `.github/handoff/STATE.md` and `.session-logs/LAST_SESSION_BRIEF.md` when **any** of these is true:

1. Context meter is at or above your session's tier threshold (see STATE.md metadata)
2. A hook notification says a handoff was saved or refreshed
3. Task scope changes materially (always, regardless of tier)
4. You are about to lose continuity (long refactor, many files, compaction imminent)

## Required handoff content

Keep both files under **400 tokens total**. Include:

- **Active task** — one sentence on what you are doing
- **Progress** — what is done vs still open
- **Files touched** — paths only, no file contents
- **Next step** — the single highest-priority action
- **Blockers** — only if present

### Token allocation by tier (400 total, both files)

| Field | Low | Medium | High / Critical |
|-------|-----|--------|-----------------|
| Active task | ~40 | ~50 | ~60 |
| Progress | ~50 | ~80 | ~100 |
| Files touched | ~30 (≤5 paths) | ~60 (≤10 paths) | ~90 (≤15 paths) |
| Next step | ~40 | ~50 | ~50 |
| Blockers | ~20 if any | ~30 if any | ~40 if any |

High/critical: put progress + next step in `LAST_SESSION_BRIEF.md`; files + blockers in `STATE.md`.

## On session start

If `.github/handoff/STATE.md` exists, read it (and `LAST_SESSION_BRIEF.md`) **before** broad exploration. Continue the task; do not re-discover work already captured in the handoff.

## VS Code hooks

Hooks live in `.github/hooks/context-handoff.json`. They fire on `SessionStart`, `PreCompact`, `Stop`, `SubagentStop`, and `PostToolUse`. Enable hooks in VS Code Settings if your organization allows them (`chat.hookFilesLocations`).

## Do not include

Secrets, tokens, env values, API responses, or large code dumps.
