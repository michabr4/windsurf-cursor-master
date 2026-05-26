# Project CodeGuard

This template includes Project CodeGuard rule files from `cosai-oasis/project-codeguard`.

## What It Does

Project CodeGuard adds security guidance to AI coding tools so they are more likely to produce safer code.

Examples of what it helps with:

- avoiding hardcoded secrets
- improving input validation
- encouraging safer authentication and authorization patterns
- reducing risky default code patterns

## Included Tool Folders

- `.github/instructions/` for GitHub Copilot-style instructions
- `.cursor/rules/` for Cursor rules
- `.windsurf/rules/` for Windsurf rules
- `.agent/rules/` for agent-compatible rule formats
- `.opencode/skills/software-security/` for OpenCode
- `.codex/skills/software-security/` for Codex-compatible skills

## What Users Need To Do

In most cases, just open the repo in your tool and let the tool load its repo-level instructions and rules.

## What Maintainers Need To Do

- update the vendored bundle occasionally from the Project CodeGuard releases page
- keep the local beginner instructions separate from upstream security rules
- mention CodeGuard in onboarding docs so users know the template is security-aware by default

## Official Project Links

- GitHub repository: https://github.com/cosai-oasis/project-codeguard
- Releases: https://github.com/cosai-oasis/project-codeguard/releases
- Project site: https://project-codeguard.org/