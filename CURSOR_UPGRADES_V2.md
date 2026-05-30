# Cursor Builder Upgrades — Version 2

> **Additive to:** `CURSOR_SETUP_PLAN.md` (V1, May 26, 2026)  
> **Issued:** May 27, 2026  
> **Status:** Active — these upgrades override V1 where they conflict  
> **What this covers:** Claude model routing, new builder rules, Anthropic MCP server, AI Factory build standards, session start protocol, structured output format.

---

## Summary of Changes from V1

| Category | V1 | V2 Change |
|----------|----|-----------|
| Model routing | Claude Sonnet 4 for everything | Opus 4 for reasoning, Sonnet 4.5 for build, Haiku for quick tasks |
| Extended thinking | Not configured | Enabled for complex implementation tasks (see rules below) |
| Anthropic MCP | Not configured | Add Anthropic API as MCP server for inline reasoning |
| Session start | No protocol | Check Comms Bridge for pending tasks at session open |
| Report format | Ad-hoc result descriptions | Structured output format required |
| AI Factory rules | None | Agent development standards + test-first requirement |
| New .cursor/rules | Builder-role only | +3 rules: ai-factory-standards, claude-reasoning, test-first |

---

## Part 1: Claude Model Routing Strategy

### 1.1 Model Assignment by Task Type

Configure Cursor to route to these models based on task category:

| Task Type | Model | When to Use |
|-----------|-------|-------------|
| Complex agent logic, architectural implementation | Claude Opus 4 | Multi-step reasoning, stateful agents, integration design |
| Standard code generation, scripting, APIs | Claude Sonnet 4.5 | Most implementation tasks |
| Quick fixes, formatting, single-function edits | Claude Haiku 3.5 | Linting fixes, docstring additions, small patches |
| Security review, CodeGuard analysis | Claude Opus 4 | Never skip Opus for security-critical code |
| Test generation | Claude Sonnet 4.5 | Standard, unless testing complex auth flows |

### 1.2 Extended Thinking Activation

Use extended thinking (when available in Cursor) for:

- Any task tagged with `complexity: high` in the Comms Bridge task JSON
- Implementing new agent `run()` methods or orchestration loops
- Writing auth flows or token management code
- Debugging integration failures with unclear root cause
- Designing data schemas that will be used across multiple agents

Do NOT use extended thinking for:
- Formatting, renaming, or simple refactors
- Adding docstrings
- Moving files or updating configs

### 1.3 How to Signal Task Complexity to Claude

When the Comms Bridge task has no complexity tag, use this pattern in your first message to Claude:

```
Complexity: [LOW | MEDIUM | HIGH]
Task type: [IMPLEMENT | DEBUG | REFACTOR | DESIGN | REVIEW]
Use extended thinking: [YES | NO]

[task description]
```

For HIGH complexity tasks, Claude should show its reasoning approach before producing code.

---

## Part 2: New Cursor Rules

Add these three rule files to `.cursor/rules/`. They extend and refine the existing rules from V1.

### Rule File 1: `ai-factory-standards.md`

```markdown
# AI Factory Agent Development Standards

## Agent File Structure (Required)
Every agent in agents/ must follow this layout:
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

## Agent Class Requirements
Every agent class must:
  1. Inherit from or follow the pattern in tools/agentic-starter-kit/
  2. Have a clear trust_tier property (T1, T2, or T3)
  3. Implement: run(), validate_inputs(), handle_error()
  4. Log all decisions to stdout at INFO level
  5. Never swallow exceptions silently — always log before re-raising

## Trust Tier Rules
  T1 (Full Autonomy): Agent runs without human review — output must be idempotent
  T2 (HITL): Agent pauses at defined checkpoint and awaits approval before proceeding
  T3 (Human-Triggered): Agent only runs when explicitly invoked — no scheduling

## Required Environment Variables Pattern
  All agents load secrets from environment only (python-dotenv).
  Never read from hardcoded strings.
  Always call load_dotenv() at the top of config.py.
  Document every required var in .env.example with a comment describing what it's for.

## KPI Instrumentation
  Every agent must print its KPI metrics at end of each run:
    print(f"[METRICS] Records processed: {n}, errors: {e}, duration: {t:.1f}s")
```

### Rule File 2: `claude-reasoning.md`

