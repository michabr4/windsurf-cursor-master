"""MIMIR NetProfile (NP) client wrapper — MGM Resorts Network Profile (cpyKey=172361).

Wraps the mimir-client library with:
  - SSO cookie-based auth (non-interactive when cookie file is valid)
  - Per-endpoint typed accessors for the NP namespace
  - Graceful error handling — never raises on individual device failures
"""

from __future__ import annotations

import logging
from typing import Any, Iterator, List, Optional

from mimir import Mimir

from config import Settings
from models import NPCollector, NPCompany, NPDevice, NPGroup

logger = logging.getLogger(__name__)


class NPClientError(Exception):
    """Raised when a MIMIR NP call fails unrecoverably."""


class NPClient:
    """Read-only MIMIR NP client scoped to a single cpyKey."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._cpy_key = settings.np_cpy_key
        self._m: Optional[Mimir] = None

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def connect(self) -> None:
        """Initialise MIMIR session and authenticate via SSO cookie."""
        self._m = Mimir(
            username=self._settings.mimir_username or None,
            cookie_file=self._settings.mimir_cookie_file,
            cache_dir=self._settings.mimir_cache_dir,
            cache_days=self._settings.mimir_cache_days,
            url=self._settings.mimir_url,
        )
        self._m.authenticate()
        logger.info("MIMIR session established for cpyKey=%s", self._cpy_key)

    def close(self) -> None:
        if self._m is not None:
            try:
                self._m.save_cookies()
            except Exception:
                pass
            self._m = None

    def __enter__(self) -> "NPClient":
        self.connect()
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    # ── Company ───────────────────────────────────────────────────────────────

    def get_company(self) -> Optional[NPCompany]:
        """Return metadata for the target company, or None on failure."""
        try:
            results = list(self._np.companies_entitled.get())
            for obj in results:
                if str(getattr(obj, "cpyKey", "")) == str(self._cpy_key):
                    return NPCompany.from_mimir(obj)
            logger.warning("cpyKey=%s not found in entitled companies", self._cpy_key)
            return None
        except Exception as exc:
            logger.error("Failed to fetch company info: %s", exc)
            return None

    # ── Groups ────────────────────────────────────────────────────────────────

    def get_groups(self) -> List[NPGroup]:
        try:
            return [
                NPGroup.from_mimir(obj, self._cpy_key)
                for obj in self._np.groups.get(cpyKey=self._cpy_key)
            ]
        except Exception as exc:
            logger.error("Failed to fetch groups: %s", exc)
            return []

    # ── Devices ───────────────────────────────────────────────────────────────

    def get_devices(self) -> List[NPDevice]:
        try:
            return [
                NPDevice.from_mimir(obj, self._cpy_key)
                for obj in self._np.devices.get(cpyKey=self._cpy_key)
            ]
        except Exception as exc:
            logger.error("Failed to fetch devices: %s", exc)
            return []

    # ── CLI ───────────────────────────────────────────────────────────────────

    def get_cli_output(self, device_id: int, command: str) -> str:
        """Return extracted CLI output for one device/command pair.

        Uses extract=1 so MIMIR returns parsed fields rather than raw text.
        Falls back to empty string on any error — never raises.
        """
        try:
            outputs = list(
                self._np.cli.get(
                    cpyKey=self._cpy_key,
                    deviceId=device_id,
                    command=command,
                    extract=1,
                )
            )
            if not outputs:
                return ""
            first = outputs[0]
            return str(getattr(first, "extract", "") or "")
        except Exception as exc:
            logger.debug(
                "CLI fetch failed device_id=%s command=%r: %s", device_id, command, exc
            )
            return ""

    # ── Config ────────────────────────────────────────────────────────────────

    def get_config_lines(self, device_id: int) -> List[str]:
        """Return running-config lines for a device (empty list on failure)."""
        try:
            lines: List[str] = []
            for obj in self._np.config.get(cpyKey=self._cpy_key, deviceId=device_id):
                line = getattr(obj, "command", None)
                if line:
                    lines.append(str(line))
            return lines
        except Exception as exc:
            logger.debug("Config fetch failed device_id=%s: %s", device_id, exc)
            return []

    # ── Collectors ────────────────────────────────────────────────────────────

    def get_collectors(self) -> List[NPCollector]:
        try:
            return [
                NPCollector.from_mimir(obj, self._cpy_key)
                for obj in self._np.collector_details.get(cpyKey=self._cpy_key)
            ]
        except Exception as exc:
            logger.error("Failed to fetch collector details: %s", exc)
            return []

    # ── Internal ──────────────────────────────────────────────────────────────

    @property
    def _np(self) -> Any:
        if self._m is None:
            raise NPClientError("Client not connected — call connect() first")
        return self._m.np
