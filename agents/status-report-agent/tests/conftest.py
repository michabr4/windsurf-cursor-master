"""Pytest configuration and shared fixtures."""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_case_data():
    """Sample Salesforce case data for testing."""
    return {
        "Id": "500xx000001234",
        "CaseNumber": "00001234",
        "Subject": "Test Case",
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
    }


@pytest.fixture
def sample_incident_data():
    """Sample ServiceNow incident data for testing."""
    return {
        "sys_id": "abc123def456",
        "number": "INC0001234",
        "short_description": "Test Incident",
        "description": "Test incident description",
        "state": "In Progress",
        "priority": "2",
        "urgency": "2",
        "impact": "2",
        "category": "Network",
        "subcategory": "Connectivity",
        "assignment_group": "Network Team",
        "assigned_to": "John Doe",
        "caller_id": "Jane Smith",
        "opened_at": "2025-01-05 10:00:00",
        "resolved_at": None,
        "closed_at": None,
        "sla_due": "2025-01-06 10:00:00",
        "business_service": "Email",
        "cmdb_ci": "email-server-01"
    }


@pytest.fixture
def sample_change_data():
    """Sample ServiceNow change data for testing."""
    return {
        "sys_id": "chg123def456",
        "number": "CHG0001234",
        "short_description": "Test Change",
        "description": "Test change description",
        "state": "Implement",
        "type": "normal",
        "priority": "3",
        "risk": "moderate",
        "impact": "2",
        "assignment_group": "Change Team",
        "assigned_to": "John Doe",
        "requested_by": "Jane Smith",
        "start_date": "2025-01-10 10:00:00",
        "end_date": "2025-01-10 12:00:00",
        "opened_at": "2025-01-05 10:00:00",
        "closed_at": None,
        "cmdb_ci": "app-server-01"
    }
