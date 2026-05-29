"""Business Review Generator orchestrator."""

from __future__ import annotations

import logging
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests

from config import Settings, get_settings
from data_collector import DataCollector
from llm_writer import LLMWriter
from metrics_calculator import MetricsCalculator
from models import QBRDraft

logger = logging.getLogger(__name__)

WEBEX_MESSAGES_URL = "https://webexapis.com/v1/messages"


class BusinessReviewGenerator:
    """Agent #3 — on-demand QBR/EBR draft generator (T2 HITL)."""

    trust_tier: str = "T2"

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self._collector = DataCollector(self.settings)
        self._calculator = MetricsCalculator()
        self._writer = LLMWriter(self.settings)

    def validate_inputs(self, account: str, quarter: str) -> None:
        if not account or not account.strip():
            raise ValueError("account is required")
        if not self.settings.helix_api_token.strip():
            raise ValueError(
                "HELIX_API_TOKEN is required. Set it in your .env file."
            )
        if not quarter or not quarter.strip():
            raise ValueError("quarter is required")
        logger.info(
            "validate_inputs passed: account=%s quarter=%s",
            account,
            quarter,
        )

    def handle_error(self, exc: Exception) -> None:
        logger.error(
            "BusinessReviewGenerator run failed: %s: %s",
            type(exc).__name__,
            exc,
        )
        raise exc

    def run(self, account: str, quarter: str) -> QBRDraft:
        start = time.monotonic()
        errors = 0
        records = 0

        placeholder = QBRDraft(
            account=account,
            quarter=quarter,
            executive_summary=self._empty_section("Executive Summary"),
            delivery_performance=self._empty_section("Delivery Performance"),
            risk_and_issues=self._empty_section("Risk & Issues"),
            next_quarter_priorities=self._empty_section("Next Quarter Priorities"),
        )

        try:
            self.validate_inputs(account, quarter)
            data = self._collector.collect(account, quarter)
            records = 1
            metrics = self._calculator.compute(data)

            exec_s, delivery, risks, priorities = self._writer.generate_all(
                data, metrics
            )

            data_sources = sorted(
                set(
                    exec_s.sources
                    + delivery.sources
                    + risks.sources
                    + priorities.sources
                    + [data.helix.source, data.salesforce.source]
                )
            )
            warnings = []
            if metrics.missing_sources:
                warnings.append(
                    f"Missing source data: {', '.join(metrics.missing_sources)}"
                )

            draft = QBRDraft(
                account=account,
                quarter=quarter,
                executive_summary=exec_s,
                delivery_performance=delivery,
                risk_and_issues=risks,
                next_quarter_priorities=priorities,
                data_sources=data_sources,
                errors=warnings,
            )

            output_path = self._save_draft(draft)
            draft.output_path = str(output_path)

            if (
                not self.settings.dry_run
                and self.settings.webex_bot_token.strip()
                and self.settings.webex_room_id.strip()
            ):
                try:
                    self._notify_webex(account)
                except Exception as exc:
                    errors += 1
                    draft.errors.append(f"Webex notification failed: {exc}")

            duration = time.monotonic() - start
            print(
                f"[METRICS] Records processed: {records}, "
                f"errors: {errors}, "
                f"output: {draft.output_path}, "
                f"duration: {duration:.1f}s"
            )
            return draft

        except ValueError as exc:
            placeholder.errors.append(str(exc))
            errors += 1
            duration = time.monotonic() - start
            print(
                f"[METRICS] Records processed: {records}, "
                f"errors: {errors}, "
                f"duration: {duration:.1f}s"
            )
            return placeholder

    def _empty_section(self, title: str):
        from models import QBRSection

        return QBRSection(title=title, body="")

    def _account_slug(self, account: str) -> str:
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", account.strip().lower()).strip("-")
        return slug or "account"

    def _save_draft(self, draft: QBRDraft) -> Path:
        out_dir = self.settings.business_review_dir
        out_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        path = out_dir / f"{stamp}-{self._account_slug(draft.account)}.md"
        template_path = Path(__file__).parent / "templates" / "business-review-template.md"
        if template_path.is_file():
            template = template_path.read_text(encoding="utf-8")
            content = template.format(
                account=draft.account,
                quarter=draft.quarter,
                generated_at=draft.generated_at.isoformat(),
                executive_summary=draft.executive_summary.body,
                delivery_performance=draft.delivery_performance.body,
                risk_and_issues=draft.risk_and_issues.body,
                next_quarter_priorities=draft.next_quarter_priorities.body,
                data_sources="\n".join(f"- {s}" for s in draft.data_sources),
            )
        else:
            content = draft.to_markdown()
        path.write_text(content, encoding="utf-8")
        logger.info("QBR draft saved to %s", path)
        return path

    def _notify_webex(self, account: str) -> None:
        message = f"Draft QBR for {account} ready — ~30 min review"
        resp = requests.post(
            WEBEX_MESSAGES_URL,
            headers={"Authorization": f"Bearer {self.settings.webex_bot_token}"},
            json={"roomId": self.settings.webex_room_id, "markdown": message},
            timeout=self.settings.http_timeout,
        )
        resp.raise_for_status()
        logger.info("Webex notification sent for %s", account)
