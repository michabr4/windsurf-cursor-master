---
description: Task spec discipline — how Windsurf must write tasks for Cursor to minimize LLM usage
---

# Task Spec Standard

Every task I (Windsurf) send to Cursor via `.comms/` must follow this format to eliminate clarification rounds and enable 1-shot execution.

## Required Spec Elements

A complete `spec` field must include ALL of the following:

1. **Exact files to touch** — list every file by path; never say "find the relevant file"
2. **What to do in each file** — function names, class names, or interface contracts for new code
3. **Expected output** — what does "done" look like? (e.g., test passes, endpoint returns X, file contains Y)
4. **What NOT to change** — put in `out_of_scope` array (prevents scope creep = fewer correction tokens)

## Required Metadata Fields

Always set these fields — never omit:

| Field | Rule |
|-------|------|
| `model` | Set per routing table in schema.md. Default `sonnet`. Never default to `opus` for simple work. |
| `complexity` | `LOW` for edits <50 lines. `MEDIUM` for new features. `HIGH` for auth/arch/debugging. |
| `files_to_read` | Only files Cursor genuinely needs. Over-including wastes context. |
| `out_of_scope` | List files/concerns explicitly excluded. Prevents unintended drift. |

## Batching Rule

Group 3–5 related tasks into a single session using `depends_on` chains rather than issuing 1 task per session. Each new Cursor session startup costs context. Chain them:

```
TASK-001 (depends_on: null) → TASK-002 (depends_on: TASK-001) → TASK-003 (depends_on: TASK-002)
```

Cursor will execute all three in one session without restarting.

## Bad vs Good Spec Examples

### Bad (vague, guarantees clarification rounds)
```
"spec": "Build the API integration for Mimir. Add the necessary routes and client."
```

### Good (bounded, 1-shot executable)
```
"spec": "Create backend/src/integrations/mimirClient.ts. Export a typed function getMimirDevices(customerId: string): Promise<MimirDevice[]> that calls GET https://mimir-prod.cisco.com/api/mimir/NP/devices with Bearer token from MIMIR_CLIENT_ID/MIMIR_CLIENT_SECRET OAuth2 flow. Add GET /api/mimir/devices/:customerId route in backend/src/routes/mimir.ts that calls this function and returns the response JSON. Done = curl /api/mimir/devices/test returns 200.",
"files_to_read": ["backend/src/routes/index.ts", "backend/src/integrations/"],
"out_of_scope": ["frontend", "database migrations"],
"model": "sonnet",
"complexity": "MEDIUM"
```

## When to Escalate to Opus

Only use `"model": "opus"` when the task has:
- Novel authentication/token flow not seen before in this codebase
- Cross-cutting architectural decisions with downstream consequences
- Root cause debugging where symptoms are misleading
- Security-sensitive code (auth, encryption, key management)

All other tasks: `sonnet` or `haiku`.
