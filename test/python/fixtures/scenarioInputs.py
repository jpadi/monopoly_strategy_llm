"""Scenario input loaders for Static Evaluator tests.

Each function documents and loads a canonical JSON fixture.
JSON fixtures are the authoritative source of scenario data.
Functions provide:
- Readable imports and IDE navigation
- Scenario documentation in docstrings
- Stable test APIs

DO NOT procedurally construct scenarios in this module.
All valid scenarios must load from canonical JSON files.
"""

from __future__ import annotations

from typing import Any

from fixtures.fixtureLoader import loadScenarioInput, loadRawScenarioInput


# ──────────────────────────────────────────────────────────────
# Trade Ratio Boundary Scenarios (Section 9)
# ──────────────────────────────────────────────────────────────


def perfectlyBalancedPrintedValueSwapInput() -> dict[str, Any]:
    """9.1: Properties of equal strategic and nominal value.

    Both players swap Orange group properties (St. James and Tennessee)
    with identical $180 printed value and no strategic advantage.

    Expected:
    - Strategic values approximately equal
    - Trade ratio close to 1.0
    - Classification: NO_FLAG
    """
    return loadScenarioInput("trade_ratio/perfectly_balanced_printed_value_swap.json")


def ratioJustBelowTwoInput() -> dict[str, Any]:
    """9.3: Trade ratio immediately below 2.0.

    Player A gives St. James Place ($180) and receives $95 cash.
    The strategic value ratio is approximately 1.89.

    Expected:
    - No SUSPICIOUS_IMBALANCE flag (threshold is >= 3.0)
    - Classification: NO_FLAG
    """
    return loadScenarioInput("trade_ratio/ratio_just_below_two.json")


def ratioExactlyTwoInput() -> dict[str, Any]:
    """9.4: Trade ratio near 2.0.

    Player A gives St. James Place ($180) and receives $90 cash.
    Note: Strategic value may differ from base asset ratio due to
    monopoly potential, blocking value, and other factors.

    Expected:
    - No SUSPICIOUS_IMBALANCE flag (threshold is >= 3.0)
    """
    return loadScenarioInput("trade_ratio/ratio_exactly_two.json")


def ratioJustAboveTwoInput() -> dict[str, Any]:
    """9.5: Trade ratio immediately above 2.0 but below 3.0.

    Player A gives St. James Place ($180) and receives $80 cash.
    Ratio approximately 2.25.

    Expected:
    - No SUSPICIOUS_IMBALANCE flag (threshold is >= 3.0)
    """
    return loadScenarioInput("trade_ratio/ratio_just_above_two.json")


def ratioJustBelowThreeInput() -> dict[str, Any]:
    """9.6: Trade ratio immediately below 3.0.

    Player A gives St. James Place ($180) and receives $62 cash.
    Ratio approximately 2.9.

    Expected:
    - No SUSPICIOUS_IMBALANCE flag (threshold is >= 3.0)
    """
    return loadScenarioInput("trade_ratio/ratio_just_below_three.json")


def ratioExactlyThreeInput() -> dict[str, Any]:
    """9.7: Trade ratio exactly 3.0.

    Player A gives St. James Place ($180) and receives $60 cash.
    Strategic value ratio: 180 / 60 = 3.0.

    Note: When initiator is the overpayer, the initiator adjustment
    may remove or downgrade SUSPICIOUS_IMBALANCE.

    Expected:
    - Ratio = 3.0 (SUSPICIOUS_IMBALANCE threshold)
    """
    return loadScenarioInput("trade_ratio/ratio_exactly_three.json")


def ratioJustAboveThreeInput() -> dict[str, Any]:
    """9.8: Trade ratio immediately above 3.0.

    Player A gives St. James Place ($180) and receives $55 cash.
    Ratio approximately 3.27.

    Expected:
    - SUSPICIOUS_IMBALANCE would be raised (ratio >= 3.0)
    - But may be removed by initiator adjustment when initiator overpays
    """
    return loadScenarioInput("trade_ratio/ratio_just_above_three.json")


