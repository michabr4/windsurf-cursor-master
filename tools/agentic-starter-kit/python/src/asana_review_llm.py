"""Optional local Ollama pass to polish Asana review comments (no secrets in prompts)."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Tuple

import requests
from dotenv import load_dotenv


load_dotenv()

_MAX_TASK_CHARS = 4000
_MAX_REPLY_CHARS = 8000


def use_llm_for_asana_review() -> bool:
    v = os.getenv("ASANA_REVIEW_USE_LLM", "").strip().lower()
    return v in ("1", "true", "yes", "on")


def polish_comment_with_ollama(
    task: Dict[str, Any],
    findings: List[Dict[str, Any]],
    draft_comment: str,
) -> Tuple[str, str | None]:
    """Return (comment_text, error_message). On failure, returns draft unchanged."""
    base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    if not base.endswith("/v1"):
        base = f"{base}/v1"
    url = f"{base}/chat/completions"
    model = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
    api_key = os.getenv("OLLAMA_API_KEY", "").strip()

    name = task.get("name") if isinstance(task.get("name"), str) else "Task"
    notes = task.get("notes") if isinstance(task.get("notes"), str) else ""
    if len(notes) > _MAX_TASK_CHARS:
        notes = notes[:_MAX_TASK_CHARS] + "…"

    issues = [f.get("message", "") for f in findings if not f.get("ok")]
    issue_block = "\n".join(f"- {m}" for m in issues if m) or "(none)"

    user_prompt = (
        "Rewrite the draft Asana task comment below. Keep every factual finding; "
        "use a friendly professional tone; use plain text only (no markdown). "
        "Stay under 3500 characters. Do not invent requirements or claim work was done.\n\n"
        f"Task title: {name}\n"
        f"Open issues from automated checks:\n{issue_block}\n\n"
        f"Draft comment:\n{draft_comment}"
    )

    headers: Dict[str, str] = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You help teammates improve Asana tasks. Output only the final comment text.",
            },
            {"role": "user", "content": user_prompt},
        ],
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=90)
        resp.raise_for_status()
        data = resp.json()
        text = _extract_content(data).strip()
        if not text:
            return draft_comment, "Ollama returned an empty reply; using rule-based draft."
        if len(text) > _MAX_REPLY_CHARS:
            text = text[:_MAX_REPLY_CHARS]
        return text, None
    except requests.RequestException as exc:
        return draft_comment, f"Ollama request failed: {exc}"


def _extract_content(response_json: Dict[str, Any]) -> str:
    choices = response_json.get("choices")
    if not isinstance(choices, list) or not choices:
        return ""
    first = choices[0]
    if not isinstance(first, dict):
        return ""
    message = first.get("message")
    if isinstance(message, dict) and isinstance(message.get("content"), str):
        return message["content"]
    return ""
