---
description: MGM Network Profile Agent — local context rules
alwaysApply: true
---

# MGM Resorts Network Profile Agent — Local Rules

## Agent Identity

- **Trust Tier:** T3 (Human-Triggered — no autonomous scheduling)
- **Company Key:** `NP_CPY_KEY=172361` (MGM Resorts International)
- **Primary API:** Cisco MIMIR NetProfile (`https://mimir-prod.cisco.com`)
- **Auth:** SSO cookie file (`MIMIR_COOKIE_FILE` env var)

## Module Layout

All imports within this agent are local (no `agents.mgm-network-profile` prefix):

```python
from config import get_settings, Settings
from extractor import NPExtractor
from models import NPSnapshot, NPDevice, NPGroup, NPCollector, Recommendation
from recommender import NPRecommender
from np_client import MIMIRNetProfileClient
```

Tools are imported as:

```python
from tools.np_tools import fetch_snapshot, generate_recommendations, snapshot_summary, top_findings
```

## Key Data Models (`models.py`)

- `NPCompany` — `cpy_key`, `cpy_name`
- `NPGroup` — `group_id`, `group_name`, `cpy_key`
- `NPDevice` — `device_id`, `device_name`, `cpy_key`, `group_id`, `software_version`, `platform`
- `NPCollector` — `collector`, `cpy_key`, `last_contact`
- `NPSnapshot` — aggregate root; exposes `device_count`, `collector_count`, `recommendations`
- `Recommendation` — `priority` (int, lower=higher), `category`, `title`, `device_name`, `detail`

## Recommendation Categories (5 fixed)

1. **Software Currency** — EOS / outdated IOS
2. **Collector Health** — stale or missing collectors
3. **Device Reachability** — no CLI or config data
4. **Config Compliance** — missing best-practice config elements
5. **Inventory Coverage** — devices not assigned to any group

## Settings Defaults (`config.py` / `.env.example`)

| Variable | Default |
| --- | --- |
| `MIMIR_URL` | `https://mimir-prod.cisco.com` |
| `NP_CPY_KEY` | `172361` |
| `MIMIR_COOKIE_FILE` | `default` (`~/.mimir-cookies-py`) |
| `MIMIR_CACHE_DIR` | `/tmp/mimir-cache` |
| `CLI_DEVICE_LIMIT` | `50` |
| `CLI_COMMANDS` | `show version,show ip interface brief,show clock` |
| `LOG_LEVEL` | `INFO` |

## Testing Conventions

- All tests live in `tests/`; fixtures in `tests/conftest.py`
- Patch targets use full dotted paths: `agent.NPExtractor`, `tools.np_tools.NPExtractor`
- Never hit the real MIMIR API in tests — always mock `NPExtractor` and `NPRecommender`
- The `populated_snapshot` fixture has exactly 1 group, 1 device, 1 collector

## Security Rules (Non-Negotiable)

- MIMIR cookie value must NEVER appear in source code
- All credentials via `.env` only; `.env` is in `.gitignore`
- HTTPS enforced for all MIMIR calls (verify the base URL starts with `https://`)
