"""Canonical scenario registry mapping all inputs to expected outputs.

This registry is the single source of truth for:
- Every named scenario input function
- Its JSON fixture path
- Its scenario family
- Its primary expected output value
- Whether it's valid or invalid

Every valid business scenario MUST have at least one expected behavioral assertion.
Empty ExpectedOutput is forbidden for business scenarios.

Use this registry to power:
- Scenario-specific unit tests (one meaningful test per scenario)
- Scenario-specific functional tests (one meaningful CQRS test per scenario)
- Registry integrity checks
- Coverage matrix generation
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any


class ScenarioFamily(str, Enum):
    """Scenario family classification."""

    TRADE_RATIO = "trade_ratio"
    BASE_ASSET_VALUE = "base_asset_value"
    DEVELOPMENT_CAPABILITY = "development_capability"
    MONOPOLY_VALUE = "monopoly_value"
    HOUSE_CONTROL = "house_control"
    RAILROAD_VALUE = "railroad_value"
    BLOCKING_VALUE = "blocking_value"
    STRATEGIC_OPPORTUNITY = "strategic_opportunity"
    RISK_COVERAGE = "risk_coverage"
    AUTOMATIC_FLAGS = "automatic_flags"
    INITIATOR_ADJUSTMENT = "initiator_adjustment"
    FINAL_CLASSIFICATION = "final_classification"
    INVALID_INPUT = "invalid_input"
    CUSTOM_BOARD = "custom_board"


class AssertionType(str, Enum):
    """Primary assertion type for the scenario."""

    CLASSIFICATION = "classification"
    FLAG_PRESENT = "flag_present"
    FLAG_ABSENT = "flag_absent"
    RISK_LABEL = "risk_label"
    WARNING_PRESENT = "warning_present"
    VALIDATION_ERROR = "validation_error"
    DEGRADED_RESULT = "degraded_result"
    CALCULATION_STATUS = "calculation_status"


@dataclass(frozen=True)
class ExpectedOutput:
    """Expected output values for a scenario.

    Every valid scenario must have at least one non-empty field.
    """

    classification: str | None = None
    flags: frozenset[str] = frozenset()
    flags_absent: frozenset[str] = frozenset()
    risk_label_a: str | None = None
    risk_label_b: str | None = None
    risk_label_a_before: str | None = None
    risk_label_a_after: str | None = None
    warnings_a: frozenset[str] = frozenset()
    warnings_b: frozenset[str] = frozenset()
    error_expected: bool = False
    validation_error: bool = False
    no_classification: bool = False
    calculation_status: str | None = None
    calculation_status_type: str | None = None
    calculation_status_side: str | None = None

    def has_behavioral_assertion(self) -> bool:
        """Return True if this output has at least one behavioral assertion."""
        return (
            self.classification is not None
            or len(self.flags) > 0
            or len(self.flags_absent) > 0
            or self.risk_label_a is not None
            or self.risk_label_b is not None
            or self.risk_label_a_before is not None
            or self.risk_label_a_after is not None
            or len(self.warnings_a) > 0
            or len(self.warnings_b) > 0
            or self.error_expected
            or self.validation_error
            or self.no_classification
            or self.calculation_status is not None
        )


@dataclass(frozen=True)
class ScenarioEntry:
    """Registry entry for a scenario."""

    name: str
    json_path: str
    family: ScenarioFamily
    description: str
    expected: ExpectedOutput
    primary_assertion: AssertionType
    is_valid: bool = True


def _buildRegistry() -> dict[str, ScenarioEntry]:
    """Build the complete scenario registry with actual expected values."""

    return {
        # ══════════════════════════════════════════════════════════════════════════════
        # TRADE RATIO SCENARIOS (Section 9)
        # ══════════════════════════════════════════════════════════════════════════════
        "perfectlyBalancedPrintedValueSwapInput": ScenarioEntry(
            name="perfectlyBalancedPrintedValueSwapInput",
            json_path="trade_ratio/perfectly_balanced_printed_value_swap.json",
            family=ScenarioFamily.TRADE_RATIO,
            description="Properties of equal strategic and nominal value",
            primary_assertion=AssertionType.CLASSIFICATION,
            expected=ExpectedOutput(
                classification="NO_FLAG",
                flags_absent=frozenset({"SUSPICIOUS_IMBALANCE", "HIGHLY_SUSPICIOUS_IMBALANCE"}),
            ),
        ),
        "ratioJustBelowTwoInput": ScenarioEntry(
            name="ratioJustBelowTwoInput",
            json_path="trade_ratio/ratio_just_below_two.json",
            family=ScenarioFamily.TRADE_RATIO,
            description="Trade ratio immediately below 2.0",
            primary_assertion=AssertionType.CLASSIFICATION,
            expected=ExpectedOutput(
                classification="NO_FLAG",
                flags_absent=frozenset({"SUSPICIOUS_IMBALANCE"}),
            ),
        ),
        "ratioExactlyTwoInput": ScenarioEntry(
            name="ratioExactlyTwoInput",
            json_path="trade_ratio/ratio_exactly_two.json",
            family=ScenarioFamily.TRADE_RATIO,
            description="Trade ratio near 2.0",
            primary_assertion=AssertionType.CLASSIFICATION,
            expected=ExpectedOutput(
                classification="NO_FLAG",
                flags_absent=frozenset({"SUSPICIOUS_IMBALANCE"}),
            ),
        ),
        "ratioJustAboveTwoInput": ScenarioEntry(
            name="ratioJustAboveTwoInput",
            json_path="trade_ratio/ratio_just_above_two.json",
            family=ScenarioFamily.TRADE_RATIO,
            description="Trade ratio immediately above 2.0 but below 3.0",
            primary_assertion=AssertionType.CLASSIFICATION,
            expected=ExpectedOutput(
                classification="NO_FLAG",
                flags_absent=frozenset({"SUSPICIOUS_IMBALANCE"}),
            ),
        ),
        "ratioJustBelowThreeInput": ScenarioEntry(
            name="ratioJustBelowThreeInput",
            json_path="trade_ratio/ratio_just_below_three.json",
            family=ScenarioFamily.TRADE_RATIO,
            description="Trade ratio immediately below 3.0 threshold",
            primary_assertion=AssertionType.CLASSIFICATION,
            expected=ExpectedOutput(
                classification="NO_FLAG",
                flags_absent=frozenset({"SUSPICIOUS_IMBALANCE"}),
            ),
        ),
        "ratioExactlyThreeInput": ScenarioEntry(
            name="ratioExactlyThreeInput",
            json_path="trade_ratio/ratio_exactly_three.json",
            family=ScenarioFamily.TRADE_RATIO,
            description="Trade ratio at SUSPICIOUS_IMBALANCE threshold",
            primary_assertion=AssertionType.CLASSIFICATION,
            expected=ExpectedOutput(
                classification="NO_FLAG",  # Initiator adjustment removed SUSPICIOUS_IMBALANCE
            ),
        ),
        "ratioJustAboveThreeInput": ScenarioEntry(
            name="ratioJustAboveThreeInput",
            json_path="trade_ratio/ratio_just_above_three.json",
            family=ScenarioFamily.TRADE_RATIO,
            description="Trade ratio just above 3.0",
            primary_assertion=AssertionType.CLASSIFICATION,
            expected=ExpectedOutput(
                classification="NO_FLAG",  # Initiator adjustment removed SUSPICIOUS_IMBALANCE
            ),
        ),
        "ratioJustBelowFiveInput": ScenarioEntry(
            name="ratioJustBelowFiveInput",
            json_path="trade_ratio/ratio_just_below_five.json",
            family=ScenarioFamily.TRADE_RATIO,
            description="Trade ratio just below 5.0 threshold",
            primary_assertion=AssertionType.CLASSIFICATION,
            expected=ExpectedOutput(
                classification="NO_FLAG",  # Initiator adjustment removed SUSPICIOUS_IMBALANCE
            ),
        ),
        "ratioExactlyFiveInput": ScenarioEntry(
            name="ratioExactlyFiveInput",
            json_path="trade_ratio/ratio_exactly_five.json",
            family=ScenarioFamily.TRADE_RATIO,
            description="Trade ratio at HIGHLY_SUSPICIOUS_IMBALANCE threshold",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="SOFT_FLAG",
                flags=frozenset({"SUSPICIOUS_IMBALANCE"}),  # Downgraded from HIGHLY by initiator adjustment
            ),
        ),
        "ratioGreaterThanFiveInput": ScenarioEntry(
            name="ratioGreaterThanFiveInput",
            json_path="trade_ratio/ratio_greater_than_five.json",
            family=ScenarioFamily.TRADE_RATIO,
            description="Raw ratio > 5.0, published capped at 5.0",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="SOFT_FLAG",
                flags=frozenset({"SUSPICIOUS_IMBALANCE", "SYMBOLIC_VALUE_TRADE"}),
            ),
        ),
        "bothStrategicValuesZeroInput": ScenarioEntry(
            name="bothStrategicValuesZeroInput",
            json_path="trade_ratio/both_strategic_values_zero.json",
            family=ScenarioFamily.TRADE_RATIO,
            description="Both strategic values equal zero",
            primary_assertion=AssertionType.CLASSIFICATION,
            expected=ExpectedOutput(classification="NO_FLAG"),
        ),
        "oneStrategicValueZeroAInput": ScenarioEntry(
            name="oneStrategicValueZeroAInput",
            json_path="trade_ratio/one_strategic_value_zero_a.json",
            family=ScenarioFamily.TRADE_RATIO,
            description="Player A receives minimal value",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="SOFT_FLAG",
                flags=frozenset({"SUSPICIOUS_IMBALANCE", "SYMBOLIC_VALUE_TRADE"}),
            ),
        ),
        "oneStrategicValueZeroBInput": ScenarioEntry(
            name="oneStrategicValueZeroBInput",
            json_path="trade_ratio/one_strategic_value_zero_b.json",
            family=ScenarioFamily.TRADE_RATIO,
            description="Player B receives minimal value",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="SOFT_FLAG",
                flags=frozenset({"SUSPICIOUS_IMBALANCE", "SYMBOLIC_VALUE_TRADE"}),
            ),
        ),
        "balancedTradeInput": ScenarioEntry(
            name="balancedTradeInput",
            json_path="trade_ratio/balanced_trade.json",
            family=ScenarioFamily.TRADE_RATIO,
            description="Moderate exchange with comparable strategic value",
            primary_assertion=AssertionType.CLASSIFICATION,
            expected=ExpectedOutput(
                classification="NO_FLAG",
                flags_absent=frozenset({"SUSPICIOUS_IMBALANCE"}),
            ),
        ),
        "slightImbalanceTradeInput": ScenarioEntry(
            name="slightImbalanceTradeInput",
            json_path="trade_ratio/slight_imbalance_trade.json",
            family=ScenarioFamily.TRADE_RATIO,
            description="One-sided trade producing SUSPICIOUS_IMBALANCE",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="SOFT_FLAG",
                flags=frozenset({"SUSPICIOUS_IMBALANCE"}),
            ),
        ),
        # ══════════════════════════════════════════════════════════════════════════════
        # BASE ASSET VALUE SCENARIOS (Section 10)
        # ══════════════════════════════════════════════════════════════════════════════
        "cashOnlyTradeInput": ScenarioEntry(
            name="cashOnlyTradeInput",
            json_path="base_asset_value/cash_only_trade.json",
            family=ScenarioFamily.BASE_ASSET_VALUE,
            description="Cash only trade",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="SOFT_FLAG",
                flags=frozenset({"SUSPICIOUS_IMBALANCE", "SYMBOLIC_VALUE_TRADE"}),
            ),
        ),
        "unmortgagedPropertyTransferInput": ScenarioEntry(
            name="unmortgagedPropertyTransferInput",
            json_path="base_asset_value/unmortgaged_property_transfer.json",
            family=ScenarioFamily.BASE_ASSET_VALUE,
            description="Unmortgaged property at full printed value",
            primary_assertion=AssertionType.CLASSIFICATION,
            expected=ExpectedOutput(
                classification="NO_FLAG",
                flags_absent=frozenset({"SUSPICIOUS_IMBALANCE"}),
            ),
        ),
        "mortgagedPropertyTransferInput": ScenarioEntry(
            name="mortgagedPropertyTransferInput",
            json_path="base_asset_value/mortgaged_property_transfer.json",
            family=ScenarioFamily.BASE_ASSET_VALUE,
            description="Mortgaged property with penalty applied",
            primary_assertion=AssertionType.CLASSIFICATION,
            expected=ExpectedOutput(
                classification="NO_FLAG",
                flags_absent=frozenset({"SUSPICIOUS_IMBALANCE"}),
            ),
        ),
        "propertyWithHousesTransferInput": ScenarioEntry(
            name="propertyWithHousesTransferInput",
            json_path="base_asset_value/property_with_houses_transfer.json",
            family=ScenarioFamily.BASE_ASSET_VALUE,
            description="Property with houses includes building value",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="SOFT_FLAG",
                flags=frozenset({"SUSPICIOUS_IMBALANCE", "SYMBOLIC_VALUE_TRADE"}),
            ),
        ),
        "propertyWithHotelTransferInput": ScenarioEntry(
            name="propertyWithHotelTransferInput",
            json_path="base_asset_value/property_with_hotel_transfer.json",
            family=ScenarioFamily.BASE_ASSET_VALUE,
            description="Property with hotel includes hotel liquidation",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="SOFT_FLAG",
                flags=frozenset({"SUSPICIOUS_IMBALANCE", "SYMBOLIC_VALUE_TRADE"}),
            ),
        ),
        "railroadTransferInput": ScenarioEntry(
            name="railroadTransferInput",
            json_path="base_asset_value/railroad_transfer.json",
            family=ScenarioFamily.BASE_ASSET_VALUE,
            description="Railroad transfer at printed value",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="SOFT_FLAG",
                flags=frozenset({"SUSPICIOUS_IMBALANCE", "SYMBOLIC_VALUE_TRADE"}),
            ),
        ),
        "utilityTransferInput": ScenarioEntry(
            name="utilityTransferInput",
            json_path="base_asset_value/utility_transfer.json",
            family=ScenarioFamily.BASE_ASSET_VALUE,
            description="Utility transfer at printed value",
            primary_assertion=AssertionType.CLASSIFICATION,
            expected=ExpectedOutput(
                classification="NO_FLAG",
                flags_absent=frozenset({"SUSPICIOUS_IMBALANCE"}),
            ),
        ),
        # ══════════════════════════════════════════════════════════════════════════════
        # DEVELOPMENT CAPABILITY SCENARIOS (Section 12)
        # ══════════════════════════════════════════════════════════════════════════════
        "cannotBuildAnyHouseInput": ScenarioEntry(
            name="cannotBuildAnyHouseInput",
            json_path="development_capability/cannot_build_any_house.json",
            family=ScenarioFamily.DEVELOPMENT_CAPABILITY,
            description="Cannot build - development multiplier 0.40",
            primary_assertion=AssertionType.CLASSIFICATION,
            expected=ExpectedOutput(
                classification="NO_FLAG",
                flags_absent=frozenset({"DANGEROUS_MONOPOLY_ENABLED"}),
            ),
        ),
        "exactlyOneHouseEachInput": ScenarioEntry(
            name="exactlyOneHouseEachInput",
            json_path="development_capability/exactly_one_house_each.json",
            family=ScenarioFamily.DEVELOPMENT_CAPABILITY,
            description="One house per property - multiplier 1.00",
            primary_assertion=AssertionType.CLASSIFICATION,
            expected=ExpectedOutput(
                classification="NO_FLAG",
                flags_absent=frozenset({"DANGEROUS_MONOPOLY_ENABLED"}),
            ),
        ),
        "exactlyThreeHousesEachInput": ScenarioEntry(
            name="exactlyThreeHousesEachInput",
            json_path="development_capability/exactly_three_houses_each.json",
            family=ScenarioFamily.DEVELOPMENT_CAPABILITY,
            description="Three houses per property - dangerous threshold",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="SOFT_FLAG",
                flags=frozenset({"DANGEROUS_MONOPOLY_ENABLED"}),
            ),
        ),
        "oneHouseShortOfDangerousInput": ScenarioEntry(
            name="oneHouseShortOfDangerousInput",
            json_path="development_capability/one_house_short_of_dangerous.json",
            family=ScenarioFamily.DEVELOPMENT_CAPABILITY,
            description="One house short of dangerous threshold",
            primary_assertion=AssertionType.FLAG_ABSENT,
            expected=ExpectedOutput(
                classification="NO_FLAG",
                flags_absent=frozenset({"DANGEROUS_MONOPOLY_ENABLED"}),
            ),
        ),
        "insufficientBankHousesInput": ScenarioEntry(
            name="insufficientBankHousesInput",
            json_path="development_capability/insufficient_bank_houses.json",
            family=ScenarioFamily.DEVELOPMENT_CAPABILITY,
            description="Bank supply constrains development",
            primary_assertion=AssertionType.FLAG_ABSENT,
            expected=ExpectedOutput(
                classification="NO_FLAG",
                flags_absent=frozenset({"DANGEROUS_MONOPOLY_ENABLED"}),
            ),
        ),
        # ══════════════════════════════════════════════════════════════════════════════
        # RAILROAD VALUE SCENARIOS (Section 15)
        # ══════════════════════════════════════════════════════════════════════════════
        "zeroRailroadsInput": ScenarioEntry(
            name="zeroRailroadsInput",
            json_path="railroad_value/zero_railroads.json",
            family=ScenarioFamily.RAILROAD_VALUE,
            description="Zero railroads owned",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="SOFT_FLAG",
                flags=frozenset({"SUSPICIOUS_IMBALANCE", "SYMBOLIC_VALUE_TRADE"}),
            ),
        ),
        "oneRailroadInput": ScenarioEntry(
            name="oneRailroadInput",
            json_path="railroad_value/one_railroad.json",
            family=ScenarioFamily.RAILROAD_VALUE,
            description="One railroad - $200 base value",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="STRONG_FLAG",
                flags=frozenset({"HIGHLY_SUSPICIOUS_IMBALANCE", "SYMBOLIC_VALUE_TRADE"}),
            ),
        ),
        "twoRailroadsInput": ScenarioEntry(
            name="twoRailroadsInput",
            json_path="railroad_value/two_railroads.json",
            family=ScenarioFamily.RAILROAD_VALUE,
            description="Two railroads - $500 base value",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="STRONG_FLAG",
                flags=frozenset({"HIGHLY_SUSPICIOUS_IMBALANCE", "SYMBOLIC_VALUE_TRADE"}),
            ),
        ),
        "threeRailroadsInput": ScenarioEntry(
            name="threeRailroadsInput",
            json_path="railroad_value/three_railroads.json",
            family=ScenarioFamily.RAILROAD_VALUE,
            description="Three railroads - $900 base value",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="STRONG_FLAG",
                flags=frozenset({"HIGHLY_SUSPICIOUS_IMBALANCE", "SYMBOLIC_VALUE_TRADE"}),
            ),
        ),
        "fourRailroadsInput": ScenarioEntry(
            name="fourRailroadsInput",
            json_path="railroad_value/four_railroads.json",
            family=ScenarioFamily.RAILROAD_VALUE,
            description="Four railroads - $1800 base value",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="STRONG_FLAG",
                flags=frozenset({"HIGHLY_SUSPICIOUS_IMBALANCE", "SYMBOLIC_VALUE_TRADE"}),
            ),
        ),
        "lowDevelopmentContextRailroadsInput": ScenarioEntry(
            name="lowDevelopmentContextRailroadsInput",
            json_path="railroad_value/low_development_context.json",
            family=ScenarioFamily.RAILROAD_VALUE,
            description="Low-dev context - 1.30 multiplier",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="STRONG_FLAG",
                flags=frozenset({"HIGHLY_SUSPICIOUS_IMBALANCE", "SYMBOLIC_VALUE_TRADE"}),
            ),
        ),
        "highDevelopmentContextRailroadsInput": ScenarioEntry(
            name="highDevelopmentContextRailroadsInput",
            json_path="railroad_value/high_development_context.json",
            family=ScenarioFamily.RAILROAD_VALUE,
            description="High-dev context - 0.80 multiplier",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="SOFT_FLAG",
                flags=frozenset({"HIGHLY_SUSPICIOUS_IMBALANCE"}),
            ),
        ),
        "strategicOverpaymentRailroadInput": ScenarioEntry(
            name="strategicOverpaymentRailroadInput",
            json_path="railroad_value/strategic_overpayment_railroad.json",
            family=ScenarioFamily.RAILROAD_VALUE,
            description="Strategic overpayment for fourth railroad",
            primary_assertion=AssertionType.CLASSIFICATION,
            expected=ExpectedOutput(
                classification="NO_FLAG",
                flags_absent=frozenset({"SUSPICIOUS_IMBALANCE"}),
            ),
        ),
        "railroadEngineInput": ScenarioEntry(
            name="railroadEngineInput",
            json_path="railroad_value/railroad_engine.json",
            family=ScenarioFamily.RAILROAD_VALUE,
            description="Complete railroad set",
            primary_assertion=AssertionType.CLASSIFICATION,
            expected=ExpectedOutput(
                classification="NO_FLAG",
                flags_absent=frozenset({"SUSPICIOUS_IMBALANCE"}),
            ),
        ),
        # ══════════════════════════════════════════════════════════════════════════════
        # BLOCKING VALUE SCENARIOS (Section 16)
        # ══════════════════════════════════════════════════════════════════════════════
        "strategicBlockingTradeInput": ScenarioEntry(
            name="strategicBlockingTradeInput",
            json_path="blocking_value/strategic_blocking_trade.json",
            family=ScenarioFamily.BLOCKING_VALUE,
            description="Acquire blocking property",
            primary_assertion=AssertionType.CLASSIFICATION,
            expected=ExpectedOutput(
                classification="NO_FLAG",
                flags_absent=frozenset({"SUSPICIOUS_IMBALANCE"}),
            ),
        ),
        "futureNegotiationLeverageInput": ScenarioEntry(
            name="futureNegotiationLeverageInput",
            json_path="blocking_value/future_negotiation_leverage.json",
            family=ScenarioFamily.BLOCKING_VALUE,
            description="Future negotiation leverage",
            primary_assertion=AssertionType.CLASSIFICATION,
            expected=ExpectedOutput(
                classification="NO_FLAG",
                flags_absent=frozenset({"SUSPICIOUS_IMBALANCE"}),
            ),
        ),
        # ══════════════════════════════════════════════════════════════════════════════
        # RISK COVERAGE SCENARIOS (Section 19)
        # ══════════════════════════════════════════════════════════════════════════════
        "zeroThreatRiskInput": ScenarioEntry(
            name="zeroThreatRiskInput",
            json_path="risk_coverage/zero_threat.json",
            family=ScenarioFamily.RISK_COVERAGE,
            description="Zero threat - no opponent exposure",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="SOFT_FLAG",
                flags=frozenset({"SUSPICIOUS_IMBALANCE", "SYMBOLIC_VALUE_TRADE"}),
            ),
        ),
        "threatGreaterThanResourcesInput": ScenarioEntry(
            name="threatGreaterThanResourcesInput",
            json_path="risk_coverage/threat_greater_than_resources.json",
            family=ScenarioFamily.RISK_COVERAGE,
            description="Threat > resources - deficit",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="STRONG_FLAG",
                flags=frozenset(
                    {
                        "BUILDABLE_MONOPOLY_GIVEN_AWAY",
                        "SUSPICIOUS_IMBALANCE",
                        "SYMBOLIC_VALUE_TRADE",
                    }
                ),
            ),
        ),
        "survivalRiskCriticalInput": ScenarioEntry(
            name="survivalRiskCriticalInput",
            json_path="risk_coverage/survival_risk_critical.json",
            family=ScenarioFamily.RISK_COVERAGE,
            description="SURVIVAL_RISK_CRITICAL (penalty >= 900)",
            primary_assertion=AssertionType.RISK_LABEL,
            expected=ExpectedOutput(
                classification="STRONG_FLAG",
                flags=frozenset(
                    {
                        "BUILDABLE_MONOPOLY_GIVEN_AWAY",
                        "SUSPICIOUS_IMBALANCE",
                        "SYMBOLIC_VALUE_TRADE",
                    }
                ),
                risk_label_a_after="SURVIVAL_RISK_CRITICAL",
                warnings_a=frozenset({"PLAYER_CANNOT_SURVIVE_ONE_LANDING"}),
            ),
        ),
        "survivalRiskModerateInput": ScenarioEntry(
            name="survivalRiskModerateInput",
            json_path="risk_coverage/survival_risk_moderate.json",
            family=ScenarioFamily.RISK_COVERAGE,
            description="SURVIVAL_RISK_MODERATE (0 < penalty < 600)",
            primary_assertion=AssertionType.RISK_LABEL,
            expected=ExpectedOutput(
                risk_label_a_before="SURVIVAL_RISK_MODERATE",
            ),
        ),
        "survivalRiskLowInput": ScenarioEntry(
            name="survivalRiskLowInput",
            json_path="risk_coverage/survival_risk_low.json",
            family=ScenarioFamily.RISK_COVERAGE,
            description="SURVIVAL_RISK_LOW (penalty = 0)",
            primary_assertion=AssertionType.RISK_LABEL,
            expected=ExpectedOutput(
                risk_label_a_before="SURVIVAL_RISK_LOW",
            ),
        ),
        "survivalRiskVeryLowInput": ScenarioEntry(
            name="survivalRiskVeryLowInput",
            json_path="risk_coverage/survival_risk_very_low.json",
            family=ScenarioFamily.RISK_COVERAGE,
            description="SURVIVAL_RISK_VERY_LOW - coverage bonus",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="SOFT_FLAG",
                flags=frozenset({"SUSPICIOUS_IMBALANCE", "SYMBOLIC_VALUE_TRADE"}),
            ),
        ),
        "tradeImprovesRiskInput": ScenarioEntry(
            name="tradeImprovesRiskInput",
            json_path="risk_coverage/trade_improves_risk.json",
            family=ScenarioFamily.RISK_COVERAGE,
            description="Trade improves risk coverage",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="STRONG_FLAG",
                flags=frozenset({"HIGHLY_SUSPICIOUS_IMBALANCE", "SYMBOLIC_VALUE_TRADE"}),
            ),
        ),
        "tradeWorsensRiskInput": ScenarioEntry(
            name="tradeWorsensRiskInput",
            json_path="risk_coverage/trade_worsens_risk.json",
            family=ScenarioFamily.RISK_COVERAGE,
            description="Trade worsens risk coverage",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="STRONG_FLAG",
                flags=frozenset(
                    {
                        "BUILDABLE_MONOPOLY_GIVEN_AWAY",
                        "SUSPICIOUS_IMBALANCE",
                        "SYMBOLIC_VALUE_TRADE",
                    }
                ),
            ),
        ),
        "riskCoverageImprovementInput": ScenarioEntry(
            name="riskCoverageImprovementInput",
            json_path="risk_coverage/risk_coverage_improvement.json",
            family=ScenarioFamily.RISK_COVERAGE,
            description="Significant risk improvement",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="STRONG_FLAG",
                flags=frozenset({"HIGHLY_SUSPICIOUS_IMBALANCE", "SYMBOLIC_VALUE_TRADE"}),
            ),
        ),
        "riskCoverageDeteriorationInput": ScenarioEntry(
            name="riskCoverageDeteriorationInput",
            json_path="risk_coverage/risk_coverage_deterioration.json",
            family=ScenarioFamily.RISK_COVERAGE,
            description="Significant risk deterioration",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="SOFT_FLAG",
                flags=frozenset({"SUSPICIOUS_IMBALANCE"}),
            ),
        ),
        # ══════════════════════════════════════════════════════════════════════════════
        # AUTOMATIC FLAGS SCENARIOS (Section 20)
        # ══════════════════════════════════════════════════════════════════════════════
        "buildableMonopolyGivenAwayPositiveInput": ScenarioEntry(
            name="buildableMonopolyGivenAwayPositiveInput",
            json_path="automatic_flags/buildable_monopoly_given_away.json",
            family=ScenarioFamily.AUTOMATIC_FLAGS,
            description="BUILDABLE_MONOPOLY_GIVEN_AWAY flag",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="REVIEW_RECOMMENDED",
                flags=frozenset(
                    {
                        "BUILDABLE_MONOPOLY_GIVEN_AWAY",
                        "DANGEROUS_MONOPOLY_ENABLED",
                        "SUSPICIOUS_IMBALANCE",
                        "SYMBOLIC_VALUE_TRADE",
                    }
                ),
            ),
        ),
        "dangerousMonopolyEnabledPositiveInput": ScenarioEntry(
            name="dangerousMonopolyEnabledPositiveInput",
            json_path="automatic_flags/dangerous_monopoly_enabled.json",
            family=ScenarioFamily.AUTOMATIC_FLAGS,
            description="DANGEROUS_MONOPOLY_ENABLED flag",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="REVIEW_RECOMMENDED",
                flags=frozenset(
                    {
                        "BUILDABLE_MONOPOLY_GIVEN_AWAY",
                        "DANGEROUS_MONOPOLY_ENABLED",
                        "SUSPICIOUS_IMBALANCE",
                        "SYMBOLIC_VALUE_TRADE",
                    }
                ),
            ),
        ),
        "symbolicValueTradePositiveInput": ScenarioEntry(
            name="symbolicValueTradePositiveInput",
            json_path="automatic_flags/symbolic_value_trade.json",
            family=ScenarioFamily.AUTOMATIC_FLAGS,
            description="SYMBOLIC_VALUE_TRADE flag",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="REVIEW_RECOMMENDED",
                flags=frozenset(
                    {
                        "BUILDABLE_MONOPOLY_GIVEN_AWAY",
                        "DANGEROUS_MONOPOLY_ENABLED",
                        "SUSPICIOUS_IMBALANCE",
                        "SYMBOLIC_VALUE_TRADE",
                    }
                ),
            ),
        ),
        "houseControlEnabledPositiveInput": ScenarioEntry(
            name="houseControlEnabledPositiveInput",
            json_path="automatic_flags/house_control_enabled.json",
            family=ScenarioFamily.AUTOMATIC_FLAGS,
            description="HOUSE_CONTROL_ENABLED flag",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="REVIEW_RECOMMENDED",
                flags=frozenset(
                    {
                        "BUILDABLE_MONOPOLY_GIVEN_AWAY",
                        "DANGEROUS_MONOPOLY_ENABLED",
                        "HIGHLY_SUSPICIOUS_IMBALANCE",
                        "SYMBOLIC_VALUE_TRADE",
                    }
                ),
            ),
        ),
        "houseSupplyDenialPositiveInput": ScenarioEntry(
            name="houseSupplyDenialPositiveInput",
            json_path="automatic_flags/house_supply_denial.json",
            family=ScenarioFamily.AUTOMATIC_FLAGS,
            description="HOUSE_SUPPLY_DENIAL flag",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="REVIEW_RECOMMENDED",
                flags=frozenset(
                    {
                        "BUILDABLE_MONOPOLY_GIVEN_AWAY",
                        "DANGEROUS_MONOPOLY_ENABLED",
                        "HIGHLY_SUSPICIOUS_IMBALANCE",
                        "SYMBOLIC_VALUE_TRADE",
                    }
                ),
            ),
        ),
        "suspiciousImbalancePositiveInput": ScenarioEntry(
            name="suspiciousImbalancePositiveInput",
            json_path="automatic_flags/suspicious_imbalance.json",
            family=ScenarioFamily.AUTOMATIC_FLAGS,
            description="SUSPICIOUS_IMBALANCE flag",
            primary_assertion=AssertionType.CLASSIFICATION,
            expected=ExpectedOutput(
                classification="NO_FLAG",  # Initiator adjustment removed flag
            ),
        ),
        "highlySuspiciousImbalancePositiveInput": ScenarioEntry(
            name="highlySuspiciousImbalancePositiveInput",
            json_path="automatic_flags/highly_suspicious_imbalance.json",
            family=ScenarioFamily.AUTOMATIC_FLAGS,
            description="HIGHLY_SUSPICIOUS_IMBALANCE flag",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="SOFT_FLAG",
                flags=frozenset({"SUSPICIOUS_IMBALANCE"}),  # Downgraded by initiator adjustment
            ),
        ),
        "dangerousMonopolyGiveawayInput": ScenarioEntry(
            name="dangerousMonopolyGiveawayInput",
            json_path="automatic_flags/dangerous_monopoly_giveaway.json",
            family=ScenarioFamily.AUTOMATIC_FLAGS,
            description="Multiple flags - dangerous monopoly giveaway",
            primary_assertion=AssertionType.CLASSIFICATION,
            expected=ExpectedOutput(
                classification="REVIEW_RECOMMENDED",
                flags=frozenset(
                    {
                        "BUILDABLE_MONOPOLY_GIVEN_AWAY",
                        "DANGEROUS_MONOPOLY_ENABLED",
                        "SUSPICIOUS_IMBALANCE",
                        "SYMBOLIC_VALUE_TRADE",
                    }
                ),
            ),
        ),
        "houseSupplyControlInput": ScenarioEntry(
            name="houseSupplyControlInput",
            json_path="automatic_flags/house_supply_control.json",
            family=ScenarioFamily.AUTOMATIC_FLAGS,
            description="House supply control scenario",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="SOFT_FLAG",
                flags=frozenset({"DANGEROUS_MONOPOLY_ENABLED"}),
            ),
        ),
        "immediateDevelopmentPreventionInput": ScenarioEntry(
            name="immediateDevelopmentPreventionInput",
            json_path="automatic_flags/immediate_development_prevention.json",
            family=ScenarioFamily.AUTOMATIC_FLAGS,
            description="Development prevention via house denial",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="REVIEW_RECOMMENDED",
                flags=frozenset(
                    {
                        "BUILDABLE_MONOPOLY_GIVEN_AWAY",
                        "DANGEROUS_MONOPOLY_ENABLED",
                        "HIGHLY_SUSPICIOUS_IMBALANCE",
                        "HOUSE_CONTROL_ENABLED",
                        "HOUSE_SUPPLY_DENIAL",
                    }
                ),
            ),
        ),
        "buildableMonopolyGiveawayInput": ScenarioEntry(
            name="buildableMonopolyGiveawayInput",
            json_path="automatic_flags/buildable_monopoly_giveaway.json",
            family=ScenarioFamily.AUTOMATIC_FLAGS,
            description="Buildable monopoly giveaway",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="REVIEW_RECOMMENDED",
                flags=frozenset(
                    {
                        "BUILDABLE_MONOPOLY_GIVEN_AWAY",
                        "DANGEROUS_MONOPOLY_ENABLED",
                        "SUSPICIOUS_IMBALANCE",
                        "SYMBOLIC_VALUE_TRADE",
                    }
                ),
            ),
        ),
        "orangeMonopolyTradeInput": ScenarioEntry(
            name="orangeMonopolyTradeInput",
            json_path="automatic_flags/orange_monopoly_trade.json",
            family=ScenarioFamily.AUTOMATIC_FLAGS,
            description="Orange monopoly completion trade",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="SOFT_FLAG",
                flags=frozenset({"SUSPICIOUS_IMBALANCE", "SYMBOLIC_VALUE_TRADE"}),
            ),
        ),
        "strategicRailroadGiveawayInput": ScenarioEntry(
            name="strategicRailroadGiveawayInput",
            json_path="automatic_flags/strategic_railroad_giveaway.json",
            family=ScenarioFamily.AUTOMATIC_FLAGS,
            description="STRATEGIC_RAILROAD_GIVEAWAY flag on mostly blocked board",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="STRONG_FLAG",
                flags=frozenset(
                    {
                        "STRATEGIC_RAILROAD_GIVEAWAY",
                        "SUSPICIOUS_IMBALANCE",
                        "SYMBOLIC_VALUE_TRADE",
                    }
                ),
            ),
        ),
        "strategicRailroadNoFlagInput": ScenarioEntry(
            name="strategicRailroadNoFlagInput",
            json_path="automatic_flags/strategic_railroad_no_flag.json",
            family=ScenarioFamily.AUTOMATIC_FLAGS,
            description="Fourth railroad not transferred — no STRATEGIC_RAILROAD_GIVEAWAY",
            primary_assertion=AssertionType.FLAG_ABSENT,
            expected=ExpectedOutput(
                flags_absent=frozenset({"STRATEGIC_RAILROAD_GIVEAWAY"}),
            ),
        ),
        "symbolicTradeInput": ScenarioEntry(
            name="symbolicTradeInput",
            json_path="automatic_flags/symbolic_trade.json",
            family=ScenarioFamily.AUTOMATIC_FLAGS,
            description="Symbolic trade scenario",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="REVIEW_RECOMMENDED",
                flags=frozenset(
                    {
                        "BUILDABLE_MONOPOLY_GIVEN_AWAY",
                        "DANGEROUS_MONOPOLY_ENABLED",
                        "SUSPICIOUS_IMBALANCE",
                        "SYMBOLIC_VALUE_TRADE",
                    }
                ),
            ),
        ),
        "houseSupplyDenialInput": ScenarioEntry(
            name="houseSupplyDenialInput",
            json_path="automatic_flags/house_supply_denial_pure.json",
            family=ScenarioFamily.AUTOMATIC_FLAGS,
            description="Pure house supply denial",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="REVIEW_RECOMMENDED",
                flags=frozenset(
                    {
                        "BUILDABLE_MONOPOLY_GIVEN_AWAY",
                        "DANGEROUS_MONOPOLY_ENABLED",
                        "HIGHLY_SUSPICIOUS_IMBALANCE",
                        "HOUSE_CONTROL_ENABLED",
                        "HOUSE_SUPPLY_DENIAL",
                    }
                ),
            ),
        ),
        # ══════════════════════════════════════════════════════════════════════════════
        # INITIATOR ADJUSTMENT SCENARIOS (Section 21)
        # ══════════════════════════════════════════════════════════════════════════════
        "initiatorIsApparentOverpayerInput": ScenarioEntry(
            name="initiatorIsApparentOverpayerInput",
            json_path="initiator_adjustment/initiator_is_apparent_overpayer.json",
            family=ScenarioFamily.INITIATOR_ADJUSTMENT,
            description="Initiator is overpayer - adjustment applies",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="SOFT_FLAG",
                flags=frozenset({"SUSPICIOUS_IMBALANCE"}),  # Adjusted from HIGHLY
            ),
        ),
        "initiatorIsNotApparentOverpayerInput": ScenarioEntry(
            name="initiatorIsNotApparentOverpayerInput",
            json_path="initiator_adjustment/initiator_is_not_apparent_overpayer.json",
            family=ScenarioFamily.INITIATOR_ADJUSTMENT,
            description="Initiator is NOT overpayer - no adjustment",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="SOFT_FLAG",
                flags=frozenset({"HIGHLY_SUSPICIOUS_IMBALANCE"}),  # Not adjusted
            ),
        ),
        # ══════════════════════════════════════════════════════════════════════════════
        # FINAL CLASSIFICATION SCENARIOS (Section 22)
        # ══════════════════════════════════════════════════════════════════════════════
        "noFlagClassificationInput": ScenarioEntry(
            name="noFlagClassificationInput",
            json_path="final_classification/no_flag.json",
            family=ScenarioFamily.FINAL_CLASSIFICATION,
            description="NO_FLAG classification",
            primary_assertion=AssertionType.CLASSIFICATION,
            expected=ExpectedOutput(
                classification="NO_FLAG",
                flags_absent=frozenset({"SUSPICIOUS_IMBALANCE", "HIGHLY_SUSPICIOUS_IMBALANCE"}),
            ),
        ),
        "softFlagClassificationInput": ScenarioEntry(
            name="softFlagClassificationInput",
            json_path="final_classification/soft_flag.json",
            family=ScenarioFamily.FINAL_CLASSIFICATION,
            description="SOFT_FLAG classification via SUSPICIOUS_IMBALANCE",
            primary_assertion=AssertionType.CLASSIFICATION,
            expected=ExpectedOutput(
                classification="SOFT_FLAG",
                flags=frozenset({"SUSPICIOUS_IMBALANCE"}),
            ),
        ),
        "strongFlagClassificationInput": ScenarioEntry(
            name="strongFlagClassificationInput",
            json_path="final_classification/strong_flag.json",
            family=ScenarioFamily.FINAL_CLASSIFICATION,
            description="STRONG_FLAG classification",
            primary_assertion=AssertionType.CLASSIFICATION,
            expected=ExpectedOutput(
                classification="REVIEW_RECOMMENDED",
                flags=frozenset(
                    {
                        "BUILDABLE_MONOPOLY_GIVEN_AWAY",
                        "DANGEROUS_MONOPOLY_ENABLED",
                        "SUSPICIOUS_IMBALANCE",
                        "SYMBOLIC_VALUE_TRADE",
                    }
                ),
            ),
        ),
        "reviewRecommendedClassificationInput": ScenarioEntry(
            name="reviewRecommendedClassificationInput",
            json_path="final_classification/review_recommended.json",
            family=ScenarioFamily.FINAL_CLASSIFICATION,
            description="REVIEW_RECOMMENDED classification",
            primary_assertion=AssertionType.CLASSIFICATION,
            expected=ExpectedOutput(
                classification="REVIEW_RECOMMENDED",
                flags=frozenset(
                    {
                        "BUILDABLE_MONOPOLY_GIVEN_AWAY",
                        "DANGEROUS_MONOPOLY_ENABLED",
                        "SUSPICIOUS_IMBALANCE",
                        "SYMBOLIC_VALUE_TRADE",
                    }
                ),
            ),
        ),
        # ══════════════════════════════════════════════════════════════════════════════
        # INVALID INPUT SCENARIOS (Section 23)
        # ══════════════════════════════════════════════════════════════════════════════
        "invalidPropertyTransferPositiveAmountInput": ScenarioEntry(
            name="invalidPropertyTransferPositiveAmountInput",
            json_path="invalid_input/property_positive_amount.json",
            family=ScenarioFamily.INVALID_INPUT,
            description="Property transfer with amount > 0",
            primary_assertion=AssertionType.VALIDATION_ERROR,
            expected=ExpectedOutput(validation_error=True),
            is_valid=False,
        ),
        "invalidCashTransferZeroAmountInput": ScenarioEntry(
            name="invalidCashTransferZeroAmountInput",
            json_path="invalid_input/cash_zero_amount.json",
            family=ScenarioFamily.INVALID_INPUT,
            description="Cash transfer with amount = 0",
            primary_assertion=AssertionType.VALIDATION_ERROR,
            expected=ExpectedOutput(validation_error=True),
            is_valid=False,
        ),
        "invalidCashTransferWithAssetIdInput": ScenarioEntry(
            name="invalidCashTransferWithAssetIdInput",
            json_path="invalid_input/cash_with_asset_id.json",
            family=ScenarioFamily.INVALID_INPUT,
            description="Cash transfer with non-null asset_id",
            primary_assertion=AssertionType.VALIDATION_ERROR,
            expected=ExpectedOutput(validation_error=True),
            is_valid=False,
        ),
        "invalidPropertyTransferMissingAssetIdInput": ScenarioEntry(
            name="invalidPropertyTransferMissingAssetIdInput",
            json_path="invalid_input/property_missing_asset_id.json",
            family=ScenarioFamily.INVALID_INPUT,
            description="Property transfer without asset_id",
            primary_assertion=AssertionType.VALIDATION_ERROR,
            expected=ExpectedOutput(validation_error=True),
            is_valid=False,
        ),
        "missingRentInformationInput": ScenarioEntry(
            name="missingRentInformationInput",
            json_path="invalid_input/missing_rent_information.json",
            family=ScenarioFamily.INVALID_INPUT,
            description="Missing rent data - partial/unavailable status",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="SOFT_FLAG",
                flags=frozenset({"SUSPICIOUS_IMBALANCE", "SYMBOLIC_VALUE_TRADE"}),
            ),
            is_valid=False,
        ),
        "multiPartyTradeInput": ScenarioEntry(
            name="multiPartyTradeInput",
            json_path="invalid_input/multi_party_trade.json",
            family=ScenarioFamily.INVALID_INPUT,
            description="Unsupported participant count (>2)",
            primary_assertion=AssertionType.DEGRADED_RESULT,
            expected=ExpectedOutput(no_classification=True),
            is_valid=False,
        ),
        "nonTradablePropertyInput": ScenarioEntry(
            name="nonTradablePropertyInput",
            json_path="invalid_input/non_tradable_property.json",
            family=ScenarioFamily.INVALID_INPUT,
            description="Non-tradable property transfer",
            primary_assertion=AssertionType.DEGRADED_RESULT,
            expected=ExpectedOutput(no_classification=True),
            is_valid=False,
        ),
        # ══════════════════════════════════════════════════════════════════════════════
        # CUSTOM BOARD SCENARIOS (Section 24)
        # ══════════════════════════════════════════════════════════════════════════════
        "customStreetGroupTradeInput": ScenarioEntry(
            name="customStreetGroupTradeInput",
            json_path="custom_board/custom_street_group.json",
            family=ScenarioFamily.CUSTOM_BOARD,
            description="Custom board with neutral multiplier",
            primary_assertion=AssertionType.FLAG_PRESENT,
            expected=ExpectedOutput(
                classification="SOFT_FLAG",
                flags=frozenset({"DANGEROUS_MONOPOLY_ENABLED"}),
            ),
        ),
        "partialMonopolyRentInput": ScenarioEntry(
            name="partialMonopolyRentInput",
            json_path="custom_board/partial_monopoly_rent.json",
            family=ScenarioFamily.CUSTOM_BOARD,
            description="Partial monopoly value when one group lacks rent data",
            primary_assertion=AssertionType.CALCULATION_STATUS,
            expected=ExpectedOutput(
                calculation_status="PARTIAL",
                calculation_status_type="monopoly_value",
                calculation_status_side="after",
            ),
        ),
        "unavailableMonopolyRentInput": ScenarioEntry(
            name="unavailableMonopolyRentInput",
            json_path="custom_board/unavailable_monopoly_rent.json",
            family=ScenarioFamily.CUSTOM_BOARD,
            description="Monopoly completed with missing rent_table produces UNAVAILABLE",
            primary_assertion=AssertionType.CALCULATION_STATUS,
            expected=ExpectedOutput(
                classification="SOFT_FLAG",
                flags=frozenset({"DANGEROUS_MONOPOLY_ENABLED"}),
                calculation_status="UNAVAILABLE",
                calculation_status_type="monopoly_value",
                calculation_status_side="after",
            ),
        ),
    }


SCENARIO_REGISTRY: dict[str, ScenarioEntry] = _buildRegistry()


def getValidScenarios() -> list[ScenarioEntry]:
    """Get all valid scenario entries."""
    return [s for s in SCENARIO_REGISTRY.values() if s.is_valid]


def getInvalidScenarios() -> list[ScenarioEntry]:
    """Get all invalid scenario entries."""
    return [s for s in SCENARIO_REGISTRY.values() if not s.is_valid]


def getScenariosByFamily(family: ScenarioFamily) -> list[ScenarioEntry]:
    """Get all scenarios in a family."""
    return [s for s in SCENARIO_REGISTRY.values() if s.family == family]


def getScenarioInputFunction(name: str) -> Callable[[], dict[str, Any]]:
    """Get the scenario input function by name."""
    from fixtures import scenarioInputs

    return getattr(scenarioInputs, name)


def getScenariosWithoutExpectations() -> list[ScenarioEntry]:
    """Get scenarios that lack behavioral assertions (should be empty for valid scenarios)."""
    return [s for s in SCENARIO_REGISTRY.values() if s.is_valid and not s.expected.has_behavioral_assertion()]
