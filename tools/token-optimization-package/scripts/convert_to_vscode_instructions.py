#!/usr/bin/env python3
"""Convert .cursor/rules/*.md templates to .github/instructions/*.instructions.md."""

from __future__ import annotations

import re
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parents[1]
SRC = PACKAGE_DIR / "templates/cursor/rules"
DEST = PACKAGE_DIR / "templates/vscode/instructions"


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    meta: dict[str, str] = {}
    for line in parts[1].strip().splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip()
    return meta, parts[2].lstrip("\n")


def apply_to(meta: dict[str, str]) -> str:
    globs = meta.get("globs", "").strip().strip("'\"")
    always = meta.get("alwaysApply", "").strip().lower() == "true"
    if globs:
        return globs
    if always:
        return "**"
    return "**"


def convert_file(src: Path) -> None:
    text = src.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)
    name = src.stem
    description = meta.get("description", name).strip("'\"")
    out = DEST / f"{name}.instructions.md"
    content = (
        "---\n"
        f"description: {description}\n"
        f'applyTo: "{apply_to(meta)}"\n'
        "---\n"
        f"{body}"
    )
    out.write_text(content, encoding="utf-8")


def main() -> int:
    DEST.mkdir(parents=True, exist_ok=True)
    for src in sorted(SRC.glob("*.md")):
        convert_file(src)
    print(f"Wrote VS Code instructions to {DEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
