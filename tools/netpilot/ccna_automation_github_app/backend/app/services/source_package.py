from __future__ import annotations

import re
from html import unescape
from pathlib import Path
from typing import Any

from app.config import get_settings


def _strip_tags(value: str) -> str:
    return re.sub(r"<[^>]*>", "", value).strip()


def _clean(value: str) -> str:
    return unescape(_strip_tags(value))


def _extract_metrics(content: str) -> list[dict[str, str]]:
    metrics: list[dict[str, str]] = []
    metric_regex = re.compile(
        r'<div[^>]*class="[^"]*metric-val[^"]*"[^>]*>(.*?)</div>\s*'
        r'<div[^>]*class="[^"]*metric-label[^"]*"[^>]*>(.*?)</div>',
        re.IGNORECASE | re.DOTALL,
    )
    for match in metric_regex.finditer(content):
        metrics.append({"value": _clean(match.group(1)), "label": _clean(match.group(2))})
    return metrics


def _extract_integration_matrix(content: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    body_match = re.search(
        r'<table[^>]*id="integ-table-k4x8"[^>]*>[\s\S]*?<tbody[^>]*>([\s\S]*?)</tbody>',
        content,
        re.IGNORECASE,
    )
    if not body_match:
        return rows

    for row_html in re.findall(r"<tr[^>]*>([\s\S]*?)</tr>", body_match.group(1), re.IGNORECASE):
        cells = [
            _clean(cell)
            for cell in re.findall(r"<td[^>]*>([\s\S]*?)</td>", row_html, re.IGNORECASE)
        ]
        if len(cells) >= 6:
            rows.append(
                {
                    "source_target": cells[0],
                    "protocol": cells[1],
                    "format": cells[2],
                    "auth": cells[3],
                    "latency_sla": cells[4],
                    "pattern": cells[5],
                }
            )
    return rows


def _extract_subsystems(content: str) -> list[str]:
    names = re.findall(
        r"<h2[^>]*>\s*Subsystem\s*\d+\s*:\s*([^<]+)</h2>",
        content,
        re.IGNORECASE,
    )
    return [_clean(name) for name in names]


def _extract_launch_phases(content: str) -> list[dict[str, str]]:
    phases: list[dict[str, str]] = []
    phase_regex = re.compile(
        r"(Phase\s*\d+\s*:\s*[^<]+)</div>\s*"
        r"<div[^>]*>(Months[^<]+)</div>[\s\S]*?"
        r"Exit Criteria</div>\s*<div[^>]*>([^<]+)</div>",
        re.IGNORECASE,
    )
    for phase_name, months, exit_criteria in phase_regex.findall(content):
        phases.append(
            {
                "phase": _clean(phase_name),
                "timeline": _clean(months),
                "exit_criteria": _clean(exit_criteria),
            }
        )
    return phases


def _extract_risks(content: str) -> list[dict[str, str]]:
    risks: list[dict[str, str]] = []
    body_match = re.search(
        r'<table[^>]*id="risk-table-j9k0"[^>]*>[\s\S]*?<tbody[^>]*>([\s\S]*?)</tbody>',
        content,
        re.IGNORECASE,
    )
    if not body_match:
        return risks

    for row_html in re.findall(r"<tr[^>]*>([\s\S]*?)</tr>", body_match.group(1), re.IGNORECASE):
        cells = [
            _clean(cell)
            for cell in re.findall(r"<td[^>]*>([\s\S]*?)</td>", row_html, re.IGNORECASE)
        ]
        if len(cells) >= 5:
            risks.append(
                {
                    "risk": cells[0],
                    "likelihood": cells[1],
                    "impact": cells[2],
                    "mitigation": cells[3],
                    "owner": cells[4],
                }
            )
    return risks


def _source_html_path() -> Path | None:
    settings = get_settings()
    if settings.source_html_path and settings.source_html_path.is_file():
        return settings.source_html_path
    return None


def get_source_package() -> dict[str, Any]:
    source_path = _source_html_path()
    if source_path is None:
        return {
            "title": "Automation + GitHub Training Hub",
            "platform_vision": "",
            "metrics": [],
            "integration_matrix": [],
            "subsystems": [],
            "launch_phases": [],
            "risks": [],
        }

    content = source_path.read_text(encoding="utf-8")

    title_match = re.search(r"<title>([^<]+)</title>", content, re.IGNORECASE)
    platform_match = re.search(
        r"<h3[^>]*>\s*Platform Vision\s*</h3>[\s\S]*?<p[^>]*>([\s\S]*?)</p>",
        content,
        re.IGNORECASE,
    )

    return {
        "title": _clean(title_match.group(1))
        if title_match
        else "Automation + GitHub Training Hub",
        "platform_vision": _clean(platform_match.group(1)) if platform_match else "",
        "metrics": _extract_metrics(content),
        "integration_matrix": _extract_integration_matrix(content),
        "subsystems": _extract_subsystems(content),
        "launch_phases": _extract_launch_phases(content),
        "risks": _extract_risks(content),
    }
