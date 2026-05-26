"""GitHub webhook signature verification and event handling."""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any

from app.config import Settings, get_settings
from app.db import get_connection, record_webhook_event, upsert_installation


def verify_signature(payload: bytes, signature_header: str | None, secret: str) -> bool:
    if not signature_header or not secret:
        return False
    if not signature_header.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header)


def handle_webhook(
    payload: bytes,
    *,
    event_type: str,
    delivery_id: str | None,
    signature_header: str | None,
    settings: Settings | None = None,
) -> dict[str, Any]:
    settings = settings or get_settings()
    if not settings.github_webhook_secret:
        return {"ok": False, "error": "GITHUB_WEBHOOK_SECRET not configured"}

    if not verify_signature(payload, signature_header, settings.github_webhook_secret):
        return {"ok": False, "error": "invalid signature"}

    try:
        data = json.loads(payload.decode("utf-8"))
    except json.JSONDecodeError:
        return {"ok": False, "error": "invalid JSON payload"}

    action = data.get("action") if isinstance(data.get("action"), str) else None
    installation = data.get("installation") or {}
    installation_id = installation.get("id")
    account = installation.get("account") or {}

    with get_connection(settings) as conn:
        record_webhook_event(
            conn,
            delivery_id=delivery_id,
            event_type=event_type,
            action=action,
            installation_id=int(installation_id) if installation_id else None,
            payload=data,
        )

        if event_type == "installation" and installation_id:
            if action in {"created", "added"}:
                upsert_installation(
                    conn,
                    installation_id=int(installation_id),
                    account_login=account.get("login"),
                    account_type=account.get("type"),
                )
            elif action == "deleted":
                conn.execute(
                    "DELETE FROM github_installations WHERE installation_id = ?",
                    (int(installation_id),),
                )

    return {
        "ok": True,
        "event": event_type,
        "action": action,
        "installation_id": installation_id,
    }
