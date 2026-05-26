"""
MGM Status Report - GitHub Actions Script
Sends daily status reports to Webex subscribers.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

WEBEX_BOT_TOKEN = os.environ.get("WEBEX_BOT_TOKEN", "").strip()
BASE_URL = "https://webexapis.com/v1"
SUBSCRIBERS_FILE = Path(os.environ.get("SUBSCRIBERS_FILE", "subscribers.json"))

# Webex markdown field max is ~7439 chars — keep below this for reliability.
WEBEX_MARKDOWN_SAFE = int(os.environ.get("WEBEX_MARKDOWN_SAFE", "7000"))
INSIGHTS_START = "## 🎥 Recent Meeting Insights"
INSIGHTS_END = "## 👥 Key Contacts"
REQUEST_TIMEOUT_SECONDS = 30


def get_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {WEBEX_BOT_TOKEN}",
        "Content-Type": "application/json",
    }


def load_subscribers() -> list[dict[str, str]]:
    """
    Support both formats:
    - {"emails": ["a@x.com", ...]}
    - {"subscribers": [{"roomName": "..."} | {"roomId": "..."} | {"toPersonEmail": "..."}]}
    """
    if not SUBSCRIBERS_FILE.exists():
        return []

    try:
        raw = json.loads(SUBSCRIBERS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"❌ Invalid JSON in {SUBSCRIBERS_FILE}: {exc}")
        return []

    targets: list[dict[str, str]] = []

    if isinstance(raw, dict) and isinstance(raw.get("emails"), list):
        for email in raw["emails"]:
            if isinstance(email, str) and email.strip():
                targets.append({"toPersonEmail": email.strip()})

    if isinstance(raw, list):
        items = raw
    elif isinstance(raw, dict) and isinstance(raw.get("subscribers"), list):
        items = raw["subscribers"]
    else:
        items = []

    for item in items:
        if not isinstance(item, dict):
            continue
        room_id = item.get("roomId") or item.get("room_id")
        room_name = item.get("roomName") or item.get("room_name") or item.get("roomTitle")
        email = item.get("toPersonEmail") or item.get("email")
        if isinstance(room_id, str) and room_id.strip():
            targets.append({"roomId": room_id.strip()})
        elif isinstance(room_name, str) and room_name.strip():
            targets.append({"roomName": room_name.strip()})
        elif isinstance(email, str) and email.strip():
            targets.append({"toPersonEmail": email.strip()})

    return targets


def send_message(target: dict[str, str], markdown: str) -> tuple[bool, str | None]:
    payload = {**target, "markdown": markdown}
    try:
        response = requests.post(
            f"{BASE_URL}/messages",
            headers=get_headers(),
            json=payload,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        return False, str(exc)

    if response.ok:
        return True, None

    detail: Any = None
    try:
        body = response.json()
        detail = body.get("message") or body.get("errors") or response.text[:500]
    except Exception:
        detail = (response.text or "")[:500] or "(empty response body)"
    return False, f"HTTP {response.status_code}: {detail}"


def resolve_room_id_from_name(room_name: str) -> str | None:
    try:
        response = requests.get(
            f"{BASE_URL}/rooms",
            headers={"Authorization": f"Bearer {WEBEX_BOT_TOKEN}"},
            params={"max": 1000},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        print(f"❌ Unable to list rooms for '{room_name}': {exc}")
        return None

    if not response.ok:
        print(f"❌ Unable to list rooms for '{room_name}': HTTP {response.status_code} {response.text[:300]}")
        return None

    rooms = response.json().get("items", [])
    matches = [
        r for r in rooms if str(r.get("title", "")).strip().lower() == room_name.strip().lower()
    ]
    if not matches:
        print(f"❌ No Webex room found with title '{room_name}'")
        return None
    if len(matches) > 1:
        print(f"❌ Multiple rooms found named '{room_name}'. Use roomId in subscribers.json.")
        return None
    return matches[0].get("id")


def resolve_target(target: dict[str, str]) -> dict[str, str] | None:
    if "roomName" not in target:
        return target
    room_id = resolve_room_id_from_name(target["roomName"])
    if not room_id:
        return None
    return {"roomId": room_id}


def load_recordings_insights() -> str:
    path = os.environ.get("RECORDINGS_INSIGHTS_PATH", "recordings_insights.md")
    if not path or not os.path.isfile(path):
        return ""
    try:
        with open(path, encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return ""


def merge_meeting_insights(static_report: str, insights_md: str) -> str:
    if not insights_md:
        return static_report
    block = f"{INSIGHTS_START}\n\n{insights_md}\n\n---\n\n"
    i0 = static_report.find(INSIGHTS_START)
    i1 = static_report.find(INSIGHTS_END)
    if i0 != -1 and i1 != -1 and i1 > i0:
        return static_report[:i0] + block + static_report[i1:]
    return static_report + "\n\n---\n\n" + insights_md + "\n"


def chunk_markdown(text: str, max_chars: int) -> list[str]:
    text = text.strip()
    if len(text) <= max_chars:
        return [text]
    chunks: list[str] = []
    rest = text
    while rest:
        if len(rest) <= max_chars:
            chunks.append(rest)
            break
        cut = rest.rfind("\n", 0, max_chars)
        if cut < max_chars // 2:
            cut = max_chars
        chunks.append(rest[:cut].rstrip())
        rest = rest[cut:].lstrip("\n")
    return chunks


def send_report_chunks(target: dict[str, str], markdown: str) -> tuple[bool, str | None]:
    parts = chunk_markdown(markdown, WEBEX_MARKDOWN_SAFE)
    for i, part in enumerate(parts):
        if len(parts) > 1:
            header = f"*(MGM Status Report — part {i + 1}/{len(parts)})*\n\n"
            part = header + part
        ok, err = send_message(target, part)
        if not ok:
            return False, err
    return True, None


def get_status_report() -> str:
    today = datetime.now().strftime("%B %d, %Y")
    time_now = datetime.now().strftime("%I:%M %p EST")
    return f"""# 📊 MGM Resorts - Consolidated Status Report
