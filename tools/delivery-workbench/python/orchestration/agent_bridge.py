"""Thin adapters to repo agents — graceful degradation when credentials missing."""

from __future__ import annotations

import importlib.util
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .paths import AGENT_COMMUNICATION, AGENT_FLERKEN, AGENT_STATUS_REPORT, WORKBENCH_ROOT


@dataclass
class StepResult:
    ok: bool
    markdown: str
    meta: dict[str, Any]


def _ensure_path(path: Path) -> None:
    s = str(path)
    if s not in sys.path:
        sys.path.insert(0, s)


def _load_module(name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {file_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def flerken_digest_markdown(*, demo: bool, dry_run: bool) -> StepResult:
    """Email triage via Flerken DigestBuilder (demo uses mock inbox + LLM when configured)."""
    if dry_run:
        return _flerken_dry_run_placeholder()

    try:
        _ensure_path(AGENT_FLERKEN)
        from src.digest_builder import DigestBuilder  # type: ignore[import-not-found]

        builder = DigestBuilder(demo=demo)
        result = builder.build()
        data = result.get("data") or {}
        if not data:
            return StepResult(
                ok=True,
                markdown="_No emails in lookback window._\n",
                meta={"mode": "demo" if demo else "live"},
            )
        return StepResult(
            ok=True,
            markdown=_format_flerken_data(data),
            meta={"mode": "demo" if demo else "live", "counts": data.get("counts", {})},
        )
    except Exception as exc:  # noqa: BLE001 — surface degradation to briefing
        return StepResult(
            ok=False,
            markdown=f"_Email digest unavailable: {exc}_\n",
            meta={"error": str(exc)},
        )


def _flerken_dry_run_placeholder() -> StepResult:
    try:
        _ensure_path(AGENT_FLERKEN)
        from src.mock_emails import MOCK_EMAILS  # type: ignore[import-not-found]

        lines = [
            "## Email digest (dry-run)",
            "",
            f"Simulated scan of **{len(MOCK_EMAILS)}** messages (Flerken mock data).",
            "Run without `--dry-run` and configure Flerken `.env` for live Graph + LLM triage.",
            "",
        ]
        for item in MOCK_EMAILS[:8]:
            email = item if hasattr(item, "subject") else item.get("email", item)
            subject = getattr(email, "subject", None) or email.get("subject", "(no subject)")
            sender = getattr(email, "from_name", None) or email.get("from_name", "unknown")
            lines.append(f"- **{subject}** — {sender}")
        return StepResult(ok=True, markdown="\n".join(lines) + "\n", meta={"mode": "dry-run"})
    except Exception as exc:  # noqa: BLE001
        return StepResult(
            ok=True,
            markdown="## Email digest (dry-run)\n\n_Placeholder — connect Flerken for triage._\n",
            meta={"error": str(exc)},
        )


def _format_flerken_data(data: dict[str, Any]) -> str:
    counts = data.get("counts", {})
    lines = [
        "## Email digest",
        "",
        data.get("executive_summary", ""),
        "",
        "| Category | Count |",
        "|----------|------:|",
        f"| Urgent | {counts.get('urgent', 0)} |",
        f"| Action required | {counts.get('action_required', 0)} |",
        f"| FYI | {counts.get('fyi', 0)} |",
        f"| Low priority | {counts.get('low_priority', 0)} |",
        "",
    ]
    triaged = data.get("triaged") or []
    urgent = [t for t in triaged if t.get("triage", {}).get("category") == "urgent"]
    if urgent:
        lines.append("### Urgent items")
        for item in urgent[:5]:
            subj = item.get("email", {}).get("subject", "(no subject)")
            lines.append(f"- {subj}")
        lines.append("")
    return "\n".join(lines)


def communication_scan_markdown(*, dry_run: bool, days: int = 7) -> StepResult:
    """Webex/email scan via communication-agent (rule-based when --no-llm)."""
    if dry_run:
        return StepResult(
            ok=True,
            markdown=(
                "## Communication scan (dry-run)\n\n"
                "_Skipped live Webex/email APIs. Set communication-agent `.env` and run "
                "`communication-scan` workflow without `--dry-run`._\n\n"
                "**TODO (TASK-015):** Wire Webex DM/mention fetch into morning briefing when "
                "`WEBEX_ACCESS_TOKEN` is configured.\n"
            ),
            meta={"mode": "dry-run", "webex": "todo"},
        )

    try:
        _ensure_path(AGENT_COMMUNICATION)
        agent_mod = _load_module("comm_agent", AGENT_COMMUNICATION / "agent.py")
        fmt_mod = _load_module("comm_fmt", AGENT_COMMUNICATION / "output_formatter.py")
        CommunicationAgent = agent_mod.CommunicationAgent
        OutputFormatter = fmt_mod.OutputFormatter

        agent = CommunicationAgent()
        report = agent.run(days_back=days, sources=["webex_chat"], use_llm=False)
        md_path = Path(AGENT_COMMUNICATION) / "output" / "_workbench_comm_scan.md"
        md_path.parent.mkdir(parents=True, exist_ok=True)
        OutputFormatter(report).to_markdown(str(md_path))
        body = md_path.read_text(encoding="utf-8")
        return StepResult(ok=True, markdown="## Communication scan\n\n" + body, meta={"days": days})
    except Exception as exc:  # noqa: BLE001
        return StepResult(
            ok=False,
            markdown=(
                "## Communication scan\n\n"
                f"_Unavailable: {exc}_\n\n"
                "Configure `agents/communication-agent/.env` (Webex token) to enable.\n"
            ),
            meta={"error": str(exc)},
        )


def status_report_markdown(*, dry_run: bool, role: str = "SDM") -> StepResult:
    """Weekly status narrative via status-report-agent demo generator."""
    if dry_run:
        return StepResult(
            ok=True,
            markdown=(
                "## Status snapshot (dry-run)\n\n"
                "_Weekly status report skipped in dry-run. Use `status-report` workflow for "
                "Salesforce + ServiceNow-backed reports._\n"
            ),
            meta={"mode": "dry-run"},
        )

    try:
        _ensure_path(AGENT_STATUS_REPORT)
        demo_mod = _load_module("sr_demo", AGENT_STATUS_REPORT / "demo.py")
        gen_mod = _load_module("sr_gen", AGENT_STATUS_REPORT / "report_generator.py")
        cfg_mod = _load_module("sr_cfg", AGENT_STATUS_REPORT / "config.py")
        report = demo_mod.generate_demo_report(role=role)
        settings = cfg_mod.Settings(output_format="markdown")
        md = gen_mod.ReportGenerator(settings).to_markdown(report)
        return StepResult(
            ok=True,
            markdown="## Status snapshot\n\n" + md,
            meta={"role": role, "demo": True},
        )
    except Exception as exc:  # noqa: BLE001
        return StepResult(
            ok=False,
            markdown=f"## Status snapshot\n\n_Unavailable: {exc}_\n",
            meta={"error": str(exc)},
        )


def calendar_placeholder() -> StepResult:
    now = datetime.now(timezone.utc).astimezone()
    return StepResult(
        ok=True,
        markdown=(
            "## Calendar (placeholder)\n\n"
            f"**Today:** {now.strftime('%A, %B %d %Y')}\n\n"
            "_No calendar connector configured. Add Microsoft Graph calendar read to a future "
            "workflow step or paste today's meetings here._\n"
        ),
        meta={"placeholder": True},
    )


def agt001_digest_markdown(*, dry_run: bool) -> StepResult:
    """Outlook inbox digest via local AGT-001 (Microsoft Graph device-code flow).

    Requires MS_CLIENT_ID and MS_TENANT_ID in .env. Gracefully degrades when
    credentials are absent or the MSAL device-code flow has not yet completed.
    Read-only — no emails are modified, deleted, or sent.
    """
    ms_client_id = os.getenv("MS_CLIENT_ID")

    if not ms_client_id:
        return StepResult(
            ok=True,
            markdown=(
                "## Email digest (AGT-001)\n\n"
                "_Microsoft Graph not configured. Set `MS_CLIENT_ID` and `MS_TENANT_ID` in `.env`"
                " then run without `--dry-run` to authenticate via device-code flow._\n\n"
                "See `docs/email/OVERVIEW.md` for setup instructions.\n"
            ),
            meta={"mode": "unconfigured"},
        )

    if dry_run:
        return StepResult(
            ok=True,
            markdown=(
                "## Email digest (AGT-001 dry-run)\n\n"
                "_Graph credentials found (`MS_CLIENT_ID` set). "
                "Run without `--dry-run` to authenticate and fetch live inbox._\n"
            ),
            meta={"mode": "dry-run", "configured": True},
        )

    try:
        _ensure_path(WORKBENCH_ROOT / "python" / "integrations")
        from agt001 import EmailChiefOfStaff  # type: ignore[import-not-found]

        digest = EmailChiefOfStaff().generate_daily_digest()
        return StepResult(
            ok=True,
            markdown=_format_agt001_digest(digest),
            meta={"mode": "live", "scanned": digest.total_emails_scanned},
        )
    except Exception as exc:  # noqa: BLE001
        return StepResult(
            ok=False,
            markdown=f"## Email digest (AGT-001)\n\n_Inbox fetch failed: {exc}_\n",
            meta={"error": str(exc)},
        )


def _format_agt001_digest(digest: Any) -> str:
    lines = [
        "## Email digest (AGT-001)",
        "",
        f"Scanned **{digest.total_emails_scanned}** messages.",
        "",
    ]
    if digest.handle_first:
        lines.append(f"### Handle first ({len(digest.handle_first)})")
        for item in digest.handle_first:
            urgency = item.urgency.upper()
            lines.append(f"- **[{urgency}]** {item.subject} — {item.sender}")
        lines.append("")
    if digest.decisions_needed:
        lines.append(f"### Decisions needed ({len(digest.decisions_needed)})")
        for item in digest.decisions_needed:
            lines.append(f"- {item.subject} — {item.sender}")
        lines.append("")
    if digest.action_required:
        lines.append(f"### Action required ({len(digest.action_required)})")
        for item in digest.action_required:
            due = f" *(due {item.due_date})*" if item.due_date else ""
            lines.append(f"- {item.subject}{due} — {item.sender}")
        lines.append("")
    follow_ups = len(digest.follow_ups)
    fyi = len(digest.fyi_items)
    delegatable = len(digest.delegatable)
    if follow_ups or fyi or delegatable:
        lines.append(f"Follow-ups: {follow_ups} | FYI: {fyi} | Delegatable: {delegatable}")
        lines.append("")
    return "\n".join(lines)

