"""
Webex SpaceLift Integration for Digitized Delivery Status Bot

Pulls messages from all Webex spaces related to Digitized Delivery,
plus personal/1:1 spaces where Digitized Delivery is referenced.
Analyzes messages using AI to extract status updates, action items, and risks.

Requires a Webex Integration with these scopes:
- spark:rooms_read
- spark:messages_read
- spark:memberships_read
- spark:people_read
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Configuration
WEBEX_ACCESS_TOKEN = os.environ.get("WEBEX_ACCESS_TOKEN", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
BASE_URL = "https://webexapis.com/v1"

# Digitized Delivery space name patterns (case-insensitive matching)
DD_SPACE_PATTERNS = [
    "digitized delivery",
    "digital delivery",
    "ise as code",
    "isaac",
    "nac-parity",
    "nac parity",
]

# Keywords to detect DD references in personal/1:1 spaces
DD_KEYWORDS = [
    "digitized delivery",
    "digital delivery",
    "ise as code",
    "isaac",
    "nac-parity",
    "nac parity",
    "as-code",
    "as code",
    "ansible automation platform",
    "dda",
    "opencode",
    "nac parity",
]

# Key DD leaders — all messages from these people are included from DD spaces,
# and their personal spaces are scanned more broadly
DD_KEY_LEADERS = [
    "dhprajap@cisco.com",
    "michabr4@cisco.com",
]

# Output file for analysis results
OUTPUT_FILE = "spacelift_analysis.json"


class WebexSpaceLift:
    """Pull and analyze Webex space messages for Digitized Delivery."""

    def __init__(self, access_token: str = None):
        self.access_token = access_token or WEBEX_ACCESS_TOKEN
        if not self.access_token:
            raise ValueError("Webex access token required")

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def _get_paginated(self, url: str, params: dict, max_items: int = 1000) -> List[Dict]:
        """Fetch paginated results from Webex API."""
        all_items = []
        while url and len(all_items) < max_items:
            response = requests.get(url, headers=self._headers(), params=params)
            if response.status_code != 200:
                print(f"  API error {response.status_code}: {response.text[:200]}")
                break
            data = response.json()
            items = data.get("items", [])
            all_items.extend(items)
            # Follow pagination link
            url = None
            params = {}
            link_header = response.headers.get("Link", "")
            if 'rel="next"' in link_header:
                url = link_header.split(";")[0].strip("<> ")
        return all_items[:max_items]

    # ── Space Discovery ──────────────────────────────────────────────

    def get_all_rooms(self) -> List[Dict]:
        """Get all Webex rooms/spaces the user is a member of."""
        print("📡 Fetching all Webex spaces...")
        rooms = self._get_paginated(
            f"{BASE_URL}/rooms",
            params={"max": 200, "sortBy": "lastactivity"},
        )
        print(f"  Found {len(rooms)} total spaces")
        return rooms

    def find_dd_spaces(self, rooms: List[Dict]) -> List[Dict]:
        """Filter rooms to those matching Digitized Delivery patterns."""
        dd_spaces = []
        for room in rooms:
            title = room.get("title", "").lower()
            if any(pattern in title for pattern in DD_SPACE_PATTERNS):
                dd_spaces.append(room)
        print(f"🎯 Found {len(dd_spaces)} Digitized Delivery spaces:")
        for s in dd_spaces:
            print(f"  - {s.get('title')}")
        return dd_spaces

    def find_personal_spaces(self, rooms: List[Dict]) -> List[Dict]:
        """Find direct/1:1 and group spaces (non-DD-titled) for keyword scanning."""
        personal = []
        for room in rooms:
            title = room.get("title", "").lower()
            room_type = room.get("type", "")
            # Skip spaces already matched as DD spaces
            if any(pattern in title for pattern in DD_SPACE_PATTERNS):
                continue
            # Include direct (1:1) spaces and group spaces
            if room_type in ("direct", "group"):
                personal.append(room)
        print(f"👤 Found {len(personal)} personal/other spaces to scan for DD references")
        return personal

    # ── Message Pulling ──────────────────────────────────────────────

    def get_messages(self, room_id: str, days_back: int = 7, max_messages: int = 500) -> List[Dict]:
        """Get messages from a specific room within the time window."""
        before = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
        # Webex API doesn't have a direct 'after' param for messages list,
        # so we pull recent and filter by date
        messages = self._get_paginated(
            f"{BASE_URL}/messages",
            params={"roomId": room_id, "max": 200, "before": before},
            max_items=max_messages,
        )
        cutoff = datetime.utcnow() - timedelta(days=days_back)
        filtered = []
        for msg in messages:
            created = msg.get("created", "")
            try:
                msg_time = datetime.strptime(created[:19], "%Y-%m-%dT%H:%M:%S")
                if msg_time >= cutoff:
                    filtered.append(msg)
            except (ValueError, TypeError):
                continue
        return filtered

    def pull_dd_space_messages(self, dd_spaces: List[Dict], days_back: int = 7) -> List[Dict]:
        """Pull all messages from Digitized Delivery spaces."""
        all_messages = []
        for space in dd_spaces:
            title = space.get("title", "")
            room_id = space.get("id")
            print(f"\n📨 Pulling messages from: {title}")
            messages = self.get_messages(room_id, days_back=days_back)
            for msg in messages:
                msg["_space_title"] = title
                msg["_space_type"] = "dd_space"
            all_messages.extend(messages)
            print(f"  → {len(messages)} messages (last {days_back} days)")
        print(f"\n📊 Total DD space messages: {len(all_messages)}")
        return all_messages

    def scan_personal_spaces_for_dd(self, personal_spaces: List[Dict], days_back: int = 7) -> List[Dict]:
        """Scan personal/other spaces for messages referencing Digitized Delivery."""
        dd_references = []
        scanned = 0
        for space in personal_spaces:
            title = space.get("title", "")
            room_id = space.get("id")
            messages = self.get_messages(room_id, days_back=days_back, max_messages=100)
            scanned += 1

            for msg in messages:
                text = msg.get("text", "").lower()
                if any(kw in text for kw in DD_KEYWORDS):
                    msg["_space_title"] = title
                    msg["_space_type"] = "personal_reference"
                    dd_references.append(msg)

            if scanned % 25 == 0:
                print(f"  Scanned {scanned}/{len(personal_spaces)} personal spaces...")

        print(f"🔍 Found {len(dd_references)} DD references in {scanned} personal spaces")
        return dd_references

    # ── Space Members ────────────────────────────────────────────────

    def get_space_members(self, room_id: str) -> List[Dict]:
        """Get members of a specific space."""
        return self._get_paginated(
            f"{BASE_URL}/memberships",
            params={"roomId": room_id, "max": 100},
        )

    def get_all_dd_participants(self, dd_spaces: List[Dict]) -> List[str]:
        """Get unique list of all participants across DD spaces."""
        participants = set()
        for space in dd_spaces:
            members = self.get_space_members(space.get("id"))
            for m in members:
                email = m.get("personEmail", "")
                if email and not email.endswith("@webex.bot"):
                    participants.add(email)
        print(f"👥 Total DD participants: {len(participants)}")
        return sorted(list(participants))

    # ── AI Analysis ──────────────────────────────────────────────────

    def analyze_messages_with_ai(self, messages: List[Dict], space_title: str = "All Spaces") -> Dict:
        """Use AI to analyze messages and extract key information."""
        if not OPENAI_API_KEY:
            return self._basic_message_analysis(messages)

        # Build message text for analysis
        msg_text = ""
        for msg in messages[:200]:  # Limit to avoid token limits
            sender = msg.get("personEmail", "unknown")
            text = msg.get("text", "")
            timestamp = msg.get("created", "")[:10]
            space = msg.get("_space_title", "")
            if text:
                msg_text += f"[{timestamp}] [{space}] {sender}: {text}\n"

        if not msg_text:
            return {"decisions": [], "action_items": [], "risks": [], "updates": [], "next_steps": []}

        try:
            import openai
            client = openai.OpenAI(api_key=OPENAI_API_KEY)

            prompt = f"""Analyze these Webex messages from Digitized Delivery spaces and extract:
