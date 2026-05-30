# Agent Card — MGM Resorts Network Profile

| Field | Value |
| --- | --- |
| **Agent Name** | MGM Resorts Network Profile |
| **Short Name** | `mgm-network-profile` |
| **Trust Tier** | T3 — Human-Triggered |
| **Status** | Development |
| **Owner** | AI Factory |
| **Last Updated** | 2026-05-28 |

---

## Purpose

Connects to the Cisco MIMIR API (NetProfile service) to extract a full network baseline snapshot for MGM Resorts International (cpyKey=172361). Analyses the snapshot across five categories and delivers a prioritised list of recommendations to help the team identify risks, outdated software, and operational gaps.

---

## Integrations

| System | Purpose | Auth |
| --- | --- | --- |
| Cisco MIMIR API | NetProfile data source (companies, groups, devices, collectors, CLI, configs) | SSO cookie file |

---

## Human Input Required

| Trigger | Input |
| --- | --- |
| Manual run | Optionally override `--cpy-key`; pass `--json` to dump snapshot to `output/` |

---

## Expected Results

- Structured `NPSnapshot` containing company, groups, devices, and collectors for cpyKey=172361.
- Prioritised `Recommendation` list covering:
  1. **Software Currency** — EOS / outdated IOS versions
  2. **Collector Health** — stale or missing collectors
  3. **Device Reachability** — devices with no CLI/config data
  4. **Config Compliance** — missing best-practice config elements
  5. **Inventory Coverage** — devices not assigned to any group

---

## KPIs

| Metric | Target |
| --- | --- |
| Records processed | All devices for cpyKey=172361 |
| Run duration | < 5 min on warm cache |
| Findings produced | ≥ 1 actionable recommendation per run |
| Errors | 0 unhandled exceptions |

---

## Files

```text
agents/mgm-network-profile/
├── agent.py          # T3 agent class — run(), validate_inputs(), handle_error(), KPI metrics
├── config.py         # pydantic-settings environment configuration
├── models.py         # typed dataclasses (NPCompany, NPGroup, NPDevice, NPCollector, etc.)
├── np_client.py      # MIMIR NetProfile client wrapper
├── extractor.py      # extraction pipeline (groups → devices → CLI → collectors)
├── recommender.py    # recommendation engine (5 categories)
├── main.py           # CLI entry point
├── tools/
│   ├── __init__.py
│   └── np_tools.py   # composable tool functions for LLM orchestrators
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_agent.py
│   └── test_tools.py
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── AGENT_CARD.md
```

---

## Pilot Plan

1. Run against MGM Resorts cpyKey=172361 in a dev environment with cached MIMIR data.
2. Review recommendations output with the SDM team.
3. Iterate on recommendation thresholds and categories.
4. Schedule weekly automated runs once T3 → T2 promotion criteria are met.

---

## Pre-Submission Checklist

- [x] `trust_tier = "T3"` declared
- [x] `run()`, `validate_inputs()`, `handle_error()` implemented
- [x] KPI metrics printed at end of `run()`
- [x] No hardcoded credentials — all config via `.env`
- [x] `.env.example` provided
- [x] `requirements.txt` present
- [x] Tests in `tests/` with fixtures in `conftest.py`
- [x] `AGENT_CARD.md` present
- [x] `README.md` present
