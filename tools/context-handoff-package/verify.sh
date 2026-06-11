#!/usr/bin/env bash
# Verify context-handoff installation in a target repository.
set -euo pipefail

PACKAGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${1:-$(pwd)}"
FAIL=0

check() {
  local label="$1"
  local path="$2"
  if [[ -e "$TARGET_DIR/$path" ]]; then
    echo "✓ $label ($path)"
  else
    echo "✗ MISSING: $path"
    FAIL=1
  fi
}

echo "Verifying context-handoff in: $TARGET_DIR"
echo

# Cursor (optional but checked if any cursor file exists)
if [[ -d "$TARGET_DIR/.cursor" ]]; then
  echo "Cursor:"
  check "rule" ".cursor/rules/context-handoff.md"
  check "hook script" ".cursor/hooks/context-handoff.py"
  check "session hook" ".cursor/hooks/session-start-handoff.py"
  check "hooks.json" ".cursor/hooks.json"
  if [[ -f "$TARGET_DIR/.cursor/hooks.json" ]]; then
    if grep -q "context-handoff.py" "$TARGET_DIR/.cursor/hooks.json"; then
      echo "✓ hooks.json references context-handoff.py"
    else
      echo "✗ hooks.json missing context-handoff.py entries"
      FAIL=1
    fi
    if grep -q "session-start-handoff.py" "$TARGET_DIR/.cursor/hooks.json"; then
      echo "✓ hooks.json references session-start-handoff.py"
    else
      echo "✗ hooks.json missing session-start-handoff.py entry"
      FAIL=1
    fi
  fi
  check "handoff dir" ".cursor/handoff/.gitkeep"
  echo
fi

# Windsurf
if [[ -d "$TARGET_DIR/.windsurf" ]] || [[ -f "$TARGET_DIR/.windsurf/rules/context-handoff.md" ]]; then
  echo "Windsurf:"
  check "rule" ".windsurf/rules/context-handoff.md"
  check "handoff dir" ".windsurf/handoff/.gitkeep"
  echo
fi

# VS Code (GitHub Copilot)
if [[ -d "$TARGET_DIR/.github/instructions" ]] || [[ -f "$TARGET_DIR/.github/instructions/context-handoff.instructions.md" ]]; then
  echo "VS Code:"
  check "instructions" ".github/instructions/context-handoff.instructions.md"
  check "hook script" ".github/hooks/context-handoff.py"
  check "session hook" ".github/hooks/session-start-handoff.py"
  check "hooks config" ".github/hooks/context-handoff.json"
  if [[ -f "$TARGET_DIR/.github/hooks/context-handoff.json" ]]; then
    if grep -q "context-handoff.py" "$TARGET_DIR/.github/hooks/context-handoff.json"; then
      echo "✓ context-handoff.json references context-handoff.py"
    else
      echo "✗ context-handoff.json missing context-handoff.py entries"
      FAIL=1
    fi
    if grep -q "session-start-handoff.py" "$TARGET_DIR/.github/hooks/context-handoff.json"; then
      echo "✓ context-handoff.json references session-start-handoff.py"
    else
      echo "✗ context-handoff.json missing session-start-handoff.py entry"
      FAIL=1
    fi
  fi
  check "handoff dir" ".github/handoff/.gitkeep"
  echo
fi

# Devin
if [[ -d "$TARGET_DIR/.devin" ]] || [[ -f "$TARGET_DIR/.devin/rules/context-handoff.md" ]]; then
  echo "Devin:"
  check "rule" ".devin/rules/context-handoff.md"
  check "handoff dir" ".devin/handoff/.gitkeep"
  echo
fi

check "session logs dir" ".session-logs/.gitkeep"

if [[ "$FAIL" -eq 0 ]]; then
  echo
  echo "All checks passed."
  exit 0
fi

echo
echo "Some checks failed. Re-run: bash \"$PACKAGE_DIR/install.sh\" --all \"$TARGET_DIR\""
exit 1
