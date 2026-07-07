"""Collect account data from Helix, Salesforce, and Delivery Tracker."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

import requests

from config import Settings
from models import (
    AccountPeriodData,
    DeliveryTrackerSnapshot,
    HelixData,
    HelixEntitlementRecord,
    HelixMilestoneRecord,
    HelixSLARecord,
    SalesforceData,
)

logger = logging.getLogger(__name__)


class DataCollector:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def collect(self, account: str, quarter: str) -> AccountPeriodData:
        helix = self.fetch_helix_data(account, quarter)
        salesforce = self.fetch_salesforce_data(account, quarter)
        tracker = self.load_delivery_tracker_json(account)
        return AccountPeriodData(
            account=account,
            quarter=quarter,
            helix=helix,
            salesforce=salesforce,
            delivery_tracker=tracker,
        )

    def fetch_helix_data(self, account: str, quarter: str) -> HelixData:
        base = self.settings.helix_base_url.rstrip("/")
        headers = {**self.settings.auth_header, "Accept": "application/json"}
        timeout = self.settings.http_timeout

        milestones: list[HelixMilestoneRecord] = []
        entitlements: list[HelixEntitlementRecord] = []
        sla: Optional[HelixSLARecord] = None

        try:
            ms_url = f"{base}/accounts/{account}/milestones"
            resp = requests.get(ms_url, headers=headers, timeout=timeout)
            if resp.ok:
                for item in resp.json().get("milestones", resp.json().get("data", [])):
                    milestones.append(
                        HelixMilestoneRecord(
                            name=item.get("name", "Milestone"),
                            completion_pct=float(item.get("completion_pct", 0)),
                            on_time=item.get("status") != "overdue",
                        )
                    )
        except requests.RequestException as exc:
            logger.warning("Helix milestones unavailable: %s", exc)

        try:
            ent_url = f"{base}/accounts/{account}/entitlements"
            resp = requests.get(ent_url, headers=headers, timeout=timeout)
            if resp.ok:
                for item in resp.json().get("entitlements", resp.json().get("data", [])):
                    entitlements.append(
                        HelixEntitlementRecord(
                            name=item.get("name", "Entitlement"),
                            utilized_pct=float(item.get("utilized_pct", 0)),
                            total_units=float(item.get("total_units", 0)),
                        )
                    )
        except requests.RequestException as exc:
            logger.warning("Helix entitlements unavailable: %s", exc)

        try:
            sla_url = f"{base}/accounts/{account}/sla"
            resp = requests.get(
                sla_url,
                headers=headers,
                timeout=timeout,
                params={"quarter": quarter},
            )
            if resp.ok:
                payload = resp.json()
                sla = HelixSLARecord(
                    target_pct=float(payload.get("target_pct", 95)),
                    actual_pct=float(payload.get("actual_pct", 0)),
                )
        except requests.RequestException as exc:
            logger.warning("Helix SLA unavailable: %s", exc)

        return HelixData(
            account=account,
            milestones=milestones,
            entitlements=entitlements,
            sla=sla,
            source="helix",
        )

    def fetch_salesforce_data(self, account: str, quarter: str) -> SalesforceData:
        if not self.settings.salesforce_mcp_token:
            logger.warning("SALESFORCE_MCP_TOKEN not set — Salesforce data unavailable")
            return SalesforceData(
                account=account,
                quarter=quarter,
                cases=[],
                csat_score=None,
                source="stub",
            )
        # Real Salesforce MCP integration deferred until ops access is granted.
        return SalesforceData(
            account=account,
            quarter=quarter,
            cases=[],
            csat_score=None,
            source="salesforce_mcp_pending",
        )

    def load_delivery_tracker_json(self, account: str) -> Optional[DeliveryTrackerSnapshot]:
        tracker_dir = self.settings.delivery_tracker_dir
        if not tracker_dir.is_dir():
            return None

        candidates = sorted(
            tracker_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        for path in candidates:
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                for row in payload.get("accounts", []):
                    name = row.get("account_name", "")
                    if account.lower() in name.lower() or name.lower() in account.lower():
                        return DeliveryTrackerSnapshot(
                            account_name=name,
                            total_open=int(row.get("total_open", 0)),
                            overdue=int(row.get("overdue", 0)),
                            sla_actual_pct=row.get("sla_actual_pct"),
                            milestone_completion_pct=row.get("milestone_completion_pct"),
                        )
            except (json.JSONDecodeError, OSError) as exc:
                logger.warning("Failed to read tracker file %s: %s", path, exc)
        return None
