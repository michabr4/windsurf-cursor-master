"""
Webex OAuth Setup for Digitized Delivery Status Bot
Run this once to get your access token for SpaceLift and recordings.
"""

import os
import webbrowser
import http.server
import socketserver
import urllib.parse
import requests
import subprocess
import sys

# Digitized Delivery Webex Integration credentials
CLIENT_ID = os.environ.get("WEBEX_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("WEBEX_CLIENT_SECRET", "")
REDIRECT_URI = "http://localhost:8080/callback"

# Scopes needed for SpaceLift + recordings
SCOPES = [
    "spark:rooms_read",
    "spark:messages_read",
    "spark:memberships_read",
    "spark:people_read",
    "spark:recordings_read",
    "meeting:recordings_read",
    "meeting:transcripts_read",
    "meeting:schedules_read",
    "meeting:participants_read",
]

AUTH_URL = "https://webexapis.com/v1/authorize"
TOKEN_URL = "https://webexapis.com/v1/access_token"
GITHUB_REPO = "michabr4/dd-status-bot"

class OAuthHandler(http.server.SimpleHTTPRequestHandler):
    """Handle OAuth callback."""
    
    def do_GET(self):
        if self.path.startswith("/callback"):
            # Parse the authorization code
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            
            if "code" in params:
                code = params["code"][0]
                print(f"\n✅ Authorization code received!")
                
                # Exchange code for token
                token_data = {
                    "grant_type": "authorization_code",
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": REDIRECT_URI,
                }
                
                response = requests.post(TOKEN_URL, data=token_data)
                
                if response.status_code == 200:
                    tokens = response.json()
                    access_token = tokens.get("access_token")
                    refresh_token = tokens.get("refresh_token")
                    expires_in = tokens.get("expires_in", 0)
                    
                    print(f"\n{'='*60}")
                    print("✅ SUCCESS! Here are your tokens:")
                    print(f"{'='*60}")
                    print(f"\n🔑 Access Token (expires in {expires_in//3600} hours):")
                    print(f"{access_token}")
                    print(f"\n🔄 Refresh Token (save this!):")
                    print(f"{refresh_token}")
                    print(f"{'='*60}")
                    
                    # Auto-set GitHub secrets
                    print(f"\n🔧 Setting GitHub secrets for {GITHUB_REPO}...")
                    try:
                        subprocess.run(
                            f'echo "{access_token}" | gh secret set WEBEX_ACCESS_TOKEN --repo {GITHUB_REPO}',
                            shell=True, check=True, capture_output=True
                        )
                        print("  ✅ WEBEX_ACCESS_TOKEN set")
                        
                        subprocess.run(
                            f'echo "{refresh_token}" | gh secret set WEBEX_REFRESH_TOKEN --repo {GITHUB_REPO}',
                            shell=True, check=True, capture_output=True
                        )
                        print("  ✅ WEBEX_REFRESH_TOKEN set")
                        print(f"\n🎉 All secrets configured for {GITHUB_REPO}!")
                    except subprocess.CalledProcessError as e:
                        print(f"  ⚠️ Could not auto-set secrets: {e}")
                        print("  Set them manually:")
                        print(f"  WEBEX_ACCESS_TOKEN = {access_token}")
                        print(f"  WEBEX_REFRESH_TOKEN = {refresh_token}")
                    
                    # Save to file
                    with open("webex_tokens.txt", "w") as f:
                        f.write(f"ACCESS_TOKEN={access_token}\n")
                        f.write(f"REFRESH_TOKEN={refresh_token}\n")
                    print("\n💾 Tokens also saved to webex_tokens.txt")
                    
                    # Send success response
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"""
                        <html><body style="font-family: Arial; text-align: center; padding: 50px;">
                        <h1>&#9989; Authorization Successful!</h1>
                        <p>You can close this window and return to the terminal.</p>
                        <p>Tokens have been saved and GitHub secrets configured.</p>
                        </body></html>
                    """)
                else:
                    print(f"\n❌ Token exchange failed: {response.text}")
                    self.send_response(400)
                    self.end_headers()
                
                # Shutdown server
                raise KeyboardInterrupt
            else:
                error = params.get("error", ["Unknown error"])[0]
                print(f"\n❌ Authorization failed: {error}")
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress logging

def main():
    # Build authorization URL
    auth_params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(SCOPES),
        "state": "dd-status-bot",
    }
    
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(auth_params)}"
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║      Webex OAuth Setup for Digitized Delivery Bot           ║
╚══════════════════════════════════════════════════════════════╝

Opening browser for authorization...

If browser doesn't open, visit this URL:
{auth_url}

Waiting for callback on http://localhost:8080/callback ...
""")
    
    # Open browser
    webbrowser.open(auth_url)
    
    # Start local server to receive callback
    with socketserver.TCPServer(("", 8080), OAuthHandler) as httpd:
        try:
            httpd.handle_request()
        except KeyboardInterrupt:
            pass
    
    print("\n✅ OAuth setup complete!")

if __name__ == "__main__":
    main()
