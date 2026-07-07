"""Configuration for MGM Resorts Network Profile agent."""

import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # MIMIR / Cisco SSO auth
    mimir_username: str = Field(default="")
    mimir_cookie_file: str = Field(default="default")
    mimir_cache_dir: str = Field(default="/tmp/mimir-cache")
    mimir_cache_days: int = Field(default=1)
    mimir_url: str = Field(default="https://mimir-prod.cisco.com")

    # Target company
    np_cpy_key: int = Field(default=172361)

    # CLI commands to run per device for data extraction
    np_cli_commands: List[str] = Field(
        default=["show version", "show ip interface brief", "show clock"]
    )

    # How many devices to pull CLI from (0 = all, use with care on large accounts)
    np_device_cli_limit: int = Field(default=50)

    # Agent behaviour
    output_dir: str = Field(default="./output")
    log_level: str = Field(default="INFO")

    def validate_auth(self) -> bool:
        """Return True when minimum auth config is present."""
        return bool(self.mimir_username or self.mimir_cookie_file == "default")


def get_settings() -> Settings:
    return Settings()
