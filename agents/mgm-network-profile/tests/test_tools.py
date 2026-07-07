"""Unit tests for tools/np_tools.py."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from tools.np_tools import fetch_snapshot, generate_recommendations, snapshot_summary, top_findings
from models import Recommendation


class TestFetchSnapshot:
    def test_returns_snapshot(self, populated_snapshot, mock_settings):
        with (
            patch("tools.np_tools.get_settings", return_value=mock_settings),
            patch("tools.np_tools.NPExtractor") as mock_cls,
        ):
            mock_cls.return_value.run.return_value = populated_snapshot
            result = fetch_snapshot()

        assert result is populated_snapshot

    def test_overrides_cpy_key(self, populated_snapshot, mock_settings):
        mock_settings.model_copy = MagicMock(return_value=mock_settings)
        with (
            patch("tools.np_tools.get_settings", return_value=mock_settings),
            patch("tools.np_tools.NPExtractor") as mock_cls,
        ):
            mock_cls.return_value.run.return_value = populated_snapshot
            fetch_snapshot(cpy_key=99999)

        mock_settings.model_copy.assert_called_once_with(update={"np_cpy_key": 99999})


class TestGenerateRecommendations:
    def test_returns_list(self, populated_snapshot):
        recs = [
            Recommendation(
                priority=1,
                category="Software Currency",
                title="EOS device",
                device_name="dev-01",
                detail="old version",
            )
        ]
        with patch("tools.np_tools.NPRecommender") as mock_cls:
            mock_cls.return_value.analyse.return_value = recs
            result = generate_recommendations(populated_snapshot)

        assert result == recs

    def test_empty_snapshot_returns_empty_list(self, empty_snapshot):
        with patch("tools.np_tools.NPRecommender") as mock_cls:
            mock_cls.return_value.analyse.return_value = []
            result = generate_recommendations(empty_snapshot)

        assert result == []


class TestSnapshotSummary:
    def test_summary_keys(self, populated_snapshot):
        summary = snapshot_summary(populated_snapshot)
        assert set(summary.keys()) == {
            "cpy_key",
            "fetched_at",
            "groups",
            "devices",
            "collectors",
            "findings",
        }

    def test_summary_values(self, populated_snapshot):
        summary = snapshot_summary(populated_snapshot)
        assert summary["cpy_key"] == 172361
        assert summary["groups"] == 1
        assert summary["devices"] == 1
        assert summary["collectors"] == 1
        assert summary["findings"] == 0


class TestTopFindings:
    def test_returns_up_to_n(self, populated_snapshot):
        populated_snapshot.recommendations = [
            Recommendation(priority=i, category="Cat", title=f"T{i}", device_name="d", detail="x")
            for i in range(15)
        ]
        result = top_findings(populated_snapshot, n=10)
        assert len(result) == 10

    def test_returns_all_when_fewer_than_n(self, populated_snapshot):
        populated_snapshot.recommendations = [
            Recommendation(priority=1, category="Cat", title="T1", device_name="d", detail="x")
        ]
        result = top_findings(populated_snapshot, n=10)
        assert len(result) == 1

    def test_empty_recommendations(self, populated_snapshot):
        populated_snapshot.recommendations = []
        result = top_findings(populated_snapshot)
        assert result == []

    def test_result_structure(self, populated_snapshot):
        populated_snapshot.recommendations = [
            Recommendation(priority=1, category="Software Currency", title="EOS", device_name="sw-01", detail="old")
        ]
        result = top_findings(populated_snapshot)
        assert result[0]["priority"] == 1
        assert result[0]["category"] == "Software Currency"
        assert result[0]["device"] == "sw-01"
