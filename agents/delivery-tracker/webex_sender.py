"""Webex Messaging sender for Delivery Tracker agent.

Sends a markdown-formatted summary to a Webex room or person.
Credentials are read from Settings (env vars WEBEX_BOT_TOKEN, WEBEX_ROOM_ID
or WEBEX_PERSON_EMAIL) — never hardcoded.

Typical call:
    from webex_sender import send_report
    msg_id = send_report(markdown_text, settings)
"""

from __future__ import annotations

import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)

_WEBEX_MESSAGES_URL = "https://webexapis.com/v1/messages"
_MAX_MARKDOWN_BYTES = 7_000


class WebexSendError(Exception):
    """Raised when the Webex API call fails."""

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(f"Webex API {status_code}: {detail}")
        self.status_code = status_code
        self.detail = detail


def _truncate(text: str, limit: int = _MAX_MARKDOWN_BYTES) -> str:
    """Trim text to at most `limit` UTF-8 bytes, appending a note if cut."""
    encoded = text.encode("utf-8")
    if len(encoded) <= limit:
        return text
    truncated = encoded[:limit].decode("utf-8", errors="ignore")
    return truncated + "\n\n*[Report truncated — run `--output md` for full output]*"


def send_markdown(
    markdown: str,
    *,
    bot_token: str,
    room_id: Optional[str] = None,
    person_email: Optional[str] = None,
    timeout: int = 15,
) -> str:
    """Post a markdown message to a Webex room or person.

    Args:
        markdown: Markdown body to send.
        bot_token: Webex bot bearer token (from env, never hardcoded).
        room_id: Webex room/space ID. Takes priority over person_email.
        person_email: Recipient email when room_id is not set.
        timeout: HTTP request timeout in seconds.

    Returns:
        The Webex message ID string.

    Raises:
        ValueError: If neither room_id nor person_email is supplied.
        WebexSendError: If the Webex API returns a non-2xx response.
    """
    if not room_id and not person_email:
        raise ValueError("Either room_id or person_email must be provided.")

    payload: dict = {"markdown": _truncate(markdown)}
    if room_id:
        payload["roomId"] = room_id
    else:
        payload["toPersonEmail"] = person_email

    try:
        resp = requests.post(
            _WEBEX_MESSAGES_URL,
            headers={
                "Authorization": f"Bearer {bot_token}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=timeout,
        )
    except requests.exceptions.Timeout as exc:
        raise WebexSendError(0, f"Request timed out after {timeout}s") from exc
    except requests.exceptions.ConnectionError as exc:
        raise WebexSendError(0, f"Connection failed: {exc}") from exc

    if not resp.ok:
        raise WebexSendError(resp.status_code, resp.text[:200])

    data = resp.json()
    msg_id: str = data.get("id", "")
    logger.info("Webex message sent — id=%s room=%s", msg_id, room_id or person_email)
    return msg_id


def send_report(markdown: str, settings) -> str:  # type: ignore[annotation-unchecked]
    """Convenience wrapper: pull credentials from Settings and call send_markdown.

    Raises:
        ValueError: If Webex is not configured in settings.
        WebexSendError: If the API call fails.
    """
    if not settings.validate_webex():
        raise ValueError(
            "Webex not configured — set WEBEX_BOT_TOKEN and WEBEX_ROOM_ID (or WEBEX_PERSON_EMAIL)"
        )
    return send_markdown(
        markdown,
        bot_token=settings.webex_bot_token,
        room_id=settings.webex_room_id,
        person_email=settings.webex_person_email,
        timeout=settings.webex_timeout,
    )
