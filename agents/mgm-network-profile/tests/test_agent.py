"""Unit tests for MGMNetworkProfileAgent."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from agent import MGMNetworkProfileAgent
from models import NPSnapshot, Recommendation


class TestAgentTrustTier:
    def test_trust_tier_is_t3(self):
        assert MGMNetworkProfileAgent.trust_tier == "T3"


class TestValidateInputs:
    def test_passes_with_valid_settings(self, mock_settings):
        agent = MGMNetworkProfileAgent(settings=mock_settings)
        agent.validate_inputs()

    def test_raises_when_mimir_url_missing(self, mock_settings):
        mock_settings.mimir_url = ""
        agent = MGMNetworkProfileAgent(settings=mock_settings)
        with pytest.raises(ValueError, match="MIMIR_URL"):
            agent.validate_inputs()

    def test_raises_when_cpy_key_missing(self, mock_settings):
        mock_settings.np_cpy_key = None
        agent = MGMNetworkProfileAgent(settings=mock_settings)
        with pytest.raises(ValueError, match="NP_CPY_KEY"):
            agent.validate_inputs()


class TestHandleError:
    def test_reraises_exception(self, mock_settings):
        agent = MGMNetworkProfileAgent(settings=mock_settings)
        with pytest.raises(RuntimeError, match="boom"):
            agent.handle_error(RuntimeError("boom"))


class TestRun:
    def test_run_returns_snapshot(self, mock_settings, populated_snapshot):
        with (
            patch("agent.NPExtractor") as mock_extractor_cls,
            patch("agent.NPRecommender") as mock_recommender_cls,
        ):
            mock_extractor = MagicMock()
            mock_extractor.run.return_value = populated_snapshot
            mock_extractor_cls.return_value = mock_extractor

            mock_recommender = MagicMock()
            mock_recommender.analyse.return_value = [
                Recommendation(
                    priority=1,
                    category="Software Currency",
                    title="EOS device",
                    device_name="mgm-core-sw-01",
                    detail="Running EOS version",
                )
            ]
            mock_recommender_cls.return_value = mock_recommender

            agent = MGMNetworkProfileAgent(settings=mock_settings)
            result = agent.run()

        assert result is populated_snapshot
        assert len(result.recommendations) == 1

    def test_run_prints_metrics(self, capsys, mock_settings, populated_snapshot):
        with (
            patch("agent.NPExtractor") as mock_extractor_cls,
            patch("agent.NPRecommender") as mock_recommender_cls,
        ):
            mock_extractor_cls.return_value.run.return_value = populated_snapshot
            mock_recommender_cls.return_value.analyse.return_value = []

            agent = MGMNetworkProfileAgent(settings=mock_settings)
            agent.run()

        captured = capsys.readouterr()
        assert "[METRICS]" in captured.out
        assert "Records processed:" in captured.out

    def test_run_handles_extractor_failure(self, capsys, mock_settings):
        with patch("agent.NPExtractor") as mock_extractor_cls:
            mock_extractor_cls.return_value.run.side_effect = ConnectionError("MIMIR down")

            agent = MGMNetworkProfileAgent(settings=mock_settings)
            with pytest.raises(ConnectionError, match="MIMIR down"):
                agent.run()

        captured = capsys.readouterr()
        assert "errors: 1" in captured.out
