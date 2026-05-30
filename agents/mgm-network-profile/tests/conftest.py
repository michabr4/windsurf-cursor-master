"""Shared pytest fixtures for MGM Resorts Network Profile tests."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from models import (
    NPCollector,
    NPCompany,
    NPDevice,
    NPGroup,
    NPSnapshot,
    Recommendation,
)


@pytest.fixture()
def mock_settings():
    """Minimal settings object suitable for unit tests (no real credentials)."""
    settings = MagicMock()
    settings.mimir_url = "https://mimir-prod.cisco.com"
    settings.np_cpy_key = 172361
    settings.mimir_cookie_file = "default"
    settings.mimir_cache_dir = "/tmp/mimir-cache-test"
    settings.cli_device_limit = 5
    settings.cli_commands = ["show version"]
    settings.log_level = "INFO"
    return settings


@pytest.fixture()
def sample_company() -> NPCompany:
    return NPCompany(cpy_key=172361, cpy_name="MGM Resorts International")


@pytest.fixture()
def sample_group() -> NPGroup:
    return NPGroup(group_id=1, group_name="Core Network", cpy_key=172361)


@pytest.fixture()
def sample_device() -> NPDevice:
    return NPDevice(
        device_id=99001,
        device_name="mgm-core-sw-01",
        cpy_key=172361,
        group_id=1,
        software_version="16.12.4",
        platform="Catalyst 9300",
    )


@pytest.fixture()
def sample_collector() -> NPCollector:
    return NPCollector(
        collector="mgm-collector-01",
        cpy_key=172361,
        last_contact="2026-05-28T10:00:00Z",
    )


@pytest.fixture()
def empty_snapshot(sample_company) -> NPSnapshot:
    return NPSnapshot(
        cpy_key=172361,
        fetched_at=datetime(2026, 5, 28, 12, 0, 0, tzinfo=timezone.utc),
        company=sample_company,
    )


@pytest.fixture()
def populated_snapshot(
    sample_company, sample_group, sample_device, sample_collector
) -> NPSnapshot:
    snap = NPSnapshot(
        cpy_key=172361,
        fetched_at=datetime(2026, 5, 28, 12, 0, 0, tzinfo=timezone.utc),
        company=sample_company,
        groups=[sample_group],
        devices=[sample_device],
        collectors=[sample_collector],
    )
    return snap
