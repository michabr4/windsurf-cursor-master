"""Outlook email reader that extracts prioritized action items.

This starter uses Microsoft Graph delegated login (device code flow) so users
can sign in interactively without storing a client secret.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import msal
import requests
from dotenv import load_dotenv


load_dotenv()


GRAPH_SCOPES = ["Mail.Read", "User.Read"]
GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"


@dataclass
class ActionItem:
    subject: str
    sender: str
    received_at: str
    due_date: Optional[str]
    priority_score: int
    priority_label: str
    reason: str
    web_link: str


class OutlookActionItemClient:
    def __init__(self) -> None:
        self.tenant_id = os.getenv("MS_TENANT_ID") or os.getenv("MS_AUTHORITY_TENANT", "organizations")
        self.client_id = os.getenv("MS_CLIENT_ID")
        self.mailbox_user = os.getenv("MS_MAILBOX_USER")
        self.max_messages = int(os.getenv("MS_OUTLOOK_MAX_MESSAGES", "40"))
        self._access_token: Optional[str] = None

    def _require(self, value: Optional[str], label: str) -> str:
        if not value:
            raise ValueError(f"Missing required environment variable: {label}")
        return value

    def _get_access_token(self) -> str:
        if self._access_token:
            return self._access_token

        tenant_id = self._require(self.tenant_id, "MS_TENANT_ID")
        client_id = self._require(self.client_id, "MS_CLIENT_ID")
        authority = f"https://login.microsoftonline.com/{tenant_id}"

        app = msal.PublicClientApplication(client_id=client_id, authority=authority)
        accounts = app.get_accounts()
        result: Dict[str, Any] = {}
        if accounts:
            result = app.acquire_token_silent(GRAPH_SCOPES, account=accounts[0]) or {}

        if "access_token" not in result:
            flow = app.initiate_device_flow(scopes=GRAPH_SCOPES)
            if "user_code" not in flow:
                raise ValueError("Failed to start Microsoft device login flow.")

            print(flow.get("message", "Sign in required."))
            result = app.acquire_token_by_device_flow(flow)

        access_token = result.get("access_token")
        if not access_token:
            error_description = result.get("error_description", "unknown authentication error")
            raise ValueError(f"Microsoft login failed: {error_description}")

        self._access_token = access_token
        return access_token

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json",
        }

    def list_recent_messages(self) -> List[Dict[str, Any]]:
        mailbox_user = (self.mailbox_user or "").strip()
        # Keep message payload lean for predictable starter behavior.
        endpoint = (
            f"{GRAPH_BASE_URL}/users/{mailbox_user}/mailFolders/inbox/messages"
            if mailbox_user
            else f"{GRAPH_BASE_URL}/me/mailFolders/inbox/messages"
        )
        query = (
            f"{endpoint}?$top={self.max_messages}"
            "&$orderby=receivedDateTime desc"
            "&$select=subject,from,importance,bodyPreview,receivedDateTime,webLink"
        )
        response = requests.get(query, headers=self._headers(), timeout=60)
        response.raise_for_status()
        return response.json().get("value", [])

    @staticmethod
    def _parse_due_date(text: str, now_utc: datetime) -> Optional[datetime]:
        normalized = text.lower()
        if "due today" in normalized:
            return now_utc.replace(hour=23, minute=59, second=0, microsecond=0)
        if "due tomorrow" in normalized:
            tomorrow = now_utc + timedelta(days=1)
            return tomorrow.replace(hour=23, minute=59, second=0, microsecond=0)

        for match in re.findall(r"\b(20\d{2}-\d{2}-\d{2})\b", text):
            try:
                return datetime.strptime(match, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                continue

        for mm, dd, yyyy in re.findall(r"\b(0?[1-9]|1[0-2])[/-](0?[1-9]|[12]\d|3[01])(?:[/-](20\d{2}))?\b", text):
            year = int(yyyy) if yyyy else now_utc.year
            try:
                return datetime(year, int(mm), int(dd), tzinfo=timezone.utc)
            except ValueError:
                continue

        return None

    @staticmethod
    def _priority_label(score: int) -> str:
        if score >= 90:
            return "critical"
        if score >= 70:
            return "high"
        if score >= 45:
            return "medium"
        return "low"

    def _score_message(self, message: Dict[str, Any], due_date: Optional[datetime], now_utc: datetime) -> tuple[int, str]:
        subject = (message.get("subject") or "").lower()
        body_preview = (message.get("bodyPreview") or "").lower()
        text = f"{subject}\n{body_preview}"
        importance = (message.get("importance") or "").lower()

        score = 15
        reasons: List[str] = []

        action_markers = ("action", "todo", "to do", "please", "need to", "follow up", "deadline", "due")
        if any(marker in text for marker in action_markers):
            score += 20
            reasons.append("contains action language")

        if importance == "high":
            score += 20
            reasons.append("marked high importance")

        urgent_markers = ("urgent", "asap", "critical", "blocker", "p1", "sev1", "immediately")
        if any(marker in text for marker in urgent_markers):
            score += 30
            reasons.append("contains urgency keywords")

        if due_date:
            days_left = (due_date.date() - now_utc.date()).days
            if days_left < 0:
                score += 35
                reasons.append("past due date")
            elif days_left == 0:
                score += 30
                reasons.append("due today")
            elif days_left <= 2:
                score += 20
                reasons.append("due very soon")
            elif days_left <= 7:
                score += 10
                reasons.append("due this week")

        final_score = min(score, 100)
        reason_text = ", ".join(reasons) if reasons else "general task signal"
        return final_score, reason_text

    def build_action_list(self) -> List[ActionItem]:
        now_utc = datetime.now(timezone.utc)
        messages = self.list_recent_messages()
        items: List[ActionItem] = []

        for message in messages:
            subject = (message.get("subject") or "").strip()
            body_preview = message.get("bodyPreview") or ""
            sender = (
                message.get("from", {})
                .get("emailAddress", {})
                .get("address", "unknown sender")
            )
            received = message.get("receivedDateTime", "")
            web_link = message.get("webLink", "")
            scan_text = f"{subject}\n{body_preview}"
            due_dt = self._parse_due_date(scan_text, now_utc)
            score, reason = self._score_message(message, due_dt, now_utc)

            # Keep low-signal messages out of the action list.
            if score < 40:
                continue

            items.append(
                ActionItem(
                    subject=subject or "(no subject)",
                    sender=sender,
                    received_at=received,
                    due_date=due_dt.date().isoformat() if due_dt else None,
                    priority_score=score,
                    priority_label=self._priority_label(score),
                    reason=reason,
                    web_link=web_link,
                )
            )

        items.sort(
            key=lambda item: (
                -item.priority_score,
                item.due_date is None,
                item.due_date or "9999-12-31",
                item.received_at,
            )
        )
        return items
