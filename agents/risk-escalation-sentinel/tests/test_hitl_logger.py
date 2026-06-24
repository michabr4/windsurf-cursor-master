"""Tests for HITL decision logger."""

import json
from pathlib import Path

import pytest

from hitl_logger import HITLLogError, VALID_ACTIONS, log_decision, read_decisions


def test_valid_action_creates_file(tmp_path):
    log_file = log_decision(
        account_id="acc-1",
        account_name="Acme Corp",
        action="escalate",
        run_date="2026-06-22",
        log_dir=tmp_path,
    )
    assert log_file.exists()
    assert log_file.name == "hitl_log_2026-06-22.jsonl"


def test_entry_fields_are_correct(tmp_path):
    log_decision(
        account_id="acc-2",
        account_name="Beta Ltd",
        action="snooze",
        run_date="2026-06-22",
        log_dir=tmp_path,
    )
    lines = (tmp_path / "hitl_log_2026-06-22.jsonl").read_text().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["account_id"] == "acc-2"
    assert entry["account_name"] == "Beta Ltd"
    assert entry["action"] == "snooze"
    assert entry["run_date"] == "2026-06-22"
    assert "timestamp" in entry


def test_notes_are_stored(tmp_path):
    log_decision(
        account_id="acc-3",
        account_name="Gamma",
        action="dismiss",
        run_date="2026-06-22",
        log_dir=tmp_path,
        notes="False positive — account is on scheduled maintenance.",
    )
    entry = json.loads(
        (tmp_path / "hitl_log_2026-06-22.jsonl").read_text().splitlines()[0]
    )
    assert "notes" in entry
    assert "False positive" in entry["notes"]


def test_notes_are_truncated_at_500_chars(tmp_path):
    long_note = "x" * 600
    log_decision(
        account_id="acc-4",
        account_name="Delta",
        action="schedule_call",
        run_date="2026-06-22",
        log_dir=tmp_path,
        notes=long_note,
    )
    entry = json.loads(
        (tmp_path / "hitl_log_2026-06-22.jsonl").read_text().splitlines()[0]
    )
    assert len(entry["notes"]) == 500


def test_multiple_decisions_appended(tmp_path):
    for action in ("escalate", "snooze", "dismiss"):
        log_decision(
            account_id=f"acc-{action}",
            account_name=f"Acct {action}",
            action=action,
            run_date="2026-06-22",
            log_dir=tmp_path,
        )
    lines = (tmp_path / "hitl_log_2026-06-22.jsonl").read_text().splitlines()
    assert len(lines) == 3


def test_invalid_action_raises_value_error(tmp_path):
    with pytest.raises(ValueError, match="Invalid HITL action"):
        log_decision(
            account_id="acc-5",
            account_name="Bad Actor",
            action="auto_send",
            run_date="2026-06-22",
            log_dir=tmp_path,
        )


def test_all_valid_actions_accepted(tmp_path):
    for i, action in enumerate(sorted(VALID_ACTIONS)):
        log_decision(
            account_id=f"acc-{i}",
            account_name=f"Acct {i}",
            action=action,
            run_date="2026-06-22",
            log_dir=tmp_path,
        )
    lines = (tmp_path / "hitl_log_2026-06-22.jsonl").read_text().splitlines()
    assert len(lines) == len(VALID_ACTIONS)


def test_read_decisions_returns_list(tmp_path):
    log_decision(
        account_id="acc-r1",
        account_name="Reader Co",
        action="escalate",
        run_date="2026-06-22",
        log_dir=tmp_path,
    )
    decisions = read_decisions(run_date="2026-06-22", log_dir=tmp_path)
    assert isinstance(decisions, list)
    assert len(decisions) == 1
    assert decisions[0]["action"] == "escalate"


def test_read_decisions_returns_empty_list_when_no_file(tmp_path):
    decisions = read_decisions(run_date="2099-01-01", log_dir=tmp_path)
    assert decisions == []


def test_log_creates_missing_log_dir(tmp_path):
    nested = tmp_path / "deep" / "nested" / "dir"
    log_decision(
        account_id="acc-n",
        account_name="Nested",
        action="dismiss",
        run_date="2026-06-22",
        log_dir=nested,
    )
    assert (nested / "hitl_log_2026-06-22.jsonl").exists()
