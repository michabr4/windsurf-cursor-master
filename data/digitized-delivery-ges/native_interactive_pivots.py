"""
Pivot-style analytics on `Pivot_Analytics` — **static value tables** (no PivotTable XML).

openpyxl-generated native PivotTables often fail Excel validation (repair on open).
These grids match the intent of the old views: Customer × Technology counts and
Segment × NaC Parity Complete counts, recomputed on each merge.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

STATIC_PIVOT_SHEETS = (
    "Pivot_by_Technology",
    "Pivot_SD-WAN_CatC_by_Segment",
    "Pivot_Customer_priority_tech",
    "Pivot_Customer_Tech",
    "Pivot_Segment_Complete",
)


def _last_data_row(ws: Any, c_customer: int) -> int:
    last = 1
    for r in range(2, ws.max_row + 1):
        v = ws.cell(row=r, column=c_customer).value
        if v is not None and str(v).strip():
            last = r
    return last


def _remove_static_pivot_sheets(wb: Any) -> None:
    for title in STATIC_PIVOT_SHEETS:
        if title in wb.sheetnames:
            del wb[title]


def _norm_complete(value: Any) -> str:
    if value is None:
        return "Other"
    s = str(value).strip()
    if not s:
        return "Other"
    low = s.lower()
    if low == "yes":
        return "Yes"
    if low == "no":
        return "No"
    return "Other"


def _str_cell(ws: Any, r: int, c: int) -> str:
    v = ws.cell(row=r, column=c).value
    if v is None:
        return "(blank)"
    s = str(v).strip()
    return s if s else "(blank)"


def _write_matrix(
    ws: Any,
    *,
    title: str,
    start_row: int,
    row_labels: list[str],
    col_labels: list[str],
    counts: dict[tuple[str, str], int],
) -> int:
    """Write title + matrix; return next free row below block."""
    ws.cell(row=start_row, column=1, value=title)
    hdr = start_row + 1
    ws.cell(row=hdr, column=1, value="")
    for j, colname in enumerate(col_labels, start=2):
        ws.cell(row=hdr, column=j, value=colname)
    r = hdr + 1
    for rowname in row_labels:
        ws.cell(row=r, column=1, value=rowname)
        for j, colname in enumerate(col_labels, start=2):
            ws.cell(row=r, column=j, value=int(counts.get((rowname, colname), 0)))
        r += 1
    return r + 1


def add_native_interactive_pivots(wb: Any, score_sheet_name: str, h: dict[str, int]) -> None:
    """
    Build `Pivot_Analytics` as static cross-tabs (no pivotCache / pivotTable parts).
    Clears any workbook pivots list so the package does not emit broken pivot XML.
    """
    _remove_static_pivot_sheets(wb)
    for sheet in wb.worksheets:
        sheet._pivots = []
    wb._pivots = []

    ws = wb[score_sheet_name]
    c_cust = h["Customer Name"]
    c_tech = h["Technologies"]
    c_seg = h["Customer Segment"]
    c_comp = h["NaC Parity Complete"]
    last_r = _last_data_row(ws, c_cust)
    if last_r < 2:
        return

    ct_cust_tech: Counter[tuple[str, str]] = Counter()
    ct_seg_comp: Counter[tuple[str, str]] = Counter()

    for r in range(2, last_r + 1):
        if not _str_cell(ws, r, c_cust) or _str_cell(ws, r, c_cust) == "(blank)":
            continue
        cust = _str_cell(ws, r, c_cust)
        tech = _str_cell(ws, r, c_tech)
        seg = _str_cell(ws, r, c_seg)
        comp = _norm_complete(ws.cell(row=r, column=c_comp).value)
        ct_cust_tech[(cust, tech)] += 1
        ct_seg_comp[(seg, comp)] += 1

    customers = sorted({p[0] for p in ct_cust_tech})
    techs = sorted({p[1] for p in ct_cust_tech})
    segments = sorted({p[0] for p in ct_seg_comp})
    comps = ("Yes", "No", "Other")

    if "Pivot_Analytics" in wb.sheetnames:
        del wb["Pivot_Analytics"]
    ps = wb.create_sheet("Pivot_Analytics", 1)
    ps.cell(row=1, column=1, value="Static pivot-style summaries (rebuilt each merge; filter/sort in Excel).")

    next_row = _write_matrix(
        ps,
        title="Customer × Technology — row counts",
        start_row=3,
        row_labels=customers,
        col_labels=techs,
        counts=ct_cust_tech,
    )
    _write_matrix(
        ps,
        title="Customer Segment × NaC Parity Complete — row counts (Yes/No/Other)",
        start_row=next_row + 1,
        row_labels=segments,
        col_labels=list(comps),
        counts=ct_seg_comp,
    )
