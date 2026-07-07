#!/usr/bin/env bash
# Clone teamspace-mcp and verify uv can run it.
# Usage:
#   ./scripts/setup_teamspace_mcp.sh 'git@github.cisco.com:YOUR_ORG/teamspace-mcp.git'
# Or:
#   export TEAMSPACE_MCP_REPO_URL='...'
#   ./scripts/setup_teamspace_mcp.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="${TEAMSPACE_MCP_ENV_FILE:-$ROOT/.env}"

if [[ -f "$ENV_FILE" ]]; then
  line="$(grep -E '^TEAMSPACE_MCP_REPO_URL=' "$ENV_FILE" | tail -1 || true)"
  if [[ -n "$line" ]]; then
    val="${line#TEAMSPACE_MCP_REPO_URL=}"
    val="${val%$'\r'}"
    val="${val#\"}"
    val="${val%\"}"
    export TEAMSPACE_MCP_REPO_URL="${TEAMSPACE_MCP_REPO_URL:-$val}"
  fi
fi

REPO_URL="${1:-${TEAMSPACE_MCP_REPO_URL:-}}"
TARGET="${TEAMSPACE_MCP_DIR:-$HOME/teamspace-mcp}"
UV="${UV:-$HOME/.local/bin/uv}"

if [[ -z "$REPO_URL" ]]; then
  echo "Usage: $0 <git-clone-url>"
  echo "Or set TEAMSPACE_MCP_REPO_URL in $ENV_FILE"
  echo "Example: $0 'git@github.cisco.com:cx/teamspace-mcp.git'"
  exit 1
fi

if [[ ! -x "$UV" ]]; then
  echo "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  UV="$HOME/.local/bin/uv"
fi

if [[ -d "$TARGET/.git" ]]; then
  echo "Already cloned at $TARGET — pulling latest..."
  git -C "$TARGET" pull --ff-only
else
  echo "Cloning into $TARGET ..."
  git clone "$REPO_URL" "$TARGET"
fi

echo "Verifying teamspace-mcp starts..."
cd "$TARGET"
"$UV" sync
"$UV" run teamspace-mcp --help | head -5

echo ""
echo "Done. Reload MCP in Cursor (Settings → MCP)."
echo "Config expects project at: $TARGET"
