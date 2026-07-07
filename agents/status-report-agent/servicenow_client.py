"""ServiceNow API client for Status Report Agent."""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

import requests
from requests.auth import HTTPBasicAuth

from config import Settings
from models import (
    ServiceNowIncident, ServiceNowChange, ServiceNowTask,
    IncidentMetrics, ChangeMetrics, ProjectMetrics, SLAStatus
)

logger = logging.getLogger(__name__)


class ServiceNowClient:
    """Client for interacting with ServiceNow REST API."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.base_url = settings.sn_instance_url.rstrip("/")
        self.auth = HTTPBasicAuth(settings.sn_username, settings.sn_password)
        self._session: Optional[requests.Session] = None
    
    @property
    def session(self) -> requests.Session:
        """Get or create requests session."""
        if self._session is None:
            self._session = requests.Session()
            self._session.auth = self.auth
            self._session.headers.update({
                "Content-Type": "application/json",
                "Accept": "application/json"
            })
        return self._session
    
    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request to ServiceNow API."""
        url = f"{self.base_url}/api/now/{endpoint}"
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"ServiceNow API error: {e}")
            raise
    
    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """Parse ServiceNow datetime string."""
        if not dt_str:
            return None
        try:
            return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            except ValueError:
                return None
    
    def get_incidents(
        self,
        lookback_days: int = 7,
        assignment_group: Optional[str] = None,
        state_filter: Optional[List[str]] = None
    ) -> List[ServiceNowIncident]:
        """
        Fetch incidents from ServiceNow.
        
        Args:
            lookback_days: Number of days to look back
            assignment_group: Optional assignment group to filter by
            state_filter: Optional list of states to include
        
        Returns:
            List of ServiceNowIncident objects
        """
        since_date = (datetime.utcnow() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
        
        query = f"sys_updated_on>={since_date}"
        
        if assignment_group:
            query += f"^assignment_group.name={assignment_group}"
        
        if state_filter:
            states = ",".join(state_filter)
            query += f"^stateIN{states}"
        
        params = {
            "sysparm_query": query,
            "sysparm_limit": 500,
            "sysparm_display_value": "true",
            "sysparm_fields": (
                "sys_id,number,short_description,description,state,priority,"
                "urgency,impact,category,subcategory,assignment_group,assigned_to,"
                "caller_id,opened_at,resolved_at,closed_at,sla_due,business_service,cmdb_ci"
            )
        }
        
        try:
            result = self._get("table/incident", params)
            incidents = []
            
            for record in result.get("result", []):
                incident = ServiceNowIncident(
                    sys_id=record["sys_id"],
                    number=record["number"],
                    short_description=record["short_description"] or "",
                    description=record.get("description"),
                    state=record["state"],
                    priority=record["priority"],
                    urgency=record["urgency"],
                    impact=record["impact"],
                    category=record.get("category"),
                    subcategory=record.get("subcategory"),
                    assignment_group=record.get("assignment_group"),
                    assigned_to=record.get("assigned_to"),
                    caller_id=record.get("caller_id"),
                    opened_at=self._parse_datetime(record["opened_at"]) or datetime.utcnow(),
                    resolved_at=self._parse_datetime(record.get("resolved_at")),
                    closed_at=self._parse_datetime(record.get("closed_at")),
                    sla_due=self._parse_datetime(record.get("sla_due")),
                    business_service=record.get("business_service"),
                    cmdb_ci=record.get("cmdb_ci")
                )
                incidents.append(incident)
            
            logger.info(f"Fetched {len(incidents)} incidents from ServiceNow")
            return incidents
            
        except Exception as e:
            logger.error(f"Failed to fetch incidents: {e}")
            raise
    
    def get_changes(
        self,
        lookback_days: int = 7,
        assignment_group: Optional[str] = None,
        type_filter: Optional[List[str]] = None
    ) -> List[ServiceNowChange]:
        """
        Fetch change requests from ServiceNow.
        
        Args:
            lookback_days: Number of days to look back
            assignment_group: Optional assignment group to filter by
            type_filter: Optional list of change types to include
        
        Returns:
            List of ServiceNowChange objects
        """
        since_date = (datetime.utcnow() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
        
        query = f"sys_updated_on>={since_date}"
        
        if assignment_group:
            query += f"^assignment_group.name={assignment_group}"
        
        if type_filter:
            types = ",".join(type_filter)
            query += f"^typeIN{types}"
        
        params = {
            "sysparm_query": query,
            "sysparm_limit": 200,
            "sysparm_display_value": "true",
            "sysparm_fields": (
                "sys_id,number,short_description,description,state,type,priority,"
                "risk,impact,assignment_group,assigned_to,requested_by,"
                "start_date,end_date,opened_at,closed_at,cmdb_ci"
            )
        }
        
        try:
            result = self._get("table/change_request", params)
            changes = []
            
            for record in result.get("result", []):
                change = ServiceNowChange(
                    sys_id=record["sys_id"],
                    number=record["number"],
                    short_description=record["short_description"] or "",
                    description=record.get("description"),
                    state=record["state"],
                    type=record.get("type", "normal"),
                    priority=record["priority"],
                    risk=record.get("risk", "moderate"),
                    impact=record["impact"],
                    assignment_group=record.get("assignment_group"),
                    assigned_to=record.get("assigned_to"),
                    requested_by=record.get("requested_by"),
                    start_date=self._parse_datetime(record.get("start_date")),
                    end_date=self._parse_datetime(record.get("end_date")),
                    opened_at=self._parse_datetime(record["opened_at"]) or datetime.utcnow(),
                    closed_at=self._parse_datetime(record.get("closed_at")),
                    cmdb_ci=record.get("cmdb_ci")
                )
                changes.append(change)
            
            logger.info(f"Fetched {len(changes)} changes from ServiceNow")
            return changes
            
        except Exception as e:
            logger.error(f"Failed to fetch changes: {e}")
            raise
    
    def get_tasks(
        self,
        lookback_days: int = 14,
        assignment_group: Optional[str] = None,
        state_filter: Optional[List[str]] = None
    ) -> List[ServiceNowTask]:
        """
        Fetch tasks from ServiceNow.
        
        Args:
            lookback_days: Number of days to look back
            assignment_group: Optional assignment group to filter by
            state_filter: Optional list of states to include
        
        Returns:
            List of ServiceNowTask objects
        """
        since_date = (datetime.utcnow() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
        
        query = f"sys_updated_on>={since_date}"
        
        if assignment_group:
            query += f"^assignment_group.name={assignment_group}"
        
        if state_filter:
            states = ",".join(state_filter)
            query += f"^stateIN{states}"
        
        params = {
            "sysparm_query": query,
            "sysparm_limit": 300,
            "sysparm_display_value": "true",
            "sysparm_fields": (
                "sys_id,number,short_description,state,priority,"
                "assignment_group,assigned_to,due_date,opened_at,closed_at,"
                "percent_complete,parent"
            )
        }
        
        try:
            result = self._get("table/sc_task", params)
            tasks = []
            
            for record in result.get("result", []):
                task = ServiceNowTask(
                    sys_id=record["sys_id"],
                    number=record["number"],
                    short_description=record["short_description"] or "",
                    state=record["state"],
                    priority=record["priority"],
                    assignment_group=record.get("assignment_group"),
                    assigned_to=record.get("assigned_to"),
                    due_date=self._parse_datetime(record.get("due_date")),
                    opened_at=self._parse_datetime(record["opened_at"]) or datetime.utcnow(),
                    closed_at=self._parse_datetime(record.get("closed_at")),
                    percent_complete=int(record.get("percent_complete", 0) or 0),
                    parent=record.get("parent")
                )
                tasks.append(task)
            
            logger.info(f"Fetched {len(tasks)} tasks from ServiceNow")
            return tasks
            
        except Exception as e:
            logger.error(f"Failed to fetch tasks: {e}")
            raise
    
    def calculate_incident_metrics(
        self,
        incidents: List[ServiceNowIncident],
        period_start: datetime,
        period_end: datetime
    ) -> IncidentMetrics:
        """
        Calculate aggregated incident metrics.
        
        Args:
            incidents: List of incidents to analyze
            period_start: Start of reporting period
            period_end: End of reporting period
        
        Returns:
            IncidentMetrics with aggregated data
        """
        metrics = IncidentMetrics()
        
        if not incidents:
            return metrics
        
        metrics.total_incidents = len(incidents)
        
        open_states = ["New", "In Progress", "On Hold", "1", "2", "3"]
        resolved_states = ["Resolved", "Closed", "6", "7"]
        
        by_state: Dict[str, int] = {}
        by_priority: Dict[str, int] = {}
        by_category: Dict[str, int] = {}
        
        resolution_times = []
        
        for incident in incidents:
            # State
            state = incident.state
            by_state[state] = by_state.get(state, 0) + 1
            
            if state in open_states:
                metrics.open_incidents += 1
            elif state in resolved_states:
                metrics.resolved_incidents += 1
            
            # Priority
            priority = incident.priority
            by_priority[priority] = by_priority.get(priority, 0) + 1
            
            if priority in ["1", "1 - Critical", "Critical"]:
                metrics.p1_count += 1
            elif priority in ["2", "2 - High", "High"]:
                metrics.p2_count += 1
            
            # Category
            category = incident.category or "Uncategorized"
            by_category[category] = by_category.get(category, 0) + 1
            
            # New this period
            if period_start <= incident.opened_at <= period_end:
                metrics.new_this_period += 1
            
            # Resolved this period
            if incident.resolved_at and period_start <= incident.resolved_at <= period_end:
                metrics.resolved_this_period += 1
                resolution_times.append(incident.age_hours)
            
            # SLA status
            sla = incident.sla_status
            if sla == SLAStatus.MET:
                metrics.sla_met_count += 1
            elif sla == SLAStatus.BREACHED:
                metrics.sla_breached_count += 1
            elif sla == SLAStatus.AT_RISK:
                metrics.sla_at_risk_count += 1
        
        metrics.by_state = by_state
        metrics.by_priority = by_priority
        metrics.by_category = by_category
        
        if resolution_times:
            metrics.avg_resolution_hours = sum(resolution_times) / len(resolution_times)
            metrics.mttr_hours = metrics.avg_resolution_hours
        
        total_sla = metrics.sla_met_count + metrics.sla_breached_count
        if total_sla > 0:
            metrics.sla_compliance_pct = (metrics.sla_met_count / total_sla) * 100
        
        return metrics
    
    def calculate_change_metrics(
        self,
        changes: List[ServiceNowChange],
        period_start: datetime,
        period_end: datetime
    ) -> ChangeMetrics:
        """
        Calculate aggregated change metrics.
        
        Args:
            changes: List of changes to analyze
            period_start: Start of reporting period
            period_end: End of reporting period
        
        Returns:
            ChangeMetrics with aggregated data
        """
        metrics = ChangeMetrics()
        
        if not changes:
            return metrics
        
        metrics.total_changes = len(changes)
        
        completed_states = ["Closed", "Implemented", "Review", "closed", "implement"]
        
        by_type: Dict[str, int] = {}
        by_risk: Dict[str, int] = {}
        
        successful = 0
        failed = 0
        
        for change in changes:
            # Type
            change_type = change.type or "normal"
            by_type[change_type] = by_type.get(change_type, 0) + 1
            
            if change_type.lower() == "emergency":
                metrics.emergency_count += 1
            
            # Risk
            risk = change.risk or "moderate"
            by_risk[risk] = by_risk.get(risk, 0) + 1
            
            # State
            state = change.state.lower() if change.state else ""
            if any(s in state for s in ["closed", "implemented", "complete"]):
                metrics.completed_changes += 1
                if "failed" in state or "unsuccessful" in state:
                    failed += 1
                else:
                    successful += 1
            else:
                metrics.pending_changes += 1
            
            # Scheduled this period
            if change.start_date and period_start <= change.start_date <= period_end:
                metrics.scheduled_this_period += 1
        
        metrics.by_type = by_type
        metrics.by_risk = by_risk
        metrics.failed_count = failed
        
        if successful + failed > 0:
            metrics.success_rate = (successful / (successful + failed)) * 100
        
        return metrics
    
    def calculate_task_metrics(
        self,
        tasks: List[ServiceNowTask],
        period_start: datetime,
        period_end: datetime
    ) -> ProjectMetrics:
        """
        Calculate aggregated task/project metrics.
        
        Args:
            tasks: List of tasks to analyze
            period_start: Start of reporting period
            period_end: End of reporting period
        
        Returns:
            ProjectMetrics with aggregated data
        """
        metrics = ProjectMetrics()
        
        if not tasks:
            return metrics
        
        metrics.total_tasks = len(tasks)
        
        completed_states = ["Closed", "Complete", "Resolved", "closed", "3"]
        in_progress_states = ["Work in Progress", "In Progress", "Active", "2"]
        
        by_priority: Dict[str, int] = {}
        completion_pcts = []
        now = datetime.utcnow()
        
        for task in tasks:
            # Priority
            priority = task.priority
            by_priority[priority] = by_priority.get(priority, 0) + 1
            
            # State
            state = task.state
            if state in completed_states:
                metrics.completed_tasks += 1
            elif state in in_progress_states:
                metrics.in_progress_tasks += 1
            
            # Overdue
            if task.due_date and task.due_date < now and state not in completed_states:
                metrics.overdue_tasks += 1
            
            # Completion percentage
            completion_pcts.append(task.percent_complete)
            
            # On track vs at risk
            if task.due_date:
                if task.due_date < now and state not in completed_states:
                    metrics.at_risk_count += 1
                else:
                    metrics.on_track_count += 1
        
        metrics.by_priority = by_priority
        
        if completion_pcts:
            metrics.avg_completion_pct = sum(completion_pcts) / len(completion_pcts)
        
        return metrics
