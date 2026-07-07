// ── Safe Agentic Template — Guided Wizard ──────────────────────
// No type="module" so this works in Edge from file:// URLs.
// All doc content is inlined — no fetch() calls needed.
// marked.js (loaded from CDN) renders Markdown to HTML.

var DOCS = {
  "GETTING_STARTED.md": "# Getting Started\n\nThis guide is for people who may be new to coding tools.\n\n## What This Repo Is For\n\nUse this template when you want an AI coding assistant to help you build something without starting from a blank folder.\n\n**Good fit for:**\n- Internal tools\n- API experiments\n- Small automation scripts\n- Dashboards and simple browser tools\n- Early prototypes\n\n## Basic Setup\n\n1. Copy `.env.example` to `.env`.\n2. Fill in only the API values you need.\n3. If you are using Python, follow `docs/PYTHON_SETUP.md`.\n4. If you are using Node, follow `docs/NODE_SETUP.md`.\n5. Choose a starter path: **Python**, **Node**, or **Web**.\n6. Open the repo in your coding tool.\n7. Ask the assistant to explain the starter files before making changes.\n\n## If APIs Are New To You\n\nRead `docs/API_BASICS.md` before jumping into the Webex or CIRCUIT examples.\n\n## Safe Rules\n\n- Never paste secrets into chat screenshots.\n- Never place API tokens directly in browser JavaScript.\n- Keep `.env` local — never commit it.\n- Start with one small feature, not a full rewrite.\n",

  "docs/API_BASICS.md": "# API Basics\n\nUse this page if words like API, request, response, or endpoint still feel abstract.\n\n## What An API Is\n\nAn API is a defined way for one piece of software to ask another piece of software for data or actions.\n\n> **Plain language:** an API is like a service counter with a menu.\n\n- Your app asks for something in a known format.\n- The other system replies in a known format.\n- Both sides follow the same rules.\n\n## Common API Terms\n\n- **Request**: the question your app sends\n- **Response**: the answer the API sends back\n- **Endpoint**: a specific API URL for one kind of action or data\n- **Token**: a secret string that proves who you are\n- **JSON**: a common text format APIs use for data\n\n## Safe Pattern For This Repo\n\n```\nBrowser UI -> Python or Node backend -> External API\n```\n\nWhy this matters:\n- the browser should not hold private tokens\n- backend code can read `.env` safely\n- backend code can simplify API data before sending it to the UI\n",

  "docs/CLI_BASICS.md": "# CLI Basics\n\nUse this page if words like CLI, terminal, command, or shell still feel unfamiliar.\n\n## What A CLI Is\n\nA CLI is a Command Line Interface.\n\n> **Plain language:** it is a text-based way to tell a computer or tool what to do.\n\nInstead of clicking buttons, you type commands.\n\n## Common CLI Terms\n\n- **Terminal**: the window where you type commands\n- **Command**: the instruction you type\n- **Output**: the text the command prints back\n- **Folder** or **directory**: the place you are currently working in\n- **Script**: a saved command shortcut, often run by tools like `npm`\n\n## Why CLI Matters For Agents\n\nMany coding agents can use the CLI for you.\n\nThat means an agent can:\n- run a sample\n- inspect files\n- install dependencies when needed\n- show you the result of a command\n\nIn beginner terms: the agent can use the terminal as one of its tools, not just edit files.\n",

  "docs/STACK_CHOOSER.md": "# Stack Chooser\n\nUse this when you are not sure whether to start with Python, Node, or a static web UI.\n\n## Choose Python When\n- You want scripts or automation\n- You want a backend that is easy to read\n- You expect to work with APIs, AI libraries, or data processing\n\n> **Plain language:** Python is a \"do work for me\" language.\n\n## Choose Node When\n- You want JavaScript on the server\n- Your frontend and backend should share one language\n- You want API routes or a lightweight web server\n\n> **Plain language:** Node lets JavaScript run as a server, not just in the browser.\n\n## Choose Static Web When\n- You want a simple browser page\n- You want to prototype layout and UX quickly\n- Your data can come from mock data or a backend API\n\n## Quick Rule Of Thumb\n\n| Need | Use |\n|------|-----|\n| Secrets or private API calls | Python or Node |\n| Simple browser interface only | web/ |\n| UI + private API access | web/ + Python or Node |\n",

  "docs/ENV_VARS.md": "# Environment Variables\n\nThis template uses one shared `.env.example` at the root.\n\n## What An Environment Variable Is\n\nAn environment variable is a labeled box for a secret or configuration value.\n\n**Example:** `WEBEX_ACCESS_TOKEN` stores your Webex Personal Access Token.\n\n## Setup\n\n```\ncopy .env.example .env\n```\n\nThen open `.env` and fill in only the values you need.\n\n## Webex Variables\n\n| Variable | Purpose |\n|----------|---------|\n| `WEBEX_ACCESS_TOKEN` | Personal Access Token from developer.webex.com |\n| `WEBEX_API_BASE_URL` | Webex API base URL |\n| `WEBEX_DEMO_ROOM_ID` | Optional saved demo room |\n\n## CIRCUIT / Cisco Variables\n\n| Variable | Purpose |\n|----------|---------|\n| `BRIDGE_API_CLIENT_ID` | OAuth client id |\n| `BRIDGE_API_CLIENT_SECRET` | OAuth client secret |\n| `BRIDGE_API_TOKEN_URL` | Token endpoint |\n| `BRIDGE_API_APP_KEY` | App identifier |\n\n## Private vs Public\n\n**Private (backend only):** tokens, secrets, API keys.\n\n**Public (may be in browser):** app title, public backend URL, non-sensitive feature flags.\n",

  "SECURITY.md": "# Security Notes\n\n## Core Rules\n\n- Keep secrets in `.env`, not in source files.\n- Do not put tokens in browser-delivered JavaScript.\n- Use backend code for private API calls.\n- Commit `.env.example`, not `.env`.\n- Review AI-generated code before using it with real systems.\n\n## What Stays On The Server\n\nThese belong in Python or Node **only**:\n\n- API keys\n- OAuth client secrets\n- Private access tokens\n- Recording or transcript downloads that require auth\n\n## Webex PAT Reminder\n\nA Webex Personal Access Token acts like your user account. **Treat it like a password.**\n\n## AI Assistant Guardrails\n\nAsk your assistant to:\n- Explain planned changes before editing many files\n- Avoid logging secrets\n- Prefer small, reviewable changes\n- Keep browser code free of secrets\n",

  "docs/TOOL_GUIDE.md": "# Tool Guide\n\n## GitHub Copilot in VS Code\n\nBuilt into VS Code — chat, inline edits, code suggestions, agent mode.\n\n**Use if:** you want a familiar editor with strong built-in AI workflows.\n\nInstructions file: `.github/copilot-instructions.md`\n\n## Cursor\n\nAI-first code editor with agent workflows and repo-level rules.\n\n**Use if:** you want a dedicated AI editor with strong repo navigation.\n\nInstructions folder: `.cursor/rules/`\n\n## Windsurf\n\nAI editor designed for fast onboarding from VS Code or Cursor.\n\n**Use if:** you want fast AI-assisted flow and easy migration.\n\nInstructions folder: `.windsurf/rules/`\n\n## Claude Code\n\nAnthropic's coding agent — terminal, VS Code, desktop, web.\n\n**Use if:** you want strong agentic workflow via `CLAUDE.md`.\n\n## OpenCode\n\nOpen-source AI coding agent — terminal-first with IDE integration.\n\n**Use if:** you want an open tool via `AGENTS.md`.\n",

  "docs/WEBEX_SETUP.md": "# Webex Setup\n\n## What A Personal Access Token (PAT) Is\n\nA PAT is a token that lets the Webex API act as you. **Treat it like a password.**\n\n## How To Get It\n\n1. Open [developer.webex.com](https://developer.webex.com)\n2. Sign in\n3. Go to your personal token area\n4. Copy the token\n5. Put it in `.env` as `WEBEX_ACCESS_TOKEN`\n\n## What The Sample Can Do\n\n- List spaces you belong to\n- List messages in a space\n- List recordings visible to your account\n- List transcripts visible to your account\n\n## Safe Usage Pattern\n\n```\nBrowser  →  your backend (Python/Node)  →  Webex API\n```\n\n**Never** call Webex directly from browser JavaScript with your PAT.\n",

  "docs/PYTHON_SETUP.md": "# Python Setup\n\n## Requirements\n\n- Python 3.11 or newer\n\n## Step-by-Step\n\n```\n# 1. Create a local virtual environment\npython -m venv .venv\n\n# 2. Activate it (Windows PowerShell)\n.\\.venv\\Scripts\\Activate.ps1\n\n# 3. Activate it (macOS / Linux)\nsource .venv/bin/activate\n\n# 4. Upgrade pip\npython -m pip install --upgrade pip\n\n# 5. Install dependencies\npip install -r python/requirements.txt\n\n# 6. Run a sample\npython python/examples/circuit_demo.py\n```\n\n## Why A Local .venv?\n\n- Keeps this repo's packages separate from other projects.\n- The repo already ignores `.venv/` so you won't commit it.\n- Each user creates their own — nothing shared by accident.\n",

  "docs/NODE_SETUP.md": "# Node Setup\n\n## Requirements\n\n- Node.js LTS (18 or newer)\n\n## Step-by-Step\n\n```\n# 1. Install Node.js from nodejs.org\n\n# 2. Move into the node folder\ncd node\n\n# 3. Install dependencies (once)\nnpm install\n\n# 4. Run the CIRCUIT sample\nnpm run circuit\n\n# 5. Run the Webex sample\nnpm run webex\n```\n\n## Why The node/ Folder?\n\nThe `node/` folder is the safe place for JavaScript that needs secrets. The `node_modules/` folder it creates is local and already ignored by git.\n"
};

