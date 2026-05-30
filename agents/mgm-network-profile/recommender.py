"""Recommendation engine for MGM Resorts Network Profile.

Analyses an NPSnapshot and returns a prioritised list of Recommendations
across five categories:
  1. Software Currency    — EOS/outdated IOS versions
  2. Collector Health     — stale or missing collectors
  3. Device Reachability  — devices with no CLI/config data
  4. Config Compliance    — missing best-practice config elements
  5. Inventory Coverage   — devices not assigned to any group
"""

from __future__ import annotations

import logging
import re
from typing import List, Set

from extractor import NPExtractor
from models import Category, NPSnapshot, Recommendation, Severity

logger = logging.getLogger(__name__)

# ── Config compliance checks ──────────────────────────────────────────────────

_COMPLIANCE_CHECKS = [
    {
        "name": "NTP server",
        "pattern": re.compile(r"^ntp server\s+\S+", re.MULTILINE),
        "severity": Severity.MEDIUM,
        "detail": "No NTP server configured. Accurate time is required for logging, crypto, and SNMP.",
    },
    {
        "name": "Logging",
        "pattern": re.compile(r"^logging\s+\S+", re.MULTILINE),
        "severity": Severity.MEDIUM,
        "detail": "No remote logging destination configured. Syslog export is needed for SIEM/audit trail.",
    },
    {
        "name": "SSH v2",
        "pattern": re.compile(r"ip ssh version 2", re.MULTILINE),
        "severity": Severity.HIGH,
        "detail": "SSH version 2 not enforced. SSHv1 is cryptographically weak.",
    },
    {
        "name": "Service password-encryption",
        "pattern": re.compile(r"service password-encryption", re.MULTILINE),
        "severity": Severity.MEDIUM,
        "detail": "Passwords in running-config are stored in cleartext (Type 0/7).",
    },
    {
        "name": "AAA new-model",
        "pattern": re.compile(r"aaa new-model", re.MULTILINE),
        "severity": Severity.HIGH,
        "detail": "AAA new-model not configured. Centralised authentication is not enforced.",
    },
    {
        "name": "No IP source-route",
        "pattern": re.compile(r"no ip source-route", re.MULTILINE),
        "severity": Severity.INFO,
        "detail": "IP source routing is not explicitly disabled.",
    },
]

# Collector status strings considered unhealthy
_UNHEALTHY_STATUSES = {"inactive", "down", "failed", "error", "unreachable"}


