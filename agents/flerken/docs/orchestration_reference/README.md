# Orchestration reference (from delivery-workbench)

These YAML specs document multi-step email workflows with **human gates** (no send/move without approval). Flerken runs a single Python pipeline today; use these as patterns when extending Flerken or when using delivery-workbench for SDM orchestration.

| File | Purpose |
| --- | --- |
| `email-inbox-review.yaml` | Full review: triage, summarize, actions, draft replies, organize proposal |
| `email-morning-digest.yaml` | Morning read-only job (excludes draft/organize steps) |

Source: `tools/delivery-workbench/orchestration/` (unchanged by consolidation).
