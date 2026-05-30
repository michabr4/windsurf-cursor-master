---
description: Model Routing — classify task complexity and route to cheapest capable model before starting work
alwaysApply: true
---

# Model Routing Protocol

## Routing Table

| Complexity | Model  | Cost/1M input | Criteria |
|------------|--------|---------------|----------|
| LOW        | haiku  | ~$0.25        | Single-file edits, markdown updates, YAML/config, status checks, simple bug fixes |
| MEDIUM     | sonnet | ~$3.00        | Multi-file changes, API integration, test writing, new feature in existing module |
| HIGH       | opus   | ~$15.00       | New agent/system design, cross-service breaking changes, architecture decisions |

## Decision Rules

**Route to haiku when ALL of the following are true:**

- Changes touch ≤ 2 files
- No new dependencies added
- No schema or interface changes
- Task spec is under 200 tokens
- No `complexity: "HIGH"` tag on the task

**Route to opus when ANY of the following is true:**

- Task is tagged `complexity: "HIGH"`
- Designing a new system, agent, or pipeline from scratch
- Change requires breaking cross-service contracts
- Task explicitly involves multi-system orchestration design

**Route to sonnet** for everything else (default).

## Why This Matters

Routing 60% of tasks to haiku instead of sonnet = **~5x cost reduction** on those tasks.

| Scenario               | Old cost | New cost | Saving |
|------------------------|----------|----------|--------|
| 10 tasks, all sonnet   | $0.30    | —        | —      |
| 6 haiku + 4 sonnet     | —        | $0.075   | 75%    |
| 20 sessions/month      | $6.00    | $1.50    | $4.50/mo |
