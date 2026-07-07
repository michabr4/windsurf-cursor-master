#!/usr/bin/env python3
"""Generate CONTEXT_HANDOFF_INSTRUCTIONS.pdf from package docs."""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

PACKAGE_DIR = Path(__file__).resolve().parents[1]
OUTPUT = PACKAGE_DIR / "CONTEXT_HANDOFF_INSTRUCTIONS.pdf"


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


class HandoffPDF(FPDF):
    def header(self) -> None:
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(40, 40, 40)
        self.cell(0, 8, ascii_safe("Context Handoff - Install Instructions"), new_x="LMARGIN", new_y="NEXT")
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
        self.set_text_color(20, 20, 20)
        self.multi_cell(0, 7, ascii_safe(title))
        self.ln(1)

    def subsection(self, title: str) -> None:
        self.ln(2)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 6, ascii_safe(title))
        self.ln(1)

    def body(self, text: str) -> None:
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5, ascii_safe(text))
        self.ln(1)

    def bullet(self, text: str) -> None:
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5, ascii_safe(f"  -  {text}"))

    def numbered(self, index: int, text: str) -> None:
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 5, ascii_safe(f"  {index}. {text}"))

    def code_block(self, text: str) -> None:
        self.set_font("Courier", "", 9)
        self.set_fill_color(245, 245, 245)
        self.set_text_color(20, 20, 20)
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
            row_height = 7
            for i, cell in enumerate(row):
                self.cell(col_widths[i], row_height, ascii_safe(cell), border=1)
            self.ln()
        self.ln(2)


