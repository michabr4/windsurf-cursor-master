---
description: Context Handoff — write complexity-adaptive session handoff when context load is high
alwaysApply: true
---

# Context Handoff Protocol

## Purpose

Preserve active task context so the next session (Windsurf or Cursor) can resume without rework.

## When to Write the Handoff

Check complexity tier after each significant cluster of tool calls. Write when the estimated context load crosses the tier threshold, and always on session end or before compaction.

### Complexity Classification

| Tier | Signals | Threshold |
| ------ | --------- | ----------- |
| **low** | ≤5 tool calls, ≤2 files, ≤3 user turns | ~65% |
| **medium** | 6–14 tool calls or 3–4 files | ~60% |
| **high** | ≥15 tool calls or ≥5 files, or task spans multiple files / refactor / migration | ~52% |
| **critical** | ≥1 subagent call or ≥25 total tool calls | ~45% — refresh after each subagent completes |

Also write immediately when:

- User signals session end ("done", "wrapping up", "closing", "end session")
- Context is about to be compacted / summarized
- Scope of the active task changes materially at critical tier

At critical tier: refresh after each subagent completes (not just once).

## Files to Write

### 1 — `.windsurf/handoff/STATE.md`

```markdown
# Session Handoff
**Created:** YYYY-MM-DD HH:MM UTC
**Complexity tier:** [low|medium|high|critical]
**Context load:** ~[N]% (tier threshold [N]%)
**Agent:** Windsurf
**Session signals:** [N] tools, [N] paths, [N] subagents

## Active task
[One sentence — what is actively being built or fixed]

## Progress
[Done vs still open — be specific; include file:line where useful]

## Files touched
- `path/to/file`
[paths only — no file contents]

## Next step
[Single highest-priority next action]

## Blockers
[Omit section if none]

## Resume instructions
1. Read this file and `.session-logs/LAST_SESSION_BRIEF.md`.
2. Do not restart from scratch — continue the active task.
3. Keep both files ≤400 tokens total; update if scope changes materially.
```

### 2 — `.session-logs/LAST_SESSION_BRIEF.md`

```markdown
# Last Session Brief
**Date:** YYYY-MM-DD  **Agent:** Windsurf  **Tier:** [tier]
**Context load at handoff:** ~[N]% (threshold [N]%)
**Active task:** [one sentence]
**Progress:** [done vs open]
**Files changed:** see Files touched in `.windsurf/handoff/STATE.md`
**Key decisions:** [any key decisions made, or omit]
**Next priority:** [single next action]
**Blockers:** [omit if none]
```

## Token Budgets by Tier

Target ≤400 tokens total across both files combined.

| Tier | Active task | Progress | Files (max paths) | Next step | Blockers |
| ------ | ----------- | -------- | ------------------ | --------- | ------- |
| low | ~40 | ~50 | ~30 (max 5) | ~40 | ~20 |
| medium | ~40 | ~60 | ~60 (max 10) | ~50 | ~30 |
| high | ~60 | ~100 | ~90 (max 15) | ~50 | ~30 |
| critical | ~60 | ~100 | ~90 (max 15) | ~50 | ~40 |

## Content Rules

- **Paths only** in "Files touched" — never dump file contents into the handoff.
- **No secrets** — no tokens, passwords, API keys, or connection strings.
- One sentence for active task and next step.
- Create `.windsurf/handoff/` directory if it does not exist.
- After saving both files, emit exactly one line: `🔁 Context handoff saved → .windsurf/handoff/STATE.md`
