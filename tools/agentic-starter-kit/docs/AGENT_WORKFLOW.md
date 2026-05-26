# Agent Workflow

This page explains how to work with AI coding assistants in this template.

## Safe Default Workflow

1. Ask the assistant to read the docs first.
2. Ask it to explain the current structure.
3. Ask for a small plan.
4. Make one limited change.
5. Review the result before expanding scope.

## Good Prompt Pattern

Use prompts like this:

"Read the README, stack chooser, environment variable guide, and security notes. Then explain the safest way to add a small feature to this repo."

## When To Use Which Folder

- `python/`: private API calls, scripts, automation, backend logic
- `node/`: JavaScript backend logic and server integrations
- `web/`: browser UI, mock data, and frontend experiments

## Questions To Ask Your Assistant

- Which stack fits my goal best?
- Does this feature require secrets?
- Should this run in the browser or on the server?
- Which existing example is closest to what I want?
- What could go wrong with permissions or API access?