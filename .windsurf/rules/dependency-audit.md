---
description: Dependency Audit — Windsurf must include audit step in specs whenever dependencies change
alwaysApply: false
---

# Dependency Audit (Windsurf Reference)

## When Writing Task Specs That Change Dependencies

If a task adds, removes, or upgrades any pip or npm package, the spec MUST include an explicit audit step.

### Add to the spec text:
```
After installing dependencies, run pip-audit (Python) or npm audit --audit-level=high (Node).
Block and report if any HIGH or CRITICAL CVEs are found. Document MEDIUM/LOW in issues but continue.
```

### Set in the task JSON:
```json
"complexity": "MEDIUM"
```
(Never LOW — dependency changes always warrant audit overhead.)

## Forbidden: Skip Audit Without Explicit Flag

Do not write a dependency-changing task without either:
1. Including the audit step in `spec`, OR
2. Explicitly setting `"skip_audit": true` with a written justification in `spec`

## Fast-Path Restriction

Tasks that add new production dependencies must be `requires_review: true`.
Tasks that only update to patch versions of existing deps may be `requires_review: false` if pip-audit passes.