var NODES = {
  welcome: { id:"welcome", type:"hero", title:"Welcome to the Safe Agentic Template", body:"This walkthrough learns what you need and takes you to exactly the right setup path. Answer a few quick questions to get started.", choices:[{label:"I'm brand new \u2014 start from the beginning",next:"what-is-this"},{label:"Explain key concepts first (APIs, CLIs, tokens)",next:"what-is-an-api"},{label:"I need security guidance",next:"security"},{label:"I have a specific tool (Copilot, Cursor\u2026)",next:"pick-tool"}] },
  "what-is-this": { id:"what-is-this", type:"content", title:"What Is This Repo For?", md:"This template gives you a safe starting point for working with AI coding assistants.\n\n**It includes:**\n- Python and Node backend starters\n- A static browser UI starter\n- CIRCUIT / Cisco API client templates\n- Webex integration examples\n- Security rules for your coding tool\n\n**Good fit for:** internal tools, API experiments, automation scripts, dashboards, early prototypes.", next:"what-is-an-api", doc:"GETTING_STARTED.md" },
  "what-is-an-api": { id:"what-is-an-api", type:"content-choice", title:"What Is An API?", md:"## API basics\n\nAn **API** is a defined way for one piece of software to ask another piece of software for data or actions.\n\n### Plain-language example\nThink of an API like a service counter with a menu:\n- your app asks for something in a known format\n- the other system replies in a known format\n- both sides follow the same rules\n\n### In this repo\n- **Webex** is an API you can ask for spaces, messages, recordings, or transcripts\n- **CIRCUIT / Cisco** examples show how code talks to another external service\n\n### Safe pattern\n```\nBrowser UI -> Python or Node backend -> External API\n```\nKeep tokens and secrets in the backend, not in browser JavaScript.", choices:[{label:"Now explain what a CLI is",next:"what-is-a-cli"},{label:"That makes sense — continue",next:"what-are-you-building"},{label:"Show me the full API basics doc",next:"api-basics-detail"},{label:"Explain security before examples",next:"security"}], doc:"docs/API_BASICS.md" },
  "api-basics-detail": { id:"api-basics-detail", type:"doc", title:"API Basics \u2014 Full Guide", docKey:"docs/API_BASICS.md", next:"what-are-you-building", nextLabel:"Next: What are you trying to build? \u2192" },
  "what-is-a-cli": { id:"what-is-a-cli", type:"content-choice", title:"What Is A CLI?", md:"## CLI basics\n\nA **CLI** is a Command Line Interface.\n\n### Plain-language example\nA CLI is a text-based way to tell a computer or tool what to do. Instead of clicking buttons, you type commands into a terminal.\n\n### In this repo\nYou may see CLI commands for things like:\n- running a sample\n- moving into the `node/` folder\n- starting an agent tool\n\n### Why it matters for agents\nMany coding agents can use the CLI as a tool. That means the agent can run commands, inspect results, and help you without you needing to memorize everything first.", choices:[{label:"Show me the full CLI basics doc",next:"cli-basics-detail"},{label:"Continue to what I want to build",next:"what-are-you-building"},{label:"Also explain what an API is",next:"what-is-an-api"},{label:"Review the tool options",next:"pick-tool"}], doc:"docs/CLI_BASICS.md" },
  "cli-basics-detail": { id:"cli-basics-detail", type:"doc", title:"CLI Basics \u2014 Full Guide", docKey:"docs/CLI_BASICS.md", next:"what-are-you-building", nextLabel:"Next: What are you trying to build? \u2192" },
  "what-are-you-building": { id:"what-are-you-building", type:"choice", title:"What are you trying to build?", choices:[{label:"A script or automation that runs on my computer",next:"pick-python"},{label:"A web server or API backend",next:"pick-node"},{label:"A browser UI \u2014 something people see in a browser",next:"pick-web"},{label:"A full tool: browser UI + private backend calls",next:"pick-fullstack"},{label:"Integrate with Webex",next:"webex-path"},{label:"I\u2019m not sure yet",next:"stack-chooser"}] },
  "stack-chooser": { id:"stack-chooser", type:"content-choice", title:"Help Me Choose a Stack", md:"## Quick decision guide\n\n| I want to... | Use |\n|---|---|\n| Write scripts, automate tasks, call APIs | **Python** |\n| Build a server, handle routes, use npm | **Node** |\n| Build a browser page with mock data | **Web (static)** |\n| Build UI + private API calls | **Web + Python or Node** |", choices:[{label:"Python sounds right",next:"pick-python"},{label:"Node sounds right",next:"pick-node"},{label:"Static browser UI for now",next:"pick-web"},{label:"I need both UI and backend",next:"pick-fullstack"}], doc:"docs/STACK_CHOOSER.md" },
  "pick-stack": { id:"pick-stack", type:"choice", title:"Which stack are you using?", choices:[{label:"Python",next:"pick-python"},{label:"Node / JavaScript",next:"pick-node"},{label:"Static browser UI only",next:"pick-web"},{label:"Both a UI and a backend",next:"pick-fullstack"}] },
  "pick-python": { id:"pick-python", type:"content-choice", title:"Python Setup", md:"## You chose Python \u2713\n\nPython is the simplest backend default for most internal tools.\n\n### Quick setup\n\n```\npython -m venv .venv\n.\\.venv\\Scripts\\Activate.ps1\npip install -r python/requirements.txt\n```\n\n### Run a sample\n```\npython python/examples/circuit_demo.py\npython python/examples/webex_demo.py\n```", choices:[{label:"Full Python setup guide",next:"python-detail"},{label:"Set up environment variables",next:"env-vars"},{label:"I also want a browser UI",next:"pick-fullstack"},{label:"Integrate Webex",next:"webex-path"}], doc:"docs/PYTHON_SETUP.md" },
  "python-detail": { id:"python-detail", type:"doc", title:"Python Setup \u2014 Full Guide", docKey:"docs/PYTHON_SETUP.md", next:"env-vars", nextLabel:"Next: Environment Variables \u2192" },
  "pick-node": { id:"pick-node", type:"content-choice", title:"Node Setup", md:"## You chose Node \u2713\n\nNode lets JavaScript run as a server, not just in the browser.\n\n### Quick setup\n\n```\ncd node\nnpm install\nnpm run circuit\nnpm run webex\n```", choices:[{label:"Full Node setup guide",next:"node-detail"},{label:"Set up environment variables",next:"env-vars"},{label:"I also want a browser UI",next:"pick-fullstack"},{label:"Integrate Webex",next:"webex-path"}], doc:"docs/NODE_SETUP.md" },
  "node-detail": { id:"node-detail", type:"doc", title:"Node Setup \u2014 Full Guide", docKey:"docs/NODE_SETUP.md", next:"env-vars", nextLabel:"Next: Environment Variables \u2192" },
  "pick-web": { id:"pick-web", type:"content-choice", title:"Static Browser UI", md:"## You chose the Static Web UI \u2713\n\nYou are already here! This page is the web starter.\n\n### Key rule\nThe browser should never hold API keys, tokens, or OAuth secrets.\n\nIf you need private API calls, add a Python or Node backend.\n\n### Quick start\n```\n# Open web/index.html in VS Code with Live Preview\n# or open it directly in a browser.\n```", choices:[{label:"I also need private API calls \u2014 add a backend",next:"pick-fullstack"},{label:"Add Webex data to my UI",next:"webex-path"},{label:"Set up environment variables",next:"env-vars"},{label:"I\u2019m ready \u2014 what\u2019s my first prompt?",next:"first-prompt"}] },
  "pick-fullstack": { id:"pick-fullstack", type:"content-choice", title:"UI + Backend (Full Stack)", md:"## Full Stack Pattern \u2713\n\n```\nBrowser (web/)  \u2192  Your backend (Python or Node)  \u2192  External APIs\n```\n\nThe browser never touches secrets directly.\n\n### What goes where\n| Layer | Location | Holds |\n|---|---|---|\n| UI | `web/` | HTML, CSS, browser JS \u2014 no secrets |\n| Backend | `python/` or `node/` | API keys, tokens, logic |\n| Secrets | `.env` | Never committed to git |", choices:[{label:"My backend will be Python",next:"pick-python"},{label:"My backend will be Node",next:"pick-node"},{label:"Set up environment variables now",next:"env-vars"},{label:"Review the security rules",next:"security"}] },
  "webex-path": { id:"webex-path", type:"content-choice", title:"Webex Integration", md:"## Webex Integration\n\nThe sample uses a **Personal Access Token (PAT)** \u2014 treat it like a password.\n\n### Get your PAT\n1. Go to developer.webex.com\n2. Sign in \u2192 copy your personal token\n3. Add it to `.env` as `WEBEX_ACCESS_TOKEN`\n\n### Safe pattern\n```\nBrowser \u2192 Python/Node backend \u2192 Webex API\n```\n**Never call Webex directly from browser JavaScript.**", choices:[{label:"First explain what an API is",next:"what-is-an-api"},{label:"Full Webex setup guide",next:"webex-detail"},{label:"Set up my .env file",next:"env-vars"},{label:"My backend is Python",next:"pick-python"},{label:"My backend is Node",next:"pick-node"}], doc:"docs/WEBEX_SETUP.md" },
  "webex-detail": { id:"webex-detail", type:"doc", title:"Webex Setup \u2014 Full Guide", docKey:"docs/WEBEX_SETUP.md", next:"env-vars", nextLabel:"Next: Environment Variables \u2192" },
  "env-vars": { id:"env-vars", type:"content-choice", title:"Environment Variables", md:"## Setting Up Your .env\n\n```\ncopy .env.example .env\n```\n\nOpen `.env` and fill in only what you need.\n\n### Critical rules\n- \u2705 Commit `.env.example` (no real values)\n- \u274c Never commit `.env` (real secrets)\n- \u274c Never paste secrets into browser JavaScript\n\n### Variables you might need\n| Variable | For |\n|---|---|\n| `WEBEX_ACCESS_TOKEN` | Webex examples |\n| `BRIDGE_API_CLIENT_ID` | CIRCUIT examples |\n| `BRIDGE_API_CLIENT_SECRET` | CIRCUIT examples |", choices:[{label:"Full environment variables guide",next:"env-detail"},{label:"I\u2019ve set up .env \u2014 run my first sample",next:"run-sample"},{label:"Review security rules",next:"security"},{label:"Choose my coding tool",next:"pick-tool"},{label:"What is a CLI?",next:"what-is-a-cli"}], doc:"docs/ENV_VARS.md" },
  "env-detail": { id:"env-detail", type:"doc", title:"Environment Variables \u2014 Full Guide", docKey:"docs/ENV_VARS.md", next:"run-sample", nextLabel:"Next: Run a Sample \u2192" },
  "security": { id:"security", type:"doc", title:"Security Guide", docKey:"SECURITY.md", next:"pick-stack", nextLabel:"Got it \u2014 pick my stack \u2192" },
  "run-sample": { id:"run-sample", type:"choice", title:"Which sample do you want to run first?", choices:[{label:"Python CIRCUIT sample",next:"run-python-circuit"},{label:"Python Webex sample",next:"run-python-webex"},{label:"Node CIRCUIT sample",next:"run-node-circuit"},{label:"Node Webex sample",next:"run-node-webex"}] },
  "run-python-circuit": { id:"run-python-circuit", type:"terminal", title:"Run the Python CIRCUIT Sample", steps:[{label:"Activate your virtual environment",cmd:".\\.venv\\Scripts\\Activate.ps1"},{label:"Run the sample",cmd:"python python/examples/circuit_demo.py"}], note:"Make sure BRIDGE_API_CLIENT_ID and BRIDGE_API_CLIENT_SECRET are set in .env first.", next:"first-prompt" },
  "run-python-webex": { id:"run-python-webex", type:"terminal", title:"Run the Python Webex Sample", steps:[{label:"Activate your virtual environment",cmd:".\\.venv\\Scripts\\Activate.ps1"},{label:"Run the sample",cmd:"python python/examples/webex_demo.py"}], note:"Make sure WEBEX_ACCESS_TOKEN is set in .env first.", next:"first-prompt" },
  "run-node-circuit": { id:"run-node-circuit", type:"terminal", title:"Run the Node CIRCUIT Sample", steps:[{label:"Move into the node folder",cmd:"cd node"},{label:"Install dependencies (first time only)",cmd:"npm install"},{label:"Run the sample",cmd:"npm run circuit"}], note:"Make sure BRIDGE_API_CLIENT_ID and BRIDGE_API_CLIENT_SECRET are set in .env first.", next:"first-prompt" },
  "run-node-webex": { id:"run-node-webex", type:"terminal", title:"Run the Node Webex Sample", steps:[{label:"Move into the node folder",cmd:"cd node"},{label:"Install dependencies (first time only)",cmd:"npm install"},{label:"Run the sample",cmd:"npm run webex"}], note:"Make sure WEBEX_ACCESS_TOKEN is set in .env first.", next:"first-prompt" },
  "pick-tool": { id:"pick-tool", type:"choice", title:"Which AI coding tool are you using?", choices:[{label:"GitHub Copilot in VS Code",next:"tool-copilot"},{label:"Cursor",next:"tool-cursor"},{label:"Windsurf",next:"tool-windsurf"},{label:"Claude Code",next:"tool-claude"},{label:"OpenCode",next:"tool-opencode"},{label:"I haven\u2019t decided yet",next:"tool-guide"}] },
  "tool-guide": { id:"tool-guide", type:"doc", title:"Tool Guide \u2014 All Options", docKey:"docs/TOOL_GUIDE.md", next:"first-prompt", nextLabel:"Next: First Prompt \u2192" },
  "tool-copilot": { id:"tool-copilot", type:"content", title:"GitHub Copilot Setup", md:"## GitHub Copilot in VS Code \u2713\n\nYour repo instructions are already in place:\n- `.github/copilot-instructions.md` \u2014 project-level guidance\n- `.github/instructions/` \u2014 CodeGuard security rules\n\n### Good first prompts\n```\n\"Explain this repo to me like I am a beginner and tell me which folder to start in.\"\n\n\"Read the env docs and tell me which values I need for the Webex example.\"\n\n\"Help me build a small internal tool without exposing secrets in the browser.\"\n```", next:"first-prompt", doc:"docs/TOOL_GUIDE.md" },
  "tool-cursor": { id:"tool-cursor", type:"content", title:"Cursor Setup", md:"## Cursor \u2713\n\nYour repo rules are already in place:\n- `.cursor/rules/` \u2014 project-level rules for Cursor\n\nOpen the repo folder in Cursor. The rules load automatically.\n\n### Good first prompt\n```\n\"Explain this repo and tell me which starter file to change first.\"\n```", next:"first-prompt", doc:"docs/TOOL_GUIDE.md" },
  "tool-windsurf": { id:"tool-windsurf", type:"content", title:"Windsurf Setup", md:"## Windsurf \u2713\n\nYour repo rules are already in place:\n- `.windsurf/rules/` \u2014 project-level rules\n\nOpen the repo folder in Windsurf. The rules load automatically.", next:"first-prompt", doc:"docs/TOOL_GUIDE.md" },
  "tool-claude": { id:"tool-claude", type:"content", title:"Claude Code Setup", md:"## Claude Code \u2713\n\nYour repo already includes:\n- `CLAUDE.md` \u2014 project guidance for Claude Code\n- `.agent/rules/` \u2014 CodeGuard security rules\n\nRun `claude` in the repo root. Claude Code will read `CLAUDE.md` automatically.", next:"first-prompt", doc:"docs/TOOL_GUIDE.md" },
  "tool-opencode": { id:"tool-opencode", type:"content", title:"OpenCode Setup", md:"## OpenCode \u2713\n\nYour repo already includes:\n- `AGENTS.md` \u2014 project guidance for OpenCode\n- `.opencode/skills/` \u2014 CodeGuard security skills\n\nRun `opencode` in the repo root. It reads `AGENTS.md` automatically.", next:"first-prompt", doc:"docs/TOOL_GUIDE.md" },
  "first-prompt": { id:"first-prompt", type:"content", title:"You\u2019re Ready \u2014 Your First Prompt", md:"## You\u2019re set up \u2713\n\nHere are strong first prompts for any AI coding assistant:\n\n```\n\"Explain this repo to me like I am a beginner and\n tell me which folder I should start in.\"\n```\n\n```\n\"Read the env docs and tell me which values I need\n for the Webex example.\"\n```\n\n```\n\"Help me build a simple dashboard using the existing\n starter files without exposing secrets in the browser.\"\n```\n\n## Next steps\n\n- Ask the assistant to **explain before it edits**.\n- Make **one small change** at a time.\n- Run and verify a sample before building on top of it.", next:null }
};

