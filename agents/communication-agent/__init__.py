"""Communication Intelligence Agent package."""

from .agent import CommunicationAgent, create_agent
from .config import Settings, get_settings
from .models import (
    ActionItem, Conversation, Message, Participant,
    AgentReport, Priority, SourceType, ConversationType
)

__version__ = "1.0.0"
__all__ = [
    "CommunicationAgent",
    "create_agent",
    "Settings",
    "get_settings",
    "ActionItem",
    "Conversation",
    "Message",
    "Participant",
    "AgentReport",
    "Priority",
    "SourceType",
    "ConversationType",
]
