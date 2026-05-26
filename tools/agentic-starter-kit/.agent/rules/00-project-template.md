# Project Template Rule

- Read `README.md`, `GETTING_STARTED.md`, `docs/STACK_CHOOSER.md`, `docs/ENV_VARS.md`, and `SECURITY.md` before broad changes.
- Prefer simple explanations because this template is for less technical users.
- If the user is unsure about stack choice, setup, or beginner concepts, suggest `web/index.html` for the guided wizard and offer to keep helping in chat.
- If the user asks for concrete development work, assume the stack choice is already made unless they explicitly ask for comparison or direction.
- Keep secrets in `.env` and out of browser code.
- Use `python/` or `node/` for private API integrations.
- Use `web/` for UI only.
- Reuse the CIRCUIT and Webex starter clients when possible.
- Treat missing Webex recordings or transcripts as a likely permissions issue, not automatically a coding bug.
- If stack or setup questions come up later, use the onboarding docs to explain the tradeoffs before inventing new guidance.