"""
Digitized Delivery Status Report - GitHub Actions Script
Sends daily status reports to all subscribers via Webex.

Dynamically builds report from:
1. spacelift_analysis.json (SpaceLift message analysis)
2. Recording analysis (if available)
Falls back to a static template if no analysis data is present.
"""

import os
import json
import requests
from datetime import datetime

# Configuration
WEBEX_BOT_TOKEN = os.environ.get("WEBEX_BOT_TOKEN", "")
BASE_URL = "https://webexapis.com/v1"
SUBSCRIBERS_FILE = "subscribers.json"
SPACELIFT_FILE = "spacelift_analysis.json"

def load_subscribers():
    """Load subscribers from JSON file."""
    if os.path.exists(SUBSCRIBERS_FILE):
        with open(SUBSCRIBERS_FILE, "r") as f:
            return json.load(f)
    return {"emails": []}

def load_spacelift_analysis():
    """Load SpaceLift analysis results if available."""
    if os.path.exists(SPACELIFT_FILE):
        with open(SPACELIFT_FILE, "r") as f:
            return json.load(f)
    return None

def get_headers():
    return {
        "Authorization": f"Bearer {WEBEX_BOT_TOKEN}",
        "Content-Type": "application/json"
    }

def send_message(email: str, markdown: str):
    """Send a message to a person via Webex. Splits long messages automatically."""
    MAX_LEN = 7000  # Webex markdown limit is ~7439 bytes

    if len(markdown) <= MAX_LEN:
        payload = {"toPersonEmail": email, "markdown": markdown}
        response = requests.post(f"{BASE_URL}/messages", headers=get_headers(), json=payload)
        if response.status_code != 200:
            print(f"    Webex API {response.status_code}: {response.text[:200]}")
        return response.status_code == 200

    # Split on section dividers, sending multiple messages
    sections = markdown.split("\n---\n")
    chunks = []
    current = ""
    for section in sections:
        candidate = current + ("\n---\n" if current else "") + section
        if len(candidate) > MAX_LEN and current:
            chunks.append(current)
            current = section
        else:
            current = candidate
    if current:
        chunks.append(current)

    print(f"    📎 Report split into {len(chunks)} messages ({len(markdown)} chars total)")
    all_ok = True
    for i, chunk in enumerate(chunks):
        part_label = f"({i+1}/{len(chunks)})" if len(chunks) > 1 else ""
        payload = {"toPersonEmail": email, "markdown": chunk}
        response = requests.post(f"{BASE_URL}/messages", headers=get_headers(), json=payload)
        if response.status_code != 200:
            print(f"    Webex API {response.status_code} on part {i+1}: {response.text[:200]}")
            all_ok = False
    return all_ok

