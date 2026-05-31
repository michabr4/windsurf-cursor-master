---
description: Behavioral Core — no-restatement, read-dedup, tool-batching, result-compression, output-sanitization, auto-chain
alwaysApply: true
---

## 1 · No Restatement
Never repeat the task spec, user request, or prior output. Jump directly to the result.
Never open with "You asked me to..." / "I will now..." / "Per the [rule]..." / "As you can see...".
If context is needed: cite `@filepath:line` — never quote the content itself.

## 2 · Read Deduplication
Each file is read at most once per session. Re-read only if: (a) file was edited since last read, (b) task explicitly says "re-read [filename]", or (c) last read was >120 min ago. If unsure whether content changed, check the edit diff — not a full re-read.

## 3 · Tool Call Batching
All independent tool calls MUST be parallel in a single turn. Issue sequentially ONLY when: Turn B's input depends on Turn A's output, Turn B is a write that must confirm a prior read before mutating, or Turn B is a destructive action requiring human approval.

## 4 · Result Compression

**LOW (haiku):** Three fields only — `{ id, status, summary, files_changed, completed_at }`. Omit `details`/`issues` unless there is one.

**MEDIUM (sonnet):** Add `details` as a bullet list — max 5 items, no prose paragraphs.

**HIGH (opus):** Full schema from `.comms/schema.md` — no compression.

**BLOCKED/FAILED (any complexity):**
```json
{ "id": "TASK-...", "status": "blocked", "summary": "one sentence", "details": "what was attempted + what is needed to unblock", "files_changed": [], "issues": [{"issue": "...", "fix": "..."}], "completed_at": "..." }
```
Never include: file contents, stack traces >5 lines, task spec restatements, rule explanations.

## 5 · Output Sanitization

Before writing to `.comms/outbox/`, `.session-logs/`, or any result file, scan for and replace with `[REDACTED — <type>]`:
- AWS keys: starts with `AKIA`, `AGPA`, `AIDA`, `AROA`, `ASIA`
- Stripe: `sk_live_`, `pk_live_`, `sk_test_`, `pk_test_`
- Google API: `AIza` + 35 chars · GitHub tokens: `ghp_`, `gho_`, `ghu_`, `ghs_`, `ghr_`
- JWTs: three base64 segments starting with `eyJ`
- Private keys: `-----BEGIN * KEY-----` blocks
- Connection strings with credentials: `://user:password@`
- Any env variable VALUE (variable NAMEs are safe)

Safe to write: file paths, function/class names, error messages (values stripped), HTTP status codes, aggregate counts, task IDs, commit SHAs.

## 6 · Auto-Chain

After task completes — if inbox has task T where `T.depends_on == completed.id` (or null) AND `T.requires_review == false` AND `T.fast_path == true`: auto-claim T, announce `"Auto-chaining → [T.id] — [T.title]"`, execute immediately.

Rules:
- `requires_review` absent/null = treat as `true` (safe default: pause for review)
- Never skip an unsatisfied `depends_on` (prerequisite must be in `completed/`)
- Multiple fast-path tasks: execute in priority order (critical → high → medium → low)
- Session depth cap: **10 tasks** — then stop and surface a batch summary
- On `failed`: stop all auto-chaining, alert user, wait for instruction
- On `blocked`: auto-chain to other independent fast-path tasks if any; else stop and alert

End-of-chain: `"Auto-chain complete. [N] tasks executed. [M] task(s) awaiting Windsurf review. [Inbox clear | X review-path tasks remain.]"`