**Generated:** {today} at {time_now}
**Overall Status:** 🟡 YELLOW

---

## 📡 Data Sources Analyzed

| Source | Items | Period |
|--------|-------|--------|
| 🗨️ Webex Chat Messages | 500+ messages | Last 7 days |
| 🎥 Meeting Recordings | 1 recording | Last 7 days |
| 👥 MGM Spaces Monitored | 20+ spaces | Active |
| 👤 MGM Participants Tracked | 112 people | Cisco team |

**Spaces Monitored:**
- MGM LCS Space (External)
- MGM Firepower Pursuit / War Room
- MGM CX Delivery & Success Leadership
- MGM Digitized Delivery - ISE as Code
- MGM Palo TKO / ZScaler TKO
- MGM Architecture Huddle
- INT MGM TAC Support
- *...and 13 more*

---

## 🎯 Executive Summary

| Workstream | Status | Owner |
|------------|--------|-------|
| Firewall Migration | 🟡 PO pending MGM review | Mike Culp |
| Technical Discovery | 🟢 Kickoff today (Apr 10) | Team |
| PAN Support Gap | 🔴 **CRITICAL** - Expires Apr 15 | Jason Anderson |
| ISE Automation (ISAAC) | 🟢 Cert renewal in progress | Daniel |
| Secure Access | ⚪ Pending FW completion | TBD |

---

## ⚠️ CRITICAL ALERT: Palo Alto Support Expiry

**⏰ Deadline: April 15, 2026 (5 days)**

| Risk | Mitigation |
|------|------------|
| No 3rd party support after Apr 15 | "Frying Pan" space with ex-PAN engineers |
| Coverage gap during migration | Mike Culp 75-80% allocation |
| MGM declined PAN "scorched earth" offer | Strong Cisco partnership |

---

## 🎯 Recommended Next Steps

| # | Priority | Action | Target | Owner |
|---|----------|--------|--------|-------|
| 1 | 🔴 IMMEDIATE | Validate SCC access for Daniel/Mike Culp | Today | Mike Brown |
| 2 | 🔴 IMMEDIATE | Engage MGM security team with Nexar | Today | Jason Anderson |
| 3 | 🟡 HIGH | Finalize PAN support gap mitigation plan | Apr 14 | Team |
| 4 | 🟡 HIGH | Increase Mike Culp allocation to 75-80% | Apr 11 | Leadership |
| 5 | 🟡 HIGH | Schedule Netscout TAPs call (Scott/Deepak/Phil) | Apr 14 | Mike Brown |
| 6 | 🟢 MEDIUM | Complete ISE PSN05 certificate investigation | Apr 12 | Daniel |
| 7 | 🟢 MEDIUM | Identify Nexar 3rd party support group | Apr 11 | Jason |

