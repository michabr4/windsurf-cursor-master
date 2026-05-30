---
description: Effectiveness Signals — instrument all code to emit measurable quality, health, and velocity signals
globs: "**/*.py,**/*.ts,**/*.js,**/*.mjs"
alwaysApply: false
---

# Effectiveness Signals — Builder Protocol

## Purpose

Every piece of code Cursor writes or modifies must be **instrumentable** — it must produce signals that allow humans and the Windsurf architect to assess whether the work is actually effective. This rule defines the exact patterns to use.

---

## 1. Agent KPI Line (Required for ALL agents)

Every `run()` method in every agent class MUST exit by printing a structured KPI line. This is the primary effectiveness signal for AI agents.

**Required format:**

```python
print(
    f"[METRICS] agent={self.__class__.__name__} "
    f"records_in={records_in} records_out={records_out} "
    f"errors={error_count} duration={elapsed:.1f}s "
    f"trust_tier={self.trust_tier} hitl_required={hitl_required}"
)
```

**Extended format for HITL agents (T2):**

```python
print(
    f"[METRICS] agent={self.__class__.__name__} "
    f"records_in={records_in} records_out={records_out} "
    f"errors={error_count} duration={elapsed:.1f}s "
    f"trust_tier={self.trust_tier} hitl_required={hitl_required} "
    f"llm_calls={llm_call_count} llm_fallbacks={llm_fallback_count} "
    f"output_fields_complete={output_coverage_pct:.0f}%"
)
```

**Rules:**
- Always capture `start_time = time.time()` at the top of `run()` and compute `elapsed = time.time() - start_time` before printing
- `hitl_required` is `True` for T2 agents, `False` for T1
- `llm_fallback_count` increments when the LLM returns empty, malformed, or off-topic output
- `output_coverage_pct` = required output fields present ÷ total required fields × 100
- Never print raw token values, API keys, or personal data in this line

---

## 2. Bot Token Pre-Validation (Required for ALL bots)

Every bot script that calls an external API with a bearer token MUST run a token check before the first API call. Expired tokens are the #1 failure mode for bots in this workspace.

**Required pattern:**

```python
import os
import requests
from datetime import datetime

def check_token_validity(token_env_var: str) -> dict:
    """Validate token is present and not returning 401. Returns signal dict."""
    token = os.environ.get(token_env_var, "")
    if not token:
        print(f"[TOKEN_CHECK] var={token_env_var} valid=False reason=missing")
        return {"valid": False, "reason": "missing"}

    # Lightweight probe — use a low-cost endpoint
    resp = requests.get(
        "https://webexapis.com/v1/people/me",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    if resp.status_code == 401:
        print(f"[TOKEN_CHECK] var={token_env_var} valid=False reason=401_unauthorized")
        return {"valid": False, "reason": "401_unauthorized"}

    print(f"[TOKEN_CHECK] var={token_env_var} valid=True status={resp.status_code}")
    return {"valid": True}


# Call at the top of main() BEFORE any business logic
token_status = check_token_validity("WEBEX_BOT_TOKEN")
if not token_status["valid"]:
    raise SystemExit(f"[ABORT] Token invalid — reason: {token_status['reason']}. Rotate token and update GitHub Secret.")
```

**Rules:**
- Call `check_token_validity` before ANY other network call
- If token is invalid, raise `SystemExit` with a clear human-readable message — do NOT silently continue
- The `[TOKEN_CHECK]` log line is the signal Windsurf reads to assess bot health
- Use a different probe endpoint if not Webex (adapt URL but keep the pattern)

---

## 3. Platform / Tool Build Health Check

For any TypeScript/React/Node project, after making code changes:

- Run `npm run build` and confirm exit code 0 before marking the task complete
- If the build fails, fix the error before reporting done — a broken build is a `partial` result, not `success`
- Include in the RESULT file's `details` field: `build: clean | warnings_only | errors`
- Include test count if tests exist: `tests: N passed, N failed`

