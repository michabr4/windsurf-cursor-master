---
description: Model Routing — classify task complexity and route to cheapest capable model before starting work
alwaysApply: true
---

# Model Routing Protocol — Claude Enterprise

## Monthly Budget Ceiling: $1,000

| Threshold | Action |
| --------- | ------ |
| < $750 (75%) | Normal routing applies |
| $750–$900 (75–90%) | Downgrade MEDIUM tasks to Haiku where output quality permits |
| $900–$1,000 (90–100%) | Suspend Opus entirely — route all HIGH tasks to Sonnet |
| ≥ $1,000 | Alert user before starting any task with estimated cost > $5 |

## Routing Table

| Complexity | Model | ≈Cost/1M input | ≈Cost/1M output | When to use |
| ---------- | ----- | -------------- | --------------- | ----------- |
| LOW | Claude Haiku 3.5 | $0.80 | $4.00 | Single-file edits, markdown, YAML/config, status checks, simple bug fixes |
| MEDIUM | Claude Sonnet 4 | $3.00 | $15.00 | Multi-file changes, API integration, test writing, new feature in existing module |
| HIGH | Claude Opus 4 | $15.00 | $75.00 | New agent/system design, cross-service breaking changes, architecture decisions |

## Decision Rules

**Route to Haiku when ALL of the following are true:**

- Changes touch ≤ 2 files
- No new dependencies added
- No schema or interface changes
- Task spec is under 200 tokens
- No `complexity: "HIGH"` tag on the task

**Route to Opus ONLY when ALL of the following are true:**

- Task is tagged `complexity: "HIGH"` AND
- Designing a new system, agent, or pipeline from scratch OR cross-service breaking change AND
- Expected to touch ≥ 5 files or add a new integration layer AND
- Monthly spend < $900 (budget gate)

**Route to Sonnet** for everything else (default).

## Why This Matters

Routing 60% of tasks to Haiku instead of Sonnet = **~4x cost reduction** on those tasks. Keeping Opus rare is critical — one Opus session costs ~30× a Haiku session.

| Scenario | Cost/session | 100 sessions/month |
| -------- | ------------ | ------------------ |
| All Sonnet | ~$0.05 | ~$5/month |
| 60% Haiku + 40% Sonnet | ~$0.025 | ~$2.50/month |
| 5% Opus misrouted (5 sessions) | +$1.20 | +$1.20/month |
| **Budget ceiling headroom** | — | **~$992 remaining for enterprise overhead** |

## Routing Telemetry

Emit exactly one line at the start of your first substantive response for any non-trivial task:

`[ROUTING] task="<3-word summary>" complexity=LOW|MEDIUM|HIGH routed_to=haiku|sonnet|opus`

Omit for pure conversational exchanges (≤2 turns, no file edits). This feeds the adaptive routing audit — data collected here identifies mis-routed tasks and informs threshold tuning.
