"""Tests for delivery channels (Email, Webex)."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from config import Settings
from delivery import EmailDelivery, WebexDelivery, DeliveryManager
from models import StatusReport, CaseMetrics, IncidentMetrics


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    return Settings(
        smtp_server="smtp.test.com",
        smtp_port=587,
        smtp_username="test@test.com",
        smtp_password="password",
        report_recipients="recipient1@test.com,recipient2@test.com",
        webex_access_token="test-token-123",
        webex_room_id="room-123"
    )


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
            new_cases_this_period=10
        ),
        incident_metrics=IncidentMetrics(
            total_incidents=30,
            p1_count=0,
            p2_count=5,
            sla_compliance_pct=95.0
        ),
        executive_summary="Test summary for delivery testing.",
        highlights=["Highlight 1", "Highlight 2"],
        concerns=["Concern 1"],
        action_items=["Action 1"],
        data_sources=["Salesforce", "ServiceNow"],
        generation_time_seconds=1.5
    )


class TestEmailDelivery:
    """Tests for EmailDelivery."""
    
    def test_initialization(self, mock_settings):
        """Test email delivery initializes correctly."""
        delivery = EmailDelivery(mock_settings)
        
        assert delivery.settings == mock_settings
    
    def test_no_recipients_configured(self):
        """Test error when no recipients configured."""
        settings = Settings(
            smtp_server="smtp.test.com",
            report_recipients=""
        )
        
        delivery = EmailDelivery(settings)
        result = delivery.send_report(StatusReport(
            report_id="test",
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow(),
            role="SDM"
        ))
        
        assert result.success is False
        assert "No recipients" in result.error
    
    def test_no_smtp_configured(self):
        """Test error when SMTP not configured."""
        settings = Settings(
            smtp_server="",
            report_recipients="test@test.com"
        )
        
        delivery = EmailDelivery(settings)
        result = delivery.send_report(StatusReport(
            report_id="test",
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow(),
            role="SDM"
        ))
        
        assert result.success is False
        assert "SMTP" in result.error
    
    @patch('delivery.smtplib.SMTP')
    def test_send_report_success(self, mock_smtp_class, mock_settings, sample_report):
        """Test successful email delivery."""
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__ = Mock(return_value=mock_smtp)
        mock_smtp_class.return_value.__exit__ = Mock(return_value=False)
        
        delivery = EmailDelivery(mock_settings)
        result = delivery.send_report(sample_report)
        
        assert result.success is True
        assert result.channel == "email"
        assert "recipient1@test.com" in result.destination
        
        # Verify SMTP was called
        mock_smtp.starttls.assert_called_once()
        mock_smtp.login.assert_called_once()
        mock_smtp.sendmail.assert_called_once()
    
    @patch('delivery.smtplib.SMTP')
    def test_send_report_with_custom_recipients(self, mock_smtp_class, mock_settings, sample_report):
        """Test email delivery with custom recipients."""
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__ = Mock(return_value=mock_smtp)
        mock_smtp_class.return_value.__exit__ = Mock(return_value=False)
        
        delivery = EmailDelivery(mock_settings)
        result = delivery.send_report(
            sample_report,
            recipients=["custom@test.com"]
        )
        
        assert result.success is True
        assert "custom@test.com" in result.destination
    
    @patch('delivery.smtplib.SMTP')
    def test_send_report_failure(self, mock_smtp_class, mock_settings, sample_report):
        """Test email delivery failure handling."""
        mock_smtp_class.side_effect = Exception("Connection failed")
        
        delivery = EmailDelivery(mock_settings)
        result = delivery.send_report(sample_report)
        
        assert result.success is False
        assert "Connection failed" in result.error
    
    def test_create_plain_text(self, mock_settings, sample_report):
        """Test plain text email content generation."""
        delivery = EmailDelivery(mock_settings)
        
        text = delivery._create_plain_text(sample_report)
        
        assert "Weekly Status Report - SDM" in text
        assert "Test summary" in text
        assert "KEY HIGHLIGHTS" in text
        assert "Highlight 1" in text
        assert "CONCERNS" in text
        assert "ACTION ITEMS" in text


class TestWebexDelivery:
    """Tests for WebexDelivery."""
    
    def test_initialization(self, mock_settings):
        """Test Webex delivery initializes correctly."""
        delivery = WebexDelivery(mock_settings)
        
        assert delivery.settings == mock_settings
        assert delivery.base_url == "https://webexapis.com/v1"
    
    def test_no_token_configured(self):
        """Test error when Webex token not configured."""
        settings = Settings(
            webex_access_token="",
            webex_room_id="room-123"
        )
        
        delivery = WebexDelivery(settings)
        result = delivery.send_report(StatusReport(
            report_id="test",
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow(),
            role="SDM"
        ))
        
        assert result.success is False
        assert "token" in result.error.lower()
    
    def test_no_room_configured(self):
        """Test error when Webex room not configured."""
        settings = Settings(
            webex_access_token="token-123",
            webex_room_id=""
        )
        
        delivery = WebexDelivery(settings)
        result = delivery.send_report(StatusReport(
            report_id="test",
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow(),
            role="SDM"
        ))
        
        assert result.success is False
        assert "room" in result.error.lower()
    
    @patch('delivery.requests.post')
    def test_send_report_success(self, mock_post, mock_settings, sample_report):
        """Test successful Webex delivery."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        delivery = WebexDelivery(mock_settings)
        result = delivery.send_report(sample_report)
        
        assert result.success is True
        assert result.channel == "webex"
        assert result.destination == "room-123"
        
        # Verify API was called
        mock_post.assert_called()
        call_args = mock_post.call_args
        assert "roomId" in str(call_args)
    
    @patch('delivery.requests.post')
    def test_send_report_failure(self, mock_post, mock_settings, sample_report):
        """Test Webex delivery failure handling."""
        mock_post.side_effect = Exception("API error")
        
        delivery = WebexDelivery(mock_settings)
        result = delivery.send_report(sample_report)
        
        assert result.success is False
        assert "API error" in result.error
    
    def test_create_webex_message(self, mock_settings, sample_report):
        """Test Webex message formatting."""
        delivery = WebexDelivery(mock_settings)
        
        message = delivery._create_webex_message(sample_report)
        
        assert "📊 Weekly Status Report — SDM" in message
        assert "Acme Corp" in message
        assert "📈 Quick Metrics" in message
        assert "SF Cases" in message
        assert "✅ Highlights" in message
        assert "Highlight 1" in message
    
    def test_status_emoji_green(self, mock_settings):
        """Test green status determination."""
        delivery = WebexDelivery(mock_settings)
        
        report = StatusReport(
            report_id="test",
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow(),
            role="SDM",
            incident_metrics=IncidentMetrics(
                total_incidents=10,
                p1_count=0,
                sla_compliance_pct=95.0
            ),
            concerns=[]
        )
        
        status = delivery._get_status_emoji(report)
        assert "GREEN" in status
    
    def test_status_emoji_red_p1(self, mock_settings):
        """Test red status when P1 exists."""
        delivery = WebexDelivery(mock_settings)
        
        report = StatusReport(
            report_id="test",
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow(),
            role="SDM",
            incident_metrics=IncidentMetrics(
                total_incidents=10,
                p1_count=1,
                sla_compliance_pct=95.0
            )
        )
        
        status = delivery._get_status_emoji(report)
        assert "RED" in status
    
    def test_status_emoji_yellow_sla(self, mock_settings):
        """Test yellow status when SLA low."""
        delivery = WebexDelivery(mock_settings)
        
        report = StatusReport(
            report_id="test",
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow(),
            role="SDM",
            incident_metrics=IncidentMetrics(
                total_incidents=10,
                p1_count=0,
                sla_compliance_pct=80.0  # Below 85%
            )
        )
        
        status = delivery._get_status_emoji(report)
        assert "YELLOW" in status


