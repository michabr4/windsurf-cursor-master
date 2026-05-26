"""AGT-001: Outlook Email Chief-of-Staff Agent (Read-Only Mode)

This agent builds on the existing OutlookActionItemClient to provide:
1. Daily inbox synthesis (structured digest)
2. Decision extraction (items requiring your decision)
3. Action item tracking (commitments and follow-ups)
4. Urgency flagging (prioritized "handle first" list)

All capabilities are read-only. No emails are modified, deleted, or sent.

Feeds into:
- CHAIN-001 (Case Insight) — Step 1: email summarization
- CHAIN-002 (Governance Pulse) — Step 2: digest formatting
- CHAIN-003 (Weekly Readout) — Step 3: executive narrative
- CHAIN-004 (Case Lifecycle) — Steps 1 + 6
- CHAIN-005 (Meeting-to-Action) — Steps 3 + 5
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

from src.outlook_action_items import ActionItem, OutlookActionItemClient

load_dotenv()


@dataclass
class EmailClassification:
    """Classification of a single email message."""
    subject: str
    sender: str
    received_at: str
    category: str  # action_required | decision_needed | fyi | follow_up | delegatable
    urgency: str   # critical | high | medium | low
    summary: str
    key_asks: List[str]
    due_date: Optional[str]
    web_link: str


@dataclass
class DailyDigest:
    """Structured daily inbox synthesis."""
    generated_at: str
    total_emails_scanned: int
    handle_first: List[EmailClassification]
    decisions_needed: List[EmailClassification]
    action_required: List[EmailClassification]
    follow_ups: List[EmailClassification]
    fyi_items: List[EmailClassification]
    delegatable: List[EmailClassification]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, default=str)

    def to_text_summary(self) -> str:
        """Plain-text summary for quick reading."""
        lines = [
            f"=== Daily Inbox Digest — {self.generated_at} ===",
            f"Emails scanned: {self.total_emails_scanned}",
            "",
        ]

        if self.handle_first:
            lines.append(f"HANDLE FIRST ({len(self.handle_first)}):")
            for item in self.handle_first:
                lines.append(f"  [{item.urgency.upper()}] {item.subject}")
                lines.append(f"    From: {item.sender}")
                if item.key_asks:
                    lines.append(f"    Asks: {'; '.join(item.key_asks)}")
                lines.append("")

        if self.decisions_needed:
            lines.append(f"DECISIONS NEEDED ({len(self.decisions_needed)}):")
            for item in self.decisions_needed:
                lines.append(f"  {item.subject}")
                lines.append(f"    From: {item.sender}")
                lines.append(f"    Summary: {item.summary}")
                lines.append("")

        if self.action_required:
            lines.append(f"ACTION REQUIRED ({len(self.action_required)}):")
            for item in self.action_required:
                due = item.due_date or "no due date"
                lines.append(f"  {item.subject} (due: {due})")
                lines.append(f"    From: {item.sender}")
                lines.append("")

        if self.follow_ups:
            lines.append(f"FOLLOW-UPS ({len(self.follow_ups)}):")
            for item in self.follow_ups:
                lines.append(f"  {item.subject} — {item.sender}")
            lines.append("")

        fyi_count = len(self.fyi_items)
        delegatable_count = len(self.delegatable)
        if fyi_count or delegatable_count:
            lines.append(f"FYI: {fyi_count} | Delegatable: {delegatable_count}")
            lines.append("")

        lines.append("=== End of Digest ===")
        return "\n".join(lines)


@dataclass
class ChainOutput:
    """Standardized output for orchestration chains."""
    agent_id: str
    chain_id: Optional[str]
    step_number: Optional[int]
    timestamp: str
    status: str  # success | partial | error
    data: Dict[str, Any]
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EmailChiefOfStaff:
    """AGT-001: Outlook Email Chief-of-Staff Agent.

    Read-only mode. Summarizes, classifies, and prioritizes inbox email.
    """

    AGENT_ID = "AGT-001"

    # Keywords for classification
    DECISION_KEYWORDS = (
        "approve", "decision", "sign off", "sign-off", "go/no-go",
        "choose", "select", "confirm", "authorize", "green light",
        "your call", "your decision", "need your input",
    )
    FOLLOW_UP_KEYWORDS = (
        "follow up", "following up", "circling back", "checking in",
        "any update", "status update", "reminder", "gentle reminder",
    )
    DELEGATION_KEYWORDS = (
        "fyi", "for your information", "no action needed",
        "just sharing", "for awareness", "for reference",
    )

    def __init__(self) -> None:
        self._client = OutlookActionItemClient()

    def _classify_email(self, message: Dict[str, Any], action_item: Optional[ActionItem]) -> EmailClassification:
        """Classify a single email into a category and urgency level."""
        subject = (message.get("subject") or "").strip()
        body_preview = (message.get("bodyPreview") or "").strip()
        sender = (
            message.get("from", {})
            .get("emailAddress", {})
            .get("address", "unknown")
        )
        received = message.get("receivedDateTime", "")
        web_link = message.get("webLink", "")
        text_lower = f"{subject} {body_preview}".lower()

        # Determine category
        category = "fyi"
        if any(kw in text_lower for kw in self.DECISION_KEYWORDS):
            category = "decision_needed"
        elif action_item and action_item.priority_score >= 40:
            category = "action_required"
        elif any(kw in text_lower for kw in self.FOLLOW_UP_KEYWORDS):
            category = "follow_up"
        elif any(kw in text_lower for kw in self.DELEGATION_KEYWORDS):
            category = "delegatable"

        # Determine urgency from action item score or fallback
        if action_item:
            urgency = action_item.priority_label
        else:
            urgency = "low"
            importance = (message.get("importance") or "").lower()
            if importance == "high":
                urgency = "high"

        # Extract key asks (simple heuristic)
        key_asks = []
        ask_markers = ("please ", "can you ", "could you ", "need you to ", "action: ", "todo: ", "to do: ")
        for line in body_preview.split("."):
            line_lower = line.strip().lower()
            if any(line_lower.startswith(m) or f" {m}" in line_lower for m in ask_markers):
                cleaned = line.strip()
                if cleaned and len(cleaned) > 10:
                    key_asks.append(cleaned[:200])

        # Build summary
        summary = body_preview[:300] if body_preview else "(no preview available)"

        return EmailClassification(
            subject=subject or "(no subject)",
            sender=sender,
            received_at=received,
            category=category,
            urgency=urgency,
            summary=summary,
            key_asks=key_asks[:5],
            due_date=action_item.due_date if action_item else None,
            web_link=web_link,
        )

    def generate_daily_digest(self) -> DailyDigest:
        """Generate a structured daily inbox digest.

        This is the primary output of AGT-001 in read-only mode.
        """
        now_utc = datetime.now(timezone.utc)
        messages = self._client.list_recent_messages()
        action_items = self._client.build_action_list()

        # Build lookup from subject+sender to action item
        action_map: Dict[str, ActionItem] = {}
        for ai in action_items:
            key = f"{ai.subject}|{ai.sender}"
            action_map[key] = ai

        # Classify all messages
        classifications: List[EmailClassification] = []
        for msg in messages:
            subject = (msg.get("subject") or "").strip()
            sender = (
                msg.get("from", {})
                .get("emailAddress", {})
                .get("address", "unknown")
            )
            key = f"{subject}|{sender}"
            action_item = action_map.get(key)
            classification = self._classify_email(msg, action_item)
            classifications.append(classification)

        # Sort into buckets
        handle_first = [c for c in classifications if c.urgency in ("critical", "high") and c.category in ("action_required", "decision_needed")]
        decisions = [c for c in classifications if c.category == "decision_needed" and c not in handle_first]
        actions = [c for c in classifications if c.category == "action_required" and c not in handle_first]
        follow_ups = [c for c in classifications if c.category == "follow_up"]
        fyi = [c for c in classifications if c.category == "fyi"]
        delegatable = [c for c in classifications if c.category == "delegatable"]

        # Cap handle_first to top 5
        handle_first = handle_first[:5]

        return DailyDigest(
            generated_at=now_utc.isoformat(),
            total_emails_scanned=len(messages),
            handle_first=handle_first,
            decisions_needed=decisions,
            action_required=actions,
            follow_ups=follow_ups,
            fyi_items=fyi,
            delegatable=delegatable,
        )

    def summarize_for_chain(self, chain_id: str, step_number: int) -> ChainOutput:
        """Produce a chain-compatible output for orchestration.

        Used by CHAIN-001 (step 1), CHAIN-002 (step 2), CHAIN-003 (step 3),
        CHAIN-004 (step 1), CHAIN-005 (step 3).
        """
        try:
            digest = self.generate_daily_digest()
            return ChainOutput(
                agent_id=self.AGENT_ID,
                chain_id=chain_id,
                step_number=step_number,
                timestamp=datetime.now(timezone.utc).isoformat(),
                status="success",
                data=digest.to_dict(),
            )
        except Exception as exc:
            return ChainOutput(
                agent_id=self.AGENT_ID,
                chain_id=chain_id,
                step_number=step_number,
                timestamp=datetime.now(timezone.utc).isoformat(),
                status="error",
                data={},
                error_message=str(exc),
            )
