#!/usr/bin/env python3
"""Inject saved handoff context when a session starts or after compaction."""

from __future__ import annotations

import json
import sys
from pathlib import Path

STATE_FILE = Path(".cursor/handoff/STATE.md")
BRIEF_FILE = Path(".session-logs/LAST_SESSION_BRIEF.md")
MAX_CHARS = 4000


def load_input() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    return json.loads(raw)


def read_excerpt(path: Path, limit: int) -> str:
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def main() -> int:
    _ = load_input()

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

    context = "\n\n".join(sections)
    print(json.dumps({"additional_context": context}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
