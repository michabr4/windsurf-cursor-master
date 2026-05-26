"""
Webex Recordings Analyzer for Digitized Delivery Status Reports

Pulls meeting recordings and transcripts from DD participants,
extracts key information using AI, and incorporates into daily status reports.

Requires a Webex Integration with these scopes:
- spark:recordings_read
- meeting:recordings_read  
- meeting:transcripts_read
- spark-admin:recordings_read (optional, for org-wide access)
- meeting:schedules_read
- meeting:participants_read
- spark:people_read
- spark:rooms_read
- spark:memberships_read
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

# Search terms for filtering recordings
DD_SEARCH_TERMS = [
    "digitized delivery",
    "digital delivery",
    "ise as code",
    "isaac",
    "nac-parity",
    "nac parity",
    "ges delivery",
]

# Key DD leaders — ALL their recordings/meetings are included (no keyword filter)
DD_KEY_LEADERS = [
    "dhprajap@cisco.com",
    "michabr4@cisco.com",
]


class WebexRecordingsAnalyzer:
    """Analyze Webex recordings for Digitized Delivery meetings."""
    
    # Known DD participants to track their meetings too
    DD_PARTICIPANTS = [
        "michabr4@cisco.com",
        "dhprajap@cisco.com",
    ]
    
    # DD-related Webex spaces to source participant lists from
    DD_SPACES = [
        "GES Digitized Delivery",
        "MGM Digitized Delivery",
        "Digitized Delivery",
    ]
    
    def __init__(self, access_token: str = None):
        self.access_token = access_token or WEBEX_ACCESS_TOKEN
        if not self.access_token:
            raise ValueError("Webex access token required")
        self.dd_participant_ids = []
    
    def _headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def get_dd_space_members(self) -> List[str]:
        """
        Get all members from DD-related Webex spaces.
        Returns list of email addresses.
        """
        dd_members = set(self.DD_PARTICIPANTS)
        
        # Get all rooms
        response = requests.get(
            f"{BASE_URL}/rooms",
            headers=self._headers(),
            params={"max": 200}
        )
        
        if response.status_code != 200:
            print(f"Could not fetch rooms: {response.status_code}")
            return list(dd_members)
        
        rooms = response.json().get("items", [])
        
        # Find DD-related spaces
        for room in rooms:
            title = room.get("title", "")
            if any(dd in title.upper() for dd in ["DIGITIZED DELIVERY", "DIGITAL DELIVERY", "ISE AS CODE", "ISAAC"]):
                room_id = room.get("id")
                
                # Get members of this space
                members_response = requests.get(
                    f"{BASE_URL}/memberships",
                    headers=self._headers(),
                    params={"roomId": room_id, "max": 100}
                )
                
                if members_response.status_code == 200:
                    members = members_response.json().get("items", [])
                    for member in members:
                        email = member.get("personEmail", "")
                        if email and "@cisco.com" in email:
                            dd_members.add(email)
                    print(f"  Found {len(members)} members in '{title}'")
        
        print(f"Total DD participants identified: {len(dd_members)}")
        return list(dd_members)
    
    def get_recordings_for_person(self, email: str, days_back: int = 7) -> List[Dict]:
        """Get recordings hosted by a specific person."""
        from_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%dT00:00:00Z")
        to_date = datetime.utcnow().strftime("%Y-%m-%dT23:59:59Z")
        
        params = {
            "from": from_date,
            "to": to_date,
            "hostEmail": email,
            "max": 50
        }
        
        response = requests.get(
            f"{BASE_URL}/recordings",
            headers=self._headers(),
            params=params
        )
        
        if response.status_code == 200:
            return response.json().get("items", [])
        return []

    def get_meetings_participated(self, email: str, days_back: int = 7) -> List[Dict]:
        """Get meetings where a person participated (attended, not just hosted)."""
        from_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%dT00:00:00Z")
        to_date = datetime.utcnow().strftime("%Y-%m-%dT23:59:59Z")
        meetings = []

        # List meetings in the date range
        params = {
            "from": from_date,
            "to": to_date,
            "meetingType": "meeting",
            "state": "ended",
            "max": 100,
        }
        response = requests.get(
            f"{BASE_URL}/meetings",
            headers=self._headers(),
            params=params,
        )
        if response.status_code != 200:
            return []

        all_meetings = response.json().get("items", [])

        # Check participant lists for each meeting
        for mtg in all_meetings:
            meeting_id = mtg.get("id")
            if not meeting_id:
                continue
            part_resp = requests.get(
                f"{BASE_URL}/meetingParticipants",
                headers=self._headers(),
                params={"meetingId": meeting_id, "max": 200},
            )
            if part_resp.status_code != 200:
                continue
            participants = part_resp.json().get("items", [])
            emails = [p.get("email", "").lower() for p in participants]
            if email.lower() in emails:
                mtg["_participant_emails"] = emails
                meetings.append(mtg)

        return meetings

    def get_recordings_for_meeting(self, meeting_id: str) -> List[Dict]:
        """Get recordings for a specific meeting ID."""
        response = requests.get(
            f"{BASE_URL}/recordings",
            headers=self._headers(),
            params={"meetingId": meeting_id, "max": 10},
        )
        if response.status_code == 200:
            return response.json().get("items", [])
        return []
    
    def get_recordings(self, days_back: int = 7, include_participants: bool = True) -> List[Dict]:
        """
        Get recordings from the past N days matching DD search terms.
        Includes recordings from DD space participants if include_participants=True.
        """
        from_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%dT00:00:00Z")
        to_date = datetime.utcnow().strftime("%Y-%m-%dT23:59:59Z")
        
        all_recordings = []
        seen_ids = set()
        
        # Get my own recordings
        params = {
            "from": from_date,
            "to": to_date,
            "max": 100
        }
        
        response = requests.get(
            f"{BASE_URL}/recordings",
            headers=self._headers(),
            params=params
        )
        
        if response.status_code == 200:
            my_recordings = response.json().get("items", [])
            for r in my_recordings:
                if r.get("id") not in seen_ids:
                    all_recordings.append(r)
                    seen_ids.add(r.get("id"))
            print(f"Found {len(my_recordings)} of my recordings")
        
        # Get ALL recordings from key DD leaders (hosted + participated)
        print("\n🔍 Pulling ALL recordings from DD key leaders...")
        for email in DD_KEY_LEADERS:
            if email == "michabr4@cisco.com":
                continue  # Already got mine above

            # 1. Recordings they hosted
            person_recordings = self.get_recordings_for_person(email, days_back)
            added_hosted = 0
            for r in person_recordings:
                if r.get("id") not in seen_ids:
                    r["_source_email"] = email
                    r["_include_reason"] = "key_leader_hosted"
                    all_recordings.append(r)
                    seen_ids.add(r.get("id"))
                    added_hosted += 1
            if added_hosted:
                print(f"  📌 {email}: {added_hosted} hosted recordings")

            # 2. Meetings they participated in (check for recordings)
            print(f"  🔎 Checking meetings {email} participated in...")
            participated_meetings = self.get_meetings_participated(email, days_back)
            added_participated = 0
            for mtg in participated_meetings:
                meeting_id = mtg.get("id")
                mtg_recordings = self.get_recordings_for_meeting(meeting_id)
                for r in mtg_recordings:
                    if r.get("id") not in seen_ids:
                        r["_source_email"] = email
                        r["_include_reason"] = "key_leader_participated"
                        r["_meeting_title"] = mtg.get("title", "")
                        all_recordings.append(r)
                        seen_ids.add(r.get("id"))
                        added_participated += 1
            if added_participated:
                print(f"  📌 {email}: {added_participated} recordings from meetings attended")
            if not added_hosted and not added_participated:
                print(f"  ℹ️  {email}: no recordings found (hosted or participated)")
        
        # Get recordings from other DD participants (keyword-filtered)
        if include_participants:
            print("\n🔍 Scanning other DD participant recordings...")
            dd_members = self.get_dd_space_members()
            
            for email in dd_members:
                if email in DD_KEY_LEADERS:
                    continue  # Already got all their recordings
                
                person_recordings = self.get_recordings_for_person(email, days_back)
                dd_recordings = [
                    r for r in person_recordings
                    if any(term in r.get("topic", "").lower() for term in DD_SEARCH_TERMS)
                ]
                
                for r in dd_recordings:
                    if r.get("id") not in seen_ids:
                        r["_source_email"] = email
                        r["_include_reason"] = "dd_keyword_match"
                        all_recordings.append(r)
                        seen_ids.add(r.get("id"))
                
                if dd_recordings:
                    print(f"  Found {len(dd_recordings)} DD recordings from {email}")
        
        print(f"\n📹 Total recordings collected: {len(all_recordings)}")
        # Note: key leader recordings are included even without DD keywords
        return all_recordings
    
    def get_transcript(self, recording_id: str) -> Optional[str]:
        """Get transcript for a specific recording."""
        response = requests.get(
            f"{BASE_URL}/recordings/{recording_id}/transcripts",
            headers=self._headers()
        )
        
        if response.status_code != 200:
            print(f"No transcript available for {recording_id}")
            return None
        
        transcripts = response.json().get("items", [])
        if not transcripts:
            return None
        
        # Get the transcript content
        transcript_id = transcripts[0].get("id")
        content_response = requests.get(
            f"{BASE_URL}/recordings/{recording_id}/transcripts/{transcript_id}/download",
            headers=self._headers()
        )
        
        if content_response.status_code == 200:
            return content_response.text
        
        return None
    
    def analyze_transcript_with_ai(self, transcript: str, meeting_title: str) -> Dict:
        """Use AI to extract key information from transcript."""
        if not OPENAI_API_KEY:
            return self._basic_analysis(transcript)
        
        try:
            import openai
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            
            prompt = f"""Analyze this Digitized Delivery meeting transcript and extract:
