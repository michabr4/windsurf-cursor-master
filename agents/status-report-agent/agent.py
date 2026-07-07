"""Main Status Report Agent orchestrator."""

import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from config import Settings, get_settings
from models import (
    StatusReport, CaseMetrics, IncidentMetrics, 
    ChangeMetrics, ProjectMetrics, ReportSection
)
from salesforce_client import SalesforceClient
from servicenow_client import ServiceNowClient
from llm_client import LLMClient
from report_generator import ReportGenerator

logger = logging.getLogger(__name__)


class StatusReportAgent:
    """
    Main agent that orchestrates data collection from Salesforce and ServiceNow,
    generates LLM-powered narratives, and produces formatted status reports.
    
    This is Agent #1 from the Helix Agentic Framework V3:
    "Automated Status Report Generation"
    
    Roles: SDM · PM · PgM
    Feasibility: VERY HIGH
    Build effort: 2-3 sprints
    
    Before: 2-3 hrs manual/role/week
    After: <10 min weekly review
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        
        # Clients (lazy initialization)
        self._sf_client: Optional[SalesforceClient] = None
        self._sn_client: Optional[ServiceNowClient] = None
        self._llm_client: Optional[LLMClient] = None
        self._report_generator: Optional[ReportGenerator] = None
        
        # Data stores
        self.cases = []
        self.incidents = []
        self.changes = []
        self.tasks = []
        
        # Metrics
        self.case_metrics: Optional[CaseMetrics] = None
        self.incident_metrics: Optional[IncidentMetrics] = None
        self.change_metrics: Optional[ChangeMetrics] = None
        self.project_metrics: Optional[ProjectMetrics] = None

        # Resolved Salesforce account (when filter is name or Id)
        self._resolved_account_id: Optional[str] = None
        self._resolved_account_name: Optional[str] = None

    @property
    def sf_client(self) -> SalesforceClient:
        """Get Salesforce client (lazy init)."""
        if self._sf_client is None:
            self._sf_client = SalesforceClient(self.settings)
        return self._sf_client
    
    @property
    def sn_client(self) -> ServiceNowClient:
        """Get ServiceNow client (lazy init)."""
        if self._sn_client is None:
            self._sn_client = ServiceNowClient(self.settings)
        return self._sn_client
    
    @property
    def llm_client(self) -> LLMClient:
        """Get LLM client (lazy init)."""
        if self._llm_client is None:
            self._llm_client = LLMClient(self.settings)
        return self._llm_client
    
    @property
    def report_generator(self) -> ReportGenerator:
        """Get report generator (lazy init)."""
        if self._report_generator is None:
            self._report_generator = ReportGenerator(self.settings)
        return self._report_generator
    
    def collect_salesforce_data(
        self,
        lookback_days: int,
        account_filter: Optional[str] = None
    ) -> None:
        """
        Collect data from Salesforce.
        
        Args:
            lookback_days: Number of days to look back
            account_filter: Optional Account Id (15/18 chars) or Account Name to filter cases
        """
        self._resolved_account_id = None
        self._resolved_account_name = None

        if not self.settings.validate_salesforce():
            logger.warning("Salesforce not configured, skipping")
            return
        
        logger.info("Collecting Salesforce data...")

        resolved_id: Optional[str] = None
        if account_filter and str(account_filter).strip():
            resolved_id, resolved_name = self.sf_client.resolve_account_filter(
                str(account_filter).strip()
            )
            self._resolved_account_id = resolved_id
            self._resolved_account_name = resolved_name
            if not resolved_id:
                logger.warning(
                    "Account filter %r did not resolve; loading cases without account scope",
                    account_filter,
                )
        
        try:
            self.cases = self.sf_client.get_cases(
                lookback_days=lookback_days,
                account_id=resolved_id
            )
            logger.info(f"Collected {len(self.cases)} cases")
        except Exception as e:
            logger.error(f"Failed to collect Salesforce cases: {e}")
            self.cases = []
    
    def collect_servicenow_data(
        self,
        lookback_days: int,
        assignment_group: Optional[str] = None
    ) -> None:
        """
        Collect data from ServiceNow.
        
        Args:
            lookback_days: Number of days to look back
            assignment_group: Optional assignment group to filter by
        """
        if not self.settings.validate_servicenow():
            logger.warning("ServiceNow not configured, skipping")
            return
        
        logger.info("Collecting ServiceNow data...")
        
        try:
            self.incidents = self.sn_client.get_incidents(
                lookback_days=lookback_days,
                assignment_group=assignment_group
            )
            logger.info(f"Collected {len(self.incidents)} incidents")
        except Exception as e:
            logger.error(f"Failed to collect incidents: {e}")
            self.incidents = []
        
        try:
            self.changes = self.sn_client.get_changes(
                lookback_days=lookback_days,
                assignment_group=assignment_group
            )
            logger.info(f"Collected {len(self.changes)} changes")
        except Exception as e:
            logger.error(f"Failed to collect changes: {e}")
            self.changes = []
        
        try:
            self.tasks = self.sn_client.get_tasks(
                lookback_days=lookback_days * 2,  # Longer lookback for tasks
                assignment_group=assignment_group
            )
            logger.info(f"Collected {len(self.tasks)} tasks")
        except Exception as e:
            logger.error(f"Failed to collect tasks: {e}")
            self.tasks = []
    
    def calculate_metrics(
        self,
        period_start: datetime,
        period_end: datetime
    ) -> None:
        """
        Calculate aggregated metrics from collected data.
        
        Args:
            period_start: Start of reporting period
            period_end: End of reporting period
        """
        logger.info("Calculating metrics...")
        
        # Salesforce case metrics
        if self.cases:
            self.case_metrics = self.sf_client.calculate_case_metrics(
                self.cases, period_start, period_end
            )
        
        # ServiceNow metrics
        if self.incidents:
            self.incident_metrics = self.sn_client.calculate_incident_metrics(
                self.incidents, period_start, period_end
            )
        
        if self.changes:
            self.change_metrics = self.sn_client.calculate_change_metrics(
                self.changes, period_start, period_end
            )
        
        if self.tasks:
            self.project_metrics = self.sn_client.calculate_task_metrics(
                self.tasks, period_start, period_end
            )
    
    def generate_narratives(
        self,
        role: str,
        period_label: str,
        account_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate LLM-powered narratives.
        
        Args:
            role: Role perspective (SDM, PM, PgM)
            period_label: Human-readable period
            account_name: Optional account name
        
        Returns:
            Dictionary with executive_summary, highlights, concerns, actions
        """
        if not self.settings.validate_llm():
            logger.warning("LLM not configured, using placeholder narratives")
            return {
                "executive_summary": self._generate_placeholder_summary(),
                "highlights": [],
                "concerns": [],
                "actions": []
            }
        
        logger.info("Generating LLM narratives...")
        
        # Executive summary
        executive_summary = self.llm_client.generate_executive_summary(
            role=role,
            period_label=period_label,
            case_metrics=self.case_metrics,
            incident_metrics=self.incident_metrics,
            change_metrics=self.change_metrics,
            project_metrics=self.project_metrics,
            account_name=account_name
        )
        
        # Highlights and concerns
        hc = self.llm_client.generate_highlights_and_concerns(
            case_metrics=self.case_metrics,
            incident_metrics=self.incident_metrics,
            change_metrics=self.change_metrics,
            project_metrics=self.project_metrics
        )
        
        return {
            "executive_summary": executive_summary,
            "highlights": hc.get("highlights", []),
            "concerns": hc.get("concerns", []),
            "actions": hc.get("actions", [])
        }
    
    def _generate_placeholder_summary(self) -> str:
        """Generate a placeholder summary when LLM is not available."""
        parts = []
        
        if self.case_metrics:
            parts.append(f"Salesforce: {self.case_metrics.total_cases} cases "
                        f"({self.case_metrics.open_cases} open, "
                        f"{self.case_metrics.new_cases_this_period} new this period)")
        
        if self.incident_metrics:
            parts.append(f"Incidents: {self.incident_metrics.total_incidents} total "
                        f"({self.incident_metrics.p1_count} P1, {self.incident_metrics.p2_count} P2), "
                        f"SLA compliance: {self.incident_metrics.sla_compliance_pct:.1f}%")
        
        if self.change_metrics:
            parts.append(f"Changes: {self.change_metrics.total_changes} total "
                        f"({self.change_metrics.completed_changes} completed)")
        
        if self.project_metrics:
            parts.append(f"Tasks: {self.project_metrics.total_tasks} total "
                        f"({self.project_metrics.overdue_tasks} overdue)")
        
        return "\n\n".join(parts) if parts else "No data available for this period."
    
    def run(
        self,
        lookback_days: Optional[int] = None,
        role: Optional[str] = None,
        account_filter: Optional[str] = None,
        assignment_group: Optional[str] = None,
        save_report: bool = True,
        output_format: Optional[str] = None
    ) -> StatusReport:
        """
        Run the full status report generation pipeline.
        
        Args:
            lookback_days: Number of days to look back (default from settings)
            role: Role perspective - SDM, PM, or PgM (default from settings)
            account_filter: Optional Salesforce account name/ID to filter by
            assignment_group: Optional ServiceNow assignment group to filter by
            save_report: Whether to save the report to file
            output_format: Output format (markdown, html, json)
        
        Returns:
            StatusReport object
        """
        start_time = time.time()
        
        # Apply defaults
        lookback_days = lookback_days or self.settings.lookback_days
        role = role or self.settings.role
        raw_filter = account_filter if account_filter is not None else self.settings.account_filter
        account_filter = (raw_filter or "").strip() or None
        
        # Calculate period
        period_end = datetime.utcnow()
        period_start = period_end - timedelta(days=lookback_days)
        
        logger.info("=" * 60)
        logger.info("Status Report Agent Starting")
        logger.info(f"Role: {role}")
        logger.info(f"Period: {period_start.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')}")
        logger.info(f"Account filter: {account_filter or 'None'}")
        logger.info("=" * 60)
        
        # Collect data
        self.collect_salesforce_data(lookback_days, account_filter)
        self.collect_servicenow_data(lookback_days, assignment_group)
        
        # Calculate metrics
        self.calculate_metrics(period_start, period_end)
        
        # Generate narratives
        period_label = f"{period_start.strftime('%b %d')} - {period_end.strftime('%b %d, %Y')}"
        display_account = self._resolved_account_name or account_filter
        narratives = self.generate_narratives(role, period_label, display_account)
        
        # Build report
        generation_time = time.time() - start_time
        
        data_sources = []
        if self.cases:
            data_sources.append("Salesforce")
        if self.incidents or self.changes or self.tasks:
            data_sources.append("ServiceNow")
        
        report = StatusReport(
            report_id=str(uuid.uuid4()),
            generated_at=datetime.utcnow(),
            period_start=period_start,
            period_end=period_end,
            role=role,
            account_name=display_account,
            case_metrics=self.case_metrics,
            incident_metrics=self.incident_metrics,
            change_metrics=self.change_metrics,
            project_metrics=self.project_metrics,
            executive_summary=narratives["executive_summary"],
            highlights=narratives["highlights"],
            concerns=narratives["concerns"],
            action_items=narratives["actions"],
            data_sources=data_sources,
            generation_time_seconds=generation_time
        )
        
        # Save report
        if save_report:
            output_format = output_format or self.settings.output_format
            filepath = self.report_generator.save(report, output_format)
            logger.info(f"Report saved: {filepath}")
        
        logger.info("=" * 60)
        logger.info("Status Report Agent Complete")
        logger.info(f"Generation time: {generation_time:.1f}s")
        logger.info(f"Data sources: {', '.join(data_sources)}")
        logger.info("=" * 60)
        
        return report


def create_agent(settings: Optional[Settings] = None) -> StatusReportAgent:
    """Factory function to create a configured agent."""
    return StatusReportAgent(settings)
