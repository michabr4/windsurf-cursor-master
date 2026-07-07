#!/bin/bash
# Setup Daily MGM Status Report Bot
# This creates a macOS LaunchAgent that runs the bot daily

# Configuration - EDIT THESE VALUES
SCHEDULE_HOUR=8      # Hour to run (0-23, 24-hour format)
SCHEDULE_MINUTE=0    # Minute to run (0-59)
BOT_TOKEN="${WEBEX_BOT_TOKEN:-YOUR_TOKEN_HERE}"
RECIPIENT="michabr4@cisco.com"

# Paths
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLIST_NAME="com.cisco.mgm-status-bot"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_NAME}.plist"
LOG_PATH="$HOME/Library/Logs/mgm-status-bot.log"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       MGM Status Report Bot - Daily Schedule Setup           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Create the LaunchAgent plist
cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${PLIST_NAME}</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>${SCRIPT_DIR}/webex_bot.py</string>
        <string>--email</string>
        <string>${RECIPIENT}</string>
    </array>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>WEBEX_BOT_TOKEN</key>
        <string>${BOT_TOKEN}</string>
    </dict>
    
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>${SCHEDULE_HOUR}</integer>
        <key>Minute</key>
        <integer>${SCHEDULE_MINUTE}</integer>
    </dict>
    
    <key>StandardOutPath</key>
    <string>${LOG_PATH}</string>
    
    <key>StandardErrorPath</key>
    <string>${LOG_PATH}</string>
    
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
EOF

echo "✅ Created LaunchAgent: $PLIST_PATH"
echo ""

# Unload if already loaded
launchctl unload "$PLIST_PATH" 2>/dev/null

# Load the new agent
launchctl load "$PLIST_PATH"

echo "✅ LaunchAgent loaded!"
echo ""
echo "📅 Schedule: Daily at $(printf '%02d:%02d' $SCHEDULE_HOUR $SCHEDULE_MINUTE)"
echo "📧 Recipient: $RECIPIENT"
echo "📝 Logs: $LOG_PATH"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Commands:"
echo "  View logs:     tail -f ~/Library/Logs/mgm-status-bot.log"
echo "  Stop bot:      launchctl unload $PLIST_PATH"
echo "  Start bot:     launchctl load $PLIST_PATH"
echo "  Run now:       launchctl start $PLIST_NAME"
echo "  Check status:  launchctl list | grep mgm"
echo ""
echo "To change schedule time, edit SCHEDULE_HOUR and SCHEDULE_MINUTE"
echo "in this script and run it again."
echo ""