1. Key decisions made
2. Action items (with owners if mentioned)
3. Risks or concerns raised
4. Important status updates
5. Next steps discussed

Focus on: ISE as Code (ISAAC), Network Automation, Infrastructure as Code, CI/CD, and any customer delivery updates.

IMPORTANT RULES:
- Summarize insights at the milestone/theme level. Do NOT quote or paraphrase any individual participant's messages.
- Do NOT include participant names, email addresses, or direct quotes in any output field.
- Write each item as a concise, professional status update (e.g. "Certificate renewal completed across all 6 lab nodes").

Messages:
{msg_text[:15000]}

Provide a structured summary in JSON format:
{{
    "decisions": ["decision 1", "decision 2"],
    "action_items": ["action 1", "action 2"],
    "risks": ["risk 1", "risk 2"],
    "updates": ["update 1", "update 2"],
    "next_steps": ["step 1", "step 2"],
    "workstream_status": {{
        "workstream_name": "status description"
    }}
}}
"""
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )

            result = response.choices[0].message.content
            # Try to parse JSON from the response
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                # Try to find JSON in the response
                start = result.find("{")
                end = result.rfind("}") + 1
                if start >= 0 and end > start:
                    return json.loads(result[start:end])
                return self._basic_message_analysis(messages)

        except Exception as e:
            print(f"AI analysis failed: {e}")
            return self._basic_message_analysis(messages)

    def _basic_message_analysis(self, messages: List[Dict]) -> Dict:
        """Basic keyword-based analysis when AI is not available.
        Produces clean summaries without participant names or raw quotes."""
        action_keywords = ["action", "todo", "will do", "need to", "should", "must", "requesting", "can you"]
        risk_keywords = ["risk", "concern", "issue", "problem", "blocker", "worried", "error", "not working"]
        update_keywords = ["update", "completed", "done", "finished", "progress", "working on", "successfully"]
        decision_keywords = ["decided", "agreed", "confirmed", "approved", "will go with", "plan is"]

        decisions = set()
        action_items = set()
        risks = set()
        updates = set()

        for msg in messages:
            text = msg.get("text", "")
            if not text:
                continue
            space = msg.get("_space_title", "DD Space")
            text_lower = text.lower()

            # Extract a clean summary phrase — first sentence, no names
            summary = text.split("\n")[0].strip()
            if len(summary) > 120:
                summary = summary[:117] + "..."

            if any(k in text_lower for k in decision_keywords):
                decisions.add(f"[{space}] {summary}")
            if any(k in text_lower for k in action_keywords):
                action_items.add(f"[{space}] {summary}")
            if any(k in text_lower for k in risk_keywords):
                risks.add(f"[{space}] {summary}")
            if any(k in text_lower for k in update_keywords):
                updates.add(f"[{space}] {summary}")

        return {
            "decisions": sorted(list(decisions))[:10],
            "action_items": sorted(list(action_items))[:10],
            "risks": sorted(list(risks))[:10],
            "updates": sorted(list(updates))[:10],
            "next_steps": [],
            "workstream_status": {},
        }

    # ── Full Pipeline ────────────────────────────────────────────────

    def run_full_analysis(self, days_back: int = 7, scan_personal: bool = True) -> Dict:
        """
        Run the complete SpaceLift analysis pipeline:
        1. Discover DD spaces
        2. Pull DD space messages
        3. Scan personal spaces for DD references
        4. Analyze with AI
        5. Return structured results
        """
        print("=" * 60)
        print(f"🚀 Digitized Delivery SpaceLift Analysis (last {days_back} days)")
        print("=" * 60)

        # Step 1: Discover spaces
        all_rooms = self.get_all_rooms()
        dd_spaces = self.find_dd_spaces(all_rooms)

        # Step 2: Pull DD space messages
        dd_messages = self.pull_dd_space_messages(dd_spaces, days_back=days_back)

        # Step 3: Scan personal spaces
        personal_refs = []
        if scan_personal:
            personal_spaces = self.find_personal_spaces(all_rooms)
            personal_refs = self.scan_personal_spaces_for_dd(personal_spaces, days_back=days_back)

        all_messages = dd_messages + personal_refs

        # Step 4: Get participants
        participants = self.get_all_dd_participants(dd_spaces)

        # Step 5: Analyze
        print("\n🧠 Analyzing messages...")
        analysis = self.analyze_messages_with_ai(all_messages)

        # Step 6: Build result
        spaces_summary = []
        for s in dd_spaces:
            space_msgs = [m for m in dd_messages if m.get("_space_title") == s.get("title")]
            spaces_summary.append({
                "title": s.get("title"),
                "message_count": len(space_msgs),
                "type": "dd_space",
            })

        result = {
            "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "period_days": days_back,
            "spaces_monitored": spaces_summary,
            "total_dd_messages": len(dd_messages),
            "total_personal_refs": len(personal_refs),
            "total_messages_analyzed": len(all_messages),
            "participants_tracked": len(participants),
            "participants": participants,
            "analysis": analysis,
        }

        # Save to file
        with open(OUTPUT_FILE, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Analysis saved to {OUTPUT_FILE}")

        return result

    def format_for_report(self, result: Dict) -> str:
        """Format analysis results for inclusion in the daily status report."""
        analysis = result.get("analysis", {})
        spaces = result.get("spaces_monitored", [])

        output = ""

        # Data sources table
        output += "## 📡 Data Sources Analyzed\n\n"
        output += "| Source | Items | Period |\n"
        output += "|--------|-------|--------|\n"
        output += f"| 🗨️ Webex Chat Messages | {result.get('total_messages_analyzed', 0)} messages | Last {result.get('period_days', 7)} days |\n"
        output += f"| 👥 DD Spaces Monitored | {len(spaces)} spaces | Active |\n"
        output += f"| 👤 DD Participants Tracked | {result.get('participants_tracked', 0)} people | Cisco team |\n"
        output += f"| 🔍 Personal Space References | {result.get('total_personal_refs', 0)} messages | Last {result.get('period_days', 7)} days |\n"
        output += "\n**Spaces Monitored:**\n"
        for s in spaces:
            output += f"- {s['title']} ({s['message_count']} messages)\n"
        output += "\n---\n\n"

        # Workstream status
        ws_status = analysis.get("workstream_status", {})
        if ws_status:
            output += "## 🎯 Workstream Status\n\n"
            output += "| Workstream | Status |\n"
            output += "|------------|--------|\n"
            for ws, status in ws_status.items():
                output += f"| {ws} | {status} |\n"
            output += "\n---\n\n"

        # Updates
        updates = analysis.get("updates", [])
        if updates:
            output += "## 📋 Key Updates\n\n"
            for u in updates[:8]:
                output += f"- {u}\n"
            output += "\n---\n\n"

        # Action items
        actions = analysis.get("action_items", [])
        if actions:
            output += "## 🎯 Action Items\n\n"
            for i, a in enumerate(actions[:8], 1):
                output += f"| {i} | {a} |\n"
            output += "\n---\n\n"

        # Risks
        risks = analysis.get("risks", [])
        if risks:
            output += "## ⚠️ Risks & Concerns\n\n"
            for r in risks[:5]:
                output += f"- ⚠️ {r}\n"
            output += "\n---\n\n"

        # Decisions
        decisions = analysis.get("decisions", [])
        if decisions:
            output += "## ✅ Decisions Made\n\n"
            for d in decisions[:5]:
                output += f"- {d}\n"
            output += "\n---\n\n"

        # Next steps
        next_steps = analysis.get("next_steps", [])
        if next_steps:
            output += "## 🔜 Next Steps\n\n"
            for s in next_steps[:5]:
                output += f"- {s}\n"
            output += "\n"

        return output


def load_spacelift_export(filepath: str) -> List[Dict]:
    """Load a SpaceLift JSON export file and return messages."""
    with open(filepath, "r") as f:
        return json.load(f)


def analyze_export(filepath: str) -> Dict:
    """Analyze a SpaceLift export file without needing live Webex API access."""
    messages = load_spacelift_export(filepath)

    # Organize by space
    spaces = {}
    for msg in messages:
        space = msg.get("space", "Unknown")
        if space not in spaces:
            spaces[space] = []
        spaces[space].append(msg)

    # Identify DD spaces
    dd_spaces = {}
    personal_refs = []
    for space, msgs in spaces.items():
        space_lower = space.lower()
        if any(p in space_lower for p in DD_SPACE_PATTERNS):
            dd_spaces[space] = msgs
        else:
            # Check for DD keyword references
            for msg in msgs:
                text = msg.get("text", "").lower()
                if any(kw in text for kw in DD_KEYWORDS):
                    personal_refs.append(msg)

    # Get unique participants
    participants = set()
    for msgs in dd_spaces.values():
        for msg in msgs:
            sender = msg.get("sender", "")
            if sender:
                participants.add(sender)

    spaces_summary = []
    for title, msgs in dd_spaces.items():
        spaces_summary.append({
            "title": title,
            "message_count": len(msgs),
            "type": "dd_space",
        })

    # Flatten all DD messages
    all_dd_msgs = []
    for msgs in dd_spaces.values():
        for msg in msgs:
            all_dd_msgs.append({
                "text": msg.get("text", ""),
                "personEmail": msg.get("sender", ""),
                "created": msg.get("timestamp", ""),
                "_space_title": msg.get("space", ""),
            })

    result = {
        "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "period_days": "all (from export)",
        "spaces_monitored": spaces_summary,
        "total_dd_messages": len(all_dd_msgs),
        "total_personal_refs": len(personal_refs),
        "total_messages_analyzed": len(all_dd_msgs) + len(personal_refs),
        "participants_tracked": len(participants),
        "participants": sorted(list(participants)),
        "analysis": {},
    }

    # Try AI analysis if available
    if OPENAI_API_KEY:
        spacelift = WebexSpaceLift.__new__(WebexSpaceLift)
        spacelift.access_token = ""
        result["analysis"] = spacelift.analyze_messages_with_ai(all_dd_msgs)
    else:
        spacelift = WebexSpaceLift.__new__(WebexSpaceLift)
        spacelift.access_token = ""
        result["analysis"] = spacelift._basic_message_analysis(all_dd_msgs)

    # Save
    with open(OUTPUT_FILE, "w") as f:
        json.dump(result, f, indent=2)
    print(f"💾 Export analysis saved to {OUTPUT_FILE}")

    return result


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Webex SpaceLift for Digitized Delivery")
    parser.add_argument("--days", "-d", type=int, default=7, help="Days to look back")
    parser.add_argument("--token", "-t", help="Webex access token")
    parser.add_argument("--no-personal", action="store_true", help="Skip scanning personal spaces")
    parser.add_argument("--export", "-e", help="Analyze a SpaceLift JSON export file instead of live API")
    parser.add_argument("--list-spaces", action="store_true", help="Just list DD spaces, don't pull messages")

    args = parser.parse_args()

    # If analyzing an export file
    if args.export:
        print(f"📁 Analyzing SpaceLift export: {args.export}")
        result = analyze_export(args.export)
        spacelift = WebexSpaceLift.__new__(WebexSpaceLift)
        spacelift.access_token = ""
        report = spacelift.format_for_report(result)
        print("\n" + report)
        return

    # Live API mode
    token = args.token or WEBEX_ACCESS_TOKEN
    if not token:
        print("❌ Set WEBEX_ACCESS_TOKEN or use --token")
        print("\nTo get a token:")
        print("1. Go to developer.webex.com/my-apps")
        print("2. Create an Integration with rooms/messages scopes")
        print("3. Complete OAuth flow to get access token")
        exit(1)

    spacelift = WebexSpaceLift(token)

    if args.list_spaces:
        rooms = spacelift.get_all_rooms()
        dd_spaces = spacelift.find_dd_spaces(rooms)
        return

    result = spacelift.run_full_analysis(
        days_back=args.days,
        scan_personal=not args.no_personal,
    )
    report = spacelift.format_for_report(result)
    print("\n" + report)


if __name__ == "__main__":
    main()
