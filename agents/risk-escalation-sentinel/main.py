"""CLI entry point for Risk & Escalation Sentinel."""

from __future__ import annotations

import argparse
import logging
import sys

from config import get_settings
from sentinel import RiskEscalationSentinel


def _configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Risk & Escalation Sentinel — daily account risk scan (T2 HITL)",
    )
    parser.add_argument(
        "--date",
        metavar="YYYY-MM-DD",
        help="Delivery Tracker run date to evaluate (default: today)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Evaluate risks and write report without sending Webex cards",
    )
    args = parser.parse_args(argv)

    settings = get_settings()
    settings.dry_run = args.dry_run
    _configure_logging(settings.log_level)

    agent = RiskEscalationSentinel(settings=settings)
    report = agent.run(run_date=args.date)

    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