// ── State ──────────────────────────────────────────────────────
var wizHistory = [];
var currentNodeId = "welcome";
try {
  var s = JSON.parse(localStorage.getItem("wiz-state") || "{}");
  if (s.currentNodeId && NODES[s.currentNodeId]) { currentNodeId = s.currentNodeId; wizHistory = s.wizHistory || []; }
} catch(e) {}

function saveState() { try { localStorage.setItem("wiz-state", JSON.stringify({currentNodeId:currentNodeId,wizHistory:wizHistory})); } catch(e) {} }

// ── DOM ────────────────────────────────────────────────────────
var wizardBody   = document.getElementById("wizard-body");
var breadcrumb   = document.getElementById("wizard-breadcrumb");
var progressFill = document.getElementById("wizard-progress-fill");
var btnBack      = document.getElementById("btn-back");
var btnNext      = document.getElementById("btn-next");
var btnRestart   = document.getElementById("btn-restart");
var overlay      = document.getElementById("doc-overlay");
var overlayTitle = document.getElementById("doc-overlay-title");
var overlayBody  = document.getElementById("doc-overlay-body");
var closeBtn     = document.getElementById("doc-close-btn");

// ── MD ─────────────────────────────────────────────────────────
function renderMd(text) {
  if (typeof marked !== "undefined") { try { return marked.parse(text); } catch(e) {} }
  return "<p>" + text.replace(/\n\n/g,"</p><p>") + "</p>";
}
function esc(s) { return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }

