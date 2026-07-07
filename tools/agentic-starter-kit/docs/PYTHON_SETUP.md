# Python Setup

Use this page if you want to run the Python starter files.

## Recommendation

Use a local virtual environment named `.venv`.

Why:

- it keeps this repo's Python packages separate from other projects
- it reduces version conflicts on less technical machines
- it is already ignored by git in this template

Do not commit a virtual environment into the repository. Each person should create their own local `.venv`.

## What To Install First

Install Python 3.11 or newer if you do not already have it.

When installing on Windows, enable the option that adds Python to your PATH if the installer offers it.

## First-Time Setup

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r python/requirements.txt
```

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r python/requirements.txt
```

## Run The Examples

```powershell
python python/examples/webex_demo.py
python python/examples/circuit_demo.py
python python/examples/outlook_action_items_demo.py
```

## Common Beginner Notes

- If `python` does not work, try `python3`.
- If activation is blocked in PowerShell, open a new terminal and run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

- Keep the terminal open while the virtual environment is active.
- When you come back later, activate `.venv` again before running Python commands.

## What The Virtual Environment Does

A virtual environment is just a project-local Python toolbox. It gives this repo its own package installs without changing other Python projects on your machine.