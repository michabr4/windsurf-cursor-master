"""List your recent Asana tasks (needs ASANA_ACCESS_TOKEN in .env).

Usage:
  python python/examples/asana_list_my_tasks.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

PYTHON_ROOT = Path(__file__).resolve().parents[1]
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

load_dotenv()

from src.asana_client import AsanaClient  # noqa: E402


def main() -> None:
    client = AsanaClient()
    token = client._require_token()
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    me = requests.get(
        "https://app.asana.com/api/1.0/users/me",
        headers=headers,
        params={"opt_fields": "name,gid"},
        timeout=30,
    )
    me.raise_for_status()
    user_gid = me.json()["data"]["gid"]
    tasks = requests.get(
        "https://app.asana.com/api/1.0/tasks",
        headers=headers,
        params={
            "assignee": user_gid,
            "completed_since": "now",
            "opt_fields": "name,permalink_url,due_on,completed",
            "limit": 15,
        },
        timeout=30,
    )
    tasks.raise_for_status()
    items = tasks.json().get("data", [])
    if not items:
        print("No open tasks assigned to you (or token lacks access).")
        return
    print("Open tasks assigned to you:\n")
    for t in items:
        if not isinstance(t, dict):
            continue
        gid = t.get("gid", "")
        name = t.get("name", "")
        due = t.get("due_on") or "no due date"
        print(f"  {gid}  {name}  (due: {due})")
        url = t.get("permalink_url")
        if isinstance(url, str) and url:
            print(f"         {url}")
    print("\nReview one:")
    print("  python python/examples/asana_review_cli.py <GID or URL>")


if __name__ == "__main__":
    main()