def ratioJustBelowFiveInput() -> dict[str, Any]:
    """9.9: Trade ratio immediately below 5.0.

    Player A gives St. James Place ($180) and receives $37 cash.
    Ratio approximately 4.86.

    Expected:
    - SUSPICIOUS_IMBALANCE (if not adjusted)
    - Not HIGHLY_SUSPICIOUS_IMBALANCE (threshold is >= 5.0)
    """
    return loadScenarioInput("trade_ratio/ratio_just_below_five.json")


def ratioExactlyFiveInput() -> dict[str, Any]:
    """9.10: Trade ratio exactly 5.0.

    Player A gives St. James Place ($180) and receives $36 cash.
    Strategic value ratio: 180 / 36 = 5.0.

    Expected:
    - HIGHLY_SUSPICIOUS_IMBALANCE threshold (ratio >= 5.0)
    - When initiator is overpayer, may be downgraded to SUSPICIOUS_IMBALANCE
    """
    return loadScenarioInput("trade_ratio/ratio_exactly_five.json")


def ratioGreaterThanFiveInput() -> dict[str, Any]:
    """9.11: Raw trade ratio greater than 5.0.

    Player A gives St. James Place ($180) and receives $10 cash.
    Raw ratio: 180 / 10 = 18.0.

    Expected:
    - Raw ratio preserved in evidence
    - Published ratio capped at MAX_TRADE_RATIO (5.0)
    - HIGHLY_SUSPICIOUS_IMBALANCE or SUSPICIOUS_IMBALANCE
    """
    return loadScenarioInput("trade_ratio/ratio_greater_than_five.json")


def bothStrategicValuesZeroInput() -> dict[str, Any]:
    """9.12: Both strategic values equal zero.

    Both players exchange $100 cash back and forth.
    Net position change is zero for both.

    Expected:
    - Denominator protection (floor at 1)
    - Finite ratio despite zero values
    """
    return loadScenarioInput("trade_ratio/both_strategic_values_zero.json")


def oneStrategicValueZeroAInput() -> dict[str, Any]:
    """9.13a: One strategic value zero - Player A receives minimal value.

    Player A gives St. James Place ($180) and receives only $1 cash.
    This is essentially a one-sided giveaway.

    Expected:
    - High trade ratio (significant imbalance)
    - HIGHLY_SUSPICIOUS_IMBALANCE or similar flag
    """
    return loadScenarioInput("trade_ratio/one_strategic_value_zero_a.json")


def oneStrategicValueZeroBInput() -> dict[str, Any]:
    """9.13b: One strategic value zero - Player B receives minimal value.

    Player B gives St. James Place ($180) and receives only $1 cash.
    Opposite direction of oneStrategicValueZeroAInput.

    Expected:
    - High trade ratio
    - Significant imbalance flags
    """
    return loadScenarioInput("trade_ratio/one_strategic_value_zero_b.json")


def balancedTradeInput() -> dict[str, Any]:
    """Moderate exchange with comparable strategic value on both sides.

    Players swap Orange group properties with small cash adjustment.
    St. James goes to Player B, Tennessee goes to Player A, plus $100 cash.

    Expected:
    - Classification: NO_FLAG or low imbalance
    - Approximately balanced strategic values
    """
    return loadScenarioInput("trade_ratio/balanced_trade.json")


def slightImbalanceTradeInput() -> dict[str, Any]:
    """One-sided trade that should produce SUSPICIOUS_IMBALANCE.

    Similar to balanced trade but with larger cash difference ($400).

    Expected:
    - SUSPICIOUS_IMBALANCE flag
    - Classification: SOFT_FLAG
    """
    return loadScenarioInput("trade_ratio/slight_imbalance_trade.json")


# ──────────────────────────────────────────────────────────────
# Base Asset Value Scenarios (Section 10)
# ──────────────────────────────────────────────────────────────


def cashOnlyTradeInput() -> dict[str, Any]:
    """10.1: Cash only trade.

    Player A gives $500 cash to Player B with no property exchange.

    Expected:
    - Base asset value equals cash amount
    - Line items show cash transfer
    """
    return loadScenarioInput("base_asset_value/cash_only_trade.json")


def unmortgagedPropertyTransferInput() -> dict[str, Any]:
    """10.2: Unmortgaged property transfer.

    Player A gives unmortgaged St. James Place ($180) for $180 cash.
    Property is valued at full printed price.

    Expected:
    - Property valued at $180 (printed value)
    - No mortgage penalty applied
    """
    return loadScenarioInput("base_asset_value/unmortgaged_property_transfer.json")


