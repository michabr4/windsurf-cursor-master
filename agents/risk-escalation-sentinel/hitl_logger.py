"""HITL decision logger for Risk & Escalation Sentinel.

Records SDM actions on risk cards to a newline-delimited JSON (JSONL)
log file — one file per run date, one entry per decision.

Typical usage (from a webhook handler or CLI):
    from hitl_logger import log_decision
    log_decision(
        account_id="acc-123",
        account_name="Acme Corp",
        action="escalate",
        run_date="2026-06-22",
        log_dir=settings.risk_sentinel_dir,
    )
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

VALID_ACTIONS = frozenset({"escalate", "schedule_call", "snooze", "dismiss"})


class HITLLogError(Exception):
    """Raised when a HITL log operation fails."""


def log_decision(
    account_id: str,
    account_name: str,
    action: str,
    run_date: str,
    log_dir: Path,
    notes: Optional[str] = None,
) -> Path:
    """Append one SDM decision entry to the daily HITL log.

    Args:
        account_id: Helix account ID.
        account_name: Account display name.
        action: SDM choice — one of 'escalate', 'schedule_call', 'snooze', 'dismiss'.
        run_date: ISO date of the sentinel scan (YYYY-MM-DD).
        log_dir: Directory to write HITL logs into (created if absent).
        notes: Optional free-text SDM note (max 500 chars).

    Returns:
        Path to the JSONL log file that was appended.

    Raises:
        ValueError: If action is not one of VALID_ACTIONS.
        HITLLogError: If writing the log entry fails.
    """
    if action not in VALID_ACTIONS:
        raise ValueError(
            f"Invalid HITL action '{action}'. "
            f"Must be one of: {sorted(VALID_ACTIONS)}"
        )

    try:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"hitl_log_{run_date}.jsonl"

        entry: dict = {
            "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "run_date": run_date,
            "account_id": account_id,
            "account_name": account_name,
            "action": action,
        }
        if notes:
            entry["notes"] = notes[:500]

        with log_file.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")

        logger.info(
            "HITL decision logged: account=%s action=%s file=%s",
            account_name,
            action,
            log_file.name,
        )
        return log_file

    except OSError as exc:
        raise HITLLogError(f"Failed to write HITL log: {exc}") from exc


def read_decisions(run_date: str, log_dir: Path) -> List[dict]:
    """Read all HITL decisions for a given run date.

    Args:
        run_date: ISO date string (YYYY-MM-DD).
        log_dir: Directory containing HITL log files.

    Returns:
        List of decision dicts in chronological order.
        Returns empty list if no log file exists for that date.
    """
    log_file = Path(log_dir) / f"hitl_log_{run_date}.jsonl"
    if not log_file.is_file():
        return []

    decisions = []
    for line in log_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            decisions.append(json.loads(line))
    return decisions
