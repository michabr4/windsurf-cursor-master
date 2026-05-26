# Commenting Guide

Good comments explain the "why" behind code decisions, highlight safety considerations, and clarify unexpected behavior, but they should not restate what the code obviously does line by line. When you comment code in this repo, focus on decisions that might not be obvious to someone reading it later, especially around security choices, API behavior, and beginner-friendly patterns. The best comments prevent confusion; low-value comments just add noise.

## Recommended Amount

Use a light-to-moderate amount of comments.

- Explain intent, not mechanics.
- Keep comments light and local to non-obvious code.
- Document safety boundaries and secret-handling rules.
- Clarify surprising API behavior, pagination, or permission caveats.
- Skip obvious inline comments when names already tell the story.

## Practical Rule For This Repo

If you would have to explain a line or block during review, add a short comment now. If the code is already obvious from names and structure, leave it uncommented.
