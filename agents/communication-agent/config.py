"""Configuration management for the Communication Intelligence Agent."""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
from enum import Enum


class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class OutputFormat(str, Enum):
    JSON = "json"
    CSV = "csv"
    MARKDOWN = "markdown"


class RuntimeMode(str, Enum):
    CONTINUOUS = "continuous"
    INTERVAL = "interval"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Webex Configuration
    webex_access_token: str = Field(..., description="Webex API access token")
    webex_bot_token: Optional[str] = Field(None, description="Optional Webex bot token")
    
    # Microsoft Graph Configuration
    ms_client_id: str = Field(..., description="Azure AD application client ID")
    ms_client_secret: str = Field(..., description="Azure AD application client secret")
    ms_tenant_id: str = Field(..., description="Azure AD tenant ID")
    ms_user_email: str = Field(default="michabr4@cisco.com", description="User email for Graph API")
    
    # LLM Configuration
    llm_provider: LLMProvider = Field(default=LLMProvider.OPENAI, description="LLM provider to use")
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key")
    openai_model: str = Field(default="gpt-4-turbo-preview", description="OpenAI model to use")
    anthropic_api_key: Optional[str] = Field(None, description="Anthropic API key")
    anthropic_model: str = Field(default="claude-3-sonnet-20240229", description="Anthropic model to use")
    
    # Agent Configuration
    max_messages_per_room: int = Field(default=100, description="Max messages to fetch per Webex room")
    max_emails_to_fetch: int = Field(default=200, description="Max emails to fetch from Outlook")
    lookback_days: int = Field(default=7, description="Number of days to look back for messages")
    runtime_mode: RuntimeMode = Field(default=RuntimeMode.CONTINUOUS, description="Runtime mode: continuous or interval")
    runtime_interval_minutes: int = Field(default=60, description="Scheduled runtime interval in minutes")
    continuous_backoff_seconds: int = Field(default=5, description="Pause between continuous runs to avoid API thrash")
    
    # Output Configuration
    output_format: OutputFormat = Field(default=OutputFormat.JSON, description="Output format")
    output_dir: str = Field(default="./output", description="Output directory")
    
    # Classification Configuration
    internal_domains: List[str] = Field(
        default=["cisco.com", "webex.com", "ciscospark.com"],
        description="Domains considered internal"
    )
    
    # Priority Keywords
    high_priority_keywords: List[str] = Field(
        default=["urgent", "asap", "critical", "escalation", "p1", "sev1", "immediately"],
        description="Keywords indicating high priority"
    )
    medium_priority_keywords: List[str] = Field(
        default=["important", "soon", "this week", "follow up", "action required"],
        description="Keywords indicating medium priority"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        
    @property
    def active_llm_key(self) -> str:
        """Get the API key for the active LLM provider."""
        if self.llm_provider == LLMProvider.OPENAI:
            if not self.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            return self.openai_api_key
        else:
            if not self.anthropic_api_key:
                raise ValueError("Anthropic API key not configured")
            return self.anthropic_api_key
    
    @property
    def active_llm_model(self) -> str:
        """Get the model name for the active LLM provider."""
        if self.llm_provider == LLMProvider.OPENAI:
            return self.openai_model
        return self.anthropic_model


def get_settings() -> Settings:
    """Load and return application settings."""
    return Settings()
