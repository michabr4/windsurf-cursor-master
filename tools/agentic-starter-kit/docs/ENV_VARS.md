# Environment Variables

This template uses one shared `.env.example` at the root.

## What An Environment Variable Is

An environment variable is a named setting. In beginner terms, it is a labeled box for a secret or configuration value.

Example:

- `WEBEX_ACCESS_TOKEN` stores your Webex Personal Access Token.

## Webex Variables

- `WEBEX_ACCESS_TOKEN`: your Personal Access Token from `developer.webex.com`
- `WEBEX_API_BASE_URL`: the Webex API base URL
- `WEBEX_DEMO_ROOM_ID`: optional room id for a saved demo
- `WEBEX_MAX_PAGE_SIZE`: optional page size for list calls

## CIRCUIT / Cisco Variables

- `BRIDGE_API_CLIENT_ID`: OAuth client id for Bridge token requests
- `BRIDGE_API_CLIENT_SECRET`: OAuth client secret for Bridge token requests
- `BRIDGE_API_TOKEN_URL`: token endpoint
- `BRIDGE_API_APP_KEY`: app identifier used by the Cisco chat example
- `CISCO_BRAIN_USER_ID`: your Cisco user identifier used in the sample metadata
- `CISCO_CHAT_API_BASE_URL`: Cisco chat endpoint base URL
- `AZURE_OPENAI_API_KEY`: key used by the original sample flow
- `CISCO_CHAT_MODEL`: chat model name
- `CISCO_CHAT_API_VERSION`: API version for the chat call

## Ollama (local chat, optional)

Use these when you want the Circuit chat demo to call a local Ollama server instead of Cisco chat.

- `USE_OLLAMA`: set to `1` or `true` to send chat to Ollama
- `OLLAMA_BASE_URL`: Ollama host (default `http://localhost:11434`; `/v1` is added automatically)
- `OLLAMA_MODEL`: model tag sent to Ollama (default `qwen2.5-coder:7b`; run `ollama pull qwen2.5-coder:7b` first)
- `OLLAMA_API_KEY`: optional bearer token if your Ollama install requires one

## Asana (task review sample)

**OAuth (recommended when your company blocks personal access tokens)**

- `ASANA_CLIENT_ID` and `ASANA_CLIENT_SECRET`: from your org’s Asana OAuth app in the [Developer Console](https://app.asana.com/0/developer-console).
- `ASANA_OAUTH_REDIRECT_URI`: must match exactly what is registered on the app (default `http://127.0.0.1:8845/oauth/callback`).
- `ASANA_ACCESS_TOKEN`, `ASANA_REFRESH_TOKEN`, `ASANA_TOKEN_EXPIRES_AT`: filled automatically after you sign in at `http://127.0.0.1:8845/oauth/start`. Do not paste these in chat.

**Optional legacy mode**

- `ASANA_ACCESS_TOKEN` alone: only if your org still allows a Personal Access Token (not client id/secret).

- `ASANA_REVIEW_PORT`: port for the local review UI server (default `8845`).
- `ASANA_REVIEW_USE_LLM`: set to `1` or `true` to polish review comments with local Ollama (`OLLAMA_BASE_URL`, `OLLAMA_MODEL`). You can also pass `--llm` on the CLI or check the box in the web UI.
- `ASANA_REVIEW_WEBHOOK_SECRET`: if set, enables `POST /api/asana/webhook` on the local server. Send the same value in header `X-Asana-Review-Secret`. Body: `{"task":"GID or URL"}` or an Asana `events` payload. Optional `"post": true` to comment immediately (use with care).

## Outlook / Microsoft Graph Variables

- `MS_TENANT_ID`: tenant for login authority. Use `organizations` by default.
- `MS_CLIENT_ID`: application (client) id for your Graph app registration
- `MS_MAILBOX_USER`: optional mailbox user principal name or user id to read (example: `you@company.com`). Leave blank to read your own mailbox with delegated login.
- `MS_OUTLOOK_MAX_MESSAGES`: how many recent inbox messages to scan for action items

## Public Vs Private Values

Private values should stay in backend code only:

- tokens
- secrets
- API keys

Public values may be safe in the browser if they are not sensitive:

- app title
- public backend URL
- feature flags with no security impact