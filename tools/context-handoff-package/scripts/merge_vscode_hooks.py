#!/usr/bin/env python3
"""Merge context-handoff hook entries into an existing .github/hooks/*.json file."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def load_json(path: Path) -> dict:
    if not path.is_file():
        return {"hooks": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    data.setdefault("hooks", {})
    if not isinstance(data["hooks"], dict):
        raise ValueError(f"{path} hooks field must be an object")
    return data


def hook_key(entry: dict) -> str:
    command = str(entry.get("command") or "")
    hook_type = str(entry.get("type") or "")
    return f"{hook_type}|{command}"


def merge_hooks(target: dict, fragment: dict) -> tuple[dict, int]:
    merged = target
    merged.setdefault("hooks", {})
    added = 0

    for event, entries in (fragment.get("hooks") or {}).items():
        if not isinstance(entries, list):
            continue
        existing = merged["hooks"].setdefault(event, [])
        if not isinstance(existing, list):
            existing = []
            merged["hooks"][event] = existing
        seen = {hook_key(item) for item in existing if isinstance(item, dict)}
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            key = hook_key(entry)
            if key in seen:
                continue
            existing.append(entry)
            seen.add(key)
            added += 1

    return merged, added


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: merge_vscode_hooks.py <target-hooks.json> <fragment.json>", file=sys.stderr)
        return 2

    target_path = Path(sys.argv[1])
    fragment_path = Path(sys.argv[2])
    target = load_json(target_path)
    fragment = load_json(fragment_path)
    merged, added = merge_hooks(target, fragment)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
    print(f"merged {added} hook entries into {target_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
