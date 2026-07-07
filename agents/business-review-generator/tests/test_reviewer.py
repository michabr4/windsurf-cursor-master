"""Tests for BusinessReviewGenerator orchestrator."""

from unittest.mock import MagicMock, patch

import pytest

from models import (
    AccountPeriodData,
    ComputedMetrics,
    HelixData,
    QBRSection,
    QBRDraft,
    SalesforceData,
)
from reviewer import BusinessReviewGenerator


def _sections():
    s = QBRSection(title="S", body="body", sources=["helix.sla"])
    return s, s, s, s


def test_trust_tier():
    assert BusinessReviewGenerator.trust_tier == "T2"


def test_validate_inputs_passes(mock_settings):
    gen = BusinessReviewGenerator(settings=mock_settings)
    gen.validate_inputs("Acme Corp", "Q2-2026")


def test_validate_inputs_fails_empty_account(mock_settings):
    gen = BusinessReviewGenerator(settings=mock_settings)
    with pytest.raises(ValueError, match="account is required"):
        gen.validate_inputs("", "Q2-2026")


def test_validate_inputs_fails_missing_helix_token(mock_settings):
    mock_settings.helix_api_token = ""
    gen = BusinessReviewGenerator(settings=mock_settings)
    with pytest.raises(ValueError, match="HELIX_API_TOKEN"):
        gen.validate_inputs("Acme Corp", "Q2-2026")


def test_handle_error_reraises(mock_settings):
    gen = BusinessReviewGenerator(settings=mock_settings)
    with pytest.raises(RuntimeError, match="boom"):
        gen.handle_error(RuntimeError("boom"))


@patch("reviewer.LLMWriter")
@patch("reviewer.MetricsCalculator")
@patch("reviewer.DataCollector")
def test_run_happy_path_prints_metrics(
    mock_collector_cls,
    mock_calc_cls,
    mock_writer_cls,
    capsys,
    mock_settings,
):
    data = AccountPeriodData(
        account="Acme Corp",
        quarter="Q2-2026",
        helix=HelixData(account="Acme Corp"),
        salesforce=SalesforceData(account="Acme Corp", source="stub"),
    )
    metrics = ComputedMetrics()
    mock_collector_cls.return_value.collect.return_value = data
    mock_calc_cls.return_value.compute.return_value = metrics
    mock_writer_cls.return_value.generate_all.return_value = _sections()

    draft = BusinessReviewGenerator(settings=mock_settings).run("Acme Corp", "Q2-2026")
    captured = capsys.readouterr()

    assert isinstance(draft, QBRDraft)
    assert draft.output_path
    assert "[METRICS]" in captured.out


@patch("reviewer.LLMWriter")
@patch("reviewer.MetricsCalculator")
@patch("reviewer.DataCollector")
def test_run_missing_salesforce_does_not_crash(
    mock_collector_cls,
    mock_calc_cls,
    mock_writer_cls,
    capsys,
    mock_settings,
):
    data = AccountPeriodData(
        account="Acme Corp",
        quarter="Q2-2026",
        helix=HelixData(account="Acme Corp"),
        salesforce=SalesforceData(account="Acme Corp", source="stub"),
    )
    metrics = ComputedMetrics(missing_sources=["salesforce"])
    mock_collector_cls.return_value.collect.return_value = data
    mock_calc_cls.return_value.compute.return_value = metrics
    mock_writer_cls.return_value.generate_all.return_value = _sections()

    draft = BusinessReviewGenerator(settings=mock_settings).run("Acme Corp", "Q2-2026")
    captured = capsys.readouterr()

    assert draft.output_path
    assert "[METRICS]" in captured.out


def test_run_metrics_on_validation_failure(capsys, mock_settings):
    mock_settings.helix_api_token = ""
    draft = BusinessReviewGenerator(settings=mock_settings).run("Acme Corp", "Q2-2026")
    captured = capsys.readouterr()

    assert draft.errors
    assert "[METRICS]" in captured.out
