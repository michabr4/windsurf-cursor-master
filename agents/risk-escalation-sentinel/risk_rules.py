"""Risk rule evaluation for account delivery metrics."""

from __future__ import annotations

from typing import List

from models import AccountRisk, DeliveryAccountRecord, RiskTier


class RiskEvaluator:
    """Apply the five SDM risk rules in priority order."""

    HIGH_RULES = (
        "P1/P2 open > 48h",
        "SLA breach predicted within 5 days",
        "Health score dropped > 15 pts in 7 days",
    )
    MEDIUM_RULES = (
        "Milestone slipped > 2 weeks",
        "Entitlement < 20% with renewal < 60 days",
    )

    def evaluate(self, accounts: List[DeliveryAccountRecord]) -> List[AccountRisk]:
        return [self.evaluate_account(account) for account in accounts]

    def evaluate_account(self, account: DeliveryAccountRecord) -> AccountRisk:
        triggered: List[str] = []

        if self._p1_p2_open_over_48h(account):
            triggered.append(self.HIGH_RULES[0])
        if self._sla_breach_within_5_days(account):
            triggered.append(self.HIGH_RULES[1])
        if self._health_score_drop(account):
            triggered.append(self.HIGH_RULES[2])
        if self._milestone_slipped(account):
            triggered.append(self.MEDIUM_RULES[0])
        if self._entitlement_renewal_risk(account):
            triggered.append(self.MEDIUM_RULES[1])

        tier = self._tier_from_rules(triggered)
        summary, action = self._summarize(account, tier, triggered)

        return AccountRisk(
            account_id=account.account_id,
            account_name=account.account_name,
            tier=tier,
            triggered_rules=triggered,
            summary=summary,
            recommended_action=action,
        )

    def _tier_from_rules(self, triggered: List[str]) -> RiskTier:
        if any(rule in self.HIGH_RULES for rule in triggered):
            return RiskTier.HIGH
        if any(rule in self.MEDIUM_RULES for rule in triggered):
            return RiskTier.MEDIUM
        return RiskTier.LOW

    def _p1_p2_open_over_48h(self, account: DeliveryAccountRecord) -> bool:
        if account.p1_p2_open_over_48h is not None:
            return account.p1_p2_open_over_48h > 0
        return account.critical_high > 0 and account.avg_age_days >= 2

    def _sla_breach_within_5_days(self, account: DeliveryAccountRecord) -> bool:
        if account.sla_breach_within_days is not None:
            return account.sla_breach_within_days <= 5
        if account.sla_status in ("at_risk", "breached"):
            return True
        if (
            account.sla_actual_pct is not None
            and account.sla_target_pct is not None
            and account.sla_actual_pct < account.sla_target_pct
        ):
            gap = account.sla_target_pct - account.sla_actual_pct
            return gap >= 5
        return False

    def _health_score_drop(self, account: DeliveryAccountRecord) -> bool:
        if account.health_score is None or account.health_score_prior_7d is None:
            return False
        return (account.health_score_prior_7d - account.health_score) > 15

    def _milestone_slipped(self, account: DeliveryAccountRecord) -> bool:
        if account.milestone_slip_days is not None:
            return account.milestone_slip_days >= 14
        return account.milestones_overdue > 0

    def _entitlement_renewal_risk(self, account: DeliveryAccountRecord) -> bool:
        if account.entitlement_pct is None or account.renewal_days is None:
            return False
        return account.entitlement_pct < 20 and account.renewal_days < 60

    def _summarize(
        self,
        account: DeliveryAccountRecord,
        tier: RiskTier,
        triggered: List[str],
    ) -> tuple[str, str]:
        if tier == RiskTier.LOW:
            return (
                f"{account.account_name} has no active risk signals.",
                "Continue monitoring on the daily delivery tracker review.",
            )

        rules = ", ".join(triggered)
        summary = (
            f"{account.account_name} flagged {tier.value}: {rules}. "
            f"Open cases: {account.total_open}, overdue: {account.overdue}, "
            f"escalated: {account.escalated}."
        )
        if tier == RiskTier.HIGH:
            action = (
                "Review immediately and choose an escalation path in Webex: "
                "Escalate Now, Schedule Call, Snooze 48h, or Dismiss."
            )
        else:
            action = "Schedule a check-in with the account team within 48 hours."
        return summary, action
