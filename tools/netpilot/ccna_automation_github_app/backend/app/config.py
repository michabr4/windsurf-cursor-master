"""Application configuration from environment."""

from __future__ import annotations

import os
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = APP_ROOT / "data"
DEFAULT_DB_PATH = DATA_DIR / "ccna_study.db"
SCHEMA_PATH = APP_ROOT / "data_model" / "schema.sql"
SEED_PATH = APP_ROOT / "data_model" / "seed.json"
DOMAIN_MAP_PATH = APP_ROOT / "data_model" / "domain_map.yaml"


def _env(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


class Settings:
    database_path: Path
    source_html_path: Path | None
    github_app_id: str
    github_webhook_secret: str
    github_private_key: str
    github_private_key_path: Path | None
    cors_origin_regex: str

    def __init__(self) -> None:
        db = _env("DATABASE_PATH")
        self.database_path = Path(db) if db else DEFAULT_DB_PATH

        html = _env("SOURCE_HTML_PATH")
        self.source_html_path = Path(html) if html else None

        self.github_app_id = _env("GITHUB_APP_ID")
        self.github_webhook_secret = _env("GITHUB_WEBHOOK_SECRET")
        self.github_private_key = _env("GITHUB_APP_PRIVATE_KEY")
        key_path = _env("GITHUB_APP_PRIVATE_KEY_PATH")
        self.github_private_key_path = Path(key_path) if key_path else None

        self.cors_origin_regex = _env(
            "CORS_ORIGIN_REGEX",
            r"https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+):5173",
        )

    @property
    def github_configured(self) -> bool:
        has_key = bool(self.github_private_key) or (
            self.github_private_key_path and self.github_private_key_path.is_file()
        )
        return bool(self.github_app_id and self.github_webhook_secret and has_key)

    def load_github_private_key(self) -> str | None:
        if self.github_private_key:
            return self.github_private_key.replace("\\n", "\n")
        if self.github_private_key_path and self.github_private_key_path.is_file():
            return self.github_private_key_path.read_text(encoding="utf-8")
        return None


def get_settings() -> Settings:
    return Settings()
