"""Report formatter for Delivery Tracker.

Converts a WeeklySummary into:
  - A rich console table (for terminal display)
  - A markdown string (for file output or Webex posting)
"""

from __future__ import annotations

from typing import Optional

from rich.console import Console
from rich.table import Table
from rich import box

from models import AccountCaseMetrics, SLAStatus, WeeklySummary


_SLA_ICON = {
    SLAStatus.MET: "✅",
    SLAStatus.AT_RISK: "⚠️",
    SLAStatus.BREACHED: "🔴",
}


def _sla_cell(metrics: AccountCaseMetrics) -> str:
    if metrics.sla_status is None or metrics.sla_actual_pct is None:
        return "—"
    icon = _SLA_ICON.get(metrics.sla_status, "")
    return f"{icon} {metrics.sla_actual_pct:.1f}%"


def _milestone_cell(metrics: AccountCaseMetrics) -> str:
    if metrics.milestone_completion_pct is None:
        return "—"
    overdue_note = f" ({metrics.milestones_overdue} overdue)" if metrics.milestones_overdue else ""
    return f"{metrics.milestone_completion_pct:.0f}%{overdue_note}"


def render_console(summary: WeeklySummary, console: Optional[Console] = None) -> None:
    """Print the weekly summary as a rich table to the console."""
    console = console or Console()

    console.print()
    console.rule(f"[bold cyan]Delivery Tracker — {summary.period_label}[/bold cyan]")
    console.print()

    if summary.has_errors:
        for err in summary.errors:
            console.print(f"[bold red]ERROR:[/bold red] {err}")
        console.print()
        return

    # ── KPI banner ────────────────────────────────────────────────────────────
    console.print(
        f"[bold]Open cases:[/bold] {summary.total_open_cases}  "
        f"[bold]Overdue:[/bold] {summary.total_overdue}  "
        f"[bold]Escalated:[/bold] {summary.total_escalated}  "
        f"[bold]Accounts at SLA risk:[/bold] {len(summary.accounts_at_risk_sla)}"
    )
    console.print()

    # ── Per-account table ─────────────────────────────────────────────────────
    table = Table(
        box=box.ROUNDED,
        show_header=True,
        header_style="bold blue",
        expand=True,
    )
    table.add_column("Account", style="bold", min_width=20)
    table.add_column("Health", justify="center")
    table.add_column("Open", justify="right")
    table.add_column("Crit/High", justify="right")
    table.add_column("Overdue", justify="right")
    table.add_column("Escalated", justify="right")
    table.add_column("Avg Age", justify="right")
    table.add_column("SLA", justify="right")
    table.add_column("Milestones", justify="right")

    for m in sorted(summary.accounts, key=lambda x: (x.health_score or 100), reverse=False):
        overdue_style = "bold red" if m.overdue > 0 else ""
        escalated_style = "bold red" if m.escalated > 0 else ""
        health_cell = (
            f"{m.health_tier} {m.health_score:.0f}"
            if m.health_score is not None
            else "—"
        )
        table.add_row(
            m.account_name,
            health_cell,
            str(m.total_open),
            str(m.critical_high),
            f"[{overdue_style}]{m.overdue}[/{overdue_style}]" if overdue_style else str(m.overdue),
            f"[{escalated_style}]{m.escalated}[/{escalated_style}]" if escalated_style else str(m.escalated),
            f"{m.avg_age_days:.0f}d",
            _sla_cell(m),
            _milestone_cell(m),
        )

    console.print(table)

    if summary.accounts_at_risk_sla:
        console.print()
        console.print(
            "[bold yellow]⚠️  SLA attention needed:[/bold yellow] "
            + ", ".join(summary.accounts_at_risk_sla)
        )

    console.print()
    console.print(
        f"[dim]Generated {summary.generated_at.strftime('%Y-%m-%d %H:%M UTC')} "
        f"| Delivery Tracker v1 | T1 read-only[/dim]"
    )
    console.print()


def render_markdown(summary: WeeklySummary) -> str:
    """Return the summary as a markdown string."""
    lines: list[str] = []

    lines.append(f"# Delivery Tracker — {summary.period_label}")
    lines.append("")

    if summary.has_errors:
        for err in summary.errors:
            lines.append(f"> **ERROR:** {err}")
        return "\n".join(lines)

    # KPI row
    lines.append(
        f"**Open cases:** {summary.total_open_cases} | "
        f"**Overdue:** {summary.total_overdue} | "
        f"**Escalated:** {summary.total_escalated} | "
        f"**Accounts at SLA risk:** {len(summary.accounts_at_risk_sla)}"
    )
    lines.append("")

    # Per-account table
    lines.append("| Account | Health | Open | Crit/High | Overdue | Escalated | Avg Age | SLA | Milestones |")
    lines.append("|---------|:------:|-----:|----------:|--------:|----------:|--------:|-----|------------|")

    for m in sorted(summary.accounts, key=lambda x: (x.health_score or 100), reverse=False):
        overdue = f"**{m.overdue}**" if m.overdue > 0 else str(m.overdue)
        escalated = f"**{m.escalated}**" if m.escalated > 0 else str(m.escalated)
        health_cell = (
            f"{m.health_tier} {m.health_score:.0f}"
            if m.health_score is not None
            else "—"
        )
        lines.append(
            f"| {m.account_name} "
            f"| {health_cell} "
            f"| {m.total_open} "
            f"| {m.critical_high} "
            f"| {overdue} "
            f"| {escalated} "
            f"| {m.avg_age_days:.0f}d "
            f"| {_sla_cell(m)} "
            f"| {_milestone_cell(m)} |"
        )

    lines.append("")

    if summary.accounts_at_risk_sla:
        lines.append(
            f"⚠️ **SLA attention needed:** {', '.join(summary.accounts_at_risk_sla)}"
        )
        lines.append("")

    lines.append(
        f"*Generated {summary.generated_at.strftime('%Y-%m-%d %H:%M UTC')} "
        f"| Delivery Tracker v1 | T1 read-only*"
    )

    return "\n".join(lines)
