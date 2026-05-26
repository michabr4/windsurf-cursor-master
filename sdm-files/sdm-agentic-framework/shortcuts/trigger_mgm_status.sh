#!/bin/bash
# Trigger MGM Status Report via GitHub API
# This can be called from iOS Shortcuts via SSH or Webhook

GITHUB_TOKEN="${GITHUB_TOKEN:-YOUR_TOKEN_HERE}"
REPO="michabr4/mgm-status-bot"
WORKFLOW="daily-report.yml"

curl -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Content-Type: application/json" \
  "https://api.github.com/repos/$REPO/actions/workflows/$WORKFLOW/dispatches" \
  -d '{"ref":"master"}'

echo "✅ MGM Status Report triggered!"
