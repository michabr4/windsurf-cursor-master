"""Webex HITL notifications for high-risk accounts."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

import requests

from config import Settings
from models import AccountRisk

logger = logging.getLogger(__name__)

WEBEX_MESSAGES_URL = "https://webexapis.com/v1/messages"


class WebexNotifier:
    """Send adaptive-card style HITL prompts for HIGH risk accounts."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def send_high_risk_card(self, risk: AccountRisk) -> bool:
        """Post a Webex message with four HITL action buttons."""
        if self.settings.dry_run:
            logger.info("Dry-run: skipping Webex card for %s", risk.account_name)
            return False

        payload = {
            "roomId": self.settings.webex_room_id,
            "text": f"HIGH risk: {risk.account_name}",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": self._build_card(risk),
                }
            ],
        }
        resp = requests.post(
            WEBEX_MESSAGES_URL,
            headers={"Authorization": f"Bearer {self.settings.webex_bot_token}"},
            json=payload,
            timeout=10,
        )
        resp.raise_for_status()
        logger.info("Webex HITL card sent for %s", risk.account_name)
        return True

    def _build_card(self, risk: AccountRisk) -> Dict[str, Any]:
        return {
            "type": "AdaptiveCard",
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.2",
            "body": [
                {
                    "type": "TextBlock",
                    "text": f"HIGH RISK — {risk.account_name}",
                    "weight": "Bolder",
                    "size": "Medium",
                },
                {"type": "TextBlock", "text": risk.summary, "wrap": True},
                {
                    "type": "TextBlock",
                    "text": f"Recommended: {risk.recommended_action}",
                    "wrap": True,
                    "isSubtle": True,
                },
            ],
            "actions": [
                {
                    "type": "Action.Submit",
                    "title": "Escalate Now",
                    "data": {"action": "escalate", "account_id": risk.account_id},
                },
                {
                    "type": "Action.Submit",
                    "title": "Schedule Call",
                    "data": {"action": "schedule_call", "account_id": risk.account_id},
                },
                {
                    "type": "Action.Submit",
                    "title": "Snooze 48h",
                    "data": {"action": "snooze", "account_id": risk.account_id},
                },
                {
                    "type": "Action.Submit",
                    "title": "Dismiss",
                    "data": {"action": "dismiss", "account_id": risk.account_id},
                },
            ],
        }

    def send_medium_risk_summary(self, risks: List[AccountRisk]) -> bool:
        """Post a single markdown summary of all MEDIUM risk accounts.

        Returns True if the message was sent, False if skipped (dry-run or
        empty list).
        """
        if not risks:
            return False
        if self.settings.dry_run:
            logger.info(
                "Dry-run: skipping medium-risk summary (%d accounts)", len(risks)
            )
            return False

        lines = ["**⚠️ MEDIUM RISK — Schedule check-ins within 48h**", ""]
        for risk in risks:
            rules = ", ".join(risk.triggered_rules) or "no specific rules"
            lines.append(f"- **{risk.account_name}** — {rules}")
        lines.append("")
        lines.append(
            f"_Total: {len(risks)} account(s). Review the full sentinel report for details._"
        )

        payload = {
            "roomId": self.settings.webex_room_id,
            "markdown": "\n".join(lines),
        }
        resp = requests.post(
            WEBEX_MESSAGES_URL,
            headers={"Authorization": f"Bearer {self.settings.webex_bot_token}"},
            json=payload,
            timeout=10,
        )
        resp.raise_for_status()
        logger.info("Webex medium-risk summary sent for %d accounts", len(risks))
        return True
