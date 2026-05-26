#!/usr/bin/env sh
# Fetch mail (or sample) then remind you to run orchestration in Cursor.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

SAMPLE=0
if [ "${1:-}" = "--sample" ]; then
  SAMPLE=1
  shift
fi

if [ "$SAMPLE" -eq 1 ]; then
  ./scripts/email_fetch.sh --sample
else
  echo "==> Sign in with your Cisco work account when the browser opens."
  ./scripts/email_fetch.sh "$@" || {
    echo ""
    echo "Fetch failed. Try: ./scripts/run_email_review.sh --sample"
    exit 1
  }
fi

OUT="${ROOT}/data/runs/email/latest/messages.json"
echo ""
echo "Messages: $OUT"
echo ""
echo "In Cursor, paste:"
echo "  Follow agents/orchestrator-email.md and orchestration/email-inbox-review"
echo "  using data/runs/email/latest/messages.json. Draft only."
