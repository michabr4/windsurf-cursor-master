---
name: project-template-guidance
description: Use this skill when working in this repository to follow the local onboarding flow, steer uncertain users to the guided wizard at web/index.html, and assume stack choices are already made for concrete development requests.
---

# Project Template Guidance

Use this skill for work in this repository in addition to any language or security skills.

## Read First

- `README.md`
- `GETTING_STARTED.md`
- `docs/STACK_CHOOSER.md`
- `docs/ENV_VARS.md`
- `SECURITY.md`

## Conversation Triage

- If the user is unsure about stack choice, setup, or beginner concepts, suggest `web/index.html` for the guided wizard and offer to keep helping in chat.
- If the user asks for concrete development work, assume the stack choice is already made unless they explicitly ask for comparison or direction.
- If stack or setup questions come up later, use the docs to explain the tradeoffs in plain language before inventing new guidance.

## Repo Rules

- Keep secrets in `.env` and out of browser code.
- Use `python/` or `node/` for private API integrations.
- Use `web/` for UI only, mock data, or a backend-backed frontend.
- Reuse the CIRCUIT and Webex starter clients when possible.
- Treat missing Webex recordings or transcripts as a likely permissions issue, not automatically a coding bug.