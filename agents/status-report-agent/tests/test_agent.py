"""Tests for main agent orchestrator."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from config import Settings
from agent import StatusReportAgent, create_agent
from models import (
    StatusReport, CaseMetrics, IncidentMetrics, 
    ChangeMetrics, ProjectMetrics, SalesforceCase, ServiceNowIncident
)


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    return Settings(
        sf_instance_url="https://test.salesforce.com",
        sf_username="test@test.com",
        sf_password="password",
        sf_security_token="token",
        sn_instance_url="https://test.service-now.com",
        sn_username="admin",
        sn_password="password",
        azure_openai_endpoint="https://test.openai.azure.com",
        azure_openai_key="test-key",
        azure_openai_deployment="gpt-4o",
        llm_provider="azure",
        lookback_days=7,
        role="SDM",
        output_dir="./test_output",
        output_format="markdown"
    )


class TestStatusReportAgent:
    """Tests for StatusReportAgent."""
    
    def test_agent_initialization(self, mock_settings):
        """Test agent initializes correctly."""
        agent = StatusReportAgent(mock_settings)
        
        assert agent.settings == mock_settings
        assert agent._sf_client is None  # Lazy init
        assert agent._sn_client is None
        assert agent._llm_client is None
        assert agent.cases == []
        assert agent.incidents == []
    
    def test_create_agent_factory(self, mock_settings):
        """Test factory function."""
        agent = create_agent(mock_settings)
        
        assert isinstance(agent, StatusReportAgent)
        assert agent.settings == mock_settings
    
    def test_lazy_client_initialization(self, mock_settings):
        """Test clients are lazily initialized."""
        agent = StatusReportAgent(mock_settings)
        
        # Clients should be None initially
        assert agent._sf_client is None
        assert agent._sn_client is None
        
        # Accessing property should create client
        with patch('agent.SalesforceClient') as mock_sf:
            _ = agent.sf_client
            mock_sf.assert_called_once_with(mock_settings)
    
    @patch('agent.SalesforceClient')
    def test_collect_salesforce_data(self, mock_sf_class, mock_settings):
        """Test Salesforce data collection."""
        mock_client = MagicMock()
        mock_client.get_cases.return_value = [
            MagicMock(case_number="001"),
            MagicMock(case_number="002")
        ]
        mock_sf_class.return_value = mock_client
        
        agent = StatusReportAgent(mock_settings)
        agent.collect_salesforce_data(lookback_days=7)
        
        assert len(agent.cases) == 2
        mock_client.get_cases.assert_called_once()
    
    @patch('agent.ServiceNowClient')
    def test_collect_servicenow_data(self, mock_sn_class, mock_settings):
        """Test ServiceNow data collection."""
        mock_client = MagicMock()
        mock_client.get_incidents.return_value = [MagicMock(number="INC001")]
        mock_client.get_changes.return_value = [MagicMock(number="CHG001")]
        mock_client.get_tasks.return_value = [MagicMock(number="TASK001")]
        mock_sn_class.return_value = mock_client
        
        agent = StatusReportAgent(mock_settings)
        agent.collect_servicenow_data(lookback_days=7)
        
        assert len(agent.incidents) == 1
        assert len(agent.changes) == 1
        assert len(agent.tasks) == 1
    
    @patch('agent.SalesforceClient')
    @patch('agent.ServiceNowClient')
    def test_calculate_metrics(self, mock_sn_class, mock_sf_class, mock_settings):
        """Test metrics calculation."""
        # Setup Salesforce mock
        mock_sf = MagicMock()
        mock_sf.calculate_case_metrics.return_value = MagicMock(total_cases=50)
        mock_sf_class.return_value = mock_sf
        
        # Setup ServiceNow mock
        mock_sn = MagicMock()
        mock_sn.calculate_incident_metrics.return_value = MagicMock(total_incidents=30)
        mock_sn.calculate_change_metrics.return_value = MagicMock(total_changes=10)
        mock_sn.calculate_task_metrics.return_value = MagicMock(total_tasks=20)
        mock_sn_class.return_value = mock_sn
        
        agent = StatusReportAgent(mock_settings)
        agent.cases = [MagicMock()]
        agent.incidents = [MagicMock()]
        agent.changes = [MagicMock()]
        agent.tasks = [MagicMock()]
        
        now = datetime.utcnow()
        agent.calculate_metrics(now - timedelta(days=7), now)
        
        assert agent.case_metrics is not None
        assert agent.incident_metrics is not None
        assert agent.change_metrics is not None
        assert agent.project_metrics is not None
    
    def test_generate_placeholder_summary(self, mock_settings):
        """Test placeholder summary generation when LLM unavailable."""
        agent = StatusReportAgent(mock_settings)
        
        # Set some metrics
        from models import CaseMetrics, IncidentMetrics
        agent.case_metrics = CaseMetrics(
            total_cases=50,
            open_cases=20,
            new_cases_this_period=10
        )
        agent.incident_metrics = IncidentMetrics(
            total_incidents=30,
            p1_count=1,
            p2_count=5,
            sla_compliance_pct=92.5
        )
        
        summary = agent._generate_placeholder_summary()
        
        assert "50 cases" in summary
        assert "30 total" in summary
        assert "92.5%" in summary
    
    @patch('agent.SalesforceClient')
    @patch('agent.ServiceNowClient')
    @patch('agent.LLMClient')
    @patch('agent.ReportGenerator')
    def test_run_full_pipeline(self, mock_gen_class, mock_llm_class, 
                                mock_sn_class, mock_sf_class, mock_settings):
        """Test full agent pipeline."""
        # Setup mocks
        mock_sf = MagicMock()
        mock_sf.get_cases.return_value = []
        mock_sf.calculate_case_metrics.return_value = MagicMock(total_cases=0)
        mock_sf_class.return_value = mock_sf
        
        mock_sn = MagicMock()
        mock_sn.get_incidents.return_value = []
        mock_sn.get_changes.return_value = []
        mock_sn.get_tasks.return_value = []
        mock_sn.calculate_incident_metrics.return_value = MagicMock(total_incidents=0)
        mock_sn.calculate_change_metrics.return_value = MagicMock(total_changes=0)
        mock_sn.calculate_task_metrics.return_value = MagicMock(total_tasks=0)
        mock_sn_class.return_value = mock_sn
        
        mock_llm = MagicMock()
        mock_llm.generate_executive_summary.return_value = "Test summary"
        mock_llm.generate_highlights_and_concerns.return_value = {
            "highlights": ["H1"],
            "concerns": ["C1"],
            "actions": ["A1"]
        }
        mock_llm_class.return_value = mock_llm
        
        mock_gen = MagicMock()
        mock_gen.save.return_value = "/path/to/report.md"
        mock_gen_class.return_value = mock_gen
        
        agent = StatusReportAgent(mock_settings)
        report = agent.run(lookback_days=7, role="SDM")
        
        assert isinstance(report, StatusReport)
        assert report.role == "SDM"
        assert report.executive_summary == "Test summary"
        mock_gen.save.assert_called_once()
    
    @patch('agent.SalesforceClient')
    @patch('agent.ServiceNowClient')
    @patch('agent.ReportGenerator')
    def test_run_without_llm(self, mock_gen_class, mock_sn_class, mock_sf_class, mock_settings):
        """Test agent run when LLM is not configured."""
        # Disable LLM
        mock_settings.azure_openai_endpoint = ""
        mock_settings.azure_openai_key = ""
        
        mock_sf = MagicMock()
        mock_sf.get_cases.return_value = []
        mock_sf_class.return_value = mock_sf
        
        mock_sn = MagicMock()
        mock_sn.get_incidents.return_value = []
        mock_sn.get_changes.return_value = []
        mock_sn.get_tasks.return_value = []
        mock_sn_class.return_value = mock_sn
        
        mock_gen = MagicMock()
        mock_gen.save.return_value = "/path/to/report.md"
        mock_gen_class.return_value = mock_gen
        
        agent = StatusReportAgent(mock_settings)
        report = agent.run(save_report=True)
        
        # Should still generate report with placeholder summary
        assert isinstance(report, StatusReport)
    
    @patch('agent.ReportGenerator')
    def test_run_with_account_filter(self, mock_gen_class, mock_settings):
        """Test agent run with account filter."""
        mock_settings.account_filter = "Acme Corp"
        
        mock_gen = MagicMock()
        mock_gen.save.return_value = "/path/report.md"
        mock_gen_class.return_value = mock_gen
        
        agent = StatusReportAgent(mock_settings)
        
        with patch.object(agent, 'collect_salesforce_data') as mock_sf:
            with patch.object(agent, 'collect_servicenow_data'):
                with patch.object(agent, 'calculate_metrics'):
                    with patch.object(agent, 'generate_narratives') as mock_narr:
                        mock_narr.return_value = {
                            "executive_summary": "Test",
                            "highlights": [],
                            "concerns": [],
                            "actions": []
                        }
                        agent.run()
        
        # Verify account filter was passed
        mock_sf.assert_called_once()


class TestAgentIntegration:
    """Integration tests for agent (require mocked external services)."""
    
    @patch('agent.SalesforceClient')
    @patch('agent.ServiceNowClient')
    @patch('agent.LLMClient')
    def test_end_to_end_report_generation(self, mock_llm_class, mock_sn_class, 
                                           mock_sf_class, mock_settings, tmp_path):
        """Test complete report generation flow."""
        mock_settings.output_dir = str(tmp_path)
        
        # Setup realistic mock data
        from models import SalesforceCase, ServiceNowIncident
        
        now = datetime.utcnow()
        
        mock_cases = [
            SalesforceCase(
                id="1", case_number="001", subject="Test Case",
                status="Open", priority="High",
                created_date=now - timedelta(days=3),
                last_modified_date=now
            )
        ]
        
        mock_incidents = [
            ServiceNowIncident(
                sys_id="1", number="INC001",
                short_description="Test Incident",
                state="In Progress", priority="2",
                urgency="2", impact="2",
                opened_at=now - timedelta(hours=5)
            )
        ]
        
        # Setup mocks
        mock_sf = MagicMock()
        mock_sf.get_cases.return_value = mock_cases
        mock_sf.calculate_case_metrics.return_value = CaseMetrics(
            total_cases=1, open_cases=1, new_cases_this_period=1
        )
        mock_sf_class.return_value = mock_sf
        
        mock_sn = MagicMock()
        mock_sn.get_incidents.return_value = mock_incidents
        mock_sn.get_changes.return_value = []
        mock_sn.get_tasks.return_value = []
        mock_sn.calculate_incident_metrics.return_value = IncidentMetrics(
            total_incidents=1, p1_count=0, sla_compliance_pct=100.0
        )
        mock_sn.calculate_change_metrics.return_value = ChangeMetrics(total_changes=0)
        mock_sn.calculate_task_metrics.return_value = ProjectMetrics(total_tasks=0)
        mock_sn_class.return_value = mock_sn
        
        mock_llm = MagicMock()
        mock_llm.generate_executive_summary.return_value = "All systems operational."
        mock_llm.generate_highlights_and_concerns.return_value = {
            "highlights": ["100% SLA compliance"],
            "concerns": [],
            "actions": []
        }
        mock_llm_class.return_value = mock_llm
        
        # Run agent
        agent = StatusReportAgent(mock_settings)
        report = agent.run(lookback_days=7, role="SDM", save_report=True)
        
        # Verify report
        assert report.role == "SDM"
        assert report.executive_summary == "All systems operational."
        assert "Salesforce" in report.data_sources
        assert "ServiceNow" in report.data_sources
        assert report.generation_time_seconds > 0
        
        # Verify file was created
        import os
        files = os.listdir(tmp_path)
        assert any(f.endswith('.md') for f in files)
