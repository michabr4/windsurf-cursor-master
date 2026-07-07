"""Digest builder — assembles triaged emails into a formatted HTML digest."""

from datetime import datetime, timezone
from typing import Any

from jinja2 import Template

from .llm_client import LLMClient
from .outlook_client import OutlookClient
from .mock_emails import MOCK_EMAILS
from .severity import apply_severity
from .config import cfg

DIGEST_TEMPLATE = Template("""\
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; color: #1a1a1a; }
  .container { max-width: 680px; margin: 0 auto; background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
  .header { background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 28px 32px; }
  .header h1 { margin: 0 0 6px 0; font-size: 24px; font-weight: 700; }
  .header .subtitle { opacity: 0.85; font-size: 14px; }
  .summary { padding: 24px 32px; background: #fafafa; border-bottom: 1px solid #eee; font-size: 15px; line-height: 1.6; color: #444; }
  .stats { display: flex; gap: 16px; padding: 16px 32px; border-bottom: 1px solid #eee; }
  .stat { flex: 1; text-align: center; padding: 12px 8px; border-radius: 8px; }
  .stat-urgent { background: #fef2f2; color: #dc2626; }
  .stat-action { background: #fff7ed; color: #ea580c; }
  .stat-fyi { background: #eff6ff; color: #2563eb; }
  .stat-low { background: #f0fdf4; color: #16a34a; }
  .stat .num { font-size: 28px; font-weight: 700; }
  .stat .label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 2px; }
  .section { padding: 20px 32px; }
  .section h2 { font-size: 16px; font-weight: 600; margin: 0 0 16px 0; padding-bottom: 8px; border-bottom: 2px solid; }
  .section-urgent h2 { color: #dc2626; border-color: #dc2626; }
  .section-action h2 { color: #ea580c; border-color: #ea580c; }
  .section-fyi h2 { color: #2563eb; border-color: #2563eb; }
  .section-low h2 { color: #16a34a; border-color: #16a34a; }
  .email-card { background: #fafafa; border-radius: 8px; padding: 14px 16px; margin-bottom: 12px; border-left: 4px solid #ddd; }
  .section-urgent .email-card { border-left-color: #dc2626; }
  .section-action .email-card { border-left-color: #ea580c; }
  .section-fyi .email-card { border-left-color: #2563eb; }
  .section-low .email-card { border-left-color: #16a34a; }
  .email-subject { font-weight: 600; font-size: 14px; margin-bottom: 4px; }
  .email-from { font-size: 12px; color: #888; margin-bottom: 6px; }
  .email-summary { font-size: 13px; color: #555; line-height: 1.5; }
  .email-actions { margin-top: 8px; font-size: 12px; }
  .email-actions li { color: #6366f1; margin-bottom: 2px; }
  .draft-reply { background: #f0f0ff; border-radius: 6px; padding: 10px 12px; margin-top: 8px; font-size: 13px; color: #444; border-left: 3px solid #6366f1; }
  .draft-label { font-size: 11px; text-transform: uppercase; color: #6366f1; font-weight: 600; margin-bottom: 4px; }
  .footer { text-align: center; padding: 20px 32px; font-size: 12px; color: #aaa; border-top: 1px solid #eee; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; }
  .badge-unread { background: #dbeafe; color: #1d4ed8; }
  .badge-attachment { background: #fef3c7; color: #92400e; }
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>Forge Daily Digest</h1>
    <div class="subtitle">{{ timestamp }} &middot; {{ total_emails }} emails scanned &middot; {{ lookback_hours }}h window</div>
  </div>

  <div class="summary">{{ executive_summary | replace('\\n', '<br>') }}</div>

  <div class="stats">
    <div class="stat stat-urgent"><div class="num">{{ counts.urgent }}</div><div class="label">Urgent</div></div>
    <div class="stat stat-action"><div class="num">{{ counts.action_required }}</div><div class="label">Action</div></div>
    <div class="stat stat-fyi"><div class="num">{{ counts.fyi }}</div><div class="label">FYI</div></div>
    <div class="stat stat-low"><div class="num">{{ counts.low_priority }}</div><div class="label">Low</div></div>
  </div>

  {% for section_key, section_label in [('urgent', 'Urgent'), ('action_required', 'Action Required'), ('fyi', 'FYI'), ('low_priority', 'Low Priority')] %}
  {% if sections[section_key] %}
  <div class="section section-{{ section_key.replace('_', '-') }}">
    <h2>{{ section_label }} ({{ sections[section_key] | length }})</h2>
    {% for item in sections[section_key] %}
    <div class="email-card">
      <div class="email-subject">
        {{ item.email.subject }}
        {% if not item.email.is_read %}<span class="badge badge-unread">UNREAD</span>{% endif %}
        {% if item.email.has_attachments %}<span class="badge badge-attachment">ATTACHMENT</span>{% endif %}
      </div>
      <div class="email-from">From: {{ item.email.from_name or item.email.from }} &middot; {{ item.email.received[:16] }}</div>
      <div class="email-summary">{{ item.triage.summary }}</div>
      {% if item.triage.action_items %}
      <ul class="email-actions">
        {% for action in item.triage.action_items %}
        <li>{{ action }}</li>
        {% endfor %}
      </ul>
      {% endif %}
      {% if item.triage.draft_reply %}
      <div class="draft-reply">
        <div class="draft-label">Draft Reply</div>
        {{ item.triage.draft_reply }}
      </div>
      {% endif %}
    </div>
    {% endfor %}
  </div>
  {% endif %}
  {% endfor %}

  <div class="footer">
    Powered by Forge &middot; Your Personal AI Assistant<br>
    Triaged with {{ model_name }} &middot; Delivered via Microsoft Graph
  </div>
</div>
</body>
</html>
""")


