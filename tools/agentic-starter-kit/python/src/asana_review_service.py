"""Orchestrates fetch, checks, optional LLM polish, and report writing."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.asana_client import AsanaClient
from src.asana_review_llm import polish_comment_with_ollama, use_llm_for_asana_review
from src.asana_task_review import build_suggested_comment, run_checks, write_reports


@dataclass
class ReviewOutcome:
    task_gid: str
    task: Dict[str, Any]
    findings: List[Dict[str, Any]]
    suggested_comment: str
    draft_comment: str
    llm_applied: bool
    llm_error: Optional[str]
    markdown_path: str
    json_path: str


def review_task(
    task_gid: str,
    *,
    asana: AsanaClient | None = None,
    out_dir: Path,
    use_llm: bool | None = None,
) -> ReviewOutcome:
    client = asana or AsanaClient()
    task = client.get_task(task_gid)
    findings = run_checks(task)
    draft = build_suggested_comment(task, findings)

    want_llm = use_llm_for_asana_review() if use_llm is None else use_llm
    llm_applied = False
    llm_error: Optional[str] = None
    final_comment = draft

    if want_llm:
        final_comment, llm_error = polish_comment_with_ollama(task, findings, draft)
        llm_applied = llm_error is None

    md_path, json_path = write_reports(
        out_dir,
        task_gid,
        task,
        findings,
        final_comment,
        draft_comment=draft,
        llm_applied=llm_applied,
        llm_error=llm_error,
    )

    return ReviewOutcome(
        task_gid=task_gid,
        task=task,
        findings=findings,
        suggested_comment=final_comment,
        draft_comment=draft,
        llm_applied=llm_applied and llm_error is None,
        llm_error=llm_error,
        markdown_path=md_path,
        json_path=json_path,
    )


def outcome_to_api_dict(outcome: ReviewOutcome) -> Dict[str, Any]:
    return {
        "ok": True,
        "task_gid": outcome.task_gid,
        "markdown_path": outcome.markdown_path,
        "json_path": outcome.json_path,
        "findings": outcome.findings,
        "suggested_comment": outcome.suggested_comment,
        "draft_comment": outcome.draft_comment,
        "llm_applied": outcome.llm_applied,
        "llm_error": outcome.llm_error,
        "markdown_body": Path(outcome.markdown_path).read_text(encoding="utf-8"),
    }
