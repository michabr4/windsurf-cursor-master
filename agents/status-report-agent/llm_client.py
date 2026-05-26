"""LLM client for narrative generation in Status Report Agent."""

import logging
from typing import Optional, Dict, Any, List
import json

from config import Settings
from models import (
    StatusReport, CaseMetrics, IncidentMetrics, 
    ChangeMetrics, ProjectMetrics, ReportSection
)

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for LLM-based narrative generation."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self._client = None
        self._provider = settings.llm_provider
    
    def _init_client(self):
        """Initialize the appropriate LLM client."""
        if self._client is not None:
            return
        
        if self._provider == "azure":
            try:
                from openai import AzureOpenAI
                self._client = AzureOpenAI(
                    azure_endpoint=self.settings.azure_openai_endpoint,
                    api_key=self.settings.azure_openai_key,
                    api_version=self.settings.azure_openai_api_version
                )
                logger.info("Azure OpenAI client initialized")
            except ImportError:
                logger.error("openai package not installed")
                raise
        else:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.settings.openai_api_key)
                logger.info("OpenAI client initialized")
            except ImportError:
                logger.error("openai package not installed")
                raise
    
    def _get_model(self) -> str:
        """Get the model name based on provider."""
        if self._provider == "azure":
            return self.settings.azure_openai_deployment
        return self.settings.openai_model
    
    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Make a call to the LLM."""
        self._init_client()
        
        try:
            response = self._client.chat.completions.create(
                model=self._get_model(),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise
    
    def generate_executive_summary(
        self,
        role: str,
        period_label: str,
        case_metrics: Optional[CaseMetrics],
        incident_metrics: Optional[IncidentMetrics],
        change_metrics: Optional[ChangeMetrics],
        project_metrics: Optional[ProjectMetrics],
        account_name: Optional[str] = None
    ) -> str:
        """
        Generate an executive summary narrative.
        
        Args:
            role: The role perspective (SDM, PM, PgM)
            period_label: Human-readable period (e.g., "Jan 1 - Jan 7, 2025")
            case_metrics: Salesforce case metrics
            incident_metrics: ServiceNow incident metrics
            change_metrics: ServiceNow change metrics
            project_metrics: ServiceNow task/project metrics
            account_name: Optional account name for context
        
        Returns:
            Executive summary narrative string
        """
        system_prompt = f"""You are an expert {role} (Service Delivery Manager/Project Manager/Program Manager) at Cisco CX.
Your task is to write a concise, professional executive summary for a weekly status report.

Guidelines:
- Be direct and data-driven
- Lead with the most important information
- Highlight wins and concerns clearly
- Keep it to 3-4 paragraphs maximum
- Use professional but accessible language
- Include specific numbers from the metrics
- End with a forward-looking statement

Role-specific focus:
- SDM: Focus on service health, SLA compliance, incident trends, customer impact
- PM: Focus on project progress, deliverables, risks, timeline adherence
- PgM: Focus on portfolio health, resource utilization, cross-project dependencies, financial health"""

        metrics_summary = self._format_metrics_for_prompt(
            case_metrics, incident_metrics, change_metrics, project_metrics
        )
        
        account_context = f" for {account_name}" if account_name else ""
        
        user_prompt = f"""Write an executive summary for the {role} weekly status report{account_context}.

Reporting Period: {period_label}

METRICS DATA:
{metrics_summary}

Generate a professional executive summary that:
1. Opens with overall status (Green/Yellow/Red assessment)
2. Highlights key wins and accomplishments
3. Notes any concerns or risks requiring attention
4. Provides a brief outlook for the coming week"""

        return self._call_llm(system_prompt, user_prompt)
    
    def generate_section_narrative(
        self,
        section_title: str,
        metrics: Dict[str, Any],
        role: str
    ) -> ReportSection:
        """
        Generate narrative for a specific report section.
        
        Args:
            section_title: Title of the section (e.g., "Incident Management")
            metrics: Dictionary of metrics for this section
            role: The role perspective
        
        Returns:
            ReportSection with generated content
        """
        system_prompt = f"""You are an expert {role} at Cisco CX writing a section of a status report.
Write clear, concise content for the "{section_title}" section.

Guidelines:
- Be factual and data-driven
- Use bullet points for lists
- Highlight anomalies or trends
- Keep it focused and scannable
- Include specific numbers"""

        user_prompt = f"""Write the "{section_title}" section based on these metrics:

{json.dumps(metrics, indent=2, default=str)}

Provide:
1. A brief narrative summary (2-3 sentences)
2. 2-3 key highlights (positive items)
3. 0-2 concerns (if any issues exist)
4. 0-2 recommended actions (if needed)

