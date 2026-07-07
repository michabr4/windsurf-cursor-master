#!/usr/bin/env bash
# Run ON YOUR MAC once: add Actions secrets and optionally trigger the daily report workflow.
# Prerequisites: brew install gh && gh auth login -h github.com

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v gh >/dev/null 2>&1; then
  echo "Install GitHub CLI: brew install gh"
  exit 1
fi

if ! gh auth status -h github.com >/dev/null 2>&1; then
  echo "Log in first:"
  echo "  gh auth login -h github.com"
  exit 1
fi

BRANCH="$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || echo master)"
REPO="$(gh repo view --json nameWithOwner -q .nameWithOwner)"

echo "=== MGM Status Bot — GitHub Actions secrets ==="
echo "Repo: $REPO (default branch: $BRANCH)"
echo ""
echo "1) WEBEX_BOT_TOKEN (required) — paste bot token when prompted."
gh secret set WEBEX_BOT_TOKEN

read -p "Add WEBEX_ACCESS_TOKEN for live recording insights? [y/N] " a1
if [[ "${a1,,}" == "y" ]]; then
  gh secret set WEBEX_ACCESS_TOKEN
fi

read -p "Add OPENAI_API_KEY for transcript AI summaries? [y/N] " a2
if [[ "${a2,,}" == "y" ]]; then
  gh secret set OPENAI_API_KEY
fi

echo ""
read -p "Run workflow 'MGM Daily Status Report' now? [y/N] " run
if [[ "${run,,}" == "y" ]]; then
  gh workflow run daily-report.yml --ref "$BRANCH"
  echo "Started. Open: https://github.com/$REPO/actions"
fi

echo "Done."