class NPRecommender:
    """Stateless analyser — call analyse(snapshot) to get recommendations."""

    def analyse(self, snapshot: NPSnapshot) -> List[Recommendation]:
        recs: List[Recommendation] = []

        recs.extend(self._check_software_currency(snapshot))
        recs.extend(self._check_collector_health(snapshot))
        recs.extend(self._check_device_reachability(snapshot))
        recs.extend(self._check_config_compliance(snapshot))
        recs.extend(self._check_inventory_coverage(snapshot))

        recs.sort(key=lambda r: _SEVERITY_ORDER.get(r.severity, 99))
        logger.info(
            "Generated %d recommendations (%s)",
            len(recs),
            snapshot.recommendation_count_by_severity,
        )
        return recs

    # ── 1. Software Currency ──────────────────────────────────────────────────

    def _check_software_currency(self, snapshot: NPSnapshot) -> List[Recommendation]:
        recs: List[Recommendation] = []
        no_version: List[str] = []

        for device in snapshot.devices:
            if not device.ios_version:
                no_version.append(device.device_name)
                continue

            if NPExtractor.is_eos_version(device.ios_version):
                recs.append(Recommendation(
                    category=Category.SOFTWARE_CURRENCY,
                    severity=Severity.HIGH,
                    title=f"EOS IOS version on {device.device_name}",
                    detail=(
                        f"Running IOS {device.ios_version} which falls under a known "
                        f"end-of-support prefix. Upgrade to a current Cisco-recommended release."
                    ),
                    device_id=device.device_id,
                    device_name=device.device_name,
                ))

        if no_version:
            recs.append(Recommendation(
                category=Category.SOFTWARE_CURRENCY,
                severity=Severity.MEDIUM,
                title=f"{len(no_version)} device(s) with unknown IOS version",
                detail=(
                    f"Could not determine IOS version for: "
                    f"{', '.join(no_version[:10])}{'...' if len(no_version) > 10 else ''}. "
                    f"Verify reachability and collection status."
                ),
            ))

        return recs

    # ── 2. Collector Health ───────────────────────────────────────────────────

    def _check_collector_health(self, snapshot: NPSnapshot) -> List[Recommendation]:
        recs: List[Recommendation] = []

        if not snapshot.collectors:
            recs.append(Recommendation(
                category=Category.COLLECTOR_HEALTH,
                severity=Severity.CRITICAL,
                title="No collectors found for this account",
                detail=(
                    "MIMIR returned no collector details for cpyKey="
                    f"{snapshot.cpy_key}. Data collection may be completely offline."
                ),
            ))
            return recs

        for collector in snapshot.collectors:
            status = (collector.status or "").lower()
            if status in _UNHEALTHY_STATUSES:
                recs.append(Recommendation(
                    category=Category.COLLECTOR_HEALTH,
                    severity=Severity.CRITICAL,
                    title=f"Collector '{collector.collector}' is {collector.status}",
                    detail=(
                        f"Collector '{collector.collector}' is reporting status "
                        f"'{collector.status}'. Device data for this collector may be stale. "
                        f"Last seen: {collector.last_seen or 'unknown'}."
                    ),
                    collector=collector.collector,
                ))
            elif not status:
                recs.append(Recommendation(
                    category=Category.COLLECTOR_HEALTH,
                    severity=Severity.MEDIUM,
                    title=f"Collector '{collector.collector}' has no status",
                    detail=(
                        f"Collector '{collector.collector}' returned no status. "
                        f"Verify it is registered and polling correctly."
                    ),
                    collector=collector.collector,
                ))

        return recs

    # ── 3. Device Reachability ────────────────────────────────────────────────

    def _check_device_reachability(self, snapshot: NPSnapshot) -> List[Recommendation]:
        unreachable = [
            d for d in snapshot.devices
            if not d.cli_outputs and not d.ios_version
        ]
        if not unreachable:
            return []

        return [Recommendation(
            category=Category.DEVICE_REACHABILITY,
            severity=Severity.HIGH,
            title=f"{len(unreachable)} device(s) returned no CLI data",
            detail=(
                f"These devices could not be queried via MIMIR CLI: "
                f"{', '.join(d.device_name for d in unreachable[:15])}"
                f"{'...' if len(unreachable) > 15 else ''}. "
                f"Check connectivity, credentials, and collector assignment."
            ),
        )]

    # ── 4. Config Compliance ──────────────────────────────────────────────────

    def _check_config_compliance(self, snapshot: NPSnapshot) -> List[Recommendation]:
        recs: List[Recommendation] = []

        for device in snapshot.devices:
            if not device.cli_outputs:
                continue
            full_text = "\n".join(device.cli_outputs.values())

            for check in _COMPLIANCE_CHECKS:
                if not check["pattern"].search(full_text):
                    recs.append(Recommendation(
                        category=Category.CONFIG_COMPLIANCE,
                        severity=check["severity"],
                        title=f"Missing '{check['name']}' on {device.device_name}",
                        detail=check["detail"],
                        device_id=device.device_id,
                        device_name=device.device_name,
                    ))

        return recs

    # ── 5. Inventory Coverage ─────────────────────────────────────────────────

    def _check_inventory_coverage(self, snapshot: NPSnapshot) -> List[Recommendation]:
        if not snapshot.groups:
            return [Recommendation(
                category=Category.INVENTORY_COVERAGE,
                severity=Severity.MEDIUM,
                title="No network groups defined for this account",
                detail=(
                    "No NP groups found. Grouping devices by site/function enables "
                    "targeted reporting and faster troubleshooting."
                ),
            )]
        return []


# ── Helpers ───────────────────────────────────────────────────────────────────

_SEVERITY_ORDER = {
    Severity.CRITICAL: 0,
    Severity.HIGH: 1,
    Severity.MEDIUM: 2,
    Severity.INFO: 3,
}
