#!/usr/bin/env sh
# Fetch inbox JSON for email orchestration (minimal IT via Graph PowerShell).
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
  export MS_MAILBOX_UPN MS_AUTH_MODE MS_TENANT_ID MS_CLIENT_ID MS_GRAPH_SCOPES
fi

SINCE_HOURS=48
MAX_MESSAGES=40
OUT="${ROOT}/data/runs/email/latest/messages.json"

while [ $# -gt 0 ]; do
  case "$1" in
    --since-hours) SINCE_HOURS="$2"; shift 2 ;;
    --max-messages) MAX_MESSAGES="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    --sample)
      mkdir -p "$(dirname "$OUT")"
      cp "${ROOT}/python/connectors/microsoft_mail/fixtures/sample-messages.json" "$OUT"
      echo "Sample mode: wrote $OUT"
      exit 0
      ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

AUTH_MODE="${MS_AUTH_MODE:-graph_powershell}"

if [ "$AUTH_MODE" = "sample" ]; then
  mkdir -p "$(dirname "$OUT")"
  cp "${ROOT}/python/connectors/microsoft_mail/fixtures/sample-messages.json" "$OUT"
  echo "Sample mode: wrote $OUT"
  exit 0
fi

if [ "$AUTH_MODE" = "device_code" ]; then
  export PYTHONPATH="${ROOT}/python${PYTHONPATH:+:${PYTHONPATH}}"
  exec python3 "${ROOT}/python/connectors/microsoft_mail/fetch_device_code.py" \
    --since-hours "$SINCE_HOURS" --max-messages "$MAX_MESSAGES" --out "$OUT"
fi

PWSH=""
if command -v pwsh >/dev/null 2>&1; then
  PWSH="pwsh"
elif [ -x "${ROOT}/.tools/pwsh" ]; then
  PWSH="${ROOT}/.tools/pwsh"
fi

if [ -z "$PWSH" ]; then
  echo "PowerShell not found. Run: ./scripts/email-setup.sh" >&2
  echo "Or use: ./scripts/email_fetch.sh --sample" >&2
  exit 1
fi

mkdir -p "$(dirname "$OUT")"
"$PWSH" -NoProfile -File "${ROOT}/scripts/email-fetch-graph.ps1" \
  -SinceHours "$SINCE_HOURS" -MaxMessages "$MAX_MESSAGES" -OutFile "$OUT"
