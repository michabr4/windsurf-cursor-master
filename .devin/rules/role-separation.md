---
description: Role separation decision tree — what goes to Windsurf, Cursor, or a script/automation
---

# Role Separation

Use this decision tree before assigning any work to avoid burning LLM tokens on tasks that don't need them.

## Decision Tree

```
1. Is this a file move, rename, git op, or status update?
   → Shell script / manual. No LLM.

2. Is this data processing, CSV transformation, or template generation?
   → Python script. No LLM. Only escalate to Cursor if the logic is novel.

3. Is this planning, roadmap design, task decomposition, or architecture?
   → Windsurf (me) only. Never send planning work to Cursor.

4. Is this a single-file edit, config change, or <50-line implementation?
   → Cursor with model: haiku. Provide exact file path in task spec.

5. Is this a multi-file feature implementation with clear scope?
   → Cursor with model: sonnet. Use files_to_read carefully.

6. Is this auth, orchestration, novel architecture, or security-critical code?
   → Cursor with model: opus, complexity: HIGH.
```

## What Windsurf Does (My Role)

- Plan and decompose work into bounded tasks
- Write task specs with exact file paths, expected outputs, and out_of_scope
- Review Cursor results and decide next steps
- Design system architecture and integration contracts
- Write Windsurf rules and workflows
- Manage task batching and session strategy

## What Cursor Does (Builder Role)

- Implement code per spec — no design decisions
- Write tests for new code
- Run linters and report results
- Report SUCCESS / PARTIAL / FAILED to outbox
- Ask for clarification before starting if spec is ambiguous (not during)

## What Neither Should Do (Automate It)

| Task | Automation |
|------|-----------|
| Move `.comms/` task files | `mcp3_claim_task` / `mcp3_submit_result` (MCP, not LLM reasoning) |
| Git commit + push | `git commit -m "type(scope): desc" && git push` |
| Rename files across a directory | Shell one-liner (`find . -name "*.old" -exec rename ...`) |
| Generate boilerplate from template | Python script with jinja2 |
| Download/upload data | `curl` or `wget`, no LLM |

## Anti-Patterns to Avoid

- **Windsurf sending "design + implement" tasks to Cursor** — split into two tasks: Windsurf designs, Cursor implements
- **Cursor making architectural decisions** — if spec is unclear, Cursor should block and ask, not guess
- **Using Opus for simple refactors** — even a "feels complex" refactor is likely Sonnet territory
- **New Cursor session for each small task** — batch 3–5 related tasks per session
- **Windsurf re-explaining context Cursor already knows** — use `files_to_read` to point at source of truth; don't duplicate in spec text