def build_dynamic_report(spacelift: dict) -> str:
    """Build a dynamic report from SpaceLift analysis data."""
    today = datetime.now().strftime("%B %d, %Y")
    time_now = datetime.now().strftime("%I:%M %p EST")
    analysis = spacelift.get("analysis", {})
    spaces = spacelift.get("spaces_monitored", [])

    report = f"""# 📊 Digitized Delivery - Consolidated Status Report
**Generated:** {today} at {time_now}
**Overall Status:** 🟡 YELLOW

---

## 📡 Data Sources Analyzed

| Source | Items | Period |
|--------|-------|--------|
| 🗨️ Webex Chat Messages | {spacelift.get('total_messages_analyzed', 0)} messages | Last {spacelift.get('period_days', 7)} days |
| 🎥 Meeting Recordings | Analyzed | Last 7 days |
| 👥 DD Spaces Monitored | {len(spaces)} spaces | Active |
| 👤 DD Participants Tracked | {spacelift.get('participants_tracked', 0)} people | Cisco team |
| 🔍 Personal Space References | {spacelift.get('total_personal_refs', 0)} messages | Last {spacelift.get('period_days', 7)} days |

**Spaces Monitored:**
"""
    for s in spaces:
        report += f"- {s['title']} ({s['message_count']} messages)\n"

    report += "\n---\n\n"

    # Executive Summary
    report += """## 🎯 Executive Summary

| Workstream | Status | Owner |
|------------|--------|-------|
| ISE as Code (ISAAC) - MGM | 🟢 Lab 90% complete, cert renewal done | Rakesh / Chetankumar |
| NAC Parity | 🟡 Cat-C & SDWAN data collection | Dhrumil Prajapati |
| Digital Document Automation | 🟡 Template reviews in progress | Dhrumil Prajapati |
| AI-Assisted Development | 🟢 OpenCode + Copilot rollout | Dhrumil Prajapati |
| GES Engagement Tracking | 🟡 Power BI dashboard build-out | Mike Brown |

---

"""

    # Workstream status (from AI analysis) — append if present
    ws_status = analysis.get("workstream_status", {})
    if ws_status:
        report += "## 📈 AI-Detected Workstream Updates\n\n"
        report += "| Workstream | Status |\n"
        report += "|------------|--------|\n"
        for ws, status in ws_status.items():
            report += f"| {ws} | {status} |\n"
        report += "\n---\n\n"

    # Key updates
    updates = analysis.get("updates", [])
    if updates:
        report += "## 📋 Key Updates\n\n"
        for u in updates[:8]:
            report += f"- {u}\n"
        report += "\n---\n\n"

    # Action items — merge AI-detected with standing items
    report += """## 🎯 Recommended Next Steps

| # | Priority | Action | Target | Owner |
|---|----------|--------|--------|-------|
| 1 | 🔴 HIGH | Complete ISAAC lab install & resolve remaining infra issues | This week | Chetankumar / Raphael |
| 2 | 🔴 HIGH | Setup YAML files for ISE PROD & begin observability playbooks | Next 2 wks | Rakesh / Chetankumar |
| 3 | 🟡 HIGH | Prepare ISAAC TOI for Darrin & MGM team (patch upgrade demo) | Before prod upgrade | Rakesh |
| 4 | 🟡 HIGH | Resolve credential management (Ansible Vault vs AAP Survey) | This week | Chetankumar / Raphael |
| 5 | 🟡 MED | Complete DDA template reviews with volunteers | This week | Dhrumil / GES Core Team |
| 6 | 🟡 MED | Continue NAC Parity data collection (Cat-C & SDWAN forms) | Ongoing | Dhrumil |
| 7 | 🟢 MED | Share GES engagement tracker with leadership | This week | Mike Brown |
| 8 | 🟢 LOW | Engage MGM virtualization team for vSphere API access | Next sprint | Rakesh |

---

"""

    # AI-detected action items
    actions = analysis.get("action_items", [])
    if actions:
        report += "## 🤖 AI-Detected Action Items\n\n"
        for i, a in enumerate(actions[:8], 1):
            report += f"- [ ] {a}\n"
        report += "\n---\n\n"

    # Risk register
    report += """## ⚠️ Risk Register

| ID | Severity | Risk | Mitigation | Owner |
|----|----------|------|------------|-------|
| R1 | 🟡 MED | MGM hesitant on ISAAC prod patch — Darrin wants lab demo first | Full lab demo + TOI before any prod changes | Rakesh |
| R2 | 🟡 MED | Credential mgmt for ISAAC scripts — Ansible Vault may not work for MGM infra | Exploring AAP Survey method as alternative | Chetankumar |
| R3 | 🟡 MED | vSphere API access blocked — needs MGM virtualization team | Deferred; not blocking current milestones | Rakesh |
| R4 | 🟢 LOW | GES engagement data incomplete in Power BI | Data collection in progress, focus areas being identified | Mike Brown |
| R5 | 🟢 LOW | DDA template review needs more volunteers | Soliciting from GES Core Team | Dhrumil |

---

"""

    # AI-detected risks
    risks = analysis.get("risks", [])
    if risks:
        report += "## 🤖 AI-Detected Risks & Concerns\n\n"
        for r in risks[:5]:
            report += f"- ⚠️ {r}\n"
        report += "\n---\n\n"

    # Decisions
    decisions = analysis.get("decisions", [])
    if decisions:
        report += "## ✅ Decisions Made\n\n"
        for d in decisions[:5]:
            report += f"- {d}\n"
        report += "\n---\n\n"

    # Next steps
    next_steps = analysis.get("next_steps", [])
    if next_steps:
        report += "## 🔜 AI-Detected Next Steps\n\n"
        for s in next_steps[:5]:
            report += f"- {s}\n"
        report += "\n---\n\n"

    # Timeline
    report += """## 📅 Timeline & Milestones

```
Completed ━━🟢━━ ISAAC lab: 6 nodes up, cert renewal done ✓
Completed ━━🟢━━ OpenCode + Copilot strategy adopted ✓
Completed ━━🟢━━ NAC Parity data collection form live ✓
This Week ━━🟡━━ ISAAC: Resolve remaining lab infra issues
This Week ━━🟡━━ DDA: Complete template reviews
This Week ━━🟡━━ Share GES engagement tracker
Next 2 Wk ━━�━━ ISAAC: PROD YAML setup + observability
Next 2 Wk ━━🟡━━ ISAAC: TOI for Darrin & MGM team
3 Weeks   ━━🔴━━ 🎯 ISAAC Patch 10 upgrade in PROD (target)
TBD       ━━⚪━━ vSphere API access (deferred)
```

---

"""

    # Recordings section (loaded separately)
    recordings_file = "recordings_analysis.json"
    if os.path.exists(recordings_file):
        with open(recordings_file, "r") as f:
            rec_data = json.load(f)
        if rec_data.get("meetings_analyzed"):
            report += "## 🎥 Recent Meeting Insights\n\n"
            report += f"**Meetings Analyzed (Last 7 Days):** {len(rec_data['meetings_analyzed'])}\n\n"
            for m in rec_data["meetings_analyzed"][:5]:
                status = "✅" if m.get("has_transcript") else "⚠️ No transcript"
                report += f"- 📹 {m.get('date', '')}: {m.get('title', 'Unknown')} {status}\n"
            report += "\n*Note: Enable Webex transcription for AI-powered meeting summaries*\n\n---\n\n"

    report += """## �� Key Contacts

| Role | Name | Email | Focus |
|------|------|-------|-------|
| Program Management Lead | Mike Brown | michabr4@cisco.com | Overall coordination & GES engagement tracking |
| Technical Lead, Principal Arch | Dhrumil Prajapati | dhprajap@cisco.com | DD strategy, tooling, NAC Parity, DDA |
| ISAAC / ISE Lead | Rakesh | ragade@cisco.com | ISE as Code adoption, MGM coordination |
| ISAAC Engineering | Chetankumar Phulpagare | cphulpag@cisco.com | ISAAC playbooks & automation |
| ISAAC Engineering | Raphael Moreno | rmorenot@cisco.com | ISAAC troubleshooting & cert automation |
| ISE Support | Liliana (Karen) | karenmar@cisco.com | ISE cert & access coordination |
| ISAAC Support | Shirley Puente | shpuente@cisco.com | ISAAC team coordination |
| ISAAC Engineering | Stuart Malone | stumalon@cisco.com | ISAAC documentation & Box/SharePoint |
| GES Leader | Nakia Stringfield | nstringf@cisco.com | GES leadership & engagement review |
| GES Leader | Michael Shomake | mshomake@cisco.com | GES data & Power BI |

---

## 🔄 Active Workstreams Detail

| Workstream | Status | Next Action |
|------------|--------|-------------|
| 🔐 ISE as Code (ISAAC) | Lab 90% — 6 nodes up, certs done | PROD YAML setup + observability playbooks |
| 🌐 NAC Parity | Data collection active | Cat-C & SDWAN forms to CDAs |
| 📄 Digital Document Automation | Template reviews | Volunteers reviewing this week |
| 🛠️ AI-Assisted Development | Adopted | OpenCode + GitHub Copilot deployed |
| 📊 GES Engagement Tracking | Building | Power BI dashboard + tracker sharing |

---

*📧 Reply "unsubscribe" to stop • Contact: michabr4@cisco.com*
*🤖 Auto-generated from Webex SpaceLift + Recordings Analysis*
"""
    return report

