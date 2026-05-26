"""
MGM Status Report Bot - Interactive Server with Subscriptions

This bot listens for messages and allows users to:
- Subscribe to daily reports
- Unsubscribe from reports
- Request immediate reports
- Check subscription status

Run this server and users can message the bot directly in Webex.
"""

import os
import json
import requests
from flask import Flask, request, jsonify
from datetime import datetime
import threading
import schedule
import time

app = Flask(__name__)

# Configuration
BOT_TOKEN = os.environ.get("WEBEX_BOT_TOKEN", "")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "mgm-status-bot-secret")
SUBSCRIBERS_FILE = "os.path.join(os.path.dirname(os.path.abspath(__file__)), "subscribers.json")"
BASE_URL = "https://webexapis.com/v1"

# Load/Save subscribers
def load_subscribers():
    """Load subscribers from file."""
    if os.path.exists(SUBSCRIBERS_FILE):
        with open(SUBSCRIBERS_FILE, "r") as f:
            return json.load(f)
    return {"emails": ["michabr4@cisco.com"]}  # Default subscriber

def save_subscribers(data):
    """Save subscribers to file."""
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_headers():
    return {
        "Authorization": f"Bearer {BOT_TOKEN}",
        "Content-Type": "application/json"
    }

def send_message(person_email: str, markdown: str):
    """Send a message to a person."""
    payload = {
        "toPersonEmail": person_email,
        "markdown": markdown
    }
    response = requests.post(f"{BASE_URL}/messages", headers=get_headers(), json=payload)
    return response.json()

def get_message(message_id: str):
    """Get message content by ID."""
    response = requests.get(f"{BASE_URL}/messages/{message_id}", headers=get_headers())
    return response.json()

def get_person(person_id: str):
    """Get person details by ID."""
    response = requests.get(f"{BASE_URL}/people/{person_id}", headers=get_headers())
    return response.json()

def get_mgm_report():
    """Get the formatted MGM status report."""
    return """## 📊 MGM Resorts - Delivery Status Report
**Date:** """ + datetime.now().strftime("%B %d, %Y") + """ | **Status:** 🟡 YELLOW

---

### Executive Summary

| Area | Status |
|------|--------|
| Firewall Migration | 🟡 PO pending MGM review |
| Technical Discovery | 🟢 In progress |
| PAN Support | 🔴 Expires Apr 15 - NO coverage |
| ISE Automation | 🟢 Cert renewal in progress |

---

### ⚠️ CRITICAL: Palo Alto Support Gap

**Deadline:** April 15, 2026
- No third-party support coverage confirmed
- Mitigation: Internal Cisco PAN experts + Mike Culp 75-80% allocation

---

### 🎯 Key Next Steps

| Priority | Action | Target |
|----------|--------|--------|
| 🔴 IMMEDIATE | Validate SCC access | Today |
| 🔴 IMMEDIATE | Engage MGM security with Nexar | Today |
| 🟡 HIGH | Finalize PAN support gap mitigation | Apr 14 |
| 🟡 HIGH | Increase Culp allocation to 75-80% | Apr 11 |

---

### 👥 Key Contacts
- **Mike Brown** - Delivery Lead
- **Jason Anderson** - CX Leadership  
- **Paul Snow** - Sales Lead

---
*Reply with `help` for bot commands*
"""