// ── Navigation ─────────────────────────────────────────────────
function goTo(id, push) {
  if (push !== false) wizHistory.push(currentNodeId);
  currentNodeId = id; saveState(); renderPage();
}
function goBack() { if (!wizHistory.length) return; currentNodeId = wizHistory.pop(); saveState(); renderPage(); }
function restart() { wizHistory = []; currentNodeId = "welcome"; saveState(); renderPage(); }

// ── Render ─────────────────────────────────────────────────────
function renderPage() {
  var node = NODES[currentNodeId];
  if (!node) { restart(); return; }

  var pct = Math.min(98, wizHistory.length === 0 ? 4 : 4 + wizHistory.length * 11);
  progressFill.style.width = pct + "%";

  var crumbs = wizHistory.slice(-3);
  var ch = crumbs.map(function(id) {
    var n = NODES[id]; return n ? "<span class='crumb'>" + esc(n.title) + "</span><span class='crumb-sep'>\u203a</span>" : "";
  }).join("") + "<span class='crumb crumb-current'>" + esc(node.title) + "</span>";
  breadcrumb.innerHTML = ch;

  btnBack.hidden    = wizHistory.length === 0;
  btnNext.hidden    = true;
  btnRestart.hidden = currentNodeId === "welcome";

  if (node.type === "hero")           renderHero(node);
  else if (node.type === "choice")    renderChoice(node);
  else if (node.type === "content")   renderContent(node);
  else if (node.type === "content-choice") renderContentChoice(node);
  else if (node.type === "doc")       renderDoc(node);
  else if (node.type === "terminal")  renderTerminal(node);
  else renderContent(node);
}