def get_static_report():
    """Fallback static report when no SpaceLift data is available."""
    today = datetime.now().strftime("%B %d, %Y")
    time_now = datetime.now().strftime("%I:%M %p EST")

    return f"""# 📊 Digitized Delivery - Consolidated Status Report
**Generated:** {today} at {time_now}
**Overall Status:** 🟡 YELLOW

---

## 📡 Data Sources

*SpaceLift analysis not available for this run. Showing static summary.*

**Spaces Monitored:**
- GES Digitized Delivery | Core Team
- MGM Digitized Delivery - ISE as Code Adoption
- Digitized Delivery - GES Leader Space
- GES Digitized Delivery (general)
- PS Digitized Delivery Learning Path Stakeholders

---

## 🎯 Executive Summary

| Workstream | Status | Owner |
|------------|--------|-------|
| ISE as Code (ISAAC) - MGM | 🟢 Lab 90% complete, cert renewal done | Rakesh / Chetankumar |
| NAC Parity | 🟡 Cat-C & SDWAN data collection | Dhrumil Prajapati |
| Digital Document Automation | 🟡 Template reviews in progress | Dhrumil Prajapati |
| AI-Assisted Development | 🟢 OpenCode + Copilot rollout | Dhrumil Prajapati |
| GES Engagement Tracking | 🟡 Power BI dashboard build-out | Mike Brown |

---

## 🎯 Recommended Next Steps

| # | Priority | Action | Target | Owner |
|---|----------|--------|--------|-------|
| 1 | � HIGH | Complete ISAAC lab install & resolve remaining infra issues | This week | Chetankumar / Raphael |
| 2 | 🔴 HIGH | Setup YAML files for ISE PROD & begin observability playbooks | Next 2 wks | Rakesh / Chetankumar |
| 3 | 🟡 HIGH | Prepare ISAAC TOI for Darrin & MGM team (patch upgrade demo) | Before prod | Rakesh |
| 4 | 🟡 HIGH | Resolve credential management (Ansible Vault vs AAP Survey) | This week | Chetankumar / Raphael |
| 5 | 🟡 MED | Complete DDA template reviews with volunteers | This week | Dhrumil / GES Core Team |
| 6 | 🟡 MED | Continue NAC Parity data collection (Cat-C & SDWAN) | Ongoing | Dhrumil |
| 7 | 🟢 MED | Share GES engagement tracker with leadership | This week | Mike Brown |
| 8 | 🟢 LOW | Engage MGM virtualization team for vSphere API access | Next sprint | Rakesh |

---

## ⚠️ Risk Register

| ID | Severity | Risk | Mitigation | Owner |
|----|----------|------|------------|-------|
| R1 | 🟡 MED | MGM hesitant on ISAAC prod patch — wants lab demo first | Full lab demo + TOI before prod changes | Rakesh |
| R2 | 🟡 MED | Credential mgmt — Ansible Vault may not work for MGM | Exploring AAP Survey method | Chetankumar |
| R3 | 🟡 MED | vSphere API access blocked by MGM virtualization team | Deferred; not blocking current work | Rakesh |
| R4 | 🟢 LOW | GES engagement data incomplete in Power BI | Data collection in progress | Mike Brown |
| R5 | 🟢 LOW | DDA template review needs more volunteers | Soliciting from GES Core Team | Dhrumil |

---

## 📅 Timeline & Milestones

```
Completed ━━🟢━━ ISAAC lab: 6 nodes up, cert renewal done ✓
Completed ━━🟢━━ OpenCode + Copilot strategy adopted ✓
Completed ━━🟢━━ NAC Parity data collection form live ✓
This Week ━━🟡━━ ISAAC: Resolve remaining lab infra issues
This Week ━━🟡━━ DDA: Complete template reviews
This Week ━━🟡━━ Share GES engagement tracker
Next 2 Wk ━━🟡━━ ISAAC: PROD YAML setup + observability
Next 2 Wk ━━🟡━━ ISAAC: TOI for Darrin & MGM team
3 Weeks   ━━🔴━━ 🎯 ISAAC Patch 10 upgrade in PROD (target)
TBD       ━━⚪━━ vSphere API access (deferred)
```

---

## 🎥 Recent Meeting Insights

**Meetings Analyzed (Last 7 Days):**
- 📹 GESW PMO Team Call
- 📹 Dhru / Mike 1:1
- 📹 (INT) MGM Architecture Huddle

*Note: Enable Webex transcription for AI-powered meeting summaries*

---

## 👥 Key Contacts

| Role | Name | Email | Focus |
|------|------|-------|-------|
| Program Management Lead | Mike Brown | michabr4@cisco.com | Overall coordination & GES engagement tracking |
| Technical Lead, Principal Arch | Dhrumil Prajapati | dhprajap@cisco.com | DD strategy, tooling, NAC Parity, DDA |
| ISAAC / ISE Lead | Rakesh | ragade@cisco.com | ISE as Code adoption, MGM coordination |
| ISAAC Engineering | Chetankumar Phulpagare | cphulpag@cisco.com | ISAAC playbooks & automation |
| ISAAC Engineering | Raphael Moreno | rmorenot@cisco.com | ISAAC troubleshooting & cert automation |
| ISE Support | Liliana (Karen) | karenmar@cisco.com | ISE cert & access coordination |
| ISAAC Support | Shirley Puente | shpuente@cisco.com | ISAAC team coordination |
| ISAAC Engineering | Stuart Malone | stumalon@cisco.com | ISAAC documentation & Box/SharePoint |
| GES Leader | Nakia Stringfield | nstringf@cisco.com | GES leadership & engagement review |
| GES Leader | Michael Shomake | mshomake@cisco.com | GES data & Power BI |

---

## 🔄 Active Workstreams Detail

| Workstream | Status | Next Action |
|------------|--------|-------------|
| 🔐 ISE as Code (ISAAC) | Lab 90% — 6 nodes up, certs done | PROD YAML setup + observability playbooks |
| 🌐 NAC Parity | Data collection active | Cat-C & SDWAN forms to CDAs |
| 📄 Digital Document Automation | Template reviews | Volunteers reviewing this week |
| 🛠️ AI-Assisted Development | Adopted | OpenCode + GitHub Copilot deployed |
| 📊 GES Engagement Tracking | Building | Power BI dashboard + tracker sharing |

---

*📧 Reply "unsubscribe" to stop • Contact: michabr4@cisco.com*
*🤖 Auto-generated • SpaceLift data will appear when WEBEX_ACCESS_TOKEN is configured*
"""

