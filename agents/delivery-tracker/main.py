"""CLI entry point for Delivery Tracker agent.

Usage:
    python main.py                   # console table only
    python main.py --output md       # markdown file in ./output/
    python main.py --output both     # console + markdown file
    python main.py --dry-run         # validate config, skip Helix calls
    python main.py --accounts "ACME Corp,Globex"
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from rich.console import Console

from config import get_settings
from report_formatter import render_console, render_markdown
from tracker import DeliveryTracker


def _configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )


def _write_markdown(content: str, output_dir: str) -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.utcnow().strftime("%Y%m%d-%H%M")
    filepath = out / f"delivery-tracker-{stamp}.md"
    filepath.write_text(content, encoding="utf-8")
    return filepath


def _dry_run(settings, console: Console) -> int:
    console.print("[bold yellow]Dry-run mode — validating configuration only[/bold yellow]")
    console.print()
    ok = settings.validate_helix()
    console.print(f"  HELIX_BASE_URL  : {'[green]set[/green]' if settings.helix_base_url else '[red]MISSING[/red]'}")
    console.print(f"  HELIX_API_TOKEN : {'[green]set[/green]' if settings.helix_api_token else '[red]MISSING[/red]'}")
    console.print(f"  LOOKBACK_DAYS   : {settings.lookback_days}")
    console.print(f"  ACCOUNT_FILTER  : {settings.account_filter or '(all accounts)'}")
    console.print(f"  OUTPUT_DIR      : {settings.output_dir}")
    console.print()
    if ok:
        console.print("[bold green]✅  Config valid — ready to run.[/bold green]")
        return 0
    console.print("[bold red]❌  Config invalid — set missing env vars in .env[/bold red]")
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Delivery Tracker — weekly Helix case/SLA/milestone summary",
    )
    parser.add_argument(
        "--output",
        choices=["console", "md", "both"],
        default="console",
        help="Output format (default: console)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate config and exit without making API calls",
    )
    parser.add_argument(
        "--accounts",
        metavar="NAMES",
        help="Comma-separated account name substring filter (overrides ACCOUNT_FILTER env var)",
    )
    parser.add_argument(
        "--lookback",
        type=int,
        metavar="DAYS",
        help="Lookback window in days (overrides LOOKBACK_DAYS env var)",
    )
    args = parser.parse_args(argv)

    settings = get_settings()

    if args.accounts:
        settings.account_filter = args.accounts
    if args.lookback:
        settings.lookback_days = args.lookback

    _configure_logging(settings.log_level)
    console = Console()

    if args.dry_run:
        return _dry_run(settings, console)

    tracker = DeliveryTracker(settings=settings)
    summary = tracker.run()

    if args.output in ("console", "both"):
        render_console(summary, console=console)

    if args.output in ("md", "both"):
        md = render_markdown(summary)
        path = _write_markdown(md, settings.output_dir)
        console.print(f"[dim]Markdown saved → {path}[/dim]")

    return 1 if summary.has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
