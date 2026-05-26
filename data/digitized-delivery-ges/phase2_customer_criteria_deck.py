#!/usr/bin/env python3
"""
Build a PowerPoint appendix: one slide per criterion bullet from the two Phase 2
readiness slides, each listing **Customer Name** values **split by SD-WAN vs Cat-C/SDA**,
plus confirmed rules, engagement process, and a **separate** slide for **>0%–<80%**
interim-pipeline accounts (not mixed with ≥80% motion/RACI cohorts).

Default base deck: SaC_NaC_Adoption_Plan.pptx (for theme/layouts). Output is a copy
with the new section appended.
"""

from __future__ import annotations

import argparse
import shutil
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Callable

from openpyxl import load_workbook
from pptx import Presentation
from pptx.enum.shapes import PP_PLACEHOLDER
from pptx.util import Pt

PHASE1_TECHS = frozenset({"SD-WAN", "Cat-C/SDA"})
TECH_ORDER = ("SD-WAN", "Cat-C/SDA")
PARITY_THRESH = 0.80
MAX_NAMES_PER_TECH = 38
MAX_NAMES_PER_COLUMN = 45


@dataclass(frozen=True)
class ScopedRow:
    customer: str
    technology: str
    parity_pct: Any  # float 0..1 or None
    parity_complete: Any
    segment: str


def _col_index(headers: list[Any], name: str) -> int:
    for i, h in enumerate(headers, start=1):
        if h == name:
            return i
    raise KeyError(name)


def _is_num(v: Any) -> bool:
    return isinstance(v, (int, float)) and v == v


def _pct_value(v: Any) -> float | None:
    if not _is_num(v):
        return None
    return float(v)


def load_scoped_rows(xlsx: Path) -> list[ScopedRow]:
    wb = load_workbook(xlsx, data_only=True)
    ws = wb["as-code score"]
    headers = [ws.cell(1, c).value for c in range(1, ws.max_column + 1)]
    c_cust = _col_index(headers, "Customer Name")
    c_tech = _col_index(headers, "Technologies")
    c_pct = _col_index(headers, "NaC Parity %")
    c_comp = _col_index(headers, "NaC Parity Complete")
    c_seg = _col_index(headers, "Customer Segment")
    out: list[ScopedRow] = []
    for r in range(2, ws.max_row + 1):
        cust = ws.cell(r, c_cust).value
        if cust is None or not str(cust).strip():
            continue
        tech = str(ws.cell(r, c_tech).value or "").strip()
        if tech not in PHASE1_TECHS:
            continue
        seg_v = ws.cell(r, c_seg).value
        seg = str(seg_v).strip() if seg_v is not None and str(seg_v).strip() else ""
        out.append(
            ScopedRow(
                customer=str(cust).strip(),
                technology=tech,
                parity_pct=ws.cell(r, c_pct).value,
                parity_complete=ws.cell(r, c_comp).value,
                segment=seg,
            )
        )
    wb.close()
    return out


def _unique_sorted(customers: set[str]) -> list[str]:
    return sorted(customers, key=str.casefold)


def tech_lists(rows: list[ScopedRow], row_ok: Callable[[ScopedRow], bool]) -> dict[str, list[str]]:
    """Customers with ≥1 scoped row of each technology satisfying row_ok."""
    d = {"SD-WAN": set(), "Cat-C/SDA": set()}
    for r in rows:
        if r.technology not in d:
            continue
        if not row_ok(r):
            continue
        d[r.technology].add(r.customer)
    return {t: _unique_sorted(d[t]) for t in TECH_ORDER}


