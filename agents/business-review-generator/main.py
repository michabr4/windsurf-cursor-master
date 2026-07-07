"""CLI entry point for Business Review Generator."""

from __future__ import annotations

import argparse
import logging
import sys

from config import get_settings
from reviewer import BusinessReviewGenerator


def _configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Business Review Generator — QBR/EBR draft (T2 HITL)",
    )
    parser.add_argument("--account", required=True, help='Account name, e.g. "Acme Corp"')
    parser.add_argument("--quarter", required=True, help="Quarter label, e.g. Q2-2026")
    parser.add_argument(
        "--format",
        choices=["md"],
        default="md",
        help="Output format (default: md)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Skip LLM calls and Webex notifications",
    )
    args = parser.parse_args(argv)

    settings = get_settings()
    settings.dry_run = args.dry_run
    _configure_logging(settings.log_level)

    generator = BusinessReviewGenerator(settings=settings)
    draft = generator.run(args.account, args.quarter)

    if draft.output_path:
        print(f"Draft saved → {draft.output_path}")
    if draft.errors:
        for err in draft.errors:
            print(f"Warning: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
