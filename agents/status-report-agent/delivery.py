"""Delivery channels for Status Report Agent - Email and Webex."""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List
from pathlib import Path
from datetime import datetime

import requests

from config import Settings
from models import StatusReport, ReportDeliveryResult
from report_generator import ReportGenerator

logger = logging.getLogger(__name__)

# Webex Messages API markdown limit (leave headroom below 7439)
_WEBEX_MARKDOWN_MAX = 7200


def _truncate_for_webex(text: str, max_chars: int) -> str:
    """Trim text for Webex markdown body; avoid mid-word cuts when possible."""
    if not text or len(text) <= max_chars:
        return text.strip()
    cut = text[: max_chars - 1].rsplit(" ", 1)[0]
    return (cut or text[: max_chars]).rstrip() + "…"


class EmailDelivery:
    """Email delivery for status reports."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.report_generator = ReportGenerator(settings)
    
    def send_report(
        self,
        report: StatusReport,
        recipients: Optional[List[str]] = None,
        subject: Optional[str] = None,
        attach_formats: Optional[List[str]] = None
    ) -> ReportDeliveryResult:
        """
        Send status report via email.
        
        Args:
            report: StatusReport to send
            recipients: List of email addresses (defaults to settings)
            subject: Email subject (auto-generated if not provided)
            attach_formats: List of formats to attach (e.g., ['markdown', 'json'])
        
        Returns:
            ReportDeliveryResult with success status
        """
        recipients = recipients or self.settings.recipients_list
        
        if not recipients:
            return ReportDeliveryResult(
                channel="email",
                success=False,
                destination="",
                error="No recipients configured"
            )
        
        if not self.settings.smtp_server:
            return ReportDeliveryResult(
                channel="email",
                success=False,
                destination=", ".join(recipients),
                error="SMTP server not configured"
            )
        
        # Generate subject
        if not subject:
            account_suffix = f" - {report.account_name}" if report.account_name else ""
            subject = f"Weekly Status Report ({report.role}){account_suffix} - {report.period_label}"
        
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.settings.smtp_username
            msg["To"] = ", ".join(recipients)
            
            # Plain text version
            text_content = self._create_plain_text(report)
            msg.attach(MIMEText(text_content, "plain"))
            
            # HTML version
            html_content = self.report_generator.to_html(report)
            msg.attach(MIMEText(html_content, "html"))
            
            # Attachments
            if attach_formats:
                for fmt in attach_formats:
                    self._attach_format(msg, report, fmt)
            
            # Send
            with smtplib.SMTP(self.settings.smtp_server, self.settings.smtp_port) as server:
                server.starttls()
                if self.settings.smtp_username and self.settings.smtp_password:
                    server.login(self.settings.smtp_username, self.settings.smtp_password)
                server.sendmail(
                    self.settings.smtp_username,
                    recipients,
                    msg.as_string()
                )
            
            logger.info(f"Email sent to {len(recipients)} recipients")
            
            return ReportDeliveryResult(
                channel="email",
                success=True,
                destination=", ".join(recipients)
            )
            
        except Exception as e:
            logger.error(f"Email delivery failed: {e}")
            return ReportDeliveryResult(
                channel="email",
                success=False,
                destination=", ".join(recipients),
                error=str(e)
            )
    
    def _create_plain_text(self, report: StatusReport) -> str:
        """Create plain text version of report."""
        lines = [
            f"Weekly Status Report - {report.role}",
            f"Period: {report.period_label}",
            f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M UTC')}",
            "",
            "=" * 60,
            "EXECUTIVE SUMMARY",
            "=" * 60,
            "",
            report.executive_summary,
            ""
        ]
        
        if report.highlights:
            lines.extend(["", "KEY HIGHLIGHTS:", ""])
            for h in report.highlights:
                lines.append(f"  * {h}")
        
        if report.concerns:
            lines.extend(["", "CONCERNS:", ""])
            for c in report.concerns:
                lines.append(f"  ! {c}")
        
        if report.action_items:
            lines.extend(["", "ACTION ITEMS:", ""])
            for a in report.action_items:
                lines.append(f"  [ ] {a}")
        
        lines.extend([
            "",
            "-" * 60,
            f"Generated by Status Report Agent in {report.generation_time_seconds:.1f}s",
            f"Data sources: {', '.join(report.data_sources)}"
        ])
        
        return "\n".join(lines)
    
    def _attach_format(self, msg: MIMEMultipart, report: StatusReport, fmt: str):
        """Attach report in specified format."""
        if fmt == "markdown" or fmt == "md":
            content = self.report_generator.to_markdown(report)
            filename = f"status_report_{report.role}_{report.generated_at.strftime('%Y%m%d')}.md"
            mime_type = "text/markdown"
        elif fmt == "json":
            content = self.report_generator.to_json(report)
            filename = f"status_report_{report.role}_{report.generated_at.strftime('%Y%m%d')}.json"
            mime_type = "application/json"
        elif fmt == "html":
            content = self.report_generator.to_html(report)
            filename = f"status_report_{report.role}_{report.generated_at.strftime('%Y%m%d')}.html"
            mime_type = "text/html"
        else:
            return
        
        part = MIMEBase("application", "octet-stream")
        part.set_payload(content.encode("utf-8"))
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={filename}")
        msg.attach(part)


class WebexDelivery:
    """Webex Teams delivery for status reports."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.base_url = "https://webexapis.com/v1"
        self.report_generator = ReportGenerator(settings)
    
    def _get_headers(self) -> dict:
        """Get authorization headers."""
        return {
            "Authorization": f"Bearer {self.settings.webex_access_token}",
            "Content-Type": "application/json"
        }
    
    def send_report(
        self,
        report: StatusReport,
        room_id: Optional[str] = None,
        include_full_report: bool = False
    ) -> ReportDeliveryResult:
        """
        Send status report to Webex room.
        
        Args:
            report: StatusReport to send
            room_id: Webex room ID (defaults to settings)
            include_full_report: Whether to include full report as file
        
        Returns:
            ReportDeliveryResult with success status
        """
        room_id = room_id or self.settings.webex_room_id
        
        if not self.settings.webex_access_token:
            return ReportDeliveryResult(
                channel="webex",
                success=False,
                destination=room_id or "",
                error="Webex access token not configured"
            )
        
        if not room_id:
            return ReportDeliveryResult(
                channel="webex",
                success=False,
                destination="",
                error="Webex room ID not configured"
            )
        
        try:
            # Create summary message
            message = self._create_webex_message(
                report, hint_attachment=include_full_report
            )
            
            # Send message
            response = requests.post(
                f"{self.base_url}/messages",
                headers=self._get_headers(),
                json={
                    "roomId": room_id,
                    "markdown": message
                }
            )
            response.raise_for_status()
            
            logger.info(f"Webex message sent to room {room_id}")
            
            # Optionally upload full report as file
            if include_full_report:
                self._upload_report_file(report, room_id)
            
            return ReportDeliveryResult(
                channel="webex",
                success=True,
                destination=room_id
            )
            
        except Exception as e:
            logger.error(f"Webex delivery failed: {e}")
            return ReportDeliveryResult(
                channel="webex",
                success=False,
                destination=room_id,
                error=str(e)
            )
    
    def _create_webex_message(
        self, report: StatusReport, hint_attachment: bool = False
    ) -> str:
        """Create Webex-formatted message from report."""
        period_days = max(
            1, (report.period_end - report.period_start).days
        )
        cadence = "Daily" if period_days <= 1 else "Weekly"

        def render_with_budget(summary_max: int) -> str:
            lines: list[str] = [
                f"## 📊 {cadence} Status Report — {report.role}",
                f"**Period:** {report.period_label}",
                "",
            ]
            if report.account_name:
                lines.append(f"**Account:** {report.account_name}")
                lines.append("")
            status_emoji = self._get_status_emoji(report)
            lines.append(f"### Overall Status: {status_emoji}")
            lines.append("")
            if report.executive_summary and report.executive_summary.strip():
                lines.append("### 📝 Executive summary")
                lines.append(
                    _truncate_for_webex(
                        report.executive_summary.strip(), summary_max
                    )
                )
                lines.append("")
            lines.append("### 📈 Quick Metrics")
            if report.case_metrics:
                cm = report.case_metrics
                lines.append(
                    f"- **SF Cases:** {cm.total_cases} total "
                    f"({cm.open_cases} open, {cm.new_cases_this_period} new)"
                )
            if report.incident_metrics:
                im = report.incident_metrics
                lines.append(
                    f"- **Incidents:** {im.total_incidents} total "
                    f"(P1: {im.p1_count}, P2: {im.p2_count})"
                )
                lines.append(f"- **SLA Compliance:** {im.sla_compliance_pct:.1f}%")
            if report.change_metrics:
                chm = report.change_metrics
                lines.append(
                    f"- **Changes:** {chm.total_changes} "
                    f"({chm.completed_changes} completed)"
                )
            if report.project_metrics:
                pm = report.project_metrics
                lines.append(
                    f"- **Tasks:** {pm.total_tasks} ({pm.overdue_tasks} overdue)"
                )
            lines.append("")
            if report.highlights:
                lines.append("### ✅ Highlights")
                for h in report.highlights[:5]:
                    lines.append(f"- {h}")
                lines.append("")
            if report.concerns:
                lines.append("### ⚠️ Attention Needed")
                for c in report.concerns[:4]:
                    lines.append(f"- {c}")
                lines.append("")
            if report.action_items:
                lines.append("### 📋 Action Items")
                for a in report.action_items[:5]:
                    lines.append(f"- [ ] {a}")
                lines.append("")
            lines.append("---")
            lines.append(
                f"*Generated in {report.generation_time_seconds:.1f}s | "
                f"{', '.join(report.data_sources)}*"
            )
            if hint_attachment:
                lines.append("")
                lines.append(
                    "*Full narrative and metric tables: check the `.md` attachment on this message "
                    "when file upload succeeds (bot needs permission to post files in this space).*"
                )
            return "\n".join(lines)

        body = ""
        for budget in (3500, 1800, 900, 400):
            body = render_with_budget(budget)
            if len(body) <= _WEBEX_MARKDOWN_MAX:
                break
        if len(body) > _WEBEX_MARKDOWN_MAX:
            return _truncate_for_webex(body, _WEBEX_MARKDOWN_MAX)
        return body
    
    def _get_status_emoji(self, report: StatusReport) -> str:
        """Determine overall status emoji based on metrics."""
        concerns = len(report.concerns) if report.concerns else 0
        
        # Check for critical issues
        if report.incident_metrics:
            if report.incident_metrics.p1_count > 0:
                return "🔴 RED"
            if report.incident_metrics.sla_compliance_pct < 85:
                return "🟡 YELLOW"
        
        if report.project_metrics:
            if report.project_metrics.overdue_tasks > 5:
                return "🟡 YELLOW"
        
        if concerns >= 3:
            return "🟡 YELLOW"
        
        return "🟢 GREEN"
    
    def _upload_report_file(self, report: StatusReport, room_id: str):
        """Upload full report as a file to Webex room."""
        try:
            # Generate markdown content
            content = self.report_generator.to_markdown(report)
            filename = f"status_report_{report.role}_{report.generated_at.strftime('%Y%m%d')}.md"
            
            # Upload file
            files = {
                "files": (filename, content.encode("utf-8"), "text/markdown")
            }
            
            response = requests.post(
                f"{self.base_url}/messages",
                headers={"Authorization": f"Bearer {self.settings.webex_access_token}"},
                data={"roomId": room_id, "text": "Full report attached"},
                files=files
            )
            if not response.ok:
                logger.error(
                    "Webex file upload failed: %s %s",
                    response.status_code,
                    response.text[:2000],
                )
            response.raise_for_status()
            
            logger.info(f"Report file uploaded to Webex room")
            
        except Exception as e:
            logger.error("Failed to upload report file to Webex: %s", e, exc_info=True)


