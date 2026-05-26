"""Outlook email client using Microsoft Graph API with device-code auth."""

from datetime import datetime, timedelta, timezone
from typing import Any

import msal
import requests

from .config import cfg

GRAPH_BASE = "https://graph.microsoft.com/v1.0"


class OutlookClient:
    """Fetches and sends emails via Microsoft Graph API.

    Uses MSAL device-code flow — no client secret needed.
    On first run, you'll see a URL + code to paste into a browser.
    The token is cached so subsequent runs skip the browser step.
    """

    def __init__(self) -> None:
        self._app = msal.PublicClientApplication(
            client_id=cfg.AZURE_CLIENT_ID,
            authority=f"https://login.microsoftonline.com/{cfg.AZURE_TENANT_ID}",
        )
        self._token: str | None = None

    def _authenticate(self) -> str:
        """Acquire an access token (cached or via device-code flow)."""
        if self._token:
            return self._token

        accounts = self._app.get_accounts()
        result = None

        if accounts:
            result = self._app.acquire_token_silent(
                scopes=cfg.GRAPH_SCOPES, account=accounts[0]
            )

        if not result:
            flow = self._app.initiate_device_flow(scopes=cfg.GRAPH_SCOPES)
            if "user_code" not in flow:
                raise RuntimeError(f"Device flow failed: {flow.get('error_description', 'unknown error')}")

            print("\n┌─────────────────────────────────────────────┐")
            print("│  🔐  Flerken needs Outlook access            │")
            print("│                                               │")
            print(f"│  Open: {flow['verification_uri']:<36} │")
            print(f"│  Code: {flow['user_code']:<36} │")
            print("│                                               │")
            print("│  Waiting for you to sign in...                │")
            print("└─────────────────────────────────────────────┘\n")

            result = self._app.acquire_token_by_device_flow(flow)

        if "access_token" not in result:
            raise RuntimeError(f"Auth failed: {result.get('error_description', 'unknown error')}")

        self._token = result["access_token"]
        return self._token

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._authenticate()}",
            "Content-Type": "application/json",
        }

    def fetch_recent_emails(self, count: int | None = None, hours: int | None = None) -> list[dict[str, Any]]:
        """Fetch recent emails from the inbox.

        Args:
            count: Max emails to return (default: from config).
            hours: Look back this many hours (default: from config).

        Returns:
            List of email dicts with keys: id, subject, from, received,
            body_preview, body, importance, is_read, has_attachments.
        """
        count = count or cfg.EMAIL_SCAN_COUNT
        hours = hours or cfg.LOOKBACK_HOURS

        since = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

        url = (
            f"{GRAPH_BASE}/me/mailFolders/inbox/messages"
            f"?$top={count}"
            f"&$orderby=receivedDateTime desc"
            f"&$filter=receivedDateTime ge {since}"
            f"&$select=id,subject,from,receivedDateTime,bodyPreview,body,"
            f"importance,isRead,hasAttachments"
        )

        resp = requests.get(url, headers=self._headers(), timeout=30)
        resp.raise_for_status()
        data = resp.json()

        emails = []
        for msg in data.get("value", []):
            emails.append({
                "id": msg["id"],
                "subject": msg.get("subject", "(no subject)"),
                "from": msg.get("from", {}).get("emailAddress", {}).get("address", "unknown"),
                "from_name": msg.get("from", {}).get("emailAddress", {}).get("name", ""),
                "received": msg.get("receivedDateTime", ""),
                "body_preview": msg.get("bodyPreview", ""),
                "body": msg.get("body", {}).get("content", ""),
                "importance": msg.get("importance", "normal"),
                "is_read": msg.get("isRead", False),
                "has_attachments": msg.get("hasAttachments", False),
            })

        return emails

    def send_email(self, to: str, subject: str, html_body: str) -> None:
        """Send an email via Microsoft Graph."""
        payload = {
            "message": {
                "subject": subject,
                "body": {"contentType": "HTML", "content": html_body},
                "toRecipients": [
                    {"emailAddress": {"address": to}}
                ],
            },
            "saveToSentItems": "true",
        }

        resp = requests.post(
            f"{GRAPH_BASE}/me/sendMail",
            headers=self._headers(),
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()

    def create_draft(self, to: str, subject: str, html_body: str) -> dict[str, Any]:
        """Create a draft email (human-in-the-loop: review before sending)."""
        payload = {
            "subject": subject,
            "body": {"contentType": "HTML", "content": html_body},
            "toRecipients": [
                {"emailAddress": {"address": to}}
            ],
        }

        resp = requests.post(
            f"{GRAPH_BASE}/me/messages",
            headers=self._headers(),
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()