```markdown
# Claude Reasoning Protocol for Cursor

## When to Ask Claude to Reason Before Coding
Use this protocol before writing implementation code for:
  - New agent logic (any agent run() method)
  - Integration with external APIs (Salesforce, Helix, Webex, SNOW)
  - Authentication and token refresh flows
  - Data transformation or normalization logic spanning >50 lines
  - Any code touching customer data (PII, ticket data, financial)

## Reasoning-First Pattern
Before generating code for a complex task, ask Claude to:
  1. Restate the problem in its own words (reveals misunderstandings)
  2. Identify the 2-3 main implementation approaches
  3. Select the recommended approach and explain why
  4. List the top 3 risks or edge cases for the chosen approach
  Then: write the code based on that reasoning.

## Extended Thinking Prompt Prefix
For HIGH complexity tasks, prefix your request with:
  "Think step by step before writing code.
   First explain your approach, identify edge cases, then implement."

## Do NOT Reason First For
  - Single-function edits
  - Config changes
  - Adding log statements
  - Formatting or naming changes
```

### Rule File 3: `test-first.md`

```markdown
# Test-First Development Protocol

## Requirement
For any new function, class, or agent component: write the test BEFORE the implementation.

## Process
  1. Read the spec's "Test Criteria" section from the Comms Bridge task
  2. Write failing tests that cover each criterion
  3. Implement the code to make tests pass
  4. Report: "Tests written first: [list], all passing: [YES/NO]" in result

## Test File Conventions
  tests/test_[module].py
  Test functions: test_[what_it_does]_[when_condition]()
  Example: test_delivery_tracker_returns_empty_when_no_milestones()

## Minimum Test Coverage Per Agent
  - Happy path: 1+ tests
  - Error path (API down, bad input): 1+ tests
  - Auth failure: 1 test
  - Edge case (empty data, null fields): 1+ tests

## Skipping Tests
Only skip with explicit permission from Windsurf in the task spec.
Always note in report: "Tests skipped: [reason]"
```

---

## Part 3: Anthropic MCP Server Configuration

Add the Anthropic API as an MCP server in Cursor. This enables Claude to be called directly during builds for inline reasoning tasks — separate from the primary chat model.

### 3.1 When to Use the Anthropic MCP Server

