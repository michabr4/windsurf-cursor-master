"""Offline Apple Mail export digest (regex priority, no Graph/OpenAI).

Ported from personal-automation/email_digest.py during EMAIL-CONSOLIDATE.
Use when you have a Mail.app unit-delimited export instead of live Graph access.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROW = "\x1fROW\x1f"
COL = "\x1fCOL\x1f"

HIGH_PAT = re.compile(
    r"\b(urgent|asap|immediately|security\s*alert|fraud|action\s*required|"
    r"deadline|overdue|legal|court|time-?sensitive|critical|expire[sd]?|"
    r"\bp0\b|\bp1\b|\bp2\b|sev\s*0|sev\s*1|outage|breach|"
    r"complianc|audit\b|sla\b.*(miss|breach)|escalat)\b",
    re.I,
)
MED_PAT = re.compile(
    r"\b(remind(er)?|please\s*review|rsvp|meeting|calendar|invoice|payment|"
    r"approval|sign|signature|response\s*needed|feedback|"
    r"fyi|for your awareness|action\s*needed|follow\s*up|"
    r"please\s*confirm|needs?\s*your)\b",
    re.I,
)
LOW_PAT = re.compile(
    r"\b(newsletter|digest|unsubscribe|promo(tion)?|sale\s|%?\s*off|"
    r"marketing|no-?reply|noreply|deal\s+of|automated\s*message|"
    r"do\s*not\s*reply|mailer-daemon|postmaster)\b",
    re.I,
)

DATE_PATTERNS = [
    (re.compile(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b"), "mdy"),
    (re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b"), "ymd"),
    (
        re.compile(
            r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?\b",
            re.I,
        ),
        "mon_day",
    ),
]


def normalize_subject(s: str) -> str:
    t = (s or "").strip()
    while True:
        m = re.match(r"^\s*(re|fw|fwd)\s*:\s*", t, re.I)
        if not m:
            break
        t = t[m.end() :].strip()
    return t.casefold()


def priority_for(subject: str, sender: str) -> str:
    blob = f"{subject} {sender}"
    if HIGH_PAT.search(blob):
        return "High"
    if LOW_PAT.search(blob):
        return "Low"
    if MED_PAT.search(blob):
        return "Medium"
    return "Medium"


def action_for(subject: str, sender: str, pr: str) -> str:
    blob = f"{subject} {sender}".lower()
    if subject.strip().lower().startswith("(sent) "):
        return "Outbound copy; confirm recipient saw reply or archive if thread is closed."
    if "invoice" in blob or "payment" in blob:
        return "Review billing / pay or dispute if needed; file receipt."
    if "sign" in blob or "signature" in blob or "docusign" in blob:
        return "Complete signature or review attached agreement."
    if "meeting" in blob or "calendar" in blob or "invite" in blob:
        return "Accept/decline invite; add to calendar; prep agenda."
    if "rsvp" in blob:
        return "Respond with attendance by stated date."
    if "review" in blob or "feedback" in blob:
        return "Read thread and reply with review or decision."
    if "security" in blob or "password" in blob or "verify" in blob:
        return "Verify legitimacy; if real, follow provider steps (avoid links if suspicious)."
    if any(
        k in blob
        for k in ("tracking", "shipment", "delivered", "package", "fedex", "ups ", "usps")
    ):
        return "Track delivery or confirm receipt; file order details if needed."
    if "out of office" in blob or re.search(r"\booo\b", blob) or "vacation" in blob:
        return "Note auto-reply; adjust expectations on response time."
    if pr == "Low":
        return "Optional: skim or archive; unsubscribe if noise."
    return "Read when convenient; reply or file if a response is expected."


def due_hint(subject: str) -> str:
    if not subject:
        return "—"
    for pat, _kind in DATE_PATTERNS:
        m = pat.search(subject)
        if m:
            return f"Possible date in subject: {m.group(0)}"
    if re.search(r"\bby\s+(mon|tue|wed|thu|fri|sat|sun|tomorrow|eod|eow)\b", subject, re.I):
        m = re.search(r"\bby\s+.+$", subject, re.I)
        return f"Relative deadline phrasing: {m.group(0).strip()}" if m else "—"
    return "—"


def parse_export(raw: str) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for chunk in raw.split(ROW):
        chunk = chunk.strip()
        if not chunk:
            continue
        parts = chunk.split(COL)
        if len(parts) < 3:
            continue
        subj, sender, recd = parts[0], parts[1], parts[2]
        rows.append((subj.strip(), sender.strip(), recd.strip()))
    seen: set[tuple[str, str, str]] = set()
    unique: list[tuple[str, str, str]] = []
    for r in rows:
        if r in seen:
            continue
        seen.add(r)
        unique.append(r)
    return unique


def build_markdown(rows: list[tuple[str, str, str]], source_note: str) -> str:
    groups: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for subj, sender, recd in rows:
        key = normalize_subject(subj) or "(no subject)"
        groups[key].append((subj, sender, recd))

    lines: list[str] = [
        "# Offline email digest",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        f"**Source:** {source_note}",
        "",
        "## Summary",
        "",
        f"- **Threads / subject groups:** {len(groups)}",
        f"- **Messages:** {len(rows)}",
        "",
        "## Groups (by normalized subject)",
        "",
    ]

    def group_score(g: list[tuple[str, str, str]]) -> tuple[int, int]:
        pr_order = {"High": 3, "Medium": 2, "Low": 1}
        best = max(pr_order[priority_for(s, snd)] for s, snd, _ in g)
        return (best, len(g))

    for key in sorted(groups.keys(), key=lambda k: group_score(groups[k]), reverse=True):
        msgs = groups[key]
        canonical = msgs[0][0] or "(no subject)"
        pr = priority_for(canonical, msgs[0][1])
        lines.extend(
            [
                f"### {canonical}",
                "",
                f"- **Priority:** {pr}",
                f"- **Suggested action:** {action_for(canonical, msgs[0][1], pr)}",
                f"- **Due / dates:** {due_hint(canonical)}",
                f"- **Messages in group:** {len(msgs)}",
                "",
                "| Received | From | Subject |",
                "| --- | --- | --- |",
            ]
        )
        for subj, sender, recd in sorted(msgs, key=lambda x: x[2], reverse=True):
            lines.append(
                f"| {recd} | {sender.replace('|', '\\|')} | {subj.replace('|', '\\|')} |"
            )
        lines.append("")

    return "\n".join(lines)


def run_offline_digest(export_path: Path | None, output_dir: Path) -> Path:
    """Parse export file or stdin and write markdown digest to output_dir."""
    if export_path and export_path.exists():
        raw = export_path.read_text(encoding="utf-8", errors="replace")
        note = export_path.name
    else:
        raw = sys.stdin.read()
        note = "stdin"

    rows = parse_export(raw)
    md = build_markdown(rows, note)
    output_dir.mkdir(parents=True, exist_ok=True)
    out = output_dir / "offline_mail_digest.md"
    out.write_text(md, encoding="utf-8")
    return out
