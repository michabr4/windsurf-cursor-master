"""Tests for data models."""

import pytest
from datetime import datetime, timedelta

from models import (
    SalesforceCase, ServiceNowIncident, SLAStatus,
    CaseMetrics, IncidentMetrics, StatusReport
)


class TestSalesforceCase:
    """Tests for SalesforceCase model."""
    
    def test_case_creation(self):
        """Test basic case creation."""
        case = SalesforceCase(
            id="500xx000001234",
            case_number="00001234",
            subject="Test case",
            status="Open",
            priority="High",
            created_date=datetime.utcnow() - timedelta(days=5),
            last_modified_date=datetime.utcnow()
        )
        
        assert case.case_number == "00001234"
        assert case.status == "Open"
        assert case.priority == "High"
    
    def test_case_age_calculation(self):
        """Test case age calculation."""
        created = datetime.utcnow() - timedelta(days=10)
        case = SalesforceCase(
            id="500xx000001234",
            case_number="00001234",
            subject="Test case",
            status="Open",
            priority="Medium",
            created_date=created,
            last_modified_date=datetime.utcnow()
        )
        
        assert case.age_days == 10
    
    def test_closed_case_age(self):
        """Test age calculation for closed case."""
        created = datetime.utcnow() - timedelta(days=10)
        closed = datetime.utcnow() - timedelta(days=3)
        
        case = SalesforceCase(
            id="500xx000001234",
            case_number="00001234",
            subject="Test case",
            status="Closed",
            priority="Medium",
            created_date=created,
            closed_date=closed,
            last_modified_date=datetime.utcnow()
        )
        
        assert case.age_days == 7  # 10 - 3 = 7 days


class TestServiceNowIncident:
    """Tests for ServiceNowIncident model."""
    
    def test_incident_creation(self):
        """Test basic incident creation."""
        incident = ServiceNowIncident(
            sys_id="abc123",
            number="INC0001234",
            short_description="Test incident",
            state="In Progress",
            priority="2",
            urgency="2",
            impact="2",
            opened_at=datetime.utcnow() - timedelta(hours=5)
        )
        
        assert incident.number == "INC0001234"
        assert incident.state == "In Progress"
    
    def test_incident_age_hours(self):
        """Test incident age calculation in hours."""
        opened = datetime.utcnow() - timedelta(hours=24)
        
        incident = ServiceNowIncident(
            sys_id="abc123",
            number="INC0001234",
            short_description="Test incident",
            state="In Progress",
            priority="2",
            urgency="2",
            impact="2",
            opened_at=opened
        )
        
        assert abs(incident.age_hours - 24.0) < 0.1
    
    def test_sla_status_met(self):
        """Test SLA status when met."""
        opened = datetime.utcnow() - timedelta(hours=4)
        resolved = datetime.utcnow() - timedelta(hours=1)
        sla_due = datetime.utcnow() + timedelta(hours=2)
        
        incident = ServiceNowIncident(
            sys_id="abc123",
            number="INC0001234",
            short_description="Test incident",
            state="Resolved",
            priority="2",
            urgency="2",
            impact="2",
            opened_at=opened,
            resolved_at=resolved,
            sla_due=sla_due
        )
        
        assert incident.sla_status == SLAStatus.MET
    
    def test_sla_status_breached(self):
        """Test SLA status when breached."""
        opened = datetime.utcnow() - timedelta(hours=10)
        sla_due = datetime.utcnow() - timedelta(hours=2)  # Past due
        
        incident = ServiceNowIncident(
            sys_id="abc123",
            number="INC0001234",
            short_description="Test incident",
            state="In Progress",
            priority="1",
            urgency="1",
            impact="1",
            opened_at=opened,
            sla_due=sla_due
        )
        
        assert incident.sla_status == SLAStatus.BREACHED
    
    def test_sla_status_at_risk(self):
        """Test SLA status when at risk."""
        opened = datetime.utcnow() - timedelta(hours=9)
        sla_due = datetime.utcnow() + timedelta(hours=1)  # 10% remaining
        
        incident = ServiceNowIncident(
            sys_id="abc123",
            number="INC0001234",
            short_description="Test incident",
            state="In Progress",
            priority="2",
            urgency="2",
            impact="2",
            opened_at=opened,
            sla_due=sla_due
        )
        
        assert incident.sla_status == SLAStatus.AT_RISK


class TestCaseMetrics:
    """Tests for CaseMetrics model."""
    
    def test_default_metrics(self):
        """Test default metric values."""
        metrics = CaseMetrics()
        
        assert metrics.total_cases == 0
        assert metrics.open_cases == 0
        assert metrics.avg_age_days == 0.0
        assert metrics.by_priority == {}
    
    def test_metrics_with_data(self):
        """Test metrics with populated data."""
        metrics = CaseMetrics(
            total_cases=50,
            open_cases=20,
            closed_cases=30,
            new_cases_this_period=10,
            resolved_this_period=15,
            by_priority={"High": 10, "Medium": 25, "Low": 15},
            avg_age_days=5.5,
            escalated_count=3
        )
        
        assert metrics.total_cases == 50
        assert metrics.open_cases == 20
        assert metrics.by_priority["High"] == 10


class TestIncidentMetrics:
    """Tests for IncidentMetrics model."""
    
    def test_sla_compliance_calculation(self):
        """Test SLA compliance percentage."""
        metrics = IncidentMetrics(
            total_incidents=100,
            sla_met_count=90,
            sla_breached_count=10,
            sla_at_risk_count=5
        )
        
        assert metrics.sla_compliance_pct == 0.0  # Not auto-calculated in model
    
    def test_p1_p2_counts(self):
        """Test P1/P2 incident counts."""
        metrics = IncidentMetrics(
            total_incidents=50,
            p1_count=2,
            p2_count=8,
            by_priority={"1": 2, "2": 8, "3": 20, "4": 20}
        )
        
        assert metrics.p1_count == 2
        assert metrics.p2_count == 8


class TestStatusReport:
    """Tests for StatusReport model."""
    
    def test_report_creation(self):
        """Test basic report creation."""
        now = datetime.utcnow()
        report = StatusReport(
            report_id="test-123",
            period_start=now - timedelta(days=7),
            period_end=now,
            role="SDM",
            executive_summary="Test summary",
            data_sources=["Salesforce", "ServiceNow"]
        )
        
        assert report.report_id == "test-123"
        assert report.role == "SDM"
        assert "Salesforce" in report.data_sources
    
    def test_period_label(self):
        """Test period label generation."""
        report = StatusReport(
            report_id="test-123",
            period_start=datetime(2025, 1, 1),
            period_end=datetime(2025, 1, 7),
            role="SDM"
        )
        
        assert "Jan 01" in report.period_label
        assert "Jan 07" in report.period_label
    
    def test_report_with_metrics(self):
        """Test report with all metrics."""
        now = datetime.utcnow()
        
        report = StatusReport(
            report_id="test-123",
            period_start=now - timedelta(days=7),
            period_end=now,
            role="SDM",
            case_metrics=CaseMetrics(total_cases=50, open_cases=20),
            incident_metrics=IncidentMetrics(total_incidents=30, p1_count=1),
            executive_summary="Test summary",
            highlights=["Highlight 1", "Highlight 2"],
            concerns=["Concern 1"],
            action_items=["Action 1", "Action 2"]
        )
        
        assert report.case_metrics.total_cases == 50
        assert report.incident_metrics.p1_count == 1
        assert len(report.highlights) == 2
        assert len(report.action_items) == 2
