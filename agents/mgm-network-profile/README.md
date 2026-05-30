# MGM Resorts Network Profile

Extracts a full network baseline snapshot for MGM Resorts International via the Cisco MIMIR NetProfile API and delivers a prioritised list of actionable recommendations.

**Trust Tier:** T3 — Human-Triggered  
**Company Key (cpyKey):** 172361

---

## Quick Start

```bash
# 1. Create and activate a virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env — set MIMIR_COOKIE_FILE at minimum

# 4. Run baseline extraction
python main.py

# 5. Dump JSON snapshot to output/
python main.py --json
```

---

## Environment Variables

| Variable | Default | Description |
| --- | --- | --- |
| `MIMIR_URL` | `https://mimir-prod.cisco.com` | MIMIR API base URL |
| `NP_CPY_KEY` | `172361` | MGM Resorts NetProfile company key |
| `MIMIR_COOKIE_FILE` | `default` | SSO cookie file path (`default` = `~/.mimir-cookies-py`) |
| `MIMIR_CACHE_DIR` | `/tmp/mimir-cache` | Local MIMIR response cache directory |
| `CLI_DEVICE_LIMIT` | `50` | Max devices to query CLI data for per run |
| `CLI_COMMANDS` | `show version,show ip interface brief,show clock` | Comma-separated CLI commands |
| `LOG_LEVEL` | `INFO` | Python logging level |

---

## Project Structure

```text
agents/mgm-network-profile/
├── agent.py          # AI Factory T3 agent class
├── config.py         # Environment configuration (pydantic-settings)
├── models.py         # Typed dataclasses
├── np_client.py      # MIMIR NetProfile client wrapper
├── extractor.py      # Data extraction pipeline
├── recommender.py    # Recommendation engine (5 categories)
├── main.py           # CLI entry point
├── tools/
│   └── np_tools.py   # Composable tool functions
├── tests/
│   ├── conftest.py
│   ├── test_agent.py
│   └── test_tools.py
├── .env.example
├── requirements.txt
├── AGENT_CARD.md
└── README.md
```

---

## Recommendation Categories

1. **Software Currency** — devices running EOS or outdated IOS versions
2. **Collector Health** — stale or missing NetProfile collectors
3. **Device Reachability** — devices with no CLI or config data collected
4. **Config Compliance** — devices missing best-practice configuration elements
5. **Inventory Coverage** — devices not assigned to any NetProfile group

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Governance

See [AGENT_CARD.md](AGENT_CARD.md) for trust tier, integrations, KPIs, and pilot plan.
