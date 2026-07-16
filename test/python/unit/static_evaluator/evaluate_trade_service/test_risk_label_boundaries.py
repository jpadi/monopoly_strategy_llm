"""Risk label tier boundary coverage through named scenarios."""

from __future__ import annotations

import pytest
from fixtures import scenarioInputs

from .assertions.evidence_assertions import assertCalculationExists

RISK_LABEL_SCENARIOS = [
    pytest.param(
        scenarioInputs.survivalRiskCriticalInput,
        "before",
        "SURVIVAL_RISK_CRITICAL",
        id="critical_before",
    ),
    pytest.param(
        scenarioInputs.survivalRiskModerateInput,
        "before",
        "SURVIVAL_RISK_MODERATE",
        id="moderate_before",
    ),
    pytest.param(
        scenarioInputs.survivalRiskLowInput,
        "before",
        "SURVIVAL_RISK_LOW",
        id="low_before",
    ),
    pytest.param(
        scenarioInputs.survivalRiskVeryLowInput,
        "before",
        "SURVIVAL_RISK_VERY_LOW",
        id="very_low_before",
    ),
]


@pytest.mark.parametrize(
    ("input_fn", "side", "expected_label"),
    RISK_LABEL_SCENARIOS,
)
def test_risk_label_tier(execute_scenario, input_fn, side: str, expected_label: str) -> None:
    """Each committed risk scenario publishes the independently derived label."""
    evidence = execute_scenario(input_fn())
    calc = assertCalculationExists(
        evidence,
        "immediate_risk",
        side=side,
        player_id="player_a",
    )
    assert calc["intermediate_values"]["risk_label"] == expected_label


def test_risk_label_tiers_are_distinct(execute_scenario) -> None:
    """Adjacent tier scenarios produce distinct labels across the penalty spectrum."""
    scenarios = [
        scenarioInputs.survivalRiskCriticalInput(),
        scenarioInputs.survivalRiskModerateInput(),
        scenarioInputs.survivalRiskLowInput(),
        scenarioInputs.survivalRiskVeryLowInput(),
    ]
    labels = []
    for input_data in scenarios:
        evidence = execute_scenario(input_data)
        calc = assertCalculationExists(
            evidence,
            "immediate_risk",
            side="before",
            player_id="player_a",
        )
        labels.append(calc["intermediate_values"]["risk_label"])

    assert labels == [
        "SURVIVAL_RISK_CRITICAL",
        "SURVIVAL_RISK_MODERATE",
        "SURVIVAL_RISK_LOW",
        "SURVIVAL_RISK_VERY_LOW",
    ]
