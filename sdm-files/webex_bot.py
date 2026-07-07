"""
Webex Bot for MGM Status Report Delivery

Setup:
1. Go to https://developer.webex.com/my-apps
2. Click "Create a New App" → "Create a Bot"
3. Copy the Bot Access Token
4. Add the bot to your desired Webex space
5. Get the Room ID (see get_rooms() function)
"""

import requests
import json
from datetime import datetime
import os

class WebexBot:
    """Webex Teams Bot for status report delivery."""
    
    def __init__(self, access_token: str = None):
        self.access_token = access_token or os.environ.get("WEBEX_BOT_TOKEN")
        self.base_url = "https://webexapis.com/v1"
        
        if not self.access_token:
            raise ValueError(
                "Webex Bot Token required. Set WEBEX_BOT_TOKEN env var or pass to constructor.\n"
                "Create a bot at: https://developer.webex.com/my-apps"
            )
    
    def _headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def get_bot_info(self):
        """Get bot's own info."""
        response = requests.get(f"{self.base_url}/people/me", headers=self._headers())
        response.raise_for_status()
        return response.json()
    
    def get_rooms(self):
        """List all rooms the bot is a member of."""
        response = requests.get(f"{self.base_url}/rooms", headers=self._headers())
        response.raise_for_status()
        rooms = response.json().get("items", [])
        
        print("\n📋 Rooms the bot has access to:")
        print("-" * 60)
        for room in rooms:
            print(f"  Name: {room['title']}")
            print(f"  ID:   {room['id']}")
            print(f"  Type: {room['type']}")
            print("-" * 60)
        
        return rooms
    
    def send_message(self, room_id: str, markdown: str, text: str = None):
        """Send a message to a room."""
        payload = {
            "roomId": room_id,
            "markdown": markdown
        }
        if text:
            payload["text"] = text
        
        response = requests.post(
            f"{self.base_url}/messages",
            headers=self._headers(),
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def send_file(self, room_id: str, file_path: str, message: str = None):
        """Send a file to a room."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        with open(file_path, "rb") as f:
            files = {"files": (os.path.basename(file_path), f)}
            data = {"roomId": room_id}
            if message:
                data["text"] = message
            
            response = requests.post(
                f"{self.base_url}/messages",
                headers=headers,
                data=data,
                files=files
            )
        
        response.raise_for_status()
        return response.json()
    
    def send_mgm_status_report(self, room_id: str):
        """Send the MGM status report to a Webex room."""
        
        # Format the report as Webex markdown
        report = self._format_mgm_report()
        
        # Send the message
        result = self.send_message(room_id, report)
        print(f"✅ Status report sent to room!")
        
        # Also send the PowerPoint file if it exists
        pptx_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "MGM_Status_Report_20260410.pptx")
        if os.path.exists(pptx_path):
            self.send_file(room_id, pptx_path, "📊 Full PowerPoint report attached")
            print(f"✅ PowerPoint file sent!")
        
        return result
    
    def _format_mgm_report(self):
        """Format MGM status report for Webex."""
        
        report = """## 📊 MGM Resorts - Delivery Status Report
**Date:** April 10, 2026 | **Status:** 🟡 YELLOW

---

### Executive Summary

| Area | Status |
|------|--------|
| Firewall Migration | 🟡 PO pending MGM review |
| Technical Discovery | 🟢 Kickoff today (Apr 10) |
| PAN Support | 🔴 Expires Apr 15 - NO coverage |
| ISE Automation | 🟢 Cert renewal in progress |

---

### ⚠️ CRITICAL: Palo Alto Support Gap

**Deadline:** April 15, 2026
- No third-party support coverage confirmed
- Mitigation: Internal Cisco PAN experts + Mike Culp 75-80% allocation
- "Frying Pan" space created with ex-PAN engineers

---

### 🎯 Recommended Next Steps

| Priority | Action | Target |
|----------|--------|--------|
| 🔴 **IMMEDIATE** | Validate SCC access (Daniel/Mike Culp) | Today |
| 🔴 **IMMEDIATE** | Engage MGM security with Nexar | Today |
| 🟡 **HIGH** | Finalize PAN support gap mitigation | Apr 14 |
| 🟡 **HIGH** | Increase Culp allocation to 75-80% | Apr 11 |
| 🟡 **HIGH** | Schedule Netscout TAPs call | Apr 14 |
| 🟢 **MEDIUM** | Complete ISE PSN05 investigation | Apr 12 |

---

### 📅 Key Milestones

```
Apr 10  🟢 Technical Discovery Kickoff
Apr 11-12  🟡 Complete Network/SCC Access
Apr 15  🔴 ⚠️ PAN Support Expires
Apr 17-18  🟡 Migration Plan v1 Complete
May 1   ⚪ Phase 1 Migration Start (Target)
```

---

### ⚠️ Risk Register

| Severity | Risk |
|----------|------|
| 🔴 HIGH | PAN support expires Apr 15 - no 3rd party coverage |
| 🔴 HIGH | S2S VPN migration complexity (Mike Culp flagged) |
| 🟡 MED | Resource constraints - Culp needs 75-80% allocation |
| 🟢 LOW | ISE PSN05 certificate error - investigation ongoing |

---

### 👥 Key Contacts

- **Mike Brown** - Delivery Lead
- **Jason Anderson** - CX Leadership  
- **Paul Snow** - Sales Lead
- **Mike Culp** - Technical Lead (Firepower)

---
*Generated from Webex Spacelift export analysis*
"""
        return report
    
    def send_to_person(self, email: str):
        """Send the MGM status report directly to a person."""
        
        report = self._format_mgm_report()
        
        payload = {
            "toPersonEmail": email,
            "markdown": report
        }
        
        response = requests.post(
            f"{self.base_url}/messages",
            headers=self._headers(),
            json=payload
        )
        response.raise_for_status()
        print(f"✅ Status report sent to {email}!")
        
        # Also send the PowerPoint file
        pptx_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "MGM_Status_Report_20260410.pptx")
        if os.path.exists(pptx_path):
            headers = {"Authorization": f"Bearer {self.access_token}"}
            with open(pptx_path, "rb") as f:
                files = {"files": (os.path.basename(pptx_path), f)}
                data = {"toPersonEmail": email, "text": "📊 Full PowerPoint report attached"}
                response = requests.post(
                    f"{self.base_url}/messages",
                    headers=headers,
                    data=data,
                    files=files
                )
            response.raise_for_status()
            print(f"✅ PowerPoint file sent to {email}!")
        
        return response.json()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Webex Bot for MGM Status Report")
    parser.add_argument("--token", "-t", help="Webex Bot Access Token")
    parser.add_argument("--room", "-r", help="Room ID to send report to")
    parser.add_argument("--email", "-e", help="Email to send report to directly")
    parser.add_argument("--list-rooms", action="store_true", help="List available rooms")
    parser.add_argument("--bot-info", action="store_true", help="Show bot info")
    
    args = parser.parse_args()
    
    try:
        bot = WebexBot(args.token)
        
        if args.bot_info:
            info = bot.get_bot_info()
            print(f"\n🤖 Bot Info:")
            print(f"  Name: {info.get('displayName')}")
            print(f"  Email: {info.get('emails', ['N/A'])[0]}")
            print(f"  ID: {info.get('id')}")
            return
        
        if args.list_rooms:
            bot.get_rooms()
            return
        
        if args.email:
            bot.send_to_person(args.email)
            return
        
        if args.room:
            bot.send_mgm_status_report(args.room)
            return
        
        # Default: show help
        print("""
🤖 MGM Status Report Webex Bot

Usage:
  1. Set your bot token:
     export WEBEX_BOT_TOKEN="your_token_here"
  
  2. List rooms the bot can access:
     python webex_bot.py --list-rooms
  
  3. Send report to a room:
     python webex_bot.py --room "ROOM_ID_HERE"
  
  4. Send report directly to your email:
     python webex_bot.py --email "michabr4@cisco.com"

To create a bot:
  1. Go to https://developer.webex.com/my-apps
  2. Click "Create a New App" → "Create a Bot"
  3. Copy the Access Token
  4. Add the bot to your Webex space
""")
        
    except ValueError as e:
        print(f"❌ Error: {e}")
    except requests.exceptions.HTTPError as e:
        print(f"❌ API Error: {e}")
        print(f"   Response: {e.response.text}")


if __name__ == "__main__":
    main()
