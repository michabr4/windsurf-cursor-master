#!/usr/bin/env python3
"""Comms Bridge MCP server — file-based task handoff for Windsurf ↔ Cursor."""

from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger("comms-bridge")
logging.basicConfig(level=logging.INFO, stream=os.sys.stderr)

PRIORITIES = ("critical", "high", "medium", "low")
PRIORITY_RANK = {name: index for index, name in enumerate(PRIORITIES)}

RESULT_STATUSES = ("success", "partial", "failed", "blocked")

TASK_ID_PATTERN = re.compile(r"^TASK-(\d{4})-(\d{4})-(\d{3})$")

TASK_REQUIRED_FIELDS = frozenset(
    {
        "id",
        "from",
        "to",
        "priority",
        "type",
        "phase",
        "title",
        "spec",
        "depends_on",
        "files_to_read",
        "created_at",
        "status",
    }
)

RESULT_REQUIRED_FIELDS = frozenset(
    {
        "id",
        "from",
        "to",
        "type",
        "status",
        "summary",
        "details",
        "files_changed",
        "issues",
        "completed_at",
    }
)

mcp = FastMCP("comms-bridge")


def _comms_root() -> Path:
    raw = os.environ.get("COMMS_DIR", "").strip()
    if not raw:
        raise RuntimeError(
            "COMMS_DIR is not set. Point it at your workspace .comms folder "
            "(see mcp-servers/comms-bridge-mcp/.env.example)."
        )
    return Path(raw).expanduser().resolve()


def _ensure_layout(root: Path) -> None:
    for name in ("inbox", "outbox", "active", "completed"):
        (root / name).mkdir(parents=True, exist_ok=True)


def _iso_now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    data = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    tmp.write_text(data, encoding="utf-8")
    tmp.replace(path)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path.name}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path.name}")
    return data


def _validate_task(data: dict[str, Any], *, expected_id: str | None = None) -> None:
    missing = TASK_REQUIRED_FIELDS - data.keys()
    if missing:
        raise ValueError(f"Task missing fields: {sorted(missing)}")
    if data["priority"] not in PRIORITIES:
        raise ValueError(f"Invalid priority: {data['priority']}")
    if expected_id and data.get("id") != expected_id:
        raise ValueError(f"Task id mismatch: file has {data.get('id')}, expected {expected_id}")


def _validate_result(data: dict[str, Any], *, expected_id: str | None = None) -> None:
    missing = RESULT_REQUIRED_FIELDS - data.keys()
    if missing:
        raise ValueError(f"Result missing fields: {sorted(missing)}")
    if data["status"] not in RESULT_STATUSES:
        raise ValueError(f"Invalid result status: {data['status']}")
    if expected_id and data.get("id") != expected_id:
        raise ValueError(f"Result id mismatch: file has {data.get('id')}, expected {expected_id}")


def _task_dirs(root: Path) -> tuple[Path, Path, Path]:
    return root / "inbox", root / "active", root / "completed"


def _list_task_files(*dirs: Path) -> list[Path]:
    files: list[Path] = []
    for directory in dirs:
        if directory.is_dir():
            files.extend(sorted(directory.glob("TASK-*.json")))
    return files


def _next_task_id(root: Path) -> str:
    now = datetime.now()
    prefix = f"TASK-{now.strftime('%Y')}-{now.strftime('%m%d')}"
    max_seq = 0
    inbox, active, completed = _task_dirs(root)
    for path in _list_task_files(inbox, active, completed):
        if not path.stem.startswith(f"{prefix}-"):
            continue
        match = TASK_ID_PATTERN.match(path.stem)
        if match:
            max_seq = max(max_seq, int(match.group(3)))
    return f"{prefix}-{max_seq + 1:03d}"


def _find_task_path(root: Path, task_id: str) -> Path | None:
    inbox, active, completed = _task_dirs(root)
    for directory in (inbox, active, completed):
        candidate = directory / f"{task_id}.json"
        if candidate.is_file():
            return candidate
    return None


@mcp.tool()
def send_task(
    title: str,
    spec: str,
    priority: str,
    phase: str,
    depends_on: str | None = None,
    files_to_read: list[str] | None = None,
) -> str:
    """Create a new task in the comms inbox (Windsurf → Cursor).

    Auto-generates a TASK-{YYYY}-{MMDD}-{NNN} id, sets status pending, and writes
    to inbox/. Priority must be critical, high, medium, or low.
    """
    if priority not in PRIORITIES:
        raise ValueError(f"priority must be one of: {', '.join(PRIORITIES)}")

    root = _comms_root()
    _ensure_layout(root)
    task_id = _next_task_id(root)
    payload: dict[str, Any] = {
        "id": task_id,
        "from": "windsurf",
        "to": "cursor",
        "priority": priority,
        "type": "instruction",
        "phase": phase,
        "title": title,
        "spec": spec,
        "depends_on": depends_on,
        "files_to_read": files_to_read or [],
        "created_at": _iso_now(),
        "status": "pending",
    }
    _validate_task(payload, expected_id=task_id)
    path = root / "inbox" / f"{task_id}.json"
    _atomic_write_json(path, payload)
    logger.info("send_task %s -> %s", task_id, path)
    return task_id


