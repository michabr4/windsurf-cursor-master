#!/bin/bash
# MGM Status Bot - Self-Service Subscription Server
# Run this script to enable self-service subscriptions

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Load secrets from .env (never commit .env)
if [ -f "$SCRIPT_DIR/.env" ]; then
  set -a
  # shellcheck source=/dev/null
  source "$SCRIPT_DIR/.env"
  set +a
fi
if [ -z "${WEBEX_BOT_TOKEN:-}" ]; then
  echo "❌ WEBEX_BOT_TOKEN is not set. Copy .env.example to .env and add your token,"
  echo "   or export WEBEX_BOT_TOKEN before running this script."
  echo "   Rotate at: https://developer.webex.com/my-apps"
  exit 1
fi

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       MGM Status Bot - Self-Service Setup                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Start ngrok in background
echo "🌐 Starting ngrok tunnel..."
ngrok http 5050 > /dev/null 2>&1 &
NGROK_PID=$!
sleep 5

# Get the public URL
NGROK_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['tunnels'][0]['public_url'] if d.get('tunnels') else '')" 2>/dev/null)

if [ -z "$NGROK_URL" ]; then
    echo "❌ Failed to start ngrok. Make sure authtoken is configured."
    echo "   Run: ngrok config add-authtoken YOUR_TOKEN"
    kill $NGROK_PID 2>/dev/null
    exit 1
fi

echo "✅ Ngrok URL: $NGROK_URL"
echo ""

# Start the bot server
echo "🤖 Starting bot server..."
echo ""
python3 webex_bot_server.py --webhook-url "${NGROK_URL}/webhook"

# Cleanup on exit
trap "kill $NGROK_PID 2>/dev/null" EXIT
