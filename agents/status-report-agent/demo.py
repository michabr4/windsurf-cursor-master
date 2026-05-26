"""Demo mode for Status Report Agent - generates sample report with mock data."""

from datetime import datetime, timedelta
import random

from models import (
    StatusReport, CaseMetrics, IncidentMetrics,
    ChangeMetrics, ProjectMetrics, ReportSection
)
from report_generator import ReportGenerator
from config import Settings


def generate_demo_report(role: str = "SDM", account_name: str = None) -> StatusReport:
    """
    Generate a demo status report with realistic mock data.
    
    Args:
        role: Role perspective (SDM, PM, PgM)
        account_name: Optional account name
    
    Returns:
        StatusReport with sample data
    """
    now = datetime.utcnow()
    period_start = now - timedelta(days=7)
    
    # Generate realistic metrics
    case_metrics = CaseMetrics(
        total_cases=47,
        open_cases=18,
        closed_cases=29,
        new_cases_this_period=12,
        resolved_this_period=15,
        by_priority={"High": 8, "Medium": 24, "Low": 15},
        by_status={"Open": 10, "In Progress": 8, "Closed": 29},
        by_account={
            "Acme Corp": 12,
            "TechStart Inc": 8,
            "Global Systems": 15,
            "DataFlow Ltd": 7,
            "Other": 5
        },
        avg_age_days=4.2,
        oldest_case_days=18,
        escalated_count=3
    )
    
    incident_metrics = IncidentMetrics(
        total_incidents=34,
        open_incidents=9,
        resolved_incidents=25,
        new_this_period=11,
        resolved_this_period=14,
        by_priority={"1": 1, "2": 6, "3": 15, "4": 12},
        by_state={"New": 2, "In Progress": 5, "On Hold": 2, "Resolved": 25},
        by_category={"Network": 12, "Application": 10, "Hardware": 7, "Other": 5},
        p1_count=1,
        p2_count=6,
        avg_resolution_hours=5.8,
        mttr_hours=5.8,
        sla_met_count=30,
        sla_breached_count=2,
        sla_at_risk_count=2,
        sla_compliance_pct=93.8
    )
    
    change_metrics = ChangeMetrics(
        total_changes=18,
        completed_changes=14,
        pending_changes=4,
        scheduled_this_period=6,
        by_type={"normal": 12, "standard": 4, "emergency": 2},
        by_risk={"low": 8, "moderate": 7, "high": 3},
        emergency_count=2,
        failed_count=1,
        success_rate=92.9
    )
    
    project_metrics = ProjectMetrics(
        total_tasks=28,
        completed_tasks=19,
        in_progress_tasks=6,
        overdue_tasks=3,
        by_priority={"1": 4, "2": 10, "3": 14},
        avg_completion_pct=68.0,
        on_track_count=22,
        at_risk_count=6
    )
    
    # Role-specific executive summaries
    summaries = {
        "SDM": """**Overall Status: 🟢 GREEN**

This week demonstrated strong service delivery performance across all key metrics. SLA compliance reached 93.8%, exceeding our 90% target, with only 2 breaches out of 34 incidents. The single P1 incident (network outage affecting Acme Corp) was resolved within 2.5 hours, well under the 4-hour SLA.

Case volume remained stable with 12 new cases opened against 15 resolved, reducing our backlog by 6%. Three escalated cases require continued attention, but all have active mitigation plans in place.

Looking ahead, we have 4 pending changes scheduled for next week, including a critical infrastructure upgrade for Global Systems. The change success rate of 92.9% gives confidence in our change management process.""",

        "PM": """**Overall Status: 🟡 YELLOW**

Project delivery is progressing with 68% average completion across active tasks. We completed 19 tasks this week, but 3 tasks are now overdue requiring immediate attention. The overdue items are primarily related to the DataFlow migration project, which has encountered unexpected data quality issues.

Resource utilization is at 87%, with some team members at capacity. We've identified a need for additional support on the Global Systems implementation, which is currently at risk due to scope changes.

Key milestone: The Acme Corp Phase 2 deployment is on track for next Friday's go-live. All pre-deployment checks are complete and stakeholder sign-off has been obtained.""",

        "PgM": """**Overall Status: 🟢 GREEN**

Portfolio health remains strong with 22 of 28 initiatives on track. The 6 at-risk items are being actively managed with mitigation plans in place. Cross-program dependencies are well-coordinated, with no blocking issues identified this week.

Financial performance is within budget at 94% of planned spend. The emergency changes this week (2 total) were both approved through expedited governance and completed successfully.

Strategic alignment review completed for Q2 initiatives. Three new opportunities identified for automation improvements that could reduce manual effort by an estimated 120 hours/month across the portfolio."""
    }
    
    # Role-specific highlights and concerns
    highlights_by_role = {
        "SDM": [
            "SLA compliance at 93.8%, exceeding 90% target",
            "P1 incident resolved in 2.5 hours (under 4-hour SLA)",
            "Case backlog reduced by 6% (15 resolved vs 12 new)",
            "Zero customer-impacting change failures"
        ],
        "PM": [
            "19 tasks completed this week",
            "Acme Corp Phase 2 on track for Friday go-live",
            "All pre-deployment checks passed",
            "Stakeholder sign-off obtained for 3 deliverables"
        ],
        "PgM": [
            "22 of 28 initiatives on track (79%)",
            "Portfolio spend at 94% of budget",
            "No cross-program blocking dependencies",
            "3 automation opportunities identified (120 hrs/month savings)"
        ]
    }
    
    concerns_by_role = {
        "SDM": [
            "3 escalated cases require executive attention",
            "2 SLA breaches this week (both P3 incidents)",
            "Aging case #00045123 at 18 days needs resolution plan"
        ],
        "PM": [
            "3 tasks overdue (DataFlow migration blocked)",
            "Resource constraint on Global Systems implementation",
            "Scope change request pending approval"
        ],
        "PgM": [
            "6 initiatives at risk requiring mitigation",
            "2 emergency changes indicate potential process gaps",
            "Q3 resource planning deadline approaching"
        ]
    }
    
    actions_by_role = {
        "SDM": [
            "Schedule escalation review meeting with account team",
            "Complete root cause analysis for SLA breaches",
            "Update capacity plan for holiday coverage"
        ],
        "PM": [
            "Escalate DataFlow data quality issues to vendor",
            "Request additional resource for Global Systems",
            "Finalize Acme Corp go-live runbook"
        ],
        "PgM": [
            "Review at-risk initiatives in Thursday governance",
            "Complete Q3 resource allocation proposal",
            "Schedule automation opportunity assessment"
        ]
    }
    
    report = StatusReport(
        report_id=f"demo-{now.strftime('%Y%m%d%H%M%S')}",
        generated_at=now,
        period_start=period_start,
        period_end=now,
        role=role,
        account_name=account_name,
        case_metrics=case_metrics,
        incident_metrics=incident_metrics,
        change_metrics=change_metrics,
        project_metrics=project_metrics,
        executive_summary=summaries.get(role, summaries["SDM"]),
        highlights=highlights_by_role.get(role, highlights_by_role["SDM"]),
        concerns=concerns_by_role.get(role, concerns_by_role["SDM"]),
        action_items=actions_by_role.get(role, actions_by_role["SDM"]),
        sections=[
            ReportSection(
                title="Service Health",
                content="All monitored services are operational. Uptime this week: 99.7%.",
                highlights=["Zero unplanned outages"],
                concerns=[],
                actions=[]
            ),
            ReportSection(
                title="Customer Satisfaction",
                content="CSAT score for resolved cases: 4.6/5.0 (target: 4.5).",
                highlights=["Above target CSAT"],
                concerns=["2 negative feedback items to address"],
                actions=["Follow up on negative feedback within 48 hours"]
            )
        ],
        data_sources=["Salesforce (Demo)", "ServiceNow (Demo)"],
        generation_time_seconds=0.5
    )
    
    return report


