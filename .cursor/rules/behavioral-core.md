---
description: Behavioral Core — no-restatement, read-dedup, tool-batching, result-compression, output-sanitization, auto-chain, autonomous-no-prompt
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

**BLOCKED/FAILED:** `{ id, status:"blocked", summary, details:"attempted+needed", files_changed:[], issues:[{issue,fix}], completed_at }` — never include file contents, stack traces >5 lines, or rule restatements.

## 5 · Output Sanitization

Before writing to `.comms/outbox/`, `.session-logs/`, or any result file, scan for and replace with `[REDACTED — <type>]`:
- AWS keys: starts with `AKIA`, `AGPA`, `AIDA`, `AROA`, `ASIA`
- Stripe: `sk_live_`, `pk_live_`, `sk_test_`, `pk_test_`
- Google API: `AIza` + 35 chars · GitHub tokens: `ghp_`, `gho_`, `ghu_`, `ghs_`, `ghr_`
- JWTs: three base64 segments starting with `eyJ`
- Private keys: `-----BEGIN * KEY-----` blocks
- Connection strings with credentials: `://user:password@`
- Any env variable VALUE (variable NAMEs are safe)

## 6 · Auto-Chain

After task completes — if inbox has task T where `T.depends_on == completed.id` (or null) AND `T.fast_path == true`: auto-claim T, announce `"Auto-chaining → [T.id] — [T.title]"`, execute immediately.

Rules:
- `requires_review` absent/null = treat as `false` (autonomous default)
- Never skip an unsatisfied `depends_on` (prerequisite must be in `completed/`)
- Multiple fast-path tasks: execute in priority order (critical → high → medium → low)
- Session depth cap: **10 tasks** — then stop and surface a batch summary
- On `failed`: stop all auto-chaining, alert user, wait for instruction
- On `blocked`: auto-chain to other independent fast-path tasks if any; else stop and alert

End-of-chain: `"Chain done. [N] executed. [M] awaiting review. [Inbox clear | X remain.]"`

## 7 · Autonomous Mode — No Prompting

**Default: proceed without asking.** State assumptions inline as `[ASSUME] <assumption> — proceeding`, then execute. The user corrects output, not the plan.

**Hard-stop only for:**

1. Secret/credential required but absent from env
2. Command is on Execution Fence "Requires Explicit User Approval" list
3. Irreversible data loss with no rollback

Everything else — unclear scope, missing context, incomplete spec — assume and proceed.

**Self-correction loop (before escalating any failure):**

1. Tool call fails → retry once with a corrected approach
2. Second attempt fails → emit `[RETRY_FAILED] step=<name> error=<msg>` and continue remaining steps
3. Collect all failures in `RESULT.issues` — surface at the end, never interrupt mid-task

**Loop completion:** Run ALL steps of a multi-step task to completion before surfacing the result. No mid-task acknowledgment pauses unless hitting a hard-stop condition above.
