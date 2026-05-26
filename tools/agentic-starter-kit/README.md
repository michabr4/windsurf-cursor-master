# Safe Agentic Coding Template

This repository is a beginner-friendly starter for people using AI coding tools to build small apps, automations, and integrations.

It is designed to work across multiple assistants and editors:

- GitHub Copilot in VS Code
- Cursor
- Windsurf
- Claude Code
- OpenCode

It includes:

- plain-language docs for non-developers
- a shared `.env.example` for common API settings
- Python and Node starter code
- a simple static web UI starter
- CIRCUIT/Cisco client templates in Python and Node
- Webex Personal Access Token examples for spaces, messages, recordings, and transcripts
- Project CodeGuard security rules for supported agent tools

## Guided Browser Tutorial

Open `web/index.html` in a browser (or use the VS Code Live Preview extension) to launch an interactive step-by-step wizard that walks you through concepts, stack selection, environment setup, and running a sample — no install required.

## Download And Open The Folder

1. Download this repository as a `.zip` file from GitHub.
2. Extract the `.zip` file to a normal folder on your computer, such as `Documents` or `Desktop`.
3. Open your agentic development tool of choice.
4. Use that tool's **Open Folder** option and select the extracted project folder.
5. Then continue with the setup steps below.

## Start Here

1. Download the repo `.zip`, extract it to a folder on your computer, and open that folder in your preferred agentic development tool.
2. Open [web/index.html](web/index.html) in a browser for the guided setup wizard, **or** read [GETTING_STARTED.md](GETTING_STARTED.md) for the written version.
3. If you are new to the runtime setup, read [docs/PYTHON_SETUP.md](docs/PYTHON_SETUP.md) or [docs/NODE_SETUP.md](docs/NODE_SETUP.md).
4. If APIs are new to you, read [docs/API_BASICS.md](docs/API_BASICS.md).
5. If CLIs or terminals are new to you, read [docs/CLI_BASICS.md](docs/CLI_BASICS.md).
6. Choose your tech stack: [docs/STACK_CHOOSER.md](docs/STACK_CHOOSER.md) (Python, Node, or static web).
7. Choose your coding model: [docs/MODEL_ADVISOR.md](docs/MODEL_ADVISOR.md) (Claude, GPT, or Gemini).
8. Copy `.env.example` to `.env` and fill in only the values you need.
9. Pick one starter path:
   - [python](python) for scripts, data work, or backend automation
   - [node](node) for JavaScript servers and integrations
   - [web](web) for a simple browser-based UI
10. Use your preferred coding assistant with the repo instructions included here.

## Run A Sample

### Python sample

1. Create and activate a local virtual environment by following [docs/PYTHON_SETUP.md](docs/PYTHON_SETUP.md).
2. Run the Webex sample: `python python/examples/webex_demo.py`
3. Run the CIRCUIT sample: `python python/examples/circuit_demo.py`
4. Run the Outlook action-item sample: `python python/examples/outlook_action_items_demo.py`
5. Run the Asana task review: set `ASANA_CLIENT_ID` and `ASANA_CLIENT_SECRET` in `.env`, start `python python/examples/asana_review_server.py`, then open `http://127.0.0.1:8845/oauth/start` to sign in. CLI: `python python/examples/asana_review_cli.py <task GID or URL>` (`--confirm` to post, `--llm` for Ollama). See [docs/ENV_VARS.md](docs/ENV_VARS.md).

### Node sample

1. Install Node and dependencies by following [docs/NODE_SETUP.md](docs/NODE_SETUP.md).
2. Run the Webex sample: `npm run webex`
3. Run the CIRCUIT sample: `npm run circuit`

### Static web sample

Open `web/index.html` in a browser. It uses mock data and does not require secrets.

## What The Main Options Mean

- Python: a readable programming language often used for automation, APIs, AI workflows, and data tasks.
- JavaScript: the language most often used in the browser and also commonly used on servers with Node.js.
- Node.js: the runtime that lets JavaScript run outside the browser, usually for servers, scripts, and backend jobs.
- HTML: the structure of a web page.
- CSS: the visual styling of a web page.
- UI or frontend: what a person sees and clicks.
- Server or backend: the part that talks to databases, APIs, files, and private secrets.
- API: a way for one system to talk to another system using defined requests and responses.
- CLI or terminal: a text-based way to run commands and tools.
- `.env` file: a local file for secrets and settings like API keys. It should not be committed to source control.

## Repository Layout

- [docs](docs) explains the template, stacks, tools, environment variables, and API examples.
- [python](python) contains Python starter clients and demos.
- [node](node) contains JavaScript and Node starter clients and demos.
- [web](web) contains a static UI starter that avoids exposing secrets in the browser.
- [CIRCUIT_API.txt](CIRCUIT_API.txt) is the original source note that informed the CIRCUIT starter clients.

## Included API Samples

- CIRCUIT/Cisco example:
  - Bridge OAuth client credential token flow
  - Cisco-hosted chat request pattern based on the original note
- Webex example using a Personal Access Token from `developer.webex.com`:
  - list spaces
  - list messages in a space
  - list recordings
  - list transcripts and fetch transcript details

## Tool References

Official documentation links are collected in [docs/TOOL_GUIDE.md](docs/TOOL_GUIDE.md).

## Commenting Style

The repo's comment approach is documented in [docs/COMMENTING_GUIDE.md](docs/COMMENTING_GUIDE.md).

## Security Defaults

This template is meant to be safe by default:

- `.env` is ignored by git
- browser code does not contain private API tokens
- Project CodeGuard rules are included for supported tools
- docs explain what should stay on the server side

See [SECURITY.md](SECURITY.md) for practical safety rules.

Project CodeGuard details are in [docs/CODEGUARD.md](docs/CODEGUARD.md).

## Relationship to delivery-workbench

This repository is a **shareable template**: starter code, CodeGuard rules, docs, and sample MCP servers for new agentic projects.

For a **personal SDM operational workspace** (playbooks, email orchestration, project outputs, AGT-001 integrations), use [../delivery-workbench](../delivery-workbench) in this monorepo—or your own fork of that workbench. CodeGuard rules in this kit are the canonical source; copy or symlink them into other repos as needed.

## Recommended First Prompt

Try this with your coding assistant after reading the docs:

"Read the README, stack chooser, and env docs. Then tell me which starter path fits a small internal tool that reads API data and shows it in a simple web page."