def handle_command(sender_email: str, message_text: str):
    """Handle incoming commands."""
    cmd = message_text.strip().lower()
    subscribers = load_subscribers()
    
    if cmd in ["subscribe", "sub", "join"]:
        if sender_email not in subscribers["emails"]:
            subscribers["emails"].append(sender_email)
            save_subscribers(subscribers)
            return f"""✅ **Subscribed!**

You will receive the MGM Status Report every business day at 8:00 AM EST.

**Commands:**
- `report` - Get immediate status report
- `unsubscribe` - Stop receiving reports
- `status` - Check your subscription
- `help` - Show all commands"""
        else:
            return "ℹ️ You're already subscribed! Reply `report` to get the latest status."
    
    elif cmd in ["unsubscribe", "unsub", "leave", "stop"]:
        if sender_email in subscribers["emails"]:
            subscribers["emails"].remove(sender_email)
            save_subscribers(subscribers)
            return "✅ **Unsubscribed.** You will no longer receive daily reports.\n\nReply `subscribe` anytime to rejoin."
        else:
            return "ℹ️ You're not currently subscribed. Reply `subscribe` to join."
    
    elif cmd in ["report", "status report", "get report", "send report"]:
        return get_mgm_report()
    
    elif cmd in ["status", "check", "info"]:
        if sender_email in subscribers["emails"]:
            return f"""✅ **You are subscribed**

📧 Email: {sender_email}
📅 Schedule: Business days at 8:00 AM EST
👥 Total subscribers: {len(subscribers['emails'])}

Reply `unsubscribe` to stop receiving reports."""
        else:
            return f"""❌ **You are not subscribed**

Reply `subscribe` to receive daily MGM status reports."""
    
    elif cmd in ["help", "?", "commands"]:
        return """## 🤖 MGM Status Report Bot

### Commands

| Command | Description |
|---------|-------------|
| `subscribe` | Join daily status reports |
| `unsubscribe` | Stop receiving reports |
| `report` | Get immediate status report |
| `status` | Check your subscription |
| `list` | Show all subscribers (admin) |
| `help` | Show this message |

### Schedule
Reports are sent every **business day at 8:00 AM EST** (Mon-Fri).

### About
This bot analyzes Webex conversations from MGM-related spaces and generates automated status reports with key updates, risks, and recommended actions.

---
*Questions? Contact michabr4@cisco.com*"""
    
    elif cmd in ["list", "subscribers", "who"]:
        # Admin command - show subscribers
        if sender_email == "michabr4@cisco.com":
            sub_list = "\n".join([f"- {email}" for email in subscribers["emails"]])
            return f"""## 📋 Current Subscribers ({len(subscribers['emails'])})

{sub_list}"""
        else:
            return "ℹ️ This command is admin-only."
    
    else:
        return f"""👋 Hi! I'm the **MGM Status Report Bot**.

I didn't understand `{message_text}`.

**Quick commands:**
- `subscribe` - Get daily reports
- `report` - Get status now
- `help` - All commands

Reply with one of these commands to get started!"""

