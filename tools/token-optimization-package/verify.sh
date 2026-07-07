#!/usr/bin/env bash
# Verify token-optimization installation in a target repository.
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

check_glob_false() {
  local path="$1"
  if [[ -f "$TARGET_DIR/$path" ]] && grep -q "alwaysApply: false" "$TARGET_DIR/$path"; then
    echo "✓ $path has alwaysApply: false"
  elif [[ -f "$TARGET_DIR/$path" ]]; then
    echo "✗ $path should have alwaysApply: false (P0 glob gate)"
    FAIL=1
  fi
}

echo "Verifying token-optimization in: $TARGET_DIR"
echo

if [[ -d "$TARGET_DIR/.cursor/rules" ]]; then
  echo "Cursor:"
  for rule in model-routing spec-length-cap session-warm-up comms-retention effectiveness-signals \
    codeguard-1-crypto-algorithms codeguard-1-digital-certificates; do
    check "rule" ".cursor/rules/${rule}.md"
  done
  check_glob_false ".cursor/rules/effectiveness-signals.md"
  check_glob_false ".cursor/rules/codeguard-1-crypto-algorithms.md"
  check_glob_false ".cursor/rules/codeguard-1-digital-certificates.md"
  echo
fi

if [[ -d "$TARGET_DIR/.github/instructions" ]] || ls "$TARGET_DIR/.github/instructions/"*token* >/dev/null 2>&1; then
  echo "VS Code:"
  for rule in model-routing spec-length-cap session-warm-up comms-retention effectiveness-signals \
    codeguard-1-crypto-algorithms codeguard-1-digital-certificates; do
    check "instructions" ".github/instructions/${rule}.instructions.md"
  done
  echo
fi

if [[ -d "$TARGET_DIR/.windsurf/rules" ]]; then
  echo "Windsurf:"
  for rule in model-routing spec-length-cap session-warm-up comms-retention effectiveness-signals; do
    check "rule" ".windsurf/rules/${rule}.md"
  done
  check_glob_false ".windsurf/rules/effectiveness-signals.md"
  echo
fi

if [[ -d "$TARGET_DIR/.devin/rules" ]]; then
  echo "Devin:"
  for rule in model-routing spec-length-cap session-warm-up comms-retention effectiveness-signals; do
    check "rule" ".devin/rules/${rule}.md"
  done
  echo
fi

check "comms archive dir" ".comms/archive/.gitkeep"
check "session logs dir" ".session-logs/.gitkeep"

if [[ "$FAIL" -eq 0 ]]; then
  echo
  echo "All checks passed."
  exit 0
fi

echo
echo "Some checks failed. Re-run: bash \"$PACKAGE_DIR/install.sh\" --all \"$TARGET_DIR\""
exit 1
