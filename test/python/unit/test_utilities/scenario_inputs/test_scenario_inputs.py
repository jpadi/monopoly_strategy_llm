"""Tests verifying scenario input loader behavior.

This module tests fixture loading infrastructure, NOT the business behavior
of individual scenarios (that's done in test_scenario_expectations.py).

Tests here verify:
- Loader functions work correctly
- JSON fixtures have required structure
- Module purity (no procedural construction)
- Classic board completeness constraint
"""

from __future__ import annotations

import inspect

import pytest

from fixtures import scenarioInputs


# Representative samples for loader tests (not all scenarios)
SAMPLE_VALID_SCENARIOS = [
    "balancedTradeInput",
    "exactlyThreeHousesEachInput",
    "fourRailroadsInput",
    "survivalRiskCriticalInput",
    "reviewRecommendedClassificationInput",
]

SAMPLE_INVALID_SCENARIOS = [
    "invalidPropertyTransferPositiveAmountInput",
    "invalidCashTransferZeroAmountInput",
    "multiPartyTradeInput",
]


class TestFixtureLoaderBehavior:
    """Tests for the fixture loading infrastructure."""

    def test_scenario_function_returns_dict(self) -> None:
        """Scenario functions return dictionaries."""
        data = scenarioInputs.balancedTradeInput()
        assert isinstance(data, dict)

    def test_scenario_function_returns_same_as_direct_load(self) -> None:
        """Named functions match direct JSON loading."""
        from fixtures.fixtureLoader import loadScenarioInput

        via_function = scenarioInputs.balancedTradeInput()
        via_direct = loadScenarioInput("trade_ratio/balanced_trade.json")

        assert via_function == via_direct

    @pytest.mark.parametrize("func_name", SAMPLE_VALID_SCENARIOS)
    def test_valid_scenario_has_required_sections(self, func_name: str) -> None:
        """Valid scenarios have all required input sections."""
        func = getattr(scenarioInputs, func_name)
        data = func()

        assert "metadata" in data
        assert "game_configuration" in data
        assert "board_state_before" in data
        assert "board_state_after" in data
        assert "trade" in data

    @pytest.mark.parametrize("func_name", SAMPLE_INVALID_SCENARIOS)
    def test_invalid_scenario_loads_without_error(self, func_name: str) -> None:
        """Invalid scenarios load via raw loader (bypassing validation)."""
        func = getattr(scenarioInputs, func_name)
        data = func()

        assert isinstance(data, dict)
        assert "trade" in data


class TestScenarioDeterminism:
    """Tests that scenario loading is deterministic."""

    def test_multiple_loads_are_identical(self) -> None:
        """Loading the same scenario twice returns identical data."""
        first = scenarioInputs.balancedTradeInput()
        second = scenarioInputs.balancedTradeInput()
        assert first == second

    def test_deterministic_metadata(self) -> None:
        """Scenarios have fixed timestamps, not runtime-generated."""
        data = scenarioInputs.balancedTradeInput()
        assert data["metadata"]["evaluation_timestamp"] == "2026-01-01T00:00:00Z"
        assert data["metadata"]["platform"] == "test_harness"


class TestClassicBoardCompleteness:
    """Tests that classic board fixtures have complete 28-property boards."""

    def test_classic_scenario_has_28_properties(self) -> None:
        """A classic board scenario has 28 properties."""
        data = scenarioInputs.balancedTradeInput()
        config = data["game_configuration"]

        if config.get("ruleset_name") == "classic_monopoly":
            before = data["board_state_before"]["properties"]
            after = data["board_state_after"]["properties"]

            assert len(before) == 28
            assert len(after) == 28


class TestScenarioModulePurity:
    """Critical guard: scenarioInputs.py must ONLY load JSON fixtures.

    This prevents accidental introduction of procedural board construction
    which would violate the canonical JSON fixture philosophy.
    """

    def test_module_does_not_import_procedural_helpers(self) -> None:
        """scenarioInputs.py must not import procedural construction helpers."""
        source = inspect.getsource(scenarioInputs)

        forbidden_patterns = [
            "from copy import",
            "deepcopy",
            "classicTwoPlayerBoard",
            "customTwoPlayerBoard",
            "twoPlayerBoard",
            "_tradeEnvelope",
            "assignPropertyOwners",
        ]

        for pattern in forbidden_patterns:
            assert pattern not in source, (
                f"scenarioInputs.py contains forbidden pattern '{pattern}'. "
                "Scenario functions must only load JSON fixtures."
            )

    def test_all_public_functions_call_loader(self) -> None:
        """Every public scenario function must call a fixture loader."""
        for name in dir(scenarioInputs):
            if name.startswith("_"):
                continue
            obj = getattr(scenarioInputs, name)
            if not callable(obj) or not inspect.isfunction(obj):
                continue
            if name in ("loadScenarioInput", "loadRawScenarioInput"):
                continue

            source = inspect.getsource(obj)
            assert "loadScenarioInput" in source or "loadRawScenarioInput" in source, (
                f"Function {name} does not call a fixture loader."
            )
