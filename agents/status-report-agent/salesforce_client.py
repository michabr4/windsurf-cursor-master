"""Salesforce API client for Status Report Agent."""

import logging
import re
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple

from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceError

from config import Settings
from models import (
    SalesforceCase, SalesforceOpportunity, SalesforceAccount,
    CaseMetrics
)

logger = logging.getLogger(__name__)

_SF_ID_RE = re.compile(r"^[a-zA-Z0-9]{15}([a-zA-Z0-9]{3})?$")


def _soql_string_literal(value: str) -> str:
    """Single-quote a value for SOQL (escape ' as '')."""
    return "'" + value.replace("'", "''") + "'"


class SalesforceClient:
    """Client for interacting with Salesforce API."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self._sf: Optional[Salesforce] = None
    
    def _connect(self) -> Salesforce:
        """Establish connection to Salesforce."""
        if self._sf is not None:
            return self._sf
        
        try:
            self._sf = Salesforce(
                username=self.settings.sf_username,
                password=self.settings.sf_password,
                security_token=self.settings.sf_security_token,
                instance_url=self.settings.sf_instance_url,
                client_id=self.settings.sf_client_id or "StatusReportAgent"
            )
            logger.info("Connected to Salesforce")
            return self._sf
        except SalesforceError as e:
            logger.error(f"Salesforce connection failed: {e}")
            raise
    
    @property
    def sf(self) -> Salesforce:
        """Get Salesforce connection (lazy initialization)."""
        return self._connect()

    def resolve_account_filter(self, raw: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Map CLI/env account filter to a Salesforce Account Id and display name.

        Accepts either a 15/18-character Account Id or a human-readable name
        (exact match first, then single-word contains via LIKE).
        """
        text = (raw or "").strip()
        if not text:
            return None, None

        if _SF_ID_RE.fullmatch(text):
            acct = self.get_account(text)
            if acct:
                return acct.id, acct.name
            logger.warning("No Account found for Id prefix=%s…", text[:6])
            return None, None

        exact_q = (
            "SELECT Id, Name FROM Account WHERE Name = "
            + _soql_string_literal(text)
            + " LIMIT 5"
        )
        try:
            res = self.sf.query_all(exact_q)
            recs = res.get("records", [])
            if len(recs) == 1:
                r = recs[0]
                return r["Id"], r["Name"]
            if len(recs) > 1:
                logger.warning(
                    "Multiple Salesforce accounts named %r; narrow the name or pass Account Id",
                    text,
                )
                r = recs[0]
                return r["Id"], r["Name"]
        except SalesforceError as e:
            logger.error("Account exact lookup failed: %s", e)
            return None, None

        like_q = (
            "SELECT Id, Name FROM Account WHERE Name LIKE "
            + _soql_string_literal("%" + text + "%")
            + " ORDER BY Name ASC LIMIT 10"
        )
        try:
            res = self.sf.query_all(like_q)
            recs = res.get("records", [])
            if not recs:
                logger.warning("No Salesforce account matched filter %r", text)
                return None, None
            if len(recs) > 1:
                names = [r["Name"] for r in recs[:5]]
                logger.warning(
                    "Ambiguous account filter %r; matches include %s — using first",
                    text,
                    names,
                )
            r = recs[0]
            return r["Id"], r["Name"]
        except SalesforceError as e:
            logger.error("Account name lookup failed: %s", e)
            return None, None

    def get_cases(
        self,
        lookback_days: int = 7,
        account_id: Optional[str] = None,
        status_filter: Optional[List[str]] = None
    ) -> List[SalesforceCase]:
        """
        Fetch cases from Salesforce.
        
        Args:
            lookback_days: Number of days to look back for cases
            account_id: Optional account ID to filter by
            status_filter: Optional list of statuses to include
        
        Returns:
            List of SalesforceCase objects
        """
        since_date = (datetime.utcnow() - timedelta(days=lookback_days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        query = f"""
            SELECT Id, CaseNumber, Subject, Description, Status, Priority,
                   AccountId, Account.Name, Contact.Name, Owner.Name,
                   CreatedDate, ClosedDate, LastModifiedDate,
                   Type, Origin, Reason, IsEscalated
            FROM Case
            WHERE LastModifiedDate >= {since_date}
        """
        
        if account_id:
            safe_id = account_id.replace("'", "''")
            query += f" AND AccountId = '{safe_id}'"
        
        if status_filter:
            statuses = "', '".join(s.replace("'", "''") for s in status_filter)
            query += f" AND Status IN ('{statuses}')"
        
        query += " ORDER BY CreatedDate DESC LIMIT 500"
        
        try:
            result = self.sf.query_all(query)
            cases = []
            
            for record in result.get("records", []):
                case = SalesforceCase(
                    id=record["Id"],
                    case_number=record["CaseNumber"],
                    subject=record["Subject"] or "",
                    description=record.get("Description"),
                    status=record["Status"],
                    priority=record["Priority"] or "Medium",
                    account_id=record.get("AccountId"),
                    account_name=record.get("Account", {}).get("Name") if record.get("Account") else None,
                    contact_name=record.get("Contact", {}).get("Name") if record.get("Contact") else None,
                    owner_name=record.get("Owner", {}).get("Name") if record.get("Owner") else None,
                    created_date=datetime.fromisoformat(record["CreatedDate"].replace("Z", "+00:00")),
                    closed_date=datetime.fromisoformat(record["ClosedDate"].replace("Z", "+00:00")) if record.get("ClosedDate") else None,
                    last_modified_date=datetime.fromisoformat(record["LastModifiedDate"].replace("Z", "+00:00")),
                    case_type=record.get("Type"),
                    origin=record.get("Origin"),
                    reason=record.get("Reason"),
                    is_escalated=record.get("IsEscalated", False)
                )
                cases.append(case)
            
            logger.info(f"Fetched {len(cases)} cases from Salesforce")
            return cases
            
        except SalesforceError as e:
            logger.error(f"Failed to fetch cases: {e}")
            raise
    
    def get_opportunities(
        self,
        lookback_days: int = 30,
        account_id: Optional[str] = None,
        stage_filter: Optional[List[str]] = None
    ) -> List[SalesforceOpportunity]:
        """
        Fetch opportunities from Salesforce.
        
        Args:
            lookback_days: Number of days to look back
            account_id: Optional account ID to filter by
            stage_filter: Optional list of stages to include
        
        Returns:
            List of SalesforceOpportunity objects
        """
        since_date = (datetime.utcnow() - timedelta(days=lookback_days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        query = f"""
            SELECT Id, Name, AccountId, Account.Name, StageName, Amount,
                   CloseDate, Probability, Owner.Name, CreatedDate,
                   LastModifiedDate, FiscalQuarter, FiscalYear
            FROM Opportunity
            WHERE LastModifiedDate >= {since_date}
        """
        
        if account_id:
            safe_id = account_id.replace("'", "''")
            query += f" AND AccountId = '{safe_id}'"
        
        if stage_filter:
            stages = "', '".join(s.replace("'", "''") for s in stage_filter)
            query += f" AND StageName IN ('{stages}')"
        
        query += " ORDER BY CloseDate ASC LIMIT 200"
        
        try:
            result = self.sf.query_all(query)
            opportunities = []
            
            for record in result.get("records", []):
                opp = SalesforceOpportunity(
                    id=record["Id"],
                    name=record["Name"],
                    account_id=record.get("AccountId"),
                    account_name=record.get("Account", {}).get("Name") if record.get("Account") else None,
                    stage=record["StageName"],
                    amount=record.get("Amount"),
                    close_date=datetime.strptime(record["CloseDate"], "%Y-%m-%d").date() if record.get("CloseDate") else None,
                    probability=record.get("Probability"),
                    owner_name=record.get("Owner", {}).get("Name") if record.get("Owner") else None,
                    created_date=datetime.fromisoformat(record["CreatedDate"].replace("Z", "+00:00")),
                    last_modified_date=datetime.fromisoformat(record["LastModifiedDate"].replace("Z", "+00:00")),
                    fiscal_quarter=record.get("FiscalQuarter"),
                    fiscal_year=record.get("FiscalYear")
                )
                opportunities.append(opp)
            
            logger.info(f"Fetched {len(opportunities)} opportunities from Salesforce")
            return opportunities
            
        except SalesforceError as e:
            logger.error(f"Failed to fetch opportunities: {e}")
            raise
    
    def get_account(self, account_id: str) -> Optional[SalesforceAccount]:
        """Fetch a single account by ID."""
        safe_id = account_id.replace("'", "''")
        query = f"""
            SELECT Id, Name, AccountNumber, Industry, Type, Owner.Name,
                   AnnualRevenue
            FROM Account
            WHERE Id = '{safe_id}'
        """
        
        try:
            result = self.sf.query(query)
            records = result.get("records", [])
            
            if not records:
                return None
            
            record = records[0]
            return SalesforceAccount(
                id=record["Id"],
                name=record["Name"],
                account_number=record.get("AccountNumber"),
                industry=record.get("Industry"),
                type=record.get("Type"),
                owner_name=record.get("Owner", {}).get("Name") if record.get("Owner") else None,
                annual_revenue=record.get("AnnualRevenue")
            )
            
        except SalesforceError as e:
            logger.error(f"Failed to fetch account {account_id}: {e}")
            return None
    
    def get_accounts_by_name(self, name_pattern: str) -> List[SalesforceAccount]:
        """Search accounts by name pattern."""
        esc = name_pattern.replace("'", "''")
        query = f"""
            SELECT Id, Name, AccountNumber, Industry, Type, Owner.Name,
                   AnnualRevenue
            FROM Account
            WHERE Name LIKE '%{esc}%'
            LIMIT 50
        """
        
        try:
            result = self.sf.query_all(query)
            accounts = []
            
            for record in result.get("records", []):
                account = SalesforceAccount(
                    id=record["Id"],
                    name=record["Name"],
                    account_number=record.get("AccountNumber"),
                    industry=record.get("Industry"),
                    type=record.get("Type"),
                    owner_name=record.get("Owner", {}).get("Name") if record.get("Owner") else None,
                    annual_revenue=record.get("AnnualRevenue")
                )
                accounts.append(account)
            
            return accounts
            
        except SalesforceError as e:
            logger.error(f"Failed to search accounts: {e}")
            return []
    
    def calculate_case_metrics(
        self,
        cases: List[SalesforceCase],
        period_start: datetime,
        period_end: datetime
    ) -> CaseMetrics:
        """
        Calculate aggregated case metrics.
        
        Args:
            cases: List of cases to analyze
            period_start: Start of reporting period
            period_end: End of reporting period
        
        Returns:
            CaseMetrics with aggregated data
        """
        metrics = CaseMetrics()
        
        if not cases:
            return metrics
        
        metrics.total_cases = len(cases)
        
        # Status counts
        open_statuses = ["New", "Open", "In Progress", "Pending", "Escalated"]
        closed_statuses = ["Closed", "Resolved"]
        
        by_status: Dict[str, int] = {}
        by_priority: Dict[str, int] = {}
        by_account: Dict[str, int] = {}
        
        ages = []
        
        for case in cases:
            # Status
            status = case.status
            by_status[status] = by_status.get(status, 0) + 1
            
            if status in open_statuses:
                metrics.open_cases += 1
            elif status in closed_statuses:
                metrics.closed_cases += 1
            
            # Priority
            priority = case.priority
            by_priority[priority] = by_priority.get(priority, 0) + 1
            
            # Account
            account = case.account_name or "Unknown"
            by_account[account] = by_account.get(account, 0) + 1
            
            # New this period
            if period_start <= case.created_date <= period_end:
                metrics.new_cases_this_period += 1
            
            # Resolved this period
            if case.closed_date and period_start <= case.closed_date <= period_end:
                metrics.resolved_this_period += 1
            
            # Age
            ages.append(case.age_days)
            
            # Escalated
            if case.is_escalated:
                metrics.escalated_count += 1
        
        metrics.by_status = by_status
        metrics.by_priority = by_priority
        metrics.by_account = by_account
        
        if ages:
            metrics.avg_age_days = sum(ages) / len(ages)
            metrics.oldest_case_days = max(ages)
        
        return metrics
