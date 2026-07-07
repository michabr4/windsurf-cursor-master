#!/usr/bin/env bash
# session-primer.sh — print a compact context brief at the start of a new session
# Usage: bash scripts/session-primer.sh
# Or add to your shell profile: alias prime='cd ~/path/to/repo && bash scripts/session-primer.sh'

set -euo pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null || echo ".")"

echo "═══════════════════════════════════════════════════════"
echo "  SESSION PRIMER — $(date '+%Y-%m-%d %H:%M %Z')"
echo "═══════════════════════════════════════════════════════"

# Git context
echo ""
echo "── Git ───────────────────────────────────────────────"
echo "  Branch : $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')"
echo "  Last   : $(git log -1 --pretty='%h %s' 2>/dev/null || echo 'no commits')"
dirty=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
[[ "$dirty" -gt 0 ]] && echo "  ⚠️  $dirty uncommitted change(s)"

# Comms pipeline
echo ""
echo "── Comms pipeline ───────────────────────────────────"
inbox=$(ls .comms/inbox/*.json 2>/dev/null | wc -l | tr -d ' ')
active=$(ls .comms/active/*.json 2>/dev/null | wc -l | tr -d ' ')
outbox=$(ls .comms/outbox/*.json 2>/dev/null | wc -l | tr -d ' ')
echo "  Inbox: $inbox  Active: $active  Outbox: $outbox"

for f in .comms/active/*.json; do
  [[ -f "$f" ]] || continue
  id=$(python3 -c "import json; d=json.load(open('$f')); print(d.get('id','?'))" 2>/dev/null)
  title=$(python3 -c "import json; d=json.load(open('$f')); print(d.get('title','?'))" 2>/dev/null)
  echo "  → ACTIVE: [$id] $title"
done

for f in .comms/outbox/*.json; do
  [[ -f "$f" ]] || continue
  id=$(python3 -c "import json; d=json.load(open('$f')); print(d.get('task_id','?'))" 2>/dev/null)
  status=$(python3 -c "import json; d=json.load(open('$f')); print(d.get('status','?'))" 2>/dev/null)
  echo "  ⚠️  OUTBOX: [$id] status=$status — needs Windsurf review"
done

# Inbox preview (top 3 by priority)
if [[ "$inbox" -gt 0 ]]; then
  echo ""
  echo "  Pending tasks:"
  python3 - <<'EOF' 2>/dev/null || true
import json, os, glob
tasks = []
for f in glob.glob(".comms/inbox/*.json"):
    try:
        with open(f) as fh:
            d = json.load(fh)
        tasks.append((d.get("priority","low"), d.get("id","?"), d.get("title","?")))
    except Exception:
        pass
order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
tasks.sort(key=lambda x: order.get(x[0], 9))
for pri, tid, title in tasks[:5]:
    print(f"    [{pri:8}] {tid} — {title}")
EOF
fi

# Recent session logs
echo ""
echo "── Recent session logs ───────────────────────────────"
if [[ -d .session-logs ]]; then
  mapfile -t logs < <(find .session-logs -name "activity-report.md" | sort -r | head -3)
  if [[ ${#logs[@]} -gt 0 ]]; then
    for log in "${logs[@]}"; do
      echo "  $log"
    done
  else
    echo "  None"
  fi
else
  echo "  No session logs yet"
fi

# Token health snapshot
echo ""
echo "── Token health ─────────────────────────────────────"
always_total=0
always_count=0
for f in .cursor/rules/*.md .windsurf/rules/*.md; do
  [[ -f "$f" ]] || continue
  grep -q "alwaysApply: true" "$f" 2>/dev/null || continue
  size=$(wc -c < "$f")
  always_total=$((always_total + size))
  always_count=$((always_count + 1))
done
tok=$((always_total / 4))
echo "  Always-on rules: $always_count files · $always_total bytes · ~$tok tokens/session"
[[ $always_total -gt 15000 ]] && echo "  ⚠️  Above 15KB threshold — run 'make token-audit'"

echo ""
echo "═══════════════════════════════════════════════════════"
