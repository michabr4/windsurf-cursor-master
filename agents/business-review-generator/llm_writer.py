"""LLM-powered QBR section generation with template fallback."""

from __future__ import annotations

import logging
from typing import List

from config import Settings
from models import AccountPeriodData, ComputedMetrics, QBRSection

logger = logging.getLogger(__name__)


class LLMWriter:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def generate_all(
        self,
        data: AccountPeriodData,
        metrics: ComputedMetrics,
    ) -> tuple[QBRSection, QBRSection, QBRSection, QBRSection]:
        return (
            self.executive_summary(data, metrics),
            self.delivery_performance(data, metrics),
            self.risk_and_issues(data, metrics),
            self.next_quarter_priorities(data, metrics),
        )

    def executive_summary(
        self, data: AccountPeriodData, metrics: ComputedMetrics
    ) -> QBRSection:
        return self._section(
            title="Executive Summary",
            section_key="Executive Summary",
            data=data,
            metrics=metrics,
            sources=self._all_sources(metrics),
            missing=bool(metrics.missing_sources),
        )

    def delivery_performance(
        self, data: AccountPeriodData, metrics: ComputedMetrics
    ) -> QBRSection:
        return self._section(
            title="Delivery Performance",
            section_key="Delivery performance",
            data=data,
            metrics=metrics,
            sources=metrics.sla.sources + metrics.milestone.sources,
            missing=not metrics.sla.sources and not metrics.milestone.sources,
        )

    def risk_and_issues(
        self, data: AccountPeriodData, metrics: ComputedMetrics
    ) -> QBRSection:
        overdue = data.delivery_tracker.overdue if data.delivery_tracker else 0
        body_extra = f" Overdue items flagged: {overdue}." if overdue else ""
        section = self._section(
            title="Risk & Issues",
            section_key="Risk & issues",
            data=data,
            metrics=metrics,
            sources=metrics.case.sources,
            missing=not metrics.case.sources,
        )
        if body_extra and not self._use_llm():
            section.body += body_extra
        return section

    def next_quarter_priorities(
        self, data: AccountPeriodData, metrics: ComputedMetrics
    ) -> QBRSection:
        return self._section(
            title="Next Quarter Priorities",
            section_key="Next quarter priorities",
            data=data,
            metrics=metrics,
            sources=metrics.entitlement.sources + metrics.milestone.sources,
            missing=not metrics.entitlement.sources,
        )

    def _section(
        self,
        title: str,
        section_key: str,
        data: AccountPeriodData,
        metrics: ComputedMetrics,
        sources: List[str],
        missing: bool,
    ) -> QBRSection:
        if self._use_llm():
            body = self._call_llm(title, data, metrics)
        else:
            body = self._placeholder(section_key, data.account, data.quarter)
        return QBRSection(
            title=title,
            body=body,
            sources=sources,
            has_missing_data=missing,
        )

    def _use_llm(self) -> bool:
        return bool(self.settings.llm_model) and not self.settings.dry_run

    def _placeholder(self, section_key: str, account: str, quarter: str) -> str:
        return (
            "[DRAFT — REVIEW REQUIRED]\n"
            f"{section_key}: Data collected for {account} covering {quarter}.\n"
            "[LLM generation skipped — set LLM_MODEL in .env to enable]"
        )

    def _call_llm(
        self, title: str, data: AccountPeriodData, metrics: ComputedMetrics
    ) -> str:
        try:
            import litellm

            prompt = (
                f"Write the {title} section for a QBR for {data.account} "
                f"({data.quarter}). Use only these metrics: {metrics.model_dump_json()}."
            )
            response = litellm.completion(
                model=self.settings.llm_model,
                api_base=self.settings.llm_base_url or None,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content or self._placeholder(
                title, data.account, data.quarter
            )
        except Exception as exc:
            logger.warning("LLM call failed, using placeholder: %s", exc)
            return self._placeholder(title, data.account, data.quarter)

    def _all_sources(self, metrics: ComputedMetrics) -> List[str]:
        sources: List[str] = []
        for block in (metrics.case, metrics.milestone, metrics.entitlement, metrics.sla):
            sources.extend(block.sources)
        return sources
