"""Webex HITL notifications for high-risk accounts."""

from __future__ import annotations

import logging
from typing import Any, Dict

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
