"""Tests for MetricsCalculator."""

from models import AccountPeriodData, DeliveryTrackerSnapshot, HelixData


def test_compute_case_velocity_sources(sample_account_data):
    from metrics_calculator import MetricsCalculator

    result = MetricsCalculator().compute_case_velocity(sample_account_data)
    assert result["sources"] == []


def test_compute_case_velocity_from_tracker():
    from metrics_calculator import MetricsCalculator

    data = AccountPeriodData(
        account="Acme",
        quarter="Q2-2026",
        helix=HelixData(account="Acme"),
        delivery_tracker=DeliveryTrackerSnapshot(account_name="Acme", total_open=5),
    )
    result = MetricsCalculator().compute_case_velocity(data)
    assert result["open_cases"] == 5
    assert "delivery_tracker.total_open" in result["sources"]


def test_compute_sla_compliance_sources(sample_account_data):
    from metrics_calculator import MetricsCalculator

    result = MetricsCalculator().compute_sla_compliance(sample_account_data)
    assert result["compliance_pct"] == 97
    assert "helix.sla.actual_pct" in result["sources"]


def test_compute_milestone_ontime_sources(sample_account_data):
    from metrics_calculator import MetricsCalculator

    result = MetricsCalculator().compute_milestone_ontime(sample_account_data)
    assert result["on_time_pct"] == 50.0
    assert "helix.milestones" in result["sources"]


def test_compute_utilization_sources(sample_account_data):
    from metrics_calculator import MetricsCalculator

    result = MetricsCalculator().compute_utilization(sample_account_data)
    assert result["utilization_pct"] == 65.0
    assert "helix.entitlements.utilized_pct" in result["sources"]
