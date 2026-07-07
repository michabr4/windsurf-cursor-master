"""Data models for MGM Resorts Network Profile agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


# ── Raw NP data models ───────────────────────────────────────────────────────

@dataclass
class NPCompany:
    cpy_key: int
    cpy_name: str
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_mimir(cls, obj: Any) -> "NPCompany":
        raw = obj.__dict__ if hasattr(obj, "__dict__") else {}
        return cls(
            cpy_key=int(getattr(obj, "cpyKey", 0) or 0),
            cpy_name=str(getattr(obj, "cpyName", "") or ""),
            raw=raw,
        )


@dataclass
class NPGroup:
    group_name: str
    cpy_key: int
    device_count: Optional[int] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_mimir(cls, obj: Any, cpy_key: int) -> "NPGroup":
        raw = obj.__dict__ if hasattr(obj, "__dict__") else {}
        return cls(
            group_name=str(getattr(obj, "groupName", "") or ""),
            cpy_key=cpy_key,
            device_count=_int_or_none(getattr(obj, "deviceCount", None)),
            raw=raw,
        )


@dataclass
class NPDevice:
    device_id: int
    device_name: str
    cpy_key: int
    ip_address: Optional[str] = None
    platform: Optional[str] = None
    ios_version: Optional[str] = None
    uptime: Optional[str] = None
    last_collection: Optional[str] = None
    cli_outputs: Dict[str, str] = field(default_factory=dict, repr=False)
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_mimir(cls, obj: Any, cpy_key: int) -> "NPDevice":
        raw = obj.__dict__ if hasattr(obj, "__dict__") else {}
        return cls(
            device_id=int(getattr(obj, "deviceId", 0) or 0),
            device_name=str(getattr(obj, "deviceName", "") or ""),
            cpy_key=cpy_key,
            ip_address=str(getattr(obj, "ipAddress", "") or "") or None,
            platform=str(getattr(obj, "platform", "") or "") or None,
            ios_version=str(getattr(obj, "iosVersion", "") or "") or None,
            last_collection=str(getattr(obj, "lastCollection", "") or "") or None,
            raw=raw,
        )


@dataclass
class NPCollector:
    collector: str
    cpy_key: int
    status: Optional[str] = None
    last_seen: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_mimir(cls, obj: Any, cpy_key: int) -> "NPCollector":
        raw = obj.__dict__ if hasattr(obj, "__dict__") else {}
        return cls(
            collector=str(getattr(obj, "collector", "") or ""),
            cpy_key=cpy_key,
            status=str(getattr(obj, "status", "") or "") or None,
            last_seen=str(getattr(obj, "lastSeen", "") or "") or None,
            raw=raw,
        )


# ── Recommendation model ─────────────────────────────────────────────────────

class Severity:
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    INFO = "info"


class Category:
    SOFTWARE_CURRENCY = "Software Currency"
    COLLECTOR_HEALTH = "Collector Health"
    DEVICE_REACHABILITY = "Device Reachability"
    CONFIG_COMPLIANCE = "Config Compliance"
    INVENTORY_COVERAGE = "Inventory Coverage"


@dataclass
class Recommendation:
    category: str
    severity: str
    title: str
    detail: str
    device_id: Optional[int] = None
    device_name: Optional[str] = None
    collector: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "severity": self.severity,
            "title": self.title,
            "detail": self.detail,
            "device_id": self.device_id,
            "device_name": self.device_name,
            "collector": self.collector,
        }


# ── Aggregated snapshot ───────────────────────────────────────────────────────

@dataclass
class NPSnapshot:
    cpy_key: int
    fetched_at: datetime
    company: Optional[NPCompany]
    groups: List[NPGroup]
    devices: List[NPDevice]
    collectors: List[NPCollector]
    recommendations: List[Recommendation] = field(default_factory=list)

    @property
    def device_count(self) -> int:
        return len(self.devices)

    @property
    def collector_count(self) -> int:
        return len(self.collectors)

    @property
    def recommendation_count_by_severity(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for r in self.recommendations:
            counts[r.severity] = counts.get(r.severity, 0) + 1
        return counts


# ── Helpers ───────────────────────────────────────────────────────────────────

def _int_or_none(val: Any) -> Optional[int]:
    try:
        return int(val)
    except (TypeError, ValueError):
        return None
