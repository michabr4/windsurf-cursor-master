# CLAUDE.md

This repository is designed for less technical users working with coding agents.

## Working Rules

- Read the onboarding docs before changing code.
- Prefer plain language when explaining stack choices.
- If the user is unsure about stack choice, setup, or beginner concepts, suggest `web/index.html` as the guided wizard and offer to keep helping in chat if they prefer conversation.
- If the user asks for concrete development work, assume the stack choice is already made unless they explicitly ask for comparison or direction.
- Keep secrets in `.env`.
- Do not place PATs, API keys, or OAuth secrets in browser code.
- Prefer extending the starter clients over building parallel one-off code.
- Treat missing Webex recordings or transcripts as a possible permissions issue.

## Important Docs

- `README.md`
- `GETTING_STARTED.md`
- `docs/STACK_CHOOSER.md`
- `docs/ENV_VARS.md`
- `SECURITY.md`
- `docs/TOOL_GUIDE.md`
- `docs/CIRCUIT_API.md`
- `docs/WEBEX_SETUP.md`

If stack or setup questions come up later, use these docs to answer in plain language before inventing new guidance.

## Stack Guidance

- Python is the default backend for readable automation.
- Node is the JavaScript server option.
- `web/` is for browser UI only and should not contain secrets.