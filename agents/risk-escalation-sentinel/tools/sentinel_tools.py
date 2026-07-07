"""Tool wrappers exposed for orchestration layers."""

from __future__ import annotations

from typing import List

from config import Settings
from models import AccountRisk, DeliveryAccountRecord
from risk_rules import RiskEvaluator
from webex_notifier import WebexNotifier


def evaluate_risks(accounts: List[DeliveryAccountRecord]) -> List[AccountRisk]:
    return RiskEvaluator().evaluate(accounts)


def get_high_risk_accounts(risks: List[AccountRisk]) -> List[AccountRisk]:
    return [risk for risk in risks if risk.tier.value == "HIGH"]


def format_risk_card(risk: AccountRisk, settings: Settings | None = None) -> dict:
    notifier = WebexNotifier(settings or Settings(dry_run=True))
    return notifier._build_card(risk)
