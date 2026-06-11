#!/usr/bin/env python3
"""Generate TOKEN_OPTIMIZATION_INSTRUCTIONS.pdf from package docs."""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

PACKAGE_DIR = Path(__file__).resolve().parents[1]
OUTPUT = PACKAGE_DIR / "TOKEN_OPTIMIZATION_INSTRUCTIONS.pdf"


def ascii_safe(text: str) -> str:
    return (
        text.replace("\u2014", "-")
        .replace("\u2013", "-")
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2022", "-")
        .replace("\u2264", "<=")
    )


class TokenOptPDF(FPDF):
    def header(self) -> None:
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(40, 40, 40)
        self.cell(0, 8, ascii_safe("Token Optimization - Install Instructions"), new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)
        self.set_x(self.l_margin)

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"Page {self.page_no()}", align="C")

    def section(self, title: str) -> None:
        self.ln(3)
        self.set_font("Helvetica", "B", 13)
        self.multi_cell(0, 7, ascii_safe(title))
        self.ln(1)

    def subsection(self, title: str) -> None:
        self.ln(2)
        self.set_font("Helvetica", "B", 11)
        self.multi_cell(0, 6, ascii_safe(title))
        self.ln(1)

    def body(self, text: str) -> None:
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 5, ascii_safe(text))
        self.ln(1)

    def bullet(self, text: str) -> None:
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 5, ascii_safe(f"  -  {text}"))

    def numbered(self, index: int, text: str) -> None:
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 5, ascii_safe(f"  {index}. {text}"))

    def code_block(self, text: str) -> None:
        self.set_font("Courier", "", 9)
        self.set_fill_color(245, 245, 245)
        for line in text.strip().splitlines():
            self.cell(0, 5, f"  {line}", new_x="LMARGIN", new_y="NEXT", fill=True)
        self.ln(2)

    def table(self, headers: list[str], rows: list[list[str]], col_widths: list[int]) -> None:
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(230, 230, 230)
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 7, ascii_safe(header), border=1, fill=True)
        self.ln()
        self.set_font("Helvetica", "", 8)
        for row in rows:
            self.set_x(self.l_margin)
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 7, ascii_safe(cell), border=1)
            self.ln()
        self.ln(2)


def build_pdf() -> None:
    pdf = TokenOptPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, "Token Optimization Package", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 8, "Target: ~88% context overhead reduction", new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(pdf.l_margin)
    pdf.ln(4)

    pdf.body(
        "Baseline was ~72% overhead reduction (14,400 tokens saved/session). "
        "This package installs P0 glob-gating fixes and P1 protocol rules from TOKEN_OPTIMIZATION_PLAN.md."
    )

    pdf.section("Fastest path (recommended)")
    pdf.numbered(1, "Open tools/token-optimization-package/PROMPT.md")
    pdf.numbered(2, "Copy everything below the horizontal rule line")
    pdf.numbered(3, "Paste into Cursor, VS Code Copilot, Windsurf, or Devin")
    pdf.numbered(4, "Agent runs installer and returns Step 5 checklist")

    pdf.subsection("Or run two commands (repo root)")
    pdf.code_block(
        "bash tools/token-optimization-package/install.sh --all\n"
        "bash tools/token-optimization-package/verify.sh"
    )

    pdf.section("P0 - Glob-gate heavy rules (done)")
    pdf.table(
        ["Rule", "Fix", "Tokens freed"],
        [
            ["effectiveness-signals", "alwaysApply false + code globs", "~1,840/session"],
            ["codeguard crypto (Cursor)", "alwaysApply false + globs", "~500/session"],
            ["codeguard certs (Cursor)", "alwaysApply false + cert globs", "~485/session"],
            ["effectiveness (Windsurf)", "alwaysApply false + globs", "~1,170/session"],
        ],
        [52, 78, 60],
    )
    pdf.body("P0 total: ~4,000 tokens/session on sessions that do not touch code files.")

    pdf.section("P1 - New protocol rules")
    pdf.subsection("model-routing.md")
    pdf.bullet("Route LOW complexity to haiku, MEDIUM to sonnet, HIGH to opus")
    pdf.bullet('Emit [ROUTING] telemetry line at task start')
    pdf.bullet("~75% cost reduction on routed low-complexity tasks")

    pdf.subsection("spec-length-cap.md")
    pdf.bullet("spec <= 300 tokens; files_to_read <= 5 items")
    pdf.bullet("No inline file contents or rule re-statements in specs")
    pdf.bullet("~20,000 tokens/month at 100 tasks")

    pdf.subsection("session-warm-up.md")
    pdf.bullet("Read only LAST_SESSION_BRIEF.md + .comms/active/ at session start")
    pdf.bullet("Never scan .comms/completed/ or full activity reports")
    pdf.bullet("~16,000 tokens/month at 20 sessions")

    pdf.subsection("comms-retention.md")
    pdf.bullet("Cap .comms/completed/ at 20 files")
    pdf.bullet("Move older files to .comms/archive/ at session end")
    pdf.bullet("~60% less directory listing noise in pipeline scans")

    pdf.section("Cumulative impact")
    pdf.table(
        ["Phase", "Tokens/session", "Monthly (20 sessions)"],
        [
            ["Baseline", "14,400", "288,000"],
            ["+ P0 glob fixes", "+4,000", "+80,000"],
            ["+ P1 warm-up", "+800", "+16,000"],
            ["+ P1 spec cap (avg)", "+667", "+13,400"],
            ["New total", "~19,867", "~397,400"],
        ],
        [55, 55, 80],
    )
    pdf.body("New reduction: approximately 88% overhead vs unoptimized baseline.")

    pdf.section("What gets installed")
    pdf.table(
        ["Tool", "Files", "Location"],
        [
            ["Cursor", "7 rules", ".cursor/rules/"],
            ["VS Code", "7 instructions", ".github/instructions/"],
            ["Windsurf", "5 rules", ".windsurf/rules/"],
            ["Devin", "5 rules", ".devin/rules/"],
        ],
        [28, 28, 134],
    )
    pdf.body("Also creates .comms/archive/ and .session-logs/")

    pdf.section("P2 backlog (not installed by package)")
    pdf.bullet("Compress heavy codeguard rule files to fast-path summaries")
    pdf.bullet("Deduplicate .windsurf vs .cursor codeguard copies")
    pdf.bullet("Cap project-progress-tracker update frequency")
    pdf.body("Implement P2 only when explicitly requested.")

    pdf.section("Works with context-handoff")
    pdf.body(
        "Install both packages for full coverage. session-warm-up reads LAST_SESSION_BRIEF.md; "
        "context-handoff-package writes it. No conflict."
    )
    pdf.code_block(
        "bash tools/context-handoff-package/install.sh --all\n"
        "bash tools/token-optimization-package/install.sh --all"
    )

    pdf.section("Done when")
    pdf.bullet('verify.sh prints "All checks passed."')
    pdf.bullet("P0 rules show alwaysApply: false with globs (Cursor/Windsurf)")
    pdf.bullet("Architect returns PROMPT Step 5 checklist")

    pdf.section("Package files")
    pdf.bullet("PROMPT.md - AI install prompt")
    pdf.bullet("COPY_PASTE_FOR_ARCHITECT.md - email blurb")
    pdf.bullet("TOKEN_OPTIMIZATION_PLAN.md - full plan")
    pdf.bullet("install.sh / verify.sh / generate-pdf.sh")

    pdf.output(OUTPUT)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    build_pdf()