class DigestBuilder:
    """Orchestrates the full digest pipeline: fetch → triage → build → send."""

    def __init__(self, demo: bool = False) -> None:
        self.demo = demo
        if not demo:
            self.outlook = OutlookClient()
        self.llm = LLMClient()

    def build(self) -> dict[str, Any]:
        """Run the full pipeline and return digest data + HTML."""
        # 1. Fetch emails (or use mock data in demo mode)
        if self.demo:
            print("  [DEMO MODE] Using realistic mock emails...")
            emails = MOCK_EMAILS
        else:
            print("  Fetching emails from Outlook...")
            emails = self.outlook.fetch_recent_emails()
        print(f"  Found {len(emails)} emails in the last {cfg.LOOKBACK_HOURS}h")

        if not emails:
            return {"html": "<p>No emails found in the lookback window.</p>", "data": {}}

        # 2. Triage with LLM
        print(f"  Triaging emails with {cfg.LLM_MODEL}...")
        triaged = self.llm.triage_batch(emails)
        print(f"  Triaged {len(triaged)} emails")

        # 2b. Apply severity engine (tone + recurrence adjustments)
        print("  Applying severity analysis (tone, recurrence, escalation)...")
        triaged = apply_severity(triaged)
        escalated = sum(1 for t in triaged if t["triage"].get("severity_factors"))
        if escalated:
            print(f"  Severity engine escalated {escalated} email(s)")

        # 3. Categorize
        sections: dict[str, list] = {
            "urgent": [],
            "action_required": [],
            "fyi": [],
            "low_priority": [],
        }
        for item in triaged:
            cat = item["triage"].get("category", "low_priority")
            if cat in sections:
                sections[cat].append(item)
            else:
                sections["low_priority"].append(item)

        counts = {k: len(v) for k, v in sections.items()}

        # 4. Generate executive summary
        print("  Generating executive summary...")
        exec_summary = self.llm.generate_digest_summary(triaged)

        # 5. Render HTML
        now = datetime.now(timezone.utc).strftime("%A, %B %d %Y at %H:%M UTC")
        html = DIGEST_TEMPLATE.render(
            timestamp=now,
            total_emails=len(emails),
            lookback_hours=cfg.LOOKBACK_HOURS,
            executive_summary=exec_summary,
            counts=counts,
            sections=sections,
            model_name=cfg.LLM_MODEL,
        )

        return {
            "html": html,
            "data": {
                "total": len(emails),
                "counts": counts,
                "executive_summary": exec_summary,
                "triaged": triaged,
            },
        }

    def send_digest(self, html: str) -> None:
        """Send the digest email to self (skipped in demo mode)."""
        if self.demo:
            print("  [DEMO MODE] Skipping email send — open the HTML file instead.")
            return
        subject = f"Forge Daily Digest — {datetime.now(timezone.utc).strftime('%b %d, %Y')}"
        print(f"  Sending digest to {cfg.MY_EMAIL}...")
        self.outlook.send_email(
            to=cfg.MY_EMAIL,
            subject=subject,
            html_body=html,
        )
        print("  Digest sent!")
