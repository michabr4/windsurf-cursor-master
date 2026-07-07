import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

WEBEX_API_MESSAGES_URL = "https://webexapis.com/v1/messages"
WEBEX_API_ROOMS_URL = "https://webexapis.com/v1/rooms"
SUBSCRIBERS_FILE = Path(os.getenv("SUBSCRIBERS_FILE", "subscribers.json"))
REQUEST_TIMEOUT_SECONDS = 20


def _load_subscribers(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        print(f"ERROR: subscribers file not found: {path}")
        return []

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON in {path}: {exc}")
        return []

    if isinstance(raw, list):
        items = raw
    elif isinstance(raw, dict) and isinstance(raw.get("subscribers"), list):
        items = raw["subscribers"]
    else:
        print(
            "ERROR: subscribers.json must be either a list or an object with a "
            "'subscribers' list"
        )
        return []

    normalized: list[dict[str, str]] = []
    for item in items:
        if not isinstance(item, dict):
            continue

        room_id = item.get("roomId") or item.get("room_id")
        room_name = item.get("roomName") or item.get("room_name") or item.get("roomTitle")
        email = item.get("toPersonEmail") or item.get("email")

        if room_id:
            normalized.append({"roomId": str(room_id)})
        elif room_name:
            normalized.append({"roomName": str(room_name)})
        elif email:
            normalized.append({"toPersonEmail": str(email)})

    return normalized


def _build_report_markdown() -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return (
        "## MGM Daily Status Report\n"
        f"Generated: **{now}**\n\n"
        "- Delivery pipeline: ✅ Operational\n"
        "- Report bot: ✅ Running\n"
        "- Notes: Update this template in `send_reports.py` with your real status sources."
    )


def _send_message(token: str, target: dict[str, str], markdown: str, dry_run: bool) -> bool:
    payload = {**target, "markdown": markdown}

    if dry_run:
        print(f"DRY_RUN: would send payload: {payload}")
        return True

    response = requests.post(
        WEBEX_API_MESSAGES_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    if response.status_code >= 300:
        print(
            "ERROR: Webex API send failed "
            f"for target {target} with status {response.status_code}: {response.text}"
        )
        return False

    return True


def _resolve_room_id_from_name(token: str, room_name: str) -> str | None:
    response = requests.get(
        WEBEX_API_ROOMS_URL,
        headers={"Authorization": f"Bearer {token}"},
        params={"max": 1000},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    if response.status_code >= 300:
        print(
            "ERROR: failed to list Webex rooms "
            f"with status {response.status_code}: {response.text}"
        )
        return None

    items = response.json().get("items", [])
    exact_matches = [
        room for room in items if str(room.get("title", "")).strip().lower() == room_name.strip().lower()
    ]

    if not exact_matches:
        print(f"ERROR: no Webex room found with title '{room_name}'")
        return None

    if len(exact_matches) > 1:
        print(
            f"ERROR: multiple Webex rooms found with title '{room_name}'. "
            "Use roomId in subscribers.json to disambiguate."
        )
        return None

    return exact_matches[0].get("id")


def _resolve_target(token: str, target: dict[str, str], dry_run: bool) -> dict[str, str] | None:
    if "roomName" not in target:
        return target

    room_name = target["roomName"]
    if dry_run:
        print(f"DRY_RUN: would resolve roomName '{room_name}' to roomId via Webex API")
        return {"roomName": room_name}

    room_id = _resolve_room_id_from_name(token, room_name)
    if not room_id:
        return None

    return {"roomId": room_id}


def main() -> int:
    token = os.getenv("WEBEX_BOT_TOKEN", "").strip()
    dry_run = os.getenv("DRY_RUN", "").lower() in {"1", "true", "yes"}

    if not token and not dry_run:
        print("ERROR: missing WEBEX_BOT_TOKEN")
        return 1

    subscribers = _load_subscribers(SUBSCRIBERS_FILE)
    if not subscribers:
        print("WARNING: no valid subscribers found. Nothing to send.")
        return 0

    markdown = _build_report_markdown()

    success_count = 0
    for target in subscribers:
        resolved_target = _resolve_target(token, target, dry_run)
        if not resolved_target:
            continue
        if _send_message(token, resolved_target, markdown, dry_run):
            success_count += 1

    total = len(subscribers)
    print(f"Completed sends: {success_count}/{total}")

    if success_count == total:
        return 0

    print("ERROR: one or more report sends failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
