#!/usr/bin/env python3
"""
Append two slides to the adoption plan deck: Phase 2 criteria (from the plan)
plus a readiness snapshot derived from `SaC-NaC Readiness Checklist v1_merged.xlsx`.

Phase 2 in the plan: engage customers at ~80%+ NaC feature parity (SD-WAN / Cat-C
parity collection context). Threshold here is NaC Parity % >= 0.80 on each row.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

from openpyxl import load_workbook
from pptx import Presentation
from pptx.enum.shapes import PP_PLACEHOLDER
from pptx.util import Pt


PHASE1_TECHS = frozenset({"SD-WAN", "Cat-C/SDA"})
PARITY_THRESH = 0.80


def _col_index(headers: list[Any], name: str) -> int:
    for i, h in enumerate(headers, start=1):
        if h == name:
            return i
    raise KeyError(name)


def _is_num(v: Any) -> bool:
    return isinstance(v, (int, float)) and v == v


def compute_readiness_metrics(xlsx: Path) -> dict[str, Any]:
    wb = load_workbook(xlsx, data_only=True)
    ws = wb["as-code score"]
    headers = [ws.cell(1, c).value for c in range(1, ws.max_column + 1)]
    c_cust = _col_index(headers, "Customer Name")
    c_tech = _col_index(headers, "Technologies")
    c_pct = _col_index(headers, "NaC Parity %")
    c_comp = _col_index(headers, "NaC Parity Complete")
    c_seg = _col_index(headers, "Customer Segment")

    scoped: list[tuple[str, str, Any, Any, str]] = []
    for r in range(2, ws.max_row + 1):
        cust = ws.cell(r, c_cust).value
        if cust is None or not str(cust).strip():
            continue
        tech = str(ws.cell(r, c_tech).value or "").strip()
        if tech not in PHASE1_TECHS:
            continue
        pct = ws.cell(r, c_pct).value
        comp = ws.cell(r, c_comp).value
        seg_v = ws.cell(r, c_seg).value
        seg = str(seg_v).strip() if seg_v is not None and str(seg_v).strip() else "(blank)"
        scoped.append((str(cust).strip(), tech, pct, comp, seg))

    wb.close()

    has_pct = [x for x in scoped if _is_num(x[2])]
    ge = [x for x in scoped if _is_num(x[2]) and float(x[2]) >= PARITY_THRESH]
    lt = [x for x in scoped if _is_num(x[2]) and float(x[2]) < PARITY_THRESH]
    no_pct = [x for x in scoped if not _is_num(x[2])]

    cust_max: dict[str, float] = {}
    for cust, _, pct, _, _ in scoped:
        if _is_num(pct):
            v = float(pct)
            cust_max[cust] = max(cust_max.get(cust, 0.0), v)

    cust_any_pct = len(cust_max)
    cust_ge = sum(1 for v in cust_max.values() if v >= PARITY_THRESH)

    seg_ct = Counter(x[4] for x in ge)
    comp_ct = Counter(
        str(x[3]).strip() if x[3] is not None else "(blank)" for x in ge
    )

    return {
        "scoped_rows": len(scoped),
        "rows_with_pct": len(has_pct),
        "rows_ge_thresh": len(ge),
        "rows_lt_thresh": len(lt),
        "rows_no_pct": len(no_pct),
        "unique_customers_any_pct": cust_any_pct,
        "unique_customers_ge_thresh": cust_ge,
        "segment_ge": seg_ct,
        "complete_ge": comp_ct,
        "xlsx_name": xlsx.name,
    }


def _set_body_bullets(slide: Any, lines: list[str]) -> None:
    body = None
    for shape in slide.shapes:
        if shape.is_placeholder and shape.placeholder_format.type == PP_PLACEHOLDER.BODY:
            body = shape
            break
    if body is None:
        raise RuntimeError("No BODY placeholder on slide layout")
    tf = body.text_frame
    tf.clear()
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.level = 0
        if p.font.size is None:
            p.font.size = Pt(14)


def append_slides(
    ppt_in: Path,
    ppt_out: Path,
    metrics: dict[str, Any],
) -> None:
    prs = Presentation(str(ppt_in))
    layout = prs.slide_layouts[19]  # "Title, 1 Column with Bullets" (same as Phase 2 slide)

    # --- Slide A: criteria + data snapshot ---
    s1 = prs.slides.add_slide(layout)
    s1.shapes.title.text = "Phase 2 — readiness snapshot vs. 80% parity bar"
    foot = f"Source: {metrics['xlsx_name']} · SD-WAN & Cat-C/SDA rows only · generated {date.today().isoformat()}"
    seg_ge = metrics["segment_ge"]
    seg_line = ", ".join(f"{k}: {v}" for k, v in seg_ge.most_common(6))

    lines_a = [
        "Adoption plan (Phase 2): engage and strategize with customers at ~80%+ NaC feature parity; final % TBD per strategy deck (**).",
        f"Readiness view: {metrics['scoped_rows']} rows for SD-WAN + Cat-C/SDA; "
        f"{metrics['rows_with_pct']} rows have a numeric NaC Parity %.",
        f"At/above 80% parity (NaC Parity % ≥ {int(PARITY_THRESH * 100)}%): {metrics['rows_ge_thresh']} rows — candidate pool for Phase 2 conversations.",
        f"Below 80% but with %: {metrics['rows_lt_thresh']} rows — prioritize parity uplift, access, or gating before Phase 2.",
        f"No numeric parity %: {metrics['rows_no_pct']} rows — parity exercise / data still needed.",
        f"Customers (scoped techs) with any parseable %: {metrics['unique_customers_any_pct']}; "
        f"customers hitting ≥80% on at least one scoped row: {metrics['unique_customers_ge_thresh']}.",
        f"Segment mix for ≥80% rows: {seg_line}.",
        foot,
    ]
    _set_body_bullets(s1, lines_a)

    # --- Slide B: plan operating criteria tied to sheet fields ---
    s2 = prs.slides.add_slide(layout)
    s2.shapes.title.text = "Phase 2 — plan criteria mapped to readiness data"
    comp_ge = metrics["complete_ge"]
    comp_str = ", ".join(f"{k}: {v}" for k, v in comp_ge.most_common())

    lines_b = [
        "Threshold: treat NaC Parity % ≥ 80% as the Phase 2 parity gate for this workbook snapshot (aligns to deck baseline pending final data).",
        f"Among ≥80% scoped rows, NaC Parity Complete distribution: {comp_str} (sheet tracks survey completion / parity state).",
        "Plan motion (not in sheet): engineer + SDA / service seller for sales motion; document resistance; feed missing features to dev with test timeline.",
        "Plan artifacts (not in sheet): project plan + RACI per architecture; journey map for adoption.",
        "Next data actions: close the 46 scoped rows without numeric % so the ≥80% pool is not understated; validate segment fields where blank.",
        foot,
    ]
    _set_body_bullets(s2, lines_b)

    prs.save(str(ppt_out))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ppt", type=Path, default=Path("SaC_NaC_Adoption_Plan.pptx"))
    p.add_argument(
        "--xlsx",
        type=Path,
        default=Path("SaC-NaC Readiness Checklist v1_merged.xlsx"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("SaC_NaC_Adoption_Plan_phase2_readiness_slides.pptx"),
    )
    args = p.parse_args()

    m = compute_readiness_metrics(args.xlsx)
    append_slides(args.ppt, args.out, m)
    print(f"Wrote {args.out.resolve()} with 2 new slides (Phase 2 + readiness).")


if __name__ == "__main__":
    main()