**In RESULT JSON:**

```json
{
  "details": "...\n\nBuild health: clean (0 errors, 0 warnings)\nTests: 12 passed, 0 failed\nDev server: starts cleanly on localhost:5173"
}
```

---

## 4. HITL Checkpoint Signal (T2 agents)

When a T2 agent reaches its HITL checkpoint, it must emit a structured pause signal before stopping execution:

```python
print(
    f"[HITL_CHECKPOINT] agent={self.__class__.__name__} "
    f"checkpoint={checkpoint_name} "
    f"draft_output_path={output_path} "
    f"awaiting_approval=True "
    f"timestamp={datetime.utcnow().isoformat()}"
)
```

Log this to the governance log at `data/runs/{agent-name}/hitl-log.jsonl`:

```python
import json

def log_hitl_event(agent_name: str, event: dict) -> None:
    log_path = f"data/runs/{agent_name}/hitl-log.jsonl"
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a") as f:
        f.write(json.dumps({**event, "ts": datetime.utcnow().isoformat()}) + "\n")
```

---

## 5. Error Rate Instrumentation

Every agent and bot must maintain error counters. Use this pattern:

```python
error_count = 0

try:
    result = do_something()
except Exception as e:
    error_count += 1
    print(f"[ERROR] step=do_something error={type(e).__name__} msg={str(e)[:200]}")
    # Do NOT swallow — re-raise or handle explicitly
    raise
```

**Rules:**
- `error_count` feeds into the `[METRICS]` line
- Always include `step=` so the signal identifies WHERE the error occurred
- Truncate exception messages to 200 chars in logs (`str(e)[:200]`)
- Never log stack traces longer than 5 lines to stdout

---

## 6. Cycle Time Instrumentation

Track end-to-end cycle time for all agents. Measure from trigger to delivery:

```python
import time

cycle_start = time.time()

# ... all agent work ...

cycle_elapsed = time.time() - cycle_start
print(f"[CYCLE_TIME] agent={agent_name} seconds={cycle_elapsed:.1f} minutes={cycle_elapsed/60:.1f}")
```

For async/scheduled agents, also log the trigger-to-start latency if detectable.

---

## 7. Output Coverage Check

For agents that produce structured output (JSON, PPTX, Webex card), validate required fields are populated before emitting:

```python
REQUIRED_OUTPUT_FIELDS = ["summary", "delivery_health", "risks", "next_steps"]

def check_output_coverage(output: dict, required: list) -> float:
    present = sum(1 for f in required if output.get(f))
    pct = (present / len(required)) * 100
    print(f"[OUTPUT_COVERAGE] fields_required={len(required)} fields_present={present} coverage={pct:.0f}%")
    return pct

coverage = check_output_coverage(agent_output, REQUIRED_OUTPUT_FIELDS)
if coverage < 90:
    print(f"[WARN] Output coverage {coverage:.0f}% below 90% threshold")
```

---

## Acceptance Criteria Additions

The following signals MUST be present in any agent/bot code Cursor delivers. A result is **partial** (not `success`) if any of these are missing:

- [ ] `[METRICS]` line printed at every `run()` exit
- [ ] `[TOKEN_CHECK]` line printed before first API call (bots only)
- [ ] `[HITL_CHECKPOINT]` line printed at HITL pause point (T2 agents only)
- [ ] `[ERROR]` log pattern used in all except blocks
- [ ] `[CYCLE_TIME]` line printed at end of run
- [ ] Build is clean (`npm run build` or `python -m pytest` passes) before result is filed

---

## What NOT to Log

Never include in any `[METRICS]`, `[TOKEN_CHECK]`, or other signal line:

- Token values or partial token values
- API response bodies
- User PII (names, emails, phone numbers)
- Database connection strings
- Any string matching AWS key, JWT, or private key patterns

If a signal value would expose any of the above, replace with `[redacted]`.
