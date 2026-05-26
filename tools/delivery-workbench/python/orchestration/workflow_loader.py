"""Load orchestration workflow YAML definitions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .paths import ORCHESTRATION_DIR


def load_workflow(name: str) -> dict[str, Any]:
    """Load workflow by file stem (e.g. email-digest)."""
    path = ORCHESTRATION_DIR / f"{name}.yaml"
    if not path.is_file():
        raise FileNotFoundError(f"Workflow not found: {path}")
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid workflow YAML: {path}")
    return data


def list_workflows() -> list[str]:
    return sorted(p.stem for p in ORCHESTRATION_DIR.glob("*.yaml"))
