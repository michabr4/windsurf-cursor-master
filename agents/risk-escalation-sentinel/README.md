# Risk & Escalation Sentinel — Agent #2 (T2 HITL)

Daily scan of Delivery Tracker JSON output. Applies five risk rules per account,
writes a sentinel report, and sends Webex HITL cards for HIGH risks.

## Quick start

```bash
cd agents/risk-escalation-sentinel
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Ensure Delivery Tracker JSON exists, e.g.:
# data/runs/delivery-tracker/2026-05-29.json

python main.py --dry-run --date 2026-05-29
python main.py --date 2026-05-29
```

## Risk rules

| Rule | Tier |
| --- | --- |
| P1/P2 open > 48h | HIGH |
| SLA breach predicted within 5 days | HIGH |
| Health score dropped > 15 pts in 7 days | HIGH |
| Milestone slipped > 2 weeks | MEDIUM |
| Entitlement < 20% with renewal < 60 days | MEDIUM |

## Output

- `data/runs/risk-sentinel/YYYY-MM-DD.json`
- Webex adaptive card per HIGH risk (four HITL buttons)

## Tests

```bash
pytest tests/ -v
```
