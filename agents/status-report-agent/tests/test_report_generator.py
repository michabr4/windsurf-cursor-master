"""Tests for report generation."""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import json

from config import Settings
from report_generator import ReportGenerator
from models import (
    StatusReport, CaseMetrics, IncidentMetrics,
    ChangeMetrics, ProjectMetrics, ReportSection
)


@pytest.fixture
def mock_settings():
    """Create mock settings with temp output dir."""
    with tempfile.TemporaryDirectory() as tmpdir:
        settings = Settings(
            output_dir=tmpdir,
            output_format="markdown"
        )
        yield settings


@pytest.fixture
def sample_report():
    """Create a sample report for testing."""
    now = datetime.utcnow()
    
    return StatusReport(
        report_id="test-report-123",
        generated_at=now,
        period_start=now - timedelta(days=7),
        period_end=now,
        role="SDM",
        account_name="Acme Corp",
        case_metrics=CaseMetrics(
            total_cases=50,
            open_cases=20,
            closed_cases=30,
            new_cases_this_period=10,
            resolved_this_period=15,
            by_priority={"High": 10, "Medium": 25, "Low": 15},
            avg_age_days=5.5,
            escalated_count=3
        ),
        incident_metrics=IncidentMetrics(
            total_incidents=30,
            open_incidents=10,
            resolved_incidents=20,
            new_this_period=8,
            resolved_this_period=12,
            p1_count=1,
            p2_count=5,
            mttr_hours=4.5,
            sla_compliance_pct=92.5,
            sla_met_count=25,
            sla_breached_count=2,
            by_priority={"1": 1, "2": 5, "3": 15, "4": 9}
        ),
        change_metrics=ChangeMetrics(
            total_changes=15,
            completed_changes=12,
            pending_changes=3,
            emergency_count=1,
            success_rate=95.0,
            by_type={"normal": 10, "standard": 4, "emergency": 1}
        ),
        project_metrics=ProjectMetrics(
            total_tasks=25,
            completed_tasks=18,
            in_progress_tasks=5,
            overdue_tasks=2,
            avg_completion_pct=72.0,
            on_track_count=20,
            at_risk_count=5
        ),
        executive_summary="This week showed strong operational performance with SLA compliance at 92.5%. We resolved 15 cases and 12 incidents. One P1 incident was handled within SLA. Two tasks are overdue and require attention.",
        highlights=[
            "SLA compliance at 92.5%, exceeding 90% target",
            "Resolved 15 cases, reducing backlog by 12%",
            "Zero P1 incidents caused by changes"
        ],
        concerns=[
            "2 tasks overdue by more than 5 days",
            "3 escalated cases require executive attention"
        ],
        action_items=[
            "Review overdue tasks with project team",
            "Schedule escalation review meeting",
            "Update capacity plan for next sprint"
        ],
        sections=[
            ReportSection(
                title="Case Management",
                content="Case volume remained stable this week with 10 new cases opened.",
                highlights=["15 cases resolved"],
                concerns=["3 escalations"],
                actions=["Review escalation process"]
            )
        ],
        data_sources=["Salesforce", "ServiceNow"],
        generation_time_seconds=2.5
    )


