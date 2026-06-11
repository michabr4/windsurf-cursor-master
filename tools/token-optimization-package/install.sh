#!/usr/bin/env bash
# Install token-optimization rules and directories into a target repository.
set -euo pipefail

PACKAGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="$(pwd)"
INSTALL_CURSOR=0
INSTALL_VSCODE=0
INSTALL_WINDSURF=0
INSTALL_DEVIN=0

RULES_CURSOR=(
  model-routing.md
  spec-length-cap.md
  session-warm-up.md
  comms-retention.md
  effectiveness-signals.md
  codeguard-1-crypto-algorithms.md
  codeguard-1-digital-certificates.md
)

RULES_WINDSURF=(
  model-routing.md
  spec-length-cap.md
  session-warm-up.md
  comms-retention.md
  effectiveness-signals.md
)

RULES_DEVIN=(
  model-routing.md
  spec-length-cap.md
  session-warm-up.md
  comms-retention.md
  effectiveness-signals.md
)

usage() {
  cat <<'EOF'
Usage: install.sh [options] [TARGET_DIR]

Options:
  --cursor     Install Cursor rules (P0 globs + P1 protocols)
  --vscode     Install VS Code / GitHub Copilot instructions
  --windsurf   Install Windsurf rules
  --devin      Install Devin rules
  --all        Install all of the above (default)
  --help       Show this help

Examples:
  ./install.sh --all
  ./install.sh --cursor /path/to/repo
  ./install.sh --vscode --windsurf
EOF
}

copy_tree() {
  local src="$1"
  local dest="$2"
  mkdir -p "$dest"
  if command -v rsync >/dev/null 2>&1; then
    rsync -a "$src/" "$dest/"
  else
    cp -R "$src/." "$dest/"
  fi
}

append_gitignore() {
  local file="$TARGET_DIR/.gitignore"
  local marker="# token-optimization-package"
  local -a lines=(
    ""
    "# token-optimization-package — runtime artifacts (do not commit)"
    ".session-logs/LAST_SESSION_BRIEF.md"
  )
  touch "$file"
  if ! grep -qF "$marker" "$file"; then
    printf '%s\n' "${lines[@]}" >>"$file"
    return 0
  fi
  local line
  for line in "${lines[@]}"; do
    [[ -z "$line" || "$line" == "$marker" ]] && continue
    if ! grep -qF "$line" "$file"; then
      echo "$line" >>"$file"
    fi
  done
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cursor) INSTALL_CURSOR=1; shift ;;
    --vscode) INSTALL_VSCODE=1; shift ;;
    --windsurf) INSTALL_WINDSURF=1; shift ;;
    --devin) INSTALL_DEVIN=1; shift ;;
    --all) INSTALL_CURSOR=1; INSTALL_VSCODE=1; INSTALL_WINDSURF=1; INSTALL_DEVIN=1; shift ;;
    --help|-h) usage; exit 0 ;;
    -*) echo "Unknown option: $1" >&2; usage; exit 1 ;;
    *)
      TARGET_DIR="$(cd "$1" && pwd)"
      shift
      ;;
  esac
done

if [[ "$INSTALL_CURSOR$INSTALL_VSCODE$INSTALL_WINDSURF$INSTALL_DEVIN" == "0000" ]]; then
  INSTALL_CURSOR=1
  INSTALL_VSCODE=1
  INSTALL_WINDSURF=1
  INSTALL_DEVIN=1
fi

cd "$TARGET_DIR"
echo "Installing token-optimization into: $TARGET_DIR"

python3 "$PACKAGE_DIR/scripts/convert_to_vscode_instructions.py" >/dev/null

if [[ "$INSTALL_CURSOR" -eq 1 ]]; then
  echo "→ Cursor"
  mkdir -p "$TARGET_DIR/.cursor/rules"
  for rule in "${RULES_CURSOR[@]}"; do
    cp "$PACKAGE_DIR/templates/cursor/rules/$rule" "$TARGET_DIR/.cursor/rules/$rule"
  done
fi

if [[ "$INSTALL_VSCODE" -eq 1 ]]; then
  echo "→ VS Code (GitHub Copilot)"
  copy_tree "$PACKAGE_DIR/templates/vscode/instructions" "$TARGET_DIR/.github/instructions"
fi

if [[ "$INSTALL_WINDSURF" -eq 1 ]]; then
  echo "→ Windsurf"
  mkdir -p "$TARGET_DIR/.windsurf/rules"
  for rule in "${RULES_WINDSURF[@]}"; do
    cp "$PACKAGE_DIR/templates/windsurf/rules/$rule" "$TARGET_DIR/.windsurf/rules/$rule"
  done
fi

if [[ "$INSTALL_DEVIN" -eq 1 ]]; then
  echo "→ Devin"
  mkdir -p "$TARGET_DIR/.devin/rules"
  for rule in "${RULES_DEVIN[@]}"; do
    cp "$PACKAGE_DIR/templates/devin/rules/$rule" "$TARGET_DIR/.devin/rules/$rule"
  done
fi

copy_tree "$PACKAGE_DIR/templates/shared/comms/archive" "$TARGET_DIR/.comms/archive"
copy_tree "$PACKAGE_DIR/templates/shared/session-logs" "$TARGET_DIR/.session-logs"
append_gitignore

echo "Done. Run: bash \"$PACKAGE_DIR/verify.sh\" \"$TARGET_DIR\""
