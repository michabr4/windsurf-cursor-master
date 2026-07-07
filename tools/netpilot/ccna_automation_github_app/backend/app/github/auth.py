"""GitHub App JWT and installation access tokens."""

from __future__ import annotations

import time
from typing import Any

import httpx
import jwt

from app.config import Settings, get_settings

GITHUB_API = "https://api.github.com"


def create_app_jwt(settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    private_key = settings.load_github_private_key()
    if not private_key or not settings.github_app_id:
        raise ValueError("GitHub App credentials are not configured")

    now = int(time.time())
    payload = {
        "iat": now - 60,
        "exp": now + 600,
        "iss": settings.github_app_id,
    }
    return jwt.encode(payload, private_key, algorithm="RS256")


def get_installation_access_token(
    installation_id: int,
    settings: Settings | None = None,
) -> dict[str, Any]:
    app_jwt = create_app_jwt(settings)
    url = f"{GITHUB_API}/app/installations/{installation_id}/access_tokens"
    response = httpx.post(
        url,
        headers={
            "Authorization": f"Bearer {app_jwt}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        timeout=30.0,
    )
    response.raise_for_status()
    return response.json()
