---
description: Context handoff — write session state when context meter reaches 60%
alwaysApply: true
---

# Context Handoff at 60%

Hooks auto-write `.cursor/handoff/STATE.md` when estimated context usage crosses **60%**. You must keep that file accurate when you can see the context meter approaching the threshold.

## When to update the handoff

Update `.cursor/handoff/STATE.md` and `.session-logs/LAST_SESSION_BRIEF.md` when **any** of these is true:

1. The context meter is at or above **60%**
2. A hook notification says a handoff was saved
3. You are about to lose continuity (long refactor, many files, compaction imminent)

## Required handoff content

Keep both files under 400 tokens total. Include:

- **Active task** — one sentence on what you are doing
- **Progress** — what is done vs still open
- **Files touched** — paths only, no file contents
- **Next step** — the single highest-priority action
- **Blockers** — only if present

## On session start

If `.cursor/handoff/STATE.md` exists, read it (and `LAST_SESSION_BRIEF.md`) **before** broad exploration. Continue the task; do not re-discover work already captured in the handoff.

## Do not include

Secrets, tokens, env values, API responses, or large code dumps.
