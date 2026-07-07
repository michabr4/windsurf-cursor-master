"""AI-powered action item extraction and classification engine."""

import logging
import json
import re
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from models import (
    Conversation, ActionItem, Priority, SourceType, ConversationType
)
from config import Settings, LLMProvider

logger = logging.getLogger(__name__)

# System prompt for action extraction
EXTRACTION_SYSTEM_PROMPT = """You are an expert assistant that extracts action items from business communications.

Your task is to analyze conversation text and extract:
1. Action items - specific tasks that need to be done
2. Assignees - who is responsible (if mentioned)
3. Due dates - when it needs to be done (if mentioned or implied)
4. Priority - based on urgency indicators and context

Rules for extraction:
- Only extract CONCRETE action items, not general discussions
- Look for phrases like "please", "need to", "can you", "will you", "action required", "follow up", "by [date]"
- Infer due dates from context (e.g., "by end of week", "tomorrow", "ASAP")
- Determine priority based on:
  * HIGH: urgent, critical, ASAP, escalation, P1, SEV1, blocking, immediately
  * MEDIUM: important, soon, this week, follow up needed, action required
  * LOW: when you get a chance, nice to have, FYI with action, low priority

Output format: JSON array of action items with this structure:
{
  "actions": [
    {
      "description": "Clear description of the action item",
      "assignee": "Name or email if mentioned, null if unclear",
      "due_date": "ISO date string if mentioned/inferred, null otherwise",
      "due_date_reasoning": "Why this due date was chosen",
      "priority": "high|medium|low",
      "priority_reasoning": "Why this priority was assigned",
      "source_text": "The exact text that indicates this action"
    }
  ]
}

If no action items are found, return: {"actions": []}
"""

CLASSIFICATION_SYSTEM_PROMPT = """You are analyzing a business conversation to determine:
1. Whether this is a customer conversation or internal discussion
2. The customer/company name if it's a customer conversation

Context clues:
- Customer conversations often have external email domains
- Internal discussions are between colleagues at the same company
- Look for company names, project names, or customer references in the text

Output format:
{
  "is_customer": true/false,
  "customer_name": "Name if identified, null otherwise",
  "confidence": "high|medium|low",
  "reasoning": "Brief explanation"
}
"""


