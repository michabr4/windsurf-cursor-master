"""Data models for Risk & Escalation Sentinel."""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class RiskTier(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class DeliveryAccountRecord(BaseModel):
    """One account row from Delivery Tracker JSON output."""

    account_id: str
    account_name: str
    total_open: int = 0
    critical_high: int = 0
    overdue: int = 0
    escalated: int = 0
    avg_age_days: float = 0.0
    sla_status: Optional[str] = None
    sla_actual_pct: Optional[float] = None
    sla_target_pct: Optional[float] = None
    milestone_completion_pct: Optional[float] = None
    milestones_overdue: int = 0
    p1_p2_open_over_48h: Optional[int] = None
    sla_breach_within_days: Optional[int] = None
    health_score: Optional[float] = None
    health_score_prior_7d: Optional[float] = None
    milestone_slip_days: Optional[int] = None
    entitlement_pct: Optional[float] = None
    renewal_days: Optional[int] = None


class DeliveryTrackerRun(BaseModel):
    """Delivery Tracker JSON file shape."""

    generated_at: Optional[datetime] = None
    period_label: str = ""
    lookback_days: int = 7
    accounts: List[DeliveryAccountRecord] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


class AccountRisk(BaseModel):
    account_id: str
    account_name: str
    tier: RiskTier = RiskTier.LOW
    triggered_rules: List[str] = Field(default_factory=list)
    summary: str = ""
    recommended_action: str = ""


class SentinelReport(BaseModel):
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    source_file: str = ""
    run_date: str = ""
    accounts_evaluated: int = 0
    high_risk: List[AccountRisk] = Field(default_factory=list)
    medium_risk: List[AccountRisk] = Field(default_factory=list)
    low_risk_count: int = 0
    webex_cards_sent: int = 0
    errors: List[str] = Field(default_factory=list)
