"""Webex integration client for fetching chats, messages, and meeting transcripts."""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Generator
import requests
from webexteamssdk import WebexTeamsAPI
from webexteamssdk.exceptions import ApiError

from models import (
    Message, Conversation, Participant, MeetingTranscript,
    SourceType, ConversationType
)
from config import Settings

logger = logging.getLogger(__name__)


class WebexClient:
    """Client for interacting with Webex APIs."""
    
    BASE_URL = "https://webexapis.com/v1"
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.api = WebexTeamsAPI(access_token=settings.webex_access_token)
        self.headers = {
            "Authorization": f"Bearer {settings.webex_access_token}",
            "Content-Type": "application/json"
        }
        self._me = None
    
    @property
    def me(self) -> dict:
        """Get current user info (cached)."""
        if self._me is None:
            self._me = self.api.people.me()
        return self._me
    
    def _is_internal_email(self, email: str) -> bool:
        """Check if an email belongs to an internal domain."""
        if not email:
            return False
        domain = email.split("@")[-1].lower()
        return domain in [d.lower() for d in self.settings.internal_domains]
    
    def _classify_conversation(self, participants: List[Participant]) -> ConversationType:
        """Classify conversation as customer or internal based on participants."""
        external_count = sum(1 for p in participants if not p.is_internal)
        if external_count > 0:
            return ConversationType.CUSTOMER
        return ConversationType.INTERNAL
    
    def _extract_customer_name(self, participants: List[Participant], room_title: str) -> Optional[str]:
        """Try to extract customer name from participants or room title."""
        # First, try to find external participants
        external = [p for p in participants if not p.is_internal]
        if external:
            # Try to get organization from email domain
            domains = set()
            for p in external:
                if p.email and "@" in p.email:
                    domain = p.email.split("@")[-1].split(".")[0]
                    if domain.lower() not in ["gmail", "yahoo", "hotmail", "outlook"]:
                        domains.add(domain.title())
            if domains:
                return ", ".join(sorted(domains))
        
        # Fall back to room title parsing
        # Common patterns: "Customer Name - Topic", "Customer Name | Topic"
        for sep in [" - ", " | ", " / "]:
            if sep in room_title:
                potential_name = room_title.split(sep)[0].strip()
                if len(potential_name) > 2 and len(potential_name) < 50:
                    return potential_name
        
        return None
    
    def _participant_from_person(self, person) -> Participant:
        """Convert Webex person object to Participant model."""
        email = getattr(person, 'emails', [None])[0] if hasattr(person, 'emails') else str(person)
        display_name = getattr(person, 'displayName', None)
        
        if isinstance(person, str):
            email = person
            display_name = None
        
        return Participant(
            email=email or "unknown",
            display_name=display_name,
            is_internal=self._is_internal_email(email or ""),
            organization=email.split("@")[-1] if email and "@" in email else None
        )
    
    def get_rooms(self, max_rooms: int = 100) -> Generator[dict, None, None]:
        """Fetch all rooms (spaces) the user is a member of."""
        try:
            rooms = self.api.rooms.list(max=max_rooms, sortBy="lastactivity")
            for room in rooms:
                yield room
        except ApiError as e:
            logger.error(f"Failed to fetch rooms: {e}")
            raise
    
    def get_direct_messages_rooms(self) -> Generator[dict, None, None]:
        """Fetch all 1:1 direct message rooms."""
        try:
            rooms = self.api.rooms.list(type="direct", sortBy="lastactivity")
            for room in rooms:
                yield room
        except ApiError as e:
            logger.error(f"Failed to fetch direct rooms: {e}")
            raise
    
    def get_room_messages(
        self, 
        room_id: str, 
        max_messages: Optional[int] = None,
        before: Optional[datetime] = None
    ) -> List[Message]:
        """Fetch messages from a specific room."""
        max_messages = max_messages or self.settings.max_messages_per_room
        messages = []
        
        try:
            params = {"roomId": room_id, "max": min(max_messages, 1000)}
            if before:
                params["before"] = before.isoformat() + "Z"
            
            room_messages = self.api.messages.list(**params)
            
            for msg in room_messages:
                if len(messages) >= max_messages:
                    break
                
                sender = self._participant_from_person(msg.personEmail)
                
                messages.append(Message(
                    id=msg.id,
                    source_type=SourceType.WEBEX_CHAT,
                    source_id=room_id,
                    sender=sender,
                    content=msg.text or msg.html or "",
                    timestamp=datetime.fromisoformat(msg.created.replace("Z", "+00:00")),
                    has_attachments=bool(msg.files) if hasattr(msg, 'files') else False,
                    attachment_names=[],
                    mentioned_people=msg.mentionedPeople if hasattr(msg, 'mentionedPeople') else []
                ))
                
        except ApiError as e:
            logger.error(f"Failed to fetch messages for room {room_id}: {e}")
        
        return messages
    
    def get_room_memberships(self, room_id: str) -> List[Participant]:
        """Get all members of a room."""
        participants = []
        try:
            memberships = self.api.memberships.list(roomId=room_id)
            for member in memberships:
                participants.append(self._participant_from_person(member.personEmail))
        except ApiError as e:
            logger.error(f"Failed to fetch memberships for room {room_id}: {e}")
        return participants
    
    def get_messages_sent_to_me(self, lookback_days: Optional[int] = None) -> List[Message]:
        """Fetch messages where the current user is mentioned or in direct messages."""
        lookback_days = lookback_days or self.settings.lookback_days
        cutoff = datetime.utcnow() - timedelta(days=lookback_days)
        messages = []
        
        # Get messages mentioning me
        try:
            mentioned = self.api.messages.list(mentionedPeople="me", max=500)
            for msg in mentioned:
                msg_time = datetime.fromisoformat(msg.created.replace("Z", "+00:00"))
                if msg_time.replace(tzinfo=None) < cutoff:
                    continue
                    
                sender = self._participant_from_person(msg.personEmail)
                messages.append(Message(
                    id=msg.id,
                    source_type=SourceType.WEBEX_CHAT,
                    source_id=msg.roomId,
                    sender=sender,
                    content=msg.text or msg.html or "",
                    timestamp=msg_time,
                    has_attachments=bool(msg.files) if hasattr(msg, 'files') else False,
                    mentioned_people=["me"]
                ))
        except ApiError as e:
            logger.warning(f"Failed to fetch mentioned messages: {e}")
        
        # Get direct messages
        for room in self.get_direct_messages_rooms():
            room_messages = self.get_room_messages(room.id, max_messages=50)
            for msg in room_messages:
                if msg.timestamp.replace(tzinfo=None) >= cutoff:
                    msg.is_direct_message = True
                    messages.append(msg)
        
        return messages
    
    def get_all_conversations(self, lookback_days: Optional[int] = None) -> List[Conversation]:
        """Fetch all conversations with messages within the lookback period."""
        lookback_days = lookback_days or self.settings.lookback_days
        cutoff = datetime.utcnow() - timedelta(days=lookback_days)
        conversations = []
        
        logger.info(f"Fetching Webex conversations from the last {lookback_days} days...")
        
        for room in self.get_rooms():
            # Check last activity
            last_activity = None
            if hasattr(room, 'lastActivity') and room.lastActivity:
                last_activity = datetime.fromisoformat(room.lastActivity.replace("Z", "+00:00"))
                if last_activity.replace(tzinfo=None) < cutoff:
                    continue
            
            # Get participants
            participants = self.get_room_memberships(room.id)
            
            # Get messages
            messages = self.get_room_messages(room.id)
            
            # Filter messages by date
            messages = [m for m in messages if m.timestamp.replace(tzinfo=None) >= cutoff]
            
            if not messages:
                continue
            
            # Classify conversation
            conv_type = self._classify_conversation(participants)
            external_participants = [p for p in participants if not p.is_internal]
            customer_name = self._extract_customer_name(participants, room.title)
            
            conversation = Conversation(
                id=room.id,
                source_type=SourceType.WEBEX_CHAT,
                title=room.title,
                conversation_type=conv_type,
                participants=participants,
                messages=messages,
                created_at=datetime.fromisoformat(room.created.replace("Z", "+00:00")) if room.created else None,
                last_activity=last_activity,
                customer_name=customer_name,
                external_participants=external_participants
            )
            
            conversations.append(conversation)
            logger.debug(f"Processed room: {room.title} ({len(messages)} messages)")
        
        logger.info(f"Found {len(conversations)} active Webex conversations")
        return conversations
    
    def get_meeting_transcripts(self, lookback_days: Optional[int] = None) -> List[MeetingTranscript]:
        """Fetch meeting transcripts from Webex Meetings API."""
        lookback_days = lookback_days or self.settings.lookback_days
        cutoff = datetime.utcnow() - timedelta(days=lookback_days)
        transcripts = []
        
        logger.info(f"Fetching Webex meeting transcripts from the last {lookback_days} days...")
        
        # List meetings
        try:
            from_date = cutoff.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            to_date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
            
            response = requests.get(
                f"{self.BASE_URL}/meetings",
                headers=self.headers,
                params={
                    "from": from_date,
                    "to": to_date,
                    "meetingType": "meeting",
                    "state": "ended",
                    "max": 100
                }
            )
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch meetings: {response.status_code} - {response.text}")
                return transcripts
            
            meetings = response.json().get("items", [])
            
            for meeting in meetings:
                meeting_id = meeting.get("id")
                
                # Try to get transcript
                transcript_response = requests.get(
                    f"{self.BASE_URL}/meetingTranscripts",
                    headers=self.headers,
                    params={"meetingId": meeting_id}
                )
                
                if transcript_response.status_code != 200:
                    continue
                
                transcript_data = transcript_response.json().get("items", [])
                
                if not transcript_data:
                    continue
                
                # Get transcript content
                for t in transcript_data:
                    transcript_id = t.get("id")
                    content_response = requests.get(
                        f"{self.BASE_URL}/meetingTranscripts/{transcript_id}/download",
                        headers=self.headers
                    )
                    
                    if content_response.status_code != 200:
                        continue
                    
                    # Parse transcript content (VTT format typically)
                    transcript_text = content_response.text
                    segments = self._parse_transcript(transcript_text)
                    
                    # Get meeting participants
                    participants = []
                    participants_response = requests.get(
                        f"{self.BASE_URL}/meetingParticipants",
                        headers=self.headers,
                        params={"meetingId": meeting_id}
                    )
                    
                    if participants_response.status_code == 200:
                        for p in participants_response.json().get("items", []):
                            participants.append(Participant(
                                email=p.get("email", "unknown"),
                                display_name=p.get("displayName"),
                                is_internal=self._is_internal_email(p.get("email", ""))
                            ))
                    
                    host_email = meeting.get("hostEmail", "unknown")
                    
                    transcripts.append(MeetingTranscript(
                        meeting_id=meeting_id,
                        title=meeting.get("title", "Untitled Meeting"),
                        start_time=datetime.fromisoformat(meeting.get("start", "").replace("Z", "+00:00")),
                        end_time=datetime.fromisoformat(meeting.get("end", "").replace("Z", "+00:00")) if meeting.get("end") else None,
                        duration_minutes=meeting.get("durationMinutes"),
                        host=Participant(
                            email=host_email,
                            display_name=meeting.get("hostDisplayName"),
                            is_internal=self._is_internal_email(host_email)
                        ),
                        participants=participants,
                        transcript_segments=segments
                    ))
                    
        except Exception as e:
            logger.error(f"Failed to fetch meeting transcripts: {e}")
        
        logger.info(f"Found {len(transcripts)} meeting transcripts")
        return transcripts
    
    def _parse_transcript(self, vtt_content: str) -> List[dict]:
        """Parse VTT transcript format into segments."""
        segments = []
        lines = vtt_content.strip().split("\n")
        
        current_segment = {}
        for line in lines:
            line = line.strip()
            
            # Skip WEBVTT header and empty lines
            if not line or line.startswith("WEBVTT") or line.startswith("NOTE"):
                continue
            
            # Timestamp line
            if "-->" in line:
                current_segment["timestamp"] = line.split("-->")[0].strip()
                continue
            
            # Speaker and text line
            if ":" in line and current_segment.get("timestamp"):
                parts = line.split(":", 1)
                current_segment["speaker"] = parts[0].strip()
                current_segment["text"] = parts[1].strip() if len(parts) > 1 else ""
                segments.append(current_segment.copy())
                current_segment = {}
            elif current_segment.get("timestamp"):
                current_segment["speaker"] = "Unknown"
                current_segment["text"] = line
                segments.append(current_segment.copy())
                current_segment = {}
        
        return segments
    
    def convert_transcript_to_conversation(self, transcript: MeetingTranscript) -> Conversation:
        """Convert a meeting transcript to a Conversation for unified processing."""
        messages = []
        
        for i, segment in enumerate(transcript.transcript_segments):
            speaker_email = "unknown@meeting.local"
            speaker_name = segment.get("speaker", "Unknown")
            
            # Try to match speaker to participant
            for p in transcript.participants:
                if p.display_name and speaker_name.lower() in p.display_name.lower():
                    speaker_email = p.email
                    break
            
            messages.append(Message(
                id=f"{transcript.meeting_id}_seg_{i}",
                source_type=SourceType.WEBEX_MEETING_TRANSCRIPT,
                source_id=transcript.meeting_id,
                sender=Participant(
                    email=speaker_email,
                    display_name=speaker_name,
                    is_internal=self._is_internal_email(speaker_email)
                ),
                content=segment.get("text", ""),
                timestamp=transcript.start_time,
                has_attachments=False
            ))
        
        conv_type = self._classify_conversation(transcript.participants)
        external = [p for p in transcript.participants if not p.is_internal]
        customer_name = self._extract_customer_name(transcript.participants, transcript.title)
        
        return Conversation(
            id=transcript.meeting_id,
            source_type=SourceType.WEBEX_MEETING_TRANSCRIPT,
            title=transcript.title,
            conversation_type=conv_type,
            participants=transcript.participants,
            messages=messages,
            created_at=transcript.start_time,
            last_activity=transcript.end_time,
            customer_name=customer_name,
            external_participants=external
        )