class ActionExtractor:
    """Extracts action items from conversations using LLM."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self._client = None
        
    @property
    def client(self):
        """Lazy-load the LLM client."""
        if self._client is None:
            if self.settings.llm_provider == LLMProvider.OPENAI:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.settings.openai_api_key)
            else:
                from anthropic import Anthropic
                self._client = Anthropic(api_key=self.settings.anthropic_api_key)
        return self._client
    
    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Call the configured LLM and return the response."""
        try:
            if self.settings.llm_provider == LLMProvider.OPENAI:
                response = self.client.chat.completions.create(
                    model=self.settings.openai_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                return response.choices[0].message.content
            else:
                response = self.client.messages.create(
                    model=self.settings.anthropic_model,
                    max_tokens=4096,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ]
                )
                return response.content[0].text
                
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise
    
    def _parse_relative_date(self, date_str: str) -> Optional[datetime]:
        """Parse relative date strings into datetime objects."""
        if not date_str:
            return None
        
        date_str = date_str.lower().strip()
        now = datetime.utcnow()
        
        # Try ISO format first
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except:
            pass
        
        # Common relative patterns
        patterns = {
            r"today": now,
            r"tomorrow": now + timedelta(days=1),
            r"end of day|eod|by eod": now.replace(hour=17, minute=0, second=0),
            r"end of week|eow|by eow": now + timedelta(days=(4 - now.weekday()) % 7),
            r"next week": now + timedelta(days=7),
            r"this week": now + timedelta(days=(4 - now.weekday()) % 7),
            r"asap|immediately|urgent": now + timedelta(days=1),
            r"(\d+)\s*days?": lambda m: now + timedelta(days=int(m.group(1))),
            r"(\d+)\s*weeks?": lambda m: now + timedelta(weeks=int(m.group(1))),
            r"monday": now + timedelta(days=(0 - now.weekday()) % 7 or 7),
            r"tuesday": now + timedelta(days=(1 - now.weekday()) % 7 or 7),
            r"wednesday": now + timedelta(days=(2 - now.weekday()) % 7 or 7),
            r"thursday": now + timedelta(days=(3 - now.weekday()) % 7 or 7),
            r"friday": now + timedelta(days=(4 - now.weekday()) % 7 or 7),
        }
        
        for pattern, result in patterns.items():
            match = re.search(pattern, date_str)
            if match:
                if callable(result):
                    return result(match)
                return result
        
        return None
    
    def _keyword_priority_check(self, text: str) -> Tuple[Optional[Priority], List[str]]:
        """Check for priority keywords in text."""
        text_lower = text.lower()
        matched_keywords = []
        
        for keyword in self.settings.high_priority_keywords:
            if keyword.lower() in text_lower:
                matched_keywords.append(keyword)
        
        if matched_keywords:
            return Priority.HIGH, matched_keywords
        
        for keyword in self.settings.medium_priority_keywords:
            if keyword.lower() in text_lower:
                matched_keywords.append(keyword)
        
        if matched_keywords:
            return Priority.MEDIUM, matched_keywords
        
        return None, []
    
    def extract_actions_from_conversation(self, conversation: Conversation) -> List[ActionItem]:
        """Extract action items from a single conversation."""
        if not conversation.messages:
            return []
        
        # Prepare conversation text for analysis
        conv_text = conversation.full_text
        
        # Truncate if too long (keep most recent messages)
        max_chars = 12000
        if len(conv_text) > max_chars:
            conv_text = "...[earlier messages truncated]...\n" + conv_text[-max_chars:]
        
        user_prompt = f"""Analyze this conversation and extract action items:

Conversation Title: {conversation.title}
Type: {conversation.conversation_type.value}
Participants: {', '.join([p.email for p in conversation.participants[:10]])}

--- Conversation ---
{conv_text}
--- End Conversation ---

Extract all action items from this conversation."""

        try:
            response = self._call_llm(EXTRACTION_SYSTEM_PROMPT, user_prompt)
            result = json.loads(response)
            
            actions = []
            for item in result.get("actions", []):
                # Parse due date
                due_date = None
                if item.get("due_date"):
                    due_date = self._parse_relative_date(item["due_date"])
                
                # Determine priority
                priority_str = item.get("priority", "medium").lower()
                priority = Priority(priority_str) if priority_str in ["high", "medium", "low"] else Priority.MEDIUM
                
                # Check for keyword-based priority override
                keyword_priority, matched_keywords = self._keyword_priority_check(
                    item.get("description", "") + " " + item.get("source_text", "")
                )
                if keyword_priority and keyword_priority.value < priority.value:
                    priority = keyword_priority
                
                action = ActionItem(
                    id=str(uuid.uuid4()),
                    description=item.get("description", ""),
                    assignee=item.get("assignee"),
                    due_date=due_date,
                    due_date_reasoning=item.get("due_date_reasoning"),
                    priority=priority,
                    priority_reasoning=item.get("priority_reasoning"),
                    source_conversation_id=conversation.id,
                    source_conversation_title=conversation.title,
                    source_type=conversation.source_type,
                    conversation_type=conversation.conversation_type,
                    customer_name=conversation.customer_name,
                    extracted_from_text=item.get("source_text", ""),
                    related_participants=[p.email for p in conversation.participants[:5]],
                    keywords_matched=matched_keywords
                )
                actions.append(action)
            
            logger.debug(f"Extracted {len(actions)} actions from '{conversation.title}'")
            return actions
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            return []
        except Exception as e:
            logger.error(f"Action extraction failed for '{conversation.title}': {e}")
            return []
    
    def extract_actions_batch(self, conversations: List[Conversation]) -> List[ActionItem]:
        """Extract actions from multiple conversations."""
        all_actions = []
        
        for i, conv in enumerate(conversations):
            logger.info(f"Processing conversation {i+1}/{len(conversations)}: {conv.title}")
            actions = self.extract_actions_from_conversation(conv)
            all_actions.extend(actions)
        
        logger.info(f"Extracted {len(all_actions)} total action items from {len(conversations)} conversations")
        return all_actions
    
    def classify_conversation(self, conversation: Conversation) -> Tuple[ConversationType, Optional[str]]:
        """Use LLM to classify conversation if automatic classification is uncertain."""
        if conversation.conversation_type != ConversationType.UNKNOWN:
            return conversation.conversation_type, conversation.customer_name
        
        # Prepare text for classification
        sample_text = conversation.full_text[:4000]
        participants_str = ", ".join([
            f"{p.display_name or p.email} ({p.organization or 'unknown org'})"
            for p in conversation.participants[:10]
        ])
        
        user_prompt = f"""Classify this conversation:

Title: {conversation.title}
Participants: {participants_str}

Sample content:
{sample_text}

Determine if this is a customer conversation or internal discussion."""

        try:
            response = self._call_llm(CLASSIFICATION_SYSTEM_PROMPT, user_prompt)
            result = json.loads(response)
            
            is_customer = result.get("is_customer", False)
            customer_name = result.get("customer_name")
            
            conv_type = ConversationType.CUSTOMER if is_customer else ConversationType.INTERNAL
            
            logger.debug(f"Classified '{conversation.title}' as {conv_type.value}")
            return conv_type, customer_name
            
        except Exception as e:
            logger.warning(f"Classification failed for '{conversation.title}': {e}")
            return ConversationType.UNKNOWN, None
    
    def prioritize_actions(self, actions: List[ActionItem]) -> List[ActionItem]:
        """Apply additional prioritization logic to actions."""
        now = datetime.utcnow()
        
        for action in actions:
            # Boost priority for overdue items
            if action.due_date and action.due_date < now:
                if action.priority != Priority.HIGH:
                    action.priority = Priority.HIGH
                    action.priority_reasoning = (action.priority_reasoning or "") + " [Escalated: overdue]"
            
            # Boost priority for customer-facing items
            if action.conversation_type == ConversationType.CUSTOMER:
                if action.priority == Priority.LOW:
                    action.priority = Priority.MEDIUM
                    action.priority_reasoning = (action.priority_reasoning or "") + " [Escalated: customer-facing]"
            
            # Boost priority for items due within 24 hours
            if action.due_date:
                hours_until_due = (action.due_date - now).total_seconds() / 3600
                if 0 < hours_until_due <= 24 and action.priority != Priority.HIGH:
                    action.priority = Priority.HIGH
                    action.priority_reasoning = (action.priority_reasoning or "") + " [Escalated: due within 24h]"
        
        # Sort by priority and due date
        priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        actions.sort(key=lambda a: (
            priority_order.get(a.priority, 2),
            a.due_date or datetime.max
        ))
        
        return actions


