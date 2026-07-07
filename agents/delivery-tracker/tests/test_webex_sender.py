"""Unit tests for webex_sender.

HTTP calls are mocked via the `responses` library — no real Webex API required.
"""

from __future__ import annotations

import pytest
import responses as rsps_lib

from config import Settings
from webex_sender import (
    WebexSendError,
    _MAX_MARKDOWN_BYTES,
    _truncate,
    send_markdown,
    send_report,
)

_WEBEX_URL = "https://webexapis.com/v1/messages"
_TOKEN = "test-bot-token-xyz"
_ROOM_ID = "Y2lzY29zcGFyazovL3VzL1JPT00vYWJj"
_EMAIL = "sdm@example.com"
_MSG_ID = "msg-abc123"


# ── _truncate ─────────────────────────────────────────────────────────────────

def test_truncate_short_text_unchanged():
    text = "Hello, world!"
    assert _truncate(text) == text


def test_truncate_cuts_at_byte_limit():
    long_text = "a" * (_MAX_MARKDOWN_BYTES + 500)
    result = _truncate(long_text)
    assert len(result.encode("utf-8")) <= _MAX_MARKDOWN_BYTES + 100
    assert "truncated" in result.lower()


def test_truncate_exact_limit_unchanged():
    text = "a" * _MAX_MARKDOWN_BYTES
    assert _truncate(text) == text


# ── send_markdown ─────────────────────────────────────────────────────────────

@rsps_lib.activate
def test_send_markdown_to_room_succeeds():
    rsps_lib.add(rsps_lib.POST, _WEBEX_URL, json={"id": _MSG_ID}, status=200)
    msg_id = send_markdown("**Weekly report**", bot_token=_TOKEN, room_id=_ROOM_ID)
    assert msg_id == _MSG_ID


@rsps_lib.activate
def test_send_markdown_to_person_succeeds():
    rsps_lib.add(rsps_lib.POST, _WEBEX_URL, json={"id": _MSG_ID}, status=200)
    msg_id = send_markdown("**Weekly report**", bot_token=_TOKEN, person_email=_EMAIL)
    assert msg_id == _MSG_ID


@rsps_lib.activate
def test_auth_header_contains_bearer_token():
    rsps_lib.add(rsps_lib.POST, _WEBEX_URL, json={"id": _MSG_ID}, status=200)
    send_markdown("text", bot_token=_TOKEN, room_id=_ROOM_ID)
    req = rsps_lib.calls[0].request
    assert req.headers["Authorization"] == f"Bearer {_TOKEN}"


@rsps_lib.activate
def test_room_id_sent_in_payload():
    rsps_lib.add(rsps_lib.POST, _WEBEX_URL, json={"id": _MSG_ID}, status=200)
    send_markdown("text", bot_token=_TOKEN, room_id=_ROOM_ID)
    import json
    body = json.loads(rsps_lib.calls[0].request.body)
    assert body["roomId"] == _ROOM_ID
    assert "toPersonEmail" not in body


@rsps_lib.activate
def test_person_email_sent_when_no_room_id():
    rsps_lib.add(rsps_lib.POST, _WEBEX_URL, json={"id": _MSG_ID}, status=200)
    send_markdown("text", bot_token=_TOKEN, person_email=_EMAIL)
    import json
    body = json.loads(rsps_lib.calls[0].request.body)
    assert body["toPersonEmail"] == _EMAIL
    assert "roomId" not in body


@rsps_lib.activate
def test_room_id_takes_priority_over_email():
    rsps_lib.add(rsps_lib.POST, _WEBEX_URL, json={"id": _MSG_ID}, status=200)
    send_markdown("text", bot_token=_TOKEN, room_id=_ROOM_ID, person_email=_EMAIL)
    import json
    body = json.loads(rsps_lib.calls[0].request.body)
    assert body["roomId"] == _ROOM_ID
    assert "toPersonEmail" not in body


def test_raises_value_error_when_no_target():
    with pytest.raises(ValueError, match="room_id or person_email"):
        send_markdown("text", bot_token=_TOKEN)


@rsps_lib.activate
def test_raises_webex_send_error_on_4xx():
    rsps_lib.add(rsps_lib.POST, _WEBEX_URL, status=401, body="Unauthorized")
    with pytest.raises(WebexSendError) as exc_info:
        send_markdown("text", bot_token=_TOKEN, room_id=_ROOM_ID)
    assert exc_info.value.status_code == 401


@rsps_lib.activate
def test_raises_webex_send_error_on_5xx():
    rsps_lib.add(rsps_lib.POST, _WEBEX_URL, status=503, body="Service Unavailable")
    with pytest.raises(WebexSendError) as exc_info:
        send_markdown("text", bot_token=_TOKEN, room_id=_ROOM_ID)
    assert exc_info.value.status_code == 503


# ── send_report ───────────────────────────────────────────────────────────────

@rsps_lib.activate
def test_send_report_uses_settings():
    rsps_lib.add(rsps_lib.POST, _WEBEX_URL, json={"id": _MSG_ID}, status=200)
    settings = Settings(
        helix_base_url="https://helix.test",
        helix_api_token="tok",
        webex_bot_token=_TOKEN,
        webex_room_id=_ROOM_ID,
    )
    msg_id = send_report("## Report", settings)
    assert msg_id == _MSG_ID


def test_send_report_raises_when_not_configured():
    settings = Settings(
        helix_base_url="https://helix.test",
        helix_api_token="tok",
    )
    with pytest.raises(ValueError, match="Webex not configured"):
        send_report("## Report", settings)
