"""Tests for WebexNotifier."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from config import Settings
from models import AccountRisk, RiskTier
from webex_notifier import WebexNotifier


@pytest.fixture()
def live_settings(settings):
    settings.dry_run = False
    settings.webex_bot_token = "live-token"
    settings.webex_room_id = "room-abc"
    return settings


@pytest.fixture()
def high_risk() -> AccountRisk:
    return AccountRisk(
        account_id="acc-h",
        account_name="Acme Corp",
        tier=RiskTier.HIGH,
        triggered_rules=["P1/P2 open > 48h"],
        summary="Acme Corp flagged HIGH: P1/P2 open > 48h.",
        recommended_action="Escalate Now.",
    )


@pytest.fixture()
def medium_risks():
    return [
        AccountRisk(
            account_id="acc-m1",
            account_name="Beta Ltd",
            tier=RiskTier.MEDIUM,
            triggered_rules=["Milestone slipped > 2 weeks"],
        ),
        AccountRisk(
            account_id="acc-m2",
            account_name="Gamma Inc",
            tier=RiskTier.MEDIUM,
            triggered_rules=["Entitlement < 20% with renewal < 60 days"],
        ),
    ]


class TestSendHighRiskCard:
    def test_dry_run_returns_false(self, settings, high_risk):
        notifier = WebexNotifier(settings)
        assert notifier.send_high_risk_card(high_risk) is False

    @patch("webex_notifier.requests.post")
    def test_live_posts_to_webex(self, mock_post, live_settings, high_risk):
        mock_post.return_value = MagicMock(status_code=200)
        notifier = WebexNotifier(live_settings)
        result = notifier.send_high_risk_card(high_risk)
        assert result is True
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args
        assert call_kwargs.kwargs["json"]["roomId"] == "room-abc"
        assert "attachments" in call_kwargs.kwargs["json"]

    @patch("webex_notifier.requests.post")
    def test_raises_on_http_error(self, mock_post, live_settings, high_risk):
        mock_post.return_value = MagicMock(status_code=401)
        mock_post.return_value.raise_for_status.side_effect = (
            requests.HTTPError("401 Unauthorized")
        )
        notifier = WebexNotifier(live_settings)
        with pytest.raises(requests.HTTPError):
            notifier.send_high_risk_card(high_risk)


class TestBuildCard:
    def test_has_four_actions(self, settings, high_risk):
        notifier = WebexNotifier(settings)
        card = notifier._build_card(high_risk)
        assert len(card["actions"]) == 4

    def test_action_titles(self, settings, high_risk):
        notifier = WebexNotifier(settings)
        titles = [a["title"] for a in notifier._build_card(high_risk)["actions"]]
        assert titles == ["Escalate Now", "Schedule Call", "Snooze 48h", "Dismiss"]

    def test_action_data_contains_account_id(self, settings, high_risk):
        notifier = WebexNotifier(settings)
        card = notifier._build_card(high_risk)
        for action in card["actions"]:
            assert action["data"]["account_id"] == "acc-h"

    def test_card_schema_version(self, settings, high_risk):
        notifier = WebexNotifier(settings)
        card = notifier._build_card(high_risk)
        assert card["type"] == "AdaptiveCard"
        assert card["version"] == "1.2"


class TestSendMediumRiskSummary:
    def test_empty_list_returns_false(self, settings):
        notifier = WebexNotifier(settings)
        assert notifier.send_medium_risk_summary([]) is False

    def test_dry_run_returns_false(self, settings, medium_risks):
        notifier = WebexNotifier(settings)
        assert notifier.send_medium_risk_summary(medium_risks) is False

    @patch("webex_notifier.requests.post")
    def test_live_posts_markdown(self, mock_post, live_settings, medium_risks):
        mock_post.return_value = MagicMock(status_code=200)
        notifier = WebexNotifier(live_settings)
        result = notifier.send_medium_risk_summary(medium_risks)
        assert result is True
        call_kwargs = mock_post.call_args.kwargs
        assert "markdown" in call_kwargs["json"]
        assert "Beta Ltd" in call_kwargs["json"]["markdown"]
        assert "Gamma Inc" in call_kwargs["json"]["markdown"]

    @patch("webex_notifier.requests.post")
    def test_live_posts_to_correct_room(self, mock_post, live_settings, medium_risks):
        mock_post.return_value = MagicMock(status_code=200)
        notifier = WebexNotifier(live_settings)
        notifier.send_medium_risk_summary(medium_risks)
        assert mock_post.call_args.kwargs["json"]["roomId"] == "room-abc"

    @patch("webex_notifier.requests.post")
    def test_raises_on_http_error(self, mock_post, live_settings, medium_risks):
        mock_post.return_value = MagicMock(status_code=500)
        mock_post.return_value.raise_for_status.side_effect = (
            requests.HTTPError("500 Server Error")
        )
        notifier = WebexNotifier(live_settings)
        with pytest.raises(requests.HTTPError):
            notifier.send_medium_risk_summary(medium_risks)
