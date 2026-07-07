"""Asana OAuth 2.0 (authorization code) for local task review tools.

Uses ASANA_CLIENT_ID, ASANA_CLIENT_SECRET, and ASANA_OAUTH_REDIRECT_URI from .env.
Stores ASANA_ACCESS_TOKEN, ASANA_REFRESH_TOKEN, and ASANA_TOKEN_EXPIRES_AT in .env after login.
"""

from __future__ import annotations

import os
import secrets
import time
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv


load_dotenv()

_AUTHORIZE_URL = "https://app.asana.com/-/oauth_authorize"
_TOKEN_URL = "https://app.asana.com/-/oauth_token"
_DEFAULT_SCOPES = "default"
_pending_state: Dict[str, float] = {}
_STATE_TTL_SEC = 600


def repo_env_path() -> Path:
    return Path(__file__).resolve().parents[2] / ".env"


def oauth_configured() -> bool:
    return bool(os.getenv("ASANA_CLIENT_ID", "").strip() and os.getenv("ASANA_CLIENT_SECRET", "").strip())


def redirect_uri() -> str:
    explicit = os.getenv("ASANA_OAUTH_REDIRECT_URI", "").strip()
    if explicit:
        return explicit
    port = os.getenv("ASANA_REVIEW_PORT", "8845").strip() or "8845"
    return f"http://127.0.0.1:{port}/oauth/callback"


def has_refresh_token() -> bool:
    return bool(os.getenv("ASANA_REFRESH_TOKEN", "").strip())


def has_access_token() -> bool:
    return bool(os.getenv("ASANA_ACCESS_TOKEN", "").strip())


def is_authenticated() -> bool:
    if has_refresh_token():
        return True
    return has_access_token() and not oauth_configured()


def login_start_url() -> str:
    """Build Asana authorize URL and remember CSRF state."""
    client_id = _require_client_id()
    state = secrets.token_urlsafe(24)
    _pending_state[state] = time.time()
    _prune_states()
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri(),
        "response_type": "code",
        "state": state,
        "scope": os.getenv("ASANA_OAUTH_SCOPES", _DEFAULT_SCOPES).strip() or _DEFAULT_SCOPES,
    }
    return f"{_AUTHORIZE_URL}?{urlencode(params)}"


def exchange_code(code: str, state: str) -> None:
    if state not in _pending_state:
        raise ValueError("Invalid or expired OAuth state. Start login again from /oauth/start.")
    del _pending_state[state]
    _exchange_token(
        {
            "grant_type": "authorization_code",
            "client_id": _require_client_id(),
            "client_secret": _require_client_secret(),
            "redirect_uri": redirect_uri(),
            "code": code,
        }
    )


def get_valid_access_token() -> str:
    """Return a bearer token, refreshing via OAuth when configured."""
    load_dotenv(override=True)

    if oauth_configured() and has_refresh_token():
        expires_at = _expires_at_epoch()
        access = os.getenv("ASANA_ACCESS_TOKEN", "").strip()
        if access and expires_at and time.time() < expires_at - 120:
            return access
        return _refresh_access_token()

    access = os.getenv("ASANA_ACCESS_TOKEN", "").strip()
    if access:
        return access

    if oauth_configured():
        port = os.getenv("ASANA_REVIEW_PORT", "8845")
        raise ValueError(
            "Asana is not connected yet. Open "
            f"http://127.0.0.1:{port}/oauth/start in your browser to sign in."
        )
    raise ValueError(
        "Missing Asana credentials. Set ASANA_CLIENT_ID and ASANA_CLIENT_SECRET, "
        "or ASANA_ACCESS_TOKEN for personal-token mode."
    )


def _refresh_access_token() -> str:
    refresh = os.getenv("ASANA_REFRESH_TOKEN", "").strip()
    if not refresh:
        raise ValueError("Missing ASANA_REFRESH_TOKEN. Sign in again at /oauth/start.")
    data = _exchange_token(
        {
            "grant_type": "refresh_token",
            "client_id": _require_client_id(),
            "client_secret": _require_client_secret(),
            "refresh_token": refresh,
        }
    )
    token = data.get("access_token")
    if not isinstance(token, str) or not token:
        raise RuntimeError("Asana refresh did not return an access_token.")
    return token


def _exchange_token(form: Dict[str, str]) -> Dict[str, Any]:
    resp = requests.post(_TOKEN_URL, data=form, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"Asana OAuth token error {resp.status_code}: {resp.text[:500]}")
    payload = resp.json()
    if not isinstance(payload, dict):
        raise RuntimeError("Unexpected Asana OAuth response.")
    access = payload.get("access_token")
    if not isinstance(access, str) or not access:
        raise RuntimeError("Asana OAuth response missing access_token.")

    updates: Dict[str, str] = {"ASANA_ACCESS_TOKEN": access}
    refresh = payload.get("refresh_token")
    if isinstance(refresh, str) and refresh:
        updates["ASANA_REFRESH_TOKEN"] = refresh
    expires_in = payload.get("expires_in")
    if isinstance(expires_in, (int, float)) and expires_in > 0:
        updates["ASANA_TOKEN_EXPIRES_AT"] = str(int(time.time() + float(expires_in)))

    _write_env_updates(repo_env_path(), updates)
    load_dotenv(override=True)
    return payload


def _write_env_updates(env_path: Path, updates: Dict[str, str]) -> None:
    lines: list[str] = []
    if env_path.is_file():
        lines = env_path.read_text(encoding="utf-8").splitlines()

    remaining = dict(updates)
    out: list[str] = []
    seen_keys: set[str] = set()

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in line:
            out.append(line)
            continue
        key, _, _ = line.partition("=")
        key = key.strip()
        if key in remaining:
            out.append(f"{key}={remaining.pop(key)}")
            seen_keys.add(key)
        else:
            out.append(line)

    for key, value in remaining.items():
        if key not in seen_keys:
            out.append(f"{key}={value}")

    text = "\n".join(out)
    if text and not text.endswith("\n"):
        text += "\n"
    env_path.write_text(text, encoding="utf-8")


def _expires_at_epoch() -> Optional[float]:
    raw = os.getenv("ASANA_TOKEN_EXPIRES_AT", "").strip()
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def _require_client_id() -> str:
    v = os.getenv("ASANA_CLIENT_ID", "").strip()
    if not v:
        raise ValueError("Missing ASANA_CLIENT_ID in .env")
    return v


def _require_client_secret() -> str:
    v = os.getenv("ASANA_CLIENT_SECRET", "").strip()
    if not v:
        raise ValueError("Missing ASANA_CLIENT_SECRET in .env")
    return v


def _prune_states() -> None:
    now = time.time()
    expired = [s for s, t in _pending_state.items() if now - t > _STATE_TTL_SEC]
    for s in expired:
        del _pending_state[s]