def mortgagedPropertyTransferInput() -> dict[str, Any]:
    """10.3: Mortgaged property transfer.

    Player A gives mortgaged St. James Place for $81 cash.
    Mortgage value = $90, unmortgage cost = $90 * 1.1 = $99.
    Adjusted value = $180 - $99 = $81.

    Expected:
    - Mortgage penalty applied (unmortgage cost)
    - Adjusted property value < printed value
    """
    return loadScenarioInput("base_asset_value/mortgaged_property_transfer.json")


def propertyWithHousesTransferInput() -> dict[str, Any]:
    """10.4: Property with houses transfer.

    Player A gives St. James Place with 2 houses.
    Building value = 2 * $100 * 0.5 = $100.
    Total value = $180 + $100 = $280.

    Expected:
    - Building liquidation value included
    - Total value > printed value
    """
    return loadScenarioInput("base_asset_value/property_with_houses_transfer.json")


def propertyWithHotelTransferInput() -> dict[str, Any]:
    """10.5: Property with hotel transfer.

    Player A gives St. James Place with hotel.
    Hotel liquidation = 5 * $100 * 0.5 = $250.
    Total value = $180 + $250 = $430.

    Expected:
    - Hotel liquidation value included
    - Follows hotel_liquidation_basis (houses_plus_hotel)
    """
    return loadScenarioInput("base_asset_value/property_with_hotel_transfer.json")


def railroadTransferInput() -> dict[str, Any]:
    """10.7: Railroad transfer.

    Player A gives Reading Railroad for $200 cash.
    Railroad printed value = $200.

    Expected:
    - Railroad valued at printed price
    """
    return loadScenarioInput("base_asset_value/railroad_transfer.json")


def utilityTransferInput() -> dict[str, Any]:
    """10.8: Utility transfer.

    Player A gives Electric Company for $150 cash.
    Utility printed value = $150.

    Expected:
    - Utility valued at printed price
    """
    return loadScenarioInput("base_asset_value/utility_transfer.json")


# ──────────────────────────────────────────────────────────────
# Development Capability Scenarios (Section 12)
# ──────────────────────────────────────────────────────────────


def cannotBuildAnyHouseInput() -> dict[str, Any]:
    """12.1: Cannot build any house.

    Player A completes Orange monopoly but has only $50 cash.
    Cannot afford even 1 house at $100 each.

    Expected:
    - Buildable = false
    - Development multiplier = 0.40 (cannot_build)
    """
    return loadScenarioInput("development_capability/cannot_build_any_house.json")


def exactlyOneHouseEachInput() -> dict[str, Any]:
    """12.2: Exactly one house per property.

    Player A completes Orange monopoly with $300 cash.
    Can afford 3 houses (one per property).

    Expected:
    - Buildable = true
    - Dangerous = false
    - Development multiplier = 1.00
    """
    return loadScenarioInput("development_capability/exactly_one_house_each.json")


def exactlyThreeHousesEachInput() -> dict[str, Any]:
    """12.4: Exactly three houses per property (Dangerous threshold).

    Player A completes Orange monopoly with $900 cash.
    Can afford 9 houses (three per property).

    Expected:
    - Buildable = true
    - Dangerous = true
    - Development multiplier = 1.50
    - DANGEROUS_MONOPOLY_ENABLED flag
    """
    return loadScenarioInput("development_capability/exactly_three_houses_each.json")


def oneHouseShortOfDangerousInput() -> dict[str, Any]:
    """12.5: One house short of dangerous.

    Player A completes Orange monopoly with $599 cash.
    Can afford 5 houses (not enough for 3-3-3 = dangerous).

    Expected:
    - Buildable = true
    - Dangerous = false (cannot reach 3 houses per property)
    """
    return loadScenarioInput("development_capability/one_house_short_of_dangerous.json")


def insufficientBankHousesInput() -> dict[str, Any]:
    """12.8: Insufficient bank houses.

    Player A completes Orange monopoly with $2000 cash,
    but bank only has 2 houses available.

    Expected:
    - House supply constrains development
    - Cannot build evenly on 3-property group with 2 houses
    """
    return loadScenarioInput("development_capability/insufficient_bank_houses.json")


