"""CLI entry point for Delivery Tracker agent.

Usage:
    python main.py                   # console table only
    python main.py --output md       # markdown file in ./output/
    python main.py --output both     # console + markdown file
    python main.py --output webex    # post to Webex (requires WEBEX_* env vars)
    python main.py --output all      # console + markdown file + Webex
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
from webex_sender import WebexSendError, send_report


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
    console.print()
    console.print("[bold]Webex (optional)[/bold]")
    console.print(f"  WEBEX_BOT_TOKEN  : {'[green]set[/green]' if settings.webex_bot_token else '[dim]not set[/dim]'}")
    console.print(f"  WEBEX_ROOM_ID    : {'[green]set[/green]' if settings.webex_room_id else '[dim]not set[/dim]'}")
    console.print(f"  WEBEX_PERSON_EMAIL: {'[green]set[/green]' if settings.webex_person_email else '[dim]not set[/dim]'}")
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
        choices=["console", "md", "both", "webex", "all"],
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

    if args.output in ("console", "both", "all"):
        render_console(summary, console=console)

    if args.output in ("md", "both", "all"):
        md = render_markdown(summary)
        path = _write_markdown(md, settings.output_dir)
        console.print(f"[dim]Markdown saved → {path}[/dim]")

    if args.output in ("webex", "all"):
        if not settings.validate_webex():
            console.print(
                "[bold red]Webex not configured — set WEBEX_BOT_TOKEN and "
                "WEBEX_ROOM_ID (or WEBEX_PERSON_EMAIL) in .env[/bold red]"
            )
        else:
            md = md if args.output == "all" else render_markdown(summary)
            try:
                msg_id = send_report(md, settings)
                console.print(f"[dim]Webex message sent → {msg_id}[/dim]")
            except WebexSendError as exc:
                console.print(f"[bold red]Webex send failed: {exc}[/bold red]")

    return 1 if summary.has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
