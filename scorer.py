"""Deterministic AML alert risk scorer.

The thesis of this demo: money decisions are made by rules, not by a model.
This module assigns a risk score and disposition from fixed, auditable weights.
An LLM never runs here and never changes a number - it only explains the output
downstream (see explain.py). That keeps the decision deterministic, reproducible,
and defensible to a regulator.

Every points contribution is returned in `factors` so the score can be audited
line by line.
"""
from __future__ import annotations
from dataclasses import dataclass, field

# Fixed rule weights. Changing scoring = changing this table, under version control.
# No model, no drift, no "the AI decided".
WEIGHTS = {
    "structuring": 35,          # multiple sub-threshold transfers just under a reporting limit
    "rapid_movement": 25,       # funds in and out within a short window (pass-through / mule)
    "high_risk_jurisdiction": 20,
    "sanctions_name_match": 40, # fuzzy match against a sanctions/PEP list
    "dormant_then_active": 15,  # long-dormant account suddenly transacting at volume
    "counterparty_new": 10,     # first-time counterparty
    "amount_over_expected": 15, # transacted well above the customer's declared profile
}

BANDS = [(70, "ESCALATE"), (40, "REVIEW"), (0, "MONITOR")]


@dataclass
class ScoreResult:
    alert_id: str
    score: int
    disposition: str
    factors: list[dict] = field(default_factory=list)  # [{rule, points, detail}]


def score_alert(alert: dict) -> ScoreResult:
    """Pure function: alert features -> deterministic score. No side effects, no LLM."""
    factors: list[dict] = []
    total = 0
    for rule, points in WEIGHTS.items():
        if alert.get("signals", {}).get(rule):
            total += points
            factors.append({
                "rule": rule,
                "points": points,
                "detail": alert["signals"][rule],
            })
    total = min(total, 100)  # cap; disposition is banded, not linear beyond 100
    disposition = next(label for threshold, label in BANDS if total >= threshold)
    return ScoreResult(alert_id=alert["id"], score=total, disposition=disposition, factors=factors)
