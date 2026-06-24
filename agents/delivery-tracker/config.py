"""Configuration management for Delivery Tracker agent."""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Helix API
    helix_base_url: str = Field(default="")
    helix_api_token: str = Field(default="")
    helix_timeout: int = Field(default=30)

    # Agent behaviour
    lookback_days: int = Field(default=7)
    account_filter: Optional[str] = Field(default=None)
    output_dir: str = Field(default="./output")

    # Webex messaging
    webex_bot_token: str = Field(default="")
    webex_room_id: Optional[str] = Field(default=None)
    webex_person_email: Optional[str] = Field(default=None)
    webex_timeout: int = Field(default=15)

    # Logging
    log_level: str = Field(default="INFO")

    def validate_helix(self) -> bool:
        """Return True when minimum Helix credentials are present."""
        return bool(self.helix_base_url and self.helix_api_token)

    def validate_webex(self) -> bool:
        """Return True when minimum Webex credentials are present."""
        return bool(self.webex_bot_token and (self.webex_room_id or self.webex_person_email))

    @property
    def auth_header(self) -> dict:
        """HTTP Authorization header for Helix API calls."""
        return {"Authorization": f"Bearer {self.helix_api_token}"}


def get_settings() -> Settings:
    """Factory — returns a Settings instance."""
    return Settings()