# ──────────────────────────────────────────────────────────────
# Railroad Value Scenarios (Section 15)
# ──────────────────────────────────────────────────────────────


def zeroRailroadsInput() -> dict[str, Any]:
    """15.1: Zero railroads owned.

    Simple cash trade with no railroad ownership.

    Expected:
    - Railroad value = 0
    """
    return loadScenarioInput("railroad_value/zero_railroads.json")


def oneRailroadInput() -> dict[str, Any]:
    """15.2: One railroad owned (after trade).

    Player A acquires one railroad.

    Expected:
    - Railroad value = $200 (base value for 1 railroad)
    """
    return loadScenarioInput("railroad_value/one_railroad.json")


def twoRailroadsInput() -> dict[str, Any]:
    """15.3: Two railroads owned (after trade).

    Player A has one railroad and acquires another.

    Expected:
    - Railroad value = $500 (base value for 2 railroads)
    """
    return loadScenarioInput("railroad_value/two_railroads.json")


def threeRailroadsInput() -> dict[str, Any]:
    """15.4: Three railroads owned (after trade).

    Player A has two railroads and acquires a third.

    Expected:
    - Railroad value = $900 (base value for 3 railroads)
    """
    return loadScenarioInput("railroad_value/three_railroads.json")


def fourRailroadsInput() -> dict[str, Any]:
    """15.5: Four railroads owned (complete set).

    Player A has three railroads and acquires the fourth.

    Expected:
    - Railroad value = $1800 (base value for 4 railroads)
    - Complete railroad set
    """
    return loadScenarioInput("railroad_value/four_railroads.json")


def lowDevelopmentContextRailroadsInput() -> dict[str, Any]:
    """15.7: Low-development context (0-1 developed monopolies).

    Player A acquires fourth railroad on undeveloped board.

    Expected:
    - Railroad value multiplied by 1.30 (low-dev context)
    """
    return loadScenarioInput("railroad_value/low_development_context.json")


def highDevelopmentContextRailroadsInput() -> dict[str, Any]:
    """15.9: Developed-monopoly context (2+ developed monopolies).

    Player A acquires fourth railroad on board with developed monopolies.

    Expected:
    - Railroad value multiplied by 0.80 (high-dev context)
    """
    return loadScenarioInput("railroad_value/high_development_context.json")


def strategicOverpaymentRailroadInput() -> dict[str, Any]:
    """Strategic overpayment for fourth railroad on blocked board.

    Player A pays $1800 cash for the fourth railroad.

    Expected:
    - High railroad value due to complete set
    - Strategic justification for overpayment
    """
    return loadScenarioInput("railroad_value/strategic_overpayment_railroad.json")


def railroadEngineInput() -> dict[str, Any]:
    """Player A completes the four-railroad engine.

    Player A acquires the last two railroads needed.

    Expected:
    - Complete railroad set ($1800 base value)
    - Context multiplier applied
    """
    return loadScenarioInput("railroad_value/railroad_engine.json")


# ──────────────────────────────────────────────────────────────
# Blocking Value Scenarios (Section 16)
# ──────────────────────────────────────────────────────────────


def strategicBlockingTradeInput() -> dict[str, Any]:
    """Acquire a blocking red property while preserving leverage.

    Player A acquires Illinois Avenue to block the red group.

    Expected:
    - Blocking value calculated
    - Strategic justification for premium
    """
    return loadScenarioInput("blocking_value/strategic_blocking_trade.json")


def futureNegotiationLeverageInput() -> dict[str, Any]:
    """Acquire a green property needed by multiple opponents.

    Player A acquires North Carolina Avenue.

    Expected:
    - Future negotiation bonus calculated
    """
    return loadScenarioInput("blocking_value/future_negotiation_leverage.json")


# ──────────────────────────────────────────────────────────────
# Risk Coverage Scenarios (Section 19)
# ──────────────────────────────────────────────────────────────


