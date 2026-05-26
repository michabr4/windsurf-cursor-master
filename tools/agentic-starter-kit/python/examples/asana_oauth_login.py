"""Open the browser to complete Asana OAuth (needs the review server running).

1. Add ASANA_CLIENT_ID and ASANA_CLIENT_SECRET to .env
2. Register redirect URI in Asana (default http://127.0.0.1:8845/oauth/callback)
3. Run: python python/examples/asana_review_server.py
4. Run: python python/examples/asana_oauth_login.py
"""

from __future__ import annotations

import os
import sys
import webbrowser
from pathlib import Path


PYTHON_ROOT = Path(__file__).resolve().parents[1]
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from src.asana_oauth import login_start_url, oauth_configured, redirect_uri  # noqa: E402


def main() -> None:
    if not oauth_configured():
        print("Set ASANA_CLIENT_ID and ASANA_CLIENT_SECRET in .env first.")
        raise SystemExit(1)
    port = os.getenv("ASANA_REVIEW_PORT", "8845")
    print(f"Redirect URI in Asana app must be: {redirect_uri()}")
    print("Start the server if it is not running:")
    print("  python python/examples/asana_review_server.py")
    url = login_start_url()
    print(f"\nOpening: {url}\n")
    webbrowser.open(url)
    print("After you approve access in the browser, tokens are saved to .env.")


if __name__ == "__main__":
    main()