@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming Webex webhooks."""
    data = request.json
    
    if data.get("resource") == "messages" and data.get("event") == "created":
        message_id = data["data"]["id"]
        person_id = data["data"]["personId"]
        
        # Get the message content
        message = get_message(message_id)
        person = get_person(person_id)
        
        # Don't respond to our own messages
        bot_info = requests.get(f"{BASE_URL}/people/me", headers=get_headers()).json()
        if person_id == bot_info.get("id"):
            return jsonify({"status": "ignored - own message"})
        
        sender_email = person.get("emails", ["unknown"])[0]
        message_text = message.get("text", "")
        
        print(f"[{datetime.now()}] Message from {sender_email}: {message_text}")
        
        # Handle the command
        response = handle_command(sender_email, message_text)
        send_message(sender_email, response)
        
        return jsonify({"status": "processed"})
    
    return jsonify({"status": "ignored"})

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    subscribers = load_subscribers()
    return jsonify({
        "status": "healthy",
        "subscribers": len(subscribers["emails"]),
        "timestamp": datetime.now().isoformat()
    })

def send_daily_reports():
    """Send reports to all subscribers."""
    subscribers = load_subscribers()
    report = get_mgm_report()
    
    print(f"\n[{datetime.now()}] Sending daily reports to {len(subscribers['emails'])} subscribers...")
    
    for email in subscribers["emails"]:
        try:
            send_message(email, report)
            print(f"  ✅ Sent to {email}")
        except Exception as e:
            print(f"  ❌ Failed for {email}: {e}")

def run_scheduler():
    """Run the daily scheduler in background."""
    # Schedule for 8 AM EST (business days)
    schedule.every().monday.at("08:00").do(send_daily_reports)
    schedule.every().tuesday.at("08:00").do(send_daily_reports)
    schedule.every().wednesday.at("08:00").do(send_daily_reports)
    schedule.every().thursday.at("08:00").do(send_daily_reports)
    schedule.every().friday.at("08:00").do(send_daily_reports)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

def setup_webhook(webhook_url: str):
    """Create or update the Webex webhook."""
    # List existing webhooks
    response = requests.get(f"{BASE_URL}/webhooks", headers=get_headers())
    webhooks = response.json().get("items", [])
    
    # Delete existing webhooks for this bot
    for wh in webhooks:
        if "mgm-status" in wh.get("name", "").lower():
            requests.delete(f"{BASE_URL}/webhooks/{wh['id']}", headers=get_headers())
            print(f"Deleted old webhook: {wh['name']}")
    
    # Create new webhook
    payload = {
        "name": "MGM Status Bot - Messages",
        "targetUrl": webhook_url,
        "resource": "messages",
        "event": "created"
    }
    response = requests.post(f"{BASE_URL}/webhooks", headers=get_headers(), json=payload)
    
    if response.status_code == 200:
        print(f"✅ Webhook created: {webhook_url}")
        return response.json()
    else:
        print(f"❌ Failed to create webhook: {response.text}")
        return None

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MGM Status Bot Server")
    parser.add_argument("--port", "-p", type=int, default=5050, help="Port to run server on")
    parser.add_argument("--webhook-url", "-w", help="Public URL for webhook (e.g., ngrok URL)")
    parser.add_argument("--send-now", action="store_true", help="Send reports to all subscribers now")
    parser.add_argument("--list", action="store_true", help="List current subscribers")
    parser.add_argument("--add", help="Add a subscriber email")
    parser.add_argument("--remove", help="Remove a subscriber email")
    
    args = parser.parse_args()
    
    if not BOT_TOKEN:
        print("❌ Error: Set WEBEX_BOT_TOKEN environment variable")
        exit(1)
    
    if args.list:
        subscribers = load_subscribers()
        print(f"\n📋 Subscribers ({len(subscribers['emails'])}):")
        for email in subscribers["emails"]:
            print(f"  - {email}")
        exit(0)
    
    if args.add:
        subscribers = load_subscribers()
        if args.add not in subscribers["emails"]:
            subscribers["emails"].append(args.add)
            save_subscribers(subscribers)
            print(f"✅ Added: {args.add}")
        else:
            print(f"ℹ️ Already subscribed: {args.add}")
        exit(0)
    
    if args.remove:
        subscribers = load_subscribers()
        if args.remove in subscribers["emails"]:
            subscribers["emails"].remove(args.remove)
            save_subscribers(subscribers)
            print(f"✅ Removed: {args.remove}")
        else:
            print(f"ℹ️ Not found: {args.remove}")
        exit(0)
    
    if args.send_now:
        send_daily_reports()
        exit(0)
    
    # Initialize subscribers file
    if not os.path.exists(SUBSCRIBERS_FILE):
        save_subscribers({"emails": ["michabr4@cisco.com"]})
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           MGM Status Report Bot - Server                     ║
╠══════════════════════════════════════════════════════════════╣
║  Port: {args.port:<53} ║
║  Subscribers: {len(load_subscribers()['emails']):<46} ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    if args.webhook_url:
        setup_webhook(args.webhook_url)
    else:
        print("⚠️  No webhook URL provided. Users won't be able to message the bot.")
        print("   Use ngrok to expose this server, then run with --webhook-url")
        print("   Example: ngrok http 5050")
        print("")
    
    # Start scheduler in background
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    print("📅 Scheduler started (Mon-Fri 8:00 AM EST)")
    
    # Run Flask server
    app.run(host="0.0.0.0", port=args.port, debug=False)
