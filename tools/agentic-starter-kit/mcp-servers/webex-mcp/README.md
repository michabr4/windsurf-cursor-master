# Webex MCP Server (Phase 3)

**Status:** Planned — disabled in `~/.cursor/mcp.json` until implemented.

## Purpose

Allow Cursor to interact with Webex directly: send messages, read spaces, manage bot subscriptions, and test status report delivery.

## Capabilities (planned)

- `list_spaces` — List Webex spaces the bot is in
- `send_message` — Send a message to a space (text or adaptive card)
- `read_messages` — Read recent messages from a space
- `list_members` — List members of a space
- `create_space` — Create a new Webex space
- `add_member` — Add a person to a space

## Auth

`WEBEX_BOT_TOKEN` from `~/.env.cursor`

## Stack

- Protocol: MCP stdio (Python)
- Dependencies: `webexteamssdk`, `mcp`

Built when ROADMAP Phase 3 begins per `CURSOR_SETUP_PLAN.md`.
