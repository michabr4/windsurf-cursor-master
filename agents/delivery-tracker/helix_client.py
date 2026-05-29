"""Helix REST API client for Delivery Tracker agent.

Connects to the Helix / ServiceFlow REST API using a Bearer token.
All calls are read-only (GET). No data is written back to Helix.

Environment variables (via config.Settings):
    HELIX_BASE_URL   - e.g. https://helix.example.com/api/v1
    HELIX_API_TOKEN  - Bearer token issued by the Helix admin portal
    HELIX_TIMEOUT    - Request timeout in seconds (default 30)
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, date, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import Settings
from models import HelixAccount, HelixCase, HelixMilestone, HelixSLARecord

logger = logging.getLogger(__name__)

_RETRY_TOTAL = 3
_RETRY_BACKOFF = 0.5
_RETRY_STATUS = {429, 500, 502, 503, 504}


class HelixAPIError(Exception):
    """Raised when the Helix API returns a non-2xx response."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        super().__init__(f"Helix API error {status_code}: {message}")


class HelixClient:
    """Read-only Helix REST API client."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._session = self._build_session()

    def _build_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update(
            {
                "Authorization": f"Bearer {self._settings.helix_api_token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )
        retry = Retry(
            total=_RETRY_TOTAL,
            backoff_factor=_RETRY_BACKOFF,
            status_forcelist=_RETRY_STATUS,
            allowed_methods=["GET"],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        return session

    def _url(self, path: str) -> str:
        base = self._settings.helix_base_url.rstrip("/")
        return f"{base}/{path.lstrip('/')}"

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = self._url(path)
        try:
            resp = self._session.get(
                url, params=params, timeout=self._settings.helix_timeout
            )
        except requests.exceptions.ConnectionError as exc:
            raise HelixAPIError(0, f"Connection failed: {exc}") from exc
        except requests.exceptions.Timeout as exc:
            raise HelixAPIError(0, f"Request timed out after {self._settings.helix_timeout}s") from exc

        if not resp.ok:
            raise HelixAPIError(resp.status_code, resp.text[:200])

        return resp.json()

    def ping(self) -> bool:
        """Return True if the API is reachable and the token is valid."""
        try:
            self._get("/health")
            return True
        except HelixAPIError as exc:
            logger.warning("Helix ping failed: %s", exc)
            return False

    def get_accounts(self, name_filter: Optional[str] = None) -> List[HelixAccount]:
        """Fetch all accounts the token has access to, optionally filtered by name."""
        params: Dict[str, Any] = {"page_size": 200}
        if name_filter:
            params["name"] = name_filter

        data = self._get("/accounts", params=params)
        items = data if isinstance(data, list) else data.get("results", [])
        return [self._parse_account(item) for item in items]

    def get_cases(
        self,
        account_id: str,
        lookback_days: int = 7,
        status_filter: Optional[List[str]] = None,
    ) -> List[HelixCase]:
        """Fetch open/recent cases for an account within the lookback window."""
        since = (datetime.now(timezone.utc) - timedelta(days=lookback_days)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        params: Dict[str, Any] = {
            "account_id": account_id,
            "updated_after": since,
            "page_size": 500,
        }
        if status_filter:
            params["status"] = ",".join(status_filter)

        data = self._get("/cases", params=params)
        items = data if isinstance(data, list) else data.get("results", [])
        return [self._parse_case(item) for item in items]

    def get_open_cases(self, account_id: str, lookback_days: int = 7) -> List[HelixCase]:
        """Convenience wrapper: cases that are not resolved/closed."""
        return self.get_cases(
            account_id,
            lookback_days=lookback_days,
            status_filter=["open", "in_progress", "pending_customer"],
        )

    def get_overdue_cases(self, account_id: str) -> List[HelixCase]:
        """Fetch cases past their due date that are still open."""
        params: Dict[str, Any] = {
            "account_id": account_id,
            "overdue": "true",
            "page_size": 200,
        }
        data = self._get("/cases", params=params)
        items = data if isinstance(data, list) else data.get("results", [])
        return [self._parse_case(item) for item in items]

    def get_milestones(self, account_id: str) -> List[HelixMilestone]:
        """Fetch project milestones for an account."""
        params: Dict[str, Any] = {"account_id": account_id, "page_size": 200}
        data = self._get("/milestones", params=params)
        items = data if isinstance(data, list) else data.get("results", [])
        return [self._parse_milestone(item) for item in items]

    def get_sla_metrics(
        self, account_id: str, lookback_days: int = 7
    ) -> Optional[HelixSLARecord]:
        """Fetch SLA adherence record for the lookback period."""
        period_end = date.today()
        period_start = period_end - timedelta(days=lookback_days)
        params: Dict[str, Any] = {
            "account_id": account_id,
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
        }
        try:
            data = self._get("/sla/metrics", params=params)
        except HelixAPIError as exc:
            logger.warning("SLA metrics unavailable for account %s: %s", account_id, exc)
            return None

        if not data:
            return None
        return self._parse_sla(data, account_id, period_start, period_end)

    # ── Parsers ────────────────────────────────────────────────────────────────

    @staticmethod
    def _parse_account(raw: Dict[str, Any]) -> HelixAccount:
        contract_end = None
        if raw.get("contract_end_date"):
            try:
                contract_end = date.fromisoformat(raw["contract_end_date"][:10])
            except ValueError:
                pass
        return HelixAccount(
            id=str(raw["id"]),
            name=raw.get("name", "Unknown"),
            account_manager=raw.get("account_manager"),
            segment=raw.get("segment"),
            contract_end_date=contract_end,
        )

    @staticmethod
    def _parse_case(raw: Dict[str, Any]) -> HelixCase:
        def _dt(val: Optional[str]) -> Optional[datetime]:
            if not val:
                return None
            try:
                return datetime.fromisoformat(val.replace("Z", "+00:00"))
            except ValueError:
                return None

        return HelixCase(
            id=str(raw["id"]),
            case_number=str(raw.get("case_number", raw["id"])),
            title=raw.get("title") or raw.get("subject", ""),
            status=raw.get("status", "open"),
            priority=raw.get("priority", "medium"),
            account_id=str(raw.get("account_id", "")),
            account_name=raw.get("account_name"),
            owner=raw.get("owner") or raw.get("assigned_to"),
            created_date=_dt(raw.get("created_date") or raw.get("created_at")) or datetime.utcnow(),
            updated_date=_dt(raw.get("updated_date") or raw.get("updated_at")) or datetime.utcnow(),
            due_date=_dt(raw.get("due_date")),
            resolved_date=_dt(raw.get("resolved_date")),
            sla_status=raw.get("sla_status"),
            is_escalated=bool(raw.get("is_escalated", False)),
        )

    @staticmethod
    def _parse_milestone(raw: Dict[str, Any]) -> HelixMilestone:
        due = None
        if raw.get("due_date"):
            try:
                due = date.fromisoformat(raw["due_date"][:10])
            except ValueError:
                pass
        return HelixMilestone(
            id=str(raw["id"]),
            name=raw.get("name", ""),
            account_id=str(raw.get("account_id", "")),
            status=raw.get("status", "not_started"),
            due_date=due,
            completion_pct=float(raw.get("completion_pct", raw.get("completion", 0))),
            owner=raw.get("owner"),
        )

    @staticmethod
    def _parse_sla(
        raw: Dict[str, Any],
        account_id: str,
        period_start: date,
        period_end: date,
    ) -> HelixSLARecord:
        return HelixSLARecord(
            account_id=account_id,
            period_start=period_start,
            period_end=period_end,
            target_pct=float(raw.get("target_pct", 95.0)),
            actual_pct=float(raw.get("actual_pct", raw.get("adherence_pct", 0.0))),
            cases_total=int(raw.get("cases_total", 0)),
            cases_met=int(raw.get("cases_met", 0)),
            cases_breached=int(raw.get("cases_breached", 0)),
        )
