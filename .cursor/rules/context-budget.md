---
description: Context Budget — hard caps on files_to_read and rule loading to minimize token consumption
alwaysApply: true
---

# Context Budget Rule

## files_to_read Hard Caps

| Model | Max files to read |
|-------|------------------|
| haiku | 3 |
| sonnet | 6 |
| opus | 10 |

If a task lists more files than the cap allows:

1. Read only files that directly contain the function/class being changed
2. Skip `*.md` docs unless the spec explicitly requires them
3. Skip test files unless the task is specifically about tests
4. Note in RESULT: `"Context budget applied — skipped: [list of skipped files]"`

## Rule Loading — Load Only What Applies

Always load these regardless of task type:

- `core-context`
- `builder-role`
- `comms-protocol`
- `output-sanitization`
- `cursor-execution-fence`
- `auto-chain`
- `context-budget`
- `result-compression`

Load these ONLY when the task touches matching file types:

| Rule group | Load when task touches |
|-----------|----------------------|
| `codeguard-0-api-web-services` | `.ts`, `.py`, `.go`, `.java` with HTTP/REST |
| `codeguard-0-authentication-mfa` | Auth flows, login, tokens, session |
| `codeguard-0-data-storage` | DB queries, ORM, migrations |
| `codeguard-1-crypto-algorithms` | Any cryptographic operation |
| `codeguard-0-safe-c-functions` | `.c`, `.h` files only |
| `codeguard-0-mobile-apps` | `.swift`, `.kt`, `.dart` only |
| `codeguard-0-xml-and-serialization` | XML, YAML, JSON schema parsing |
| `test-first` | Tasks with `type: "test"` or spec mentions "write tests" |
| `dependency-audit` | Tasks that add/change packages |
| `claude-reasoning` | Tasks with `complexity: "HIGH"` |

Skip all others by default.

## Deduplication Rule

Never repeat in response text what is already defined in a loaded rule. Reference by name only:

- Wrong: "Following conventional commit format: type(scope): description..."
- Right: "Following `core-context` commit format"

## Spec Content — Trim Before Processing

If a task spec re-states a rule that is already loaded, ignore the re-stated version and apply the canonical rule. This prevents context bloat from duplicated instructions.
