#!/usr/bin/env python3
"""Write a session handoff when context usage reaches the configured threshold."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

THRESHOLD_PERCENT = 60
HANDOFF_DIR = Path(".cursor/handoff")
STATE_FILE = HANDOFF_DIR / "STATE.md"
BRIEF_FILE = Path(".session-logs/LAST_SESSION_BRIEF.md")

# Conservative defaults; preCompact supplies exact values when available.
MODEL_CONTEXT_WINDOWS = {
    "opus": 200_000,
    "sonnet": 200_000,
    "haiku": 200_000,
    "claude": 200_000,
    "gpt-4": 128_000,
    "gpt-5": 128_000,
    "composer": 128_000,
    "default": 128_000,
}


def load_input() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    return json.loads(raw)


def resolve_context_window(model: str, payload: dict) -> int:
    explicit = payload.get("context_window_size")
    if isinstance(explicit, int) and explicit > 0:
        return explicit
    model_lower = (model or "").lower()
    for key, size in MODEL_CONTEXT_WINDOWS.items():
        if key != "default" and key in model_lower:
            return size
    return MODEL_CONTEXT_WINDOWS["default"]


def estimate_usage_from_transcript(payload: dict) -> float | None:
    """Rough context % from transcript file size (~4 chars/token on JSONL)."""
    transcript_path = payload.get("transcript_path")
    if not isinstance(transcript_path, str) or not transcript_path:
        return None
    path = Path(transcript_path)
    if not path.is_file():
        return None
    try:
        size = path.stat().st_size
    except OSError:
        return None
    if size <= 0:
        return None
    window = resolve_context_window(str(payload.get("model") or ""), payload)
    return (float(size) / 4.0 / float(window)) * 100.0


def compute_usage_percent(payload: dict) -> float | None:
    event = payload.get("hook_event_name") or payload.get("hookEventName") or ""

    if event == "preCompact":
        percent = payload.get("context_usage_percent")
        if isinstance(percent, (int, float)):
            return float(percent)
        tokens = payload.get("context_tokens")
        window = payload.get("context_window_size")
        if isinstance(tokens, (int, float)) and isinstance(window, (int, float)) and window > 0:
            return (float(tokens) / float(window)) * 100.0
        return None

    if event in ("afterAgentResponse", "stop", "postToolUse"):
        estimated = estimate_usage_from_transcript(payload)
        if estimated is not None:
            return estimated
        input_tokens = payload.get("input_tokens")
        if isinstance(input_tokens, (int, float)) and input_tokens > 0:
            window = resolve_context_window(str(payload.get("model") or ""), payload)
            return (float(input_tokens) / float(window)) * 100.0

    return None


def marker_path(conversation_id: str) -> Path:
    safe_id = conversation_id.replace("/", "_") or "unknown"
    return HANDOFF_DIR / f".triggered-{safe_id}"


def extract_transcript_snippets(transcript_path: str | None) -> tuple[str, str]:
    if not transcript_path:
        return "", ""
    path = Path(transcript_path)
    if not path.is_file():
        return "", ""

    last_user = ""
    last_assistant = ""
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            role = row.get("role")
            message = row.get("message") or {}
            parts = message.get("content") or []
            text_chunks: list[str] = []
            for part in parts:
                if isinstance(part, dict) and part.get("type") == "text":
                    text = part.get("text") or ""
                    if text.strip():
                        text_chunks.append(text.strip())
            combined = "\n".join(text_chunks).strip()
            if not combined:
                continue
            if role == "user":
                last_user = combined[:1200]
            elif role == "assistant":
                last_assistant = combined[:1200]
    except OSError:
        return "", ""

    return last_user, last_assistant


def write_handoff(payload: dict, usage_percent: float, *, force_refresh: bool) -> bool:
    conversation_id = str(payload.get("conversation_id") or "unknown")
    marker = marker_path(conversation_id)
    if marker.exists() and not force_refresh:
        return False

    HANDOFF_DIR.mkdir(parents=True, exist_ok=True)
    BRIEF_FILE.parent.mkdir(parents=True, exist_ok=True)

    transcript_path = payload.get("transcript_path")
    last_user, last_assistant = extract_transcript_snippets(
        transcript_path if isinstance(transcript_path, str) else None
    )
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    model = str(payload.get("model") or "unknown")

    state_lines = [
        "# Session Handoff",
        f"**Created:** {now}",
        f"**Context usage:** {usage_percent:.1f}% (threshold {THRESHOLD_PERCENT}%)",
        f"**Model:** {model}",
        f"**Conversation:** {conversation_id}",
        "",
        "## Last user request",
        last_user or "_Unavailable — enrich this section if you continue in-session._",
        "",
        "## Last agent summary",
        last_assistant or "_Unavailable — enrich this section if you continue in-session._",
        "",
        "## Resume instructions",
        "1. Read this file and `.session-logs/LAST_SESSION_BRIEF.md`.",
        "2. Do not restart from scratch — continue the active task.",
        "3. Update both files if the task scope changes materially.",
        "",
    ]
    STATE_FILE.write_text("\n".join(state_lines), encoding="utf-8")

    brief_lines = [
        "# Last Session Brief",
        f"**Date:** {now.split(' ')[0]}  **Agent:** Cursor",
        f"**Context usage at handoff:** {usage_percent:.1f}%",
        "**Files changed:** see git status / recent edits",
        f"**Key decisions:** handoff auto-created at {THRESHOLD_PERCENT}% context threshold",
        "**Active task:** see `.cursor/handoff/STATE.md` → Last user request",
        "**Next priority:** continue the task from the handoff without re-discovery",
        "",
    ]
    BRIEF_FILE.write_text("\n".join(brief_lines), encoding="utf-8")
    marker.write_text(now, encoding="utf-8")
    return True


def main() -> int:
    payload = load_input()
    event = payload.get("hook_event_name") or payload.get("hookEventName") or ""
    usage_percent = compute_usage_percent(payload)

    if usage_percent is None or usage_percent < THRESHOLD_PERCENT:
        print("{}")
        return 0

    force_refresh = event == "preCompact"
    created = write_handoff(payload, usage_percent, force_refresh=force_refresh)

    if event == "preCompact" and created:
        print(
            json.dumps(
                {
                    "user_message": (
                        f"Context handoff saved to {STATE_FILE} "
                        f"({usage_percent:.0f}% used). Open a new chat and ask the agent "
                        "to continue from that file."
                    )
                }
            )
        )
        return 0

    if event == "preCompact":
        print(
            json.dumps(
                {
                    "user_message": (
                        f"Context at {usage_percent:.0f}%. Handoff already on disk at {STATE_FILE}."
                    )
                }
            )
        )
        return 0

    if created and event in ("afterAgentResponse", "stop", "postToolUse"):
        print(
            json.dumps(
                {
                    "additional_context": (
                        f"Context usage is ~{usage_percent:.0f}% (threshold {THRESHOLD_PERCENT}%). "
                        f"Session handoff saved to {STATE_FILE}. Update it if the task changes; "
                        "open a new chat to continue from the handoff if needed."
                    )
                }
            )
        )
        return 0

    print("{}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
