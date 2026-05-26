# Security Notes

This template is built for less technical users, so the safest path needs to be obvious.

## Core Rules

- Keep secrets in `.env`, not in source files.
- Do not put tokens in browser-delivered JavaScript.
- Use backend code for private API calls.
- Commit `.env.example`, not `.env`.
- Review AI-generated code before using it with real systems.

## What Should Stay On The Server Side

These belong in Python or Node code, not in static web files:

- API keys
- OAuth client secrets
- private access tokens
- recording or transcript downloads that require auth
- any request that should not be visible to end users

## Webex PAT Reminder

A Webex Personal Access Token acts like your user account for API calls. Treat it like a password.

## CIRCUIT/Cisco Reminder

The Bridge client secret, app key, and related values should stay in `.env` and be used only from backend code.

## AI Assistant Guardrails

Ask your coding assistant to:

- explain planned changes before editing many files
- avoid destructive git commands
- avoid logging secrets
- prefer small, reviewable changes
- keep browser code free of secrets

## CodeGuard

This template is intended to include Project CodeGuard rule files for supported editors and coding agents. Those rules add secure-by-default guidance during code generation and review.