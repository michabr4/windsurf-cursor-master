# Getting started (about 30 minutes)

Welcome. This guide sets up your **Delivery Workbench** without any external tools.

## 1. Open the workspace

1. In Cursor: **File → Open Folder** → choose this `delivery-workbench` folder.
2. Skim [README.md](README.md) and [SECURITY.md](SECURITY.md).

## 2. Optional: environment file

Only needed for the local server or CLI helpers.

```bash
cp .env.example .env
```

You can leave defaults. Set `USE_LLM=1` only if you run a local Ollama instance and want optional draft polish.

## 3. Try a playbook without the server

1. Open `playbooks/weekly-rhythm.md`.
2. In Cursor chat, say: *Walk me through weekly-rhythm for project `_example` using the templates.*
3. Save the result under `data/` or `projects/_example/outputs/`.

No API keys required.

## 4. Optional: local home page

```bash
python3 python/server/workbench_server.py
```

Open `http://127.0.0.1:8840/` (port from `.env` or default 8840).

Press Ctrl+C to stop the server.

## 5. Scaffold a draft from the CLI

```bash
chmod +x scripts/workbench.sh
./scripts/workbench.sh new-status-draft --project _example
```

Creates a dated file under `data/_example/` from `templates/status-report.md`.

List commands:

```bash
./scripts/workbench.sh --help
```

## 6. Add your first real project

```bash
cp -r projects/_example projects/my-engagement
```

Edit `projects/my-engagement/project.yaml` (name, cadence, stakeholders—no secrets).

## 7. Weekly habit

| When | What |
|------|------|
| Monday | `playbooks/weekly-rhythm.md` |
| After meetings | `playbooks/meeting-follow-up.md` |
| Before steering | `playbooks/status-report.md` or `stakeholder-update.md` |
| When risks appear | `playbooks/raid-log.md` |

## 8. Integrations (later)

When you have used file-based workflows for a week or two, read [docs/CONNECTORS.md](docs/CONNECTORS.md) to add optional connectors one at a time.

## Need help in Cursor?

Ask: *Follow SECURITY.md and the playbook for [name]. Draft only; do not post anywhere.*