def build_pdf() -> None:
    pdf = HandoffPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(10, 10, 10)
    pdf.cell(0, 12, "Context Handoff Package", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 8, "Spoon-fed install guide for your architect", new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(pdf.l_margin)
    pdf.ln(4)

    pdf.body(
        "Long AI sessions lose context when the window compacts or you start a new chat. "
        "This package installs rules and hooks so the agent saves a small handoff (<=400 tokens) "
        "and the next session can resume without rework."
    )

    pdf.section("Fastest path (recommended)")
    pdf.numbered(1, "Open tools/context-handoff-package/PROMPT.md in the repo.")
    pdf.numbered(2, "Copy everything below the horizontal rule line in PROMPT.md.")
    pdf.numbered(3, "Paste into your AI tool (Cursor, VS Code Copilot, Windsurf, or Devin) and send.")
    pdf.numbered(4, "Let the agent run the installer and report the checklist back.")

    pdf.subsection("Or run two commands (repo root)")
    pdf.code_block(
        "bash tools/context-handoff-package/install.sh --all\n"
        "bash tools/context-handoff-package/verify.sh"
    )

    pdf.subsection("Install one tool only")
    pdf.code_block(
        "bash tools/context-handoff-package/install.sh --cursor\n"
        "bash tools/context-handoff-package/install.sh --vscode\n"
        "bash tools/context-handoff-package/install.sh --windsurf\n"
        "bash tools/context-handoff-package/install.sh --devin"
    )

    pdf.section("What gets installed")
    pdf.table(
        ["Tool", "Handoff file", "How it triggers"],
        [
            ["Cursor", ".cursor/handoff/STATE.md", "Hooks in .cursor/hooks.json"],
            ["VS Code", ".github/handoff/STATE.md", "Copilot hooks (.github/hooks/)"],
            ["Windsurf", ".windsurf/handoff/STATE.md", "Rule (agent writes on thresholds)"],
            ["Devin", ".devin/handoff/STATE.md", "Rule (agent writes on thresholds)"],
        ],
        [25, 55, 110],
    )
    pdf.body("All tools also use .session-logs/LAST_SESSION_BRIEF.md (shared brief).")

    pdf.section("Complexity tiers")
    pdf.table(
        ["Tier", "Signals", "Trigger", "Refresh"],
        [
            ["Low", "<=5 tools, <=2 paths, no subagents", "65%", "preCompact only"],
            ["Medium", "Default session", "60%", "preCompact + scope change"],
            ["High", ">=15 tools or >=5 paths or multi-file", "52%", "+12% or scope change"],
            ["Critical", "Subagents or >=25 tools", "45%", "+10%, subagent, or scope"],
        ],
        [22, 70, 22, 76],
    )

    pdf.section("Handoff content (agent enriches)")
    pdf.body("Keep both STATE and LAST_SESSION_BRIEF under 400 tokens total combined.")
    pdf.bullet("Active task - one sentence")
    pdf.bullet("Progress - done vs still open")
    pdf.bullet("Files touched - paths only, no file contents")
    pdf.bullet("Next step - single highest-priority action")
    pdf.bullet("Blockers - only if present")
    pdf.ln(2)
    pdf.body("Never include: secrets, tokens, env values, API responses, or code dumps.")

    pdf.section("Cursor hooks (automated)")
    pdf.table(
        ["Event", "Script", "Behavior"],
        [
            ["afterAgentResponse", "context-handoff.py", "Write/refresh when threshold crossed"],
            ["stop", "context-handoff.py", "Same on agent stop"],
            ["preCompact", "context-handoff.py", "Always write before compaction"],
            ["subagentStop", "context-handoff.py", "Refresh after subagents (critical tier)"],
            ["sessionStart", "session-start-handoff.py", "Inject saved handoff on new session"],
        ],
        [38, 52, 100],
    )

    pdf.section("VS Code hooks (GitHub Copilot)")
    pdf.body(
        "Prerequisites: Agent hooks are preview. Org must allow hooks. "
        "Confirm chat.hookFilesLocations includes .github/hooks. "
        "For monorepo subfolders, enable chat.useCustomizationsInParentRepositories."
    )
    pdf.table(
        ["Event", "Script", "Behavior"],
        [
            ["SessionStart", "session-start-handoff.py", "Inject saved handoff"],
            ["PreCompact", "context-handoff.py", "Always write before compaction"],
            ["Stop", "context-handoff.py", "Write/refresh when threshold crossed"],
            ["SubagentStop", "context-handoff.py", "Refresh after subagents"],
            ["PostToolUse", "context-handoff.py", "Check threshold after each tool"],
        ],
        [32, 52, 106],
    )

    pdf.section("Package files")
    pdf.bullet("PROMPT.md - paste into AI tool")
    pdf.bullet("README.md - full docs and troubleshooting")
    pdf.bullet("COPY_PASTE_FOR_ARCHITECT.md - email/Slack blurb")
    pdf.bullet("install.sh - one-command installer")
    pdf.bullet("verify.sh - post-install checks")

    pdf.section("Troubleshooting")
    pdf.table(
        ["Problem", "Fix"],
        [
            ["verify.sh fails", "Re-run: install.sh --all"],
            ["Cursor hooks not firing", "Enable hooks in Cursor Settings; chmod +x scripts"],
            ["VS Code hooks not firing", "Check org policy; Copilot Chat Hooks output channel"],
            ["Wrong repo path", "install.sh --all /path/to/repo"],
            ["Duplicate hook entries", "Safe to re-run — merge scripts skip duplicates"],
        ],
        [55, 135],
    )

    pdf.section("Done when")
    pdf.bullet('verify.sh prints "All checks passed."')
    pdf.bullet("Do not commit STATE.md, LAST_SESSION_BRIEF.md, or .triggered-* (in .gitignore)")
    pdf.bullet("Architect replies with PROMPT Step 5 checklist")

    pdf.section("Copy to another repo")
    pdf.body(
        "Copy the entire tools/context-handoff-package/ folder into the target repo, "
        "then run install.sh --all or paste PROMPT.md into the AI tool."
    )

    pdf.output(OUTPUT)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    build_pdf()
