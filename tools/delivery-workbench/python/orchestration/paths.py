"""Repository and workbench path helpers."""

from __future__ import annotations

from pathlib import Path

WORKBENCH_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = WORKBENCH_ROOT.parents[1]
ORCHESTRATION_DIR = WORKBENCH_ROOT / "orchestration"
RUNS_DIR = WORKBENCH_ROOT / "data" / "runs"
MORNING_BRIEFING_DIR = RUNS_DIR / "morning-briefing"

AGENT_FORGE = REPO_ROOT / "agents" / "forge"
AGENT_COMMUNICATION = REPO_ROOT / "agents" / "communication-agent"
AGENT_STATUS_REPORT = REPO_ROOT / "agents" / "status-report-agent"
