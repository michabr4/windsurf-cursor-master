"""
email_reader.py — Connect to Outlook via Microsoft Graph and fetch recent emails.

Uses MSAL device code flow so no passwords are stored in code.
Token is cached locally so you only sign in once.
"""

import os
import json
import atexit
from datetime import datetime, timezone, timedelta

import msal
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

GRAPH_BASE = "https://graph.microsoft.com/v1.0"
SCOPES = ["Mail.Read"]

CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
TENANT_ID = os.getenv("AZURE_TENANT_ID")
TOKEN_CACHE_FILE = "token_cache.json"


def _build_msal_app():
    """Build an MSAL public client app with persistent token cache."""
    cache = msal.SerializableTokenCache()

    if os.path.exists(TOKEN_CACHE_FILE):
        with open(TOKEN_CACHE_FILE, "r") as f:
            cache.deserialize(f.read())

    def _save_cache():
        if cache.has_state_changed:
            with open(TOKEN_CACHE_FILE, "w") as f:
                f.write(cache.serialize())

    atexit.register(_save_cache)

    authority = f"https://login.microsoftonline.com/{TENANT_ID}"
    app = msal.PublicClientApplication(
        CLIENT_ID,
        authority=authority,
        token_cache=cache,
    )
    return app


def _get_access_token():
    """Acquire a token silently (cached) or via device code flow."""
    app = _build_msal_app()

    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result and "access_token" in result:
            return result["access_token"]

    # No cached token — use device code flow
    flow = app.initiate_device_flow(scopes=SCOPES)
    if "user_code" not in flow:
        raise RuntimeError(f"Device flow failed: {json.dumps(flow, indent=2)}")

    print("\n" + "=" * 55)
    print("  SIGN IN TO MICROSOFT")
    print("=" * 55)
    print(f"  1. Open:  {flow['verification_uri']}")
    print(f"  2. Enter: {flow['user_code']}")
    print("=" * 55 + "\n")
    print("Waiting for you to sign in...")

    result = app.acquire_token_by_device_flow(flow)

    if "access_token" not in result:
        error = result.get("error_description", result.get("error", "Unknown error"))
        raise RuntimeError(f"Authentication failed: {error}")

    print("Signed in successfully!\n")
    return result["access_token"]


def _strip_html(html_body):
    """Remove HTML tags and return clean text."""
    if not html_body:
        return ""
    soup = BeautifulSoup(html_body, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    return text


def fetch_emails(hours=24, max_emails=20):
    """
    Fetch recent emails from Outlook inbox.

    Args:
        hours: Look back this many hours (default 24)
        max_emails: Maximum emails to return (default 20)

    Returns:
        List of dicts with: sender, subject, received, preview
    """
    if not CLIENT_ID or CLIENT_ID == "paste-your-client-id-here":
        raise RuntimeError(
            "Missing AZURE_CLIENT_ID. "
            "Please fill in your .env file with your Azure app credentials. "
            "See the tutorial for setup instructions."
        )
    if not TENANT_ID or TENANT_ID == "paste-your-tenant-id-here":
        raise RuntimeError(
            "Missing AZURE_TENANT_ID. "
            "Please fill in your .env file with your Azure app credentials."
        )

    token = _get_access_token()
    headers = {"Authorization": f"Bearer {token}"}

    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    params = {
        "$top": max_emails,
        "$orderby": "receivedDateTime desc",
        "$filter": f"receivedDateTime ge {since}",
        "$select": "from,subject,receivedDateTime,body,bodyPreview,isRead,importance",
    }

    response = requests.get(
        f"{GRAPH_BASE}/me/messages",
        headers=headers,
        params=params,
        timeout=30,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Graph API error ({response.status_code}): {response.text}"
        )

    data = response.json()
    messages = data.get("value", [])

    emails = []
    for msg in messages:
        sender_data = msg.get("from", {}).get("emailAddress", {})
        body_html = msg.get("body", {}).get("content", "")
        body_text = _strip_html(body_html)

        emails.append(
            {
                "sender": sender_data.get("name", sender_data.get("address", "Unknown")),
                "sender_email": sender_data.get("address", ""),
                "subject": msg.get("subject", "(no subject)"),
                "received": msg.get("receivedDateTime", ""),
                "preview": body_text[:500] if body_text else msg.get("bodyPreview", ""),
                "is_read": msg.get("isRead", False),
                "importance": msg.get("importance", "normal"),
            }
        )

    return emails


if __name__ == "__main__":
    print("Fetching your recent emails...\n")
    results = fetch_emails()
    print(f"Found {len(results)} emails:\n")
    for i, email in enumerate(results, 1):
        read_marker = " " if email["is_read"] else "*"
        print(f"  {read_marker} {i}. {email['sender']} — {email['subject']}")
    print()
