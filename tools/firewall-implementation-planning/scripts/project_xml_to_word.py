#!/usr/bin/env python3
"""
Build a readable .docx task list from an MS Project XML (MSPDI) file.
Names, WBS, durations, predecessors, and notes are in a wide table (no column hiding).

Usage:
  python3 project_xml_to_word.py [input.xml] [output.docx]
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path
import xml.etree.ElementTree as ET

NS = {"p": "http://schemas.microsoft.com/project"}

try:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Inches, Pt
    from docx.oxml import OxmlElement
except ImportError as e:
    print("Install: pip install python-docx", file=sys.stderr)
    raise SystemExit(1) from e


def parse_duration_h(s: str | None) -> float:
    if not s:
        return 0.0
    s = s.strip()
    if s in ("", "PT0H0M0S"):
        return 0.0
    m = re.match(r"^PT(\d+(?:\.\d+)?)H0M0S$", s)
    if m:
        h = float(m.group(1))
        return h / 8.0
    m2 = re.match(r"^PT(\d+(?:\.\d+)?)D$", s)
    if m2:
        return float(m2.group(1))
    return 0.0


def text(el) -> str:
    return el.text.strip() if el is not None and el.text else ""


def task_type_label(summary: bool, milestone: bool) -> str:
    if summary:
        return "Summary"
    if milestone:
        return "Milestone"
    return "Task"


def duration_label(ddays: float, milestone: bool) -> str:
    if milestone and ddays == 0:
        return "0d"
    if ddays > 0:
        return f"{int(ddays)}d" if ddays == int(ddays) else f"{ddays:.1f}d"
    return "0d"


def set_repeat_header_row(table) -> None:
    """First row marked as table header (repeats on new pages in Word)."""
    tr = table.rows[0]._tr
    trPr = tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    trPr.append(tbl_header)


def main() -> int:
    here = Path(__file__).resolve().parent
    project_dir = here.parent / "project"
    xml_path = Path(sys.argv[1]) if len(sys.argv) > 1 else project_dir / "MGM_Palo_to_Cisco_Actionable_Plan.xml"
    out_path = (
        Path(sys.argv[2])
        if len(sys.argv) > 2
        else project_dir / "MGM_Palo_to_Cisco_Actionable_Plan_Task_List.docx"
    )
    if not xml_path.is_file():
        print(f"Missing: {xml_path}", file=sys.stderr)
        return 1

    tree = ET.parse(str(xml_path))
    root = tree.getroot()
    tasks_el = root.find("p:Tasks", NS)
    if tasks_el is None:
        print("No <Tasks> in file", file=sys.stderr)
        return 1

    task_nodes = [t for t in tasks_el.findall("p:Task", NS)]
    if not task_nodes:
        return 1

    def int_id(n):
        id_el = n.find("p:ID", NS)
        if id_el is None or id_el.text is None:
            return 0
        try:
            return int(id_el.text)
        except ValueError:
            return 0

    task_nodes.sort(key=int_id)
    rows: list[dict] = []
    for t in task_nodes:
        uii = t.find("p:UID", NS)
        if uii is None or uii.text is None:
            continue
        uidv = int(uii.text)
        preds = [pl.find("p:PredecessorUID", NS) for pl in t.findall("p:PredecessorLink", NS)]
        pred_list = [text(x) for x in preds if x is not None]
        rows.append(
            {
                "id": int_id(t),
                "uid": uidv,
                "name": text(t.find("p:Name", NS) or t),
                "wbs": text(t.find("p:WBS", NS) or t),
                "summary": text(t.find("p:Summary", NS) or t) in ("1", "true", "True"),
                "milestone": text(t.find("p:Milestone", NS) or t) in ("1", "true", "True"),
                "duration_days": parse_duration_h(text(t.find("p:Duration", NS))),
                "predecessor_uids": [x for x in pred_list if x],
                "notes": text(t.find("p:Notes", NS) or t),
            }
        )
    if not rows:
        return 1

    uid_to_display_id: dict[str, int] = {str(r["uid"]): 1 + r["id"] for r in rows}
    for r in rows:
        p_line = []
        for puid in r["predecessor_uids"]:
            d = uid_to_display_id.get(str(puid))
            if d is not None:
                p_line.append(str(d))
        r["predecessor_rownums"] = ",".join(p_line) if p_line else ""

    doc = Document()
    t_style = doc.styles["Normal"]
    t_style.font.name = "Calibri"
    t_style.font.size = Pt(11)

    title = doc.add_heading("MGM Palo to Cisco: actionable task list", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = meta.add_run(
        f"Source: {xml_path.name}\nGenerated: {date.today().isoformat()}\n"
        f"For scheduling, open the .xml in Microsoft Project or use the Excel import file in this folder."
    )
    run.font.size = Pt(10)
    run.font.italic = True

    doc.add_paragraph(
        "This document lists every task and summary row with full names (readable without fixing spreadsheet columns). "
        "The Row# column matches the first column (ID) in the Excel *Tasks* sheet and is used for predecessor links in Project."
    )

    doc.add_heading("All tasks", level=1)
    col_headers = [
        "Row#",
        "WBS",
        "Task name",
        "Type",
        "Duration",
        "Predecessors (row#)",
        "Notes",
    ]
    w_table = doc.add_table(rows=1 + len(rows), cols=len(col_headers), style="Table Grid")
    set_repeat_header_row(w_table)

    hdr = w_table.rows[0].cells
    for c, h in enumerate(col_headers):
        hdr[c].text = h
        for p in hdr[c].paragraphs:
            for r in p.runs:
                r.font.bold = True
                r.font.size = Pt(9)

    for i, r in enumerate(rows, start=1):
        ddays = r["duration_days"]
        cells = w_table.rows[i].cells
        cells[0].text = str(1 + r["id"])
        cells[1].text = r["wbs"]
        cells[2].text = r["name"]
        cells[3].text = task_type_label(r["summary"], r["milestone"])
        cells[4].text = duration_label(ddays, r["milestone"])
        cells[5].text = r["predecessor_rownums"] or "—"
        cells[6].text = r["notes"] or "—"
        for c in range(7):
            for p in cells[c].paragraphs:
                p.paragraph_format.space_after = Pt(0)
                for run in p.runs:
                    run.font.size = Pt(9 if c != 2 else 10)

    w_table.autofit = False
    w_table.columns[0].width = Inches(0.5)
    w_table.columns[1].width = Inches(0.6)
    w_table.columns[2].width = Inches(2.4)
    w_table.columns[3].width = Inches(0.7)
    w_table.columns[4].width = Inches(0.6)
    w_table.columns[5].width = Inches(0.9)
    w_table.columns[6].width = Inches(1.4)

    doc.add_page_break()
    doc.add_heading("Quick import tips", level=1)
    tips = [
        "Open MGM_Palo_to_Cisco_Actionable_Plan.xml in Microsoft Project (desktop) to get a full Gantt; save as .mpp if needed.",
        "To import from Excel, prefer the .xlsx file, widen the Name column if it looks blank, and map Predecessors to the row numbers shown above.",
    ]
    for t in tips:
        doc.add_paragraph(t, style="List Bullet")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out_path))
    print(f"Wrote: {out_path} ({len(rows)} tasks)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
