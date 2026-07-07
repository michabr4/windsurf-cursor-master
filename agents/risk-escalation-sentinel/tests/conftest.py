"""Shared fixtures for Risk & Escalation Sentinel tests."""

import json
import sys
from pathlib import Path

import pytest

_AGENT_ROOT = Path(__file__).resolve().parents[1]
if str(_AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(_AGENT_ROOT))

from config import Settings
from models import DeliveryAccountRecord


@pytest.fixture()
def settings(tmp_path) -> Settings:
    data_dir = tmp_path / "data" / "runs"
    tracker_dir = data_dir / "delivery-tracker"
    tracker_dir.mkdir(parents=True)
    sentinel_dir = data_dir / "risk-sentinel"
    sentinel_dir.mkdir(parents=True)
    return Settings(
        data_dir=str(data_dir),
        webex_bot_token="test-webex-token",
        webex_room_id="room-123",
        dry_run=True,
    )


@pytest.fixture()
def sample_tracker_payload() -> dict:
    return {
        "period_label": "Week of 2026-05-29",
        "lookback_days": 7,
        "accounts": [
            {
                "account_id": "acc-high",
                "account_name": "High Risk Co",
                "total_open": 5,
                "critical_high": 2,
                "avg_age_days": 3,
                "p1_p2_open_over_48h": 1,
            },
            {
                "account_id": "acc-low",
                "account_name": "Stable Co",
                "total_open": 1,
                "critical_high": 0,
                "avg_age_days": 1,
            },
        ],
    }


@pytest.fixture()
def tracker_json_file(settings, sample_tracker_payload):
    path = settings.delivery_tracker_dir / "2026-05-29.json"
    path.write_text(json.dumps(sample_tracker_payload), encoding="utf-8")
    return path


@pytest.fixture()
def p1_p2_account() -> DeliveryAccountRecord:
    return DeliveryAccountRecord(
        account_id="a1",
        account_name="Alpha",
        p1_p2_open_over_48h=2,
    )


@pytest.fixture()
def sla_account() -> DeliveryAccountRecord:
    return DeliveryAccountRecord(
        account_id="a2",
        account_name="Beta",
        sla_breach_within_days=3,
    )


@pytest.fixture()
def health_account() -> DeliveryAccountRecord:
    return DeliveryAccountRecord(
        account_id="a3",
        account_name="Gamma",
        health_score=70,
        health_score_prior_7d=90,
    )


@pytest.fixture()
def milestone_account() -> DeliveryAccountRecord:
    return DeliveryAccountRecord(
        account_id="a4",
        account_name="Delta",
        milestone_slip_days=21,
    )


@pytest.fixture()
def entitlement_account() -> DeliveryAccountRecord:
    return DeliveryAccountRecord(
        account_id="a5",
        account_name="Epsilon",
        entitlement_pct=10,
        renewal_days=30,
    )