class TestReportGenerator:
    """Tests for ReportGenerator."""
    
    def test_generator_initialization(self, mock_settings):
        """Test generator initializes correctly."""
        generator = ReportGenerator(mock_settings)
        
        assert generator.output_dir.exists()
    
    def test_to_markdown(self, mock_settings, sample_report):
        """Test Markdown generation."""
        generator = ReportGenerator(mock_settings)
        
        markdown = generator.to_markdown(sample_report)
        
        # Check header
        assert "# Weekly Status Report — SDM" in markdown
        assert "Acme Corp" in markdown
        
        # Check executive summary
        assert "## Executive Summary" in markdown
        assert "92.5%" in markdown
        
        # Check highlights
        assert "✅ Key Highlights" in markdown
        assert "SLA compliance at 92.5%" in markdown
        
        # Check concerns
        assert "⚠️ Concerns" in markdown
        assert "overdue" in markdown.lower()
        
        # Check action items
        assert "📋 Action Items" in markdown
        assert "[ ]" in markdown  # Checkbox format
        
        # Check metrics tables
        assert "| Metric | Value |" in markdown
        assert "| Total Cases | 50 |" in markdown
        assert "| P1 Count | 1 |" in markdown
        
        # Check footer
        assert "2.5s" in markdown
        assert "Salesforce" in markdown
    
    def test_to_html(self, mock_settings, sample_report):
        """Test HTML generation."""
        generator = ReportGenerator(mock_settings)
        
        html = generator.to_html(sample_report)
        
        # Check HTML structure
        assert "<!DOCTYPE html>" in html
        assert "<html>" in html
        assert "</html>" in html
        
        # Check title
        assert "<title>" in html
        assert "SDM" in html
        
        # Check styling
        assert "<style>" in html
        assert "font-family" in html
        
        # Check content
        assert "Executive Summary" in html
        assert "92.5%" in html
    
    def test_to_json(self, mock_settings, sample_report):
        """Test JSON generation."""
        generator = ReportGenerator(mock_settings)
        
        json_str = generator.to_json(sample_report)
        
        # Parse and validate
        data = json.loads(json_str)
        
        assert data["report_id"] == "test-report-123"
        assert data["role"] == "SDM"
        assert data["account_name"] == "Acme Corp"
        assert data["case_metrics"]["total_cases"] == 50
        assert data["incident_metrics"]["p1_count"] == 1
        assert len(data["highlights"]) == 3
        assert len(data["action_items"]) == 3
    
    def test_save_markdown(self, mock_settings, sample_report):
        """Test saving report as Markdown."""
        generator = ReportGenerator(mock_settings)
        
        filepath = generator.save(sample_report, "markdown")
        
        assert Path(filepath).exists()
        assert filepath.endswith(".md")
        
        content = Path(filepath).read_text()
        assert "Weekly Status Report" in content
    
    def test_save_html(self, mock_settings, sample_report):
        """Test saving report as HTML."""
        generator = ReportGenerator(mock_settings)
        
        filepath = generator.save(sample_report, "html")
        
        assert Path(filepath).exists()
        assert filepath.endswith(".html")
        
        content = Path(filepath).read_text()
        assert "<!DOCTYPE html>" in content
    
    def test_save_json(self, mock_settings, sample_report):
        """Test saving report as JSON."""
        generator = ReportGenerator(mock_settings)
        
        filepath = generator.save(sample_report, "json")
        
        assert Path(filepath).exists()
        assert filepath.endswith(".json")
        
        content = Path(filepath).read_text()
        data = json.loads(content)
        assert data["report_id"] == "test-report-123"
    
    def test_save_all_formats(self, mock_settings, sample_report):
        """Test saving report in all formats."""
        generator = ReportGenerator(mock_settings)
        
        paths = generator.save_all_formats(sample_report)
        
        assert "markdown" in paths
        assert "html" in paths
        assert "json" in paths
        
        for fmt, path in paths.items():
            assert Path(path).exists()
    
    def test_filename_includes_account(self, mock_settings, sample_report):
        """Test that filename includes account name when present."""
        generator = ReportGenerator(mock_settings)
        
        filepath = generator.save(sample_report, "markdown")
        
        assert "Acme_Corp" in filepath
    
    def test_report_without_metrics(self, mock_settings):
        """Test report generation with minimal data."""
        now = datetime.utcnow()
        
        minimal_report = StatusReport(
            report_id="minimal-123",
            period_start=now - timedelta(days=7),
            period_end=now,
            role="PM",
            executive_summary="Minimal report for testing."
        )
        
        generator = ReportGenerator(mock_settings)
        markdown = generator.to_markdown(minimal_report)
        
        assert "Weekly Status Report — PM" in markdown
        assert "Minimal report for testing." in markdown
        # Should not have metrics tables
        assert "Salesforce Cases" not in markdown
