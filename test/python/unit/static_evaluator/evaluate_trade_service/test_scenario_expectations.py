"""Scenario-specific behavioral unit tests.

Each scenario is tested exactly once with its declared expected behavior.
This is NOT a smoke test - every test verifies the specific output
the scenario was designed to produce.

Philosophy:
- One meaningful test per scenario
- Every test makes at least one behavioral assertion
- No redundant parameterization across multiple generic tests
"""

from __future__ import annotations

import pytest

from Monopoly.StaticEvaluation.Domain.Model.TransferValidation import (
    TransferValidationError,
)

from .assertions.scenario_registry import (
    ScenarioEntry,
    getValidScenarios,
    getInvalidScenarios,
    getScenarioInputFunction,
)
from .assertions.scenario_expectations import assert_scenario_expectations


# ==============================================================================
# VALID SCENARIO TESTS - One meaningful test per scenario
# ==============================================================================

VALID_SCENARIOS = [pytest.param(entry, id=entry.name) for entry in getValidScenarios()]


@pytest.mark.parametrize("scenario", VALID_SCENARIOS)
def test_scenario_produces_expected_behavior(
    execute_scenario,
    scenario: ScenarioEntry,
) -> None:
    """Each valid scenario produces its declared expected behavior.

    This test verifies the SPECIFIC output each scenario was designed to produce,
    not just that it executes without error.
    """
    input_func = getScenarioInputFunction(scenario.name)
    input_data = input_func()

    evidence = execute_scenario(input_data)

    assert_scenario_expectations(evidence, scenario)


# ==============================================================================
# INVALID SCENARIO TESTS - One test per invalid scenario
# ==============================================================================

VALIDATION_ERROR_SCENARIOS = [
    pytest.param(entry, id=entry.name)
    for entry in getInvalidScenarios()
    if entry.expected.validation_error
]


@pytest.mark.parametrize("scenario", VALIDATION_ERROR_SCENARIOS)
def test_invalid_scenario_raises_validation_error(
    execute_scenario,
    scenario: ScenarioEntry,
) -> None:
    """Invalid scenarios with validation errors raise TransferValidationError."""
    input_func = getScenarioInputFunction(scenario.name)
    input_data = input_func()

    with pytest.raises(TransferValidationError):
        execute_scenario(input_data)


DEGRADED_RESULT_SCENARIOS = [
    pytest.param(entry, id=entry.name)
    for entry in getInvalidScenarios()
    if entry.expected.no_classification and not entry.expected.validation_error
]


@pytest.mark.parametrize("scenario", DEGRADED_RESULT_SCENARIOS)
def test_degraded_scenario_produces_no_classification(
    execute_scenario,
    scenario: ScenarioEntry,
) -> None:
    """Degraded scenarios produce evidence but no classification."""
    input_func = getScenarioInputFunction(scenario.name)
    input_data = input_func()

    evidence = execute_scenario(input_data)

    assert_scenario_expectations(evidence, scenario)


# Handle scenarios that execute but have flags (like missingRentInformationInput)
INVALID_BUT_EXECUTES_SCENARIOS = [
    pytest.param(entry, id=entry.name)
    for entry in getInvalidScenarios()
    if not entry.expected.validation_error
    and not entry.expected.no_classification
    and entry.expected.has_behavioral_assertion()
]


@pytest.mark.parametrize("scenario", INVALID_BUT_EXECUTES_SCENARIOS)
def test_invalid_scenario_executes_with_expected_output(
    execute_scenario,
    scenario: ScenarioEntry,
) -> None:
    """Some invalid scenarios execute with degraded but verifiable output."""
    input_func = getScenarioInputFunction(scenario.name)
    input_data = input_func()

    evidence = execute_scenario(input_data)

    assert_scenario_expectations(evidence, scenario)
