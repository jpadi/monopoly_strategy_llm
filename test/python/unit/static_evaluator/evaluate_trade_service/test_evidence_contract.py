"""Evidence contract tests: determinism, JSON serialization, dependency graph."""

from __future__ import annotations

import json

import pytest
from fixtures import scenarioInputs

from .assertions.evidence_assertions import (
    assertDeterministicIds,
    assertJsonSerializable,
    assertTradeRatio,
    assertValidDependencyGraph,
)

DETERMINISM_SCENARIOS = [
    pytest.param(scenarioInputs.balancedTradeInput, id="balancedTradeInput"),
    pytest.param(
        scenarioInputs.dangerousMonopolyEnabledPositiveInput,
        id="dangerousMonopolyEnabledPositiveInput",
    ),
    pytest.param(
        scenarioInputs.reviewRecommendedClassificationInput,
        id="reviewRecommendedClassificationInput",
    ),
    pytest.param(scenarioInputs.unavailableMonopolyRentInput, id="unavailableMonopolyRentInput"),
    pytest.param(scenarioInputs.partialMonopolyRentInput, id="partialMonopolyRentInput"),
]

SERIALIZATION_SCENARIOS = [
    pytest.param(scenarioInputs.balancedTradeInput, id="balancedTradeInput"),
    pytest.param(scenarioInputs.unavailableMonopolyRentInput, id="unavailableMonopolyRentInput"),
    pytest.param(scenarioInputs.multiPartyTradeInput, id="multiPartyTradeInput"),
    pytest.param(scenarioInputs.customStreetGroupTradeInput, id="customStreetGroupTradeInput"),
]

DEPENDENCY_SCENARIOS = [
    pytest.param(scenarioInputs.balancedTradeInput, id="balancedTradeInput"),
    pytest.param(scenarioInputs.survivalRiskCriticalInput, id="survivalRiskCriticalInput"),
    pytest.param(scenarioInputs.ratioGreaterThanFiveInput, id="ratioGreaterThanFiveInput"),
]


@pytest.mark.parametrize("input_fn", DETERMINISM_SCENARIOS)
def test_deterministic_output(execute_scenario, input_fn) -> None:
    """Same input produces identical serialized evidence on repeated runs."""
    input_data = input_fn()
    first = execute_scenario(input_data)
    second = execute_scenario(input_data)
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assertDeterministicIds(first)


@pytest.mark.parametrize("input_fn", SERIALIZATION_SCENARIOS)
def test_json_serializable_output(execute_scenario, input_fn) -> None:
    """Evidence dict is fully JSON-serializable without Python-specific values."""
    evidence = execute_scenario(input_fn())
    assertJsonSerializable(evidence)


@pytest.mark.parametrize("input_fn", DEPENDENCY_SCENARIOS)
def test_valid_dependency_graph(execute_scenario, input_fn) -> None:
    """All dependent_calculation_ids resolve and final references are valid."""
    evidence = execute_scenario(input_fn())
    assertValidDependencyGraph(evidence)


def test_trade_ratio_helper_uses_canonical_keys(execute_scenario) -> None:
    """assertTradeRatio reads raw_trade_ratio and published_trade_ratio."""
    evidence = execute_scenario(scenarioInputs.ratioGreaterThanFiveInput())
    assertTradeRatio(evidence, expected_raw=18.0, expected_published=5.0)