class RuleBasedExtractor:
    """Fallback rule-based action extractor when LLM is unavailable."""
    
    ACTION_PATTERNS = [
        r"(?:please|pls|kindly)\s+(.{10,100}?)(?:\.|$)",
        r"(?:can you|could you|will you|would you)\s+(.{10,100}?)(?:\?|$)",
        r"(?:need to|needs to|must)\s+(.{10,100}?)(?:\.|$)",
        r"(?:action required|action needed)[:\s]+(.{10,100}?)(?:\.|$)",
        r"(?:follow up|followup)[:\s]+(.{10,100}?)(?:\.|$)",
        r"(?:todo|to-do|to do)[:\s]+(.{10,100}?)(?:\.|$)",
        r"(?:by|before|due)\s+(?:eod|end of day|tomorrow|monday|tuesday|wednesday|thursday|friday|next week)[,\s]+(.{10,100}?)(?:\.|$)",
    ]
    
    def __init__(self, settings: Settings):
        self.settings = settings
    
    def extract_actions(self, conversation: Conversation) -> List[ActionItem]:
        """Extract actions using regex patterns."""
        actions = []
        text = conversation.full_text
        
        for pattern in self.ACTION_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                action_text = match.group(1).strip()
                if len(action_text) < 10:
                    continue
                
                # Determine priority from keywords
                priority = Priority.MEDIUM
                keywords = []
                
                for kw in self.settings.high_priority_keywords:
                    if kw.lower() in action_text.lower():
                        priority = Priority.HIGH
                        keywords.append(kw)
                        break
                
                if priority != Priority.HIGH:
                    for kw in self.settings.medium_priority_keywords:
                        if kw.lower() in action_text.lower():
                            keywords.append(kw)
                
                actions.append(ActionItem(
                    id=str(uuid.uuid4()),
                    description=action_text,
                    assignee=None,
                    due_date=None,
                    priority=priority,
                    priority_reasoning=f"Matched keywords: {keywords}" if keywords else "Default priority",
                    source_conversation_id=conversation.id,
                    source_conversation_title=conversation.title,
                    source_type=conversation.source_type,
                    conversation_type=conversation.conversation_type,
                    customer_name=conversation.customer_name,
                    extracted_from_text=match.group(0),
                    keywords_matched=keywords
                ))
        
        return actions
