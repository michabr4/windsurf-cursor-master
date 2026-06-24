"""Unit tests for DeliveryTracker orchestrator.

HelixClient methods are mocked so no real HTTP is needed.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

from helix_client import HelixAPIError
from models import AccountCaseMetrics, HelixAccount, SLAStatus, WeeklySummary
from tracker import DeliveryTracker


def _make_tracker(settings, client_mock):
    tracker = DeliveryTracker(settings=settings)
    tracker._client = client_mock
    return tracker


def _mock_client(
    accounts=None,
    open_cases=None,
    milestones=None,
    sla=None,
    accounts_error=False,
):
    client = MagicMock()
    if accounts_error:
        client.get_accounts.side_effect = HelixAPIError("timeout", 0)
    else:
        client.get_accounts.return_value = accounts or []
    client.get_open_cases.return_value = open_cases or []
    client.get_milestones.return_value = milestones or []
    client.get_sla_metrics.return_value = sla
    return client


# ── Missing credentials ───────────────────────────────────────────────────────

def test_run_errors_when_no_credentials(settings):
    settings.helix_base_url = ""
    settings.helix_api_token = ""
    tracker = DeliveryTracker(settings=settings)
    summary = tracker.run()
    assert summary.has_errors
    assert "HELIX_BASE_URL" in summary.errors[0]


# ── No accounts returned ──────────────────────────────────────────────────────

def test_run_errors_when_no_accounts(settings):
    tracker = _make_tracker(settings, _mock_client(accounts=[]))
    summary = tracker.run()
    assert summary.has_errors
    assert "No accounts" in summary.errors[0]


# ── Accounts API failure ───────────────────────────────────────────────────────

def test_run_errors_on_accounts_api_failure(settings):
    tracker = _make_tracker(settings, _mock_client(accounts_error=True))
    summary = tracker.run()
    assert summary.has_errors
    assert "Failed to fetch accounts" in summary.errors[0]


# ── Happy path: basic aggregation ────────────────────────────────────────────

def test_run_aggregates_open_cases(settings, sample_account, sample_open_case, sample_milestone, sample_sla):
    client = _mock_client(
        accounts=[sample_account],
        open_cases=[sample_open_case],
        milestones=[sample_milestone],
        sla=sample_sla,
    )
    tracker = _make_tracker(settings, client)
    summary = tracker.run()

    assert not summary.has_errors
    assert summary.total_open_cases == 1
    assert summary.total_overdue == 0
    assert summary.total_escalated == 0
    assert len(summary.accounts) == 1
    assert summary.accounts[0].account_name == "ACME Corp"


def test_run_counts_overdue(settings, sample_account, sample_overdue_case):
    client = _mock_client(
        accounts=[sample_account],
        open_cases=[sample_overdue_case],
    )
    tracker = _make_tracker(settings, client)
    summary = tracker.run()

    assert summary.total_overdue == 1
    assert summary.accounts[0].overdue == 1


def test_run_flags_sla_at_risk(settings, sample_account, sample_sla):
    sample_sla.actual_pct = 90.0
    sample_sla.target_pct = 95.0
    client = _mock_client(
        accounts=[sample_account],
        sla=sample_sla,
    )
    tracker = _make_tracker(settings, client)
    summary = tracker.run()

    assert summary.accounts_at_risk_sla == ["ACME Corp"]


def test_run_handles_sla_api_error_gracefully(settings, sample_account):
    client = _mock_client(accounts=[sample_account])
    client.get_sla_metrics.side_effect = HelixAPIError("SLA endpoint unavailable", 503)
    tracker = _make_tracker(settings, client)
    summary = tracker.run()

    assert not summary.has_errors
    assert summary.accounts[0].sla_status is None


def test_run_handles_case_api_error_gracefully(settings, sample_account):
    client = _mock_client(accounts=[sample_account])
    client.get_open_cases.side_effect = HelixAPIError("Cases endpoint unavailable", 503)
    tracker = _make_tracker(settings, client)
    summary = tracker.run()

    assert not summary.has_errors
    assert summary.accounts[0].total_open == 0


# ── Multi-account aggregation ────────────────────────────────────────────────

def test_run_aggregates_multiple_accounts(settings, sample_open_case):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    accounts = [
        HelixAccount(id="acc-1", name="Account A"),
        HelixAccount(id="acc-2", name="Account B"),
    ]
    client = _mock_client(accounts=accounts, open_cases=[sample_open_case])
    tracker = _make_tracker(settings, client)
    summary = tracker.run()

    assert summary.total_open_cases == 2
    assert len(summary.accounts) == 2


# ── WeeklySummary defaults ────────────────────────────────────────────────────

def test_weekly_summary_defaults():
    s = WeeklySummary(period_label="test", lookback_days=7)
    assert s.total_open_cases == 0
    assert s.total_overdue == 0
    assert s.accounts_at_risk_sla == []
    assert not s.has_errors
    assert isinstance(s.generated_at, datetime)


# ── AI Factory standard methods ───────────────────────────────────────────────

def test_trust_tier():
    assert DeliveryTracker.trust_tier == "T1"


def test_validate_inputs_passes(settings):
    tracker = DeliveryTracker(settings=settings)
    tracker.validate_inputs()


def test_validate_inputs_fails(settings):
    settings.helix_base_url = ""
    settings.helix_api_token = ""
    tracker = DeliveryTracker(settings=settings)
    with pytest.raises(ValueError, match="HELIX_BASE_URL and HELIX_API_TOKEN"):
        tracker.validate_inputs()


def test_handle_error_reraises(settings):
    tracker = DeliveryTracker(settings=settings)
    exc = RuntimeError("boom")
    with pytest.raises(RuntimeError, match="boom"):
        tracker.handle_error(exc)


def test_run_prints_metrics(capsys, settings, sample_account, sample_open_case):
    client = _mock_client(accounts=[sample_account], open_cases=[sample_open_case])
    tracker = _make_tracker(settings, client)
    summary = tracker.run()
    captured = capsys.readouterr()
    assert "[METRICS]" in captured.out
    assert not summary.has_errors


def test_run_metrics_on_validation_failure(capsys, settings):
    settings.helix_base_url = ""
    settings.helix_api_token = ""
    tracker = DeliveryTracker(settings=settings)
    tracker.run()
    captured = capsys.readouterr()
    assert "[METRICS]" in captured.out


# ── Health score ──────────────────────────────────────────────────────────────

def test_health_score_perfect_account():
    m = AccountCaseMetrics(account_id="a", account_name="A")
    score = DeliveryTracker._compute_health_score(m)
    assert score == 100.0
    assert m.health_tier == "—"


def test_health_score_overdue_deducts():
    m = AccountCaseMetrics(account_id="a", account_name="A", overdue=3)
    score = DeliveryTracker._compute_health_score(m)
    assert score == 85.0


def test_health_score_overdue_cap():
    m = AccountCaseMetrics(account_id="a", account_name="A", overdue=10)
    score = DeliveryTracker._compute_health_score(m)
    assert score == 75.0


def test_health_score_sla_at_risk():
    m = AccountCaseMetrics(account_id="a", account_name="A", sla_status=SLAStatus.AT_RISK)
    score = DeliveryTracker._compute_health_score(m)
    assert score == 90.0


def test_health_score_sla_breached():
    m = AccountCaseMetrics(account_id="a", account_name="A", sla_status=SLAStatus.BREACHED)
    score = DeliveryTracker._compute_health_score(m)
    assert score == 75.0


def test_health_score_multiple_signals():
    m = AccountCaseMetrics(
        account_id="a",
        account_name="A",
        overdue=2,
        critical_high=3,
        escalated=1,
        sla_status=SLAStatus.AT_RISK,
        milestones_overdue=1,
    )
    score = DeliveryTracker._compute_health_score(m)
    assert score == 100.0 - 10 - 9 - 10 - 10 - 5


def test_health_score_never_below_zero():
    m = AccountCaseMetrics(
        account_id="a",
        account_name="A",
        overdue=100,
        critical_high=100,
        escalated=100,
        sla_status=SLAStatus.BREACHED,
        milestones_overdue=100,
    )
    score = DeliveryTracker._compute_health_score(m)
    assert score == 0.0


def test_health_tier_tiers():
    m = AccountCaseMetrics(account_id="a", account_name="A")
    m.health_score = 95.0
    assert m.health_tier == "🟢"
    m.health_score = 70.0
    assert m.health_tier == "🟡"
    m.health_score = 50.0
    assert m.health_tier == "🟠"
    m.health_score = 20.0
    assert m.health_tier == "🔴"


def test_run_sets_health_score(settings, sample_account, sample_open_case, sample_sla):
    client = _mock_client(
        accounts=[sample_account],
        open_cases=[sample_open_case],
        sla=sample_sla,
    )
    tracker = _make_tracker(settings, client)
    summary = tracker.run()
    assert summary.accounts[0].health_score is not None
    assert 0.0 <= summary.accounts[0].health_score <= 100.0
