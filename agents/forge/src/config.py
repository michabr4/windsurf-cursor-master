"""Configuration loader — reads .env and exposes settings."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)


class Config:
    # LLM (Ollama — runs locally, no API key needed)
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama3.1:8b")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "ollama")  # Ollama ignores this but OpenAI client requires it

    # Azure / Microsoft Graph
    AZURE_CLIENT_ID: str = os.getenv("AZURE_CLIENT_ID", "")
    AZURE_TENANT_ID: str = os.getenv("AZURE_TENANT_ID", "")
    GRAPH_SCOPES: list[str] = ["Mail.Read", "Mail.Send", "User.Read"]

    # Digest
    MY_EMAIL: str = os.getenv("MY_EMAIL", "")
    EMAIL_SCAN_COUNT: int = int(os.getenv("EMAIL_SCAN_COUNT", "50"))
    LOOKBACK_HOURS: int = int(os.getenv("LOOKBACK_HOURS", "24"))

    @classmethod
    def validate(cls) -> list[str]:
        """Return list of missing required config values."""
        missing = []
        if not cls.AZURE_CLIENT_ID or "your" in cls.AZURE_CLIENT_ID:
            missing.append("AZURE_CLIENT_ID")
        if not cls.AZURE_TENANT_ID or "your" in cls.AZURE_TENANT_ID:
            missing.append("AZURE_TENANT_ID")
        if not cls.MY_EMAIL or "your" in cls.MY_EMAIL:
            missing.append("MY_EMAIL")
        return missing


cfg = Config()