function renderHero(node) {
  wizardBody.innerHTML =
    "<div class='wiz-hero'>" +
      "<p class='wiz-eyebrow'>Guided Setup</p>" +
      "<h1 class='wiz-h1'>" + esc(node.title) + "</h1>" +
      "<p class='wiz-lede'>" + esc(node.body) + "</p>" +
      "<div class='wiz-choices wiz-choices-hero'>" +
        node.choices.map(function(c){ return "<button class='wiz-choice-btn wiz-choice-hero' data-next='" + c.next + "'>" + esc(c.label) + "</button>"; }).join("") +
      "</div>" +
    "</div>";
  bindChoices(); bindDocBtns();
}

function renderChoice(node) {
  wizardBody.innerHTML =
    "<div class='wiz-choice-screen'>" +
      "<h2 class='wiz-h2'>" + esc(node.title) + "</h2>" +
      "<div class='wiz-choices'>" +
        node.choices.map(function(c){ return "<button class='wiz-choice-btn' data-next='" + c.next + "'>" + esc(c.label) + "</button>"; }).join("") +
      "</div>" +
    "</div>";
  bindChoices();
}

function renderContent(node) {
  var mdHtml = node.md ? renderMd(node.md) : (node.body ? "<p>" + esc(node.body) + "</p>" : "");
  var docBtn = node.doc ? "<button class='wiz-doc-btn' data-doc='" + node.doc + "'>Read full doc \u2197</button>" : "";
  if (node.next) { btnNext.hidden = false; btnNext.textContent = node.nextLabel || "Continue \u2192"; btnNext.onclick = function(){ goTo(node.next); }; }
  else { btnRestart.hidden = false; }
  wizardBody.innerHTML =
    "<div class='wiz-content'>" +
      "<h2 class='wiz-h2'>" + esc(node.title) + "</h2>" +
      "<div class='md-content'>" + mdHtml + "</div>" +
      docBtn +
    "</div>";
  bindDocBtns();
}

