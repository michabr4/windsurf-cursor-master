#!/usr/bin/env python3
"""
Merge Customer NaC Parity Database.xlsx into SaC-NaC Readiness Checklist v1.xlsx.

Rules:
- Catalyst Center -> Cat-C/SDA (Technologies column).
- NaC Parity Complete = Yes iff parsed parity fraction is strictly > 0; otherwise No
  (including unparseable / no-access free text).
- NaC Parity % stored as 0..1 fraction when parseable (Excel convention: 1 = 100%).
  The sheet's percentage number format (e.g. 0%) is applied so values display as 100%, not 1.
- Match rows on Technologies + customer name only when that parity customer already exists
  on the *baseline* SaC-NaC Readiness Checklist v1.xlsx (snapshot before this merge).
- If the customer is not on that baseline, always append a new line (never update an
  existing v1 row). If the customer is on baseline but no (customer, tech) row exists,
  append a new line as before.
- NaC Parity Reviewer is set from survey submitter display name + Your CEC, e.g. "Jane Doe (jdoe)".
- After merge: SD-WAN / Cat-C/SDA rows with no parity % and no survey trace get
  NaC Parity Complete=No and NaC Parity Comments noting the exercise was not completed.
- Pivot_Analytics sheet: static cross-tab counts (no PivotTable XML; avoids Excel repair).
- Governance_Data + Governance_Charts sheets (parity completion views for reviews).
- Rows appended for new customers get the same NaC Score array formula as the template
  (parity merge does not populate that column otherwise).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from openpyxl import load_workbook

from governance_charts import add_governance_charts
from native_interactive_pivots import add_native_interactive_pivots
from workbook_analytics import (
    add_data_table_to_score_sheet,
    apply_sdwan_catcsda_parity_gaps,
    fill_missing_nac_score_formulas,
)

READINESS_PATH = Path("SaC-NaC Readiness Checklist v1.xlsx")
PARITY_PATH = Path("Customer NaC Parity Database.xlsx")
OUTPUT_PATH = Path("SaC-NaC Readiness Checklist v1_merged.xlsx")

NO_PARSE_PHRASES = (
    "n/a",
    "na",
    "no access",
    "no direct access",
    "don't have direct access",
    "dont have direct access",
    "waiting to get access",
    "error in collection",
)


def norm_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def map_technology(raw: Any) -> str:
    if raw is None:
        return ""
    t = str(raw).strip()
    if not t:
        return ""
    key = norm_spaces(t)
    if key == "catalyst center" or "catalyst center" in key:
        return "Cat-C/SDA"
    if "sd-wan" in key or key.replace(" ", "") == "sdwan":
        return "SD-WAN"
    return t


def map_segment_from_region(region: Any) -> str | None:
    if region is None:
        return None
    r = norm_spaces(str(region))
    if not r:
        return None
    if "ges east" in r or r == "ges east":
        return "GES-East"
    if "ges west" in r:
        return "GES-West"
    if "ges central" in r:
        return "GES-Central"
    if "ges premier" in r or "premier" in r:
        return "GES-Premier"
    if r == "other":
        return "Other"
    return None


def parse_parity_pct(raw: Any) -> tuple[float | None, list[float]]:
    """
    Return (fraction_0_to_1, list of percent numbers found for diagnostics).
    fraction uses min(percent_values)/100 when percents found.
    """
    if raw is None:
        return None, []
    text = str(raw).strip()
    if not text:
        return None, []

    low = text.lower()
    for phrase in NO_PARSE_PHRASES:
        if phrase in low:
            return None, []

    pcts = [float(m.group(1)) for m in re.finditer(r"(\d+(?:\.\d+)?)\s*%", text)]
    if pcts:
        m = min(pcts)
        return max(0.0, min(1.0, m / 100.0)), pcts

    if re.fullmatch(r"\d+(?:\.\d+)?", text):
        v = float(text)
        if v <= 1.0:
            return max(0.0, min(1.0, v)), [v * 100.0]
        return max(0.0, min(1.0, v / 100.0)), [v]

    m2 = re.search(r"(\d+(?:\.\d+)?)", text)
    if m2:
        v = float(m2.group(1))
        if v <= 1.0 and "%" not in text:
            return max(0.0, min(1.0, v)), [v * 100.0]
        if v > 1.0:
            return max(0.0, min(1.0, v / 100.0)), [v]

    return None, []


def parity_complete_from_fraction(frac: float | None) -> str:
    if frac is None:
        return "No"
    return "Yes" if frac > 0 else "No"


def format_parity_reviewer(display_name: str, cec: Any) -> str | None:
    """Combine submitter name and CEC ID for NaC Parity Reviewer."""
    name = display_name.strip() if display_name else ""
    cid = str(cec).strip() if cec is not None and str(cec).strip() else ""
    if name and cid:
        if cid.lower() in name.lower():
            return name
        return f"{name} ({cid})"
    if name:
        return name
    if cid:
        return cid
    return None


def collect_baseline_customer_names(ws: Any, col: int) -> list[str]:
    """Distinct Customer Name values from the workbook as loaded (pre-merge baseline)."""
    seen: set[str] = set()
    out: list[str] = []
    for r in range(2, ws.max_row + 1):
        v = ws.cell(row=r, column=col).value
        if v is None or not str(v).strip():
            continue
        s = str(v).strip()
        key = norm_spaces(s)
        if key in seen:
            continue
        seen.add(key)
        out.append(s)
    return out


def customer_on_baseline_readiness(parity_customer: str, baseline_names: list[str]) -> bool:
    return any(customers_match(parity_customer, bn) for bn in baseline_names)


def customers_match(parity_name: str, readiness_name: str) -> bool:
    """
    Exact match, or readiness name is a substring of the parity survey name
    (e.g. DELTA matches Delta Airlines). We intentionally do not match the
    other direction (short parity name inside longer readiness name) so
    Gilead does not collide with Gilead Sciences.
    """
    pn = norm_spaces(parity_name)
    rn = norm_spaces(readiness_name)
    if not pn or not rn:
        return False
    if pn == rn:
        return True
    if len(rn) >= 4 and rn in pn:
        return True
    return False


def read_parity_rows(path: Path) -> list[dict[str, Any]]:
    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb["Sheet1"]
    headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
    idx = {h: i for i, h in enumerate(headers) if h is not None}

    def col(name: str) -> int:
        return idx[name]

    rows_out: list[dict[str, Any]] = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row:
            continue
        cust = row[col("Customer Name")]
        if cust is None or not str(cust).strip():
            continue
        tech_raw = row[col("Technology")]
        tech = map_technology(tech_raw)
        if not tech:
            continue
        completion = row[col("Completion time")]
        nm = row[col("Name")]
        your_nm = row[col("Your Name")]
        display_name = ""
        if nm is not None and str(nm).strip():
            display_name = str(nm).strip()
        elif your_nm is not None and str(your_nm).strip():
            display_name = str(your_nm).strip()
        rows_out.append(
            {
                "response_id": row[col("Column1")],
                "completion_time": completion,
                "customer": str(cust).strip(),
                "technology": tech,
                "parity_pct_raw": row[col("What is the parity percentage per the report?")],
                "date_collection": row[col("Date of Collection")],
                "region": row[col("Customer Region (if known)")],
                "controller_access": row[col("Do you have direct access to Customer's Controllers")],
                "report_url": row[col("Please upload the NaC Parity Report here")],
                "cec": row[col("Your CEC")],
                "submitter_email": row[col("Email")],
                "submitter_name": display_name,
            }
        )
    wb.close()
    return rows_out


def sort_key_completion(x: dict[str, Any]) -> datetime:
    ct = x["completion_time"]
    if isinstance(ct, datetime):
        return ct
    if isinstance(ct, str) and ct.strip():
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.strptime(ct.strip(), fmt)
            except ValueError:
                continue
    return datetime.min


def dedupe_parity_latest(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows_sorted = sorted(rows, key=sort_key_completion, reverse=True)
    seen: set[tuple[str, str]] = set()
    out: list[dict[str, Any]] = []
    for r in rows_sorted:
        key = (norm_spaces(r["customer"]), norm_spaces(r["technology"]))
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    out.reverse()
    return out


def parity_pct_number_format(ws: Any, col: int, max_scan: int = 100) -> str:
    """Reuse an existing NaC Parity % cell format from the template sheet."""
    for r in range(2, min(max_scan, ws.max_row + 1)):
        c = ws.cell(row=r, column=col)
        fmt = c.number_format
        if fmt and str(fmt).strip() and str(fmt) != "General":
            return str(fmt)
    return "0%"


@dataclass
class HeaderMap:
    by_name: dict[str, int]

    @classmethod
    def from_row(cls, row: tuple[Any, ...] | list[Any]) -> HeaderMap:
        by_name = {}
        for i, v in enumerate(row, start=1):
            if v is not None and str(v).strip():
                by_name[str(v).strip()] = i
        return cls(by_name=by_name)

    def col(self, name: str) -> int:
        return self.by_name[name]


def main() -> None:
    parity_rows = dedupe_parity_latest(read_parity_rows(PARITY_PATH))

    wb = load_workbook(READINESS_PATH)
    ws = wb["as-code score"]
    hdr = HeaderMap.from_row(tuple(ws.cell(row=1, column=c).value for c in range(1, ws.max_column + 1)))
    h = hdr.by_name

    def last_data_row() -> int:
        last = 1
        c_cust = h["Customer Name"]
        for r in range(2, ws.max_row + 1):
            v = ws.cell(row=r, column=c_cust).value
            if v is not None and str(v).strip():
                last = r
        return last

    c_customer = h["Customer Name"]
    baseline_customer_names = collect_baseline_customer_names(ws, c_customer)
    c_tech = h["Technologies"]
    c_segment = h["Customer Segment"]
    c_reviewer = h["NaC Parity Reviewer"]
    c_complete = h["NaC Parity Complete"]
    c_comments = h["NaC Parity Comments"]
    c_pct = h["NaC Parity %"]
    pct_fmt = parity_pct_number_format(ws, c_pct)

    def set_parity_pct(r: int, val: float | None) -> None:
        cell = ws.cell(row=r, column=c_pct, value=val)
        cell.number_format = pct_fmt

    for pr in parity_rows:
        tech = pr["technology"]
        frac, pcts = parse_parity_pct(pr["parity_pct_raw"])
        complete = parity_complete_from_fraction(frac)
        comments_parts: list[str] = []
        if pr["parity_pct_raw"] is not None and str(pr["parity_pct_raw"]).strip():
            comments_parts.append(f"Parity (raw): {str(pr['parity_pct_raw']).strip()}")
        if pr["report_url"]:
            comments_parts.append(f"Report: {pr['report_url']}")
        if pr["controller_access"]:
            comments_parts.append(f"Controller access (survey): {pr['controller_access']}")
        comments = " | ".join(comments_parts) if comments_parts else None

        on_baseline = customer_on_baseline_readiness(pr["customer"], baseline_customer_names)

        match_rows: list[int] = []
        if on_baseline:
            for r in range(2, ws.max_row + 1):
                rc = ws.cell(row=r, column=c_customer).value
                rt = ws.cell(row=r, column=c_tech).value
                if rc is None or not str(rc).strip():
                    continue
                if str(rt).strip() != tech:
                    continue
                if customers_match(pr["customer"], str(rc)):
                    match_rows.append(r)

        if match_rows:
            for r in match_rows:
                if frac is not None:
                    set_parity_pct(r, round(frac, 6))
                else:
                    set_parity_pct(r, None)
                ws.cell(row=r, column=c_complete, value=complete)
                if comments:
                    ws.cell(row=r, column=c_comments, value=comments)
                rev = format_parity_reviewer(pr["submitter_name"], pr["cec"])
                if rev:
                    ws.cell(row=r, column=c_reviewer, value=rev)
        else:
            nr = last_data_row() + 1
            seg = map_segment_from_region(pr["region"])
            ws.cell(row=nr, column=c_customer, value=pr["customer"])
            ws.cell(row=nr, column=c_tech, value=tech)
            if seg:
                ws.cell(row=nr, column=c_segment, value=seg)
            if frac is not None:
                set_parity_pct(nr, round(frac, 6))
            ws.cell(row=nr, column=c_complete, value=complete)
            if comments:
                ws.cell(row=nr, column=c_comments, value=comments)
            rev = format_parity_reviewer(pr["submitter_name"], pr["cec"])
            if rev:
                ws.cell(row=nr, column=c_reviewer, value=rev)

    for r in range(2, ws.max_row + 1):
        cell = ws.cell(row=r, column=c_pct)
        if cell.value is not None and isinstance(cell.value, (int, float)):
            cell.number_format = pct_fmt

    gap_n = apply_sdwan_catcsda_parity_gaps(ws, h)
    score_n = fill_missing_nac_score_formulas(ws, h)
    add_data_table_to_score_sheet(ws, h)
    add_native_interactive_pivots(wb, "as-code score", h)
    add_governance_charts(wb, "as-code score", h)

    wb.save(OUTPUT_PATH)
    print(
        f"Wrote {OUTPUT_PATH.resolve()} with {len(parity_rows)} deduped parity records; "
        f"parity-gap rows updated: {gap_n}; NaC Score formulas filled: {score_n}."
    )


if __name__ == "__main__":
    main()