def zeroThreatRiskInput() -> dict[str, Any]:
    """19.1: Zero threat (no opponent exposure).

    All properties unowned - no landing exposure.

    Expected:
    - Zero or minimal landing exposure
    - NO_EXPOSURE limitation or very high coverage
    """
    return loadScenarioInput("risk_coverage/zero_threat.json")


def threatGreaterThanResourcesInput() -> dict[str, Any]:
    """19.2: Threat greater than all resources.

    Player A has $100 cash facing opponent's developed Orange monopoly.

    Expected:
    - Negative risk margin (deficit)
    - Positive risk penalty
    - SURVIVAL_RISK_HIGH or SURVIVAL_RISK_CRITICAL
    """
    return loadScenarioInput("risk_coverage/threat_greater_than_resources.json")


def survivalRiskCriticalInput() -> dict[str, Any]:
    """19.3: SURVIVAL_RISK_CRITICAL (penalty >= 900).

    Player A has $100 cash facing opponent's developed Dark Blue monopoly.
    Very low coverage ratio and large deficit.

    Expected:
    - SURVIVAL_RISK_CRITICAL label
    - PLAYER_CANNOT_SURVIVE_ONE_LANDING warning
    """
    return loadScenarioInput("risk_coverage/survival_risk_critical.json")


def survivalRiskVeryLowInput() -> dict[str, Any]:
    """19.5: SURVIVAL_RISK_VERY_LOW (negative penalty = coverage bonus).

    Player A has $5000 cash with no threats on board.
    Strong surplus, high coverage ratio.

    Expected:
    - SURVIVAL_RISK_VERY_LOW label
    - Negative risk penalty (coverage bonus)
    """
    return loadScenarioInput("risk_coverage/survival_risk_very_low.json")


def tradeImprovesRiskInput() -> dict[str, Any]:
    """19.16: Trade improves risk.

    Player A receives significant cash, improving coverage.

    Expected:
    - After penalty < Before penalty
    - Risk improvement shown in delta
    """
    return loadScenarioInput("risk_coverage/trade_improves_risk.json")


def tradeWorsensRiskInput() -> dict[str, Any]:
    """19.17: Trade worsens risk.

    Player A gives away most cash, increasing deficit.

    Expected:
    - After penalty > Before penalty
    - Risk deterioration shown in delta
    """
    return loadScenarioInput("risk_coverage/trade_worsens_risk.json")


def riskCoverageImprovementInput() -> dict[str, Any]:
    """Trade increases initiator cash, improving risk coverage.

    Player A receives $2300 cash against existing exposure.

    Expected:
    - Significant risk improvement
    """
    return loadScenarioInput("risk_coverage/risk_coverage_improvement.json")


def riskCoverageDeteriorationInput() -> dict[str, Any]:
    """Trade drains player cash, worsening risk coverage.

    Player A gives $2800 cash.

    Expected:
    - Significant risk deterioration
    - SUSPICIOUS_IMBALANCE (non-initiator overpays)
    """
    return loadScenarioInput("risk_coverage/risk_coverage_deterioration.json")


# ──────────────────────────────────────────────────────────────
# Automatic Flags Scenarios (Section 20)
# ──────────────────────────────────────────────────────────────


def buildableMonopolyGivenAwayPositiveInput() -> dict[str, Any]:
    """20: BUILDABLE_MONOPOLY_GIVEN_AWAY positive test.

    Player A gives away complete Orange monopoly for $10 cash.
    Player B has enough cash to build.

    Expected:
    - BUILDABLE_MONOPOLY_GIVEN_AWAY flag raised
    """
    return loadScenarioInput("automatic_flags/buildable_monopoly_given_away.json")


def dangerousMonopolyEnabledPositiveInput() -> dict[str, Any]:
    """20: DANGEROUS_MONOPOLY_ENABLED positive test.

    Trade creates Orange monopoly for Player B with $900 cash.
    Player B can reach 3 houses per property (dangerous).

    Expected:
    - DANGEROUS_MONOPOLY_ENABLED flag raised
    - Classification: SOFT_FLAG or higher
    """
    return loadScenarioInput("automatic_flags/dangerous_monopoly_enabled.json")


