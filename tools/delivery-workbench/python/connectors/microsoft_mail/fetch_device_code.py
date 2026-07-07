"""Optional fetch via MSAL device code — needs MS_CLIENT_ID (public client, no secret)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUT = REPO_ROOT / "data" / "runs" / "email" / "latest" / "messages.json"


def _load_dotenv() -> None:
    env_path = REPO_ROOT / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip())


def _fetch_graph(token: str, user_id: str, since_iso: str, top: int) -> list[dict]:
    import urllib.request

    filt = quote(f"receivedDateTime ge {since_iso}")
    if user_id.lower() == "me":
        url = (
            f"https://graph.microsoft.com/v1.0/me/messages?"
            f"$filter={filt}&$top={top}"
            f"&$orderby=receivedDateTime desc"
            f"&$select=id,subject,from,receivedDateTime,bodyPreview,isRead,conversationId"
        )
    else:
        url = (
            f"https://graph.microsoft.com/v1.0/users/{quote(user_id)}/messages?"
            f"$filter={filt}&$top={top}"
            f"&$orderby=receivedDateTime desc"
            f"&$select=id,subject,from,receivedDateTime,bodyPreview,isRead,conversationId"
        )

    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    out = []
    for m in data.get("value", []):
        from_obj = m.get("from", {}).get("emailAddress", {})
        out.append(
            {
                "id": m.get("id"),
                "subject": m.get("subject"),
                "from": from_obj.get("address", ""),
                "receivedDateTime": m.get("receivedDateTime"),
                "bodyPreview": m.get("bodyPreview"),
                "isRead": m.get("isRead"),
                "conversationId": m.get("conversationId"),
            }
        )
    return out


def main() -> int:
    _load_dotenv()
    parser = argparse.ArgumentParser(description="Fetch mail via MSAL device code")
    parser.add_argument("--since-hours", type=int, default=48)
    parser.add_argument("--max-messages", type=int, default=40)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    client_id = os.getenv("MS_CLIENT_ID", "").strip()
    if not client_id:
        print("MS_CLIENT_ID required for device_code mode.", file=sys.stderr)
        return 1

    tenant = os.getenv("MS_TENANT_ID", "organizations").strip()
    mailbox = os.getenv("MS_MAILBOX_UPN", "me").strip() or "me"
    scopes = os.getenv("MS_GRAPH_SCOPES", "Mail.Read User.Read").split()

    try:
        import msal
    except ImportError:
        print("Install msal: pip install msal", file=sys.stderr)
        return 1

    app = msal.PublicClientApplication(client_id, authority=f"https://login.microsoftonline.com/{tenant}")
    accounts = app.get_accounts()
    result = None
    if accounts:
        result = app.acquire_token_silent(scopes, account=accounts[0])

    if not result or "access_token" not in result:
        flow = app.initiate_device_flow(scopes=scopes)
        if "user_code" not in flow:
            print(flow.get("error_description", flow), file=sys.stderr)
            return 1
        print(flow["message"])
        result = app.acquire_token_by_device_flow(flow)

    if "access_token" not in result:
        print(result.get("error_description", result), file=sys.stderr)
        return 1

    since = datetime.now(timezone.utc) - timedelta(hours=args.since_hours)
    since_iso = since.strftime("%Y-%m-%dT%H:%M:%SZ")
    messages = _fetch_graph(result["access_token"], mailbox, since_iso, args.max_messages)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(messages, indent=2), encoding="utf-8")
    print(f"Wrote {len(messages)} messages to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
