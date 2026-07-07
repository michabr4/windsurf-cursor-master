"""Compute QBR metrics with source citations."""

from __future__ import annotations

from models import AccountPeriodData, ComputedMetrics


class MetricsCalculator:
    def compute(self, data: AccountPeriodData) -> ComputedMetrics:
        metrics = ComputedMetrics()
        metrics.case = self._case_metrics(data)
        metrics.milestone = self._milestone_metrics(data)
        metrics.entitlement = self._entitlement_metrics(data)
        metrics.sla = self._sla_metrics(data)

        if data.salesforce.source == "stub":
            metrics.missing_sources.append("salesforce")
        if not data.helix.milestones and not data.delivery_tracker:
            metrics.missing_sources.append("helix.milestones")
        if not data.helix.entitlements:
            metrics.missing_sources.append("helix.entitlements")
        if data.helix.sla is None and not data.delivery_tracker:
            metrics.missing_sources.append("helix.sla")

        return metrics

    def compute_case_velocity(self, data: AccountPeriodData) -> dict:
        return self._case_metrics(data).model_dump()

    def compute_sla_compliance(self, data: AccountPeriodData) -> dict:
        return self._sla_metrics(data).model_dump()

    def compute_milestone_ontime(self, data: AccountPeriodData) -> dict:
        return self._milestone_metrics(data).model_dump()

    def compute_utilization(self, data: AccountPeriodData) -> dict:
        return self._entitlement_metrics(data).model_dump()

    def _case_metrics(self, data: AccountPeriodData):
        from models import CaseMetrics

        m = CaseMetrics()
        if data.salesforce.cases:
            m.open_cases = sum(1 for c in data.salesforce.cases if c.status != "closed")
            m.case_velocity = float(len(data.salesforce.cases))
            m.sources.append("salesforce.cases")
        elif data.delivery_tracker:
            m.open_cases = data.delivery_tracker.total_open
            m.case_velocity = float(data.delivery_tracker.total_open)
            m.sources.append("delivery_tracker.total_open")
        return m

    def _milestone_metrics(self, data: AccountPeriodData):
        from models import MilestoneMetrics

        m = MilestoneMetrics()
        if data.helix.milestones:
            on_time = sum(1 for ms in data.helix.milestones if ms.on_time)
            m.on_time_pct = round(100 * on_time / len(data.helix.milestones), 1)
            m.avg_completion_pct = round(
                sum(ms.completion_pct for ms in data.helix.milestones)
                / len(data.helix.milestones),
                1,
            )
            m.sources.append("helix.milestones")
        elif data.delivery_tracker and data.delivery_tracker.milestone_completion_pct is not None:
            m.avg_completion_pct = data.delivery_tracker.milestone_completion_pct
            m.sources.append("delivery_tracker.milestone_completion_pct")
        return m

    def _entitlement_metrics(self, data: AccountPeriodData):
        from models import EntitlementMetrics

        m = EntitlementMetrics()
        if data.helix.entitlements:
            m.utilization_pct = round(
                sum(e.utilized_pct for e in data.helix.entitlements)
                / len(data.helix.entitlements),
                1,
            )
            m.sources.append("helix.entitlements.utilized_pct")
        return m

    def _sla_metrics(self, data: AccountPeriodData):
        from models import SLAComplianceMetrics

        m = SLAComplianceMetrics()
        if data.helix.sla:
            m.compliance_pct = data.helix.sla.actual_pct
            m.target_pct = data.helix.sla.target_pct
            m.sources.append("helix.sla.actual_pct")
        elif data.delivery_tracker and data.delivery_tracker.sla_actual_pct is not None:
            m.compliance_pct = data.delivery_tracker.sla_actual_pct
            m.sources.append("delivery_tracker.sla_actual_pct")
        return m
