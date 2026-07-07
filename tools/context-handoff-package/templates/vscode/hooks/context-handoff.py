#!/usr/bin/env python3
"""Write a complexity-adaptive session handoff when context usage hits tier thresholds."""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

HANDOFF_DIR = Path(os.environ.get("CONTEXT_HANDOFF_DIR", ".cursor/handoff"))
STATE_FILE = HANDOFF_DIR / "STATE.md"
BRIEF_FILE = Path(".session-logs/LAST_SESSION_BRIEF.md")
AGENT_LABEL = os.environ.get("CONTEXT_HANDOFF_AGENT", "Cursor")

TIER_ORDER = ("low", "medium", "high", "critical")

TIER_CONFIG: dict[str, dict[str, int | None]] = {
    "low": {"threshold": 65, "refresh_delta": None},
    "medium": {"threshold": 60, "refresh_delta": None},
    "high": {"threshold": 52, "refresh_delta": 12},
    "critical": {"threshold": 45, "refresh_delta": 10},
}

ENRICHMENT_HINTS: dict[str, str] = {
    "low": (
        "≤400 tokens total across both files. Budget: ~40 active task, ~50 progress, "
        "~30 files (max 5 paths), ~40 next step, ~20 blockers if any."
    ),
    "medium": (
        "≤400 tokens total across both files. Balanced budget across all five required fields."
    ),
    "high": (
        "≤400 tokens total across both files. Budget: ~60 active task, ~100 progress, "
        "~90 files (max 15 paths), ~50 next step, ~30 blockers if any."
    ),
    "critical": (
        "≤400 tokens total across both files. Budget: ~60 active task, ~100 progress, "
        "~90 files (max 15 paths), ~50 next step, ~40 blockers if any. "
        "Refresh handoff after each subagent completes or scope changes."
    ),
}

MULTI_FILE_KEYWORDS = (
    "refactor",
    "migrate",
    "migration",
    "across files",
    "multiple files",
    "multi-file",
    "orchestr",
    "integration",
)

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

PATH_KEYS = ("path", "target_file", "file_path", "target_notebook")
MAX_PATHS_IN_HINT = 15

VSCODE_EVENT_ALIASES = {
    "SessionStart": "sessionStart",
    "PreCompact": "preCompact",
    "Stop": "stop",
    "SubagentStop": "subagentStop",
    "PostToolUse": "postToolUse",
    "UserPromptSubmit": "userPromptSubmit",
}


@dataclass
class TranscriptAnalysis:
    last_user: str = ""
    last_assistant: str = ""
    tool_calls: int = 0
    subagent_calls: int = 0
    shell_calls: int = 0
    user_turns: int = 0
    unique_paths: set[str] = field(default_factory=set)
    sample_paths: list[str] = field(default_factory=list)


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


def normalize_event(event: str) -> str:
    return VSCODE_EVENT_ALIASES.get(event, event)


def conversation_id_from(payload: dict) -> str:
    return str(payload.get("conversation_id") or payload.get("sessionId") or "unknown")


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
    raw_event = payload.get("hook_event_name") or payload.get("hookEventName") or ""
    event = normalize_event(str(raw_event))

    if event == "preCompact":
        percent = payload.get("context_usage_percent")
        if isinstance(percent, (int, float)):
            return float(percent)
        tokens = payload.get("context_tokens")
        window = payload.get("context_window_size")
        if isinstance(tokens, (int, float)) and isinstance(window, (int, float)) and window > 0:
            return (float(tokens) / float(window)) * 100.0
        return None

    if event in ("afterAgentResponse", "stop", "postToolUse", "subagentStop"):
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


