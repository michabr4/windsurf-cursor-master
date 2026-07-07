"""
main.py — Email Summary Agent entry point.

Fetches your recent Outlook emails and produces an AI-powered daily brief.

Usage:
    python main.py                  # Last 24 hours, up to 20 emails
    python main.py --hours 4        # Last 4 hours
    python main.py --max 50         # Up to 50 emails
    python main.py --hours 1 --max 10
"""

import argparse
import sys
from datetime import datetime, timezone

from email_reader import fetch_emails
from summarizer import summarize_emails


def print_header(email_count, hours):
    """Print a formatted header for the daily brief."""
    now = datetime.now(timezone.utc).strftime("%A, %B %d, %Y")
    width = 55

    print()
    print("=" * width)
    print(f"  EMAIL DAILY BRIEF — {now}")
    print(f"  {email_count} emails from the last {hours} hour(s)")
    print("=" * width)
    print()


def main():
    parser = argparse.ArgumentParser(description="Email Summary Agent")
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Look back this many hours (default: 24)",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=20,
        help="Maximum emails to process (default: 20)",
    )
    args = parser.parse_args()

    # Step 1: Fetch emails
    print("\nConnecting to Outlook...")
    try:
        emails = fetch_emails(hours=args.hours, max_emails=args.max)
    except RuntimeError as e:
        print(f"\nError fetching emails: {e}")
        sys.exit(1)

    print_header(len(emails), args.hours)

    if not emails:
        print("  No emails found in that timeframe. Your inbox is clear!")
        print()
        return

    # Step 2: Show what we found
    print("  Emails retrieved:")
    for i, email in enumerate(emails, 1):
        marker = "*" if not email["is_read"] else " "
        imp = " [!]" if email["importance"] == "high" else ""
        print(f"    {marker} {i}. {email['sender']} — {email['subject']}{imp}")
    print()

    # Step 3: Summarize
    print("  Generating AI summary...\n")
    try:
        summary = summarize_emails(emails)
    except RuntimeError as e:
        print(f"\nError generating summary: {e}")
        sys.exit(1)

    print("-" * 55)
    print()
    print(summary)
    print()
    print("-" * 55)
    print("  Agent complete. Have a productive day!")
    print()


if __name__ == "__main__":
    main()
