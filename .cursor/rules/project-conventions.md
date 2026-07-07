---
description: Project Conventions — full file structure, Python and TypeScript style guide, git branch naming, security non-negotiables
alwaysApply: false
---

# Project Conventions

## File Organization
- Python projects: src/ for source, tests/ for tests, docs/ for documentation
- Node/TS projects: src/ for source, __tests__/ or tests/, docs/
- Always include: README.md, .env.example, .gitignore, requirements.txt or package.json

## Python Standards
- Use type hints on all function signatures
- Use Pydantic for data models where applicable
- Use virtual environments (venv or .venv) — never install globally
- Format with black, lint with ruff
- Minimum Python 3.11

## TypeScript/Node Standards
- Strict TypeScript — no `any` types without justification
- Use ESM imports
- Format with prettier, lint with eslint
- Minimum Node 22 (avoid deprecated Node 20)

## Git Conventions
- Branch naming: feature/short-description, fix/short-description, chore/short-description
- Commit format: type(scope): description
- Types: feat, fix, docs, chore, refactor, test, style, ci
- Never commit .env, node_modules, venv, __pycache__, .DS_Store

## Security (Non-Negotiable)
- All secrets in .env files only
- .env must be in .gitignore
- No API keys, tokens, or passwords in source code
- Use HTTPS for all external API calls
- Validate all user input
- Use parameterized queries for database access
