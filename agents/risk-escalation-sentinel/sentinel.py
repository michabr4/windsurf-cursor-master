"""Risk & Escalation Sentinel orchestrator."""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from config import Settings, get_settings
from models import AccountRisk, DeliveryTrackerRun, RiskTier, SentinelReport
from risk_rules import RiskEvaluator
from webex_notifier import WebexNotifier

logger = logging.getLogger(__name__)


class RiskEscalationSentinel:
    """Agent #2 — reads Delivery Tracker output and flags account risks."""

    trust_tier: str = "T2"

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self._evaluator = RiskEvaluator()
        self._notifier = WebexNotifier(self.settings)

    def validate_inputs(self) -> None:
        if not self.settings.validate_inputs():
            missing = []
            if not Path(self.settings.data_dir).is_dir():
                missing.append(f"DATA_DIR not found: {self.settings.data_dir}")
            if not self.settings.dry_run and not self.settings.webex_bot_token.strip():
                missing.append("WEBEX_BOT_TOKEN is required")
            raise ValueError("; ".join(missing) or "Invalid configuration")
        logger.info("validate_inputs passed: data_dir=%s", self.settings.data_dir)

    def handle_error(self, exc: Exception) -> None:
        logger.error(
            "RiskEscalationSentinel run failed: %s: %s",
            type(exc).__name__,
            exc,
        )
        raise exc

    def run(self, run_date: Optional[str] = None) -> SentinelReport:
        start = time.monotonic()
        errors = 0
        records = 0
        cards_sent = 0
        run_date = run_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")

        report = SentinelReport(run_date=run_date)

        try:
            self.validate_inputs()
            source_path = self._resolve_source_file(run_date)
            report.source_file = str(source_path)

            payload = json.loads(source_path.read_text(encoding="utf-8"))
            tracker_run = DeliveryTrackerRun.model_validate(payload)
            risks = self._evaluator.evaluate(tracker_run.accounts)
            records = len(risks)

            high, medium, low = self._partition_risks(risks)
            report.high_risk = high
            report.medium_risk = medium
            report.low_risk_count = low
            report.accounts_evaluated = records

            for risk in high:
                try:
                    if self._notifier.send_high_risk_card(risk):
                        cards_sent += 1
                except Exception as exc:
                    errors += 1
                    report.errors.append(
                        f"Webex notification failed for {risk.account_name}: {exc}"
                    )

            try:
                if self._notifier.send_medium_risk_summary(medium):
                    cards_sent += 1
            except Exception as exc:
                errors += 1
                report.errors.append(f"Webex medium-risk summary failed: {exc}")

            report.webex_cards_sent = cards_sent
            self._write_report(report, run_date)

            duration = time.monotonic() - start
            print(
                f"[METRICS] Records processed: {records}, "
                f"errors: {errors}, "
                f"high_risk: {len(high)}, "
                f"medium_risk: {len(medium)}, "
                f"webex_cards: {cards_sent}, "
                f"duration: {duration:.1f}s"
            )
            return report

        except ValueError as exc:
            report.errors.append(str(exc))
            errors += 1
            duration = time.monotonic() - start
            print(
                f"[METRICS] Records processed: {records}, "
                f"errors: {errors}, "
                f"duration: {duration:.1f}s"
            )
            return report

    def _resolve_source_file(self, run_date: str) -> Path:
        direct = self.settings.delivery_tracker_dir / f"{run_date}.json"
        if direct.is_file():
            return direct

        candidates = sorted(
            self.settings.delivery_tracker_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if candidates:
            return candidates[0]

        raise ValueError(
            f"No Delivery Tracker JSON found for {run_date} in "
            f"{self.settings.delivery_tracker_dir}"
        )

    def _partition_risks(
        self, risks: List[AccountRisk]
    ) -> tuple[List[AccountRisk], List[AccountRisk], int]:
        high = [r for r in risks if r.tier == RiskTier.HIGH]
        medium = [r for r in risks if r.tier == RiskTier.MEDIUM]
        low = sum(1 for r in risks if r.tier == RiskTier.LOW)
        return high, medium, low

    def _write_report(self, report: SentinelReport, run_date: str) -> Path:
        out_dir = self.settings.risk_sentinel_dir
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"{run_date}.json"
        path.write_text(
            report.model_dump_json(indent=2),
            encoding="utf-8",
        )
        logger.info("Sentinel report written to %s", path)
        return path
