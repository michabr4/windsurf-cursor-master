#!/usr/bin/env python3
"""Inject saved handoff context when a session starts or after compaction."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HANDOFF_DIR = Path(os.environ.get("CONTEXT_HANDOFF_DIR", ".cursor/handoff"))
STATE_FILE = HANDOFF_DIR / "STATE.md"
BRIEF_FILE = Path(".session-logs/LAST_SESSION_BRIEF.md")
MAX_CHARS = 4000

VSCODE_EVENT_ALIASES = {
    "SessionStart": "sessionStart",
    "PreCompact": "preCompact",
}


def load_input() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    return json.loads(raw)


def is_vscode_platform(event: str) -> bool:
    platform = os.environ.get("CONTEXT_HANDOFF_PLATFORM", "").lower()
    if platform == "vscode":
        return True
    if platform == "cursor":
        return False
    return bool(event and event[0].isupper())


def read_excerpt(path: Path, limit: int) -> str:
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def emit_context(context: str, *, vscode: bool, hook_event_name: str) -> None:
    if not context:
        print("{}")
        return
    if vscode:
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": hook_event_name,
                        "additionalContext": context,
                    }
                }
            )
        )
        return
    print(json.dumps({"additional_context": context}))


def main() -> int:
    payload = load_input()
    raw_event = str(payload.get("hook_event_name") or payload.get("hookEventName") or "")
    vscode = is_vscode_platform(raw_event)

    state = read_excerpt(STATE_FILE, MAX_CHARS)
    brief = read_excerpt(BRIEF_FILE, 800)
    if not state and not brief:
        print("{}")
        return 0

    sections = [
        "SESSION HANDOFF — continue the prior task; do not restart from scratch.",
    ]
    if brief:
        sections.append(f"Last session brief:\n{brief}")
    if state:
        sections.append(f"Handoff state:\n{state}")

    hook_event_name = raw_event or "SessionStart"
    emit_context("\n\n".join(sections), vscode=vscode, hook_event_name=hook_event_name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