def tech_lists_for_criterion(
    spec: dict[str, Any],
    mapping: dict[str, set[str]],
    rows: list[ScopedRow],
) -> dict[str, list[str]]:
    sid = spec["id"]
    m = mapping
    if sid == "s11_1":
        return tech_lists(rows, lambda r: True)
    if sid == "s11_2":
        return tech_lists(rows, lambda r: _pct_value(r.parity_pct) is not None)
    if sid == "s11_3":
        return tech_lists(
            rows,
            lambda r: (p := _pct_value(r.parity_pct)) is not None and p >= PARITY_THRESH,
        )
    if sid == "s11_4":
        return tech_lists(
            rows,
            lambda r: r.customer in m["s11_4_lt80_with_pct"]
            and (p := _pct_value(r.parity_pct)) is not None
            and p < PARITY_THRESH,
        )
    if sid == "s11_5":
        return tech_lists(
            rows,
            lambda r: r.customer in m["s11_5_missing_pct_any_row"]
            and _pct_value(r.parity_pct) is None,
        )
    if sid == "s12_1":
        return tech_lists(rows, lambda r: True)
    if sid in ("s12_2", "s12_3", "s12_4"):
        return tech_lists(
            rows,
            lambda r: (p := _pct_value(r.parity_pct)) is not None and p >= PARITY_THRESH,
        )
    if sid == "s12_motion_mid":
        return tech_lists(
            rows,
            lambda r: r.customer in m["s12_motion_mid"]
            and (p := _pct_value(r.parity_pct)) is not None
            and 0 < p < PARITY_THRESH,
        )
    if sid == "s12_5":
        return tech_lists(
            rows,
            lambda r: r.customer in m["s12_5_data_gaps"]
            and (
                _pct_value(r.parity_pct) is None
                or not (r.segment or "").strip()
            ),
        )
    raise KeyError(f"no tech list rule for {sid}")


def build_customer_sets(rows: list[ScopedRow]) -> dict[str, set[str]]:
    """Map criterion_id -> set of customer names (deduped). Rules documented in deck."""
    all_cust = {r.customer for r in rows}

    cust_max_pct: dict[str, float] = {}
    cust_has_numeric = set()
    cust_has_missing_pct = set()
    cust_has_lt80 = set()
    cust_has_ge80 = set()
    cust_blank_segment = set()

    for r in rows:
        if not r.segment.strip():
            cust_blank_segment.add(r.customer)
        p = _pct_value(r.parity_pct)
        if p is None:
            cust_has_missing_pct.add(r.customer)
        else:
            cust_has_numeric.add(r.customer)
            if p >= PARITY_THRESH:
                cust_has_ge80.add(r.customer)
            else:
                cust_has_lt80.add(r.customer)
            prev = cust_max_pct.get(r.customer)
            if prev is None or p > prev:
                cust_max_pct[r.customer] = p

    # ≥80% on at least one scoped row (Phase 2 candidate pool from data)
    cust_phase2_candidate = {c for c, mx in cust_max_pct.items() if mx >= PARITY_THRESH}

    # Has numeric % on some row but best row still <80%
    cust_lt80_only = {
        c
        for c in cust_has_numeric
        if cust_max_pct.get(c, 0.0) < PARITY_THRESH
    }

    # Interim pipeline: has ≥1 scoped row with 0% < parity < 80%, and never hits ≥80% gate
    cust_mid_motion = set()
    for c in cust_lt80_only:
        for r in rows:
            if r.customer != c:
                continue
            p = _pct_value(r.parity_pct)
            if p is not None and 0 < p < PARITY_THRESH:
                cust_mid_motion.add(c)
                break

    return {
        "s11_1_plan_scope": set(all_cust),
        "s11_2_any_numeric_pct": set(cust_has_numeric),
        "s11_3_ge80_candidate": set(cust_phase2_candidate),
        "s11_4_lt80_with_pct": set(cust_lt80_only),
        "s11_5_missing_pct_any_row": set(cust_has_missing_pct),
        "s11_6_any_pct": set(cust_has_numeric),
        "s11_6_ge80": set(cust_phase2_candidate),
        "s12_1_threshold_gate": set(all_cust),
        "s12_2_complete_yes_ge80": {
            r.customer for r in rows if _pct_value(r.parity_pct) is not None and _pct_value(r.parity_pct) >= PARITY_THRESH
        },
        "s12_3_motion_cohort": set(cust_phase2_candidate),
        "s12_4_artifacts_cohort": set(cust_phase2_candidate),
        "s12_motion_mid": set(cust_mid_motion),
        "s12_5_data_gaps": set(cust_has_missing_pct) | set(cust_blank_segment),
    }


