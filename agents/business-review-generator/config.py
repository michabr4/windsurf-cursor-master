"""Configuration for Business Review Generator."""

from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    helix_base_url: str = Field(default="")
    helix_api_token: str = Field(default="")
    salesforce_mcp_token: str = Field(default="")
    webex_bot_token: str = Field(default="")
    webex_room_id: str = Field(default="")
    data_dir: str = Field(default="./data/runs")
    llm_model: str = Field(default="")
    llm_base_url: str = Field(default="")
    log_level: str = Field(default="INFO")
    dry_run: bool = Field(default=False)
    http_timeout: int = Field(default=15)

    @property
    def delivery_tracker_dir(self) -> Path:
        return Path(self.data_dir) / "delivery-tracker"

    @property
    def business_review_dir(self) -> Path:
        return Path(self.data_dir) / "business-review"

    @property
    def auth_header(self) -> dict:
        return {"Authorization": f"Bearer {self.helix_api_token}"}


def get_settings() -> Settings:
    return Settings()