def symbolicValueTradePositiveInput() -> dict[str, Any]:
    """20: SYMBOLIC_VALUE_TRADE positive test.

    Player A gives complete Orange monopoly for only $1 cash.
    High strategic value exchanged for < 10% compensation.

    Expected:
    - SYMBOLIC_VALUE_TRADE flag raised
    """
    return loadScenarioInput("automatic_flags/symbolic_value_trade.json")


def houseControlEnabledPositiveInput() -> dict[str, Any]:
    """20: HOUSE_CONTROL_ENABLED positive test.

    Trade allows Player A to control 24+ houses.

    Expected:
    - HOUSE_CONTROL_ENABLED flag raised
    """
    return loadScenarioInput("automatic_flags/house_control_enabled.json")


def houseSupplyDenialPositiveInput() -> dict[str, Any]:
    """20: HOUSE_SUPPLY_DENIAL positive test.

    After trade and maximum construction, ≤4 houses remain.
    Bank starts with only 16 houses.

    Expected:
    - HOUSE_SUPPLY_DENIAL flag raised
    """
    return loadScenarioInput("automatic_flags/house_supply_denial.json")


def suspiciousImbalancePositiveInput() -> dict[str, Any]:
    """20: SUSPICIOUS_IMBALANCE positive test (ratio >= 3.0).

    Same as ratioExactlyThreeInput.

    Expected:
    - SUSPICIOUS_IMBALANCE flag (may be adjusted by initiator rule)
    """
    return loadScenarioInput("automatic_flags/suspicious_imbalance.json")


def highlySuspiciousImbalancePositiveInput() -> dict[str, Any]:
    """20: HIGHLY_SUSPICIOUS_IMBALANCE positive test (ratio >= 5.0).

    Same as ratioExactlyFiveInput.

    Expected:
    - HIGHLY_SUSPICIOUS_IMBALANCE flag (may be downgraded by initiator rule)
    """
    return loadScenarioInput("automatic_flags/highly_suspicious_imbalance.json")


def dangerousMonopolyGiveawayInput() -> dict[str, Any]:
    """Buildable/dangerous Orange monopoly enabled for opponent.

    Player A gives complete Orange monopoly to Player B for $100.
    Player B has enough cash to reach dangerous (3 houses each).

    Expected:
    - DANGEROUS_MONOPOLY_ENABLED flag
    - BUILDABLE_MONOPOLY_GIVEN_AWAY flag
    """
    return loadScenarioInput("automatic_flags/dangerous_monopoly_giveaway.json")


def houseSupplyControlInput() -> dict[str, Any]:
    """Cash for monopoly with capacity to control house supply.

    Player A pays $2000 for Orange monopoly completion.
    Can build to control most houses.

    Expected:
    - HOUSE_CONTROL_ENABLED flag possible
    """
    return loadScenarioInput("automatic_flags/house_supply_control.json")


def immediateDevelopmentPreventionInput() -> dict[str, Any]:
    """After trade, initiator can deny house supply to opponents.

    Player A builds 4 houses on each Brown property.

    Expected:
    - HOUSE_SUPPLY_DENIAL flag
    """
    return loadScenarioInput("automatic_flags/immediate_development_prevention.json")


# ──────────────────────────────────────────────────────────────
# Initiator Adjustment Scenarios (Section 21)
# ──────────────────────────────────────────────────────────────


def initiatorIsApparentOverpayerInput() -> dict[str, Any]:
    """21.1: Initiator is apparent overpayer.

    Player A initiates and pays $600 for St. James Place ($180).
    Player A is both initiator and overpayer.

    Expected:
    - Initiator adjustment may remove SUSPICIOUS_IMBALANCE
    """
    return loadScenarioInput(
        "initiator_adjustment/initiator_is_apparent_overpayer.json"
    )


def initiatorIsNotApparentOverpayerInput() -> dict[str, Any]:
    """21.2: Initiator is NOT apparent overpayer.

    Player B initiates but Player A overpays.

    Expected:
    - Initiator adjustment does NOT apply
    - Flags remain if threshold is met
    """
    return loadScenarioInput(
        "initiator_adjustment/initiator_is_not_apparent_overpayer.json"
    )


# ──────────────────────────────────────────────────────────────
# Final Classification Scenarios (Section 22)
# ──────────────────────────────────────────────────────────────