CRITERIA_SLIDES: list[dict[str, Any]] = [
    {
        "id": "s11_1",
        "title": "Criterion — Phase 2 adoption intent (plan)",
        "criterion": (
            "Adoption plan (Phase 2): engage and strategize with customers at ~80%+ "
            "NaC feature parity; final % TBD per strategy deck (**)."
        ),
        "key": "s11_1_plan_scope",
    },
    {
        "id": "s11_2",
        "title": "Criterion — Parity % coverage (scoped rows)",
        "criterion": (
            "Readiness view: count of SD-WAN + Cat-C/SDA rows with a numeric NaC Parity % "
            "vs total scoped rows. Customers listed = any scoped customer with ≥1 row "
            "where NaC Parity % is numeric."
        ),
        "key": "s11_2_any_numeric_pct",
    },
    {
        "id": "s11_3",
        "title": "Criterion — At/above 80% parity (Phase 2 candidate rows)",
        "criterion": (
            "NaC Parity % ≥ 80% on at least one SD-WAN or Cat-C/SDA row. Customers listed "
            "= unique names meeting that max-row threshold."
        ),
        "key": "s11_3_ge80_candidate",
    },
    {
        "id": "s11_4",
        "title": "Criterion — Below 80% best parity (but has numeric %)",
        "criterion": (
            "Customer’s best (max) NaC Parity % across scoped rows is <80%, while at least "
            "one scoped row has a numeric %. Prioritize parity uplift / access / gating."
        ),
        "key": "s11_4_lt80_with_pct",
    },
    {
        "id": "s11_5",
        "title": "Criterion — Missing numeric parity % (any scoped row)",
        "criterion": (
            "Customer has ≥1 SD-WAN or Cat-C/SDA row without a numeric NaC Parity %. "
            "Parity exercise / access / parsing still needed."
        ),
        "key": "s11_5_missing_pct_any_row",
    },
    {
        "id": "s11_6",
        "title": "Criterion — Any % vs ≥80% (single composite bullet)",
        "criterion": (
            "Original slide combined: (A) customers with any parseable parity % on scoped rows; "
            "(B) customers hitting ≥80% on ≥1 scoped row. Each part lists **SD-WAN** then **Cat-C/SDA**."
        ),
        "dual_keys": ("s11_6_any_pct", "s11_6_ge80"),
        "dual_labels": ("Customers with any numeric % (scoped)", "Customers ≥80% on ≥1 scoped row"),
    },
    {
        "id": "s11_7",
        "title": "Criterion — Segment mix (≥80% parity rows)",
        "criterion": (
            "Original summary bullet: segment distribution among ≥80% parity rows. "
            "Below: customers grouped by Customer Segment on qualifying rows."
        ),
        "multi_segment_ge80": True,
    },
    {
        "id": "s12_1",
        "title": "Criterion — Parity gate (workbook snapshot)",
        "criterion": (
            "Treat NaC Parity % ≥80% as the Phase 2 parity gate for this workbook. "
            "Customers listed = all customers with ≥1 scoped SD-WAN/Cat-C row (program scope)."
        ),
        "key": "s12_1_threshold_gate",
    },
    {
        "id": "s12_2",
        "title": "Criterion — NaC Parity Complete on ≥80% rows",
        "criterion": (
            "Customers appearing on ≥1 scoped row with NaC Parity % ≥80% (sheet completion "
            "field varies; list is the engagement-relevant cohort)."
        ),
        "key": "s12_2_complete_yes_ge80",
    },
    {
        "id": "s12_3",
        "title": "Criterion — Plan motion cohort (engineer + SDA / seller)",
        "criterion": (
            "From plan: engineer + SDA / service seller motion. **Only ≥80% interim-gate "
            "customers** (≥1 scoped row with NaC Parity % ≥ 0.80). Customers with 0%–80% "
            "parity are on the separate interim-pipeline slide."
        ),
        "key": "s12_3_motion_cohort",
    },
    {
        "id": "s12_4",
        "title": "Criterion — RACI & journey map cohort",
        "criterion": (
            "Plan: RACI + journey map per architecture. **Same cohort as the ≥80% interim "
            "gate only** (does not include 0%–80% pipeline accounts — see separate slide)."
        ),
        "key": "s12_4_artifacts_cohort",
    },
    {
        "id": "s12_motion_mid",
        "title": "Motion cohort — parity >0% and <80% (interim pipeline)",
        "criterion": (
            "Separate pipeline motion per leadership: customers with **no** row at/above "
            "the 80% interim gate, but **≥1** scoped SD-WAN or Cat-C/SDA row with **0% < "
            "NaC Parity % < 80%**. Lists split by technology (Customer Name grain)."
        ),
        "key": "s12_motion_mid",
    },
    {
        "id": "s12_5",
        "title": "Criterion — Data hygiene follow-ups",
        "criterion": (
            "Customers needing data follow-up: missing numeric parity % on any scoped row "
            "OR blank Customer Segment on any scoped row (union)."
        ),
        "key": "s12_5_data_gaps",
    },
]


def _ppt_text(s: str) -> str:
    """PowerPoint text fields do not render Markdown; strip emphasis markers."""
    return s.replace("**", "")


