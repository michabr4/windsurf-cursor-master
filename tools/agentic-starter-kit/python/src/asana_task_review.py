"""Deterministic checks and report builders for Asana task review."""

from __future__ import annotations

import json
import re
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


_HTML_TAG = re.compile(r"<[^>]+>")
_VAGUE_TITLES = frozenset(
    {
        "task",
        "todo",
        "to do",
        "to-do",
        "untitled",
        "new task",
        "follow up",
        "follow-up",
        "tbd",
    }
)
_AC_KEYWORDS = re.compile(
    r"\b(acceptance criteria|definition of done|done when|success criteria|ac:)\b",
    re.IGNORECASE,
)


def strip_html_notes(html: str | None) -> str:
    if not html or not isinstance(html, str):
        return ""
    text = _HTML_TAG.sub(" ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def plain_notes(task: Dict[str, Any]) -> str:
    notes = task.get("notes")
    if isinstance(notes, str) and notes.strip():
        return notes.strip()
    return strip_html_notes(task.get("html_notes") if isinstance(task.get("html_notes"), str) else None)


def run_checks(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return finding dicts: id, ok, level (info|warn|error), message."""
    findings: List[Dict[str, Any]] = []
    name = (task.get("name") or "").strip() if isinstance(task.get("name"), str) else ""
    if len(name) < 3:
        findings.append(
            {
                "id": "title_nonempty",
                "ok": False,
                "level": "error",
                "message": "Task name is missing or very short (under 3 characters).",
            }
        )
    else:
        findings.append(
            {
                "id": "title_nonempty",
                "ok": True,
                "level": "info",
                "message": "Task name looks present.",
            }
        )

    desc = plain_notes(task)
    if not desc:
        findings.append(
            {
                "id": "has_description",
                "ok": False,
                "level": "warn",
                "message": "No description in notes or html_notes — add context or acceptance criteria.",
            }
        )
    else:
        findings.append(
            {
                "id": "has_description",
                "ok": True,
                "level": "info",
                "message": "Description or notes field has content.",
            }
        )
        if len(desc) < 40:
            findings.append(
                {
                    "id": "description_length",
                    "ok": False,
                    "level": "warn",
                    "message": "Description is very short — add acceptance criteria or context.",
                }
            )

    lowered = name.lower()
    vague = lowered in _VAGUE_TITLES or (len(name) < 12 and name.islower())
    if vague:
        findings.append(
            {
                "id": "title_specific",
                "ok": False,
                "level": "warn",
                "message": "Title looks generic — use a specific outcome (who/what/when).",
            }
        )

    assignee = task.get("assignee")
    has_assignee = isinstance(assignee, dict) and bool(assignee.get("gid") or assignee.get("name"))
    findings.append(
        {
            "id": "has_assignee",
            "ok": has_assignee,
            "level": "warn" if not has_assignee else "info",
            "message": "Assign someone so ownership is clear."
            if not has_assignee
            else "Assignee is set.",
        }
    )

    completed = bool(task.get("completed"))
    due_on = task.get("due_on")
    due_at = task.get("due_at")
    has_due = bool(
        (isinstance(due_on, str) and due_on.strip())
        or (isinstance(due_at, str) and due_at.strip())
    )
    if not completed and not has_due:
        findings.append(
            {
                "id": "due_or_completed",
                "ok": False,
                "level": "warn",
                "message": "Open task has no due date — consider adding one.",
            }
        )
    else:
        findings.append(
            {
                "id": "due_or_completed",
                "ok": True,
                "level": "info",
                "message": "Task is completed or has a due date.",
            }
        )

    if not completed and has_due and isinstance(due_on, str) and due_on.strip():
        try:
            due_day = date.fromisoformat(due_on.strip()[:10])
            if due_day < date.today():
                findings.append(
                    {
                        "id": "overdue",
                        "ok": False,
                        "level": "error",
                        "message": f"Due date {due_on} is in the past — update the date or mark complete.",
                    }
                )
        except ValueError:
            pass

    projects = task.get("projects")
    if not isinstance(projects, list) or len(projects) == 0:
        findings.append(
            {
                "id": "in_project",
                "ok": False,
                "level": "warn",
                "message": "Task is not in any project — add it to the right project or section.",
            }
        )

    if not completed and desc and not _AC_KEYWORDS.search(desc):
        findings.append(
            {
                "id": "acceptance_criteria",
                "ok": False,
                "level": "warn",
                "message": "No acceptance criteria found — mention how you will know the task is done.",
            }
        )

    num_sub = task.get("num_subtasks")
    if isinstance(num_sub, int) and num_sub > 0 and not completed:
        findings.append(
            {
                "id": "subtasks_present",
                "ok": True,
                "level": "info",
                "message": f"Task has {num_sub} subtask(s) — confirm parent task reflects overall status.",
            }
        )

    custom_fields = task.get("custom_fields")
    if isinstance(custom_fields, list):
        for cf in custom_fields:
            if not isinstance(cf, dict):
                continue
            cf_name = cf.get("name") if isinstance(cf.get("name"), str) else "Custom field"
            cf_type = cf.get("type") if isinstance(cf.get("type"), str) else ""
            empty = _custom_field_empty(cf, cf_type)
            if empty:
                findings.append(
                    {
                        "id": f"custom_field:{cf.get('gid', cf_name)}",
                        "ok": False,
                        "level": "warn",
                        "message": f"Custom field “{cf_name}” appears empty.",
                    }
                )

    return findings


def _custom_field_empty(cf: Dict[str, Any], cf_type: str) -> bool:
    if cf_type == "text":
        tv = cf.get("text_value")
        return not (isinstance(tv, str) and tv.strip())
    if cf_type == "number":
        return cf.get("number_value") is None
    if cf_type == "enum":
        ev = cf.get("enum_value")
        return ev is None or (isinstance(ev, dict) and not ev.get("name"))
    return False


def build_suggested_comment(task: Dict[str, Any], findings: List[Dict[str, Any]]) -> str:
    name = task.get("name") if isinstance(task.get("name"), str) else "Task"
    lines = [
        "Automated task review (local starter)",
        f"Task: {name}",
        "",
        "Summary:",
    ]
    for f in findings:
        icon = "OK" if f.get("ok") else ("WARN" if f.get("level") == "warn" else "ISSUE")
        lines.append(f"- [{icon}] {f.get('message', '')}")
    link = task.get("permalink_url")
    if isinstance(link, str) and link:
        lines.extend(["", f"Link: {link}"])
    return "\n".join(lines)


def build_markdown_report(
    task: Dict[str, Any],
    findings: List[Dict[str, Any]],
    suggested_comment: str,
    written_files: Dict[str, str],
    *,
    draft_comment: Optional[str] = None,
    llm_applied: bool = False,
    llm_error: Optional[str] = None,
) -> str:
    name = task.get("name") if isinstance(task.get("name"), str) else "(unnamed)"
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    parts = [
        f"# Asana task review: {name}",
        "",
        f"- Generated: {ts}",
        f"- Permalink: {task.get('permalink_url') or 'n/a'}",
        f"- LLM polish: {'yes' if llm_applied else 'no'}",
        "",
        "## Checks",
        "",
    ]
    if llm_error:
        parts.append(f"- LLM note: {llm_error}")
        parts.append("")
    for f in findings:
        status = "pass" if f.get("ok") else "fail"
        parts.append(f"- **{status}** ({f.get('id')}): {f.get('message')}")
    parts.extend(
        [
            "",
            "## Suggested Asana comment (preview)",
            "",
            "```text",
            suggested_comment,
            "```",
            "",
        ]
    )
    if draft_comment and draft_comment != suggested_comment:
        parts.extend(
            [
                "## Rule-based draft (before LLM)",
                "",
                "```text",
                draft_comment,
                "```",
                "",
            ]
        )
    parts.extend(["## Output files", ""])
    for k, v in written_files.items():
        parts.append(f"- {k}: `{v}`")
    return "\n".join(parts) + "\n"


def write_reports(
    out_root: Path,
    task_gid: str,
    task: Dict[str, Any],
    findings: List[Dict[str, Any]],
    suggested_comment: str,
    *,
    draft_comment: Optional[str] = None,
    llm_applied: bool = False,
    llm_error: Optional[str] = None,
) -> Tuple[str, str]:
    out_root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = out_root / f"{task_gid}_{stamp}"
    md_path = base.with_suffix(".md")
    json_path = base.with_suffix(".json")

    written = {"markdown": str(md_path), "json": str(json_path)}

    summary = {
        "task_gid": task_gid,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "permalink_url": task.get("permalink_url"),
        "name": task.get("name"),
        "completed": task.get("completed"),
        "findings": findings,
        "suggested_comment": suggested_comment,
        "draft_comment": draft_comment or suggested_comment,
        "llm_applied": llm_applied,
        "llm_error": llm_error,
        "files": written,
    }
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    md_body = build_markdown_report(
        task,
        findings,
        suggested_comment,
        written,
        draft_comment=draft_comment,
        llm_applied=llm_applied,
        llm_error=llm_error,
    )
    md_path.write_text(md_body, encoding="utf-8")

    return str(md_path), str(json_path)
