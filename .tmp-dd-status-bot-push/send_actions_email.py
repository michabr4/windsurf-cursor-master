#!/usr/bin/env python3
"""
Generate an HTML email summarizing all Digitized Delivery actions
from the last 60 days based on SpaceLift export data.
"""

import subprocess
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

def build_html():
    now = datetime.now().strftime("%B %d, %Y")
    return f"""\
<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f4f6f8;font-family:'Segoe UI',Helvetica,Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6f8;padding:24px 0;">
<tr><td align="center">
<table width="680" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.08);">

  <!-- Header -->
  <tr><td style="background:linear-gradient(135deg,#049fd9,#6a5acd);padding:28px 32px;">
    <h1 style="margin:0;color:#fff;font-size:22px;font-weight:700;">Digitized Delivery — 60-Day Action Summary</h1>
    <p style="margin:6px 0 0;color:rgba(255,255,255,.85);font-size:13px;">Compiled {now} &bull; Sources: GES Core Team &bull; ISE as Code Adoption &bull; GES Leader Space</p>
  </td></tr>

  <!-- Executive Summary -->
  <tr><td style="padding:24px 32px 0;">
    <h2 style="margin:0 0 8px;font-size:16px;color:#049fd9;border-bottom:2px solid #049fd9;padding-bottom:6px;">Executive Summary</h2>
    <p style="font-size:14px;line-height:1.6;color:#333;margin:8px 0 0;">
      Over the past 60 days, the Digitized Delivery program has driven significant progress across three workstreams:
      <strong>ISE as Code (ISAAC) adoption at MGM</strong>, <strong>GES tooling &amp; process alignment</strong>, and
      <strong>cross-GES leadership coordination</strong>. The ISE as Code lab is now fully operational with all 6 nodes
      running, certificate automation validated, and patch upgrade workflows proven. The team is preparing for the
      first production ISE patch upgrade using ISAAC automation.
    </p>
  </td></tr>

  <!-- KPI strip -->
  <tr><td style="padding:20px 32px 0;">
    <table width="100%" cellpadding="0" cellspacing="0">
      <tr>
        <td width="25%" style="text-align:center;padding:12px;background:#f0f9ff;border-radius:8px;">
          <div style="font-size:28px;font-weight:700;color:#049fd9;">6/6</div>
          <div style="font-size:11px;color:#666;margin-top:2px;">ISE Nodes Live</div>
        </td>
        <td width="4%"></td>
        <td width="25%" style="text-align:center;padding:12px;background:#f0fff4;border-radius:8px;">
          <div style="font-size:28px;font-weight:700;color:#22c55e;">&#10003;</div>
          <div style="font-size:11px;color:#666;margin-top:2px;">Cert Automation</div>
        </td>
        <td width="4%"></td>
        <td width="25%" style="text-align:center;padding:12px;background:#fff7ed;border-radius:8px;">
          <div style="font-size:28px;font-weight:700;color:#f59e0b;">3</div>
          <div style="font-size:11px;color:#666;margin-top:2px;">Open Blockers</div>
        </td>
        <td width="4%"></td>
        <td width="25%" style="text-align:center;padding:12px;background:#fdf2f8;border-radius:8px;">
          <div style="font-size:28px;font-weight:700;color:#6a5acd;">14</div>
          <div style="font-size:11px;color:#666;margin-top:2px;">Actions Tracked</div>
        </td>
      </tr>
    </table>
  </td></tr>

  <!-- ISE as Code Actions -->
  <tr><td style="padding:24px 32px 0;">
    <h2 style="margin:0 0 10px;font-size:16px;color:#049fd9;border-bottom:2px solid #049fd9;padding-bottom:6px;">ISE as Code (ISAAC) — MGM Adoption</h2>
    <table width="100%" cellpadding="8" cellspacing="0" style="font-size:13px;border-collapse:collapse;">
      <tr style="background:#f8fafc;">
        <th align="left" style="padding:8px;color:#333;border-bottom:1px solid #e2e8f0;width:15%;">Date</th>
        <th align="left" style="padding:8px;color:#333;border-bottom:1px solid #e2e8f0;width:15%;">Status</th>
        <th align="left" style="padding:8px;color:#333;border-bottom:1px solid #e2e8f0;">Action / Milestone</th>
      </tr>
      <tr>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;color:#666;">Mar 5</td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;"><span style="background:#dcfce7;color:#166534;padding:2px 8px;border-radius:4px;font-size:11px;">Complete</span></td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;">Custom execution environment setup; DNS resolution for ISE nodes resolved</td>
      </tr>
      <tr>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;color:#666;">Mar 13</td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;"><span style="background:#dcfce7;color:#166534;padding:2px 8px;border-radius:4px;font-size:11px;">Complete</span></td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;">ISE as Code ZIP and Ops Guide uploaded to SharePoint for MGM access</td>
      </tr>
      <tr>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;color:#666;">Mar 18</td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;"><span style="background:#dcfce7;color:#166534;padding:2px 8px;border-radius:4px;font-size:11px;">Complete</span></td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;">All 6 ISE lab nodes set up via ISAAC automation; YAML validation initiated</td>
      </tr>
      <tr>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;color:#666;">Mar 20</td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;"><span style="background:#dcfce7;color:#166534;padding:2px 8px;border-radius:4px;font-size:11px;">Complete</span></td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;">CCO ID provisioning for Naga (MGM) to access Cisco download portal</td>
      </tr>
      <tr>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;color:#666;">Mar 27</td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;"><span style="background:#fef3c7;color:#92400e;padding:2px 8px;border-radius:4px;font-size:11px;">In Progress</span></td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;">Certificate private key and cert file procurement for lab ISE nodes</td>
      </tr>
      <tr>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;color:#666;">Mar 30</td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;"><span style="background:#fef3c7;color:#92400e;padding:2px 8px;border-radius:4px;font-size:11px;">In Progress</span></td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;">Target: Use ISAAC for ISE Patch 10 upgrade in production — key milestones defined (cert deploy, YAML for prod, monitoring playbook, TOI for Darrin, Git branch/PR methodology)</td>
      </tr>
      <tr>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;color:#666;">Apr 9</td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;"><span style="background:#dcfce7;color:#166534;padding:2px 8px;border-radius:4px;font-size:11px;">Complete</span></td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;">Certificate playbook executed successfully across all 6 nodes (PSN05 issue resolved)</td>
      </tr>
      <tr>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;color:#666;">Apr 10</td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;"><span style="background:#dcfce7;color:#166534;padding:2px 8px;border-radius:4px;font-size:11px;">Complete</span></td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;">Lab fully operational: all 6 nodes up, AAP connected, patch update verified, cert rotation verified</td>
      </tr>
      <tr>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;color:#666;">Apr 10</td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;"><span style="background:#fef3c7;color:#92400e;padding:2px 8px;border-radius:4px;font-size:11px;">In Progress</span></td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;">Secure credential management: evaluating AAP Survey method as alternative to Ansible Vault for MGM</td>
      </tr>
      <tr>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;color:#666;">Apr 10</td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;"><span style="background:#fee2e2;color:#991b1b;padding:2px 8px;border-radius:4px;font-size:11px;">Pending</span></td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;">Operational / observability playbooks setup (only remaining lab item)</td>
      </tr>
      <tr>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;color:#666;">Apr 10</td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;"><span style="background:#fee2e2;color:#991b1b;padding:2px 8px;border-radius:4px;font-size:11px;">Pending</span></td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;">vSphere API access — requires coordination with MGM virtualization team</td>
      </tr>
    </table>
  </td></tr>

  <!-- ISAAC Prod Readiness Plan -->
  <tr><td style="padding:20px 32px 0;">
    <h3 style="margin:0 0 8px;font-size:14px;color:#6a5acd;">Production Readiness Plan (ISE Patch Upgrade via ISAAC)</h3>
    <table width="100%" cellpadding="6" cellspacing="0" style="font-size:13px;border-collapse:collapse;background:#f8f5ff;border-radius:8px;">
      <tr><td style="padding:8px 12px;border-bottom:1px solid #ede9fe;">1. Complete lab install and repeat patch update in lab</td><td style="width:90px;text-align:center;"><span style="background:#dcfce7;color:#166534;padding:2px 8px;border-radius:4px;font-size:11px;">Done</span></td></tr>
      <tr><td style="padding:8px 12px;border-bottom:1px solid #ede9fe;">2. Set up YAML files representing production environment</td><td style="text-align:center;"><span style="background:#fef3c7;color:#92400e;padding:2px 8px;border-radius:4px;font-size:11px;">Next</span></td></tr>
      <tr><td style="padding:8px 12px;border-bottom:1px solid #ede9fe;">3. Deploy operational / observability monitoring playbook for prod</td><td style="text-align:center;"><span style="background:#fee2e2;color:#991b1b;padding:2px 8px;border-radius:4px;font-size:11px;">Pending</span></td></tr>
      <tr><td style="padding:8px 12px;border-bottom:1px solid #ede9fe;">4. TOI for Darrin: rolling update process, validations, safeguards</td><td style="text-align:center;"><span style="background:#fee2e2;color:#991b1b;padding:2px 8px;border-radius:4px;font-size:11px;">Pending</span></td></tr>
      <tr><td style="padding:8px 12px;border-bottom:1px solid #ede9fe;">5. Train MGM team on Git branches &amp; PR approval workflow</td><td style="text-align:center;"><span style="background:#fee2e2;color:#991b1b;padding:2px 8px;border-radius:4px;font-size:11px;">Pending</span></td></tr>
      <tr><td style="padding:8px 12px;border-bottom:1px solid #ede9fe;">6. Prod: run patch automation on TACACS nodes first, then RADIUS</td><td style="text-align:center;"><span style="background:#fee2e2;color:#991b1b;padding:2px 8px;border-radius:4px;font-size:11px;">Pending</span></td></tr>
    </table>
  </td></tr>

  <!-- GES Core Team Actions -->
  <tr><td style="padding:24px 32px 0;">
    <h2 style="margin:0 0 10px;font-size:16px;color:#049fd9;border-bottom:2px solid #049fd9;padding-bottom:6px;">GES Digitized Delivery — Core Team</h2>
    <table width="100%" cellpadding="8" cellspacing="0" style="font-size:13px;border-collapse:collapse;">
      <tr style="background:#f8fafc;">
        <th align="left" style="padding:8px;color:#333;border-bottom:1px solid #e2e8f0;width:15%;">Date</th>
        <th align="left" style="padding:8px;color:#333;border-bottom:1px solid #e2e8f0;width:15%;">Status</th>
        <th align="left" style="padding:8px;color:#333;border-bottom:1px solid #e2e8f0;">Action / Milestone</th>
      </tr>
      <tr>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;color:#666;">Mar 2</td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;"><span style="background:#dcfce7;color:#166534;padding:2px 8px;border-radius:4px;font-size:11px;">Complete</span></td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;">AI tooling strategy adopted: OpenCode + GitHub Copilot as primary workflow to optimize entitlements</td>
      </tr>
      <tr>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;color:#666;">Mar 16</td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;"><span style="background:#dcfce7;color:#166534;padding:2px 8px;border-radius:4px;font-size:11px;">Complete</span></td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;">NAC-Parity GitHub repository shared with the team</td>
      </tr>
      <tr>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;color:#666;">Mar 19</td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;"><span style="background:#dcfce7;color:#166534;padding:2px 8px;border-radius:4px;font-size:11px;">Complete</span></td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;">Weekly GES sync cadence confirmed as active</td>
      </tr>
      <tr>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;color:#666;">Mar 25</td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;"><span style="background:#fef3c7;color:#92400e;padding:2px 8px;border-radius:4px;font-size:11px;">In Progress</span></td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;">Digital Document Automation (DDA) template review — 2 volunteers assigned</td>
      </tr>
    </table>
  </td></tr>

  <!-- GES Leader Space Actions -->
  <tr><td style="padding:24px 32px 0;">
    <h2 style="margin:0 0 10px;font-size:16px;color:#049fd9;border-bottom:2px solid #049fd9;padding-bottom:6px;">GES Leader Space — Cross-Team Coordination</h2>
    <table width="100%" cellpadding="8" cellspacing="0" style="font-size:13px;border-collapse:collapse;">
      <tr style="background:#f8fafc;">
        <th align="left" style="padding:8px;color:#333;border-bottom:1px solid #e2e8f0;width:15%;">Date</th>
        <th align="left" style="padding:8px;color:#333;border-bottom:1px solid #e2e8f0;width:15%;">Status</th>
        <th align="left" style="padding:8px;color:#333;border-bottom:1px solid #e2e8f0;">Action / Milestone</th>
      </tr>
      <tr>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;color:#666;">Mar 11</td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;"><span style="background:#dcfce7;color:#166534;padding:2px 8px;border-radius:4px;font-size:11px;">Complete</span></td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;">Power BI dashboard shared; tool read-access invites sent to leadership</td>
      </tr>
      <tr>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;color:#666;">Mar 11</td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;"><span style="background:#fef3c7;color:#92400e;padding:2px 8px;border-radius:4px;font-size:11px;">In Progress</span></td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;">GES data collection and Power BI data pipeline assessment to identify team focus areas</td>
      </tr>
      <tr>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;color:#666;">Mar 25</td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;"><span style="background:#dcfce7;color:#166534;padding:2px 8px;border-radius:4px;font-size:11px;">Complete</span></td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;">NAC-Parity data collection form distributed to CDAs (Cat-C &amp; SD-WAN)</td>
      </tr>
      <tr>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;color:#666;">Apr 8</td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;"><span style="background:#fef3c7;color:#92400e;padding:2px 8px;border-radius:4px;font-size:11px;">In Progress</span></td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;">Share GES engagement tracker with leadership team</td>
      </tr>
    </table>
  </td></tr>

  <!-- Key Risks / Blockers -->
  <tr><td style="padding:24px 32px 0;">
    <h2 style="margin:0 0 10px;font-size:16px;color:#ef4444;border-bottom:2px solid #ef4444;padding-bottom:6px;">Open Risks &amp; Blockers</h2>
    <table width="100%" cellpadding="8" cellspacing="0" style="font-size:13px;border-collapse:collapse;">
      <tr>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;width:24px;vertical-align:top;color:#ef4444;font-weight:bold;">&#9679;</td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;"><strong>Darrin's comfort with ISAAC in production</strong> — wants lab validation before any prod use. Adoption will be gradual; TOI sessions are critical path.</td>
      </tr>
      <tr>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;width:24px;vertical-align:top;color:#f59e0b;font-weight:bold;">&#9679;</td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;"><strong>vSphere API access</strong> — requires MGM virtualization team coordination; deferred but needed for full automation.</td>
      </tr>
      <tr>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;width:24px;vertical-align:top;color:#f59e0b;font-weight:bold;">&#9679;</td>
        <td style="padding:8px;border-bottom:1px solid #f1f5f9;"><strong>Credential management</strong> — Ansible Vault may not work for MGM; AAP Survey method under evaluation.</td>
      </tr>
    </table>
  </td></tr>

  <!-- Next Steps -->
  <tr><td style="padding:24px 32px;">
    <h2 style="margin:0 0 10px;font-size:16px;color:#22c55e;border-bottom:2px solid #22c55e;padding-bottom:6px;">Recommended Next Steps</h2>
    <ol style="font-size:13px;line-height:1.8;color:#333;padding-left:20px;margin:8px 0 0;">
      <li>Set up operational/observability playbooks for ISAAC lab (last remaining lab gap)</li>
      <li>Begin YAML file preparation for ISE production environment</li>
      <li>Schedule expanded TOI sessions with Darrin covering rolling update process, validations, and safeguards</li>
      <li>Finalize secure credential strategy (AAP Survey vs. Ansible Vault)</li>
      <li>Coordinate vSphere API access with MGM virtualization team</li>
      <li>Complete DDA template review with assigned volunteers</li>
      <li>Distribute GES engagement tracker to leadership and confirm data collection pipeline</li>
      <li>Increase ISAAC cadence beyond 1 hour/week — Naga available for multiple sessions</li>
    </ol>
  </td></tr>

  <!-- Footer -->
  <tr><td style="background:#f8fafc;padding:16px 32px;border-top:1px solid #e2e8f0;">
    <p style="margin:0;font-size:11px;color:#999;text-align:center;">
      Generated from SpaceLift export (spacelift-export-2026-04-13.json) &bull; Digitized Delivery Status Bot &bull; {now}
    </p>
  </td></tr>

</table>
</td></tr>
</table>
</body>
</html>"""


def main():
    to_email = "michabr4@cisco.com"
    subject = "Digitized Delivery — 60-Day Action Summary (Feb 13 – Apr 13, 2026)"
    html_body = build_html()

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = "michabr4@cisco.com"
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    eml_path = "/tmp/dd_actions_summary.eml"
    with open(eml_path, "w") as f:
        f.write(msg.as_string())

    print(f"📄 Email saved to {eml_path}")

    result = subprocess.run(["open", "-a", "Microsoft Outlook", eml_path],
                            capture_output=True, text=True)
    if result.returncode == 0:
        print(f"📬 Email opened in Outlook for {to_email} — click Send to deliver")
    else:
        print(f"⚠️ Could not open in Outlook: {result.stderr}")
        html_path = os.path.expanduser("~/Desktop/dd_actions_summary.html")
        with open(html_path, "w") as f:
            f.write(html_body)
        print(f"📄 HTML fallback saved to {html_path}")
        subprocess.run(["open", html_path])


if __name__ == "__main__":
    main()
