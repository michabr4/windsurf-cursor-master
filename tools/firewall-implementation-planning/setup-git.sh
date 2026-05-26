#!/bin/bash
# Run once in Terminal: bash setup-git.sh
set -euo pipefail
cd "$(dirname "$0")"

if [[ -d .git ]]; then
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Git already initialized in: $(pwd)"
    git status -sb
    exit 0
  else
    echo "Removing incomplete .git folder and re-initializing..."
    rm -rf .git
  fi
fi

git init
git branch -M main
git add README.md .gitignore setup-git.sh
git commit -m "Initial commit: empty planning repo"
echo
echo "Done. Repository: $(pwd)"
git log -1 --oneline