def load_marker(conversation_id: str) -> dict | None:
    path = marker_path(conversation_id)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def save_marker(
    conversation_id: str,
    *,
    usage_percent: float,
    tier: str,
    threshold: int,
    refresh_delta: int | None,
    subagent_calls: int,
) -> None:
    HANDOFF_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    marker_path(conversation_id).write_text(
        json.dumps(
            {
                "last_write_percent": usage_percent,
                "tier": tier,
                "threshold": threshold,
                "refresh_delta": refresh_delta,
                "subagent_calls": subagent_calls,
                "written_at": now,
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def _record_path(analysis: TranscriptAnalysis, value: str) -> None:
    cleaned = value.strip()
    if not cleaned or cleaned.startswith("http"):
        return
    if cleaned not in analysis.unique_paths:
        analysis.unique_paths.add(cleaned)
        if len(analysis.sample_paths) < MAX_PATHS_IN_HINT:
            analysis.sample_paths.append(cleaned)


def _collect_paths_from_obj(analysis: TranscriptAnalysis, obj: object) -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in PATH_KEYS and isinstance(value, str):
                _record_path(analysis, value)
            else:
                _collect_paths_from_obj(analysis, value)
    elif isinstance(obj, list):
        for item in obj:
            _collect_paths_from_obj(analysis, item)


def analyze_transcript(transcript_path: str | None) -> TranscriptAnalysis:
    analysis = TranscriptAnalysis()
    if not transcript_path:
        return analysis
    path = Path(transcript_path)
    if not path.is_file():
        return analysis

    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return analysis

    for line in lines:
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
            if not isinstance(part, dict):
                continue
            part_type = part.get("type")
            if part_type == "text":
                text = (part.get("text") or "").strip()
                if text:
                    text_chunks.append(text)
            elif part_type == "tool_use":
                analysis.tool_calls += 1
                tool_name = str(part.get("name") or "")
                if tool_name == "Task":
                    analysis.subagent_calls += 1
                if tool_name == "Shell":
                    analysis.shell_calls += 1
                _collect_paths_from_obj(analysis, part.get("input") or {})

        combined = "\n".join(text_chunks).strip()
        if role == "user" and combined:
            analysis.user_turns += 1
            analysis.last_user = combined[:1200]
        elif role == "assistant" and combined:
            analysis.last_assistant = combined[:1200]

    return analysis


def classify_complexity(analysis: TranscriptAnalysis) -> str:
    user_blob = analysis.last_user.lower()
    keyword_boost = any(keyword in user_blob for keyword in MULTI_FILE_KEYWORDS)

    if analysis.subagent_calls >= 1 or analysis.tool_calls >= 25:
        return "critical"
    if analysis.tool_calls >= 15 or len(analysis.unique_paths) >= 5 or keyword_boost:
        return "high"
    if (
        analysis.tool_calls <= 5
        and len(analysis.unique_paths) <= 2
        and analysis.subagent_calls == 0
        and analysis.user_turns <= 3
    ):
        return "low"
    return "medium"


def tier_index(tier: str) -> int:
    try:
        return TIER_ORDER.index(tier)
    except ValueError:
        return TIER_ORDER.index("medium")


def should_write_handoff(
    conversation_id: str,
    usage_percent: float,
    tier: str,
    *,
    event: str,
    analysis: TranscriptAnalysis,
) -> bool:
    if event == "preCompact":
        return True

    threshold = int(TIER_CONFIG[tier]["threshold"])
    if usage_percent < threshold:
        return False

    marker = load_marker(conversation_id)
    if marker is None:
        return True

    if tier_index(tier) > tier_index(str(marker.get("tier") or "medium")):
        return True

    if tier == "critical" and analysis.subagent_calls > int(marker.get("subagent_calls") or 0):
        return True

    refresh_delta = TIER_CONFIG[tier].get("refresh_delta")
    if isinstance(refresh_delta, int):
        last_write = marker.get("last_write_percent")
        if isinstance(last_write, (int, float)) and usage_percent >= float(last_write) + refresh_delta:
            return True

    return False


def paths_hint(analysis: TranscriptAnalysis, tier: str) -> str:
    max_paths = 5 if tier == "low" else 10 if tier == "medium" else MAX_PATHS_IN_HINT
    if not analysis.sample_paths:
        return "_Enrich with paths only (no contents)._"
    shown = analysis.sample_paths[:max_paths]
    lines = [f"- `{path}`" for path in shown]
    extra = len(analysis.unique_paths) - len(shown)
    if extra > 0:
        lines.append(f"- _…and {extra} more — add key paths only._")
    return "\n".join(lines)


def write_handoff(
    payload: dict,
    usage_percent: float,
    tier: str,
    analysis: TranscriptAnalysis,
) -> None:
    HANDOFF_DIR.mkdir(parents=True, exist_ok=True)
    BRIEF_FILE.parent.mkdir(parents=True, exist_ok=True)

    conversation_id = conversation_id_from(payload)
    threshold = int(TIER_CONFIG[tier]["threshold"])
    refresh_delta = TIER_CONFIG[tier].get("refresh_delta")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    model = str(payload.get("model") or "unknown")
    enrichment = ENRICHMENT_HINTS[tier]
    state_path = str(STATE_FILE)

    state_lines = [
        "# Session Handoff",
        f"**Created:** {now}",
        f"**Complexity tier:** {tier}",
        f"**Context usage:** {usage_percent:.1f}% (tier threshold {threshold}%)",
        f"**Model:** {model}",
        f"**Conversation:** {conversation_id}",
        f"**Session signals:** {analysis.tool_calls} tools, "
        f"{len(analysis.unique_paths)} paths, {analysis.subagent_calls} subagents",
        "",
        "## Enrichment budget",
        enrichment,
        "",
        "## Active task",
        "_One sentence — agent must enrich._",
        "",
        "## Progress",
        "_Done vs still open — agent must enrich._",
        "",
        "## Files touched",
        paths_hint(analysis, tier),
        "",
        "## Next step",
        "_Single highest-priority action — agent must enrich._",
        "",
        "## Blockers",
        "_Omit section if none._",
        "",
        "## Last user request",
        analysis.last_user or "_Unavailable._",
        "",
        "## Last agent summary",
        analysis.last_assistant or "_Unavailable._",
        "",
        "## Resume instructions",
        "1. Read this file and `.session-logs/LAST_SESSION_BRIEF.md`.",
        "2. Do not restart from scratch — continue the active task.",
        "3. Keep both files ≤400 tokens total; update if scope changes materially.",
        "",
    ]
    STATE_FILE.write_text("\n".join(state_lines), encoding="utf-8")

    brief_lines = [
        "# Last Session Brief",
        f"**Date:** {now.split(' ')[0]}  **Agent:** {AGENT_LABEL}  **Tier:** {tier}",
        f"**Context usage at handoff:** {usage_percent:.1f}% (threshold {threshold}%)",
        "**Active task:** _agent must enrich — one sentence_",
        "**Progress:** _done vs open — agent must enrich_",
        f"**Files changed:** see Files touched in `{state_path}`",
        "**Key decisions:** _agent must enrich if any_",
        "**Next priority:** _single next action — agent must enrich_",
        "**Blockers:** _omit if none_",
        "",
        f"_Token budget: {enrichment}_",
        "",
    ]
    BRIEF_FILE.write_text("\n".join(brief_lines), encoding="utf-8")

    save_marker(
        conversation_id,
        usage_percent=usage_percent,
        tier=tier,
        threshold=threshold,
        refresh_delta=refresh_delta if isinstance(refresh_delta, int) else None,
        subagent_calls=analysis.subagent_calls,
    )


def enrichment_message(tier: str, usage_percent: float, threshold: int, *, refreshed: bool) -> str:
    action = "refreshed" if refreshed else "saved"
    return (
        f"Context ~{usage_percent:.0f}% ({tier} tier, threshold {threshold}%). "
        f"Handoff {action} at {STATE_FILE}. Enrich both handoff files now: "
        f"{ENRICHMENT_HINTS[tier]} "
        "Required fields: active task, progress, files touched (paths only), next step, blockers if any. "
        "No secrets or code dumps."
    )


def emit_empty() -> None:
    print("{}")


def emit_precompact_notice(message: str, *, vscode: bool) -> None:
    if vscode:
        print(json.dumps({"systemMessage": message}))
        return
    print(json.dumps({"user_message": message}))


def emit_enrichment(message: str, *, vscode: bool, hook_event_name: str) -> None:
    if vscode:
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": hook_event_name,
                        "additionalContext": message,
                    }
                }
            )
        )
        return
    print(json.dumps({"additional_context": message}))


