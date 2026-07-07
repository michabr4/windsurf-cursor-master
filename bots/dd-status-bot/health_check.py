"""
Validate Webex tokens before the daily pipeline runs.
Exits with code 1 if any required token fails (fail-fast in GitHub Actions).
"""

import os
import sys

import requests

BASE_URL = "https://webexapis.com/v1"
WEBEX_BOT_TOKEN = os.environ.get("WEBEX_BOT_TOKEN", "")
WEBEX_ACCESS_TOKEN = os.environ.get("WEBEX_ACCESS_TOKEN", "")


def check_token(name: str, token: str) -> bool:
    if not token:
        print(f"FAIL {name}: not set")
        return False

    try:
        response = requests.get(
            f"{BASE_URL}/people/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=30,
        )
    except requests.RequestException as exc:
        print(f"FAIL {name}: request error — {exc}")
        return False

    if response.status_code == 200:
        person = response.json()
        display = person.get("displayName") or person.get("emails", ["unknown"])[0]
        print(f"PASS {name}: valid ({display})")
        return True

    if response.status_code == 401:
        if name == "WEBEX_ACCESS_TOKEN":
            print(
                f"FAIL {name}: unauthorized — token may be expired. "
                "Refresh at developer.webex.com or run: python oauth_refresh.py"
            )
        else:
            print(f"FAIL {name}: unauthorized — token may be revoked or invalid")
        return False

    print(f"FAIL {name}: HTTP {response.status_code} — {response.text[:200]}")
    return False


def main() -> None:
    print("Webex token health check")
    print("-" * 40)

    bot_ok = check_token("WEBEX_BOT_TOKEN", WEBEX_BOT_TOKEN)
    access_ok = check_token("WEBEX_ACCESS_TOKEN", WEBEX_ACCESS_TOKEN)

    print("-" * 40)
    if bot_ok and access_ok:
        print("All required tokens OK")
        sys.exit(0)

    print("One or more required tokens failed")
    sys.exit(1)


if __name__ == "__main__":
    main()
