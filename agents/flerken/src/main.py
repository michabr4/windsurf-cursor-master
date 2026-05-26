"""Flerken — Personal AI Assistant entry point."""

import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .config import cfg
from .dashboard import build_dashboard
from .digest_builder import DigestBuilder

console = Console()


def print_banner(demo: bool = False) -> None:
    banner = Text()
    banner.append("  FLERKEN  ", style="bold white on purple")
    banner.append("  Personal AI Assistant\n", style="bold purple")
    banner.append("  Email Triage & Daily Digest", style="dim")
    if demo:
        banner.append("\n  DEMO MODE", style="bold yellow")
    console.print(Panel(banner, border_style="purple", padding=(1, 2)))


def check_config(demo: bool = False) -> bool:
    """Validate configuration and print helpful messages for missing values."""
    if demo:
        return True
    missing = cfg.validate()
    if missing:
        console.print("\n[bold red]Missing configuration:[/bold red]")
        for key in missing:
            console.print(f"  [red]✗[/red] {key}")
        console.print(
            "\n[dim]Copy .env.example to .env and fill in your values.[/dim]"
        )
        console.print("[dim]See README.md for setup instructions.[/dim]")
        console.print("[dim]Or run with --demo to try with mock emails.[/dim]\n")
        return False
    return True


def run_digest(demo: bool = False) -> None:
    """Run the full digest pipeline."""
    mode_label = "[yellow]DEMO[/yellow] " if demo else ""
    console.print(f"\n[bold purple]Starting {mode_label}digest pipeline...[/bold purple]\n")

    builder = DigestBuilder(demo=demo)
    result = builder.build()

    if not result["data"]:
        console.print("[yellow]No emails to digest.[/yellow]")
        return

    data = result["data"]
    counts = data["counts"]

    # Print summary to terminal
    console.print("\n[bold]Digest Summary:[/bold]")
    console.print(f"  [red]Urgent:[/red]          {counts['urgent']}")
    console.print(f"  [yellow]Action Required:[/yellow] {counts['action_required']}")
    console.print(f"  [blue]FYI:[/blue]             {counts['fyi']}")
    console.print(f"  [green]Low Priority:[/green]    {counts['low_priority']}")
    console.print(f"  [dim]Total:[/dim]           {data['total']}")

    console.print(f"\n[bold]Executive Summary:[/bold]\n{data['executive_summary']}\n")

    # Save HTML locally
    out_path = Path(__file__).resolve().parent.parent / "out"
    out_path.mkdir(exist_ok=True)
    html_file = out_path / "latest_digest.html"
    html_file.write_text(result["html"], encoding="utf-8")
    console.print(f"[dim]Digest saved to {html_file}[/dim]")

    # Generate interactive dashboard
    console.print("  Building priority dashboard...")
    dashboard_html = build_dashboard(
        triaged=data["triaged"],
        executive_summary=data["executive_summary"],
    )
    dash_file = out_path / "dashboard.html"
    dash_file.write_text(dashboard_html, encoding="utf-8")
    console.print(f"[dim]Dashboard saved to {dash_file}[/dim]")

    if demo:
        console.print(f"\n[bold green]Demo complete![/bold green] Open the dashboard:")
        console.print(f"  [cyan]open {dash_file}[/cyan]\n")
    else:
        # Send email
        try:
            builder.send_digest(result["html"])
            console.print("[bold green]Digest emailed successfully![/bold green]\n")
        except Exception as e:
            console.print(f"[bold red]Failed to send email:[/bold red] {e}")
            console.print("[dim]The HTML digest was saved locally — you can open it in a browser.[/dim]\n")


def run_offline_mail_export() -> None:
    """Parse Apple Mail unit-delimited export (no Graph/OpenAI)."""
    from .optional.offline_mail_digest import run_offline_digest

    args = [a for a in sys.argv[1:] if a != "--offline-mail"]
    export = Path(args[0]) if args else None
    out_dir = Path(__file__).resolve().parent.parent / "out"
    out_path = run_offline_digest(export, out_dir)
    console.print(f"[bold green]Offline digest written:[/bold green] {out_path}\n")


def main() -> None:
    if "--offline-mail" in sys.argv:
        print_banner(demo=False)
        run_offline_mail_export()
        return

    demo = "--demo" in sys.argv
    print_banner(demo=demo)

    if not check_config(demo=demo):
        sys.exit(1)

    run_digest(demo=demo)


if __name__ == "__main__":
    main()
