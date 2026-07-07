"""
Webex Bot Scheduler - Automated Daily Status Reports

This script can be run as a background service or scheduled via cron/launchd.
"""

import schedule
import time
import os
import sys
from datetime import datetime
from webex_bot import WebexBot

# Configuration
WEBEX_BOT_TOKEN = os.environ.get("WEBEX_BOT_TOKEN", "")
RECIPIENT_EMAIL = "michabr4@cisco.com"
SCHEDULE_TIME = "08:00"  # Default: 8:00 AM daily

def send_daily_report():
    """Send the daily MGM status report."""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Sending daily MGM status report...")
    
    try:
        bot = WebexBot(WEBEX_BOT_TOKEN)
        bot.send_to_person(RECIPIENT_EMAIL)
        print(f"✅ Report sent successfully to {RECIPIENT_EMAIL}")
    except Exception as e:
        print(f"❌ Failed to send report: {e}")

def run_scheduler(schedule_time: str = SCHEDULE_TIME):
    """Run the scheduler."""
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           MGM Status Report Bot - Scheduler                  ║
╠══════════════════════════════════════════════════════════════╣
║  Recipient: {RECIPIENT_EMAIL:<47} ║
║  Schedule:  Daily at {schedule_time:<40} ║
║  Status:    Running...                                       ║
╚══════════════════════════════════════════════════════════════╝

Press Ctrl+C to stop the scheduler.
""")
    
    # Schedule the job
    schedule.every().day.at(schedule_time).do(send_daily_report)
    
    # Also show next run time
    print(f"📅 Next scheduled run: {schedule.next_run()}")
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MGM Status Report Scheduler")
    parser.add_argument("--time", "-t", default="08:00", 
                        help="Time to send report (HH:MM format, 24-hour). Default: 08:00")
    parser.add_argument("--now", action="store_true",
                        help="Send report immediately, then continue with schedule")
    parser.add_argument("--token", help="Webex Bot Token (or set WEBEX_BOT_TOKEN env var)")
    parser.add_argument("--email", "-e", default=RECIPIENT_EMAIL,
                        help=f"Recipient email. Default: {RECIPIENT_EMAIL}")
    
    args = parser.parse_args()
    
    if args.token:
        WEBEX_BOT_TOKEN = args.token
    
    if not WEBEX_BOT_TOKEN:
        print("❌ Error: WEBEX_BOT_TOKEN required. Set env var or use --token")
        sys.exit(1)
    
    RECIPIENT_EMAIL = args.email
    
    if args.now:
        send_daily_report()
    
    run_scheduler(args.time)
