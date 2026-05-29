"""Delivery Tracker agent orchestrator.

Pulls data from Helix for each account the SDM owns, computes
per-account metrics, and produces a WeeklySummary for the formatter.

Trust tier: T1 (read-only, no human approval gate required).
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import List, Optional

from config import Settings, get_settings
from helix_client import HelixAPIError, HelixClient
from models import (
    AccountCaseMetrics,
    HelixCase,
    HelixMilestone,
    MilestoneStatus,
    Priority,
    SLAStatus,
    WeeklySummary,
)

logger = logging.getLogger(__name__)


class DeliveryTracker:
    """
    Agent #1 — Delivery Tracker

    Orchestrates per-account data collection from Helix and aggregates
    metrics into a WeeklySummary for SDM review.

    Before: ~45 min manual Helix review per week
    After:  ~5 min SDM review of auto-generated summary
    """

    trust_tier: str = "T1"

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self._client = HelixClient(self.settings)

    def validate_inputs(self) -> None:
        """Raise ValueError if required Helix configuration is missing."""
        if not self.settings.validate_helix():
            raise ValueError(
                "HELIX_BASE_URL and HELIX_API_TOKEN are required. "
                "Set them in your .env file."
            )
        logger.info(
            "validate_inputs passed: url=%s",
            self.settings.helix_base_url,
        )

    def handle_error(self, exc: Exception) -> None:
        """Log the exception before re-raising."""
        logger.error("DeliveryTracker run failed: %s: %s", type(exc).__name__, exc)
        raise exc

    def run(self) -> WeeklySummary:
        """Execute the full collection and aggregation pipeline."""
        start = time.monotonic()
        errors = 0
        records = 0

        lookback = self.settings.lookback_days
        today = datetime.now(timezone.utc)
        period_label = (
            f"Week of {(today).strftime('%Y-%m-%d')} "
            f"(last {lookback} days)"
        )

        summary = WeeklySummary(
            period_label=period_label,
            lookback_days=lookback,
        )

        try:
            self.validate_inputs()

            try:
                accounts = self._client.get_accounts(
                    name_filter=self.settings.account_filter or None
                )
            except HelixAPIError as exc:
                summary.errors.append(f"Failed to fetch accounts: {exc}")
                errors += 1
                duration = time.monotonic() - start
                print(
                    f"[METRICS] Records processed: {records}, "
                    f"errors: {errors}, "
                    f"duration: {duration:.1f}s"
                )
                return summary

            if not accounts:
                summary.errors.append("No accounts returned — check ACCOUNT_FILTER or token scope.")
                duration = time.monotonic() - start
                print(
                    f"[METRICS] Records processed: {records}, "
                    f"errors: {errors}, "
                    f"duration: {duration:.1f}s"
                )
                return summary

            account_metrics: List[AccountCaseMetrics] = []

            for account in accounts:
                logger.info("Processing account: %s (%s)", account.name, account.id)
                metrics = self._collect_account(account.id, account.name, lookback)
                account_metrics.append(metrics)

            summary.accounts = account_metrics
            summary.total_open_cases = sum(m.total_open for m in account_metrics)
            summary.total_overdue = sum(m.overdue for m in account_metrics)
            summary.total_escalated = sum(m.escalated for m in account_metrics)
            summary.accounts_at_risk_sla = [
                m.account_name
                for m in account_metrics
                if m.sla_status in (SLAStatus.AT_RISK, SLAStatus.BREACHED)
            ]

            records = len(account_metrics)
            duration = time.monotonic() - start
            print(
                f"[METRICS] Records processed: {records}, "
                f"errors: {errors}, "
                f"accounts_at_risk: {len(summary.accounts_at_risk_sla)}, "
                f"duration: {duration:.1f}s"
            )
            return summary

        except ValueError as exc:
            summary.errors.append(str(exc))
            errors += 1
            duration = time.monotonic() - start
            print(
                f"[METRICS] Records processed: {records}, "
                f"errors: {errors}, "
                f"duration: {duration:.1f}s"
            )
            return summary

    def _collect_account(
        self, account_id: str, account_name: str, lookback_days: int
    ) -> AccountCaseMetrics:
        metrics = AccountCaseMetrics(
            account_id=account_id, account_name=account_name
        )

        # ── Open cases ──────────────────────────────────────────────────────
        try:
            open_cases: List[HelixCase] = self._client.get_open_cases(
                account_id, lookback_days=lookback_days
            )
            metrics.total_open = len(open_cases)
            metrics.critical_high = sum(
                1
                for c in open_cases
                if c.priority.lower() in (Priority.CRITICAL, Priority.HIGH)
            )
            metrics.escalated = sum(1 for c in open_cases if c.is_escalated)
            overdue_cases = [c for c in open_cases if c.is_overdue]
            metrics.overdue = len(overdue_cases)

            ages = [c.age_days for c in open_cases]
            metrics.avg_age_days = round(sum(ages) / len(ages), 1) if ages else 0.0

        except HelixAPIError as exc:
            logger.warning("Cases unavailable for %s: %s", account_name, exc)

        # ── Milestones ──────────────────────────────────────────────────────
        try:
            milestones: List[HelixMilestone] = self._client.get_milestones(account_id)
            if milestones:
                total_pct = sum(m.completion_pct for m in milestones)
                metrics.milestone_completion_pct = round(
                    total_pct / len(milestones), 1
                )
                metrics.milestones_overdue = sum(
                    1 for m in milestones if m.status == MilestoneStatus.OVERDUE
                )
        except HelixAPIError as exc:
            logger.warning("Milestones unavailable for %s: %s", account_name, exc)

        # ── SLA metrics ─────────────────────────────────────────────────────
        try:
            sla = self._client.get_sla_metrics(account_id, lookback_days=lookback_days)
            if sla:
                metrics.sla_status = sla.status
                metrics.sla_actual_pct = sla.actual_pct
                metrics.sla_target_pct = sla.target_pct
        except HelixAPIError as exc:
            logger.warning("SLA data unavailable for %s: %s", account_name, exc)

        return metrics
