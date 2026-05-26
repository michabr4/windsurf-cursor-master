#!/usr/bin/env python3
"""
Read MS Project XML (MSPDI) and write an Excel file for *Import from Excel* in Microsoft Project.
Usage:
  python3 project_xml_to_excel.py [input.xml] [output.xlsx]

Column names are chosen to map easily in the Project import wizard.
"""
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

NS = {"p": "http://schemas.microsoft.com/project"}

try:
    import xlsxwriter
except ImportError as e:
    print("Install: pip install xlsxwriter", file=sys.stderr)
    raise SystemExit(1) from e

try:
    import xlwt
except ImportError:
    xlwt = None


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
    m2 = re.match(r"^PT(\d+(?:\.\d+)?)D$", s)  # rare
    if m2:
        return float(m2.group(1))
    return 0.0


def text(el) -> str:
    return el.text.strip() if el is not None and el.text else ""


def main() -> int:
    here = Path(__file__).resolve().parent
    project_dir = here.parent / "project"
    xml_path = Path(sys.argv[1]) if len(sys.argv) > 1 else project_dir / "MGM_Palo_to_Cisco_Actionable_Plan.xml"
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else project_dir / "MGM_Palo_to_Cisco_Actionable_Plan_Import.xlsx"
    out_xls = out_path.with_suffix(".xls")
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
    by_uid: dict[str, int] = {}
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
                "outline": int(text(t.find("p:OutlineLevel", NS) or t) or 0),
                "summary": text(t.find("p:Summary", NS) or t) in ("1", "true", "True"),
                "milestone": text(t.find("p:Milestone", NS) or t) in ("1", "true", "True"),
                "duration_days": parse_duration_h(text(t.find("p:Duration", NS))),
                "predecessor_uids": [x for x in pred_list if x],
                "notes": text(t.find("p:Notes", NS) or t),
            }
        )
    if not rows:
        return 1

    uid_to_display_id: dict[str, int] = {}
    for r in rows:
        uid_to_display_id[str(r["uid"])] = 1 + r["id"]  # Project row # ≈ 1+ID; ID is 0-based index

    for r in rows:
        p_line = []
        for puid in r["predecessor_uids"]:
            d = uid_to_display_id.get(str(puid))
            if d is not None:
                p_line.append(str(d))
        r["predecessor_rownums"] = ",".join(p_line) if p_line else ""

    out_path.parent.mkdir(parents=True, exist_ok=True)
    book = xlsxwriter.Workbook(str(out_path))
    ws = book.add_worksheet("Tasks")
    h_style = book.add_format({"bold": True, "bg_color": "#D7E3BC", "border": 1, "valign": "top"})
    cell = book.add_format({"border": 1, "valign": "top", "text_wrap": True})
    dcell = book.add_format({"border": 1, "valign": "top", "num_format": "0.###"})

    headers = [
        "ID",
        "WBS",
        "Name",
        "Duration (days)",
        "Duration_Project",  # e.g. 5d for mapping
        "Outline_Level",
        "Summary_YN",
        "Milestone_YN",
        "Predecessors",  # row# in *this* sheet, 1-based, per Project import
        "Notes",
    ]
    for col, h in enumerate(headers):
        ws.write(0, col, h, h_style)
    for row_idx, r in enumerate(rows, start=1):
        ddays = r["duration_days"]
        if r["milestone"] and ddays == 0:
            d_proj = "0d"
        elif ddays > 0:
            d_proj = f"{int(ddays)}d" if ddays == int(ddays) else f"{ddays:.1f}d"
        else:
            d_proj = "0d"
        ws.write(row_idx, 0, 1 + r["id"], dcell)
        ws.write_string(row_idx, 1, r["wbs"], cell)
        ws.write_string(row_idx, 2, r["name"], cell)
        ws.write_number(row_idx, 3, ddays, dcell)
        ws.write_string(row_idx, 4, d_proj, cell)
        ws.write_number(row_idx, 5, r["outline"], dcell)
        ws.write_string(row_idx, 6, "Y" if r["summary"] else "N", cell)
        ws.write_string(row_idx, 7, "Y" if r["milestone"] else "N", cell)
        ws.write_string(row_idx, 8, r["predecessor_rownums"], cell)
        ws.write_string(row_idx, 9, r["notes"], cell)

    ws.set_column(0, 0, 5)
    ws.set_column(1, 1, 9)
    ws.set_column(2, 2, 56)
    ws.set_column(3, 4, 14)
    ws.set_column(5, 7, 12)
    ws.set_column(8, 8, 20)
    ws.set_column(9, 9, 48)
    ws.freeze_panes(1, 0)

    help_s = book.add_worksheet("Import_Instructions")
    t = book.add_format({"text_wrap": True, "valign": "top"})
    steps = [
        "Import this workbook into Microsoft Project (desktop)",
        "1) File → New → blank project, or an existing template you use.",
        "2) File → Open — if your build has 'Get Data' or 'Open from Excel' use the path below; else:",
        "   In many versions: New from Excel Workbook, or: Project → Import Wizard (may vary by SKU).",
        "3) For **Import Export Wizard** (if shown):",
        "   - Select the **Tasks** sheet (first tab).",
        "   - Map: **Name** → Name; **Duration_Project** → Duration; **WBS** → WBS; **Predecessors** → Predecessors; **Milestone_YN** → (optional) Milestone if offered.",
        "   - **Predecessors** uses **row numbers** of other tasks in this file (1 = first data row, same as the row order in the 'Tasks' sheet, matching **ID** column in column A).",
        "4) After import: set **Project** → **Project Information** (start date), and **Link** the schedule if not auto-calculated. Review the network diagram.",
        "5) The XML file in this folder (MGM_Palo_to_Cisco_Actionable_Plan.xml) is an alternate; use XML **Open** if the Excel import loses links.",
    ]
    for i, s in enumerate(steps):
        help_s.write(i, 0, s, t)
    help_s.set_column(0, 0, 110)

    book.close()
    print(f"Wrote: {out_path} ({len(rows)} tasks)", file=sys.stderr)

    if xlwt is not None:
        wbx = xlwt.Workbook()
        s1 = wbx.add_sheet("Tasks")
        for c, x in enumerate(headers):
            s1.write(0, c, x)
        for i, r in enumerate(rows, start=1):
            ddays = r["duration_days"]
            if r["milestone"] and ddays == 0:
                d_proj = "0d"
            elif ddays > 0:
                d_proj = f"{int(ddays)}d" if ddays == int(ddays) else f"{ddays:.1f}d"
            else:
                d_proj = "0d"
            s1.write(i, 0, 1 + r["id"])
            s1.write(i, 1, r["wbs"])
            s1.write(i, 2, r["name"])
            s1.write(i, 3, ddays)
            s1.write(i, 4, d_proj)
            s1.write(i, 5, r["outline"])
            s1.write(i, 6, "Y" if r["summary"] else "N")
            s1.write(i, 7, "Y" if r["milestone"] else "N")
            s1.write(i, 8, r["predecessor_rownums"])
            s1.write(i, 9, r["notes"])
        s2 = wbx.add_sheet("Readme")
        s2.write(0, 0, "For Microsoft Project: use New from Excel, or Import, map the Tasks columns. Or open the .xlsx version.")
        wbx.save(str(out_xls))
        print(f"Wrote: {out_xls} (Excel 97-2003 .xls)", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
