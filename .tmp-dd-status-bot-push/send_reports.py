"""
Digitized Delivery Status Report - GitHub Actions Script
Sends daily status reports to all subscribers via Webex.

Builds report from:
1. spacelift_analysis.json (SpaceLift message analysis)
2. recordings_analysis.json (optional meeting insights)

Uses a minimal fallback when live data is unavailable (no stale hard-coded content).
"""

import os
import json
import requests
from datetime import datetime

# Configuration
WEBEX_BOT_TOKEN = os.environ.get("WEBEX_BOT_TOKEN", "")
BASE_URL = "https://webexapis.com/v1"
SUBSCRIBERS_FILE = "subscribers.json"
SPACELIFT_FILE = "spacelift_analysis.json"
RECORDINGS_FILE = "recordings_analysis.json"


def load_subscribers():
    """Load subscribers from JSON file."""
    if os.path.exists(SUBSCRIBERS_FILE):
        with open(SUBSCRIBERS_FILE, "r") as f:
            return json.load(f)
    return {"emails": []}


def load_spacelift_analysis():
    """Load SpaceLift analysis results if available."""
    if os.path.exists(SPACELIFT_FILE):
        with open(SPACELIFT_FILE, "r") as f:
            return json.load(f)
    return None


def load_recordings_analysis():
    if os.path.exists(RECORDINGS_FILE):
        with open(RECORDINGS_FILE, "r") as f:
            return json.load(f)
    return None


def get_headers():
    return {
        "Authorization": f"Bearer {WEBEX_BOT_TOKEN}",
        "Content-Type": "application/json",
    }


def send_message(email: str, markdown: str):
    """Send a message to a person via Webex. Splits long messages automatically."""
    max_len = 7000

    if len(markdown) <= max_len:
        payload = {"toPersonEmail": email, "markdown": markdown}
        response = requests.post(f"{BASE_URL}/messages", headers=get_headers(), json=payload)
        if response.status_code != 200:
            print(f"    Webex API {response.status_code}: {response.text[:200]}")
        return response.status_code == 200

    sections = markdown.split("\n---\n")
    chunks = []
    current = ""
    for section in sections:
        candidate = current + ("\n---\n" if current else "") + section
        if len(candidate) > max_len and current:
            chunks.append(current)
            current = section
        else:
            current = candidate
    if current:
        chunks.append(current)

    print(f"    Report split into {len(chunks)} messages ({len(markdown)} chars total)")
    all_ok = True
    for i, chunk in enumerate(chunks):
        payload = {"toPersonEmail": email, "markdown": chunk}
        response = requests.post(f"{BASE_URL}/messages", headers=get_headers(), json=payload)
        if response.status_code != 200:
            print(f"    Webex API {response.status_code} on part {i + 1}: {response.text[:200]}")
            all_ok = False
    return all_ok


def _analysis_has_content(analysis: dict) -> bool:
    if not analysis:
        return False
    for key in ("updates", "action_items", "risks", "decisions", "next_steps"):
        if analysis.get(key):
            return True
    return bool(analysis.get("workstream_status"))


def has_live_data(spacelift: dict) -> bool:
    if spacelift.get("data_available") is False:
        return False
    if spacelift.get("total_messages_analyzed", 0) > 0:
        return True
    return _analysis_has_content(spacelift.get("analysis", {}))


def _append_section(report: str, title: str, items: list, bullet: str = "- ") -> str:
    if not items:
        return report
    report += f"## {title}\n\n"
    for item in items[:10]:
        report += f"{bullet}{item}\n"
    report += "\n---\n\n"
    return report


def _append_recordings_section(report: str) -> str:
    rec_data = load_recordings_analysis()
    if not rec_data or not rec_data.get("meetings_analyzed"):
        return report

    report += "## Recent Meeting Insights\n\n"
    report += f"**Meetings analyzed:** {len(rec_data['meetings_analyzed'])}\n\n"
    for m in rec_data["meetings_analyzed"][:8]:
        status = "transcript" if m.get("has_transcript") else "no transcript"
        report += f"- {m.get('date', '')}: {m.get('title', 'Unknown')} ({status})\n"

    for title, key in [
        ("Meeting decisions", "decisions"),
        ("Meeting action items", "action_items"),
        ("Meeting risks", "risks"),
    ]:
        items = rec_data.get(key, [])
        if items:
            report += f"\n**{title}:**\n"
            for item in items[:5]:
                report += f"- {item}\n"

    report += "\n*Enable Webex transcription for richer meeting summaries.*\n\n---\n\n"
    return report


