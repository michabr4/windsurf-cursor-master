"""
Webex Recordings Analyzer for MGM Status Reports

Pulls meeting recordings and transcripts from you AND MGM participants,
extracts key information using AI, and incorporates into daily status reports.
Meetings without a Webex-generated transcript fall back to Whisper on the
recording audio. Action items are extracted with Claude and auto-created as
Asana tasks (deduplicated across runs via a marker embedded in task notes).

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

Optional integrations (each degrades gracefully when unset):
- OPENAI_API_KEY: GPT-4 analysis of transcripts; also powers the Whisper
  fallback transcription when a meeting has no Webex transcript.
- ANTHROPIC_API_KEY: Claude extraction of structured action items
  (due date/priority) for Asana task creation.
- ASANA_ACCESS_TOKEN + ASANA_PROJECT_GID: personal access token and target
  project for auto-created action-item tasks. Tasks are created unassigned
  (never auto-attributed to a participant) — see the no-names rule below.
"""

import hashlib
import io
import json
import os
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional

import requests

# Configuration
WEBEX_ACCESS_TOKEN = os.environ.get("WEBEX_ACCESS_TOKEN", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ASANA_ACCESS_TOKEN = os.environ.get("ASANA_ACCESS_TOKEN", "")
ASANA_PROJECT_GID = os.environ.get("ASANA_PROJECT_GID", "")
ASANA_BASE_URL = "https://app.asana.com/api/1.0"
CREATE_ASANA_TASKS = os.environ.get("CREATE_ASANA_TASKS", "true").strip().lower() not in ("0", "false", "no")
BASE_URL = "https://webexapis.com/v1"

ACTION_ITEM_SYSTEM_PROMPT = """You extract concrete action items from MGM meeting transcripts.

Rules:
- Only extract concrete action items, not general discussion.
- Do NOT include participant names, email addresses, or direct quotes anywhere in the output.
  Tasks are created unassigned; do not guess or imply who owns an item.
- Write each title as a concise, professional status update.
- If a due date is not clearly stated, leave it null - never guess.
- due_date must be an ISO date (YYYY-MM-DD) or null.
- priority is one of "high", "medium", "low".

Respond with strict JSON only:
{"action_items": [{"title": str, "due_date": str|null, "priority": "high"|"medium"|"low"}]}
If there are no action items, respond {"action_items": []}.
"""

_AUDIO_CONTENT_TYPE_EXTENSIONS = {
    "audio/mpeg": "mp3",
    "audio/mp3": "mp3",
    "audio/wav": "wav",
    "audio/x-wav": "wav",
    "audio/mp4": "m4a",
    "audio/x-m4a": "m4a",
    "video/mp4": "mp4",
}


def _audio_extension(content_type: str) -> str:
    """Map a download response's Content-Type to a file extension Whisper can sniff correctly."""
    return _AUDIO_CONTENT_TYPE_EXTENSIONS.get(content_type.split(";")[0].strip().lower(), "mp4")


def _asana_headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {ASANA_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }


def _asana_list_task_notes(project_gid: str) -> Dict[str, str]:
    """Return {task_gid: notes} for every task in a project (used for dedup checks)."""
    notes_by_gid: Dict[str, str] = {}
    url = f"{ASANA_BASE_URL}/projects/{project_gid}/tasks"
    params: Optional[Dict] = {"opt_fields": "notes", "limit": 100}
    while url:
        resp = requests.get(url, headers=_asana_headers(), params=params, timeout=30)
        if resp.status_code != 200:
            raise RuntimeError(f"Asana API {resp.status_code}: {resp.text[:300]}")
        body = resp.json()
        for item in body.get("data", []):
            gid = item.get("gid")
            if gid:
                notes_by_gid[gid] = item.get("notes") or ""
        next_page = body.get("next_page") or {}
        url = next_page.get("uri")
        params = None  # the next_page uri already includes query params
    return notes_by_gid


def _asana_create_task(project_gid: str, name: str, notes: str, due_on: Optional[str]) -> None:
    """Creates the task unassigned — never auto-attributes it to a meeting participant."""
    data: Dict = {"name": name, "notes": notes, "projects": [project_gid]}
    if due_on:
        data["due_on"] = due_on
    resp = requests.post(f"{ASANA_BASE_URL}/tasks", headers=_asana_headers(), json={"data": data}, timeout=30)
    if resp.status_code not in (200, 201):
        raise RuntimeError(f"Asana API {resp.status_code}: {resp.text[:300]}")


def create_asana_tasks(structured_actions: List[tuple]) -> int:
    """Create an Asana task per (recording_id, meeting_title, action_item) tuple.

    Dedups against existing tasks in the project via a `[webex:<marker>]` tag
    embedded in task notes, since the bot re-scans overlapping day windows on
    every run and there's no persistent state between CI runs.
    """
    if not structured_actions:
        return 0
    if not CREATE_ASANA_TASKS or not ASANA_PROJECT_GID or not ASANA_ACCESS_TOKEN:
        return 0

    try:
        existing_notes = _asana_list_task_notes(ASANA_PROJECT_GID)
    except Exception as exc:
        print(f"Asana: could not connect ({exc}); skipping task creation")
        return 0

    existing_markers = {
        marker
        for notes in existing_notes.values()
        for marker in re.findall(r"\[webex:([\w:-]+)\]", notes)
    }

    created = 0
    for recording_id, meeting_title, item in structured_actions:
        title = item["title"].strip()
        # Hash recording_id+title rather than embedding recording_id raw: Webex recording
        # IDs are base64 and can contain characters (e.g. "=") the marker regex won't match.
        marker = hashlib.sha1(f"{recording_id}:{title}".encode()).hexdigest()[:16]
        if marker in existing_markers:
            continue

        notes = (
            f"Auto-created from Webex recording analysis.\n"
            f"Meeting: {meeting_title}\n"
            f"Priority: {item.get('priority', 'medium')}\n"
            f"[webex:{marker}]"
        )
        try:
            _asana_create_task(
                project_gid=ASANA_PROJECT_GID,
                name=title,
                notes=notes,
                due_on=item.get("due_date"),
            )
            created += 1
        except Exception as exc:
            print(f"Asana: failed to create task '{title}': {exc}")

    if created:
        print(f"✅ Created {created} Asana task(s)")
    return created


class WebexRecordingsAnalyzer:
    """Analyze Webex recordings for MGM-related meetings."""
    
    # Known MGM participants to track their meetings too
    MGM_PARTICIPANTS = [
        "michabr4@cisco.com",
        # Add more MGM team members here
    ]
    
    # MGM-related Webex spaces to monitor
    MGM_SPACES = [
        "MGM LCS - R&S",
        "MGM Digitized Delivery",
        "MGM Firepower",
        "MGM CX Delivery",
    ]
    
    def __init__(self, access_token: str = None):
        self.access_token = access_token or WEBEX_ACCESS_TOKEN
        if not self.access_token:
            raise ValueError("Webex access token required")
        self.mgm_participant_ids = []
    
    def _headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def get_mgm_space_members(self) -> List[str]:
        """
        Get all members from MGM-related Webex spaces.
        Returns list of email addresses.
        """
        mgm_members = set(self.MGM_PARTICIPANTS)
        
        # Get all rooms
        response = requests.get(
            f"{BASE_URL}/rooms",
            headers=self._headers(),
            params={"max": 200}
        )
        
        if response.status_code != 200:
            print(f"Could not fetch rooms: {response.status_code}")
            return list(mgm_members)
        
        rooms = response.json().get("items", [])
        
        # Find MGM-related spaces
        for room in rooms:
            title = room.get("title", "")
            if any(mgm in title.upper() for mgm in ["MGM", "RESORTS"]):
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
                            mgm_members.add(email)
                    print(f"  Found {len(members)} members in '{title}'")
        
        print(f"Total MGM participants identified: {len(mgm_members)}")
        return list(mgm_members)
    
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
    
    def get_recordings(self, days_back: int = 7, search_term: str = "MGM", include_participants: bool = True) -> List[Dict]:
        """
        Get recordings from the past N days matching search term.
        Includes recordings from MGM space participants if include_participants=True.
        
        Args:
            days_back: Number of days to look back
            search_term: Filter recordings by title containing this term
            include_participants: Also fetch recordings from MGM participants
        
        Returns:
            List of recording metadata
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
        
        # Get recordings from MGM participants
        if include_participants:
            print("\n🔍 Scanning MGM participant recordings...")
            mgm_members = self.get_mgm_space_members()
            
            for email in mgm_members:
                if email == "michabr4@cisco.com":
                    continue  # Already got mine
                
                person_recordings = self.get_recordings_for_person(email, days_back)
                mgm_recordings = [
                    r for r in person_recordings
                    if search_term.lower() in r.get("topic", "").lower()
                ]
                
                for r in mgm_recordings:
                    if r.get("id") not in seen_ids:
                        r["_source_email"] = email  # Track who hosted it
                        all_recordings.append(r)
                        seen_ids.add(r.get("id"))
                
                if mgm_recordings:
                    print(f"  Found {len(mgm_recordings)} MGM recordings from {email}")
        
        # Filter by search term
        if search_term:
            all_recordings = [
                r for r in all_recordings 
                if search_term.lower() in r.get("topic", "").lower()
            ]
        
        print(f"\n📹 Total MGM-related recordings: {len(all_recordings)}")
        return all_recordings
    
    def get_transcript(self, recording_id: str) -> Optional[str]:
        """
        Get transcript for a specific recording.
        
        Args:
            recording_id: The recording ID
        
        Returns:
            Transcript text or None
        """
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

    def get_recording_audio_url(self, recording_id: str) -> Optional[str]:
        """Get a temporary direct-download link for a recording's audio, for Whisper fallback."""
        try:
            response = requests.get(
                f"{BASE_URL}/recordings/{recording_id}",
                headers=self._headers(),
                timeout=60,
            )
        except requests.RequestException as exc:
            print(f"Could not fetch recording details for {recording_id}: {exc}")
            return None
        if response.status_code != 200:
            return None
        links = response.json().get("temporaryDirectDownloadLinks") or {}
        return links.get("audioDownloadLink") or links.get("recordingDownloadLink")

    def transcribe_with_whisper(self, audio_url: str) -> Optional[str]:
        """Transcribe recording audio via OpenAI Whisper when no Webex transcript exists."""
        if not OPENAI_API_KEY:
            return None
        try:
            audio_response = requests.get(audio_url, timeout=120)
            audio_response.raise_for_status()
        except requests.RequestException as exc:
            print(f"Whisper: audio download failed: {exc}")
            return None

        try:
            import openai
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            audio_file = io.BytesIO(audio_response.content)
            audio_file.name = f"recording.{_audio_extension(audio_response.headers.get('Content-Type', ''))}"
            result = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
            return result.text
        except Exception as exc:
            print(f"Whisper transcription failed: {exc}")
            return None

    def get_transcript_or_whisper(self, recording_id: str) -> Optional[str]:
        """Prefer the Webex-generated transcript; fall back to Whisper on the recording audio."""
        transcript = self.get_transcript(recording_id)
        if transcript:
            return transcript
        print(f"  No Webex transcript for {recording_id}; trying Whisper fallback...")
        audio_url = self.get_recording_audio_url(recording_id)
        if not audio_url:
            print(f"  No audio download link available for {recording_id}")
            return None
        return self.transcribe_with_whisper(audio_url)

    def extract_action_items_with_claude(self, transcript: str, meeting_title: str) -> List[Dict]:
        """Use Claude to extract structured action items (due date/priority) for Asana."""
        if not ANTHROPIC_API_KEY:
            return []
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            response = client.messages.create(
                model="claude-sonnet-5",
                max_tokens=2048,
                system=ACTION_ITEM_SYSTEM_PROMPT,
                messages=[{
                    "role": "user",
                    "content": f"Meeting: {meeting_title}\n\nTranscript:\n{transcript[:15000]}",
                }],
            )
            raw = response.content[0].text.strip()
            if raw.startswith("```"):
                raw = raw.strip("`").strip()
                if raw.lower().startswith("json"):
                    raw = raw[4:].strip()
            data = json.loads(raw)
            return data.get("action_items", [])
        except Exception as exc:
            print(f"Claude action-item extraction failed: {exc}")
            return []

    def analyze_transcript_with_ai(self, transcript: str, meeting_title: str) -> Dict:
        """
        Use AI to extract key information from transcript.
        
        Args:
            transcript: The meeting transcript text
            meeting_title: Title of the meeting
        
        Returns:
            Dict with extracted information
        """
        if not OPENAI_API_KEY:
            return self._basic_analysis(transcript)
        
        try:
            import openai
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            
            prompt = f"""Analyze this MGM meeting transcript and extract:
1. Key decisions made
2. Action items (with owners if mentioned)
3. Risks or concerns raised
4. Important updates or status changes
5. Next steps discussed

Meeting: {meeting_title}

Transcript:
{transcript[:15000]}  # Limit to avoid token limits

Provide a structured summary in JSON format:
{{
    "decisions": ["decision 1", "decision 2"],
    "action_items": ["action 1 - owner", "action 2 - owner"],
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
        """Basic keyword-based analysis when AI is not available."""
        lines = transcript.split("\n")
        
        action_keywords = ["action", "todo", "will do", "need to", "should", "must"]
        risk_keywords = ["risk", "concern", "issue", "problem", "blocker", "worried"]
        decision_keywords = ["decided", "agreed", "confirmed", "approved", "will go with"]
        
        return {
            "decisions": [l for l in lines if any(k in l.lower() for k in decision_keywords)][:5],
            "action_items": [l for l in lines if any(k in l.lower() for k in action_keywords)][:5],
            "risks": [l for l in lines if any(k in l.lower() for k in risk_keywords)][:5],
            "updates": [],
            "next_steps": []
        }
    
    def analyze_recent_meetings(self, days_back: int = 7) -> Dict:
        """
        Analyze all MGM meetings from the past N days.
        
        Returns:
            Combined analysis from all meetings
        """
        recordings = self.get_recordings(days_back=days_back, search_term="MGM")

        all_decisions = []
        all_actions = []
        all_risks = []
        all_updates = []
        meetings_analyzed = []
        structured_actions = []  # (recording_id, meeting_title, action_item) for Asana

        for recording in recordings:
            recording_id = recording.get("id")
            title = recording.get("topic", "Unknown Meeting")
            date = recording.get("createTime", "")[:10]

            print(f"Analyzing: {title} ({date})")

            transcript = self.get_transcript_or_whisper(recording_id)
            if transcript:
                analysis = self.analyze_transcript_with_ai(transcript, title)

                all_decisions.extend(analysis.get("decisions", []))
                all_actions.extend(analysis.get("action_items", []))
                all_risks.extend(analysis.get("risks", []))
                all_updates.extend(analysis.get("updates", []))

                for item in self.extract_action_items_with_claude(transcript, title):
                    if item.get("title"):
                        structured_actions.append((recording_id, title, item))

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

        create_asana_tasks(structured_actions)

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
    
    parser = argparse.ArgumentParser(description="Analyze Webex recordings for MGM")
    parser.add_argument("--days", "-d", type=int, default=7, help="Days to look back")
    parser.add_argument("--token", "-t", help="Webex access token")
    parser.add_argument("--list-only", action="store_true", help="Just list recordings, don't analyze")
    parser.add_argument(
        "--output",
        "-o",
        metavar="FILE",
        help="Write formatted meeting insights (markdown) to this file for send_reports.py",
    )

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
        print(f"\n📹 MGM Recordings (last {args.days} days):")
        for r in recordings:
            print(f"  - {r.get('createTime', '')[:10]}: {r.get('topic', 'Unknown')}")
    else:
        analysis = analyzer.analyze_recent_meetings(days_back=args.days)
        report = analyzer.format_for_status_report(analysis)
        print(report)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as out:
                out.write(report.strip() + "\n")
            print(f"Wrote insights to {args.output}")


if __name__ == "__main__":
    main()
