#!/usr/bin/env python3
"""Gate git push until Bugbot has reviewed the current HEAD."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

STAMP_FILE = Path(".cursor/bugbot-stamp.json")
GIT_PUSH_RE = re.compile(r"\bgit\b.*\bpush\b", re.IGNORECASE | re.DOTALL)


def read_stdin_json() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    return json.loads(raw)


def current_head() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return None
    return result.stdout.strip() or None


def stamp_matches_head(head: str) -> bool:
    if not STAMP_FILE.is_file():
        return False
    try:
        stamp = json.loads(STAMP_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    return stamp.get("head") == head and stamp.get("status") == "reviewed"


def emit(payload: dict) -> None:
    print(json.dumps(payload))
    sys.exit(0)


def main() -> None:
    payload = read_stdin_json()
    command = payload.get("command") or ""

    if not GIT_PUSH_RE.search(command):
        emit({"permission": "allow"})
        return

    if re.search(r"\b--dry-run\b", command, re.IGNORECASE):
        emit({"permission": "allow"})
        return

    head = current_head()
    if head and stamp_matches_head(head):
        emit({"permission": "allow"})
        return

    emit(
        {
            "permission": "ask",
            "user_message": (
                "Bugbot review is required before pushing to GitHub. "
                "Approve only after the agent has run Bugbot on the current changes."
            ),
            "agent_message": (
                "Push blocked: run Bugbot first (review-bugbot skill, bugbot subagent, "
                "Diff: branch changes). After review, write .cursor/bugbot-stamp.json with "
                "the current git HEAD, then retry git push."
            ),
        }
    )


if __name__ == "__main__":
    main()
