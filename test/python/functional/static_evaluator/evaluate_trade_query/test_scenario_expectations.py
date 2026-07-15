"""Functional scenario tests through the Query Bus.

Each valid scenario is tested once through the CQRS Query Bus,
verifying the public path produces the expected behavior.

This is NOT a smoke test - every test verifies specific expected output.
"""

from __future__ import annotations

import pytest
from typing import Any

from Monopoly.StaticEvaluation.Domain.Model.TransferValidation import (
    TransferValidationError,
)

import sys
from pathlib import Path

# Add the unit test assertions to the path
sys.path.insert(
    0,
    str(
        Path(__file__).parents[3]
        / "unit"
        / "static_evaluator"
        / "evaluate_trade_service"
    ),
)

from assertions.scenario_registry import (
    ScenarioEntry,
    getValidScenarios,
    getInvalidScenarios,
    getScenarioInputFunction,
)
from assertions.scenario_expectations import assert_scenario_expectations


def _get_flags(evidence: dict[str, Any]) -> list[str]:
    """Extract flags list from evidence."""
    flags_data = evidence.get("final_conclusions", {}).get("flags", {})
    if isinstance(flags_data, dict):
        return flags_data.get("values", [])
    elif isinstance(flags_data, list):
        return flags_data
    return []


def _get_classification(evidence: dict[str, Any]) -> str | None:
    """Extract classification from evidence."""
    return evidence.get("final_conclusions", {}).get("classification")


def _assert_functional_expectations(
    evidence: dict[str, Any],
    scenario: ScenarioEntry,
) -> None:
    """Assert key business expectations for functional tests.

    Functional tests assert the primary business outcome,
    not every detail (that's the unit test's job).
    """
    expected = scenario.expected
    actual_classification = _get_classification(evidence)
    actual_flags = set(_get_flags(evidence))

    # Primary assertion: classification
    if expected.classification is not None:
        assert actual_classification == expected.classification, (
            f"Scenario {scenario.name}: expected classification {expected.classification}, "
            f"got {actual_classification}"
        )

    # Primary flag assertion: at least one expected flag must be present
    if expected.flags:
        found_flags = expected.flags & actual_flags
        assert found_flags, (
            f"Scenario {scenario.name}: expected at least one of {expected.flags}, "
            f"got {actual_flags}"
        )

    # No classification for degraded results
    if expected.no_classification:
        assert actual_classification is None, (
            f"Scenario {scenario.name}: expected no classification, got {actual_classification}"
        )


# ==============================================================================
# VALID SCENARIO FUNCTIONAL TESTS
# ==============================================================================

VALID_SCENARIOS = [pytest.param(entry, id=entry.name) for entry in getValidScenarios()]


@pytest.mark.parametrize("scenario", VALID_SCENARIOS)
def test_scenario_through_query_bus(
    execute_query,
    scenario: ScenarioEntry,
) -> None:
    """Each valid scenario produces expected output through the Query Bus.

    This verifies the complete CQRS path from Query to Evidence.
    """
    input_func = getScenarioInputFunction(scenario.name)
    input_data = input_func()

    evidence = execute_query(input_data)

    # Verify basic evidence structure
    assert evidence is not None
    assert "final_conclusions" in evidence
    assert "intermediate_calculations" in evidence

    # Verify primary business expectations
    assert_scenario_expectations(evidence, scenario)


# ==============================================================================
# INVALID SCENARIO FUNCTIONAL TESTS
# ==============================================================================

VALIDATION_ERROR_SCENARIOS = [
    pytest.param(entry, id=entry.name)
    for entry in getInvalidScenarios()
    if entry.expected.validation_error
]


@pytest.mark.parametrize("scenario", VALIDATION_ERROR_SCENARIOS)
def test_invalid_scenario_through_query_bus(
    execute_query,
    scenario: ScenarioEntry,
) -> None:
    """Invalid scenarios raise appropriate errors through the Query Bus."""
    input_func = getScenarioInputFunction(scenario.name)
    input_data = input_func()

    with pytest.raises(TransferValidationError):
        execute_query(input_data)


DEGRADED_RESULT_SCENARIOS = [
    pytest.param(entry, id=entry.name)
    for entry in getInvalidScenarios()
    if entry.expected.no_classification and not entry.expected.validation_error
]


@pytest.mark.parametrize("scenario", DEGRADED_RESULT_SCENARIOS)
def test_degraded_scenario_through_query_bus(
    execute_query,
    scenario: ScenarioEntry,
) -> None:
    """Degraded scenarios produce evidence without classification through the Query Bus."""
    input_func = getScenarioInputFunction(scenario.name)
    input_data = input_func()

    evidence = execute_query(input_data)

    assert_scenario_expectations(evidence, scenario)
