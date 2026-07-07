"""
summarizer.py — Send emails to an LLM and get a structured daily brief.

Uses OpenAI API with gpt-4o-mini for cost efficiency.
API key loaded from .env — never hardcoded.
"""

import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """You are an executive email assistant. Analyze the provided emails and produce a structured daily brief.

FORMAT YOUR RESPONSE EXACTLY LIKE THIS:

## INBOX OVERVIEW
Write 2-3 sentences summarizing the overall state of the inbox — themes, volume, anything notable.

## NEEDS ATTENTION
List emails that require the user's action, ranked by urgency. For each:
- **Sender — "Subject"**
  → Why it needs attention
  → Deadline if mentioned

## ACTION ITEMS
Bullet list of specific tasks or deadlines extracted from the emails. Include who requested it and when it's due.

## LOW PRIORITY
Briefly list newsletters, automated notifications, FYI-only messages — things that can wait or be skipped.

RULES:
- Use the sender's NAME, not their email address.
- Flag anything with a deadline in the next 48 hours.
- If an email is marked as high importance, mention it.
- Unread emails should be prioritized over read ones.
- Be concise. No filler. Executives scan, they don't read essays.
- If there are no emails, say "Your inbox is clear."
"""


def _format_emails_for_llm(emails):
    """Format email list into a text block the LLM can process."""
    if not emails:
        return "No emails found in the requested timeframe."

    lines = []
    for i, email in enumerate(emails, 1):
        read_status = "READ" if email["is_read"] else "UNREAD"
        importance = email.get("importance", "normal").upper()
        lines.append(
            f"--- Email {i} ---\n"
            f"From: {email['sender']} ({email['sender_email']})\n"
            f"Subject: {email['subject']}\n"
            f"Received: {email['received']}\n"
            f"Status: {read_status} | Importance: {importance}\n"
            f"Preview:\n{email['preview']}\n"
        )
    return "\n".join(lines)


def summarize_emails(emails):
    """
    Send emails to OpenAI and return a structured daily brief.

    Args:
        emails: List of email dicts from email_reader.fetch_emails()

    Returns:
        String containing the formatted summary
    """
    if not OPENAI_API_KEY or OPENAI_API_KEY == "paste-your-openai-key-here":
        raise RuntimeError(
            "Missing OPENAI_API_KEY. "
            "Please fill in your .env file with your OpenAI API key. "
            "Get one at https://platform.openai.com/api-keys"
        )

    client = OpenAI(api_key=OPENAI_API_KEY)

    email_text = _format_emails_for_llm(emails)

    now = datetime.now(timezone.utc).strftime("%A, %B %d, %Y at %I:%M %p UTC")
    user_message = (
        f"Current date/time: {now}\n"
        f"Number of emails: {len(emails)}\n\n"
        f"{email_text}"
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.3,
        max_tokens=1500,
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    # Quick test with fake data
    test_emails = [
        {
            "sender": "Sarah Chen",
            "sender_email": "sarah.chen@example.com",
            "subject": "Budget approval needed by EOD",
            "received": "2025-05-21T09:30:00Z",
            "preview": "Hi, I need your sign-off on the Q3 tooling budget. Please review the attached spreadsheet and approve by 5 PM today.",
            "is_read": False,
            "importance": "high",
        },
        {
            "sender": "IT Notifications",
            "sender_email": "noreply@example.com",
            "subject": "Scheduled maintenance this Saturday",
            "received": "2025-05-21T08:00:00Z",
            "preview": "Systems will be down for maintenance from 2 AM to 6 AM on Saturday.",
            "is_read": True,
            "importance": "normal",
        },
    ]

    print("Testing summarizer with sample data...\n")
    result = summarize_emails(test_emails)
    print(result)
