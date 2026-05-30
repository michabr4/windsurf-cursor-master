---
description: Tool Call Batching — always batch independent tool calls; never make sequential calls when parallel is possible
alwaysApply: true
---

# Tool Call Batching Protocol

## Core Rule

**All independent tool calls MUST be made in parallel in a single turn.**
A tool call is independent if its inputs do not depend on the output of another tool
call in the same batch.

## Mandatory Parallel Patterns

These MUST be batched — never issued sequentially:

| Scenario | Correct pattern |
|----------|----------------|
| Reading multiple files at session start | Single turn: read all at once |
| Listing fields + querying records in Airtable | One turn with both calls |
| Writing 2 new rule files | One turn: create both simultaneously |
| Running a lint check + reading a rule file | One turn: both in parallel |
| Checking inbox + reading active task | One turn: batch both |

## Sequential (Only When Dependent)

Issue sequentially ONLY when:

- Turn B's input depends on Turn A's output (e.g., use a returned file ID in the next call)
- Turn B is a write that must confirm Turn A's read before mutating
- Turn B is a destructive action that requires human approval first

## Why This Matters for Tokens

Each tool call round-trip re-invokes the model with the full context window.
Batching 3 parallel reads into 1 turn instead of 3 sequential turns =
**2 fewer context reloads** per cluster.

At ~5,000 tokens/context reload × 2 eliminated reloads × 4 task clusters/session
= **40,000 tokens/session** eliminated in long sessions.

Even in short sessions: 3 clusters × 2 extra reloads eliminated = ~30,000 tokens/session.
