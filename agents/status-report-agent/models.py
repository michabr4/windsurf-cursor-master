"""Data models for Status Report Agent."""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class Priority(str, Enum):
    """Priority levels for cases and incidents."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CaseStatus(str, Enum):
    """Case status values."""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IncidentStatus(str, Enum):
    """Incident status values."""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    RESOLVED = "resolved"
    CLOSED = "closed"


class SLAStatus(str, Enum):
    """SLA compliance status."""
    MET = "met"
    AT_RISK = "at_risk"
    BREACHED = "breached"


# ═══════════════════════════════════════════════════════════════════════════
# Salesforce Models
# ═══════════════════════════════════════════════════════════════════════════

class SalesforceCase(BaseModel):
    """Salesforce case record."""
    id: str
    case_number: str
    subject: str
    description: Optional[str] = None
    status: str
    priority: str
    account_id: Optional[str] = None
    account_name: Optional[str] = None
    contact_name: Optional[str] = None
    owner_name: Optional[str] = None
    created_date: datetime
    closed_date: Optional[datetime] = None
    last_modified_date: datetime
    case_type: Optional[str] = None
    origin: Optional[str] = None
    reason: Optional[str] = None
    is_escalated: bool = False
    
    @property
    def age_days(self) -> int:
        """Calculate case age in days."""
        end = self.closed_date or datetime.utcnow()
        return (end - self.created_date).days


class SalesforceOpportunity(BaseModel):
    """Salesforce opportunity record."""
    id: str
    name: str
    account_id: Optional[str] = None
    account_name: Optional[str] = None
    stage: str
    amount: Optional[float] = None
    close_date: Optional[date] = None
    probability: Optional[int] = None
    owner_name: Optional[str] = None
    created_date: datetime
    last_modified_date: datetime
    fiscal_quarter: Optional[str] = None
    fiscal_year: Optional[int] = None


class SalesforceAccount(BaseModel):
    """Salesforce account record."""
    id: str
    name: str
    account_number: Optional[str] = None
    industry: Optional[str] = None
    type: Optional[str] = None
    owner_name: Optional[str] = None
    health_score: Optional[float] = None
    annual_revenue: Optional[float] = None
    renewal_date: Optional[date] = None


# ═══════════════════════════════════════════════════════════════════════════
# ServiceNow Models
# ═══════════════════════════════════════════════════════════════════════════

class ServiceNowIncident(BaseModel):
    """ServiceNow incident record."""
    sys_id: str
    number: str
    short_description: str
    description: Optional[str] = None
    state: str
    priority: str
    urgency: str
    impact: str
    category: Optional[str] = None
    subcategory: Optional[str] = None
    assignment_group: Optional[str] = None
    assigned_to: Optional[str] = None
    caller_id: Optional[str] = None
    opened_at: datetime
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    sla_due: Optional[datetime] = None
    business_service: Optional[str] = None
    cmdb_ci: Optional[str] = None
    
    @property
    def age_hours(self) -> float:
        """Calculate incident age in hours."""
        end = self.resolved_at or datetime.utcnow()
        return (end - self.opened_at).total_seconds() / 3600
    
    @property
    def sla_status(self) -> SLAStatus:
        """Determine SLA status."""
        if not self.sla_due:
            return SLAStatus.MET
        now = datetime.utcnow()
        if self.resolved_at and self.resolved_at <= self.sla_due:
            return SLAStatus.MET
        if now > self.sla_due:
            return SLAStatus.BREACHED
        # At risk if within 20% of SLA window remaining
        total_window = (self.sla_due - self.opened_at).total_seconds()
        remaining = (self.sla_due - now).total_seconds()
        if remaining / total_window < 0.2:
            return SLAStatus.AT_RISK
        return SLAStatus.MET


class ServiceNowChange(BaseModel):
    """ServiceNow change request record."""
    sys_id: str
    number: str
    short_description: str
    description: Optional[str] = None
    state: str
    type: str  # normal, standard, emergency
    priority: str
    risk: str
    impact: str
    assignment_group: Optional[str] = None
    assigned_to: Optional[str] = None
    requested_by: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    opened_at: datetime
    closed_at: Optional[datetime] = None
    cmdb_ci: Optional[str] = None


class ServiceNowTask(BaseModel):
    """ServiceNow task/project task record."""
    sys_id: str
    number: str
    short_description: str
    state: str
    priority: str
    assignment_group: Optional[str] = None
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    opened_at: datetime
    closed_at: Optional[datetime] = None
    percent_complete: int = 0
    parent: Optional[str] = None  # Parent project/task


# ═══════════════════════════════════════════════════════════════════════════
# Aggregated Metrics Models
# ═══════════════════════════════════════════════════════════════════════════

class CaseMetrics(BaseModel):
    """Aggregated case metrics for reporting."""
    total_cases: int = 0
    open_cases: int = 0
    closed_cases: int = 0
    new_cases_this_period: int = 0
    resolved_this_period: int = 0
    
    by_priority: Dict[str, int] = Field(default_factory=dict)
    by_status: Dict[str, int] = Field(default_factory=dict)
    by_account: Dict[str, int] = Field(default_factory=dict)
    
    avg_age_days: float = 0.0
    oldest_case_days: int = 0
    escalated_count: int = 0
    
    trend_vs_last_period: Optional[float] = None  # % change


class IncidentMetrics(BaseModel):
    """Aggregated incident metrics for reporting."""
    total_incidents: int = 0
    open_incidents: int = 0
    resolved_incidents: int = 0
    new_this_period: int = 0
    resolved_this_period: int = 0
    
    by_priority: Dict[str, int] = Field(default_factory=dict)
    by_state: Dict[str, int] = Field(default_factory=dict)
    by_category: Dict[str, int] = Field(default_factory=dict)
    
    p1_count: int = 0
    p2_count: int = 0
    
    avg_resolution_hours: float = 0.0
    mttr_hours: float = 0.0  # Mean Time To Resolve
    
    sla_met_count: int = 0
    sla_breached_count: int = 0
    sla_at_risk_count: int = 0
    sla_compliance_pct: float = 0.0
    
    trend_vs_last_period: Optional[float] = None


class ChangeMetrics(BaseModel):
    """Aggregated change metrics for reporting."""
    total_changes: int = 0
    completed_changes: int = 0
    pending_changes: int = 0
    scheduled_this_period: int = 0
    
    by_type: Dict[str, int] = Field(default_factory=dict)
    by_risk: Dict[str, int] = Field(default_factory=dict)
    
    emergency_count: int = 0
    failed_count: int = 0
    success_rate: float = 0.0


class ProjectMetrics(BaseModel):
    """Aggregated project/task metrics for reporting."""
    total_tasks: int = 0
    completed_tasks: int = 0
    in_progress_tasks: int = 0
    overdue_tasks: int = 0
    
    by_priority: Dict[str, int] = Field(default_factory=dict)
    
    avg_completion_pct: float = 0.0
    on_track_count: int = 0
    at_risk_count: int = 0


# ═══════════════════════════════════════════════════════════════════════════
# Report Models
# ═══════════════════════════════════════════════════════════════════════════

class ReportSection(BaseModel):
    """A section of the status report."""
    title: str
    content: str
    metrics: Optional[Dict[str, Any]] = None
    highlights: List[str] = Field(default_factory=list)
    concerns: List[str] = Field(default_factory=list)
    actions: List[str] = Field(default_factory=list)


class StatusReport(BaseModel):
    """Complete status report."""
    report_id: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    period_start: datetime
    period_end: datetime
    role: str  # SDM, PM, PgM
    account_name: Optional[str] = None
    
    # Raw metrics
    case_metrics: Optional[CaseMetrics] = None
    incident_metrics: Optional[IncidentMetrics] = None
    change_metrics: Optional[ChangeMetrics] = None
    project_metrics: Optional[ProjectMetrics] = None
    
    # Generated content
    executive_summary: str = ""
    sections: List[ReportSection] = Field(default_factory=list)
    
    # Key items
    highlights: List[str] = Field(default_factory=list)
    concerns: List[str] = Field(default_factory=list)
    action_items: List[str] = Field(default_factory=list)
    
    # Metadata
    data_sources: List[str] = Field(default_factory=list)
    generation_time_seconds: float = 0.0
    
    @property
    def period_label(self) -> str:
        """Human-readable period label."""
        return f"{self.period_start.strftime('%b %d')} - {self.period_end.strftime('%b %d, %Y')}"


class ReportDeliveryResult(BaseModel):
    """Result of report delivery attempt."""
    channel: str  # email, webex, file
    success: bool
    destination: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    error: Optional[str] = None
