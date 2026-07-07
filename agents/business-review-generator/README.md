# Business Review Generator — Agent #3 (T2 HITL)

On-demand QBR/EBR draft generator. Pulls Helix + Salesforce (stub) + Delivery Tracker data, computes metrics, runs four LLM passes, saves a markdown draft, and optionally notifies Webex.

## Quick start

```bash
cd agents/business-review-generator
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

python main.py --account "Acme Corp" --quarter Q2-2026 --dry-run
```

## CLI

```bash
python main.py --account "Acme Corp" --quarter Q2-2026 [--dry-run] [--format md]
```

Output: `data/runs/business-review/YYYY-MM-DD-{account_slug}.md`

## Tests

```bash
pytest tests/ -v
```

## Trust tier

T2 — every draft requires SDM/CXM review. Agent never sends to customers.