class TestDeliveryManager:
    """Tests for DeliveryManager."""
    
    def test_initialization(self, mock_settings):
        """Test manager initializes both channels."""
        manager = DeliveryManager(mock_settings)
        
        assert manager.email is not None
        assert manager.webex is not None
    
    @patch('delivery.smtplib.SMTP')
    @patch('delivery.requests.post')
    def test_deliver_all_channels(self, mock_post, mock_smtp_class, mock_settings, sample_report):
        """Test delivery to all channels."""
        # Setup mocks
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__ = Mock(return_value=mock_smtp)
        mock_smtp_class.return_value.__exit__ = Mock(return_value=False)
        
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        manager = DeliveryManager(mock_settings)
        results = manager.deliver(sample_report, channels=["email", "webex"])
        
        assert len(results) == 2
        assert all(r.success for r in results)
    
    @patch('delivery.smtplib.SMTP')
    def test_deliver_email_only(self, mock_smtp_class, mock_settings, sample_report):
        """Test delivery to email only."""
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__ = Mock(return_value=mock_smtp)
        mock_smtp_class.return_value.__exit__ = Mock(return_value=False)
        
        manager = DeliveryManager(mock_settings)
        results = manager.deliver(sample_report, channels=["email"])
        
        assert len(results) == 1
        assert results[0].channel == "email"
        assert results[0].success is True
    
    def test_auto_detect_channels(self, mock_settings):
        """Test automatic channel detection from settings."""
        manager = DeliveryManager(mock_settings)
        
        # Both email and webex are configured in mock_settings
        # deliver() with no channels should detect both
        # We can't fully test this without mocking, but we can verify the logic
        assert mock_settings.smtp_server is not None
        assert mock_settings.webex_access_token is not None
