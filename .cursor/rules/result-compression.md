---
description: Result Compression — minimal RESULT format for LOW/MEDIUM tasks to reduce output token usage
alwaysApply: true
---

# Result Compression Protocol

## LOW Complexity (haiku model)

Three fields only. Omit `details`, `issues` (unless there is one), `next_recommended`:

```json
{
  "id": "TASK-2026-MMDD-NNN",
  "status": "success",
  "summary": "One sentence describing exactly what was done.",
  "files_changed": ["path/to/file.ext"],
  "completed_at": "2026-MM-DDTHH:MM:SS-04:00"
}
```

## MEDIUM Complexity (sonnet model)

Add `details` as a bullet list — max 5 items, no prose paragraphs:

```json
{
  "id": "TASK-2026-MMDD-NNN",
  "status": "success",
  "summary": "One sentence.",
  "details": "• Changed X in file Y\n• Added test for edge case Z\n• Fixed null guard in W",
  "files_changed": ["path/a.ts", "path/b.ts"],
  "issues": [],
  "completed_at": "2026-MM-DDTHH:MM:SS-04:00"
}
```

## HIGH Complexity (opus model)

Use full schema from `schema.md`. No compression — verbose output is warranted.

## Blocked or Failed (any complexity)

Always use full format regardless of model — error detail matters:

```json
{
  "id": "TASK-2026-MMDD-NNN",
  "status": "blocked",
  "summary": "One sentence on what blocked execution.",
  "details": "Full explanation: what was attempted, what failed, what is needed to unblock.",
  "files_changed": [],
  "issues": [{ "issue": "Description", "fix": "What is needed" }],
  "completed_at": "2026-MM-DDTHH:MM:SS-04:00"
}
```

## Issues Array Format

Per finding, two fields only:

```json
{ "issue": "What went wrong", "fix": "What was or should be done" }
```

No `severity` field for issues in MEDIUM tasks — reserve for dependency-audit findings only.

## Never Include in Compressed Results

- Full file contents
- Stack traces longer than 5 lines (truncate with `...`)
- Restatements of the task spec
- Explanations of rules followed (assumed implicit)
