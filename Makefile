.PHONY: token-audit session-prime

# ── Token audit ───────────────────────────────────────────────────────────────
# Usage: make token-audit
token-audit:
	@echo "═══════════════════════════════════════════════════════"
	@echo "  TOKEN AUDIT — Rule file inventory"
	@echo "═══════════════════════════════════════════════════════"
	@echo ""
	@echo "── Always-on rules (alwaysApply: true) ──────────────"
	@for f in .cursor/rules/*.md .windsurf/rules/*.md; do \
		[ -f "$$f" ] || continue; \
		grep -q "alwaysApply: true" "$$f" 2>/dev/null || continue; \
		size=$$(wc -c < "$$f"); \
		tok=$$(( size / 4 )); \
		flag=""; \
		[ $$size -gt 2000 ] && flag=" ⚠️  LARGE"; \
		printf "  %6d bytes (~%4d tok)  %s%s\n" "$$size" "$$tok" "$$f" "$$flag"; \
	done | sort -rn
	@echo ""
	@echo "── Rules with no frontmatter (load every session) ───"
	@for f in .cursor/rules/*.md .windsurf/rules/*.md; do \
		[ -f "$$f" ] || continue; \
		head -1 "$$f" | grep -q "^---" || echo "  NO FRONTMATTER: $$f"; \
	done
	@echo ""
	@echo "── Gated rules (alwaysApply: false) ─────────────────"
	@for f in .cursor/rules/*.md .windsurf/rules/*.md; do \
		[ -f "$$f" ] || continue; \
		grep -q "alwaysApply: false" "$$f" 2>/dev/null || continue; \
		size=$$(wc -c < "$$f"); \
		printf "  %6d bytes  %s\n" "$$size" "$$f"; \
	done | sort -rn
	@echo ""
	@echo "── Totals ────────────────────────────────────────────"
	@always_total=0; \
	for f in .cursor/rules/*.md .windsurf/rules/*.md; do \
		[ -f "$$f" ] || continue; \
		grep -q "alwaysApply: true" "$$f" 2>/dev/null || continue; \
		size=$$(wc -c < "$$f"); \
		always_total=$$((always_total + size)); \
	done; \
	tok=$$((always_total / 4)); \
	echo "  Always-on total: $${always_total} bytes (~$${tok} tokens/session)"
	@echo "═══════════════════════════════════════════════════════"

# ── Session primer ────────────────────────────────────────────────────────────
# Usage: make session-prime
session-prime:
	@echo "═══════════════════════════════════════════════════════"
	@echo "  SESSION PRIMER — $(shell date '+%Y-%m-%d %H:%M')"
	@echo "═══════════════════════════════════════════════════════"
	@echo ""
	@echo "── Git ───────────────────────────────────────────────"
	@echo "  Branch : $$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')"
	@echo "  Last   : $$(git log -1 --pretty='%h %s' 2>/dev/null || echo 'no commits')"
	@echo ""
	@echo "── Comms pipeline ───────────────────────────────────"
	@inbox=$$(ls .comms/inbox/*.json 2>/dev/null | wc -l | tr -d ' '); \
	active=$$(ls .comms/active/*.json 2>/dev/null | wc -l | tr -d ' '); \
	outbox=$$(ls .comms/outbox/*.json 2>/dev/null | wc -l | tr -d ' '); \
	echo "  Inbox: $$inbox  Active: $$active  Outbox: $$outbox"
	@if ls .comms/active/*.json 2>/dev/null | head -1 | grep -q json; then \
		echo "  Active task:"; \
		for f in .comms/active/*.json; do \
			id=$$(python3 -c "import json,sys; d=json.load(open('$$f')); print(d.get('id','?'))" 2>/dev/null); \
			title=$$(python3 -c "import json,sys; d=json.load(open('$$f')); print(d.get('title','?'))" 2>/dev/null); \
			echo "    [$$id] $$title"; \
		done; \
	fi
	@if ls .comms/outbox/*.json 2>/dev/null | head -1 | grep -q json; then \
		echo "  ⚠️  Results awaiting review in outbox"; \
	fi
	@echo ""
	@echo "── Recent session logs ───────────────────────────────"
	@if [ -d .session-logs ]; then \
		find .session-logs -name "activity-report.md" | sort -r | head -3 | while read f; do \
			echo "  $$f"; \
		done; \
	else \
		echo "  No session logs yet"; \
	fi
	@echo ""
	@echo "═══════════════════════════════════════════════════════"
