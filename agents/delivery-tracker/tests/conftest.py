"""Shared fixtures for Delivery Tracker tests."""

import sys
from pathlib import Path

import pytest

# Ensure the agent root is on sys.path so imports work without installing
_AGENT_ROOT = Path(__file__).resolve().parents[1]
if str(_AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(_AGENT_ROOT))

from config import Settings
from models import HelixAccount, HelixCase, HelixMilestone, HelixSLARecord

from datetime import datetime, date, timedelta, timezone


@pytest.fixture()
def settings() -> Settings:
    return Settings(
        helix_base_url="https://helix.test/api/v1",
        helix_api_token="test-token-abc123",
        lookback_days=7,
    )


@pytest.fixture()
def sample_account() -> HelixAccount:
    return HelixAccount(id="acc-001", name="ACME Corp")


@pytest.fixture()
def sample_open_case() -> HelixCase:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    return HelixCase(
        id="case-001",
        case_number="CS-001",
        title="Production login failure",
        status="open",
        priority="high",
        account_id="acc-001",
        account_name="ACME Corp",
        created_date=now - timedelta(days=3),
        updated_date=now,
        is_escalated=False,
    )


@pytest.fixture()
def sample_overdue_case() -> HelixCase:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    return HelixCase(
        id="case-002",
        case_number="CS-002",
        title="Slow dashboard reports",
        status="in_progress",
        priority="medium",
        account_id="acc-001",
        account_name="ACME Corp",
        created_date=now - timedelta(days=10),
        updated_date=now - timedelta(days=2),
        due_date=now - timedelta(days=1),
        is_escalated=False,
    )


@pytest.fixture()
def sample_milestone() -> HelixMilestone:
    return HelixMilestone(
        id="ms-001",
        name="Phase 1 Rollout",
        account_id="acc-001",
        status="in_progress",
        due_date=date.today() + timedelta(days=14),
        completion_pct=60.0,
    )


@pytest.fixture()
def sample_sla() -> HelixSLARecord:
    today = date.today()
    return HelixSLARecord(
        account_id="acc-001",
        period_start=today - timedelta(days=7),
        period_end=today,
        target_pct=95.0,
        actual_pct=97.5,
        cases_total=40,
        cases_met=39,
        cases_breached=1,
    )
