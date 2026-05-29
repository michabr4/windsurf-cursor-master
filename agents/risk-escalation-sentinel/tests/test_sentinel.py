"""Tests for RiskEscalationSentinel orchestrator."""

from unittest.mock import MagicMock, patch

import pytest

from models import AccountRisk, RiskTier, SentinelReport
from sentinel import RiskEscalationSentinel


def test_trust_tier():
    assert RiskEscalationSentinel.trust_tier == "T2"


def test_validate_inputs_passes(settings):
    agent = RiskEscalationSentinel(settings=settings)
    agent.validate_inputs()


def test_validate_inputs_fails_when_data_dir_missing(tmp_path):
    from config import Settings

    settings = Settings(
        data_dir=str(tmp_path / "missing"),
        webex_bot_token="token",
        dry_run=False,
    )
    agent = RiskEscalationSentinel(settings=settings)
    with pytest.raises(ValueError, match="DATA_DIR"):
        agent.validate_inputs()


def test_validate_inputs_fails_when_webex_missing(settings):
    settings.webex_bot_token = ""
    settings.dry_run = False
    agent = RiskEscalationSentinel(settings=settings)
    with pytest.raises(ValueError, match="WEBEX_BOT_TOKEN"):
        agent.validate_inputs()


def test_handle_error_reraises(settings):
    agent = RiskEscalationSentinel(settings=settings)
    with pytest.raises(RuntimeError, match="boom"):
        agent.handle_error(RuntimeError("boom"))


@patch("sentinel.WebexNotifier")
@patch("sentinel.RiskEvaluator")
def test_run_prints_metrics(
    mock_evaluator_cls,
    mock_notifier_cls,
    capsys,
    settings,
    tracker_json_file,
):
    high_risk = AccountRisk(
        account_id="acc-high",
        account_name="High Risk Co",
        tier=RiskTier.HIGH,
        triggered_rules=["P1/P2 open > 48h"],
        summary="High risk summary",
        recommended_action="Escalate",
    )
    low_risk = AccountRisk(
        account_id="acc-low",
        account_name="Stable Co",
        tier=RiskTier.LOW,
    )
    mock_evaluator_cls.return_value.evaluate.return_value = [high_risk, low_risk]
    mock_notifier_cls.return_value.send_high_risk_card.return_value = True

    report = RiskEscalationSentinel(settings=settings).run(run_date="2026-05-29")
    captured = capsys.readouterr()

    assert isinstance(report, SentinelReport)
    assert report.accounts_evaluated == 2
    assert len(report.high_risk) == 1
    assert "[METRICS]" in captured.out
    mock_notifier_cls.return_value.send_high_risk_card.assert_called_once()


def test_run_metrics_on_validation_failure(capsys, tmp_path):
    from config import Settings

    settings = Settings(
        data_dir=str(tmp_path / "missing"),
        webex_bot_token="token",
        dry_run=True,
    )
    report = RiskEscalationSentinel(settings=settings).run(run_date="2026-05-29")
    captured = capsys.readouterr()

    assert report.errors
    assert "[METRICS]" in captured.out
