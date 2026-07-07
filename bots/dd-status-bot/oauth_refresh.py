"""
Refresh Webex OAuth tokens using WEBEX_REFRESH_TOKEN.

Run locally when WEBEX_ACCESS_TOKEN expires, then copy the new access token
to the GitHub Actions secret WEBEX_ACCESS_TOKEN (and update WEBEX_REFRESH_TOKEN
if a new refresh token is returned).

Required environment variables:
  WEBEX_REFRESH_TOKEN
  WEBEX_CLIENT_ID
  WEBEX_CLIENT_SECRET
"""

import os
import sys

import requests

TOKEN_URL = "https://webexapis.com/v1/access_token"


def main() -> None:
    refresh_token = os.environ.get("WEBEX_REFRESH_TOKEN", "")
    client_id = os.environ.get("WEBEX_CLIENT_ID", "")
    client_secret = os.environ.get("WEBEX_CLIENT_SECRET", "")

    missing = [
        name
        for name, value in [
            ("WEBEX_REFRESH_TOKEN", refresh_token),
            ("WEBEX_CLIENT_ID", client_id),
            ("WEBEX_CLIENT_SECRET", client_secret),
        ]
        if not value
    ]
    if missing:
        print("Missing required environment variables:")
        for name in missing:
            print(f"  - {name}")
        print("\nUse the same client ID/secret as your Webex Integration app.")
        sys.exit(1)

    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
        },
        timeout=30,
    )

    if response.status_code != 200:
        print(f"Token refresh failed: HTTP {response.status_code}")
        print(response.text[:500])
        sys.exit(1)

    tokens = response.json()
    access_token = tokens.get("access_token", "")
    new_refresh = tokens.get("refresh_token", refresh_token)
    expires_in = tokens.get("expires_in", 0)

    print("Token refresh successful")
    print("=" * 60)
    print(f"Expires in: {expires_in // 3600}h {(expires_in % 3600) // 60}m")
    print("\nNew access token (copy to GitHub secret WEBEX_ACCESS_TOKEN):")
    print(access_token)
    print("\nRefresh token (copy to GitHub secret WEBEX_REFRESH_TOKEN if changed):")
    print(new_refresh)
    print("=" * 60)
    print("\nGitHub CLI example:")
    print('  gh secret set WEBEX_ACCESS_TOKEN --repo michabr4/dd-status-bot')
    print('  gh secret set WEBEX_REFRESH_TOKEN --repo michabr4/dd-status-bot')


if __name__ == "__main__":
    main()
