"""Output formatters for agent reports."""

import json
import csv
import os
from datetime import datetime
from typing import Optional
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from models import AgentReport, ActionItem, Priority, ConversationType
from config import Settings, OutputFormat


class OutputFormatter:
    """Formats and outputs agent reports in various formats."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.console = Console()
        
        # Ensure output directory exists
        Path(settings.output_dir).mkdir(parents=True, exist_ok=True)
    
    def _get_output_path(self, filename: str) -> str:
        """Get full path for output file."""
        return os.path.join(self.settings.output_dir, filename)
    
    def _priority_color(self, priority: Priority) -> str:
        """Get color for priority level."""
        return {
            Priority.HIGH: "red",
            Priority.MEDIUM: "yellow",
            Priority.LOW: "green"
        }.get(priority, "white")
    
    def _format_date(self, dt: Optional[datetime]) -> str:
        """Format datetime for display."""
        if not dt:
            return "Not set"
        return dt.strftime("%Y-%m-%d %H:%M")
    
    def to_json(self, report: AgentReport, filename: Optional[str] = None) -> str:
        """Export report to JSON format."""
        filename = filename or f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self._get_output_path(filename)
        
        # Convert to dict with proper serialization
        data = {
            "generated_at": report.generated_at.isoformat(),
            "lookback_days": report.lookback_days,
            "summary": {
                "total_conversations": report.total_conversations,
                "customer_conversations": report.customer_conversations,
                "internal_conversations": report.internal_conversations,
                "total_messages": report.total_messages,
                "total_emails": report.total_emails,
                "total_meeting_transcripts": report.total_meeting_transcripts,
                "total_actions": len(report.action_items),
                "high_priority_actions": report.high_priority_count,
                "overdue_actions": report.overdue_count
            },
            "action_items": [
                {
                    "id": a.id,
                    "description": a.description,
                    "assignee": a.assignee,
                    "due_date": a.due_date.isoformat() if a.due_date else None,
                    "due_date_reasoning": a.due_date_reasoning,
                    "priority": a.priority.value,
                    "priority_reasoning": a.priority_reasoning,
                    "source_type": a.source_type.value,
                    "conversation_type": a.conversation_type.value,
                    "customer_name": a.customer_name,
                    "source_conversation_title": a.source_conversation_title,
                    "extracted_from_text": a.extracted_from_text,
                    "related_participants": a.related_participants,
                    "keywords_matched": a.keywords_matched,
                    "created_at": a.created_at.isoformat()
                }
                for a in report.action_items
            ],
            "actions_by_customer": {
                k: [a.id for a in v]
                for k, v in report.actions_by_customer.items()
            },
            "actions_by_priority": {
                k: [a.id for a in v]
                for k, v in report.actions_by_priority.items()
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def to_csv(self, report: AgentReport, filename: Optional[str] = None) -> str:
        """Export action items to CSV format."""
        filename = filename or f"actions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = self._get_output_path(filename)
        
        fieldnames = [
            'id', 'description', 'assignee', 'due_date', 'priority',
            'source_type', 'conversation_type', 'customer_name',
            'source_conversation_title', 'priority_reasoning',
            'due_date_reasoning', 'keywords_matched'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for action in report.action_items:
                writer.writerow({
                    'id': action.id,
                    'description': action.description,
                    'assignee': action.assignee or '',
                    'due_date': action.due_date.isoformat() if action.due_date else '',
                    'priority': action.priority.value,
                    'source_type': action.source_type.value,
                    'conversation_type': action.conversation_type.value,
                    'customer_name': action.customer_name or '',
                    'source_conversation_title': action.source_conversation_title,
                    'priority_reasoning': action.priority_reasoning or '',
                    'due_date_reasoning': action.due_date_reasoning or '',
                    'keywords_matched': ', '.join(action.keywords_matched)
                })
        
        return filepath
    
    def to_markdown(self, report: AgentReport, filename: Optional[str] = None) -> str:
        """Export report to Markdown format."""
        filename = filename or f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = self._get_output_path(filename)
        
        lines = [
            "# Communication Intelligence Report",
            "",
            f"**Generated:** {report.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"**Lookback Period:** {report.lookback_days} days",
            "",
            "## Summary",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Total Conversations | {report.total_conversations} |",
            f"| Customer Conversations | {report.customer_conversations} |",
            f"| Internal Conversations | {report.internal_conversations} |",
            f"| Total Messages | {report.total_messages} |",
            f"| Email Threads | {report.total_emails} |",
            f"| Meeting Transcripts | {report.total_meeting_transcripts} |",
            f"| **Total Action Items** | **{len(report.action_items)}** |",
            f"| High Priority | {report.high_priority_count} |",
            f"| Overdue | {report.overdue_count} |",
            "",
        ]
        
        # High Priority Actions
        high_priority = [a for a in report.action_items if a.priority == Priority.HIGH]
        if high_priority:
            lines.extend([
                "## 🔴 High Priority Actions",
                "",
            ])
            for action in high_priority:
                lines.extend(self._format_action_md(action))
        
        # Medium Priority Actions
        medium_priority = [a for a in report.action_items if a.priority == Priority.MEDIUM]
        if medium_priority:
            lines.extend([
                "## 🟡 Medium Priority Actions",
                "",
            ])
            for action in medium_priority:
                lines.extend(self._format_action_md(action))
        
        # Low Priority Actions
        low_priority = [a for a in report.action_items if a.priority == Priority.LOW]
        if low_priority:
            lines.extend([
                "## 🟢 Low Priority Actions",
                "",
            ])
            for action in low_priority:
                lines.extend(self._format_action_md(action))
        
        # Actions by Customer
        if report.actions_by_customer:
            lines.extend([
                "## Actions by Customer/Team",
                "",
            ])
            for customer, actions in sorted(report.actions_by_customer.items()):
                lines.append(f"### {customer} ({len(actions)} actions)")
                lines.append("")
                for action in actions:
                    lines.append(f"- [{action.priority.value.upper()}] {action.description}")
                    if action.due_date:
                        lines.append(f"  - Due: {self._format_date(action.due_date)}")
                lines.append("")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return filepath
    
    def _format_action_md(self, action: ActionItem) -> list:
        """Format a single action item as Markdown."""
        lines = [
            f"### {action.description}",
            "",
            f"- **Source:** {action.source_type.value} - {action.source_conversation_title}",
            f"- **Type:** {action.conversation_type.value}",
        ]
        
        if action.customer_name:
            lines.append(f"- **Customer:** {action.customer_name}")
        
        if action.assignee:
            lines.append(f"- **Assignee:** {action.assignee}")
        
        if action.due_date:
            lines.append(f"- **Due Date:** {self._format_date(action.due_date)}")
            if action.due_date_reasoning:
                lines.append(f"  - *{action.due_date_reasoning}*")
        
        if action.priority_reasoning:
            lines.append(f"- **Priority Reasoning:** {action.priority_reasoning}")
        
        if action.extracted_from_text:
            lines.extend([
                "",
                "> " + action.extracted_from_text.replace('\n', '\n> '),
            ])
        
        lines.append("")
        return lines
    
    def print_console(self, report: AgentReport):
        """Print formatted report to console using Rich."""
        # Header
        self.console.print()
        self.console.print(Panel.fit(
            "[bold blue]Communication Intelligence Report[/bold blue]",
            subtitle=f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M')} | Lookback: {report.lookback_days} days"
        ))
        
        # Summary Table
        summary_table = Table(title="Summary", box=box.ROUNDED)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", justify="right")
        
        summary_table.add_row("Total Conversations", str(report.total_conversations))
        summary_table.add_row("Customer Conversations", str(report.customer_conversations))
        summary_table.add_row("Internal Conversations", str(report.internal_conversations))
        summary_table.add_row("Total Messages", str(report.total_messages))
        summary_table.add_row("Email Threads", str(report.total_emails))
        summary_table.add_row("Meeting Transcripts", str(report.total_meeting_transcripts))
        summary_table.add_row("[bold]Total Action Items[/bold]", f"[bold]{len(report.action_items)}[/bold]")
        summary_table.add_row("[red]High Priority[/red]", f"[red]{report.high_priority_count}[/red]")
        summary_table.add_row("[yellow]Overdue[/yellow]", f"[yellow]{report.overdue_count}[/yellow]")
        
        self.console.print(summary_table)
        self.console.print()
        
        # Action Items Table
        if report.action_items:
            actions_table = Table(title="Action Items", box=box.ROUNDED, show_lines=True)
            actions_table.add_column("#", style="dim", width=3)
            actions_table.add_column("Priority", width=8)
            actions_table.add_column("Description", width=40)
            actions_table.add_column("Customer/Team", width=15)
            actions_table.add_column("Due Date", width=12)
            actions_table.add_column("Source", width=15)
            
            for i, action in enumerate(report.action_items[:20], 1):  # Show top 20
                priority_text = Text(action.priority.value.upper())
                priority_text.stylize(self._priority_color(action.priority))
                
                customer = action.customer_name or ("Internal" if action.conversation_type == ConversationType.INTERNAL else "-")
                due = self._format_date(action.due_date) if action.due_date else "-"
                
                # Truncate description
                desc = action.description[:80] + "..." if len(action.description) > 80 else action.description
                
                actions_table.add_row(
                    str(i),
                    priority_text,
                    desc,
                    customer[:15],
                    due,
                    action.source_type.value
                )
            
            self.console.print(actions_table)
            
            if len(report.action_items) > 20:
                self.console.print(f"\n[dim]... and {len(report.action_items) - 20} more action items[/dim]")
        else:
            self.console.print("[yellow]No action items found.[/yellow]")
        
        self.console.print()
    
    def save(self, report: AgentReport, format: Optional[OutputFormat] = None) -> str:
        """Save report in the configured or specified format."""
        format = format or self.settings.output_format
        
        if format == OutputFormat.JSON:
            return self.to_json(report)
        elif format == OutputFormat.CSV:
            return self.to_csv(report)
        elif format == OutputFormat.MARKDOWN:
            return self.to_markdown(report)
        else:
            raise ValueError(f"Unknown output format: {format}")
    
    def save_all_formats(self, report: AgentReport) -> dict:
        """Save report in all available formats."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        return {
            "json": self.to_json(report, f"report_{timestamp}.json"),
            "csv": self.to_csv(report, f"actions_{timestamp}.csv"),
            "markdown": self.to_markdown(report, f"report_{timestamp}.md")
        }
