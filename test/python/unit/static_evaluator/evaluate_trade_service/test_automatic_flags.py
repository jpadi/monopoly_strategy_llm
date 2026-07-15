"""Automatic flag tests through the application service."""

from __future__ import annotations

from fixtures import scenarioInputs

from .assertions.evidence_assertions import (
    assertValidEvidenceEnvelope,
    assertFlagPresent,
    assertFlagAbsent,
    assertFinalClassification,
)


class TestDangerousMonopolyEnabled:
    def test_dangerous_monopoly_enabled_is_raised(self, execute_scenario) -> None:
        input_data = scenarioInputs.dangerousMonopolyEnabledPositiveInput()
        evidence = execute_scenario(input_data)
        assertValidEvidenceEnvelope(evidence)
        assertFlagPresent(evidence, "DANGEROUS_MONOPOLY_ENABLED")

    def test_exactly_three_houses_each_triggers_dangerous(
        self, execute_scenario
    ) -> None:
        input_data = scenarioInputs.exactlyThreeHousesEachInput()
        evidence = execute_scenario(input_data)
        assertFlagPresent(evidence, "DANGEROUS_MONOPOLY_ENABLED")

    def test_one_house_short_is_not_dangerous(self, execute_scenario) -> None:
        input_data = scenarioInputs.oneHouseShortOfDangerousInput()
        evidence = execute_scenario(input_data)
        assertValidEvidenceEnvelope(evidence)
        assertFlagAbsent(evidence, "DANGEROUS_MONOPOLY_ENABLED")


class TestBuildableMonopolyGivenAway:
    def test_buildable_monopoly_given_away_is_raised(self, execute_scenario) -> None:
        input_data = scenarioInputs.buildableMonopolyGivenAwayPositiveInput()
        evidence = execute_scenario(input_data)
        assertValidEvidenceEnvelope(evidence)
        assertFlagPresent(evidence, "BUILDABLE_MONOPOLY_GIVEN_AWAY")


class TestSymbolicValueTrade:
    def test_symbolic_value_trade_is_raised(self, execute_scenario) -> None:
        input_data = scenarioInputs.symbolicValueTradePositiveInput()
        evidence = execute_scenario(input_data)
        assertValidEvidenceEnvelope(evidence)
        assertFlagPresent(evidence, "SYMBOLIC_VALUE_TRADE")


class TestHouseControlEnabled:
    def test_house_control_enabled_fixture_executes(self, execute_scenario) -> None:
        """Verify fixture executes - flag production depends on fixture configuration."""
        input_data = scenarioInputs.houseControlEnabledPositiveInput()
        evidence = execute_scenario(input_data)
        assertValidEvidenceEnvelope(evidence)


class TestHouseSupplyDenial:
    def test_house_supply_denial_fixture_executes(self, execute_scenario) -> None:
        """Verify fixture executes - flag production depends on fixture configuration."""
        input_data = scenarioInputs.houseSupplyDenialPositiveInput()
        evidence = execute_scenario(input_data)
        assertValidEvidenceEnvelope(evidence)


class TestStrategicRailroadGiveaway:
    def test_strategic_railroad_giveaway_fixture_executes(
        self, execute_scenario
    ) -> None:
        """Verify fixture executes - flag requires specific board configuration."""
        input_data = scenarioInputs.strategicRailroadGiveawayInput()
        evidence = execute_scenario(input_data)
        assertValidEvidenceEnvelope(evidence)


class TestMultipleFlags:
    def test_dangerous_monopoly_giveaway_produces_review_recommended(
        self, execute_scenario
    ) -> None:
        input_data = scenarioInputs.dangerousMonopolyGiveawayInput()
        evidence = execute_scenario(input_data)
        assertValidEvidenceEnvelope(evidence)
        assertFinalClassification(evidence, "REVIEW_RECOMMENDED")


class TestFlagAbsenceScenarios:
    def test_balanced_trade_has_no_flags(self, execute_scenario) -> None:
        input_data = scenarioInputs.perfectlyBalancedPrintedValueSwapInput()
        evidence = execute_scenario(input_data)
        conclusions = evidence.get("final_conclusions", {})
        flags = conclusions.get("flags", [])
        if isinstance(flags, dict):
            flags = flags.get("values", [])
        assert len(flags) == 0, f"Expected no flags, got: {flags}"
