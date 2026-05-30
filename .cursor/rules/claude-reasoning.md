---
description: Claude Reasoning Protocol — when to apply reasoning-first approach and model routing by task type
globs: "agents/**/*.py,agents/**/*.ts,platforms/**/*.ts,platforms/**/*.py,sdm-files/**/*.py"
alwaysApply: false
---

# Claude Reasoning Protocol for Cursor

## When to Use Reasoning-First Approach

Use reasoning-first (think before coding) for:
- New agent `run()` methods or orchestration loops
- Integration with external APIs (Salesforce, Helix, Webex, ServiceNow)
- Authentication and token refresh flows
- Data transformation logic spanning more than 50 lines
- Any code touching customer data (PII, ticket data, financial)
- Debugging integration failures with unclear root cause

Do NOT use reasoning-first for:
- Single-function edits or simple refactors
- Config changes or renaming
- Adding log statements or docstrings
- Formatting changes

## Reasoning-First Pattern

Before generating code for a complex task, Claude must:

1. Restate the problem in its own words (reveals misunderstandings)
2. Identify the 2-3 main implementation approaches
3. Select the recommended approach and explain why
4. List the top 3 risks or edge cases for the chosen approach
5. Then write the code based on that reasoning

## Model Routing by Task Type

| Task Type | Model |
|-----------|-------|
| Complex agent logic, orchestration | Claude Opus 4 |
| Standard implementation, APIs, scripts | Claude Sonnet 4.5 |
| Quick fixes, formatting, small patches | Claude Haiku 3.5 |
| Security review, auth flows | Claude Opus 4 |
| Test generation | Claude Sonnet 4.5 |

## Extended Thinking Activation

Activate extended thinking for tasks where:
- The Comms Bridge task JSON contains `"complexity": "high"`
- You are implementing a new agent's core logic
- You are writing auth/token management code
- You are designing a data schema used across multiple agents

## Task Complexity Signal

When starting work on a new task, declare complexity:

```
Complexity: [LOW | MEDIUM | HIGH]
Task type: [IMPLEMENT | DEBUG | REFACTOR | DESIGN | REVIEW]
Use extended thinking: [YES | NO]
```

For HIGH complexity: show reasoning approach before producing code.
