---
description: Spec Length Cap — hard limits on task spec and files_to_read to prevent context bloat at task creation time
applyTo: "**"
---
# Spec Length Cap

## Hard Limits

| Field           | Maximum                        |
|-----------------|-------------------------------|
| `spec`          | 300 tokens (~1,800 characters) |
| `files_to_read` | 5 items                        |
| `title`         | 80 characters                  |
| inline examples | 0 — cite rule name instead     |

## Enforcement When Receiving a Task

If a task spec exceeds 300 tokens, trim it by applying these cuts in order:

1. Remove examples that duplicate a loaded rule — write `per rule-name.md` instead
2. Remove filler language ("please", "make sure to", "you should")
3. Convert prose paragraphs to bullet points
4. Remove context inferable from the file paths listed in `files_to_read`
5. If still over 300 tokens, summarize in one sentence: what to do, in which file, expected outcome

## Enforcement When Writing a Task (Windsurf → Cursor)

- Never paste file contents into `spec` — use `files_to_read` with path only
- Never re-state a rule's text — reference by filename
- Split tasks over 300 tokens into two separate tasks rather than one verbose spec

## Token Impact

A 500-token spec trimmed to 300 = 200 tokens saved.
At 100 tasks/month × 200 tokens = **20,000 tokens/month** = ~$0.24/month saved.
Each file_to_read that avoids inline pasting saves 100–2,000 tokens per task.