def noFlagClassificationInput() -> dict[str, Any]:
    """22: NO_FLAG classification - balanced trade with no flags.

    Same as perfectlyBalancedPrintedValueSwapInput.

    Expected:
    - Classification: NO_FLAG
    - Empty flags list
    """
    return loadScenarioInput("final_classification/no_flag.json")


def softFlagClassificationInput() -> dict[str, Any]:
    """22: SOFT_FLAG classification - moderate imbalance only.

    Same as ratioExactlyThreeInput.

    Expected:
    - Classification: SOFT_FLAG
    - One or more moderate flags
    """
    return loadScenarioInput("final_classification/soft_flag.json")


def strongFlagClassificationInput() -> dict[str, Any]:
    """22: STRONG_FLAG classification - one strong flag.

    Same as dangerousMonopolyEnabledPositiveInput.

    Expected:
    - Classification: STRONG_FLAG
    - At least one strong flag indicator
    """
    return loadScenarioInput("final_classification/strong_flag.json")


def reviewRecommendedClassificationInput() -> dict[str, Any]:
    """22: REVIEW_RECOMMENDED classification - multiple strong flags.

    Player A gives away dangerous monopoly for $1 cash.
    Multiple strong flag conditions triggered.

    Expected:
    - Classification: REVIEW_RECOMMENDED
    - Multiple strong flags
    """
    return loadScenarioInput("final_classification/review_recommended.json")


# ──────────────────────────────────────────────────────────────
# Invalid Input Scenarios (Section 23)
# ──────────────────────────────────────────────────────────────


def invalidPropertyTransferPositiveAmountInput() -> dict[str, Any]:
    """23.12: Invalid property transfer amount (amount > 0).

    Property transfer with amount = 1 (should be 0).

    Expected:
    - Validation error or degraded execution
    """
    return loadRawScenarioInput("invalid_input/property_positive_amount.json")


def invalidCashTransferZeroAmountInput() -> dict[str, Any]:
    """23.13: Invalid cash transfer amount (amount = 0).

    Cash transfer with amount = 0 (should be > 0).

    Expected:
    - Validation error or degraded execution
    """
    return loadRawScenarioInput("invalid_input/cash_zero_amount.json")


def invalidCashTransferWithAssetIdInput() -> dict[str, Any]:
    """23.14: Invalid cash transfer with non-null asset_id.

    Cash transfer with asset_id = "some_asset" (should be null).

    Expected:
    - Validation error or degraded execution
    """
    return loadRawScenarioInput("invalid_input/cash_with_asset_id.json")


def invalidPropertyTransferMissingAssetIdInput() -> dict[str, Any]:
    """23.14b: Invalid property transfer missing asset_id.

    Property transfer with asset_id = null (should have property ID).

    Expected:
    - Validation error or degraded execution
    """
    return loadRawScenarioInput("invalid_input/property_missing_asset_id.json")


def missingRentInformationInput() -> dict[str, Any]:
    """23.1: Missing rent data.

    Scenario with property missing rent_table data.

    Expected:
    - PARTIAL or UNAVAILABLE status for rent calculations
    """
    return loadRawScenarioInput("invalid_input/missing_rent_information.json")


def multiPartyTradeInput() -> dict[str, Any]:
    """23.9: Unsupported participant count (more than 2 players).

    Trade with 3 participants.

    Expected:
    - ERROR or PARTIAL status (unsupported configuration)
    """
    return loadRawScenarioInput("invalid_input/multi_party_trade.json")


def nonTradablePropertyInput() -> dict[str, Any]:
    """23.8: Non-tradable property transfer.

    Attempting to transfer a property with is_tradable = false.

    Expected:
    - Validation error or degraded execution
    """
    return loadRawScenarioInput("invalid_input/non_tradable_property.json")


# ──────────────────────────────────────────────────────────────
# Additional Automatic Flag Scenarios
# ──────────────────────────────────────────────────────────────


def buildableMonopolyGiveawayInput() -> dict[str, Any]:
    """BUILDABLE_MONOPOLY_GIVEN_AWAY test case.

    Player A gives away last Orange property for $100 cash.
    Player B now has complete Orange monopoly with enough cash to build.

    Expected:
    - BUILDABLE_MONOPOLY_GIVEN_AWAY flag raised
    """
    return loadScenarioInput("automatic_flags/buildable_monopoly_giveaway.json")


