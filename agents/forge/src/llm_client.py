"""LLM client — Ollama (local) for email triage and draft replies.

Uses the OpenAI-compatible API that Ollama exposes at localhost:11434/v1.
Also works with OpenAI/Azure OpenAI if you change LLM_BASE_URL in .env.
"""

import json
import re
from typing import Any

from openai import OpenAI

from .config import cfg

TRIAGE_SYSTEM_PROMPT = """You are Forge, a personal AI email assistant. Your job is to triage emails and create a daily digest.

You MUST respond with ONLY a valid JSON object (no markdown, no explanation outside the JSON). The JSON must have these fields:
- "category": one of "urgent", "action_required", "fyi", "low_priority", "spam"
- "summary": 1-2 sentence summary of the email content
- "action_items": list of specific actions needed (empty list if none)
- "needs_reply": boolean — does this email require a response?
- "draft_reply": if needs_reply is true, a professional draft reply (otherwise null)
- "reasoning": brief explanation of why you categorized it this way
- "tone": one of "urgent", "frustrated", "escalating", "formal", "friendly", "neutral", "automated", "suspicious"
- "urgency_score": integer 1-10 (1=can wait weeks, 5=this week, 7=today, 9=within hours, 10=drop everything)
- "escalation_signals": list of phrases or signals from the email that indicate urgency or escalation (e.g. "all hands", "by EOD", "3rd reminder", "VP presentation tomorrow"). Empty list if none.
- "topic_key": a short normalized key for the topic/thread (e.g. "production-outage", "qbr-deck", "security-training", "agent-factory"). Use lowercase with hyphens. Same topic across emails should use the same key.

Category definitions:
- urgent: Time-sensitive, needs attention within hours (escalations, outages, exec requests, angry/frustrated tone)
- action_required: Needs a response or action within 1-2 days
- fyi: Informational, good to know but no action needed
- low_priority: Newsletters, automated notifications, can be skimmed later
- spam: Irrelevant marketing, phishing attempts, junk

TONE-BASED SEVERITY RULES:
- If the tone is "frustrated" or "escalating", raise the category by one level (fyi->action_required, action_required->urgent)
- If the email contains phrases like "URGENT", "ASAP", "final reminder", "3rd time", set urgency_score >= 8
- If the subject starts with "Re: Re:" or mentions follow-up counts, note this in escalation_signals

Always be concise. Match the user's professional tone in draft replies.
Respond with ONLY the JSON object."""

DIGEST_SYSTEM_PROMPT = """You are Forge, a personal AI assistant. Given a set of triaged emails, create a brief executive summary for the daily digest.

Include:
1. A 2-3 sentence overview of the day's email landscape
2. The top 3 things that need attention today
3. Any patterns or themes you notice (e.g., "multiple follow-ups from Project X")

Be concise and actionable. Write in a friendly but professional tone."""


def _extract_json(text: str) -> dict[str, Any]:
    """Extract a JSON object from LLM output, even if wrapped in markdown fences."""
    text = text.strip()
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1)
    brace_match = re.search(r"\{.*\}", text, re.DOTALL)
    if brace_match:
        text = brace_match.group(0)
    return json.loads(text)


DEFAULT_TRIAGE = {
    "category": "low_priority",
    "summary": "",
    "action_items": [],
    "needs_reply": False,
    "draft_reply": None,
    "reasoning": "",
    "tone": "neutral",
    "urgency_score": 3,
    "escalation_signals": [],
    "topic_key": "unknown",
}


class LLMClient:
    """Wraps Ollama's OpenAI-compatible API for email triage and summarization."""

    def __init__(self) -> None:
        self._client = OpenAI(
            base_url=cfg.LLM_BASE_URL,
            api_key=cfg.LLM_API_KEY,
        )
        self._model = cfg.LLM_MODEL

    def triage_email(self, email: dict[str, Any]) -> dict[str, Any]:
        """Analyze a single email and return triage results."""
        user_message = (
            f"Subject: {email['subject']}\n"
            f"From: {email['from_name']} <{email['from']}>\n"
            f"Received: {email['received']}\n"
            f"Importance: {email['importance']}\n"
            f"Read: {email['is_read']}\n"
            f"Has Attachments: {email['has_attachments']}\n\n"
            f"Body Preview:\n{email['body_preview']}"
        )

        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": TRIAGE_SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
        )

        content = response.choices[0].message.content or "{}"
        result = _extract_json(content)
        return {**DEFAULT_TRIAGE, **result}

    def triage_batch(self, emails: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Triage multiple emails. Returns list of (email, triage) tuples."""
        results = []
        for email in emails:
            try:
                triage = self.triage_email(email)
                results.append({"email": email, "triage": triage})
            except Exception as e:
                results.append({
                    "email": email,
                    "triage": {
                        **DEFAULT_TRIAGE,
                        "summary": f"[Triage failed: {e}]",
                        "reasoning": "Error during triage",
                    },
                })
        return results

    def generate_digest_summary(self, triaged_emails: list[dict[str, Any]]) -> str:
        """Generate an executive summary for the digest."""
        summary_lines = []
        for item in triaged_emails:
            t = item["triage"]
            e = item["email"]
            summary_lines.append(
                f"[{t['category'].upper()}] {e['subject']} — from {e['from_name'] or e['from']}: {t['summary']}"
            )

        user_message = (
            f"Here are today's {len(triaged_emails)} triaged emails:\n\n"
            + "\n".join(summary_lines)
        )

        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": DIGEST_SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.4,
        )

        return response.choices[0].message.content or "No summary generated."
