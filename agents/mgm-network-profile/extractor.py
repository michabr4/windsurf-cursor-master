"""Data extraction pipeline for MGM Resorts Network Profile.

Pulls all relevant data for cpyKey=172361 via MIMIR and returns
a structured NPSnapshot ready for the recommender.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional

from config import Settings
from models import NPDevice, NPSnapshot
from np_client import NPClient

logger = logging.getLogger(__name__)

# ── IOS version patterns ──────────────────────────────────────────────────────

_VERSION_RE = re.compile(
    r"Version\s+([\d]+\.[\d]+[\w\(\)\.]+)", re.IGNORECASE
)
_PLATFORM_RE = re.compile(
    r"cisco\s+([\w\-]+(?:\s+\w+)?)\s+(?:processor|chassis|series)", re.IGNORECASE
)
_UPTIME_RE = re.compile(
    r"uptime is\s+([\d\w ,]+)", re.IGNORECASE
)

# Known EOS IOS major versions (flag for recommendation)
_EOS_VERSION_PREFIXES = ("12.0", "12.1", "12.2", "12.3", "12.4", "15.0", "15.1")


class NPExtractor:
    """Orchestrates all MIMIR NP data fetches for a single company."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def run(self) -> NPSnapshot:
        """Execute the full extraction pipeline. Returns NPSnapshot."""
        logger.info(
            "Starting extraction for cpyKey=%s", self._settings.np_cpy_key
        )
        fetched_at = datetime.now(timezone.utc)

        with NPClient(self._settings) as client:
            company = client.get_company()
            groups = client.get_groups()
            devices = client.get_devices()
            collectors = client.get_collectors()

            logger.info(
                "Fetched company=%s groups=%d devices=%d collectors=%d",
                company.cpy_name if company else "unknown",
                len(groups),
                len(devices),
                len(collectors),
            )

            self._enrich_devices(client, devices)

        snapshot = NPSnapshot(
            cpy_key=self._settings.np_cpy_key,
            fetched_at=fetched_at,
            company=company,
            groups=groups,
            devices=devices,
            collectors=collectors,
        )
        logger.info("Extraction complete")
        return snapshot

    # ── Device enrichment ─────────────────────────────────────────────────────

    def _enrich_devices(self, client: NPClient, devices: List[NPDevice]) -> None:
        """Augment devices with IOS version, platform, and uptime from CLI."""
        limit = self._settings.np_device_cli_limit
        targets = devices[:limit] if limit > 0 else devices

        if limit and len(devices) > limit:
            logger.warning(
                "Device CLI limited to first %d of %d devices (NP_DEVICE_CLI_LIMIT)",
                limit,
                len(devices),
            )

        for i, device in enumerate(targets):
            logger.debug(
                "Enriching device %d/%d: %s (id=%s)",
                i + 1,
                len(targets),
                device.device_name,
                device.device_id,
            )
            self._fetch_show_version(client, device)
            self._fetch_extra_commands(client, device)

    def _fetch_show_version(self, client: NPClient, device: NPDevice) -> None:
        """Populate ios_version, platform, and uptime from 'show version'."""
        output = client.get_cli_output(device.device_id, "show version")
        if not output:
            return

        device.cli_outputs["show version"] = output

        m = _VERSION_RE.search(output)
        if m:
            device.ios_version = m.group(1)

        m = _PLATFORM_RE.search(output)
        if m:
            device.platform = m.group(1).strip()

        m = _UPTIME_RE.search(output)
        if m:
            device.uptime = m.group(1).strip()

    def _fetch_extra_commands(self, client: NPClient, device: NPDevice) -> None:
        """Fetch additional configured CLI commands per device."""
        for cmd in self._settings.np_cli_commands:
            if cmd == "show version":
                continue
            output = client.get_cli_output(device.device_id, cmd)
            if output:
                device.cli_outputs[cmd] = output

    # ── Static helpers ────────────────────────────────────────────────────────

    @staticmethod
    def is_eos_version(version: Optional[str]) -> bool:
        """Return True if version string matches a known EOS IOS prefix."""
        if not version:
            return False
        return any(version.startswith(prefix) for prefix in _EOS_VERSION_PREFIXES)
