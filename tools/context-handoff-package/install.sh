#!/usr/bin/env bash
# Install context-handoff rules, hooks, and directories into a target repository.
set -euo pipefail

PACKAGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="$(pwd)"
INSTALL_CURSOR=0
INSTALL_VSCODE=0
INSTALL_WINDSURF=0
INSTALL_DEVIN=0

usage() {
  cat <<'EOF'
Usage: install.sh [options] [TARGET_DIR]

Options:
  --cursor     Install Cursor rules + hooks (automated handoff)
  --vscode     Install VS Code / GitHub Copilot instructions + hooks
  --windsurf   Install Windsurf rule (agent-written handoff)
  --devin      Install Devin rule (agent-written handoff)
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
  local marker="# context-handoff-package"
  local -a lines=(
    ""
    "# context-handoff-package — runtime handoff artifacts (do not commit)"
    ".cursor/handoff/STATE.md"
    ".cursor/handoff/.triggered-*"
    ".github/handoff/STATE.md"
    ".github/handoff/.triggered-*"
    ".windsurf/handoff/STATE.md"
    ".devin/handoff/STATE.md"
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
echo "Installing context-handoff into: $TARGET_DIR"

if [[ "$INSTALL_CURSOR" -eq 1 ]]; then
  echo "→ Cursor"
  copy_tree "$PACKAGE_DIR/templates/cursor/rules" "$TARGET_DIR/.cursor/rules"
  copy_tree "$PACKAGE_DIR/templates/cursor/hooks" "$TARGET_DIR/.cursor/hooks"
  copy_tree "$PACKAGE_DIR/templates/cursor/handoff" "$TARGET_DIR/.cursor/handoff"
  chmod +x "$TARGET_DIR/.cursor/hooks/context-handoff.py" \
            "$TARGET_DIR/.cursor/hooks/session-start-handoff.py"
  python3 "$PACKAGE_DIR/scripts/merge_hooks.py" \
    "$TARGET_DIR/.cursor/hooks.json" \
    "$PACKAGE_DIR/templates/cursor/hooks.json.fragment"
fi

if [[ "$INSTALL_VSCODE" -eq 1 ]]; then
  echo "→ VS Code (GitHub Copilot)"
  copy_tree "$PACKAGE_DIR/templates/vscode/instructions" "$TARGET_DIR/.github/instructions"
  copy_tree "$PACKAGE_DIR/templates/vscode/handoff" "$TARGET_DIR/.github/handoff"
  mkdir -p "$TARGET_DIR/.github/hooks"
  cp "$PACKAGE_DIR/templates/vscode/hooks/"*.py "$TARGET_DIR/.github/hooks/"
  chmod +x "$TARGET_DIR/.github/hooks/context-handoff.py" \
            "$TARGET_DIR/.github/hooks/session-start-handoff.py"
  python3 "$PACKAGE_DIR/scripts/merge_vscode_hooks.py" \
    "$TARGET_DIR/.github/hooks/context-handoff.json" \
    "$PACKAGE_DIR/templates/vscode/hooks/context-handoff.json"
fi

if [[ "$INSTALL_WINDSURF" -eq 1 ]]; then
  echo "→ Windsurf"
  copy_tree "$PACKAGE_DIR/templates/windsurf/rules" "$TARGET_DIR/.windsurf/rules"
  copy_tree "$PACKAGE_DIR/templates/windsurf/handoff" "$TARGET_DIR/.windsurf/handoff"
fi

if [[ "$INSTALL_DEVIN" -eq 1 ]]; then
  echo "→ Devin"
  copy_tree "$PACKAGE_DIR/templates/devin/rules" "$TARGET_DIR/.devin/rules"
  copy_tree "$PACKAGE_DIR/templates/devin/handoff" "$TARGET_DIR/.devin/handoff"
fi

copy_tree "$PACKAGE_DIR/templates/shared/session-logs" "$TARGET_DIR/.session-logs"
append_gitignore

echo "Done. Run: bash \"$PACKAGE_DIR/verify.sh\" \"$TARGET_DIR\""