Use it (via tool call in the agent code you're building) when:
- Building agents that need a reasoning step embedded in their logic
- The agent itself calls Claude to analyze data before acting
- You need to test Claude prompts with real API calls during development

Do NOT use it for your own implementation reasoning (that's what the model routing in Part 1 covers).

### 3.2 Cursor MCP Config Addition

Add to `~/.cursor/mcp.json` (merge with existing):

```json
{
  "mcpServers": {
    "anthropic": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server"],
      "env": {
        "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}"
      }
    }
  }
}
```

**Security note:** `ANTHROPIC_API_KEY` must come from the environment, never hardcoded. Add to `.env` and ensure `.env` is in `.gitignore`.

### 3.3 Anthropic MCP Available Tools

Once configured, these tools are available in Cursor's agent mode:

| Tool | Use Case |
|------|----------|
| `create_message` | Ask Claude to analyze data, generate summaries, make decisions |
| `count_tokens` | Estimate prompt size before sending |

Use these in agent code where the agent itself needs a reasoning step:

```python
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

def analyze_delivery_risk(milestone_data: dict) -> str:
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"Analyze this milestone data for delivery risk: {milestone_data}"
        }]
    )
    return message.content[0].text
```

---

## Part 4: Session Start Protocol

Every new Cursor session begins with this protocol:

### Step 1: Check Comms Bridge

```
1. Open .comms/inbox/ — are there pending tasks?
2. Open .comms/active/ — is there a task in progress?
3. If active task exists: resume it. Do not start new work.
4. If inbox has tasks: claim the highest-priority one (mcp3_claim_task).
5. If both empty: notify Windsurf via the comms bridge that Cursor is idle.
```

### Step 2: Load Task Context

When claiming a task, read:
- The task JSON (priority, phase, files_to_read)
- Any referenced ADR in `ADR_LOG.md`
- The domain design doc if specified (e.g., `domains/mgm-resorts/DESIGN.md`)
- The relevant spec in `WINDSURF_ARCHITECT_PLAN_V2.md` spec backlog

### Step 3: Acknowledge to Windsurf

Before starting implementation, post a brief acknowledgment comment in `.comms/transcript.md`:

```
[CURSOR][TASK-2026-XXXX-NNN] Claimed. Starting: [task title]. 
Files: [list]. Dependencies: [any blockers]. ETA: [rough estimate].
```

---

## Part 5: Structured Output Format

All Cursor result reports must use this format. This replaces the ad-hoc free-text results from V1.

### RESULT-*.json Content Standards

The `details` field in every `mcp3_submit_result` call must use this structured format:

```
STATUS: [SUCCESS | PARTIAL | FAILED | BLOCKED]

COMPLETED:
  - [specific thing 1 that was done]
  - [specific thing 2]

TEST RESULTS:
  Tests written: [YES | NO | SKIPPED — reason]
  Tests passing: [number]/[total]
  Failing tests: [list or "None"]

FILES CHANGED:
  [path]: [what changed]
  [path]: [what changed]

ISSUES FOUND:
  [BLOCK] [description — requires Windsurf decision]
  [WARN]  [description — Cursor handled it but flagging]
  [INFO]  [observation, no action needed]

CURSOR ASSUMPTIONS (if any):
  [Any decision Cursor made that wasn't in the spec]

WINDSURF REVIEW NEEDED:
  [Specific items that require Windsurf sign-off before next step]
  OR: "None — task complete and verified"

NEXT SUGGESTED TASK:
  [What Cursor recommends as the natural follow-on, or "Awaiting Windsurf direction"]
```

---

## Part 6: AI Factory Build Standards

These apply to all 34 agents in the AI Factory. They enforce consistency across the multi-session, multi-IDE build pipeline.

### 6.1 Agent Development Checklist (Before Submitting Result)

```
[ ] Agent class follows pattern in ai-factory-standards.md rule
[ ] Trust tier documented in AGENT_CARD.md and as class property
[ ] .env.example updated with all new environment variables
[ ] tests/ directory exists with at minimum: test_agent.py
[ ] Happy path test passing
[ ] Error path test passing
[ ] No hardcoded credentials (CodeGuard check)
[ ] KPI metrics printed at end of run()
[ ] README.md or AGENT_CARD.md updated to reflect current state
[ ] No imports from outside the agent's own directory except:
    - Shared integration clients (when they exist)
    - Standard library and pip packages
```

### 6.2 Integration Client Usage

Until the shared integration layer is built (Phase 3), each agent implements its own API clients. When the shared layer is ready (SPEC-035), all agents will be refactored to use it. Do not build shared clients prematurely — wait for the Windsurf spec.

### 6.3 Webex Bot Pattern

All bots sending Webex messages must:

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

Never use `requests.get/post` with hardcoded tokens. Always use `os.environ["WEBEX_BOT_TOKEN"]`.

### 6.4 Helix API Pattern

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

---

## Part 7: Domain Context Loading

When working on tasks in a specific domain, load the domain design doc before starting:

| Domain | Design Doc | When to Read |
|--------|------------|--------------|
| MGM Resorts | `domains/mgm-resorts/DESIGN.md` | Any task tagged customer=MGM |
| DD (Digital Door) | `domains/dd/DESIGN.md` | Any task tagged customer=DD |
| AI Factory | `AI_FACTORY_IMPLEMENTATION_PLAN.md` | Any agent build task |
| Shared Platform | `platforms/serviceflow-sdm/docs/ARCHITECTURE.md` | Any Helix or ServiceFlow task |

If the domain design doc doesn't exist yet, note it in the result as `[WARN] Domain design doc not found: [path] — Windsurf should create before next task in this domain.`

---

## Part 8: Security Protocol (Reinforced from V1)

These are non-negotiable. Violation of any of these is a BLOCK-level issue to be reported immediately:

1. **No secrets in source.** All credentials via `os.environ`. No exceptions.
2. **No plaintext tokens in logs.** Never log the value of any `TOKEN`, `KEY`, `SECRET`, or `PASSWORD` variable.
3. **No SHA-1, MD5, DES, RC4, AES-CBC, AES-ECB.** CodeGuard rule enforced.
4. **Input validation before processing.** Validate types, lengths, and format before acting on external data.
5. **Timeout on all HTTP calls.** Never `requests.get(url)` without `timeout=N`.
6. **Rate limit awareness.** All API calls must handle 429 responses with retry-after logic.

If you encounter existing code violating any of these: flag it as `[BLOCK] Security violation found` in the result and do not proceed with that code path until Windsurf reviews.

---

## Appendix: Quick Reference Card

Keep this in mind at all times in Cursor:

```
CHECK COMMS BRIDGE → Claim task → Read spec + ADR + domain doc
LOAD MODEL: Opus (complex) | Sonnet (standard) | Haiku (quick)
REASON FIRST if complexity=HIGH
WRITE TESTS BEFORE CODE
FOLLOW ai-factory-standards.md for any agent work
NO SECRETS IN SOURCE — ever
REPORT with structured format (Part 5)
```

---

*Cursor Upgrades V2. Additive to V1 Cursor Setup Plan. Maintained by Windsurf.*  
*Last updated: 2026-05-27*