1. Key decisions made
2. Action items (with owners if mentioned)
3. Risks or concerns raised
4. Important updates or status changes
5. Next steps discussed

Focus on: ISE as Code (ISAAC), Network Automation, Infrastructure as Code, CI/CD, NAC Parity, and customer delivery updates.

IMPORTANT RULES:
- Summarize insights at the milestone/theme level. Do NOT quote or paraphrase any individual participant's words.
- Do NOT include participant names, email addresses, or direct quotes in any output field.
- Write each item as a concise, professional status update (e.g. "Certificate renewal completed across all 6 lab nodes").

Meeting: {meeting_title}

Transcript:
{transcript[:15000]}

Provide a structured summary in JSON format:
{{
    "decisions": ["decision 1", "decision 2"],
    "action_items": ["action 1", "action 2"],
    "risks": ["risk 1", "risk 2"],
    "updates": ["update 1", "update 2"],
    "next_steps": ["step 1", "step 2"]
}}
"""
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            return json.loads(result)
            
        except Exception as e:
            print(f"AI analysis failed: {e}")
            return self._basic_analysis(transcript)
    
    def _basic_analysis(self, transcript: str) -> Dict:
        """Basic keyword-based analysis when AI is not available.
        Produces clean summaries without participant names or raw quotes."""
        import re
        lines = transcript.split("\n")

        action_keywords = ["action", "todo", "will do", "need to", "should", "must"]
        risk_keywords = ["risk", "concern", "issue", "problem", "blocker", "worried"]
        decision_keywords = ["decided", "agreed", "confirmed", "approved", "will go with"]

        def clean_line(line):
            """Strip speaker labels and timestamps from transcript lines."""
            line = re.sub(r'^[\d:]+\s*', '', line)  # timestamps
            line = re.sub(r'^[A-Za-z\s]+:\s*', '', line, count=1)  # "Speaker Name: "
            return line.strip()

        decisions = set()
        action_items = set()
        risks = set()

        for l in lines:
            lower = l.lower()
            cleaned = clean_line(l)
            if not cleaned or len(cleaned) < 10:
                continue
            if len(cleaned) > 120:
                cleaned = cleaned[:117] + "..."
            if any(k in lower for k in decision_keywords):
                decisions.add(cleaned)
            if any(k in lower for k in action_keywords):
                action_items.add(cleaned)
            if any(k in lower for k in risk_keywords):
                risks.add(cleaned)

        return {
            "decisions": sorted(list(decisions))[:5],
            "action_items": sorted(list(action_items))[:5],
            "risks": sorted(list(risks))[:5],
            "updates": [],
            "next_steps": []
        }
    
    def analyze_recent_meetings(self, days_back: int = 7) -> Dict:
        """Analyze all DD meetings from the past N days."""
        recordings = self.get_recordings(days_back=days_back)
        
        all_decisions = []
        all_actions = []
        all_risks = []
        all_updates = []
        meetings_analyzed = []
        
        for recording in recordings:
            recording_id = recording.get("id")
            title = recording.get("topic", "Unknown Meeting")
            date = recording.get("createTime", "")[:10]
            
            print(f"Analyzing: {title} ({date})")
            
            transcript = self.get_transcript(recording_id)
            if transcript:
                analysis = self.analyze_transcript_with_ai(transcript, title)
                
                all_decisions.extend(analysis.get("decisions", []))
                all_actions.extend(analysis.get("action_items", []))
                all_risks.extend(analysis.get("risks", []))
                all_updates.extend(analysis.get("updates", []))
                
                meetings_analyzed.append({
                    "title": title,
                    "date": date,
                    "has_transcript": True
                })
            else:
                meetings_analyzed.append({
                    "title": title,
                    "date": date,
                    "has_transcript": False
                })
        
        return {
            "meetings_analyzed": meetings_analyzed,
            "decisions": list(set(all_decisions)),
            "action_items": list(set(all_actions)),
            "risks": list(set(all_risks)),
            "updates": list(set(all_updates)),
            "period": f"Last {days_back} days"
        }
    
    def format_for_status_report(self, analysis: Dict) -> str:
        """Format the analysis for inclusion in status report."""
        
        output = "\n### 🎥 Meeting Insights (from Recordings)\n\n"
        
        if analysis.get("meetings_analyzed"):
            output += f"**Meetings Analyzed:** {len(analysis['meetings_analyzed'])}\n\n"
            for m in analysis["meetings_analyzed"][:5]:
                status = "✅" if m["has_transcript"] else "⚠️ No transcript"
                output += f"- {m['date']}: {m['title']} {status}\n"
            output += "\n"
        
        if analysis.get("decisions"):
            output += "**Key Decisions:**\n"
            for d in analysis["decisions"][:5]:
                output += f"- {d}\n"
            output += "\n"
        
        if analysis.get("action_items"):
            output += "**Action Items from Meetings:**\n"
            for a in analysis["action_items"][:5]:
                output += f"- [ ] {a}\n"
            output += "\n"
        
        if analysis.get("risks"):
            output += "**Risks/Concerns Raised:**\n"
            for r in analysis["risks"][:5]:
                output += f"- ⚠️ {r}\n"
            output += "\n"
        
        return output


def main():
    """Test the recordings analyzer."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze Webex recordings for Digitized Delivery")
    parser.add_argument("--days", "-d", type=int, default=7, help="Days to look back")
    parser.add_argument("--token", "-t", help="Webex access token")
    parser.add_argument("--list-only", action="store_true", help="Just list recordings, don't analyze")
    
    args = parser.parse_args()
    
    token = args.token or WEBEX_ACCESS_TOKEN
    if not token:
        print("❌ Set WEBEX_ACCESS_TOKEN or use --token")
        print("\nTo get a token:")
        print("1. Go to developer.webex.com/my-apps")
        print("2. Create an Integration with recordings scopes")
        print("3. Complete OAuth flow to get access token")
        exit(1)
    
    analyzer = WebexRecordingsAnalyzer(token)
    
    if args.list_only:
        recordings = analyzer.get_recordings(days_back=args.days)
        print(f"\n📹 DD Recordings (last {args.days} days):")
        for r in recordings:
            print(f"  - {r.get('createTime', '')[:10]}: {r.get('topic', 'Unknown')}")
    else:
        analysis = analyzer.analyze_recent_meetings(days_back=args.days)
        report = analyzer.format_for_status_report(analysis)
        print(report)


if __name__ == "__main__":
    main()
