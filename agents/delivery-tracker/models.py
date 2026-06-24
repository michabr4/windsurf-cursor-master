"""Data models for Delivery Tracker agent."""

from datetime import datetime, date, timezone
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field


class CaseStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING_CUSTOMER = "pending_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Priority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SLAStatus(str, Enum):
    MET = "met"
    AT_RISK = "at_risk"
    BREACHED = "breached"


class MilestoneStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    OVERDUE = "overdue"


# ─── Raw Helix entities ────────────────────────────────────────────────────────

class HelixAccount(BaseModel):
    id: str
    name: str
    account_manager: Optional[str] = None
    segment: Optional[str] = None
    contract_end_date: Optional[date] = None


class HelixCase(BaseModel):
    id: str
    case_number: str
    title: str
    status: str
    priority: str
    account_id: str
    account_name: Optional[str] = None
    owner: Optional[str] = None
    created_date: datetime
    updated_date: datetime
    due_date: Optional[datetime] = None
    resolved_date: Optional[datetime] = None
    sla_status: Optional[str] = None
    is_escalated: bool = False

    @property
    def age_days(self) -> int:
        end = self.resolved_date or datetime.now(timezone.utc).replace(tzinfo=None)
        return (end - self.created_date).days

    @property
    def is_overdue(self) -> bool:
        if not self.due_date:
            return False
        return datetime.now(timezone.utc).replace(tzinfo=None) > self.due_date and self.status not in (
            CaseStatus.RESOLVED, CaseStatus.CLOSED
        )


class HelixMilestone(BaseModel):
    id: str
    name: str
    account_id: str
    status: str
    due_date: Optional[date] = None
    completion_pct: float = Field(default=0.0, ge=0.0, le=100.0)
    owner: Optional[str] = None


class HelixSLARecord(BaseModel):
    account_id: str
    period_start: date
    period_end: date
    target_pct: float
    actual_pct: float
    cases_total: int
    cases_met: int
    cases_breached: int

    @property
    def status(self) -> SLAStatus:
        if self.actual_pct >= self.target_pct:
            return SLAStatus.MET
        if self.actual_pct >= self.target_pct - 5:
            return SLAStatus.AT_RISK
        return SLAStatus.BREACHED


# ─── Aggregated summaries ──────────────────────────────────────────────────────

class AccountCaseMetrics(BaseModel):
    account_id: str
    account_name: str
    total_open: int = 0
    critical_high: int = 0
    overdue: int = 0
    escalated: int = 0
    avg_age_days: float = 0.0
    sla_status: Optional[SLAStatus] = None
    sla_actual_pct: Optional[float] = None
    sla_target_pct: Optional[float] = None
    milestone_completion_pct: Optional[float] = None
    milestones_overdue: int = 0
    health_score: Optional[float] = None

    @property
    def health_tier(self) -> str:
        if self.health_score is None:
            return "—"
        if self.health_score >= 80:
            return "🟢"
        if self.health_score >= 60:
            return "🟡"
        if self.health_score >= 40:
            return "🟠"
        return "🔴"


class WeeklySummary(BaseModel):
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    period_label: str
    lookback_days: int
    accounts: List[AccountCaseMetrics] = Field(default_factory=list)
    total_open_cases: int = 0
    total_overdue: int = 0
    total_escalated: int = 0
    accounts_at_risk_sla: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0
