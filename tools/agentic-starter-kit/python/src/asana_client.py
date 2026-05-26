"""Minimal Asana REST client for local review tools.

Only calls https://app.asana.com — never user-supplied hosts (SSRF-safe for this use).
"""

from __future__ import annotations

import os
from typing import Any, Dict

import requests
from dotenv import load_dotenv


load_dotenv()

_ASANA_BASE = "https://app.asana.com/api/1.0"
_DEFAULT_TIMEOUT = 30

_TASK_OPT_FIELDS = (
    "name,notes,html_notes,due_on,due_at,completed,assignee,assignee.name,"
    "permalink_url,projects,projects.name,num_subtasks,custom_fields,"
    "custom_fields.name,custom_fields.type,custom_fields.display_value,"
    "custom_fields.text_value,custom_fields.number_value,custom_fields.enum_value"
)


class AsanaClient:
    def __init__(self, session: requests.Session | None = None) -> None:
        self._session = session or requests.Session()

    def _require_token(self) -> str:
        from src.asana_oauth import get_valid_access_token

        return get_valid_access_token()

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._require_token()}",
            "Accept": "application/json",
        }

    def get_task(self, task_gid: str) -> Dict[str, Any]:
        gid = normalize_task_gid(task_gid)
        url = f"{_ASANA_BASE}/tasks/{gid}"
        params = {"opt_fields": _TASK_OPT_FIELDS}
        resp = self._session.get(
            url,
            headers=self._headers(),
            params=params,
            timeout=_DEFAULT_TIMEOUT,
        )
        if resp.status_code != 200:
            raise RuntimeError(_format_asana_error(resp))
        data = resp.json().get("data")
        if not isinstance(data, dict):
            raise RuntimeError("Unexpected Asana response: missing task data")
        return data

    def add_comment_story(self, task_gid: str, text: str) -> Dict[str, Any]:
        gid = normalize_task_gid(task_gid)
        if not text.strip():
            raise ValueError("Comment text is empty")
        url = f"{_ASANA_BASE}/tasks/{gid}/stories"
        resp = self._session.post(
            url,
            headers={**self._headers(), "Content-Type": "application/json"},
            json={"data": {"text": text.strip()}},
            timeout=_DEFAULT_TIMEOUT,
        )
        if resp.status_code not in (200, 201):
            raise RuntimeError(_format_asana_error(resp))
        data = resp.json().get("data")
        if not isinstance(data, dict):
            raise RuntimeError("Unexpected Asana response: missing story data")
        return data


def normalize_task_gid(task_gid: str) -> str:
    s = task_gid.strip()
    if not s:
        raise ValueError("Task id is empty")
    if s.isdigit():
        return s
    parsed = parse_task_gid_from_url(s)
    if parsed:
        return parsed
    raise ValueError(
        "Task id must be numeric or a standard Asana task URL "
        "(for example https://app.asana.com/0/<project>/<task>)"
    )


def parse_task_gid_from_url(url: str) -> str | None:
    """Extract task GID from a browser URL like https://app.asana.com/0/.../TASK_GID."""
    u = url.strip()
    if "asana.com" not in u:
        return None
    # Path ends with /digits
    i = u.rfind("/")
    if i < 0:
        return None
    tail = u[i + 1 :].split("?", 1)[0].strip()
    if tail.isdigit():
        return tail
    return None


def _format_asana_error(resp: requests.Response) -> str:
    try:
        body = resp.json()
        errs = body.get("errors")
        if isinstance(errs, list) and errs:
            first = errs[0]
            if isinstance(first, dict) and first.get("message"):
                return f"Asana API {resp.status_code}: {first['message']}"
    except Exception:
        pass
    return f"Asana API {resp.status_code}: {resp.text[:500]}"
