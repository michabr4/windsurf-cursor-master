"""
Webex OAuth Setup — run locally once to obtain access + refresh tokens for integrations.

Requires a Webex *Integration* (not the bot) with redirect URI matching REDIRECT_URI.

Usage:
  export WEBEX_CLIENT_ID="..."
  export WEBEX_CLIENT_SECRET="..."
  export WEBEX_REDIRECT_URI="http://localhost:8080/callback"   # optional
  python oauth_setup.py

Then add GitHub Actions secrets:
  WEBEX_ACCESS_TOKEN   (short-lived — refresh periodically)
  WEBEX_REFRESH_TOKEN  (long-lived — store securely)
"""

import http.server
import os
import socketserver
import urllib.parse
import webbrowser

import requests

CLIENT_ID = os.environ.get("WEBEX_CLIENT_ID", "").strip()
CLIENT_SECRET = os.environ.get("WEBEX_CLIENT_SECRET", "").strip()
REDIRECT_URI = os.environ.get("WEBEX_REDIRECT_URI", "http://localhost:8080/callback").strip()

SCOPES = [
    "spark:recordings_read",
    "meeting:recordings_read",
    "meeting:transcripts_read",
    "spark:rooms_read",
    "spark:memberships_read",
    "spark:people_read",
    "meeting:schedules_read",
    "meeting:participants_read",
]

AUTH_URL = "https://webexapis.com/v1/authorize"
TOKEN_URL = "https://webexapis.com/v1/access_token"


class OAuthHandler(http.server.SimpleHTTPRequestHandler):
    """Handle OAuth callback."""

    def do_GET(self):
        if self.path.startswith("/callback"):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)

            if "code" in params:
                code = params["code"][0]
                print("\n✅ Authorization code received!")

                token_data = {
                    "grant_type": "authorization_code",
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": REDIRECT_URI,
                }

                response = requests.post(TOKEN_URL, data=token_data, timeout=60)

                if response.status_code == 200:
                    tokens = response.json()
                    access_token = tokens.get("access_token")
                    refresh_token = tokens.get("refresh_token")
                    expires_in = tokens.get("expires_in", 0)

                    print(f"\n{'=' * 60}")
                    print("✅ Tokens received (do not commit or paste into chat).")
                    print(f"{'=' * 60}")
                    print(f"\nAccess token expires in ~{expires_in // 3600} hours.")
                    print(f"\n🔄 Refresh token — add as GitHub secret WEBEX_REFRESH_TOKEN:")
                    print(refresh_token)
                    print(f"\n🔑 Access token — add as WEBEX_ACCESS_TOKEN (until it expires):")
                    print(access_token)
                    print(f"\n{'=' * 60}")

                    out = os.path.join(os.path.dirname(__file__), "webex_tokens.txt")
                    with open(out, "w", encoding="utf-8") as f:
                        f.write(f"ACCESS_TOKEN={access_token}\n")
                        f.write(f"REFRESH_TOKEN={refresh_token}\n")
                    print(f"\n💾 Also saved to {out} (gitignored).")

                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(
                        b"<html><body><h1>OK</h1><p>Return to the terminal.</p></body></html>"
                    )
                else:
                    print(f"\n❌ Token exchange failed: {response.status_code} {response.text}")
                    self.send_response(400)
                    self.end_headers()

                raise KeyboardInterrupt

            error = params.get("error", ["Unknown error"])[0]
            print(f"\n❌ Authorization failed: {error}")
            self.send_response(400)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, _format, *_args):
        pass


def main():
    global CLIENT_ID, CLIENT_SECRET
    if not CLIENT_ID or not CLIENT_SECRET:
        print(
            "Set WEBEX_CLIENT_ID and WEBEX_CLIENT_SECRET (Integration app credentials).\n"
            "Example:\n  export WEBEX_CLIENT_ID='...'\n  export WEBEX_CLIENT_SECRET='...'"
        )
        raise SystemExit(1)

    auth_params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(SCOPES),
        "state": "mgm-status-bot",
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(auth_params)}"

    print(
        f"""
Opening browser for Webex authorization…
If nothing opens, visit:
{auth_url}

Waiting for callback on {REDIRECT_URI} …
"""
    )

    webbrowser.open(auth_url)

    with socketserver.TCPServer(("", 8080), OAuthHandler) as httpd:
        try:
            httpd.handle_request()
        except KeyboardInterrupt:
            pass

    print("\nDone.")


if __name__ == "__main__":
    main()
