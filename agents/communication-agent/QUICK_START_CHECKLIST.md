# WebEx_Email_Comm_Intelligence Agent Quick Start Checklist

## 1) Open project folder

- [ ] Open terminal in `communication-agent/` (`WebEx_Email_Comm_Intelligence Agent`)

## 2) Install dependencies

- [ ] Create venv: `python -m venv venv`
- [ ] Activate venv: `source venv/bin/activate`
- [ ] Install packages: `pip install -r requirements.txt`

## 3) Configure environment

- [ ] Copy template: `cp .env.example .env`
- [ ] Set `WEBEX_ACCESS_TOKEN`
- [ ] Set `MS_CLIENT_ID`, `MS_CLIENT_SECRET`, `MS_TENANT_ID`
- [ ] Confirm `MS_USER_EMAIL=michabr4@cisco.com`
- [ ] Set one LLM provider:
  - [ ] `LLM_PROVIDER=openai` + `OPENAI_API_KEY`
  - [ ] or `LLM_PROVIDER=anthropic` + `ANTHROPIC_API_KEY`

## 4) Run the agent

- [ ] Standard run: `python main.py --days 7 --output-all`
- [ ] Optional source filter: `python main.py --sources webex_chat email`
- [ ] Optional no-LLM mode: `python main.py --no-llm`

## 5) Validate outputs

- [ ] Open `output/` folder
- [ ] Review generated files:
  - [ ] `report_*.json`
  - [ ] `actions_*.csv`
  - [ ] `report_*.md`
- [ ] Check high-priority and overdue items first

## 6) Operational next steps

- [ ] Schedule daily run (cron/Task Scheduler)
- [ ] Route high-priority actions to your task tracker
- [ ] Review and tune keywords in `.env`:
  - [ ] `HIGH_PRIORITY_KEYWORDS`
  - [ ] `MEDIUM_PRIORITY_KEYWORDS`