function renderContentChoice(node) {
  var mdHtml = node.md ? renderMd(node.md) : "";
  var docBtn = node.doc ? "<button class='wiz-doc-btn' data-doc='" + node.doc + "'>Read full doc \u2197</button>" : "";
  wizardBody.innerHTML =
    "<div class='wiz-content-choice'>" +
      "<h2 class='wiz-h2'>" + esc(node.title) + "</h2>" +
      "<div class='md-content'>" + mdHtml + "</div>" +
      docBtn +
      "<div class='wiz-choices wiz-choices-after-content'>" +
        node.choices.map(function(c){ return "<button class='wiz-choice-btn' data-next='" + c.next + "'>" + esc(c.label) + "</button>"; }).join("") +
      "</div>" +
    "</div>";
  bindChoices(); bindDocBtns();
}

function renderDoc(node) {
  var content = DOCS[node.docKey] || "# " + node.title + "\n\nContent not found.";
  btnNext.hidden = false; btnNext.textContent = node.nextLabel || "Continue \u2192";
  btnNext.onclick = function(){ goTo(node.next); };
  wizardBody.innerHTML =
    "<div class='wiz-doc-view'>" +
      "<div class='md-content'>" + renderMd(content) + "</div>" +
    "</div>";
}

function renderTerminal(node) {
  var noteHtml = node.note ? "<div class='term-note'><strong>\u26a0 Note:</strong> " + esc(node.note) + "</div>" : "";
  var stepsHtml = node.steps.map(function(s, i){
    return "<div class='term-step'><div class='term-step-label'><span class='term-step-num'>" + (i+1) + "</span><span>" + esc(s.label) + "</span></div><pre class='code-block'>" + esc(s.cmd) + "</pre></div>";
  }).join("");
  btnNext.hidden = false; btnNext.textContent = "That worked \u2014 Continue \u2192";
  btnNext.onclick = function(){ goTo(node.next); };
  wizardBody.innerHTML =
    "<div class='wiz-terminal'>" +
      "<h2 class='wiz-h2'>" + esc(node.title) + "</h2>" +
      noteHtml + "<div class='term-steps'>" + stepsHtml + "</div>" +
    "</div>";
}