def main() -> int:
    payload = load_input()
    raw_event = str(payload.get("hook_event_name") or payload.get("hookEventName") or "")
    event = normalize_event(raw_event)
    vscode = is_vscode_platform(raw_event)
    usage_percent = compute_usage_percent(payload)
    if usage_percent is None:
        emit_empty()
        return 0

    transcript_path = payload.get("transcript_path")
    analysis = analyze_transcript(transcript_path if isinstance(transcript_path, str) else None)
    tier = classify_complexity(analysis)
    threshold = int(TIER_CONFIG[tier]["threshold"])
    conversation_id = conversation_id_from(payload)

    if not should_write_handoff(
        conversation_id,
        usage_percent,
        tier,
        event=event,
        analysis=analysis,
    ):
        emit_empty()
        return 0

    marker = load_marker(conversation_id)
    refreshed = marker is not None and event != "preCompact"
    write_handoff(payload, usage_percent, tier, analysis)

    compact_message = (
        f"Context handoff saved ({tier} tier, {usage_percent:.0f}% used, "
        f"threshold {threshold}%). Continue from {STATE_FILE} in a new chat if needed."
    )

    if event == "preCompact":
        emit_precompact_notice(compact_message, vscode=vscode)
        return 0

    if event in ("afterAgentResponse", "stop", "postToolUse", "subagentStop"):
        hook_event_name = raw_event or "PostToolUse"
        emit_enrichment(
            enrichment_message(tier, usage_percent, threshold, refreshed=refreshed),
            vscode=vscode,
            hook_event_name=hook_event_name,
        )
        return 0

    emit_empty()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
