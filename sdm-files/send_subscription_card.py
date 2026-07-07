"""
Send a Webex Adaptive Card for MGM Status Bot Subscriptions
No server required - uses a simple form/email workflow
"""

import requests
import os

BOT_TOKEN = os.environ.get("WEBEX_BOT_TOKEN", "")
BASE_URL = "https://webexapis.com/v1"

def send_subscription_card(room_id: str = None, email: str = None):
    """Send an adaptive card for subscription management."""
    
    card = {
        "contentType": "application/vnd.microsoft.card.adaptive",
        "content": {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "version": "1.2",
            "body": [
                {
                    "type": "TextBlock",
                    "text": "📊 MGM Daily Status Report",
                    "weight": "Bolder",
                    "size": "Large",
                    "color": "Accent"
                },
                {
                    "type": "TextBlock",
                    "text": "Get automated status updates for MGM Resorts delivery every business day at 8:00 AM EST.",
                    "wrap": True
                },
                {
                    "type": "FactSet",
                    "facts": [
                        {"title": "Schedule", "value": "Mon-Fri @ 8:00 AM EST"},
                        {"title": "Content", "value": "Milestones, Risks, Actions"},
                        {"title": "Format", "value": "Webex Message + PowerPoint"}
                    ]
                },
                {
                    "type": "TextBlock",
                    "text": "To subscribe or unsubscribe:",
                    "weight": "Bolder",
                    "spacing": "Large"
                },
                {
                    "type": "TextBlock", 
                    "text": "📧 Email **michabr4@cisco.com** with subject:",
                    "wrap": True
                },
                {
                    "type": "TextBlock",
                    "text": "• **\"MGM Subscribe\"** - to join\\n• **\"MGM Unsubscribe\"** - to leave",
                    "wrap": True
                }
            ],
            "actions": [
                {
                    "type": "Action.OpenUrl",
                    "title": "📧 Subscribe via Email",
                    "url": "mailto:michabr4@cisco.com?subject=MGM%20Subscribe&body=Please%20add%20me%20to%20the%20MGM%20Daily%20Status%20Report%20distribution."
                },
                {
                    "type": "Action.OpenUrl", 
                    "title": "📧 Unsubscribe",
                    "url": "mailto:michabr4@cisco.com?subject=MGM%20Unsubscribe&body=Please%20remove%20me%20from%20the%20MGM%20Daily%20Status%20Report%20distribution."
                }
            ]
        }
    }
    
    headers = {
        "Authorization": f"Bearer {BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {"attachments": [card]}
    
    if room_id:
        payload["roomId"] = room_id
    elif email:
        payload["toPersonEmail"] = email
    else:
        print("❌ Provide either --room or --email")
        return
    
    # Also add a text fallback
    payload["text"] = "MGM Daily Status Report - Subscribe by emailing michabr4@cisco.com with subject 'MGM Subscribe'"
    
    response = requests.post(f"{BASE_URL}/messages", headers=headers, json=payload)
    
    if response.status_code == 200:
        print("✅ Subscription card sent!")
    else:
        print(f"❌ Error: {response.text}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--room", "-r", help="Room ID to send card to")
    parser.add_argument("--email", "-e", help="Email to send card to")
    parser.add_argument("--token", "-t", help="Webex Bot Token")
    args = parser.parse_args()
    
    if args.token:
        BOT_TOKEN = args.token
    
    if not BOT_TOKEN:
        print("❌ Set WEBEX_BOT_TOKEN or use --token")
        exit(1)
    
    send_subscription_card(room_id=args.room, email=args.email)