def orangeMonopolyTradeInput() -> dict[str, Any]:
    """Orange monopoly completion trade.

    Player B acquires final Orange property to complete monopoly.
    Receives St. James, Tennessee, and New York from Player A.

    Expected:
    - Monopoly value increase for Player B
    - Development capability enabled
    """
    return loadScenarioInput("automatic_flags/orange_monopoly_trade.json")


def strategicRailroadGiveawayInput() -> dict[str, Any]:
    """STRATEGIC_RAILROAD_GIVEAWAY test case.

    Mostly blocked classic board; player A receives fourth railroad for token cash.

    Expected:
    - STRATEGIC_RAILROAD_GIVEAWAY flag raised
    - mostlyBlockedBoard predicate true in evidence
    """
    return loadScenarioInput("automatic_flags/strategic_railroad_giveaway.json")


def symbolicTradeInput() -> dict[str, Any]:
    """SYMBOLIC_VALUE_TRADE test case.

    High-value asset exchanged for token compensation.

    Expected:
    - SYMBOLIC_VALUE_TRADE flag raised
    """
    return loadScenarioInput("automatic_flags/symbolic_trade.json")


def houseSupplyDenialInput() -> dict[str, Any]:
    """HOUSE_SUPPLY_DENIAL test case (pure).

    Trade allows player to build enough houses to exhaust bank supply.

    Expected:
    - HOUSE_SUPPLY_DENIAL flag raised
    """
    return loadScenarioInput("automatic_flags/house_supply_denial_pure.json")


# ──────────────────────────────────────────────────────────────
# Custom Board Scenarios (Section 24)
# ──────────────────────────────────────────────────────────────


def customStreetGroupTradeInput() -> dict[str, Any]:
    """24.1: Valid custom street group trade.

    Non-classic ruleset with custom property groups.

    Expected:
    - Custom board processed correctly
    - Neutral multiplier applied for unknown groups
    """
    return loadScenarioInput("custom_board/custom_street_group.json")


def partialMonopolyRentInput() -> dict[str, Any]:
    """PARTIAL monopoly_value when one completed group lacks rent data.

    Player A owns two completed monopolies after trade:
    - custom_alpha: rent available (contributes to total)
    - custom_beta: empty rent_table (UNAVAILABLE per group)

    Expected:
    - Total monopoly_value after status PARTIAL with partial sum
    - missing_inputs includes rent_table:custom_beta
    """
    return loadScenarioInput("custom_board/partial_monopoly_rent.json")


def survivalRiskModerateInput() -> dict[str, Any]:
    """SURVIVAL_RISK_MODERATE before-trade label.

    Player A cash 1600 vs dark-blue 4-house threat 1700.
    Coverage ratio 0.94 → ratio severity 300 + deficit severity 100 = penalty 400.
    """
    return loadScenarioInput("risk_coverage/survival_risk_moderate.json")


def survivalRiskLowInput() -> dict[str, Any]:
    """SURVIVAL_RISK_LOW before-trade label.

    Player A cash 1800 vs threat 1700 → non-negative margin, zero penalty.
    """
    return loadScenarioInput("risk_coverage/survival_risk_low.json")


def strategicRailroadNoFlagInput() -> dict[str, Any]:
    """Negative control: mostly blocked board but fourth railroad not transferred.

    Expected:
    - STRATEGIC_RAILROAD_GIVEAWAY absent
    """
    return loadScenarioInput("automatic_flags/strategic_railroad_no_flag.json")


def unavailableMonopolyRentInput() -> dict[str, Any]:
    """Custom board with empty rent_table completes a monopoly after trade.

    Player B receives the third purple property and completes the group, but
    rent_table is empty so monopoly rent cannot be resolved.

    Expected output:
    - calculation_type: monopoly_value
    - player: player_b
    - side: after
    - status: UNAVAILABLE
    - missing_inputs: ['rent_table']
    - result: null
    - classification: SOFT_FLAG
    - flags: DANGEROUS_MONOPOLY_ENABLED
    """
    return loadScenarioInput("custom_board/unavailable_monopoly_rent.json")
