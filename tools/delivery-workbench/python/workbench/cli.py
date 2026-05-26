"""CLI for scaffolding dated drafts into data/<project>/."""

from __future__ import annotations

import argparse
import re
import shutil
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = REPO_ROOT / "templates"
DATA = REPO_ROOT / "data"
PROJECTS = REPO_ROOT / "projects"

TEMPLATE_MAP = {
    "status-report": TEMPLATES / "status-report.md",
    "meeting-notes": TEMPLATES / "meeting-notes.md",
    "raid-entry": TEMPLATES / "raid-entry.md",
}

_SLUG_RE = re.compile(r"^[a-z0-9_][a-z0-9_-]{0,63}$")


def _validate_slug(slug: str) -> str:
    slug = slug.strip().lower()
    if not _SLUG_RE.match(slug):
        raise argparse.ArgumentTypeError(
            "project slug must be 1–64 chars: lowercase letters, digits, hyphen, underscore"
        )
    return slug


def _project_dir(slug: str) -> Path:
    proj = PROJECTS / slug
    if not proj.is_dir():
        raise SystemExit(f"Unknown project folder: {proj}\nCopy projects/_example to projects/{slug} first.")
    return proj


def _scaffold(template_key: str, slug: str, prefix: str) -> Path:
    src = TEMPLATE_MAP.get(template_key)
    if src is None or not src.is_file():
        raise SystemExit(f"Unknown template: {template_key}")

    _project_dir(slug)
    out_dir = DATA / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    today = date.today().isoformat()
    dest = out_dir / f"{today}-{prefix}.md"
    if dest.exists():
        n = 2
        while dest.exists():
            dest = out_dir / f"{today}-{prefix}-{n}.md"
            n += 1

    shutil.copy2(src, dest)
    return dest


def cmd_new_status_draft(args: argparse.Namespace) -> int:
    path = _scaffold("status-report", args.project, "status-report")
    print(f"Created: {path}")
    return 0


def cmd_new_meeting_draft(args: argparse.Namespace) -> int:
    path = _scaffold("meeting-notes", args.project, "meeting-notes")
    print(f"Created: {path}")
    return 0


def cmd_new_raid_draft(args: argparse.Namespace) -> int:
    path = _scaffold("raid-entry", args.project, "raid-entry")
    print(f"Created: {path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="workbench",
        description="Delivery Workbench — scaffold local drafts from templates.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    for name, handler, help_text in (
        ("new-status-draft", cmd_new_status_draft, "Copy status-report template to data/<project>/"),
        ("new-meeting-draft", cmd_new_meeting_draft, "Copy meeting-notes template to data/<project>/"),
        ("new-raid-draft", cmd_new_raid_draft, "Copy raid-entry template to data/<project>/"),
    ):
        p = sub.add_parser(name, help=help_text)
        p.add_argument(
            "--project",
            type=_validate_slug,
            required=True,
            help="Project slug (folder under projects/)",
        )
        p.set_defaults(func=handler)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