def run_demo(role: str = "SDM", output_format: str = "markdown", save: bool = True):
    """
    Run the demo and optionally save output.
    
    Args:
        role: Role perspective (SDM, PM, PgM)
        output_format: Output format (markdown, html, json)
        save: Whether to save to file
    
    Returns:
        Tuple of (report, filepath or None)
    """
    print(f"\n{'='*60}")
    print(f"  Status Report Agent - DEMO MODE")
    print(f"  Role: {role}")
    print(f"{'='*60}\n")
    
    report = generate_demo_report(role=role)
    
    settings = Settings(output_format=output_format)
    generator = ReportGenerator(settings)
    
    if output_format == "markdown":
        content = generator.to_markdown(report)
    elif output_format == "html":
        content = generator.to_html(report)
    else:
        content = generator.to_json(report)
    
    # Print preview
    print("📊 REPORT PREVIEW (first 2000 chars):")
    print("-" * 40)
    print(content[:2000])
    if len(content) > 2000:
        print(f"\n... [{len(content) - 2000} more characters]")
    print("-" * 40)
    
    filepath = None
    if save:
        filepath = generator.save(report, output_format)
        print(f"\n✅ Full report saved to: {filepath}")
    
    return report, filepath


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Status Report Agent in demo mode")
    parser.add_argument("--role", "-r", choices=["SDM", "PM", "PgM"], default="SDM")
    parser.add_argument("--format", "-f", choices=["markdown", "html", "json"], default="markdown")
    parser.add_argument("--no-save", action="store_true", help="Don't save to file")
    
    args = parser.parse_args()
    run_demo(role=args.role, output_format=args.format, save=not args.no_save)