@mcp.tool()
def check_inbox() -> list[dict[str, Any]]:
    """List pending tasks in inbox/, sorted by priority (critical first)."""
    root = _comms_root()
    _ensure_layout(root)
    inbox = root / "inbox"
    summaries: list[dict[str, Any]] = []
    for path in sorted(inbox.glob("TASK-*.json")):
        task = _read_json(path)
        _validate_task(task)
        summaries.append(
            {
                "id": task["id"],
                "priority": task["priority"],
                "title": task["title"],
                "phase": task["phase"],
                "created_at": task["created_at"],
            }
        )
    summaries.sort(key=lambda item: PRIORITY_RANK.get(item["priority"], 99))
    logger.info("check_inbox count=%d", len(summaries))
    return summaries


@mcp.tool()
def claim_task(task_id: str) -> dict[str, Any]:
    """Move a task from inbox/ to active/ and set status to in_progress."""
    root = _comms_root()
    _ensure_layout(root)
    inbox_path = root / "inbox" / f"{task_id}.json"
    if not inbox_path.is_file():
        raise FileNotFoundError(f"Task {task_id} not found in inbox")

    task = _read_json(inbox_path)
    _validate_task(task, expected_id=task_id)
    task["status"] = "in_progress"
    active_path = root / "active" / f"{task_id}.json"
    _atomic_write_json(active_path, task)
    inbox_path.unlink()
    logger.info("claim_task %s", task_id)
    return task


@mcp.tool()
def submit_result(
    task_id: str,
    status: str,
    summary: str,
    details: str,
    files_changed: list[str] | None = None,
    issues: list[str] | None = None,
) -> str:
    """Write a result to outbox/ and archive the task from active/ to completed/."""
    if status not in RESULT_STATUSES:
        raise ValueError(f"status must be one of: {', '.join(RESULT_STATUSES)}")

    root = _comms_root()
    _ensure_layout(root)
    active_path = root / "active" / f"{task_id}.json"
    if not active_path.is_file():
        raise FileNotFoundError(f"Task {task_id} not found in active")

    result: dict[str, Any] = {
        "id": task_id,
        "from": "cursor",
        "to": "windsurf",
        "type": "result",
        "status": status,
        "summary": summary,
        "details": details,
        "files_changed": files_changed or [],
        "issues": issues or [],
        "completed_at": _iso_now(),
        "next_recommended": None,
    }
    _validate_result(result, expected_id=task_id)

    result_path = root / "outbox" / f"RESULT-{task_id}.json"
    _atomic_write_json(result_path, result)

    completed_path = root / "completed" / f"{task_id}.json"
    _atomic_write_json(completed_path, _read_json(active_path))
    active_path.unlink()

    message = f"Result submitted for {task_id} (status={status})"
    logger.info("submit_result %s", task_id)
    return message


@mcp.tool()
def check_outbox() -> list[dict[str, Any]]:
    """List result files in outbox/ awaiting Windsurf review."""
    root = _comms_root()
    _ensure_layout(root)
    outbox = root / "outbox"
    summaries: list[dict[str, Any]] = []
    for path in sorted(outbox.glob("RESULT-*.json")):
        result = _read_json(path)
        _validate_result(result)
        summaries.append(
            {
                "id": result["id"],
                "status": result["status"],
                "summary": result["summary"],
                "completed_at": result["completed_at"],
            }
        )
    logger.info("check_outbox count=%d", len(summaries))
    return summaries


@mcp.tool()
def get_task(task_id: str) -> dict[str, Any]:
    """Return the full task JSON from inbox/, active/, or completed/."""
    root = _comms_root()
    _ensure_layout(root)
    path = _find_task_path(root, task_id)
    if path is None:
        raise FileNotFoundError(f"Task {task_id} not found")
    task = _read_json(path)
    _validate_task(task, expected_id=task_id)
    return task


@mcp.tool()
def archive_completed() -> str:
    """Move all RESULT-*.json files from outbox/ to completed/."""
    root = _comms_root()
    _ensure_layout(root)
    outbox = root / "outbox"
    completed = root / "completed"
    count = 0
    for path in sorted(outbox.glob("RESULT-*.json")):
        result = _read_json(path)
        _validate_result(result)
        dest = completed / path.name
        _atomic_write_json(dest, result)
        path.unlink()
        count += 1
    logger.info("archive_completed count=%d", count)
    return f"Archived {count} result(s) from outbox to completed"


@mcp.tool()
def get_pipeline_status() -> dict[str, int]:
    """Return counts of JSON task/result files in each comms directory."""
    root = _comms_root()
    _ensure_layout(root)
    status = {
        "inbox": len(list((root / "inbox").glob("*.json"))),
        "active": len(list((root / "active").glob("*.json"))),
        "outbox": len(list((root / "outbox").glob("*.json"))),
        "completed": len(list((root / "completed").glob("*.json"))),
    }
    logger.info("get_pipeline_status %s", status)
    return status


def main() -> None:
    _ensure_layout(_comms_root())
    mcp.run()


if __name__ == "__main__":
    main()