class DeliveryManager:
    """Manages all delivery channels."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.email = EmailDelivery(settings)
        self.webex = WebexDelivery(settings)
    
    def deliver(
        self,
        report: StatusReport,
        channels: Optional[List[str]] = None,
        email_recipients: Optional[List[str]] = None,
        webex_room_id: Optional[str] = None
    ) -> List[ReportDeliveryResult]:
        """
        Deliver report to specified channels.
        
        Args:
            report: StatusReport to deliver
            channels: List of channels ('email', 'webex'). Defaults to all configured.
            email_recipients: Override email recipients
            webex_room_id: Override Webex room ID
        
        Returns:
            List of ReportDeliveryResult for each channel
        """
        results = []
        
        # Determine channels
        if channels is None:
            channels = []
            if self.settings.smtp_server and self.settings.recipients_list:
                channels.append("email")
            if self.settings.webex_access_token and self.settings.webex_room_id:
                channels.append("webex")
        
        # Deliver to each channel
        for channel in channels:
            if channel == "email":
                result = self.email.send_report(
                    report,
                    recipients=email_recipients,
                    attach_formats=["markdown"]
                )
                results.append(result)
                
            elif channel == "webex":
                result = self.webex.send_report(
                    report,
                    room_id=webex_room_id,
                    include_full_report=True
                )
                results.append(result)
        
        # Log summary
        success_count = sum(1 for r in results if r.success)
        logger.info(f"Delivery complete: {success_count}/{len(results)} channels successful")
        
        return results
