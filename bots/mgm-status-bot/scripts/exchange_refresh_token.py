#!/usr/bin/env python3
"""
Exchange a Webex OAuth refresh token for a new access token (no browser).

Env:
  WEBEX_REFRESH_TOKEN   — from oauth_setup.py or prior OAuth
  WEBEX_CLIENT_ID       — Integration Client ID
  WEBEX_CLIENT_SECRET   — Integration Client Secret

Prints the new access_token to stdout (pipe into gh secret set WEBEX_ACCESS_TOKEN -b@-).

Does NOT print secrets if stdout is a TTY except first 8 chars — actually simpler to just print full token for piping.

Usage:
  export WEBEX_REFRESH_TOKEN='...'
  export WEBEX_CLIENT_ID='...'
  export WEBEX_CLIENT_SECRET='...'
  python scripts/exchange_refresh_token.py
"""

import os
import sys

import requests

TOKEN_URL = "https://webexapis.com/v1/access_token"


def main() -> int:
    refresh = os.environ.get("WEBEX_REFRESH_TOKEN", "").strip()
    cid = os.environ.get("WEBEX_CLIENT_ID", "").strip()
    secret = os.environ.get("WEBEX_CLIENT_SECRET", "").strip()

    if not refresh or not cid or not secret:
        print(
            "Missing WEBEX_REFRESH_TOKEN, WEBEX_CLIENT_ID, or WEBEX_CLIENT_SECRET",
            file=sys.stderr,
        )
        return 1

    r = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh,
            "client_id": cid,
            "client_secret": secret,
        },
        timeout=60,
    )

    if not r.ok:
        print(r.status_code, r.text[:1000], file=sys.stderr)
        return 1

    data = r.json()
    access = data.get("access_token", "")
    new_refresh = data.get("refresh_token")

    print(access)
    if new_refresh and new_refresh != refresh:
        print(
            "INFO: Cisco returned a rotated refresh token — update WEBEX_REFRESH_TOKEN.",
            file=sys.stderr,
        )
        print(new_refresh, file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
