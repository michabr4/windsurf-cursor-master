# AGENTS.md

This repository is a beginner-safe template for agentic coding.

## Repository Priorities

1. Keep secrets in `.env` and out of browser code.
2. Prefer small, reviewable changes.
3. Explain tradeoffs in plain language.
4. Use existing starter files before inventing new structure.
5. Read the docs before changing stack-specific code.

## Read These First

- `README.md`
- `GETTING_STARTED.md`
- `docs/STACK_CHOOSER.md`
- `docs/ENV_VARS.md`
- `SECURITY.md`

## How To Work In This Repo

- If the user is unsure about technology choices, setup, or core concepts, suggest opening `web/index.html` for the guided wizard and offer to keep helping in chat if they prefer conversation.
- If the user asks for concrete development work, assume they have already chosen a stack unless they explicitly ask for comparison or direction.
- If the user is unsure about technology choices, compare Python, Node, and static web options in simple terms and use the docs to explain the tradeoffs.
- Keep browser code free of secrets.
- Put private API calls in Python or Node.
- Reuse the CIRCUIT and Webex starter clients for new integrations where possible.
- Tell the user when an API may return empty results because of permissions rather than code failure.
- If stack or setup questions come up later, refer to `README.md`, `GETTING_STARTED.md`, `docs/STACK_CHOOSER.md`, `docs/ENV_VARS.md`, `SECURITY.md`, and other relevant docs before answering.

## Tool Neutrality

This repo supports GitHub Copilot, Cursor, Windsurf, Claude Code, and OpenCode. Do not assume the user is using only one of them.