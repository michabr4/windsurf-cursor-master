#!/usr/bin/env bash
# Build TOKEN_OPTIMIZATION_INSTRUCTIONS.pdf (creates local venv on first run).
set -euo pipefail

PACKAGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$PACKAGE_DIR/.pdf-venv"

if [[ ! -x "$VENV/bin/python3" ]]; then
  python3 -m venv "$VENV"
  "$VENV/bin/pip" install fpdf2 -q
fi

"$VENV/bin/python3" "$PACKAGE_DIR/scripts/generate_pdf.py"
