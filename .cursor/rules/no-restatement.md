---
description: No Restatement — never repeat the task spec, user message, or prior output in a response
alwaysApply: true
---

# No Restatement Protocol

## What NOT to Include in Any Response

**Never restate:**

- The task spec or any field from the task JSON (you've already read it)
- The user's request back to them before answering
- A summary of what was done when the file diff already shows it
- Rules that were followed (assume compliance is implicit)
- Prior turn output that is still visible in the conversation

**Never open a response with:**

- "You asked me to..." / "The task requires..." / "As you can see..."
- "I will now..." / "I am going to..." / "I'll start by..."
- "Per the [rule name] rule..." (just comply with the rule silently)
- Restating any bullet points from the task spec as "requirements"

## What to Do Instead

Jump directly to the result, change, or finding. If context is needed, cite a file
path and line number — do not quote the content.

**Bad:**
> You asked me to add frontmatter to the rule files. I will now do this by modifying the alwaysApply flag as specified in the task...

**Good:**
> Added frontmatter to 3 rule files — `ai-factory-standards.md`, `claude-reasoning.md`, `test-first.md`.

## Token Impact

A typical restatement preamble is 80–200 tokens.
At 8 responses/session × 140 avg = **1,120 tokens/session** eliminated.
Over 20 sessions/month = **22,400 tokens/month** saved.
