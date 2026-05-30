---
description: AI Factory Agent Development Standards — file structure, trust tiers, and KPI logging requirements
globs: "agents/**/*.py,agents/**/*.md,agents/**/*.sh,agents/**/.env.example"
alwaysApply: false
---

# AI Factory Agent Development Standards

## Agent File Structure (Required)
Every agent in agents/ must follow this layout:
```
agents/[agent-name]/
  __init__.py
  agent.py          # Main agent class
  config.py         # Config and env loading
  tools/            # Tool functions
  tests/
    test_agent.py
    test_tools.py
  AGENT_CARD.md     # Updated as agent evolves
  .env.example      # All required env vars documented
```

## Agent Class Requirements
Every agent class must:
1. Have a clear `trust_tier` property (T1, T2, or T3)
2. Implement: `run()`, `validate_inputs()`, `handle_error()`
3. Log all decisions to stdout at INFO level
4. Never swallow exceptions silently — always log before re-raising
5. Print KPI metrics at end of each run (full format per `effectiveness-signals.md`):
   ```python
   print(
       f"[METRICS] agent={self.__class__.__name__} "
       f"records_in={records_in} records_out={records_out} "
       f"errors={error_count} duration={elapsed:.1f}s "
       f"trust_tier={self.trust_tier} hitl_required={hitl_required}"
   )
   ```
   T2 agents also include: `llm_calls={n} llm_fallbacks={n} output_fields_complete={pct:.0f}%`

## Trust Tier Rules
- **T1 (Full Autonomy):** Runs without human review — output must be idempotent
- **T2 (HITL):** Pauses at defined checkpoint and awaits approval before proceeding
- **T3 (Human-Triggered):** Only runs when explicitly invoked — no scheduling

## Environment Variables
- All agents load secrets from environment only (`python-dotenv`)
- Never read from hardcoded strings
- Always call `load_dotenv()` at the top of `config.py`
- Document every required var in `.env.example` with a comment

## Webex Message Pattern
```python
import os
import requests

def send_webex_message(room_id: str, message: str) -> bool:
    token = os.environ["WEBEX_BOT_TOKEN"]
    resp = requests.post(
        "https://webexapis.com/v1/messages",
        headers={"Authorization": f"Bearer {token}"},
        json={"roomId": room_id, "markdown": message},
        timeout=10
    )
    resp.raise_for_status()
    return True
```

## Helix API Pattern
```python
import os
import requests

HELIX_BASE = "https://api.helix.cisco.com"

def get_helix_milestones(project_id: str) -> list:
    token = os.environ["HELIX_API_TOKEN"]
    resp = requests.get(
        f"{HELIX_BASE}/projects/{project_id}/milestones",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15
    )
    resp.raise_for_status()
    return resp.json().get("milestones", [])
```

## Pre-Submission Checklist
Before submitting any agent build result:
- [ ] Agent class follows structure above
- [ ] Trust tier documented in AGENT_CARD.md and as class property
- [ ] `.env.example` updated with all new environment variables
- [ ] `tests/` directory exists with test_agent.py
- [ ] Happy path test passing
- [ ] Error path test passing
- [ ] No hardcoded credentials
- [ ] Full `[METRICS]` line printed at end of `run()` (per `effectiveness-signals.md`)
- [ ] `[TOKEN_CHECK]` validation runs before first API call (bots only)
- [ ] `[HITL_CHECKPOINT]` emitted at pause point (T2 agents only)
- [ ] `[CYCLE_TIME]` line printed at run exit
- [ ] `[OUTPUT_COVERAGE]` check run before output is returned
- [ ] AGENT_CARD.md updated — includes `## Effectiveness Signals` section
- [ ] Timeout on all HTTP calls
