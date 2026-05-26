"""Main Communication Intelligence Agent orchestrator."""

import logging
from datetime import datetime
from typing import List, Optional, Dict
from collections import defaultdict

from models import (
    Conversation, ActionItem, AgentReport, Priority,
    SourceType, ConversationType
)
from config import Settings, get_settings
from webex_client import WebexClient
from email_client import EmailClient
from action_extractor import ActionExtractor, RuleBasedExtractor

logger = logging.getLogger(__name__)


class CommunicationAgent:
    """
    Main agent that orchestrates data collection from Webex and Email,
    extracts action items, and generates prioritized reports.
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.webex_client = None
        self.email_client = None
        self.action_extractor = None
        self.rule_extractor = None
        
        # Data stores
        self.conversations: List[Conversation] = []
        self.actions: List[ActionItem] = []
        
    def _init_webex(self):
        """Initialize Webex client."""
        if self.webex_client is None:
            try:
                self.webex_client = WebexClient(self.settings)
                logger.info("Webex client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Webex client: {e}")
                raise
    
    def _init_email(self):
        """Initialize Email client."""
        if self.email_client is None:
            try:
                self.email_client = EmailClient(self.settings)
                logger.info("Email client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Email client: {e}")
                raise
    
    def _init_extractors(self):
        """Initialize action extractors."""
        if self.action_extractor is None:
            try:
                self.action_extractor = ActionExtractor(self.settings)
                logger.info("LLM-based action extractor initialized")
            except Exception as e:
                logger.warning(f"LLM extractor unavailable, using rule-based: {e}")
        
        if self.rule_extractor is None:
            self.rule_extractor = RuleBasedExtractor(self.settings)
    
    def collect_webex_chats(self, lookback_days: Optional[int] = None) -> List[Conversation]:
        """Collect all Webex chat conversations."""
        self._init_webex()
        
        logger.info("Collecting Webex chat conversations...")
        conversations = self.webex_client.get_all_conversations(lookback_days)
        
        # Classify any unknown conversations
        for conv in conversations:
            if conv.conversation_type == ConversationType.UNKNOWN:
                self._init_extractors()
                conv_type, customer = self.action_extractor.classify_conversation(conv)
                conv.conversation_type = conv_type
                if customer:
                    conv.customer_name = customer
        
        self.conversations.extend(conversations)
        logger.info(f"Collected {len(conversations)} Webex chat conversations")
        return conversations
    
    def collect_webex_transcripts(self, lookback_days: Optional[int] = None) -> List[Conversation]:
        """Collect Webex meeting transcripts and convert to conversations."""
        self._init_webex()
        
        logger.info("Collecting Webex meeting transcripts...")
        transcripts = self.webex_client.get_meeting_transcripts(lookback_days)
        
        conversations = []
        for transcript in transcripts:
            conv = self.webex_client.convert_transcript_to_conversation(transcript)
            
            # Classify if unknown
            if conv.conversation_type == ConversationType.UNKNOWN:
                self._init_extractors()
                conv_type, customer = self.action_extractor.classify_conversation(conv)
                conv.conversation_type = conv_type
                if customer:
                    conv.customer_name = customer
            
            conversations.append(conv)
        
        self.conversations.extend(conversations)
        logger.info(f"Collected {len(conversations)} meeting transcripts")
        return conversations
    
    def collect_emails(self, lookback_days: Optional[int] = None) -> List[Conversation]:
        """Collect emails and convert to conversations."""
        self._init_email()
        
        logger.info("Collecting emails...")
        conversations = self.email_client.get_all_conversations(lookback_days)
        
        # Classify any unknown conversations
        for conv in conversations:
            if conv.conversation_type == ConversationType.UNKNOWN:
                self._init_extractors()
                conv_type, customer = self.action_extractor.classify_conversation(conv)
                conv.conversation_type = conv_type
                if customer:
                    conv.customer_name = customer
        
        self.conversations.extend(conversations)
        logger.info(f"Collected {len(conversations)} email threads")
        return conversations
    
    def collect_all(self, lookback_days: Optional[int] = None) -> List[Conversation]:
        """Collect data from all sources."""
        lookback_days = lookback_days or self.settings.lookback_days
        
        logger.info(f"Starting data collection (lookback: {lookback_days} days)...")
        
        # Clear previous data
        self.conversations = []
        
        # Collect from all sources
        try:
            self.collect_webex_chats(lookback_days)
        except Exception as e:
            logger.error(f"Webex chat collection failed: {e}")
        
        try:
            self.collect_webex_transcripts(lookback_days)
        except Exception as e:
            logger.error(f"Webex transcript collection failed: {e}")
        
        try:
            self.collect_emails(lookback_days)
        except Exception as e:
            logger.error(f"Email collection failed: {e}")
        
        logger.info(f"Total conversations collected: {len(self.conversations)}")
        return self.conversations
    
    def extract_actions(self, use_llm: bool = True) -> List[ActionItem]:
        """Extract action items from all collected conversations."""
        self._init_extractors()
        
        logger.info(f"Extracting actions from {len(self.conversations)} conversations...")
        
        self.actions = []
        
        for conv in self.conversations:
            try:
                if use_llm and self.action_extractor:
                    actions = self.action_extractor.extract_actions_from_conversation(conv)
                else:
                    actions = self.rule_extractor.extract_actions(conv)
                
                self.actions.extend(actions)
                
            except Exception as e:
                logger.warning(f"Action extraction failed for '{conv.title}': {e}")
                # Fall back to rule-based
                try:
                    actions = self.rule_extractor.extract_actions(conv)
                    self.actions.extend(actions)
                except Exception as e2:
                    logger.error(f"Rule-based extraction also failed: {e2}")
        
        # Apply prioritization logic
        if self.action_extractor:
            self.actions = self.action_extractor.prioritize_actions(self.actions)
        
        logger.info(f"Extracted {len(self.actions)} total action items")
        return self.actions
    
    def separate_by_type(self) -> Dict[str, List[Conversation]]:
        """Separate conversations by customer vs internal."""
        result = {
            "customer": [],
            "internal": [],
            "unknown": []
        }
        
        for conv in self.conversations:
            if conv.conversation_type == ConversationType.CUSTOMER:
                result["customer"].append(conv)
            elif conv.conversation_type == ConversationType.INTERNAL:
                result["internal"].append(conv)
            else:
                result["unknown"].append(conv)
        
        return result
    
    def group_actions_by_customer(self) -> Dict[str, List[ActionItem]]:
        """Group action items by customer name."""
        grouped = defaultdict(list)
        
        for action in self.actions:
            if action.conversation_type == ConversationType.CUSTOMER:
                key = action.customer_name or "Unknown Customer"
            else:
                key = "Internal"
            grouped[key].append(action)
        
        return dict(grouped)
    
    def group_actions_by_priority(self) -> Dict[str, List[ActionItem]]:
        """Group action items by priority."""
        grouped = {
            Priority.HIGH.value: [],
            Priority.MEDIUM.value: [],
            Priority.LOW.value: []
        }
        
        for action in self.actions:
            grouped[action.priority.value].append(action)
        
        return grouped
    
    def generate_report(self) -> AgentReport:
        """Generate a comprehensive report of all findings."""
        by_type = self.separate_by_type()
        
        # Count messages and emails
        total_messages = sum(len(c.messages) for c in self.conversations)
        email_convs = [c for c in self.conversations if c.source_type == SourceType.EMAIL]
        transcript_convs = [c for c in self.conversations if c.source_type == SourceType.WEBEX_MEETING_TRANSCRIPT]
        
        report = AgentReport(
            generated_at=datetime.utcnow(),
            lookback_days=self.settings.lookback_days,
            total_conversations=len(self.conversations),
            customer_conversations=len(by_type["customer"]),
            internal_conversations=len(by_type["internal"]),
            total_messages=total_messages,
            total_emails=len(email_convs),
            total_meeting_transcripts=len(transcript_convs),
            action_items=self.actions,
            actions_by_customer=self.group_actions_by_customer(),
            actions_by_priority=self.group_actions_by_priority()
        )
        
        return report
    
    def run(
        self,
        lookback_days: Optional[int] = None,
        use_llm: bool = True,
        sources: Optional[List[str]] = None
    ) -> AgentReport:
        """
        Run the full agent pipeline.
        
        Args:
            lookback_days: Number of days to look back for messages
            use_llm: Whether to use LLM for action extraction
            sources: List of sources to collect from ('webex_chat', 'webex_transcript', 'email')
                    If None, collects from all sources.
        
        Returns:
            AgentReport with all findings
        """
        lookback_days = lookback_days or self.settings.lookback_days
        sources = sources or ['webex_chat', 'webex_transcript', 'email']
        
        logger.info("=" * 60)
        logger.info("Communication Intelligence Agent Starting")
        logger.info(f"Lookback period: {lookback_days} days")
        logger.info(f"Sources: {sources}")
        logger.info("=" * 60)
        
        # Clear previous data
        self.conversations = []
        self.actions = []
        
        # Collect data from specified sources
        if 'webex_chat' in sources:
            try:
                self.collect_webex_chats(lookback_days)
            except Exception as e:
                logger.error(f"Webex chat collection failed: {e}")
        
        if 'webex_transcript' in sources:
            try:
                self.collect_webex_transcripts(lookback_days)
            except Exception as e:
                logger.error(f"Webex transcript collection failed: {e}")
        
        if 'email' in sources:
            try:
                self.collect_emails(lookback_days)
            except Exception as e:
                logger.error(f"Email collection failed: {e}")
        
        # Extract actions
        self.extract_actions(use_llm=use_llm)
        
        # Generate report
        report = self.generate_report()
        
        logger.info("=" * 60)
        logger.info("Agent Run Complete")
        logger.info(f"Conversations processed: {report.total_conversations}")
        logger.info(f"  - Customer: {report.customer_conversations}")
        logger.info(f"  - Internal: {report.internal_conversations}")
        logger.info(f"Action items found: {len(report.action_items)}")
        logger.info(f"  - High priority: {report.high_priority_count}")
        logger.info(f"  - Overdue: {report.overdue_count}")
        logger.info("=" * 60)
        
        return report


def create_agent(settings: Optional[Settings] = None) -> CommunicationAgent:
    """Factory function to create a configured agent."""
    return CommunicationAgent(settings)