---

## 📅 Timeline & Milestones

```
Apr 10 ━━🟢━━ Technical Discovery Kickoff ✓
Apr 11-12 ━━🟡━━ Complete Network/SCC Access
Apr 14 ━━🟡━━ Netscout TAPs Call
Apr 15 ━━🔴━━ ⚠️ PAN SUPPORT EXPIRES
Apr 17-18 ━━🟡━━ Migration Plan v1 Complete
Apr 21 ━━🟡━━ Resource Allocation Finalized
May 1 ━━⚪━━ Phase 1 Migration Start (Target)
```

---

## ⚠️ Risk Register

| ID | Severity | Risk | Mitigation | Owner |
|----|----------|------|------------|-------|
| R1 | 🔴 HIGH | PAN support expires Apr 15 - no 3rd party | Frying Pan space + internal experts | Jason |
| R2 | 🔴 HIGH | S2S VPN migration complexity | Mike Culp flagged early | Mike C |
| R3 | 🟡 MED | Resource constraints | Increase Culp to 75-80% | Leadership |
| R4 | 🟢 LOW | ISE PSN05 cert error | Investigation ongoing | Daniel |

---

## 🎥 Recent Meeting Insights

**Meetings Analyzed (Last 7 Days):**
- 📹 (INT) MGM Architecture Huddle - Apr 6, 2026

*Note: Enable Webex transcription for AI-powered meeting summaries*

---

## 👥 Key Contacts

| Role | Name | Focus |
|------|------|-------|
| Delivery Lead | Mike Brown | Overall coordination |
| CX Leadership | Jason Anderson | Executive alignment |
| Sales Lead | Paul Snow | Commercial |
| Technical Lead | Mike Culp | Firepower migration |
| ISE Lead | Daniel | ISAAC automation |

---

## Active workstreams

| Workstream | Status | Next Action |
|------------|--------|-------------|
| 🔥 Firepower Migration | Discovery | Complete SCC access |
| 🔐 ISE Automation | In Progress | PSN05 investigation |
| 📡 LCS R&S Support | Monitoring | Cat 3K syslog analysis |
| 🌐 Secure Access | Pending | Awaiting FW completion |

---

*📧 Reply "unsubscribe" to stop • Contact: michabr4@cisco.com*
*🤖 Auto-generated from Webex Spacelift + Recordings Analysis*
"""


def main() -> int:
    if not WEBEX_BOT_TOKEN:
        print("❌ Error: WEBEX_BOT_TOKEN not set")
        return 1

    subscribers = load_subscribers()
    if not subscribers:
        print("⚠️ No subscribers found")
        return 0

    print(f"📤 Sending MGM Status Report to {len(subscribers)} targets...")

    insights = load_recordings_insights()
    if insights:
        print(f"  📎 Merged recordings/AI insights ({len(insights)} chars from file)")
    else:
        print("  ℹ️ No recordings_insights.md — sending static template only")

    report = merge_meeting_insights(get_status_report(), insights)
    print(f"  📏 Full report length: {len(report)} chars (Webex limit per message: ~7439)")

    success = 0
    failed = 0
    for target in subscribers:
        resolved_target = resolve_target(target)
        if not resolved_target:
            failed += 1
            continue
        ok, err = send_report_chunks(resolved_target, report)
        target_label = (
            resolved_target.get("toPersonEmail")
            or resolved_target.get("roomId")
            or target.get("roomName")
            or "(unknown)"
        )
        if ok:
            print(f"  ✅ {target_label}")
            success += 1
        else:
            print(f"  ❌ {target_label} - {err}")
            failed += 1

    print(f"\n📊 Summary: {success} sent, {failed} failed")
    # Keep workflow green when at least one delivery succeeds.
    return 0 if success > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
