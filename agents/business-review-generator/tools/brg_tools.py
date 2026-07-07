"""Tool wrappers for orchestration layers."""

from __future__ import annotations

from config import Settings
from data_collector import DataCollector
from llm_writer import LLMWriter
from metrics_calculator import MetricsCalculator
from models import AccountPeriodData, ComputedMetrics, QBRDraft
from reviewer import BusinessReviewGenerator


def collect_account_data(
    account: str, quarter: str, settings: Settings | None = None
) -> AccountPeriodData:
    return DataCollector(settings or Settings()).collect(account, quarter)


def compute_qbr_metrics(
    data: AccountPeriodData,
) -> ComputedMetrics:
    return MetricsCalculator().compute(data)


def generate_qbr_draft(
    account: str, quarter: str, settings: Settings | None = None
) -> QBRDraft:
    return BusinessReviewGenerator(settings=settings).run(account, quarter)


def get_draft_summary(draft: QBRDraft) -> str:
    return (
        f"QBR draft for {draft.account} ({draft.quarter}) — "
        f"{len(draft.data_sources)} sources, "
        f"output: {draft.output_path or 'not saved'}"
    )
