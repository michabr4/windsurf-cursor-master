"""Microsoft Graph API client for fetching Outlook emails."""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import re
from html import unescape

import msal
import requests

from models import (
    Email, Conversation, Message, Participant,
    SourceType, ConversationType
)
from config import Settings

logger = logging.getLogger(__name__)


class EmailClient:
    """Client for interacting with Microsoft Graph API for Outlook emails."""
    
    GRAPH_URL = "https://graph.microsoft.com/v1.0"
    SCOPES = ["https://graph.microsoft.com/.default"]
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self._access_token = None
        self._token_expires = None
        
    def _get_access_token(self) -> str:
        """Get or refresh the access token using client credentials flow."""
        if self._access_token and self._token_expires and datetime.utcnow() < self._token_expires:
            return self._access_token
        
        app = msal.ConfidentialClientApplication(
            self.settings.ms_client_id,
            authority=f"https://login.microsoftonline.com/{self.settings.ms_tenant_id}",
            client_credential=self.settings.ms_client_secret
        )
        
        result = app.acquire_token_for_client(scopes=self.SCOPES)
        
        if "access_token" not in result:
            error = result.get("error_description", result.get("error", "Unknown error"))
            raise Exception(f"Failed to acquire token: {error}")
        
        self._access_token = result["access_token"]
        # Token typically valid for 1 hour, refresh 5 minutes early
        self._token_expires = datetime.utcnow() + timedelta(minutes=55)
        
        return self._access_token
    
    @property
    def headers(self) -> Dict[str, str]:
        """Get headers with current access token."""
        return {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json"
        }
    
    def _is_internal_email(self, email: str) -> bool:
        """Check if an email belongs to an internal domain."""
        if not email:
            return False
        domain = email.split("@")[-1].lower()
        return domain in [d.lower() for d in self.settings.internal_domains]
    
    def _strip_html(self, html_content: str) -> str:
        """Convert HTML to plain text."""
        if not html_content:
            return ""
        
        # Remove style and script tags with content
        text = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Replace common block elements with newlines
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</(p|div|tr|li|h[1-6])>', '\n', text, flags=re.IGNORECASE)
        
        # Remove all remaining HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Decode HTML entities
        text = unescape(text)
        
        # Clean up whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        return text.strip()
    
    def _participant_from_graph(self, recipient: dict) -> Participant:
        """Convert Graph API recipient to Participant model."""
        email_address = recipient.get("emailAddress", {})
        email = email_address.get("address", "unknown")
        name = email_address.get("name")
        
        return Participant(
            email=email,
            display_name=name,
            is_internal=self._is_internal_email(email),
            organization=email.split("@")[-1] if "@" in email else None
        )
    
    def _classify_conversation(self, participants: List[Participant]) -> ConversationType:
        """Classify email thread as customer or internal based on participants."""
        external_count = sum(1 for p in participants if not p.is_internal)
        if external_count > 0:
            return ConversationType.CUSTOMER
        return ConversationType.INTERNAL
    
    def _extract_customer_name(self, participants: List[Participant], subject: str) -> Optional[str]:
        """Try to extract customer name from participants or subject."""
        external = [p for p in participants if not p.is_internal]
        if external:
            domains = set()
            for p in external:
                if p.email and "@" in p.email:
                    domain = p.email.split("@")[-1].split(".")[0]
                    if domain.lower() not in ["gmail", "yahoo", "hotmail", "outlook", "live"]:
                        domains.add(domain.title())
            if domains:
                return ", ".join(sorted(domains))
        
        # Try to extract from subject patterns like "[Customer Name]" or "RE: Customer Name -"
        patterns = [
            r'\[([^\]]+)\]',
            r'^(?:RE:|FW:)?\s*([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)\s*[-:|]'
        ]
        for pattern in patterns:
            match = re.search(pattern, subject)
            if match:
                potential = match.group(1).strip()
                if len(potential) > 2 and len(potential) < 40:
                    return potential
        
        return None
    
    def get_emails(
        self,
        lookback_days: Optional[int] = None,
        max_emails: Optional[int] = None,
        folder: str = "inbox"
    ) -> List[Email]:
        """Fetch emails from the specified folder."""
        lookback_days = lookback_days or self.settings.lookback_days
        max_emails = max_emails or self.settings.max_emails_to_fetch
        
        cutoff = datetime.utcnow() - timedelta(days=lookback_days)
        cutoff_str = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        emails = []
        user_email = self.settings.ms_user_email
        
        logger.info(f"Fetching emails for {user_email} from the last {lookback_days} days...")
        
        # Build the request URL
        url = f"{self.GRAPH_URL}/users/{user_email}/mailFolders/{folder}/messages"
        params = {
            "$filter": f"receivedDateTime ge {cutoff_str}",
            "$orderby": "receivedDateTime desc",
            "$top": min(max_emails, 100),
            "$select": "id,subject,from,toRecipients,ccRecipients,body,receivedDateTime,hasAttachments,importance,conversationId,isRead"
        }
        
        try:
            while url and len(emails) < max_emails:
                response = requests.get(url, headers=self.headers, params=params if "?" not in url else None)
                
                if response.status_code != 200:
                    logger.error(f"Failed to fetch emails: {response.status_code} - {response.text}")
                    break
                
                data = response.json()
                
                for item in data.get("value", []):
                    sender = self._participant_from_graph({"emailAddress": item.get("from", {}).get("emailAddress", {})})
                    
                    recipients = [
                        self._participant_from_graph(r)
                        for r in item.get("toRecipients", [])
                    ]
                    
                    cc = [
                        self._participant_from_graph(r)
                        for r in item.get("ccRecipients", [])
                    ]
                    
                    body = item.get("body", {})
                    body_content = body.get("content", "")
                    body_type = body.get("contentType", "text")
                    
                    if body_type.lower() == "html":
                        body_text = self._strip_html(body_content)
                        body_html = body_content
                    else:
                        body_text = body_content
                        body_html = None
                    
                    # Check if this is a reply
                    subject = item.get("subject", "")
                    is_reply = subject.lower().startswith(("re:", "fw:", "fwd:"))
                    
                    emails.append(Email(
                        id=item.get("id"),
                        subject=subject,
                        sender=sender,
                        recipients=recipients,
                        cc=cc,
                        body_text=body_text,
                        body_html=body_html,
                        received_at=datetime.fromisoformat(item.get("receivedDateTime", "").replace("Z", "+00:00")),
                        has_attachments=item.get("hasAttachments", False),
                        conversation_id=item.get("conversationId"),
                        is_reply=is_reply,
                        importance=item.get("importance", "normal")
                    ))
                
                # Handle pagination
                url = data.get("@odata.nextLink")
                params = None  # nextLink includes all params
                
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            raise
        
        logger.info(f"Fetched {len(emails)} emails")
        return emails
    
    def get_emails_sent_to_me(self, lookback_days: Optional[int] = None) -> List[Email]:
        """Fetch emails directly sent to the user (not just CC'd)."""
        all_emails = self.get_emails(lookback_days=lookback_days)
        user_email = self.settings.ms_user_email.lower()
        
        # Filter to emails where user is in TO field
        direct_emails = [
            email for email in all_emails
            if any(r.email.lower() == user_email for r in email.recipients)
        ]
        
        logger.info(f"Found {len(direct_emails)} emails directly sent to {user_email}")
        return direct_emails
    
    def group_emails_by_thread(self, emails: List[Email]) -> Dict[str, List[Email]]:
        """Group emails by conversation thread."""
        threads = {}
        for email in emails:
            thread_id = email.conversation_id or email.id
            if thread_id not in threads:
                threads[thread_id] = []
            threads[thread_id].append(email)
        
        # Sort each thread by date
        for thread_id in threads:
            threads[thread_id].sort(key=lambda e: e.received_at)
        
        return threads
    
    def convert_emails_to_conversations(self, emails: List[Email]) -> List[Conversation]:
        """Convert emails to Conversation objects for unified processing."""
        threads = self.group_emails_by_thread(emails)
        conversations = []
        
        for thread_id, thread_emails in threads.items():
            # Collect all participants
            all_participants = set()
            for email in thread_emails:
                all_participants.add((email.sender.email, email.sender.display_name))
                for r in email.recipients + email.cc:
                    all_participants.add((r.email, r.display_name))
            
            participants = [
                Participant(
                    email=email,
                    display_name=name,
                    is_internal=self._is_internal_email(email),
                    organization=email.split("@")[-1] if "@" in email else None
                )
                for email, name in all_participants
            ]
            
            # Convert emails to messages
            messages = [
                Message(
                    id=email.id,
                    source_type=SourceType.EMAIL,
                    source_id=thread_id,
                    sender=email.sender,
                    content=f"Subject: {email.subject}\n\n{email.body_text}",
                    timestamp=email.received_at,
                    has_attachments=email.has_attachments,
                    attachment_names=email.attachment_names,
                    is_direct_message=False
                )
                for email in thread_emails
            ]
            
            # Use first email's subject as title
            title = thread_emails[0].subject if thread_emails else "Email Thread"
            
            conv_type = self._classify_conversation(participants)
            external = [p for p in participants if not p.is_internal]
            customer_name = self._extract_customer_name(participants, title)
            
            conversations.append(Conversation(
                id=thread_id,
                source_type=SourceType.EMAIL,
                title=title,
                conversation_type=conv_type,
                participants=participants,
                messages=messages,
                created_at=thread_emails[0].received_at if thread_emails else None,
                last_activity=thread_emails[-1].received_at if thread_emails else None,
                customer_name=customer_name,
                external_participants=external
            ))
        
        logger.info(f"Converted {len(emails)} emails into {len(conversations)} conversation threads")
        return conversations
    
    def get_all_conversations(self, lookback_days: Optional[int] = None) -> List[Conversation]:
        """Fetch all emails and convert to conversations."""
        emails = self.get_emails_sent_to_me(lookback_days=lookback_days)
        return self.convert_emails_to_conversations(emails)
