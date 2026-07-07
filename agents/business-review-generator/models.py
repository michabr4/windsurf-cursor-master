"""Data models for Business Review Generator."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SalesforceCase(BaseModel):
    id: str
    subject: str
    status: str = "open"
    priority: str = "medium"


class SalesforceData(BaseModel):
    account: str
    quarter: str = ""
    cases: List[SalesforceCase] = Field(default_factory=list)
    csat_score: Optional[float] = None
    source: str = "stub"


class HelixMilestoneRecord(BaseModel):
    name: str
    completion_pct: float = 0.0
    on_time: bool = True


class HelixEntitlementRecord(BaseModel):
    name: str
    utilized_pct: float = 0.0
    total_units: float = 0.0


class HelixSLARecord(BaseModel):
    target_pct: float = 95.0
    actual_pct: float = 0.0


class HelixData(BaseModel):
    account: str
    milestones: List[HelixMilestoneRecord] = Field(default_factory=list)
    entitlements: List[HelixEntitlementRecord] = Field(default_factory=list)
    sla: Optional[HelixSLARecord] = None
    source: str = "helix"


class DeliveryTrackerSnapshot(BaseModel):
    account_name: str = ""
    total_open: int = 0
    overdue: int = 0
    sla_actual_pct: Optional[float] = None
    milestone_completion_pct: Optional[float] = None


class AccountPeriodData(BaseModel):
    account: str
    quarter: str
    helix: HelixData = Field(default_factory=lambda: HelixData(account=""))
    salesforce: SalesforceData = Field(default_factory=lambda: SalesforceData(account=""))
    delivery_tracker: Optional[DeliveryTrackerSnapshot] = None


class CaseMetrics(BaseModel):
    case_velocity: Optional[float] = None
    open_cases: int = 0
    sources: List[str] = Field(default_factory=list)


class MilestoneMetrics(BaseModel):
    on_time_pct: Optional[float] = None
    avg_completion_pct: Optional[float] = None
    sources: List[str] = Field(default_factory=list)


class EntitlementMetrics(BaseModel):
    utilization_pct: Optional[float] = None
    sources: List[str] = Field(default_factory=list)


class SLAComplianceMetrics(BaseModel):
    compliance_pct: Optional[float] = None
    target_pct: Optional[float] = None
    sources: List[str] = Field(default_factory=list)


class ComputedMetrics(BaseModel):
    case: CaseMetrics = Field(default_factory=CaseMetrics)
    milestone: MilestoneMetrics = Field(default_factory=MilestoneMetrics)
    entitlement: EntitlementMetrics = Field(default_factory=EntitlementMetrics)
    sla: SLAComplianceMetrics = Field(default_factory=SLAComplianceMetrics)
    missing_sources: List[str] = Field(default_factory=list)


class QBRSection(BaseModel):
    title: str
    body: str
    sources: List[str] = Field(default_factory=list)
    has_missing_data: bool = False


class QBRDraft(BaseModel):
    account: str
    quarter: str
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    executive_summary: QBRSection
    delivery_performance: QBRSection
    risk_and_issues: QBRSection
    next_quarter_priorities: QBRSection
    data_sources: List[str] = Field(default_factory=list)
    output_path: str = ""
    errors: List[str] = Field(default_factory=list)

    def to_markdown(self) -> str:
        sections = [
            self.executive_summary,
            self.delivery_performance,
            self.risk_and_issues,
            self.next_quarter_priorities,
        ]
        lines = [
            f"# Business Review Draft — {self.account}",
            f"**Quarter:** {self.quarter}  ",
            f"**Generated:** {self.generated_at.isoformat()}  ",
            "",
        ]
        for section in sections:
            flag = " _(source data incomplete)_" if section.has_missing_data else ""
            lines.extend([f"## {section.title}{flag}", "", section.body, ""])
        lines.extend(["## Data Sources", ""])
        for src in self.data_sources:
            lines.append(f"- {src}")
        if self.errors:
            lines.extend(["", "## Warnings", ""])
            lines.extend(f"- {e}" for e in self.errors)
        return "\n".join(lines) + "\n"