Format your response as JSON:
{{
    "content": "narrative summary here",
    "highlights": ["highlight 1", "highlight 2"],
    "concerns": ["concern 1"],
    "actions": ["action 1"]
}}"""

        try:
            response = self._call_llm(system_prompt, user_prompt)
            # Parse JSON response
            data = json.loads(response)
            return ReportSection(
                title=section_title,
                content=data.get("content", ""),
                metrics=metrics,
                highlights=data.get("highlights", []),
                concerns=data.get("concerns", []),
                actions=data.get("actions", [])
            )
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return ReportSection(
                title=section_title,
                content=response,
                metrics=metrics
            )
    
    def generate_highlights_and_concerns(
        self,
        case_metrics: Optional[CaseMetrics],
        incident_metrics: Optional[IncidentMetrics],
        change_metrics: Optional[ChangeMetrics],
        project_metrics: Optional[ProjectMetrics]
    ) -> Dict[str, List[str]]:
        """
        Generate top highlights and concerns from all metrics.
        
        Returns:
            Dictionary with 'highlights', 'concerns', and 'actions' lists
        """
        system_prompt = """You are an expert service delivery analyst.
Analyze the metrics and identify the most important highlights, concerns, and recommended actions.

Be specific and actionable. Reference actual numbers."""

        metrics_summary = self._format_metrics_for_prompt(
            case_metrics, incident_metrics, change_metrics, project_metrics
        )
        
        user_prompt = f"""Analyze these metrics and provide:

{metrics_summary}

Respond in JSON format:
{{
    "highlights": ["top 3-5 positive items with specific numbers"],
    "concerns": ["top 2-3 issues requiring attention"],
    "actions": ["top 2-3 recommended actions for the coming week"]
}}"""

        try:
            response = self._call_llm(system_prompt, user_prompt)
            return json.loads(response)
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Failed to parse highlights/concerns: {e}")
            return {
                "highlights": [],
                "concerns": [],
                "actions": []
            }
    
    def _format_metrics_for_prompt(
        self,
        case_metrics: Optional[CaseMetrics],
        incident_metrics: Optional[IncidentMetrics],
        change_metrics: Optional[ChangeMetrics],
        project_metrics: Optional[ProjectMetrics]
    ) -> str:
        """Format all metrics into a string for LLM prompts."""
        sections = []
        
        if case_metrics:
            sections.append(f"""SALESFORCE CASES:
- Total Cases: {case_metrics.total_cases}
- Open Cases: {case_metrics.open_cases}
- Closed Cases: {case_metrics.closed_cases}
- New This Period: {case_metrics.new_cases_this_period}
- Resolved This Period: {case_metrics.resolved_this_period}
- Escalated: {case_metrics.escalated_count}
- Average Age: {case_metrics.avg_age_days:.1f} days
- By Priority: {case_metrics.by_priority}
- By Account: {case_metrics.by_account}""")
        
        if incident_metrics:
            sections.append(f"""SERVICENOW INCIDENTS:
- Total Incidents: {incident_metrics.total_incidents}
- Open: {incident_metrics.open_incidents}
- Resolved: {incident_metrics.resolved_incidents}
- New This Period: {incident_metrics.new_this_period}
- Resolved This Period: {incident_metrics.resolved_this_period}
- P1 Count: {incident_metrics.p1_count}
- P2 Count: {incident_metrics.p2_count}
- MTTR: {incident_metrics.mttr_hours:.1f} hours
- SLA Compliance: {incident_metrics.sla_compliance_pct:.1f}%
- SLA Breached: {incident_metrics.sla_breached_count}
- SLA At Risk: {incident_metrics.sla_at_risk_count}
- By Priority: {incident_metrics.by_priority}
- By Category: {incident_metrics.by_category}""")
        
        if change_metrics:
            sections.append(f"""SERVICENOW CHANGES:
- Total Changes: {change_metrics.total_changes}
- Completed: {change_metrics.completed_changes}
- Pending: {change_metrics.pending_changes}
- Scheduled This Period: {change_metrics.scheduled_this_period}
- Emergency Changes: {change_metrics.emergency_count}
- Failed: {change_metrics.failed_count}
- Success Rate: {change_metrics.success_rate:.1f}%
- By Type: {change_metrics.by_type}
- By Risk: {change_metrics.by_risk}""")
        
        if project_metrics:
            sections.append(f"""PROJECT/TASKS:
- Total Tasks: {project_metrics.total_tasks}
- Completed: {project_metrics.completed_tasks}
- In Progress: {project_metrics.in_progress_tasks}
- Overdue: {project_metrics.overdue_tasks}
- On Track: {project_metrics.on_track_count}
- At Risk: {project_metrics.at_risk_count}
- Avg Completion: {project_metrics.avg_completion_pct:.1f}%
- By Priority: {project_metrics.by_priority}""")
        
        return "\n\n".join(sections) if sections else "No metrics data available."
