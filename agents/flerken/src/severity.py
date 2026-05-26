"""Severity engine — post-triage severity adjustment based on tone + recurrence.

Runs after LLM triage to:
1. Detect recurring topics/senders across the batch
2. Escalate severity when tone is aggressive or topic keeps surfacing
3. Compute a composite severity_score for dashboard ranking
4. Classify emails by audience (customer vs internal)
"""

from collections import Counter
from typing import Any
import re

CATEGORY_RANK = {
    "spam": 0,
    "low_priority": 1,
    "fyi": 2,
    "action_required": 3,
    "urgent": 4,
}
RANK_TO_CATEGORY = {v: k for k, v in CATEGORY_RANK.items()}

ESCALATING_TONES = {"frustrated", "escalating", "urgent"}

# ── Audience / Customer Classification ──
CUSTOMER_PATTERNS: dict[str, list[str]] = {
    "MGM": [
        r"\bmgm\b",
        r"\bmgm\s*resorts?\b",
        r"@mgmresorts\.com",
    ],
    "Providence": [
        r"\bprovidence\b",
        r"\bprovidence\s+health\b",
        r"@providence\.org",
    ],
}

def _classify_audience(email: dict, triage: dict) -> tuple[str, str | None]:
    """Return (audience, customer_name).

    audience is 'customer' or 'internal'.
    customer_name is 'MGM', 'Providence', or None.
    """
    text = " ".join([
        email.get("subject", ""),
        email.get("body_preview", ""),
        email.get("body", ""),
        email.get("from", ""),
        email.get("from_name", ""),
        triage.get("summary", ""),
    ]).lower()

    for customer, patterns in CUSTOMER_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE):
                return "customer", customer
    return "internal", None


def _escalate_category(current: str, steps: int = 1) -> str:
    """Bump a category up by N severity levels (capped at urgent)."""
    rank = CATEGORY_RANK.get(current, 1)
    new_rank = min(rank + steps, 4)
    return RANK_TO_CATEGORY.get(new_rank, current)


def apply_severity(triaged: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Enhance triaged emails with severity adjustments and recurrence metrics.

    Mutates each item["triage"] in place, adding:
      - original_category: the LLM's raw category (before adjustments)
      - adjusted_category: final category after tone + recurrence escalation
      - severity_score: composite 1-100 score for ranking
      - recurrence_count: how many emails share the same topic_key
      - sender_frequency: how many emails from this sender
      - severity_factors: list of human-readable reasons for any escalation
    """
    # Count topic occurrences and sender frequency across the batch
    topic_counts: Counter = Counter()
    sender_counts: Counter = Counter()
    for item in triaged:
        topic_key = item["triage"].get("topic_key", "unknown")
        sender = item["email"].get("from", "unknown")
        topic_counts[topic_key] += 1
        sender_counts[sender] += 1

    for item in triaged:
        t = item["triage"]
        e = item["email"]

        original_cat = t.get("category", "low_priority")
        adjusted_cat = original_cat
        factors: list[str] = []
        urgency_score = t.get("urgency_score", 3)
        tone = t.get("tone", "neutral")
        topic_key = t.get("topic_key", "unknown")
        sender = e.get("from", "unknown")

        recurrence = topic_counts.get(topic_key, 1)
        sender_freq = sender_counts.get(sender, 1)

        # ── Audience classification ──
        audience, customer_name = _classify_audience(e, t)
        t["audience"] = audience
        t["customer_name"] = customer_name

        # ── Rule 1: Tone-based escalation ──
        if tone in ESCALATING_TONES and original_cat not in ("urgent", "spam"):
            adjusted_cat = _escalate_category(adjusted_cat)
            factors.append(f"Tone is \"{tone}\" — escalated severity")

        # ── Rule 2: Recurrence escalation ──
        if recurrence >= 3:
            adjusted_cat = _escalate_category(adjusted_cat, steps=2)
            factors.append(f"Topic \"{topic_key}\" appeared {recurrence}x — high recurrence escalation")
        elif recurrence == 2:
            adjusted_cat = _escalate_category(adjusted_cat)
            factors.append(f"Topic \"{topic_key}\" appeared {recurrence}x — recurrence bump")

        # ── Rule 3: Sender frequency ──
        if sender_freq >= 3:
            if adjusted_cat not in ("urgent",):
                adjusted_cat = _escalate_category(adjusted_cat)
            factors.append(f"Sender {sender} sent {sender_freq} emails — persistent sender")

        # ── Rule 4: Unread + high urgency score ──
        if not e.get("is_read", True) and urgency_score >= 7:
            if adjusted_cat != "urgent":
                adjusted_cat = _escalate_category(adjusted_cat)
                factors.append(f"Unread + urgency score {urgency_score}/10 — needs attention")

        # ── Rule 5: Escalation signals bonus ──
        signals = t.get("escalation_signals", [])
        if len(signals) >= 2:
            urgency_score = min(urgency_score + 1, 10)
            factors.append(f"{len(signals)} escalation signals detected")

        # ── Rule 6: Customer-related emails get priority bump ──
        if audience == "customer" and adjusted_cat not in ("urgent",):
            adjusted_cat = _escalate_category(adjusted_cat)
            factors.append(f"Customer \"{customer_name}\" referenced — customer priority bump")

        # ── Compute composite severity_score (1-100) ──
        cat_weight = CATEGORY_RANK.get(adjusted_cat, 1) * 20  # 0-80
        urgency_weight = urgency_score * 2                      # 2-20
        recurrence_bonus = min(recurrence * 3, 15)              # 0-15
        tone_bonus = 5 if tone in ESCALATING_TONES else 0      # 0-5
        unread_bonus = 3 if not e.get("is_read", True) else 0  # 0-3
        customer_bonus = 5 if audience == "customer" else 0    # 0-5

        severity_score = min(
            cat_weight + urgency_weight + recurrence_bonus + tone_bonus + unread_bonus + customer_bonus,
            100,
        )

        # ── Write back ──
        t["original_category"] = original_cat
        t["adjusted_category"] = adjusted_cat
        t["severity_score"] = severity_score
        t["recurrence_count"] = recurrence
        t["sender_frequency"] = sender_freq
        t["severity_factors"] = factors
        # Use adjusted category as the display category
        t["category"] = adjusted_cat

    # Re-sort by severity_score descending
    triaged.sort(key=lambda x: x["triage"]["severity_score"], reverse=True)
    return triaged
