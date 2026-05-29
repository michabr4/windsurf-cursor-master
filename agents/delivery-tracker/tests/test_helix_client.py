"""Unit tests for HelixClient.

All HTTP calls are mocked via the `responses` library — no real API required.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest
import responses as rsps_lib

from helix_client import HelixAPIError, HelixClient
from models import SLAStatus


@pytest.fixture()
def client(settings):
    return HelixClient(settings)


@rsps_lib.activate
def test_get_accounts_returns_list(client, settings):
    rsps_lib.add(
        rsps_lib.GET,
        f"{settings.helix_base_url}/accounts",
        json=[
            {"id": "acc-1", "name": "ACME Corp"},
            {"id": "acc-2", "name": "Globex"},
        ],
    )
    accounts = client.get_accounts()
    assert len(accounts) == 2
    assert accounts[0].id == "acc-1"
    assert accounts[1].name == "Globex"


@rsps_lib.activate
def test_get_accounts_with_pagination_envelope(client, settings):
    rsps_lib.add(
        rsps_lib.GET,
        f"{settings.helix_base_url}/accounts",
        json={"results": [{"id": "acc-3", "name": "Initech"}], "count": 1},
    )
    accounts = client.get_accounts()
    assert len(accounts) == 1
    assert accounts[0].name == "Initech"


@rsps_lib.activate
def test_get_open_cases_filters_by_status(client, settings):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    rsps_lib.add(
        rsps_lib.GET,
        f"{settings.helix_base_url}/cases",
        json=[
            {
                "id": "case-1",
                "case_number": "CS-001",
                "title": "Login failure",
                "status": "open",
                "priority": "high",
                "account_id": "acc-1",
                "created_date": now.isoformat(),
                "updated_date": now.isoformat(),
                "is_escalated": False,
            }
        ],
    )
    cases = client.get_open_cases("acc-1")
    assert len(cases) == 1
    assert cases[0].priority == "high"
    assert cases[0].is_overdue is False


@rsps_lib.activate
def test_overdue_case_detected(client, settings):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    rsps_lib.add(
        rsps_lib.GET,
        f"{settings.helix_base_url}/cases",
        json=[
            {
                "id": "case-2",
                "case_number": "CS-002",
                "title": "Slow reports",
                "status": "in_progress",
                "priority": "medium",
                "account_id": "acc-1",
                "created_date": (now - timedelta(days=10)).isoformat(),
                "updated_date": now.isoformat(),
                "due_date": (now - timedelta(days=1)).isoformat(),
                "is_escalated": False,
            }
        ],
    )
    cases = client.get_open_cases("acc-1")
    assert cases[0].is_overdue is True


@rsps_lib.activate
def test_get_milestones_parses_completion(client, settings):
    rsps_lib.add(
        rsps_lib.GET,
        f"{settings.helix_base_url}/milestones",
        json=[
            {
                "id": "ms-1",
                "name": "Phase 1",
                "account_id": "acc-1",
                "status": "in_progress",
                "completion_pct": 75.0,
                "due_date": "2026-12-31",
            }
        ],
    )
    milestones = client.get_milestones("acc-1")
    assert len(milestones) == 1
    assert milestones[0].completion_pct == 75.0


@rsps_lib.activate
def test_get_sla_metrics_met(client, settings):
    rsps_lib.add(
        rsps_lib.GET,
        f"{settings.helix_base_url}/sla/metrics",
        json={
            "target_pct": 95.0,
            "actual_pct": 98.0,
            "cases_total": 50,
            "cases_met": 49,
            "cases_breached": 1,
        },
    )
    sla = client.get_sla_metrics("acc-1")
    assert sla is not None
    assert sla.status == SLAStatus.MET
    assert sla.actual_pct == 98.0


@rsps_lib.activate
def test_get_sla_metrics_breached(client, settings):
    rsps_lib.add(
        rsps_lib.GET,
        f"{settings.helix_base_url}/sla/metrics",
        json={
            "target_pct": 95.0,
            "actual_pct": 80.0,
            "cases_total": 20,
            "cases_met": 16,
            "cases_breached": 4,
        },
    )
    sla = client.get_sla_metrics("acc-1")
    assert sla.status == SLAStatus.BREACHED


@rsps_lib.activate
def test_helix_api_error_on_4xx(client, settings):
    rsps_lib.add(
        rsps_lib.GET,
        f"{settings.helix_base_url}/accounts",
        status=401,
        body="Unauthorized",
    )
    with pytest.raises(HelixAPIError) as exc_info:
        client.get_accounts()
    assert exc_info.value.status_code == 401


@rsps_lib.activate
def test_auth_header_sent(client, settings):
    rsps_lib.add(
        rsps_lib.GET,
        f"{settings.helix_base_url}/accounts",
        json=[],
    )
    client.get_accounts()
    req = rsps_lib.calls[0].request
    assert req.headers["Authorization"] == f"Bearer {settings.helix_api_token}"


@rsps_lib.activate
def test_sla_returns_none_on_404(client, settings):
    rsps_lib.add(
        rsps_lib.GET,
        f"{settings.helix_base_url}/sla/metrics",
        status=404,
        body="Not found",
    )
    result = client.get_sla_metrics("acc-1")
    assert result is None
