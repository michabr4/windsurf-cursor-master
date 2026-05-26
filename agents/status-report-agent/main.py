#!/usr/bin/env python3
"""
Status Report Agent - CLI Entry Point

Agent #1 from Helix Agentic Framework V3:
Automated Status Report Generation

Queries Salesforce + ServiceNow, generates LLM-powered narratives,
and produces formatted weekly status reports for SDM/PM/PgM roles.
"""

import argparse
import logging
import sys
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.table import Table

from config import get_settings
from agent import StatusReportAgent
from report_generator import ReportGenerator

console = Console()


def setup_logging(verbose: bool = False):
    """Configure logging with rich handler."""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)]
    )


def print_summary(report):
    """Print a summary of the report to console."""
    console.print()
    console.print(Panel.fit(
        f"[bold cyan]Weekly Status Report — {report.role}[/bold cyan]\n"
        f"[dim]{report.period_label}[/dim]",
        border_style="cyan"
    ))
    
    # Summary table
    table = Table(title="Summary", show_header=True, header_style="bold")
    table.add_column("Metric", style="dim")
    table.add_column("Value", justify="right")
    
    if report.case_metrics:
        table.add_row("SF Cases (Total)", str(report.case_metrics.total_cases))
        table.add_row("SF Cases (Open)", str(report.case_metrics.open_cases))
        table.add_row("SF Cases (New)", str(report.case_metrics.new_cases_this_period))
    
    if report.incident_metrics:
        table.add_row("Incidents (Total)", str(report.incident_metrics.total_incidents))
        table.add_row("Incidents (P1)", str(report.incident_metrics.p1_count))
        table.add_row("SLA Compliance", f"{report.incident_metrics.sla_compliance_pct:.1f}%")
    
    if report.change_metrics:
        table.add_row("Changes (Total)", str(report.change_metrics.total_changes))
        table.add_row("Changes (Completed)", str(report.change_metrics.completed_changes))
    
    if report.project_metrics:
        table.add_row("Tasks (Total)", str(report.project_metrics.total_tasks))
        table.add_row("Tasks (Overdue)", str(report.project_metrics.overdue_tasks))
    
    console.print(table)
    
    # Executive Summary
    if report.executive_summary:
        console.print()
        console.print(Panel(
            report.executive_summary,
            title="[bold]Executive Summary[/bold]",
            border_style="green"
        ))
    
    # Highlights
    if report.highlights:
        console.print()
        console.print("[bold green]✅ Highlights[/bold green]")
        for h in report.highlights:
            console.print(f"  • {h}")
    
    # Concerns
    if report.concerns:
        console.print()
        console.print("[bold yellow]⚠️  Concerns[/bold yellow]")
        for c in report.concerns:
            console.print(f"  • {c}")
    
    # Actions
    if report.action_items:
        console.print()
        console.print("[bold blue]📋 Action Items[/bold blue]")
        for a in report.action_items:
            console.print(f"  ☐ {a}")
    
    console.print()
    console.print(f"[dim]Generated in {report.generation_time_seconds:.1f}s | "
                  f"Sources: {', '.join(report.data_sources)}[/dim]")


def main():
    parser = argparse.ArgumentParser(
        description="Status Report Agent - Automated weekly status report generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                          # Run with defaults from .env
  python main.py --role SDM --days 7      # SDM report for last 7 days
  python main.py --role PM --account Acme # PM report filtered to Acme account
  python main.py --output html --all      # Save in all formats
        """
    )
    
    parser.add_argument(
        "--role", "-r",
        choices=["SDM", "PM", "PgM"],
        help="Role perspective for the report (default: from .env or SDM)"
    )
    
    parser.add_argument(
        "--days", "-d",
        type=int,
        help="Number of days to look back (default: 7)"
    )
    
    parser.add_argument(
        "--account", "-a",
        help="Filter by Salesforce account name"
    )
    
    parser.add_argument(
        "--group", "-g",
        help="Filter by ServiceNow assignment group"
    )
    
    parser.add_argument(
        "--output", "-o",
        choices=["markdown", "md", "html", "json"],
        help="Output format (default: markdown)"
    )
    
    parser.add_argument(
        "--output-dir",
        help="Directory to save reports (default: ./output)"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Save report in all formats"
    )
    
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save report to file, only print to console"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress console output, only save file"
    )

    parser.add_argument(
        "--deliver",
        nargs="+",
        choices=["email", "webex"],
        metavar="CHANNEL",
        help="After generation, send via configured channel(s): email, webex (see .env.example)",
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Load settings
    settings = get_settings()
    
    # Override settings from args
    if args.output_dir:
        settings.output_dir = args.output_dir
    if args.output:
        settings.output_format = args.output
    
    # Create and run agent
    try:
        agent = StatusReportAgent(settings)
        
        report = agent.run(
            lookback_days=args.days,
            role=args.role,
            account_filter=args.account,
            assignment_group=args.group,
            save_report=not args.no_save,
            output_format=args.output
        )
        
        # Save all formats if requested
        if args.all and not args.no_save:
            generator = ReportGenerator(settings)
            paths = generator.save_all_formats(report)
            console.print(f"[green]Saved reports:[/green]")
            for fmt, path in paths.items():
                console.print(f"  • {fmt}: {path}")
        
        # Print summary unless quiet
        if not args.quiet:
            print_summary(report)

        if args.deliver:
            from delivery import DeliveryManager

            dm = DeliveryManager(settings)
            results = dm.deliver(report, channels=args.deliver)
            for r in results:
                dest = r.destination or "(n/a)"
                if r.success:
                    console.print(f"[green]Delivered[/green] via {r.channel} → {dest}")
                else:
                    console.print(
                        f"[red]Delivery failed[/red] ({r.channel} → {dest}): "
                        f"{r.error or 'unknown error'}"
                    )
        
        return 0
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        return 130
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if args.verbose:
            console.print_exception()
        return 1


if __name__ == "__main__":
    sys.exit(main())
