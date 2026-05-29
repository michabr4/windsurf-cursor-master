"""Tests for RiskEvaluator rules."""

from models import DeliveryAccountRecord, RiskTier
from risk_rules import RiskEvaluator


def test_p1_p2_rule_fires(p1_p2_account):
    risk = RiskEvaluator().evaluate_account(p1_p2_account)
    assert risk.tier == RiskTier.HIGH
    assert "P1/P2 open > 48h" in risk.triggered_rules


def test_p1_p2_rule_clear_when_no_critical_cases():
    account = DeliveryAccountRecord(
        account_id="clear",
        account_name="Clear Co",
        critical_high=0,
        avg_age_days=0,
    )
    risk = RiskEvaluator().evaluate_account(account)
    assert "P1/P2 open > 48h" not in risk.triggered_rules


def test_sla_breach_rule_fires(sla_account):
    risk = RiskEvaluator().evaluate_account(sla_account)
    assert risk.tier == RiskTier.HIGH
    assert "SLA breach predicted within 5 days" in risk.triggered_rules


def test_sla_breach_rule_clear_when_sla_met():
    account = DeliveryAccountRecord(
        account_id="sla-ok",
        account_name="SLA OK",
        sla_status="met",
        sla_actual_pct=98,
        sla_target_pct=95,
    )
    risk = RiskEvaluator().evaluate_account(account)
    assert "SLA breach predicted within 5 days" not in risk.triggered_rules


def test_health_score_rule_fires(health_account):
    risk = RiskEvaluator().evaluate_account(health_account)
    assert risk.tier == RiskTier.HIGH
    assert "Health score dropped > 15 pts in 7 days" in risk.triggered_rules


def test_health_score_rule_skips_without_history():
    account = DeliveryAccountRecord(
        account_id="no-health",
        account_name="No History",
        health_score=80,
    )
    risk = RiskEvaluator().evaluate_account(account)
    assert "Health score dropped > 15 pts in 7 days" not in risk.triggered_rules


def test_milestone_rule_fires(milestone_account):
    risk = RiskEvaluator().evaluate_account(milestone_account)
    assert risk.tier == RiskTier.MEDIUM
    assert "Milestone slipped > 2 weeks" in risk.triggered_rules


def test_milestone_rule_clear_without_slip():
    account = DeliveryAccountRecord(
        account_id="ms-ok",
        account_name="On Track",
        milestones_overdue=0,
        milestone_slip_days=0,
    )
    risk = RiskEvaluator().evaluate_account(account)
    assert "Milestone slipped > 2 weeks" not in risk.triggered_rules


def test_entitlement_rule_fires(entitlement_account):
    risk = RiskEvaluator().evaluate_account(entitlement_account)
    assert risk.tier == RiskTier.MEDIUM
    assert "Entitlement < 20% with renewal < 60 days" in risk.triggered_rules


def test_entitlement_rule_clear_when_above_threshold():
    account = DeliveryAccountRecord(
        account_id="ent-ok",
        account_name="Renewed",
        entitlement_pct=80,
        renewal_days=120,
    )
    risk = RiskEvaluator().evaluate_account(account)
    assert "Entitlement < 20% with renewal < 60 days" not in risk.triggered_rules
