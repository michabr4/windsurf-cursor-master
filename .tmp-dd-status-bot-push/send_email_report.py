#!/usr/bin/env python3
"""
Send Digitized Delivery status report as a rich HTML email via Outlook.
Usage: python send_email_report.py [recipient_email]
"""

import json
import os
import subprocess
import sys
from datetime import datetime


def load_spacelift():
    """Load SpaceLift analysis JSON if available."""
    for path in ["spacelift_analysis.json", os.path.expanduser("~/Downloads/spacelift-export-2026-04-13.json")]:
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
    return None


def load_recordings():
    """Load recordings analysis JSON if available."""
    if os.path.exists("recordings_analysis.json"):
        with open("recordings_analysis.json", "r") as f:
            return json.load(f)
    return None


def build_html_report(spacelift=None, recordings=None):
    """Build a rich HTML email report with infographic styling."""
    today = datetime.now().strftime("%B %d, %Y")
    time_now = datetime.now().strftime("%I:%M %p EST")

    # Pull dynamic data if available
    total_messages = 0
    total_spaces = 0
    total_participants = 0
    total_personal_refs = 0
    spaces_list = []
    ai_updates = []
    ai_actions = []
    ai_risks = []
    ai_decisions = []
    ai_next_steps = []

    if spacelift:
        total_messages = spacelift.get("total_messages_analyzed", 55)
        total_spaces = len(spacelift.get("spaces_monitored", []))
        total_participants = spacelift.get("participants_tracked", 235)
        total_personal_refs = spacelift.get("total_personal_refs", 28)
        spaces_list = [s.get("title", "") for s in spacelift.get("spaces_monitored", [])]
        analysis = spacelift.get("analysis", {})
        ai_updates = analysis.get("updates", [])
        ai_actions = analysis.get("action_items", [])
        ai_risks = analysis.get("risks", [])
        ai_decisions = analysis.get("decisions", [])
        ai_next_steps = analysis.get("next_steps", [])
    else:
        total_messages = 55
        total_spaces = 7
        total_participants = 235
        total_personal_refs = 28
        spaces_list = [
            "GES Digitized Delivery | Core Team",
            "MGM Digitized Delivery - ISE as Code Adoption",
            "Digitized Delivery - GES Leader Space",
            "GES Digitized Delivery",
            "PS Digitized Delivery Learning Path Stakeholders",
        ]

    # Recordings data
    rec_count = 0
    rec_items = []
    if recordings:
        rec_items = recordings.get("meetings_analyzed", [])
        rec_count = len(rec_items)

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background: #f4f5f7; color: #333; }}
  .container {{ max-width: 800px; margin: 0 auto; background: #fff; }}
  .header {{ background: linear-gradient(135deg, #00bceb 0%, #005073 100%); padding: 30px 40px; color: white; }}
  .header h1 {{ margin: 0 0 5px 0; font-size: 26px; font-weight: 600; }}
  .header .subtitle {{ opacity: 0.9; font-size: 14px; }}
  .header .status-badge {{ display: inline-block; background: rgba(255,255,255,0.2); padding: 4px 14px; border-radius: 20px; font-size: 13px; margin-top: 10px; }}

  .metrics-bar {{ display: flex; background: #f8f9fb; border-bottom: 1px solid #e5e7eb; }}
  .metric {{ flex: 1; text-align: center; padding: 18px 10px; border-right: 1px solid #e5e7eb; }}
  .metric:last-child {{ border-right: none; }}
  .metric .number {{ font-size: 28px; font-weight: 700; color: #005073; }}
  .metric .label {{ font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 2px; }}

  .section {{ padding: 25px 40px; }}
  .section h2 {{ font-size: 18px; color: #005073; border-bottom: 2px solid #00bceb; padding-bottom: 8px; margin-top: 0; }}
  .section h3 {{ font-size: 15px; color: #333; margin: 15px 0 8px 0; }}

  table {{ width: 100%; border-collapse: collapse; font-size: 13px; margin: 10px 0; }}
  th {{ background: #005073; color: white; padding: 10px 12px; text-align: left; font-weight: 500; }}
  td {{ padding: 10px 12px; border-bottom: 1px solid #eee; }}
  tr:nth-child(even) {{ background: #f8f9fb; }}

  .status-green {{ color: #0d9e3f; font-weight: 600; }}
  .status-yellow {{ color: #d4a017; font-weight: 600; }}
  .status-red {{ color: #d43317; font-weight: 600; }}

  .priority-high {{ background: #fee2e2; color: #991b1b; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; }}
  .priority-med {{ background: #fef3c7; color: #92400e; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; }}
  .priority-low {{ background: #d1fae5; color: #065f46; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; }}

  .risk-badge {{ display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; }}
  .risk-med {{ background: #fef3c7; color: #92400e; }}
  .risk-low {{ background: #d1fae5; color: #065f46; }}

  .timeline {{ padding: 0 0 0 20px; }}
  .timeline-item {{ position: relative; padding: 8px 0 8px 25px; border-left: 3px solid #e5e7eb; font-size: 13px; }}
  .timeline-item.done {{ border-left-color: #0d9e3f; }}
  .timeline-item.active {{ border-left-color: #d4a017; }}
  .timeline-item.target {{ border-left-color: #d43317; }}
  .timeline-item .dot {{ position: absolute; left: -8px; top: 12px; width: 13px; height: 13px; border-radius: 50%; border: 2px solid #fff; }}
  .timeline-item.done .dot {{ background: #0d9e3f; }}
  .timeline-item.active .dot {{ background: #d4a017; }}
  .timeline-item.target .dot {{ background: #d43317; }}
  .timeline-item.deferred .dot {{ background: #9ca3af; }}
  .timeline-item.deferred {{ border-left-color: #9ca3af; }}
  .timeline-label {{ font-size: 11px; color: #888; font-weight: 600; text-transform: uppercase; }}

  .contact-card {{ display: inline-block; background: #f8f9fb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 10px 15px; margin: 5px; font-size: 12px; min-width: 180px; }}
  .contact-card .name {{ font-weight: 600; color: #005073; font-size: 13px; }}
  .contact-card .role {{ color: #888; font-size: 11px; }}
  .contact-card .email {{ color: #00bceb; font-size: 11px; }}

  .footer {{ background: #f4f5f7; padding: 20px 40px; text-align: center; font-size: 11px; color: #999; border-top: 1px solid #e5e7eb; }}
  .footer a {{ color: #00bceb; text-decoration: none; }}

  .ai-tag {{ display: inline-block; background: #ede9fe; color: #5b21b6; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: 600; margin-left: 5px; }}
  .list-item {{ padding: 6px 0; border-bottom: 1px solid #f3f4f6; font-size: 13px; }}
  .list-item:last-child {{ border-bottom: none; }}

  .spaces-tag {{ display: inline-block; background: #e0f2fe; color: #0369a1; padding: 3px 10px; border-radius: 12px; font-size: 11px; margin: 3px; }}
</style>
</head>
<body>
<div class="container">

  <!-- HEADER -->
  <div class="header">
    <h1>&#128202; Digitized Delivery</h1>
    <div class="subtitle">Consolidated Status Report &mdash; {today} at {time_now}</div>
    <div class="status-badge">&#9679; Overall: YELLOW &mdash; On Track with Risks</div>
  </div>

  <!-- METRICS BAR -->
  <div class="metrics-bar">
    <div class="metric">
      <div class="number">{total_messages}</div>
      <div class="label">Messages Analyzed</div>
    </div>
    <div class="metric">
      <div class="number">{total_spaces}</div>
      <div class="label">Spaces Monitored</div>
    </div>
    <div class="metric">
      <div class="number">{total_participants}</div>
      <div class="label">Participants</div>
    </div>
    <div class="metric">
      <div class="number">{total_personal_refs}</div>
      <div class="label">DD References</div>
    </div>
  </div>

  <!-- EXECUTIVE SUMMARY -->
  <div class="section">
    <h2>&#127919; Executive Summary</h2>
    <table>
      <tr><th>Workstream</th><th>Status</th><th>Owner</th></tr>
      <tr>
        <td><strong>ISE as Code (ISAAC) &mdash; MGM</strong></td>
        <td><span class="status-green">&#9679; Lab 90% complete, cert renewal done</span></td>
        <td>Rakesh / Chetankumar</td>
      </tr>
      <tr>
        <td><strong>NAC Parity</strong></td>
        <td><span class="status-yellow">&#9679; Cat-C &amp; SDWAN data collection</span></td>
        <td>Dhrumil Prajapati</td>
      </tr>
      <tr>
        <td><strong>Digital Document Automation</strong></td>
        <td><span class="status-yellow">&#9679; Template reviews in progress</span></td>
        <td>Dhrumil Prajapati</td>
      </tr>
      <tr>
        <td><strong>AI-Assisted Development</strong></td>
        <td><span class="status-green">&#9679; OpenCode + Copilot rollout</span></td>
        <td>Dhrumil Prajapati</td>
      </tr>
      <tr>
        <td><strong>GES Engagement Tracking</strong></td>
        <td><span class="status-yellow">&#9679; Power BI dashboard build-out</span></td>
        <td>Mike Brown</td>
      </tr>
    </table>
  </div>

  <!-- RECOMMENDED NEXT STEPS -->
  <div class="section" style="background: #f8f9fb;">
    <h2>&#9989; Recommended Next Steps</h2>
    <table>
      <tr><th>#</th><th>Priority</th><th>Action</th><th>Target</th><th>Owner</th></tr>
      <tr>
        <td>1</td>
        <td><span class="priority-high">HIGH</span></td>
        <td>Complete ISAAC lab install &amp; resolve remaining infra issues</td>
        <td>This week</td>
        <td>Chetankumar / Raphael</td>
      </tr>
      <tr>
        <td>2</td>
        <td><span class="priority-high">HIGH</span></td>
        <td>Setup YAML files for ISE PROD &amp; begin observability playbooks</td>
        <td>Next 2 wks</td>
        <td>Rakesh / Chetankumar</td>
      </tr>
      <tr>
        <td>3</td>
        <td><span class="priority-high">HIGH</span></td>
        <td>Prepare ISAAC TOI for Darrin &amp; MGM team (patch upgrade demo)</td>
        <td>Before prod</td>
        <td>Rakesh</td>
      </tr>
      <tr>
        <td>4</td>
        <td><span class="priority-high">HIGH</span></td>
        <td>Resolve credential management (Ansible Vault vs AAP Survey)</td>
        <td>This week</td>
        <td>Chetankumar / Raphael</td>
      </tr>
      <tr>
        <td>5</td>
        <td><span class="priority-med">MED</span></td>
        <td>Complete DDA template reviews with volunteers</td>
        <td>This week</td>
        <td>Dhrumil / GES Core Team</td>
      </tr>
      <tr>
        <td>6</td>
        <td><span class="priority-med">MED</span></td>
        <td>Continue NAC Parity data collection (Cat-C &amp; SDWAN)</td>
        <td>Ongoing</td>
        <td>Dhrumil</td>
      </tr>
      <tr>
        <td>7</td>
        <td><span class="priority-med">MED</span></td>
        <td>Share GES engagement tracker with leadership</td>
        <td>This week</td>
        <td>Mike Brown</td>
      </tr>
      <tr>
        <td>8</td>
        <td><span class="priority-low">LOW</span></td>
        <td>Engage MGM virtualization team for vSphere API access</td>
        <td>Next sprint</td>
        <td>Rakesh</td>
      </tr>
    </table>
  </div>

  <!-- RISK REGISTER -->
  <div class="section">
    <h2>&#9888;&#65039; Risk Register</h2>
    <table>
      <tr><th>ID</th><th>Severity</th><th>Risk</th><th>Mitigation</th><th>Owner</th></tr>
      <tr>
        <td>R1</td>
        <td><span class="risk-badge risk-med">MEDIUM</span></td>
        <td>MGM hesitant on ISAAC prod patch &mdash; Darrin wants lab demo first</td>
        <td>Full lab demo + TOI before any prod changes</td>
        <td>Rakesh</td>
      </tr>
      <tr>
        <td>R2</td>
        <td><span class="risk-badge risk-med">MEDIUM</span></td>
        <td>Credential mgmt &mdash; Ansible Vault may not work for MGM infra</td>
        <td>Exploring AAP Survey method as alternative</td>
        <td>Chetankumar</td>
      </tr>
      <tr>
        <td>R3</td>
        <td><span class="risk-badge risk-med">MEDIUM</span></td>
        <td>vSphere API access blocked &mdash; needs MGM virtualization team</td>
        <td>Deferred; not blocking current milestones</td>
        <td>Rakesh</td>
      </tr>
      <tr>
        <td>R4</td>
        <td><span class="risk-badge risk-low">LOW</span></td>
        <td>GES engagement data incomplete in Power BI</td>
        <td>Data collection in progress</td>
        <td>Mike Brown</td>
      </tr>
      <tr>
        <td>R5</td>
        <td><span class="risk-badge risk-low">LOW</span></td>
        <td>DDA template review needs more volunteers</td>
        <td>Soliciting from GES Core Team</td>
        <td>Dhrumil</td>
      </tr>
    </table>
  </div>

  <!-- TIMELINE -->
  <div class="section" style="background: #f8f9fb;">
    <h2>&#128197; Timeline &amp; Milestones</h2>
    <div class="timeline">
      <div class="timeline-item done">
        <div class="dot"></div>
        <span class="timeline-label">Completed</span><br>
        ISAAC lab: 6 nodes up, cert renewal done &#10003;
      </div>
      <div class="timeline-item done">
        <div class="dot"></div>
        <span class="timeline-label">Completed</span><br>
        OpenCode + Copilot strategy adopted &#10003;
      </div>
      <div class="timeline-item done">
        <div class="dot"></div>
        <span class="timeline-label">Completed</span><br>
        NAC Parity data collection form live &#10003;
      </div>
      <div class="timeline-item active">
        <div class="dot"></div>
        <span class="timeline-label">This Week</span><br>
        ISAAC: Resolve remaining lab infra issues
      </div>
      <div class="timeline-item active">
        <div class="dot"></div>
        <span class="timeline-label">This Week</span><br>
        DDA: Complete template reviews
      </div>
      <div class="timeline-item active">
        <div class="dot"></div>
        <span class="timeline-label">Next 2 Weeks</span><br>
        ISAAC: PROD YAML setup + observability playbooks
      </div>
      <div class="timeline-item active">
        <div class="dot"></div>
        <span class="timeline-label">Next 2 Weeks</span><br>
        ISAAC: TOI for Darrin &amp; MGM team
      </div>
      <div class="timeline-item target">
        <div class="dot"></div>
        <span class="timeline-label">3 Weeks &mdash; Target</span><br>
        <strong>&#127919; ISAAC Patch 10 upgrade in PROD</strong>
      </div>
      <div class="timeline-item deferred">
        <div class="dot"></div>
        <span class="timeline-label">TBD</span><br>
        vSphere API access (deferred)
      </div>
    </div>
  </div>
"""

    # AI-detected sections (if available)
    if ai_updates or ai_actions or ai_risks or ai_decisions or ai_next_steps:
        html += """  <div class="section">
    <h2>&#129302; AI-Detected Insights <span class="ai-tag">GPT-4 Analysis</span></h2>
"""
        if ai_updates:
            html += "    <h3>Key Updates</h3>\n"
            for u in ai_updates[:6]:
                html += f'    <div class="list-item">&#8226; {u}</div>\n'

        if ai_actions:
            html += "    <h3>Action Items</h3>\n"
            for a in ai_actions[:6]:
                html += f'    <div class="list-item">&#9744; {a}</div>\n'

        if ai_risks:
            html += "    <h3>Risks &amp; Concerns</h3>\n"
            for r in ai_risks[:5]:
                html += f'    <div class="list-item">&#9888; {r}</div>\n'

        if ai_decisions:
            html += "    <h3>Decisions Made</h3>\n"
            for d in ai_decisions[:5]:
                html += f'    <div class="list-item">&#10004; {d}</div>\n'

        if ai_next_steps:
            html += "    <h3>Next Steps</h3>\n"
            for s in ai_next_steps[:5]:
                html += f'    <div class="list-item">&#10132; {s}</div>\n'

        html += "  </div>\n"

    # Spaces monitored
    html += """  <div class="section" style="background: #f8f9fb;">
    <h2>&#128225; Spaces Monitored</h2>
    <div>
"""
    for space in spaces_list:
        html += f'      <span class="spaces-tag">{space}</span>\n'
    html += """    </div>
  </div>
"""

    # Key Contacts
    html += """  <div class="section">
    <h2>&#128101; Key Contacts</h2>
    <table>
      <tr><th>Role</th><th>Name</th><th>Email</th><th>Focus</th></tr>
      <tr><td>Program Management Lead</td><td><strong>Mike Brown</strong></td><td><a href="mailto:michabr4@cisco.com">michabr4@cisco.com</a></td><td>Overall coordination &amp; GES tracking</td></tr>
      <tr><td>Technical Lead</td><td><strong>Dhrumil Prajapati</strong></td><td><a href="mailto:dhprajap@cisco.com">dhprajap@cisco.com</a></td><td>DD strategy, NAC Parity, DDA</td></tr>
      <tr><td>ISAAC / ISE Lead</td><td><strong>Rakesh</strong></td><td><a href="mailto:ragade@cisco.com">ragade@cisco.com</a></td><td>ISE as Code, MGM coordination</td></tr>
      <tr><td>ISAAC Engineering</td><td><strong>Chetankumar Phulpagare</strong></td><td><a href="mailto:cphulpag@cisco.com">cphulpag@cisco.com</a></td><td>ISAAC playbooks &amp; automation</td></tr>
      <tr><td>ISAAC Engineering</td><td><strong>Raphael Moreno</strong></td><td><a href="mailto:rmorenot@cisco.com">rmorenot@cisco.com</a></td><td>Troubleshooting &amp; cert automation</td></tr>
      <tr><td>ISE Support</td><td><strong>Liliana (Karen)</strong></td><td><a href="mailto:karenmar@cisco.com">karenmar@cisco.com</a></td><td>ISE cert &amp; access coordination</td></tr>
      <tr><td>ISAAC Support</td><td><strong>Shirley Puente</strong></td><td><a href="mailto:shpuente@cisco.com">shpuente@cisco.com</a></td><td>ISAAC team coordination</td></tr>
      <tr><td>ISAAC Engineering</td><td><strong>Stuart Malone</strong></td><td><a href="mailto:stumalon@cisco.com">stumalon@cisco.com</a></td><td>Documentation &amp; file sharing</td></tr>
      <tr><td>GES Leader</td><td><strong>Nakia Stringfield</strong></td><td><a href="mailto:nstringf@cisco.com">nstringf@cisco.com</a></td><td>GES leadership</td></tr>
      <tr><td>GES Leader</td><td><strong>Michael Shomake</strong></td><td><a href="mailto:mshomake@cisco.com">mshomake@cisco.com</a></td><td>GES data &amp; Power BI</td></tr>
    </table>
  </div>

  <!-- FOOTER -->
  <div class="footer">
    <p>&#128640; Auto-generated by Digitized Delivery Status Bot &mdash; Webex SpaceLift + Recordings Analysis</p>
    <p>Contact: <a href="mailto:michabr4@cisco.com">michabr4@cisco.com</a></p>
  </div>

</div>
</body>
</html>"""

    return html


def send_via_outlook(to_email, subject, html_body):
    """Send HTML email via Outlook by creating an .eml file and opening it."""
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    # Build a proper MIME email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = "michabr4@cisco.com"
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    eml_path = "/tmp/dd_status_report.eml"
    with open(eml_path, "w") as f:
        f.write(msg.as_string())

    print(f"📄 Email saved to {eml_path}")

    # Open the .eml in Outlook — it will appear as a compose window
    result = subprocess.run(["open", "-a", "Microsoft Outlook", eml_path], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"� Email opened in Outlook for {to_email} — click Send to deliver")
        print("   (The .eml opens as a ready-to-send message)")
        return True
    else:
        print(f"⚠️ Could not open in Outlook: {result.stderr}")
        # Fallback: open in browser
        html_path = os.path.expanduser("~/Desktop/dd_status_report.html")
        with open(html_path, "w") as f:
            f.write(html_body)
        print(f"📄 HTML report saved to {html_path}")
        subprocess.run(["open", html_path])
        return False


def main():
    recipient = sys.argv[1] if len(sys.argv) > 1 else "michabr4@cisco.com"
    today = datetime.now().strftime("%B %d, %Y")

    print(f"📊 Building DD HTML email report...")
    spacelift = load_spacelift()
    recordings = load_recordings()
    html = build_html_report(spacelift, recordings)

    subject = f"Digitized Delivery - Status Report - {today}"
    print(f"📧 Sending to {recipient} via Outlook...")
    send_via_outlook(recipient, subject, html)


if __name__ == "__main__":
    main()
