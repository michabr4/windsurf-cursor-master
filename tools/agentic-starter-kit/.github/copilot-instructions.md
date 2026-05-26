# Copilot Instructions

This repository is a safe starter template for non-developers using AI coding tools.

## Always Do This

- Read `README.md`, `GETTING_STARTED.md`, `docs/STACK_CHOOSER.md`, `docs/ENV_VARS.md`, and `SECURITY.md` before making broad changes.
- Explain Python, JavaScript, Node, HTML, CSS, frontend, and backend concepts in plain language when the user seems unsure.
- If the user is unsure about stack choice, setup, or beginner concepts, suggest `web/index.html` for the guided wizard and offer to continue in chat if they prefer conversation.
- If the user asks for concrete development work, assume they have already chosen a stack unless they explicitly ask for comparison or direction.
- Prefer small, auditable edits.
- Keep `.env` secrets out of source files and browser-delivered code.
- Reuse the starter CIRCUIT and Webex clients when building similar features.
- If stack or setup questions come up later, refer back to the onboarding docs and explain the tradeoffs in plain language.

## Repo Expectations

- Python and Node are the private API paths.
- `web/` is the safe static UI path and should use mock data or a backend API.
- Webex recordings and transcripts may be unavailable because of account permissions.
- The original reference note is in `CIRCUIT_API.txt`, but final starter code lives in the language folders.