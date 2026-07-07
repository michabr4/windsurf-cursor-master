# Getting Started

This guide is written for people who may be new to coding tools.

## What This Repo Is For

Use this template when you want an AI coding assistant to help you build something without starting from a blank folder.

Good fit:

- internal tools
- API experiments
- small automation scripts
- dashboards and simple browser tools
- early prototypes

## Guided Browser Tutorial

If you prefer a click-through experience, open `web/index.html` in a browser. The wizard asks a few questions and takes you to exactly the right setup path — covering concepts, stack choice, environment variables, and running your first sample. No install required.

To open it in VS Code: install the **Live Preview** extension, right-click `web/index.html`, and choose **Show Preview**.

## Download And Open The Project Folder

1. Download this repository as a `.zip` file.
2. Extract the `.zip` file to a folder on your computer.
3. Open your agentic development tool of choice, such as VS Code, Cursor, Windsurf, Claude Code, or OpenCode.
4. Choose **Open Folder** and select the extracted project folder.
5. Keep that folder open while you follow the steps in this guide.

## Basic Setup

1. Download the repo `.zip`, extract it to a folder on your computer, and open that folder in your preferred agentic development tool.
2. Copy `.env.example` to `.env`.
3. Fill in only the API values you need for your project.
4. If you are using Python, follow [docs/PYTHON_SETUP.md](docs/PYTHON_SETUP.md).
5. If you are using Node, follow [docs/NODE_SETUP.md](docs/NODE_SETUP.md).
6. Choose a starter path:
   - Python if you want readable scripts and backend automation.
   - Node if you want JavaScript on the server.
   - Web if you want a simple browser interface.
7. Ask the assistant to explain the starter files before making changes.

## If You Are Not Sure Which Path To Choose

Read [docs/STACK_CHOOSER.md](docs/STACK_CHOOSER.md).

## If APIs Are New To You

Read [docs/API_BASICS.md](docs/API_BASICS.md) before jumping into the Webex or CIRCUIT examples.

## If CLIs Are New To You

Read [docs/CLI_BASICS.md](docs/CLI_BASICS.md) before worrying about terminal commands or agent-run commands.

## Safe Beginner Rules

- Never paste secrets into chat screenshots or public issues.
- Never place API tokens directly in browser JavaScript.
- Keep `.env` local.
- Ask your assistant to explain what it will change before it changes many files.
- Start with one small feature, not a full product rewrite.

## Suggested Learning Order

1. Read [docs/API_BASICS.md](docs/API_BASICS.md) if APIs are new to you.
2. Read [docs/CLI_BASICS.md](docs/CLI_BASICS.md) if terminals are new to you.
3. Read [docs/STACK_CHOOSER.md](docs/STACK_CHOOSER.md).
4. Read [docs/TOOL_GUIDE.md](docs/TOOL_GUIDE.md).
5. Read [docs/ENV_VARS.md](docs/ENV_VARS.md).
6. If using Cisco or Webex APIs, read the matching docs in [docs](docs).
7. Run one sample before asking the assistant to build something new.

## Quick Commands

### Python

- Create a local virtual environment and install dependencies: see [docs/PYTHON_SETUP.md](docs/PYTHON_SETUP.md)
- Run Webex sample: `python python/examples/webex_demo.py`
- Run CIRCUIT sample: `python python/examples/circuit_demo.py`
- Run Outlook action-item sample: `python python/examples/outlook_action_items_demo.py`

### Node

- Install Node dependencies: see [docs/NODE_SETUP.md](docs/NODE_SETUP.md)
- Run Webex sample: `npm run webex`
- Run CIRCUIT sample: `npm run circuit`

### Web

- Open `web/index.html` in a browser for the safe mock-data UI starter.

## Good First Prompts

- "Explain this repo to me like I am a beginner and tell me which folder I should start in."
- "Read the env docs and tell me which values I need for the Webex example."
- "Show me the difference between the Python and Node CIRCUIT client files."
- "Help me build a simple dashboard using the existing starter files without exposing secrets in the browser."