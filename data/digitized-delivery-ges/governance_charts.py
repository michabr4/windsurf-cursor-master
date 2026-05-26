"""
Governance-oriented charts derived from the `as-code score` grid.

Adds sheets:
- Governance_Data — small summary tables (source for chart ranges).
- Governance_Charts — embedded Excel charts (no extra Python dependencies).

Intended for leadership / program reviews: parity completion mix overall,
by technology, and by customer segment.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.chart.data_source import AxDataSource, StrRef
from openpyxl.chart.label import DataLabelList
from workbook_analytics import _last_data_row

DATA_SHEET = "Governance_Data"
CHART_SHEET = "Governance_Charts"
TOP_TECH = 15


def _fix_category_strrefs(chart: Any) -> None:
    """
    openpyxl ChartBase.set_categories() always uses numRef; Excel expects strRef
    for text category labels and may fail to open or strip charts otherwise.
    """
    charts = getattr(chart, "_charts", None)
    iterable = charts if charts else (chart,)
    for ch in iterable:
        for ser in getattr(ch, "ser", ()) or ():
            cat = getattr(ser, "cat", None)
            if cat is None:
                continue
            nref = getattr(cat, "numRef", None)
            if nref is not None and getattr(nref, "f", None):
                f = nref.f
                ser.cat = AxDataSource(strRef=StrRef(f=f))


def _norm_parity_complete(value: Any) -> str:
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


def _cell_str(ws: Any, row: int, col: int) -> str:
    v = ws.cell(row=row, column=col).value
    if v is None:
        return "(unknown)"
    s = str(v).strip()
    return s if s else "(unknown)"


def _aggregate(ws: Any, h: dict[str, int]) -> tuple[Counter, dict[str, Counter], dict[str, Counter]]:
    c_cust = h["Customer Name"]
    c_tech = h["Technologies"]
    c_seg = h["Customer Segment"]
    c_comp = h["NaC Parity Complete"]
    last = _last_data_row(ws, c_cust)
    overall: Counter = Counter()
    by_tech: dict[str, Counter] = defaultdict(Counter)
    by_seg: dict[str, Counter] = defaultdict(Counter)
    for r in range(2, last + 1):
        if not _cell_str(ws, r, c_cust) or _cell_str(ws, r, c_cust) == "(unknown)":
            continue
        st = _norm_parity_complete(ws.cell(row=r, column=c_comp).value)
        overall[st] += 1
        by_tech[_cell_str(ws, r, c_tech)][st] += 1
        by_seg[_cell_str(ws, r, c_seg)][st] += 1
    return overall, by_tech, by_seg


def _rollup_top(
    by_dim: dict[str, Counter],
    top_n: int,
) -> list[tuple[str, Counter]]:
    scored = sorted(
        ((sum(ctr.values()), k, ctr) for k, ctr in by_dim.items()),
        key=lambda t: -t[0],
    )
    if len(scored) <= top_n:
        return [(k, ctr) for _, k, ctr in scored]
    top = scored[:top_n]
    tail = scored[top_n:]
    merged: Counter = Counter()
    for _, _, ctr in tail:
        merged.update(ctr)
    out = [(k, ctr) for _, k, ctr in top]
    out.append((f"Other ({len(tail)} groups)", merged))
    return out


def _write_overall(ws: Any, overall: Counter, row: int) -> tuple[int, int]:
    """Return (header_row, last_data_row) for chart references."""
    ws.cell(row=row, column=1, value="NaC Parity Complete — all customer × technology rows")
    ws.cell(row=row + 1, column=1, value="Status")
    ws.cell(row=row + 1, column=2, value="Count")
    order = ("Yes", "No", "Other")
    r = row + 2
    for label in order:
        ws.cell(row=r, column=1, value=label)
        ws.cell(row=r, column=2, value=overall.get(label, 0))
        r += 1
    for label, n in sorted(overall.items()):
        if label in order:
            continue
        ws.cell(row=r, column=1, value=label)
        ws.cell(row=r, column=2, value=n)
        r += 1
    return row + 1, r - 1


def _write_matrix(
    ws: Any,
    title: str,
    rows_dim: list[tuple[str, Counter]],
    start_row: int,
) -> tuple[int, int]:
    """
    Write [Dimension, Yes, No, Other] with header row at start_row.
    Returns (header_row, last_data_row).
    """
    ws.cell(row=start_row, column=1, value=title)
    hdr = start_row + 1
    ws.cell(row=hdr, column=1, value="Dimension")
    for i, colname in enumerate(("Yes", "No", "Other"), start=2):
        ws.cell(row=hdr, column=i, value=colname)
    r = hdr + 1
    for dim, ctr in rows_dim:
        ws.cell(row=r, column=1, value=dim)
        ws.cell(row=r, column=2, value=ctr.get("Yes", 0))
        ws.cell(row=r, column=3, value=ctr.get("No", 0))
        ws.cell(row=r, column=4, value=ctr.get("Other", 0))
        r += 1
    return hdr, r - 1


def _remove_sheet_if_present(wb: Any, title: str) -> None:
    if title in wb.sheetnames:
        del wb[title]


def add_governance_charts(wb: Any, score_sheet_name: str, h: dict[str, int]) -> None:
    required = ("Customer Name", "Technologies", "Customer Segment", "NaC Parity Complete")
    if not all(k in h for k in required):
        return

    ws_score = wb[score_sheet_name]
    overall, by_tech, by_seg = _aggregate(ws_score, h)

    _remove_sheet_if_present(wb, CHART_SHEET)
    _remove_sheet_if_present(wb, DATA_SHEET)

    ws_d = wb.create_sheet(DATA_SHEET)
    ws_d.cell(row=1, column=1, value="Source data for governance charts (regenerate via merge script).")

    hdr_o, last_o = _write_overall(ws_d, overall, row=3)

    gap1 = last_o + 3
    tech_rows = _rollup_top(by_tech, TOP_TECH)
    hdr_t, last_t = _write_matrix(ws_d, f"By technology (top {TOP_TECH} by row count)", tech_rows, gap1)

    gap2 = last_t + 3
    seg_rows = list(by_seg.items())
    seg_rows.sort(key=lambda x: -sum(x[1].values()))
    hdr_s, last_s = _write_matrix(ws_d, "By customer segment", seg_rows, gap2)

    ws_c = wb.create_sheet(CHART_SHEET, min(2, len(wb.sheetnames)))
    ws_c.cell(row=1, column=1, value="NaC readiness — governance views (refresh when workbook is merged).")

    # --- Pie: overall parity completion ---
    pie = PieChart()
    pie.title = "NaC Parity Complete — distribution (all rows)"
    labels = Reference(ws_d, min_col=1, min_row=hdr_o + 1, max_row=last_o)
    data = Reference(ws_d, min_col=2, min_row=hdr_o, max_row=last_o)
    pie.add_data(data, titles_from_data=True)
    pie.set_categories(labels)
    _fix_category_strrefs(pie)
    pie.dataLabels = DataLabelList()
    pie.dataLabels.showPercent = True
    pie.width = 16
    pie.height = 11
    ws_c.add_chart(pie, "A3")

    # --- Stacked bar: technology ---
    bar_t = BarChart()
    bar_t.type = "bar"
    bar_t.grouping = "stacked"
    bar_t.title = "NaC Parity Complete by technology (stacked)"
    bar_t.y_axis.title = "Technology"
    bar_t.x_axis.title = "Row count"
    data_t = Reference(ws_d, min_col=2, min_row=hdr_t, max_col=4, max_row=last_t)
    cats_t = Reference(ws_d, min_col=1, min_row=hdr_t + 1, max_row=last_t)
    bar_t.add_data(data_t, titles_from_data=True)
    bar_t.set_categories(cats_t)
    _fix_category_strrefs(bar_t)
    bar_t.width = 18
    bar_t.height = 12
    ws_c.add_chart(bar_t, "K3")

    # --- Stacked bar: segment ---
    bar_s = BarChart()
    bar_s.type = "bar"
    bar_s.grouping = "stacked"
    bar_s.title = "NaC Parity Complete by customer segment (stacked)"
    bar_s.y_axis.title = "Segment"
    bar_s.x_axis.title = "Row count"
    data_s = Reference(ws_d, min_col=2, min_row=hdr_s, max_col=4, max_row=last_s)
    cats_s = Reference(ws_d, min_col=1, min_row=hdr_s + 1, max_row=last_s)
    bar_s.add_data(data_s, titles_from_data=True)
    bar_s.set_categories(cats_s)
    _fix_category_strrefs(bar_s)
    bar_s.width = 18
    bar_s.height = 11
    ws_c.add_chart(bar_s, "A28")

    # Extend used range so sheet dimension covers chart anchors (avoids odd Excel layout).
    ws_c.cell(row=42, column=1, value="Chart ranges: see Governance_Data.")


def _header_by_name(ws: Any) -> dict[str, int]:
    by_name: dict[str, int] = {}
    for c in range(1, ws.max_column + 1):
        v = ws.cell(row=1, column=c).value
        if v is not None and str(v).strip():
            by_name[str(v).strip()] = c
    return by_name


def main() -> None:
    """Refresh governance sheets on an existing workbook (default: merged output)."""
    import argparse
    from pathlib import Path

    from openpyxl import load_workbook

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "workbook",
        nargs="?",
        type=Path,
        default=Path("SaC-NaC Readiness Checklist v1_merged.xlsx"),
        help="Path to .xlsx containing `as-code score`",
    )
    args = p.parse_args()
    wb = load_workbook(args.workbook)
    ws = wb["as-code score"]
    h = _header_by_name(ws)
    add_governance_charts(wb, "as-code score", h)
    wb.save(args.workbook)
    print(f"Updated governance sheets in {args.workbook.resolve()}")


if __name__ == "__main__":
    main()
