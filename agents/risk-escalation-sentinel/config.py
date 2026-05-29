"""Configuration for Risk & Escalation Sentinel."""

from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    """Settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    data_dir: str = Field(default="./data/runs")
    webex_bot_token: str = Field(default="")
    webex_room_id: str = Field(default="")
    helix_api_token: str = Field(default="")
    lookback_days: int = Field(default=7)
    log_level: str = Field(default="INFO")
    dry_run: bool = Field(default=False)

    @property
    def delivery_tracker_dir(self) -> Path:
        return Path(self.data_dir) / "delivery-tracker"

    @property
    def risk_sentinel_dir(self) -> Path:
        return Path(self.data_dir) / "risk-sentinel"

    def validate_inputs(self) -> bool:
        """Return True when required configuration is present."""
        data_path = Path(self.data_dir)
        if not data_path.is_dir():
            return False
        if not self.dry_run and not self.webex_bot_token.strip():
            return False
        return True


def get_settings() -> Settings:
    return Settings()