function bindChoices() {
  var btns = wizardBody.querySelectorAll(".wiz-choice-btn");
  for (var i = 0; i < btns.length; i++) {
    (function(b){ b.addEventListener("click", function(){ goTo(b.dataset.next); }); })(btns[i]);
  }
}
function bindDocBtns() {
  var btns = wizardBody.querySelectorAll(".wiz-doc-btn");
  for (var i = 0; i < btns.length; i++) {
    (function(b){ b.addEventListener("click", function(){ openDoc(b.dataset.doc); }); })(btns[i]);
  }
}

btnBack.addEventListener("click", goBack);
btnRestart.addEventListener("click", restart);
closeBtn.addEventListener("click", function(){ overlay.hidden = true; });
overlay.addEventListener("click", function(e){ if (e.target === overlay) overlay.hidden = true; });

function openDoc(key) {
  var content = DOCS[key]; if (!content) return;
  overlayTitle.textContent = key;
  overlayBody.innerHTML = renderMd(content);
  overlay.hidden = false;
}

// ── Style switcher ──────────────────────────────────────────────
var layoutChips = document.querySelectorAll(".layout-chip");
var colorChips  = document.querySelectorAll(".color-chip");
var htmlEl      = document.documentElement;

function setLayout(id) {
  htmlEl.setAttribute("data-layout", String(id));
  for (var i=0;i<layoutChips.length;i++) layoutChips[i].classList.toggle("active", layoutChips[i].dataset.layoutId === String(id));
  try { localStorage.setItem("wiz-layout", String(id)); } catch(e){}
}
function setColor(id) {
  htmlEl.setAttribute("data-color", String(id));
  for (var i=0;i<colorChips.length;i++) colorChips[i].classList.toggle("active", colorChips[i].dataset.colorId === String(id));
  try { localStorage.setItem("wiz-color", String(id)); } catch(e){}
}
for (var li=0;li<layoutChips.length;li++)(function(c){c.addEventListener("click",function(){setLayout(c.dataset.layoutId);});})(layoutChips[li]);
for (var ci=0;ci<colorChips.length;ci++)(function(c){c.addEventListener("click",function(){setColor(c.dataset.colorId);});})(colorChips[ci]);

var savedLayout="", savedColor="";
try { savedLayout=localStorage.getItem("wiz-layout")||""; savedColor=localStorage.getItem("wiz-color")||""; } catch(e){}
setLayout(savedLayout||htmlEl.getAttribute("data-layout")||"1");
setColor(savedColor||htmlEl.getAttribute("data-color")||"1");

renderPage();