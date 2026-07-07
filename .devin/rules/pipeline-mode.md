---
description: Pipeline Mode — smart auto-chain configuration; defines fast-path vs review-path for all tasks sent to Cursor
alwaysApply: true
---

# Pipeline Mode: Smart Auto-Chain

## Active Mode

**SMART AUTO-CHAIN** — Cursor auto-executes the next queued task when `requires_review: false`. Cursor pauses and awaits Windsurf sign-off when `requires_review: true`.

## Setting Task Path

Every task JSON sent to Cursor MUST include `requires_review` and `fast_path` fields.

### Fast Path — Cursor continues automatically

```json
"requires_review": false,
"fast_path": true
```

Use fast path ONLY when ALL of these are true:

- `complexity` is `LOW` or `MEDIUM`
- `model` is `haiku` or `sonnet`
- Task is a single-file edit, test run, formatter pass, or config change
- No security-sensitive code is touched (no auth, encryption, secrets, migrations)
- `out_of_scope` is explicitly defined
- No approval-needed commands required (see `cursor-execution-fence.md`)

### Review Path — Cursor stops and waits

```json
"requires_review": true,
"fast_path": false
```

Always use review path when:

- `complexity` is `HIGH` or `model` is `opus`
- Task touches auth, encryption, key management, or secrets
- Task modifies `.env`, `.comms/schema.md`, or any CI/CD config
- Task result determines the spec for the next task (architectural branch point)
- Task requires any approval-needed command (git push, migrations, new packages)

## Batch Design Rule

For every fast-path batch, include at most ONE review-path task at the end as a checkpoint. A batch of all-review-path tasks negates the async benefit — split into smaller units or promote to Windsurf-side work.

## Windsurf Monitoring Responsibility

- Monitor outbox ONLY for tasks where `requires_review: true`
- Do NOT intervene on fast-path tasks mid-execution — trust the chain
- If a fast-path task returns `status: "blocked"`, treat it as review-path immediately and respond before Cursor proceeds
