#!/usr/bin/env sh
# Run workbench CLI from repo root with correct PYTHONPATH.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PYTHONPATH="${ROOT}/python${PYTHONPATH:+:${PYTHONPATH}}"
cd "$ROOT"
exec python3 -m workbench "$@"