def _set_title(slide: Any, text: str) -> None:
    slide.shapes.title.text = _ppt_text(text)


def _body_shape(slide: Any) -> Any:
    for shape in slide.shapes:
        if shape.is_placeholder and shape.placeholder_format.type == PP_PLACEHOLDER.BODY:
            return shape
    raise RuntimeError("No BODY placeholder")


def _fill_body_single_column(slide: Any, paragraphs: list[tuple[int, str]]) -> None:
    """paragraphs: list of (level, text)."""
    body = _body_shape(slide)
    tf = body.text_frame
    tf.clear()
    for i, (level, text) in enumerate(paragraphs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = _ppt_text(text)
        p.level = level
        p.font.size = Pt(11)


def _paragraphs_tech_map(criterion: str, tm: dict[str, list[str]]) -> list[tuple[int, str]]:
    lines: list[tuple[int, str]] = [(0, criterion)]
    for tech in TECH_ORDER:
        names = tm[tech]
        lines.append((0, f"{tech} ({len(names)})"))
        for n in names[:MAX_NAMES_PER_TECH]:
            lines.append((1, n))
        if len(names) > MAX_NAMES_PER_TECH:
            lines.append(
                (1, f"+ {len(names) - MAX_NAMES_PER_TECH} more (see workbook)")
            )
    return lines


def _append_clarifying_slide(prs: Presentation, layout: Any, xlsx_name: str) -> None:
    slide = prs.slides.add_slide(layout)
    _set_title(slide, "Confirmed rules (leadership inputs)")
    lines = [
        (0, "Lists are split **by technology**: SD-WAN vs Cat-C/SDA on each customer slide."),
        (0, "Grain is **Customer Name** as it appears in the readiness workbook (no PID column)."),
        (0, "**80% NaC Parity %** (≥0.80 in-sheet) remains the **interim gate** until a final baseline is published."),
        (0, "**≥80% motion / RACI slides** include only interim-gate customers. **>0% and <80%** accounts are on a **separate interim-pipeline** slide."),
        (0, f"Source workbook: {xlsx_name} · generated {date.today().isoformat()}"),
    ]
    _fill_body_single_column(slide, lines)


def _append_process_slide(prs: Presentation, layout: Any) -> None:
    slide = prs.slides.add_slide(layout)
    _set_title(slide, "Structured engagement process (Phase 2)")
    steps = [
        (0, "1. Prioritize — Confirm **interim ≥80%** gate candidates with theater CDA / segment leads."),
        (0, "2. Align — Match engineer + SDA / service seller; agree account entry criteria."),
        (0, "3. Discover — Start 50K-ft as-code positioning; capture risks, dependencies, timelines."),
        (0, "4. Deepen — Technical and delivery detail as customer familiarity grows."),
        (0, "5. Document — Record resistance / alternatives; log missing features and test gates."),
        (0, "6. Plan — RACI per architecture; journey map for adoption; dev pipeline for gaps."),
        (0, "7. Gate — Go/No-Go on as-code path; refresh parity metrics before scale decisions."),
    ]
    _fill_body_single_column(slide, steps)


def _append_multi_segment_slide(
    prs: Presentation,
    layout_single: Any,
    spec: dict[str, Any],
    rows: list[ScopedRow],
) -> None:
    by_seg: dict[str, list[ScopedRow]] = defaultdict(list)
    for r in rows:
        p = _pct_value(r.parity_pct)
        if p is None or p < PARITY_THRESH:
            continue
        seg = r.segment.strip() if r.segment.strip() else "(blank)"
        by_seg[seg].append(r)
    slide = prs.slides.add_slide(layout_single)
    _set_title(slide, spec["title"])
    lines: list[tuple[int, str]] = [(0, spec["criterion"])]
    for seg in sorted(by_seg.keys(), key=lambda s: (s != "(blank)", s.casefold())):
        seg_rows = by_seg[seg]
        lines.append((0, f"{seg} — {len({r.customer for r in seg_rows})} customers"))
        tm = tech_lists(seg_rows, lambda r: True)
        for tech in TECH_ORDER:
            names = tm[tech]
            lines.append((0, f"  {tech} ({len(names)})"))
            for c in names[:MAX_NAMES_PER_TECH]:
                lines.append((1, c))
            if len(names) > MAX_NAMES_PER_TECH:
                lines.append(
                    (1, f"+ {len(names) - MAX_NAMES_PER_TECH} more in {tech} (see workbook)")
                )
    _fill_body_single_column(slide, lines)


def _append_dual_key_slide(
    prs: Presentation,
    layout_single: Any,
    spec: dict[str, Any],
    mapping: dict[str, set[str]],
    rows: list[ScopedRow],
) -> None:
    k1, k2 = spec["dual_keys"]
    lab1, lab2 = spec["dual_labels"]
    tm1 = tech_lists(
        rows,
        lambda r: r.customer in mapping[k1] and _pct_value(r.parity_pct) is not None,
    )
    tm2 = tech_lists(
        rows,
        lambda r: r.customer in mapping[k2]
        and (p := _pct_value(r.parity_pct)) is not None
        and p >= PARITY_THRESH,
    )
    slide = prs.slides.add_slide(layout_single)
    _set_title(slide, spec["title"])
    lines: list[tuple[int, str]] = [(0, spec["criterion"]), (0, lab1)]
    for tech in TECH_ORDER:
        names = tm1[tech]
        lines.append((0, f"  {tech} ({len(names)})"))
        for n in names[:MAX_NAMES_PER_TECH]:
            lines.append((1, n))
        if len(names) > MAX_NAMES_PER_TECH:
            lines.append(
                (1, f"+ {len(names) - MAX_NAMES_PER_TECH} more in {tech} (see workbook)")
            )
    lines.append((0, lab2))
    for tech in TECH_ORDER:
        names = tm2[tech]
        lines.append((0, f"  {tech} ({len(names)})"))
        for n in names[:MAX_NAMES_PER_TECH]:
            lines.append((1, n))
        if len(names) > MAX_NAMES_PER_TECH:
            lines.append(
                (1, f"+ {len(names) - MAX_NAMES_PER_TECH} more in {tech} (see workbook)")
            )
    _fill_body_single_column(slide, lines)


def _append_criterion_slide(
    prs: Presentation,
    layout_single: Any,
    _layout_two_col: Any,
    spec: dict[str, Any],
    mapping: dict[str, set[str]],
    rows: list[ScopedRow],
) -> None:
    if spec.get("multi_segment_ge80"):
        _append_multi_segment_slide(prs, layout_single, spec, rows)
        return

    if "dual_keys" in spec:
        _append_dual_key_slide(prs, layout_single, spec, mapping, rows)
        return

    tm = tech_lists_for_criterion(spec, mapping, rows)
    slide = prs.slides.add_slide(layout_single)
    _set_title(slide, spec["title"])
    _fill_body_single_column(slide, _paragraphs_tech_map(spec["criterion"], tm))


def build_deck(
    *,
    base_ppt: Path,
    xlsx: Path,
    out_ppt: Path,
) -> None:
    shutil.copy2(base_ppt, out_ppt)
    prs = Presentation(str(out_ppt))
    layouts = list(prs.slide_layouts)
    layout_single = layouts[19]  # Title, 1 Column with Bullets
    layout_two = layouts[20]  # Title, 2 Columns with Bullets

    sec = prs.slides.add_slide(layout_single)
    _set_title(sec, "Appendix — Phase 2 criteria → customers (SD-WAN & Cat-C/SDA)")
    _fill_body_single_column(
        sec,
        [
            (0, "Following slides: one per criterion from the Phase 2 readiness summary."),
            (0, "Each slide lists **Customer Name** values, split into **SD-WAN** vs **Cat-C/SDA** blocks."),
            (0, "80% parity is an **interim gate** until the business locks the final baseline."),
        ],
    )

    rows = load_scoped_rows(xlsx)
    mapping = build_customer_sets(rows)

    _append_clarifying_slide(prs, layout_single, xlsx.name)
    _append_process_slide(prs, layout_single)

    for spec in CRITERIA_SLIDES:
        _append_criterion_slide(prs, layout_single, layout_two, spec, mapping, rows)

    prs.save(str(out_ppt))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base-ppt", type=Path, default=Path("SaC_NaC_Adoption_Plan.pptx"))
    p.add_argument(
        "--xlsx",
        type=Path,
        default=Path("SaC-NaC Readiness Checklist v1_merged.xlsx"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("Phase2_SD-WAN_CatC_criteria_customer_deck.pptx"),
    )
    args = p.parse_args()
    build_deck(base_ppt=args.base_ppt, xlsx=args.xlsx, out_ppt=args.out)
    print(f"Wrote {args.out.resolve()}")


if __name__ == "__main__":
    main()