def build_dynamic_report(spacelift: dict) -> str:
    """Build report from SpaceLift AI analysis only (no hard-coded workstreams)."""
    today = datetime.now().strftime("%B %d, %Y")
    time_now = datetime.now().strftime("%I:%M %p EST")
    analysis = spacelift.get("analysis", {})
    spaces = spacelift.get("spaces_monitored", [])
    period = spacelift.get("period_days", 7)

    report = f"""# Digitized Delivery - Consolidated Status Report
**Generated:** {today} at {time_now}

---

## Data Sources Analyzed

| Source | Items | Period |
|--------|-------|--------|
| Webex chat messages | {spacelift.get('total_messages_analyzed', 0)} | Last {period} days |
| DD spaces monitored | {len(spaces)} | Active |
| Participants tracked | {spacelift.get('participants_tracked', 0)} | Cisco team |
| Personal space DD refs | {spacelift.get('total_personal_refs', 0)} | Last {period} days |

"""
    if spaces:
        report += "**Spaces monitored:**\n"
        for s in spaces:
            report += f"- {s.get('title', 'Unknown')} ({s.get('message_count', 0)} messages)\n"
        report += "\n---\n\n"

    ws_status = analysis.get("workstream_status", {})
    if ws_status:
        report += "## Workstream Status\n\n"
        report += "| Workstream | Status |\n|------------|--------|\n"
        for ws, status in ws_status.items():
            report += f"| {ws} | {status} |\n"
        report += "\n---\n\n"

    report = _append_section(report, "Key Updates", analysis.get("updates", []))
    report = _append_section(report, "Action Items", analysis.get("action_items", []), "- [ ] ")
    report = _append_section(report, "Risks and Concerns", analysis.get("risks", []))
    report = _append_section(report, "Decisions Made", analysis.get("decisions", []))
    report = _append_section(report, "Next Steps", analysis.get("next_steps", []))

    report = _append_recordings_section(report)

    report += '*Reply "unsubscribe" to stop. Contact: michabr4@cisco.com*\n'
    report += "*Auto-generated from Webex SpaceLift + Recordings Analysis*\n"
    return report


def get_unavailable_report(spacelift: dict = None) -> str:
    """Minimal fallback when live Webex data is unavailable."""
    today = datetime.now().strftime("%B %d, %Y")
    time_now = datetime.now().strftime("%I:%M %p EST")
    detail = ""
    if spacelift and spacelift.get("error"):
        detail = f"\n\n**Details:** {spacelift['error']}"

    return f"""# Digitized Delivery - Status Report
**Generated:** {today} at {time_now}

---

**Live data unavailable today** — Webex token may need refresh. Contact michabr4@cisco.com to renew.{detail}

---

*Reply "unsubscribe" to stop. Contact: michabr4@cisco.com*
"""


def get_status_report():
    """Generate report from live analysis or minimal fallback."""
    spacelift = load_spacelift_analysis()
    if spacelift and has_live_data(spacelift):
        print("Building dynamic report from SpaceLift analysis...")
        return build_dynamic_report(spacelift)

    if spacelift:
        print("SpaceLift file present but no live data; using unavailable fallback")
    else:
        print("No SpaceLift analysis file; using unavailable fallback")
    return get_unavailable_report(spacelift)


def main():
    """Send reports to all subscribers."""
    if not WEBEX_BOT_TOKEN:
        print("Error: WEBEX_BOT_TOKEN not set")
        exit(1)

    subscribers = load_subscribers()
    emails = subscribers.get("emails", [])

    if not emails:
        print("No subscribers found")
        exit(0)

    print(f"Sending Digitized Delivery Status Report to {len(emails)} subscribers...")

    report = get_status_report()
    success = 0
    failed = 0

    for email in emails:
        try:
            if send_message(email, report):
                print(f"  OK {email}")
                success += 1
            else:
                print(f"  FAIL {email} - API error")
                failed += 1
        except Exception as e:
            print(f"  FAIL {email} - {e}")
            failed += 1

    print(f"\nSummary: {success} sent, {failed} failed")

    if failed > 0:
        exit(1)


if __name__ == "__main__":
    main()