def get_status_report():
    """Generate the Digitized Delivery status report.
    Uses SpaceLift analysis if available, otherwise falls back to static template.
    """
    spacelift = load_spacelift_analysis()
    if spacelift:
        print("📊 Building dynamic report from SpaceLift analysis...")
        return build_dynamic_report(spacelift)
    else:
        print("⚠️ No SpaceLift analysis found, using static report template")
        return get_static_report()

def main():
    """Send reports to all subscribers."""
    if not WEBEX_BOT_TOKEN:
        print("❌ Error: WEBEX_BOT_TOKEN not set")
        exit(1)
    
    subscribers = load_subscribers()
    emails = subscribers.get("emails", [])
    
    if not emails:
        print("⚠️ No subscribers found")
        exit(0)
    
    print(f"📤 Sending Digitized Delivery Status Report to {len(emails)} subscribers...")
    
    report = get_status_report()
    success = 0
    failed = 0
    
    for email in emails:
        try:
            if send_message(email, report):
                print(f"  ✅ {email}")
                success += 1
            else:
                print(f"  ❌ {email} - API error")
                failed += 1
        except Exception as e:
            print(f"  ❌ {email} - {e}")
            failed += 1
    
    print(f"\n📊 Summary: {success} sent, {failed} failed")
    
    if failed > 0:
        exit(1)

if __name__ == "__main__":
    main()
