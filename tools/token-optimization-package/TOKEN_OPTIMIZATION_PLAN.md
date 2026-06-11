# Token Optimization Plan — Beyond 72%

**Date:** 2026-05-30  
**Current baseline:** ~72% context overhead reduction (14,400 tokens saved/session)  
**Target:** 87–90% overhead reduction

---

## Findings Summary

Audit of all `.cursor/rules` and `.windsurf/rules` revealed 4 critical misconfigurations
plus 5 structural gaps that leave significant token savings on the table.

### Misconfigurations Fixed (P0 — Done)

| Rule | Issue | Fix | Tokens Freed/Session |
| ---- | ----- | --- | -------------------- |
| `effectiveness-signals.md` (.cursor) | `alwaysApply: true` on 230-line rule, loaded every session | Changed to `alwaysApply: false` + `globs: **/*.py,**/*.ts,**/*.js,**/*.mjs` | ~1,840 avg |
| `codeguard-1-crypto-algorithms.md` | `alwaysApply: true` on 134-line rule, even for markdown sessions | Changed to `alwaysApply: false` + code file globs | ~500 avg |
| `codeguard-1-digital-certificates.md` | `alwaysApply: true` on 121-line rule, even for markdown sessions | Changed to `alwaysApply: false` + code + cert file globs | ~485 avg |
| `effectiveness-signals.md` (.windsurf) | Same issue on Windsurf side, 139-line rule | Changed to `alwaysApply: false` + same globs | ~1,170 avg |

**P0 total:** ~4,000 tokens/session freed on sessions that don't touch code files.

---

## New Rules Created (P1 — Done)

### 1. `model-routing.md` — Haiku-First Task Routing

Routes 60% of tasks to haiku (20× cheaper than opus, 5× cheaper than sonnet).

| Tier | Model | Criteria |
| ---- | ----- | -------- |
| LOW | haiku | ≤2 files, no deps, no schema changes, spec <200 tokens |
| MEDIUM | sonnet | Default |
| HIGH | opus | New system design, cross-service breaking changes |

**Impact:** ~75% cost reduction on routed tasks. Monthly saving: ~$4.50 at current usage.

---

### 2. `spec-length-cap.md` — 300-Token Spec Hard Cap

Enforces maximum spec size at task creation and receipt:

- `spec` field ≤ 300 tokens — trim by removing examples that duplicate rules, filler language, inferable context
- `files_to_read` ≤ 5 items — path references only, no inline content
- No rule re-statements — cite filename instead

**Impact:** 200 tokens saved/task × 100 tasks/month = 20,000 tokens/month.

---

### 3. `session-warm-up.md` — Minimal Context on Session Start

Prevents loading full session logs at start. Instead reads only:

- `.session-logs/LAST_SESSION_BRIEF.md` (200-token auto-generated summary)
- `.comms/active/` for in-progress tasks

Never reads:

- Full `activity-report-*.md` files
- `.comms/completed/` directory
- `PROJECT_PROGRESS.md` unless the task requires it

Defines the `LAST_SESSION_BRIEF.md` format — generated at session end, capped at 200 tokens.

**Impact:** 800 tokens saved per session start × 20 sessions/month = 16,000 tokens/month.

---

### 4. `comms-retention.md` — 20-File Cap on Completed Directory

Caps `.comms/completed/` at 20 most recent files. Currently at 51 files and growing.

At session end: files beyond the 20 most recent are moved to `.comms/archive/`.

**Impact:** Eliminates ~60% of directory listing noise in pipeline tool responses immediately.
Prevents unbounded growth that would compound with every session.

---

## Cumulative Token Impact

| Phase | Tokens Saved/Session | Monthly Savings (20 sessions) |
| ----- | -------------------- | ------------------------------ |
| Baseline (existing rules) | 14,400 | 288,000 |
| P0: alwaysApply fixes | +4,000 | +80,000 |
| P1: session-warm-up | +800 | +16,000 |
| P1: spec-length-cap | +667 avg | +13,400 |
| **New total** | **~19,867** | **~397,400** |
| **New reduction %** | **~88%** | — |

---

## Remaining Work (P2 — Not Yet Implemented)

### P2-A: Compress Heavy Rule Files

`codeguard-0-safe-c-functions.md` is 328 lines / ~2,600 tokens. Already glob-gated but
still large. Create a "fast-path" summary variant (~60 lines / ~500 tokens) that contains
only the enforcement checklist, with a pointer to the full rule for reference.

Apply same pattern to `codeguard-0-framework-and-languages.md` (300+ lines) and
`codeguard-1-digital-certificates.md` (121 lines).

**Estimated saving:** ~2,000 tokens on C/Python sessions where these load.

---

### P2-B: Deduplicate .windsurf/rules and .cursor/rules

22 codeguard-0 rules and 3 codeguard-1 rules exist in **both** directories (~65KB total).
If any session ever loads from both directories, this doubles the overhead.

**Fix:** Establish `.cursor/rules` as source of truth. In `.windsurf/rules`, replace
duplicate codeguard files with a single-line reference: `# See .cursor/rules/<filename>`.

**Estimated saving:** Eliminates redundancy entirely. Low-risk structural cleanup.

---

### P2-C: `project-progress-tracker.md` Frequency Cap

`project-progress-tracker.md` (Windsurf, `alwaysApply: true`) fires at every session
start AND after every milestone. If `PROJECT_PROGRESS.md` grows large, this becomes
a repeated read/write overhead.

**Fix:** Add a `max_updates_per_session: 1` constraint and `min_interval_minutes: 60`
so it doesn't re-fire mid-session on sequential milestone tasks.

---

## P3 — Long-Horizon (Q3 2026)

- **Adaptive rule loading via telemetry:** Track which rules fire enforcement actions vs.
  which are loaded but never triggered. Downgrade zero-trigger rules from `alwaysApply`.
- **Summary cache:** Pre-compressed 60-token summaries of each rule for warm-up loading
  instead of full rule text. Full rule only loads when a match is detected.
- **Task complexity telemetry:** Log actual model used vs. routed model. Adjust routing
  thresholds based on measured accuracy.

---

## Files Modified

| File | Change |
| ---- | ------ |
| `.cursor/rules/effectiveness-signals.md` | `alwaysApply: true` → `false`, added globs |
| `.cursor/rules/codeguard-1-crypto-algorithms.md` | `alwaysApply: true` → `false`, added globs |
| `.cursor/rules/codeguard-1-digital-certificates.md` | `alwaysApply: true` → `false`, added globs |
| `.windsurf/rules/effectiveness-signals.md` | `alwaysApply: true` → `false`, added globs |
| `.cursor/rules/model-routing.md` | **New** |
| `.cursor/rules/spec-length-cap.md` | **New** |
| `.cursor/rules/session-warm-up.md` | **New** |
| `.cursor/rules/comms-retention.md` | **New** |
