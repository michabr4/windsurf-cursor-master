"""Tests for API clients (Salesforce, ServiceNow)."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from config import Settings
from salesforce_client import SalesforceClient
from servicenow_client import ServiceNowClient
from models import CaseMetrics, IncidentMetrics, SLAStatus


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    settings = Settings(
        sf_instance_url="https://test.salesforce.com",
        sf_username="test@test.com",
        sf_password="password",
        sf_security_token="token",
        sn_instance_url="https://test.service-now.com",
        sn_username="admin",
        sn_password="password"
    )
    return settings


class TestSalesforceClient:
    """Tests for SalesforceClient."""
    
    @patch('salesforce_client.Salesforce')
    def test_client_initialization(self, mock_sf_class, mock_settings):
        """Test client initializes correctly."""
        client = SalesforceClient(mock_settings)
        
        # Connection should be lazy
        assert client._sf is None
    
    @patch('salesforce_client.Salesforce')
    def test_get_cases(self, mock_sf_class, mock_settings):
        """Test fetching cases from Salesforce."""
        # Setup mock
        mock_sf = MagicMock()
        mock_sf_class.return_value = mock_sf
        
        mock_sf.query_all.return_value = {
            "records": [
                {
                    "Id": "500xx000001",
                    "CaseNumber": "00001234",
                    "Subject": "Test Case 1",
                    "Description": "Test description",
                    "Status": "Open",
                    "Priority": "High",
                    "AccountId": "001xx000001",
                    "Account": {"Name": "Test Account"},
                    "Contact": {"Name": "John Doe"},
                    "Owner": {"Name": "Jane Smith"},
                    "CreatedDate": "2025-01-01T10:00:00Z",
                    "ClosedDate": None,
                    "LastModifiedDate": "2025-01-05T15:00:00Z",
                    "Type": "Problem",
                    "Origin": "Email",
                    "Reason": None,
                    "IsEscalated": False
                },
                {
                    "Id": "500xx000002",
                    "CaseNumber": "00001235",
                    "Subject": "Test Case 2",
                    "Description": None,
                    "Status": "Closed",
                    "Priority": "Medium",
                    "AccountId": "001xx000001",
                    "Account": {"Name": "Test Account"},
                    "Contact": None,
                    "Owner": {"Name": "Jane Smith"},
                    "CreatedDate": "2025-01-02T10:00:00Z",
                    "ClosedDate": "2025-01-04T10:00:00Z",
                    "LastModifiedDate": "2025-01-04T10:00:00Z",
                    "Type": "Question",
                    "Origin": "Web",
                    "Reason": None,
                    "IsEscalated": False
                }
            ]
        }
        
        client = SalesforceClient(mock_settings)
        cases = client.get_cases(lookback_days=7)
        
        assert len(cases) == 2
        assert cases[0].case_number == "00001234"
        assert cases[0].status == "Open"
        assert cases[0].account_name == "Test Account"
        assert cases[1].status == "Closed"
    
    @patch('salesforce_client.Salesforce')
    def test_calculate_case_metrics(self, mock_sf_class, mock_settings):
        """Test case metrics calculation."""
        client = SalesforceClient(mock_settings)
        
        # Create test cases
        from models import SalesforceCase
        
        now = datetime.utcnow()
        period_start = now - timedelta(days=7)
        period_end = now
        
        cases = [
            SalesforceCase(
                id="1", case_number="001", subject="Case 1",
                status="Open", priority="High",
                created_date=now - timedelta(days=5),
                last_modified_date=now,
                is_escalated=True
            ),
            SalesforceCase(
                id="2", case_number="002", subject="Case 2",
                status="Open", priority="Medium",
                created_date=now - timedelta(days=3),
                last_modified_date=now
            ),
            SalesforceCase(
                id="3", case_number="003", subject="Case 3",
                status="Closed", priority="Low",
                created_date=now - timedelta(days=10),
                closed_date=now - timedelta(days=2),
                last_modified_date=now - timedelta(days=2)
            )
        ]
        
        metrics = client.calculate_case_metrics(cases, period_start, period_end)
        
        assert metrics.total_cases == 3
        assert metrics.open_cases == 2
        assert metrics.closed_cases == 1
        assert metrics.escalated_count == 1
        assert metrics.by_priority["High"] == 1
        assert metrics.by_priority["Medium"] == 1
        assert metrics.by_priority["Low"] == 1


class TestServiceNowClient:
    """Tests for ServiceNowClient."""
    
    def test_client_initialization(self, mock_settings):
        """Test client initializes correctly."""
        client = ServiceNowClient(mock_settings)
        
        assert client.base_url == "https://test.service-now.com"
        assert client._session is None
    
    @patch('servicenow_client.requests.Session')
    def test_get_incidents(self, mock_session_class, mock_settings):
        """Test fetching incidents from ServiceNow."""
        # Setup mock
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "result": [
                {
                    "sys_id": "abc123",
                    "number": "INC0001234",
                    "short_description": "Test Incident 1",
                    "description": "Test description",
                    "state": "In Progress",
                    "priority": "2",
                    "urgency": "2",
                    "impact": "2",
                    "category": "Network",
                    "subcategory": None,
                    "assignment_group": "Network Team",
                    "assigned_to": "John Doe",
                    "caller_id": "Jane Smith",
                    "opened_at": "2025-01-05 10:00:00",
                    "resolved_at": None,
                    "closed_at": None,
                    "sla_due": "2025-01-06 10:00:00",
                    "business_service": "Email",
                    "cmdb_ci": None
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_response
        
        client = ServiceNowClient(mock_settings)
        client._session = mock_session
        
        incidents = client.get_incidents(lookback_days=7)
        
        assert len(incidents) == 1
        assert incidents[0].number == "INC0001234"
        assert incidents[0].state == "In Progress"
        assert incidents[0].priority == "2"
    
    def test_calculate_incident_metrics(self, mock_settings):
        """Test incident metrics calculation."""
        client = ServiceNowClient(mock_settings)
        
        from models import ServiceNowIncident
        
        now = datetime.utcnow()
        period_start = now - timedelta(days=7)
        period_end = now
        
        incidents = [
            ServiceNowIncident(
                sys_id="1", number="INC001",
                short_description="P1 Incident",
                state="Resolved", priority="1",
                urgency="1", impact="1",
                opened_at=now - timedelta(hours=10),
                resolved_at=now - timedelta(hours=2),
                sla_due=now + timedelta(hours=2)
            ),
            ServiceNowIncident(
                sys_id="2", number="INC002",
                short_description="P2 Incident",
                state="In Progress", priority="2",
                urgency="2", impact="2",
                opened_at=now - timedelta(hours=5),
                sla_due=now + timedelta(hours=10)
            ),
            ServiceNowIncident(
                sys_id="3", number="INC003",
                short_description="P3 Incident",
                state="New", priority="3",
                urgency="3", impact="3",
                opened_at=now - timedelta(hours=2)
            )
        ]
        
        metrics = client.calculate_incident_metrics(incidents, period_start, period_end)
        
        assert metrics.total_incidents == 3
        assert metrics.p1_count == 1
        assert metrics.p2_count == 1
        assert metrics.resolved_incidents == 1
        assert metrics.open_incidents == 2
    
    def test_calculate_change_metrics(self, mock_settings):
        """Test change metrics calculation."""
        client = ServiceNowClient(mock_settings)
        
        from models import ServiceNowChange
        
        now = datetime.utcnow()
        period_start = now - timedelta(days=7)
        period_end = now
        
        changes = [
            ServiceNowChange(
                sys_id="1", number="CHG001",
                short_description="Normal Change",
                state="Closed", type="normal",
                priority="3", risk="moderate", impact="2",
                opened_at=now - timedelta(days=5),
                start_date=now - timedelta(days=2),
                closed_at=now - timedelta(days=1)
            ),
            ServiceNowChange(
                sys_id="2", number="CHG002",
                short_description="Emergency Change",
                state="Implement", type="emergency",
                priority="1", risk="high", impact="1",
                opened_at=now - timedelta(days=1),
                start_date=now
            )
        ]
        
        metrics = client.calculate_change_metrics(changes, period_start, period_end)
        
        assert metrics.total_changes == 2
        assert metrics.emergency_count == 1
        assert metrics.by_type["normal"] == 1
        assert metrics.by_type["emergency"] == 1
