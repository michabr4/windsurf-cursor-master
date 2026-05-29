"""Shared fixtures for Business Review Generator tests."""

import sys
from pathlib import Path

import pytest

_AGENT_ROOT = Path(__file__).resolve().parents[1]
if str(_AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(_AGENT_ROOT))

from config import Settings
from models import (
    AccountPeriodData,
    ComputedMetrics,
    HelixData,
    HelixEntitlementRecord,
    HelixMilestoneRecord,
    HelixSLARecord,
    QBRDraft,
    QBRSection,
    SalesforceData,
)


@pytest.fixture()
def mock_settings(tmp_path) -> Settings:
    data_dir = tmp_path / "data" / "runs"
    (data_dir / "delivery-tracker").mkdir(parents=True)
    (data_dir / "business-review").mkdir(parents=True)
    return Settings(
        helix_base_url="https://helix.test/api/v1",
        helix_api_token="test-token",
        data_dir=str(data_dir),
        dry_run=True,
    )


@pytest.fixture()
def sample_account_data() -> AccountPeriodData:
    return AccountPeriodData(
        account="Acme Corp",
        quarter="Q2-2026",
        helix=HelixData(
            account="Acme Corp",
            milestones=[
                HelixMilestoneRecord(name="Phase 1", completion_pct=80, on_time=True),
                HelixMilestoneRecord(name="Phase 2", completion_pct=40, on_time=False),
            ],
            entitlements=[HelixEntitlementRecord(name="Support", utilized_pct=65)],
            sla=HelixSLARecord(target_pct=95, actual_pct=97),
        ),
        salesforce=SalesforceData(account="Acme Corp", quarter="Q2-2026", source="stub"),
    )


@pytest.fixture()
def sample_metrics(sample_account_data) -> ComputedMetrics:
    from metrics_calculator import MetricsCalculator

    return MetricsCalculator().compute(sample_account_data)


@pytest.fixture()
def sample_qbr_draft() -> QBRDraft:
    body = QBRSection(title="Executive Summary", body="Summary text", sources=["helix.sla"])
    return QBRDraft(
        account="Acme Corp",
        quarter="Q2-2026",
        executive_summary=body,
        delivery_performance=QBRSection(title="Delivery Performance", body="Delivery text"),
        risk_and_issues=QBRSection(title="Risk & Issues", body="Risk text"),
        next_quarter_priorities=QBRSection(title="Next Quarter Priorities", body="Priorities"),
        data_sources=["helix.sla"],
        output_path="/tmp/draft.md",
    )
