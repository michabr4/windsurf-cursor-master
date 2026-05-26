"""Report generation and formatting for Status Report Agent."""

import logging
from datetime import datetime
from typing import Optional
from pathlib import Path
import json

from config import Settings
from models import StatusReport, ReportSection

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates formatted reports from StatusReport data."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.output_dir = Path(settings.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def to_markdown(self, report: StatusReport) -> str:
        """
        Convert StatusReport to Markdown format.
        
        Args:
            report: StatusReport object
        
        Returns:
            Markdown formatted string
        """
        lines = []
        
        # Header
        lines.append(f"# Weekly Status Report — {report.role}")
        if report.account_name:
            lines.append(f"## Account: {report.account_name}")
        lines.append(f"**Period:** {report.period_label}")
        lines.append(f"**Generated:** {report.generated_at.strftime('%Y-%m-%d %H:%M UTC')}")
        lines.append("")
        
        # Executive Summary
        lines.append("---")
        lines.append("## Executive Summary")
        lines.append("")
        lines.append(report.executive_summary)
        lines.append("")
        
        # Key Highlights
        if report.highlights:
            lines.append("### ✅ Key Highlights")
            for h in report.highlights:
                lines.append(f"- {h}")
            lines.append("")
        
        # Concerns
        if report.concerns:
            lines.append("### ⚠️ Concerns & Risks")
            for c in report.concerns:
                lines.append(f"- {c}")
            lines.append("")
        
        # Action Items
        if report.action_items:
            lines.append("### 📋 Action Items")
            for a in report.action_items:
                lines.append(f"- [ ] {a}")
            lines.append("")
        
        # Metrics Summary
        lines.append("---")
        lines.append("## Metrics Summary")
        lines.append("")
        
        # Cases
        if report.case_metrics:
            cm = report.case_metrics
            lines.append("### Salesforce Cases")
            lines.append("")
            lines.append("| Metric | Value |")
            lines.append("|--------|-------|")
            lines.append(f"| Total Cases | {cm.total_cases} |")
            lines.append(f"| Open | {cm.open_cases} |")
            lines.append(f"| Closed | {cm.closed_cases} |")
            lines.append(f"| New This Period | {cm.new_cases_this_period} |")
            lines.append(f"| Resolved This Period | {cm.resolved_this_period} |")
            lines.append(f"| Escalated | {cm.escalated_count} |")
            lines.append(f"| Avg Age (days) | {cm.avg_age_days:.1f} |")
            lines.append("")
            
            if cm.by_priority:
                lines.append("**By Priority:**")
                for p, count in cm.by_priority.items():
                    lines.append(f"- {p}: {count}")
                lines.append("")
        
        # Incidents
        if report.incident_metrics:
            im = report.incident_metrics
            lines.append("### ServiceNow Incidents")
            lines.append("")
            lines.append("| Metric | Value |")
            lines.append("|--------|-------|")
            lines.append(f"| Total Incidents | {im.total_incidents} |")
            lines.append(f"| Open | {im.open_incidents} |")
            lines.append(f"| Resolved | {im.resolved_incidents} |")
            lines.append(f"| P1 Count | {im.p1_count} |")
            lines.append(f"| P2 Count | {im.p2_count} |")
            lines.append(f"| MTTR (hours) | {im.mttr_hours:.1f} |")
            lines.append(f"| SLA Compliance | {im.sla_compliance_pct:.1f}% |")
            lines.append(f"| SLA Breached | {im.sla_breached_count} |")
            lines.append("")
        
        # Changes
        if report.change_metrics:
            chm = report.change_metrics
            lines.append("### ServiceNow Changes")
            lines.append("")
            lines.append("| Metric | Value |")
            lines.append("|--------|-------|")
            lines.append(f"| Total Changes | {chm.total_changes} |")
            lines.append(f"| Completed | {chm.completed_changes} |")
            lines.append(f"| Pending | {chm.pending_changes} |")
            lines.append(f"| Emergency | {chm.emergency_count} |")
            lines.append(f"| Success Rate | {chm.success_rate:.1f}% |")
            lines.append("")
        
        # Tasks
        if report.project_metrics:
            pm = report.project_metrics
            lines.append("### Project Tasks")
            lines.append("")
            lines.append("| Metric | Value |")
            lines.append("|--------|-------|")
            lines.append(f"| Total Tasks | {pm.total_tasks} |")
            lines.append(f"| Completed | {pm.completed_tasks} |")
            lines.append(f"| In Progress | {pm.in_progress_tasks} |")
            lines.append(f"| Overdue | {pm.overdue_tasks} |")
            lines.append(f"| On Track | {pm.on_track_count} |")
            lines.append(f"| At Risk | {pm.at_risk_count} |")
            lines.append("")
        
        # Sections
        if report.sections:
            lines.append("---")
            lines.append("## Detailed Sections")
            lines.append("")
            
            for section in report.sections:
                lines.append(f"### {section.title}")
                lines.append("")
                lines.append(section.content)
                lines.append("")
                
                if section.highlights:
                    lines.append("**Highlights:**")
                    for h in section.highlights:
                        lines.append(f"- {h}")
                    lines.append("")
                
                if section.concerns:
                    lines.append("**Concerns:**")
                    for c in section.concerns:
                        lines.append(f"- ⚠️ {c}")
                    lines.append("")
                
                if section.actions:
                    lines.append("**Actions:**")
                    for a in section.actions:
                        lines.append(f"- [ ] {a}")
                    lines.append("")
        
        # Footer
        lines.append("---")
        lines.append(f"*Report generated by Status Report Agent in {report.generation_time_seconds:.1f}s*")
        lines.append(f"*Data sources: {', '.join(report.data_sources)}*")
        
        return "\n".join(lines)
    
    def to_html(self, report: StatusReport) -> str:
        """
        Convert StatusReport to HTML format.
        
        Args:
            report: StatusReport object
        
        Returns:
            HTML formatted string
        """
        md_content = self.to_markdown(report)
        
        # Simple Markdown to HTML conversion
        html_content = md_content
        
        # Headers
        html_content = html_content.replace("# ", "<h1>").replace("\n## ", "</h1>\n<h2>")
        html_content = html_content.replace("\n### ", "</h2>\n<h3>")
        
        # Bold
        import re
        html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)
        
        # Lists
        lines = html_content.split("\n")
        in_list = False
        new_lines = []
        
        for line in lines:
            if line.startswith("- "):
                if not in_list:
                    new_lines.append("<ul>")
                    in_list = True
                new_lines.append(f"<li>{line[2:]}</li>")
            else:
                if in_list:
                    new_lines.append("</ul>")
                    in_list = False
                new_lines.append(line)
        
        if in_list:
            new_lines.append("</ul>")
        
        html_content = "\n".join(new_lines)
        
        # Tables
        html_content = html_content.replace("| Metric | Value |", "<table><tr><th>Metric</th><th>Value</th></tr>")
        html_content = html_content.replace("|--------|-------|", "")
        html_content = re.sub(r'\| (.+?) \| (.+?) \|', r'<tr><td>\1</td><td>\2</td></tr>', html_content)
        
        # Wrap in HTML document
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Status Report - {report.role} - {report.period_label}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               max-width: 900px; margin: 40px auto; padding: 20px; line-height: 1.6; }}
        h1 {{ color: #049fd9; border-bottom: 2px solid #049fd9; padding-bottom: 10px; }}
        h2 {{ color: #1e3a5f; margin-top: 30px; }}
        h3 {{ color: #374151; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
        th, td {{ border: 1px solid #cbd5e1; padding: 8px 12px; text-align: left; }}
        th {{ background: #f1f5f9; font-weight: 600; }}
        tr:nth-child(even) td {{ background: #f8fafc; }}
        ul {{ margin: 10px 0; }}
        li {{ margin: 5px 0; }}
        hr {{ border: none; border-top: 1px solid #e2e8f0; margin: 30px 0; }}
        .highlight {{ background: #ecfdf5; padding: 2px 6px; border-radius: 3px; }}
        .concern {{ background: #fef2f2; padding: 2px 6px; border-radius: 3px; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
        
        return html
    
    def to_json(self, report: StatusReport) -> str:
        """
        Convert StatusReport to JSON format.
        
        Args:
            report: StatusReport object
        
        Returns:
            JSON formatted string
        """
        return report.model_dump_json(indent=2)
    
    def save(self, report: StatusReport, format: Optional[str] = None) -> str:
        """
        Save report to file.
        
        Args:
            report: StatusReport object
            format: Output format (markdown, html, json). Uses settings default if not specified.
        
        Returns:
            Path to saved file
        """
        format = format or self.settings.output_format
        
        timestamp = report.generated_at.strftime("%Y%m%d_%H%M%S")
        account_suffix = f"_{report.account_name.replace(' ', '_')}" if report.account_name else ""
        
        if format == "markdown" or format == "md":
            filename = f"status_report_{report.role}_{timestamp}{account_suffix}.md"
            content = self.to_markdown(report)
        elif format == "html":
            filename = f"status_report_{report.role}_{timestamp}{account_suffix}.html"
            content = self.to_html(report)
        elif format == "json":
            filename = f"status_report_{report.role}_{timestamp}{account_suffix}.json"
            content = self.to_json(report)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        filepath = self.output_dir / filename
        filepath.write_text(content, encoding="utf-8")
        
        logger.info(f"Report saved to {filepath}")
        return str(filepath)
    
    def save_all_formats(self, report: StatusReport) -> dict:
        """
        Save report in all formats.
        
        Args:
            report: StatusReport object
        
        Returns:
            Dictionary mapping format to filepath
        """
        paths = {}
        for fmt in ["markdown", "html", "json"]:
            paths[fmt] = self.save(report, fmt)
        return paths
