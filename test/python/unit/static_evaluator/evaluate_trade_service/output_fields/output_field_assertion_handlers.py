"""Explicit named assertion handlers for every canonical output field.

Each handler verifies semantic meaning of one inventory field key using
scenario-specific expected values from the specification and computed dumps.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .field_assertions import (
    assertConclusionReferencesCalculation,
    assertFieldEquals,
    assertFieldIn,
    assertFieldIsType,
    assertInputReferenceResolves,
    assertNonEmptyString,
    countCalculationsByStatus,
    getCalculation,
)
from .output_field_inventory import (
    CALCULATION_TYPES,
    SIDE_VALUES,
    SOURCE_LABELS,
    STATUS_VALUES,
)

SCENARIO_BALANCED = "balancedTradeInput"
SCENARIO_HOTEL = "propertyWithHotelTransferInput"
SCENARIO_RATIO5 = "ratioGreaterThanFiveInput"
SCENARIO_SURVIVAL = "survivalRiskCriticalInput"
SCENARIO_THREE_HOUSES = "exactlyThreeHousesEachInput"
SCENARIO_FOUR_RR = "fourRailroadsInput"
SCENARIO_CUSTOM_STREET = "customStreetGroupTradeInput"
SCENARIO_UNAVAILABLE = "unavailableMonopolyRentInput"
SCENARIO_PARTIAL = "partialMonopolyRentInput"
SCENARIO_MULTI_PARTY = "multiPartyTradeInput"
SCENARIO_NON_TRADABLE = "nonTradablePropertyInput"
SCENARIO_ZERO_THREAT = "zeroThreatRiskInput"
SCENARIO_MORTGAGED = "mortgagedPropertyTransferInput"
SCENARIO_BLOCKING = "strategicBlockingTradeInput"


def _require_scenario(scenario: str, expected: str) -> None:
    """Require the coverage-selected scenario for this field assertion."""
    assert scenario == expected, f"Scenario {scenario!r} does not match required {expected!r} for this field assertion"


def _first_calc(
    evidence: dict[str, Any],
    calculation_type: str,
    *,
    side: str | None = None,
    player_id: str | None = None,
) -> dict[str, Any]:
    """Return the first matching calculation."""
    return getCalculation(evidence, calculation_type, side=side, player_id=player_id)


def _calcs_with_side(evidence: dict[str, Any], side: str) -> list[dict[str, Any]]:
    """Return all calculations with the given side."""
    return [c for c in evidence["intermediate_calculations"] if c.get("side") == side]


def _calcs_with_status(evidence: dict[str, Any], status: str) -> list[dict[str, Any]]:
    """Return all calculations with the given status."""
    return [c for c in evidence["intermediate_calculations"] if c.get("status") == status]


def _find_development_capability(
    evidence: dict[str, Any],
    predicate: str,
    *,
    side: str = "after",
) -> dict[str, Any]:
    """Find a development_capability calculation by predicate."""
    for calc in evidence["intermediate_calculations"]:
        if calc.get("calculation_type") != "development_capability":
            continue
        if calc.get("side") != side:
            continue
        if calc.get("intermediate_values", {}).get("predicate") == predicate:
            return calc
    raise AssertionError(f"development_capability with predicate={predicate!r} side={side!r} not found")


def _find_dangerous_monopoly(
    evidence: dict[str, Any],
    *,
    side: str = "after",
) -> dict[str, Any]:
    """Find a dangerous_monopoly_availability calculation."""
    return _first_calc(evidence, "dangerous_monopoly_availability", side=side)


def assert_field_algorithm_id(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    assertFieldEquals(
        evidence["algorithm_id"],
        "monopoly_static_algorithm",
        field_path="algorithm_id",
        scenario=scenario,
    )


def assert_field_algorithm_name(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    assertNonEmptyString(evidence["algorithm_name"], field_path="algorithm_name", scenario=scenario)


def assert_field_algorithm_version(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    assertNonEmptyString(evidence["algorithm_version"], field_path="algorithm_version", scenario=scenario)


def assert_field_available_construction_budget_cash(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc = _first_calc(evidence, "available_construction_budget", side="before", player_id="player_a")
    assertFieldEquals(
        calc["intermediate_values"]["cash"],
        2000,
        field_path="available_construction_budget.cash",
        scenario=scenario,
    )
    assertFieldEquals(
        calc["result"],
        2390,
        field_path="available_construction_budget.result",
        scenario=scenario,
    )


def assert_field_available_risk_resources_mortgage_capacity(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_SURVIVAL)
    calc = _first_calc(evidence, "available_risk_resources", side="before", player_id="player_a")
    assertFieldEquals(
        calc["intermediate_values"]["mortgage_capacity"],
        0,
        field_path="available_risk_resources.mortgage_capacity",
        scenario=scenario,
    )
    assertFieldEquals(
        calc["result"],
        100,
        field_path="available_risk_resources.result",
        scenario=scenario,
    )


def assert_field_base_asset_value_building_value(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_HOTEL)
    calc = _first_calc(evidence, "base_asset_value", side="trade", player_id="player_a")
    assertFieldIsType(
        calc["intermediate_values"]["building_value"],
        (int, float),
        field_path="base_asset_value.building_value",
        scenario=scenario,
    )


def assert_field_base_asset_value_card_value(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_HOTEL)
    calc = _first_calc(evidence, "base_asset_value", side="trade", player_id="player_a")
    assertFieldIsType(
        calc["intermediate_values"]["card_value"],
        (int, float),
        field_path="base_asset_value.card_value",
        scenario=scenario,
    )


def assert_field_base_asset_value_cash_received(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_HOTEL)
    calc = _first_calc(evidence, "base_asset_value", side="trade", player_id="player_a")
    assertFieldEquals(
        calc["intermediate_values"]["cash_received"],
        430,
        field_path="base_asset_value.cash_received",
        scenario=scenario,
    )
    assertFieldEquals(calc["result"], 430, field_path="base_asset_value.result", scenario=scenario)


def assert_field_base_asset_value_line_item_building_value(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_HOTEL)
    calc = _first_calc(evidence, "base_asset_value", side="trade", player_id="player_a")
    for item in calc["intermediate_values"]["line_items"]:
        if item.get("type") == "property":
            assertFieldIsType(
                item["building_value"],
                (int, float),
                field_path="base_asset_value.line_item.building_value",
                scenario=scenario,
            )
            return


def assert_field_base_asset_value_line_item_printed_value(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_MORTGAGED)
    calc = _first_calc(evidence, "base_asset_value", side="trade", player_id="player_b")
    prop_items = [i for i in calc["intermediate_values"]["line_items"] if i.get("type") == "property"]
    assertFieldEquals(
        prop_items[0]["printed_value"],
        81,
        field_path="base_asset_value.line_item.printed_value",
        scenario=scenario,
    )


def assert_field_base_asset_value_line_item_property_id(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_MORTGAGED)
    calc = _first_calc(evidence, "base_asset_value", side="trade", player_id="player_b")
    prop_items = [i for i in calc["intermediate_values"]["line_items"] if i.get("type") == "property"]
    assert len(prop_items) == 1
    assertNonEmptyString(
        prop_items[0]["property_id"],
        field_path="base_asset_value.line_item.property_id",
        scenario=scenario,
    )


def assert_field_base_asset_value_line_item_transfer_id(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_HOTEL)
    calc = _first_calc(evidence, "base_asset_value", side="trade", player_id="player_a")
    item = calc["intermediate_values"]["line_items"][0]
    assertNonEmptyString(
        item["transfer_id"],
        field_path="base_asset_value.line_item.transfer_id",
        scenario=scenario,
    )


def assert_field_base_asset_value_line_item_type(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_HOTEL)
    calc = _first_calc(evidence, "base_asset_value", side="trade", player_id="player_a")
    item = calc["intermediate_values"]["line_items"][0]
    assertFieldIn(
        item["type"],
        {"cash", "property", "card"},
        field_path="base_asset_value.line_item.type",
        scenario=scenario,
    )


def assert_field_base_asset_value_line_items(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_HOTEL)
    calc = _first_calc(evidence, "base_asset_value", side="trade", player_id="player_a")
    assertFieldIsType(
        calc["intermediate_values"]["line_items"],
        list,
        field_path="base_asset_value.line_items",
        scenario=scenario,
    )
    assert len(calc["intermediate_values"]["line_items"]) >= 1


def assert_field_base_asset_value_property_value(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_HOTEL)
    calc = _first_calc(evidence, "base_asset_value", side="trade", player_id="player_a")
    assertFieldIsType(
        calc["intermediate_values"]["property_value"],
        (int, float),
        field_path="base_asset_value.property_value",
        scenario=scenario,
    )


def assert_field_blocking_value_per_property(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BLOCKING)
    calc = _first_calc(evidence, "blocking_value", side="after", player_id="player_a")
    per_property = calc["intermediate_values"]["per_property"]
    assertFieldIsType(per_property, list, field_path="blocking_value.per_property", scenario=scenario)
    st_james = next(p for p in per_property if p["blocking_property_id"] == "property_st_james")
    assertFieldEquals(
        st_james["total_blocking_value"],
        1800,
        field_path="blocking_value.per_property",
        scenario=scenario,
    )


def assert_field_classification_apparent_overpayer(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc = _first_calc(evidence, "final_static_classification", side="trade")
    value = calc["intermediate_values"]["apparent_overpayer"]
    assertFieldIsType(value, str, field_path="classification.apparent_overpayer", scenario=scenario)


def assert_field_classification_automatic_rule_flag_generated(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc = _first_calc(evidence, "final_static_classification", side="trade")
    rules = calc["intermediate_values"]["automatic_rules"]
    assert len(rules) >= 1
    rule = rules[0]
    flag = rule["flag_generated"]
    assert flag is None or isinstance(flag, str), (
        f"Scenario {scenario}: classification.automatic_rule.flag_generated must be str or None"
    )


def assert_field_classification_automatic_rule_predicate_result(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc = _first_calc(evidence, "final_static_classification", side="trade")
    rules = calc["intermediate_values"]["automatic_rules"]
    assert len(rules) >= 1
    rule = rules[0]
    assertFieldIsType(
        rule["predicate_result"],
        bool,
        field_path="classification.automatic_rule.predicate_result",
        scenario=scenario,
    )


def assert_field_classification_automatic_rule_rule(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc = _first_calc(evidence, "final_static_classification", side="trade")
    rules = calc["intermediate_values"]["automatic_rules"]
    assert len(rules) >= 1
    rule = rules[0]
    assertFieldIsType(
        rule["rule"],
        str,
        field_path="classification.automatic_rule.rule",
        scenario=scenario,
    )


def assert_field_classification_automatic_rules(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc = _first_calc(evidence, "final_static_classification", side="trade")
    value = calc["intermediate_values"]["automatic_rules"]
    assertFieldIsType(value, list, field_path="classification.automatic_rules", scenario=scenario)


def assert_field_classification_final_classification(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc = _first_calc(evidence, "final_static_classification", side="trade")
    value = calc["intermediate_values"]["final_classification"]
    assertFieldIsType(value, str, field_path="classification.final_classification", scenario=scenario)


def assert_field_classification_flags_after_initiator_adjustment(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc = _first_calc(evidence, "final_static_classification", side="trade")
    value = calc["intermediate_values"]["flags_after_initiator_adjustment"]
    assertFieldIsType(
        value,
        list,
        field_path="classification.flags_after_initiator_adjustment",
        scenario=scenario,
    )


def assert_field_classification_flags_before_initiator_adjustment(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc = _first_calc(evidence, "final_static_classification", side="trade")
    value = calc["intermediate_values"]["flags_before_initiator_adjustment"]
    assertFieldIsType(
        value,
        list,
        field_path="classification.flags_before_initiator_adjustment",
        scenario=scenario,
    )


def assert_field_classification_initiating_player_id(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc = _first_calc(evidence, "final_static_classification", side="trade")
    value = calc["intermediate_values"]["initiating_player_id"]
    assertFieldIsType(value, str, field_path="classification.initiating_player_id", scenario=scenario)


def assert_field_classification_initiator_adjustment_applied(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc = _first_calc(evidence, "final_static_classification", side="trade")
    value = calc["intermediate_values"]["initiator_adjustment_applied"]
    assertFieldIsType(
        value,
        bool,
        field_path="classification.initiator_adjustment_applied",
        scenario=scenario,
    )


def assert_field_classification_initiator_rule_evaluated(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc = _first_calc(evidence, "final_static_classification", side="trade")
    value = calc["intermediate_values"]["initiator_rule_evaluated"]
    assertFieldIsType(
        value,
        bool,
        field_path="classification.initiator_rule_evaluated",
        scenario=scenario,
    )


def assert_field_classification_strong_flag_count(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc = _first_calc(evidence, "final_static_classification", side="trade")
    value = calc["intermediate_values"]["strong_flag_count"]
    assertFieldIsType(
        value,
        (int, float),
        field_path="classification.strong_flag_count",
        scenario=scenario,
    )


def assert_field_classification_strong_flags(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc = _first_calc(evidence, "final_static_classification", side="trade")
    value = calc["intermediate_values"]["strong_flags"]
    assertFieldIsType(value, list, field_path="classification.strong_flags", scenario=scenario)


def assert_field_classification_trade_ratio(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc = _first_calc(evidence, "final_static_classification", side="trade")
    value = calc["intermediate_values"]["trade_ratio"]
    assertFieldIsType(value, (int, float), field_path="classification.trade_ratio", scenario=scenario)


def assert_field_conclusions_classification(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    assertFieldEquals(
        evidence["final_conclusions"]["classification"],
        "NO_FLAG",
        field_path="conclusions.classification",
        scenario=scenario,
    )


def assert_field_conclusions_classification_calculation_id(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc_id = evidence["final_conclusions"]["classification_calculation_id"]
    assertNonEmptyString(
        calc_id,
        field_path="conclusions.classification_calculation_id",
        scenario=scenario,
    )
    assertConclusionReferencesCalculation(evidence, calc_id)


def assert_field_conclusions_flags(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    assertFieldIsType(
        evidence["final_conclusions"]["flags"],
        dict,
        field_path="conclusions.flags",
        scenario=scenario,
    )


def assert_field_conclusions_flags_calculation_id(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc_id = evidence["final_conclusions"]["flags"]["calculation_id"]
    assertNonEmptyString(calc_id, field_path="conclusions.flags.calculation_id", scenario=scenario)
    assertConclusionReferencesCalculation(evidence, calc_id)


def assert_field_conclusions_flags_values(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    flags = evidence["final_conclusions"]["flags"]["values"]
    assertFieldIsType(flags, list, field_path="conclusions.flags.values", scenario=scenario)
    assert len(flags) == 0


def assert_field_conclusions_risk_labels(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_SURVIVAL)
    assertFieldIsType(
        evidence["final_conclusions"]["risk_labels"],
        dict,
        field_path="conclusions.risk_labels",
        scenario=scenario,
    )


def assert_field_conclusions_risk_labels_player_after(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_SURVIVAL)
    labels = evidence["final_conclusions"]["risk_labels"]["player_a"]
    assertFieldEquals(
        labels["after"],
        "SURVIVAL_RISK_CRITICAL",
        field_path="conclusions.risk_labels.player.after",
        scenario=scenario,
    )


def assert_field_conclusions_risk_labels_player_after_calculation_id(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_SURVIVAL)
    calc_id = evidence["final_conclusions"]["risk_labels"]["player_a"]["after_calculation_id"]
    assertNonEmptyString(
        calc_id,
        field_path="conclusions.risk_labels.player.after_calculation_id",
        scenario=scenario,
    )
    assertConclusionReferencesCalculation(evidence, calc_id)


def assert_field_conclusions_risk_labels_player_before(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_SURVIVAL)
    labels = evidence["final_conclusions"]["risk_labels"]["player_a"]
    assertNonEmptyString(
        labels["before"],
        field_path="conclusions.risk_labels.player.before",
        scenario=scenario,
    )


def assert_field_conclusions_risk_labels_player_before_calculation_id(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_SURVIVAL)
    calc_id = evidence["final_conclusions"]["risk_labels"]["player_a"]["before_calculation_id"]
    assertNonEmptyString(
        calc_id,
        field_path="conclusions.risk_labels.player.before_calculation_id",
        scenario=scenario,
    )
    assertConclusionReferencesCalculation(evidence, calc_id)


def assert_field_conclusions_risk_warnings(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_SURVIVAL)
    assertFieldIsType(
        evidence["final_conclusions"]["risk_warnings"],
        dict,
        field_path="conclusions.risk_warnings",
        scenario=scenario,
    )


def assert_field_conclusions_risk_warnings_calculation_ids(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_SURVIVAL)
    calc_ids = evidence["final_conclusions"]["risk_warnings"]["calculation_ids"]
    assertFieldIsType(
        calc_ids,
        list,
        field_path="conclusions.risk_warnings.calculation_ids",
        scenario=scenario,
    )
    assert len(calc_ids) >= 1
    for calc_id in calc_ids:
        assertConclusionReferencesCalculation(evidence, calc_id)


def assert_field_conclusions_risk_warnings_values(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_SURVIVAL)
    warnings = evidence["final_conclusions"]["risk_warnings"]["values"]
    assertFieldEquals(
        warnings,
        ["PLAYER_CANNOT_SURVIVE_ONE_LANDING"],
        field_path="conclusions.risk_warnings.values",
        scenario=scenario,
    )


def assert_field_conclusions_strategic_value(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    assertFieldIsType(
        evidence["final_conclusions"]["strategic_value"],
        dict,
        field_path="conclusions.strategic_value",
        scenario=scenario,
    )


def assert_field_conclusions_strategic_value_player_calculation_id(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    for player_id, entry in evidence["final_conclusions"]["strategic_value"].items():
        calc_id = entry["calculation_id"]
        assertNonEmptyString(
            calc_id,
            field_path="conclusions.strategic_value.player.calculation_id",
            scenario=scenario,
        )
        assertConclusionReferencesCalculation(evidence, calc_id)


def assert_field_conclusions_strategic_value_player_value(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    sv = evidence["final_conclusions"]["strategic_value"]
    assertFieldEquals(
        sv["player_a"]["value"],
        180,
        field_path="conclusions.strategic_value.player.value",
        scenario=scenario,
    )
    assertFieldEquals(
        sv["player_b"]["value"],
        280,
        field_path="conclusions.strategic_value.player.value",
        scenario=scenario,
    )


def assert_field_conclusions_trade_ratio(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    assertFieldIsType(
        evidence["final_conclusions"]["trade_ratio"],
        dict,
        field_path="conclusions.trade_ratio",
        scenario=scenario,
    )


def assert_field_conclusions_trade_ratio_calculation_id(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc_id = evidence["final_conclusions"]["trade_ratio"]["calculation_id"]
    assertNonEmptyString(calc_id, field_path="conclusions.trade_ratio.calculation_id", scenario=scenario)
    assertConclusionReferencesCalculation(evidence, calc_id)


def assert_field_conclusions_trade_ratio_value(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    assertFieldEquals(
        evidence["final_conclusions"]["trade_ratio"]["value"],
        1.56,
        field_path="conclusions.trade_ratio.value",
        scenario=scenario,
    )


def assert_field_coverage_ratio_no_exposure(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_ZERO_THREAT)
    calc = _first_calc(evidence, "coverage_ratio", side="after", player_id="player_a")
    assertFieldEquals(
        calc["intermediate_values"]["no_exposure"],
        True,
        field_path="coverage_ratio.no_exposure",
        scenario=scenario,
    )
    assert calc["result"] is None


def assert_field_dangerous_monopoly_availability_dangerous_predicate(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_THREE_HOUSES)
    calc = _find_dangerous_monopoly(evidence)
    assertFieldIsType(
        calc["intermediate_values"]["dangerous_predicate"],
        bool,
        field_path="dangerous_monopoly_availability.dangerous_predicate",
        scenario=scenario,
    )


def assert_field_development_capability_predicate(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_THREE_HOUSES)
    buildable = _find_development_capability(evidence, "buildable")
    dangerous = _find_development_capability(evidence, "dangerous")
    assertFieldEquals(
        buildable["intermediate_values"]["predicate"],
        "buildable",
        field_path="development_capability.predicate",
        scenario=scenario,
    )
    assertFieldEquals(
        dangerous["intermediate_values"]["predicate"],
        "dangerous",
        field_path="development_capability.predicate",
        scenario=scenario,
    )


def assert_field_final_conclusions(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    assertFieldIsType(
        evidence["final_conclusions"],
        dict,
        field_path="final_conclusions",
        scenario=scenario,
    )


def assert_field_id(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    assertNonEmptyString(evidence["id"], field_path="id", scenario=scenario)


def assert_field_immediate_risk_available_risk_resources(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_SURVIVAL)
    calc = _first_calc(evidence, "immediate_risk", side="after", player_id="player_a")
    value = calc["intermediate_values"]["available_risk_resources"]
    assertFieldIsType(
        value,
        (int, float),
        field_path="immediate_risk.available_risk_resources",
        scenario=scenario,
    )


def assert_field_immediate_risk_bounded_risk_penalty(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_SURVIVAL)
    calc = _first_calc(evidence, "immediate_risk", side="after", player_id="player_a")
    value = calc["intermediate_values"]["bounded_risk_penalty"]
    assertFieldIsType(
        value,
        (int, float),
        field_path="immediate_risk.bounded_risk_penalty",
        scenario=scenario,
    )


def assert_field_immediate_risk_coverage_ratio(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_ZERO_THREAT)
    calc = _first_calc(evidence, "immediate_risk", side="after", player_id="player_a")
    assert calc["intermediate_values"]["coverage_ratio"] is None or calc["intermediate_values"].get("no_exposure")


def assert_field_immediate_risk_coverage_ratio_component(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_SURVIVAL)
    calc = _first_calc(evidence, "immediate_risk", side="after", player_id="player_a")
    value = calc["intermediate_values"]["coverage_ratio_component"]
    assertFieldIsType(
        value,
        (int, float),
        field_path="immediate_risk.coverage_ratio_component",
        scenario=scenario,
    )


def assert_field_immediate_risk_coverage_ratio_tier(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_SURVIVAL)
    calc = _first_calc(evidence, "immediate_risk", side="after", player_id="player_a")
    value = calc["intermediate_values"]["coverage_ratio_tier"]
    assertFieldIsType(value, str, field_path="immediate_risk.coverage_ratio_tier", scenario=scenario)


def assert_field_immediate_risk_largest_threat(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_SURVIVAL)
    calc = _first_calc(evidence, "immediate_risk", side="after", player_id="player_a")
    assertFieldEquals(
        calc["intermediate_values"]["largest_threat"],
        1700,
        field_path="immediate_risk.largest_threat",
        scenario=scenario,
    )


def assert_field_immediate_risk_maximum_risk_penalty(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_SURVIVAL)
    calc = _first_calc(evidence, "immediate_risk", side="after", player_id="player_a")
    value = calc["intermediate_values"]["maximum_risk_penalty"]
    assertFieldIsType(
        value,
        (int, float),
        field_path="immediate_risk.maximum_risk_penalty",
        scenario=scenario,
    )


def assert_field_immediate_risk_minimum_risk_penalty(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_SURVIVAL)
    calc = _first_calc(evidence, "immediate_risk", side="after", player_id="player_a")
    value = calc["intermediate_values"]["minimum_risk_penalty"]
    assertFieldIsType(
        value,
        (int, float),
        field_path="immediate_risk.minimum_risk_penalty",
        scenario=scenario,
    )


def assert_field_immediate_risk_risk_label(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_SURVIVAL)
    calc = _first_calc(evidence, "immediate_risk", side="after", player_id="player_a")
    assertFieldEquals(
        calc["intermediate_values"]["risk_label"],
        "SURVIVAL_RISK_CRITICAL",
        field_path="immediate_risk.risk_label",
        scenario=scenario,
    )


def assert_field_immediate_risk_risk_margin(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_SURVIVAL)
    calc = _first_calc(evidence, "immediate_risk", side="after", player_id="player_a")
    value = calc["intermediate_values"]["risk_margin"]
    assertFieldIsType(value, (int, float), field_path="immediate_risk.risk_margin", scenario=scenario)


def assert_field_immediate_risk_surplus_or_deficit_amount(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_SURVIVAL)
    calc = _first_calc(evidence, "immediate_risk", side="after", player_id="player_a")
    value = calc["intermediate_values"]["surplus_or_deficit_amount"]
    assertFieldIsType(
        value,
        (int, float),
        field_path="immediate_risk.surplus_or_deficit_amount",
        scenario=scenario,
    )


def assert_field_immediate_risk_surplus_or_deficit_component(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_SURVIVAL)
    calc = _first_calc(evidence, "immediate_risk", side="after", player_id="player_a")
    value = calc["intermediate_values"]["surplus_or_deficit_component"]
    assertFieldIsType(
        value,
        (int, float),
        field_path="immediate_risk.surplus_or_deficit_component",
        scenario=scenario,
    )


def assert_field_immediate_risk_surplus_or_deficit_tier(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_SURVIVAL)
    calc = _first_calc(evidence, "immediate_risk", side="after", player_id="player_a")
    value = calc["intermediate_values"]["surplus_or_deficit_tier"]
    assertFieldIsType(
        value,
        str,
        field_path="immediate_risk.surplus_or_deficit_tier",
        scenario=scenario,
    )


def assert_field_immediate_risk_uncapped_risk_penalty(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_SURVIVAL)
    calc = _first_calc(evidence, "immediate_risk", side="after", player_id="player_a")
    value = calc["intermediate_values"]["uncapped_risk_penalty"]
    assertFieldIsType(
        value,
        (int, float),
        field_path="immediate_risk.uncapped_risk_penalty",
        scenario=scenario,
    )


def assert_field_immediate_risk_warnings(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_SURVIVAL)
    calc = _first_calc(evidence, "immediate_risk", side="after", player_id="player_a")
    assertFieldEquals(
        calc["intermediate_values"]["warnings"],
        ["PLAYER_CANNOT_SURVIVE_ONE_LANDING"],
        field_path="immediate_risk.warnings",
        scenario=scenario,
    )


def assert_field_intermediate_calculations(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calcs = evidence["intermediate_calculations"]
    assertFieldIsType(calcs, list, field_path="intermediate_calculations", scenario=scenario)
    assert len(calcs) == 112, f"Scenario {scenario}: expected 112 calculations, got {len(calcs)}"


def assert_field_item_calculation_type(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    for calc in evidence["intermediate_calculations"]:
        assertFieldIn(
            calc["calculation_type"],
            set(CALCULATION_TYPES),
            field_path="item.calculation_type",
            scenario=scenario,
        )


def assert_field_item_dependent_calculation_ids(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    all_ids = {c["id"] for c in evidence["intermediate_calculations"]}
    for calc in evidence["intermediate_calculations"]:
        deps = calc["dependent_calculation_ids"]
        assertFieldIsType(deps, list, field_path="item.dependent_calculation_ids", scenario=scenario)
        for dep_id in deps:
            assert dep_id in all_ids


def assert_field_item_description(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    for calc in evidence["intermediate_calculations"]:
        assertNonEmptyString(calc["description"], field_path="item.description", scenario=scenario)


def assert_field_item_formula(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    formula_calcs = [c for c in evidence["intermediate_calculations"] if "formula" in c]
    assert formula_calcs, f"Scenario {scenario}: expected at least one calculation with formula"
    non_empty = [c for c in formula_calcs if c["formula"]]
    assert non_empty, f"Scenario {scenario}: expected at least one non-empty formula"
    for calc in non_empty:
        assertNonEmptyString(calc["formula"], field_path="item.formula", scenario=scenario)


def assert_field_item_id(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    for calc in evidence["intermediate_calculations"]:
        assertNonEmptyString(calc["id"], field_path="item.id", scenario=scenario)
        assert calc["id"].startswith("calc_")


def assert_field_item_input_references(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    for calc in evidence["intermediate_calculations"]:
        refs = calc["input_references"]
        assertFieldIsType(refs, list, field_path="item.input_references", scenario=scenario)
        for ref in refs:
            if (".properties[" in ref or ".players[" in ref) and not ref.endswith("]"):
                base_ref = ref[: ref.index("]") + 1]
                assertInputReferenceResolves(input_data, base_ref, scenario=scenario)
            elif ".game_state." in ref:
                board_key = "board_state_before" if ref.startswith("board_state_before") else "board_state_after"
                field = ref.split(".game_state.", 1)[1]
                assert field in input_data[board_key]["game_state"], (
                    f"Scenario {scenario}: game_state reference {ref!r} not found"
                )
            elif ref.startswith("trade.transfers["):
                assertInputReferenceResolves(input_data, ref, scenario=scenario)
            elif ref.startswith("trade."):
                field = ref.removeprefix("trade.")
                assert field in input_data["trade"], f"Scenario {scenario}: trade reference {ref!r} not found"
            else:
                assertInputReferenceResolves(input_data, ref, scenario=scenario)


def assert_field_item_input_values(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    for calc in evidence["intermediate_calculations"]:
        assertFieldIsType(
            calc["input_values"],
            dict,
            field_path="item.input_values",
            scenario=scenario,
        )


def assert_field_item_intermediate_values(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    for calc in evidence["intermediate_calculations"]:
        assertFieldIsType(
            calc["intermediate_values"],
            dict,
            field_path="item.intermediate_values",
            scenario=scenario,
        )


def assert_field_item_limitations(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    for calc in evidence["intermediate_calculations"]:
        assertFieldIsType(calc["limitations"], list, field_path="item.limitations", scenario=scenario)


def assert_field_item_metadata(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    meta_calcs = [c for c in evidence["intermediate_calculations"] if "metadata" in c]
    for calc in meta_calcs:
        assertFieldIsType(calc["metadata"], dict, field_path="item.metadata", scenario=scenario)


def assert_field_item_missing_inputs(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    for calc in evidence["intermediate_calculations"]:
        assertFieldIsType(
            calc["missing_inputs"],
            list,
            field_path="item.missing_inputs",
            scenario=scenario,
        )


def assert_field_item_procedure(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    proc_calcs = [c for c in evidence["intermediate_calculations"] if "procedure" in c]
    assert proc_calcs, f"Scenario {scenario}: expected at least one calculation with procedure"
    non_empty = [c for c in proc_calcs if c["procedure"]]
    assert non_empty, f"Scenario {scenario}: expected at least one non-empty procedure"
    for calc in non_empty:
        assertNonEmptyString(calc["procedure"], field_path="item.procedure", scenario=scenario)


def assert_field_item_result(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_HOTEL)
    calc = _first_calc(evidence, "base_asset_value", side="trade", player_id="player_a")
    assertFieldEquals(calc["result"], 430, field_path="item.result", scenario=scenario)


def assert_field_item_side(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    for calc in evidence["intermediate_calculations"]:
        assertFieldIn(
            calc["side"],
            set(SIDE_VALUES),
            field_path="item.side",
            scenario=scenario,
        )


def assert_field_item_side_after(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    after = _calcs_with_side(evidence, "after")
    assert len(after) > 0


def assert_field_item_side_before(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    before = _calcs_with_side(evidence, "before")
    assert len(before) > 0


def assert_field_item_side_delta(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    delta = _calcs_with_side(evidence, "delta")
    assert len(delta) > 0


def assert_field_item_side_trade(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    trade = _calcs_with_side(evidence, "trade")
    assert len(trade) > 0


def assert_field_item_sources(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    for calc in evidence["intermediate_calculations"]:
        sources = calc.get("sources")
        if sources is not None:
            assertFieldIsType(sources, dict, field_path="item.sources", scenario=scenario)


def assert_field_item_status(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    for calc in evidence["intermediate_calculations"]:
        assertFieldIn(
            calc["status"],
            set(STATUS_VALUES),
            field_path="item.status",
            scenario=scenario,
        )


def assert_field_item_status_COMPLETE(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    complete = _calcs_with_status(evidence, "COMPLETE")
    assert len(complete) > 0, f"Scenario {scenario}: expected COMPLETE calculations"
    counts = countCalculationsByStatus(evidence)
    assert counts.get("COMPLETE", 0) == 112


def assert_field_item_status_ERROR(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_MULTI_PARTY)
    error_calcs = _calcs_with_status(evidence, "ERROR")
    assert len(error_calcs) >= 1
    fsc = _first_calc(evidence, "final_static_classification")
    assertFieldEquals(fsc["status"], "ERROR", field_path="item.status.ERROR", scenario=scenario)


def assert_field_item_status_UNAVAILABLE(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_UNAVAILABLE)
    unavail = [
        c
        for c in evidence["intermediate_calculations"]
        if c["calculation_type"] == "monopoly_value" and c["status"] == "UNAVAILABLE"
    ]
    assert len(unavail) >= 1, f"Scenario {scenario}: expected UNAVAILABLE monopoly_value calculations"
    totals = [c for c in unavail if "Total monopoly value" in c.get("description", "") and c.get("side") == "after"]
    assert len(totals) == 1, f"Scenario {scenario}: expected one after-side total monopoly_value UNAVAILABLE"
    total = totals[0]
    assertFieldEquals(
        total["result"],
        None,
        field_path="item.status.UNAVAILABLE.result",
        scenario=scenario,
    )
    assertFieldEquals(
        total["missing_inputs"],
        ["rent_table"],
        field_path="item.status.UNAVAILABLE",
        scenario=scenario,
    )


def assert_field_item_status_PARTIAL(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_PARTIAL)
    partial_totals = [
        c
        for c in evidence["intermediate_calculations"]
        if c["calculation_type"] == "monopoly_value"
        and c["status"] == "PARTIAL"
        and "Total monopoly value" in c.get("description", "")
        and c.get("side") == "after"
        and "player_a" in c.get("description", "")
    ]
    assert len(partial_totals) == 1, f"Scenario {scenario}: expected one PARTIAL total monopoly_value for player_a"
    total = partial_totals[0]
    assertFieldEquals(
        total["result"],
        800,
        field_path="item.status.PARTIAL.result",
        scenario=scenario,
    )
    assert "rent_table:custom_beta" in total["missing_inputs"], (
        f"Scenario {scenario}: expected rent_table:custom_beta in missing_inputs"
    )
    assert total.get("limitations"), f"Scenario {scenario}: PARTIAL total must publish limitations"


def assert_field_item_subject(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    for calc in evidence["intermediate_calculations"]:
        assertFieldIsType(calc["subject"], dict, field_path="item.subject", scenario=scenario)


def assert_field_item_unit(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    for calc in evidence["intermediate_calculations"]:
        if "unit" in calc:
            assertNonEmptyString(calc["unit"], field_path="item.unit", scenario=scenario)


def assert_field_landing_exposure_threat_property_id(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_SURVIVAL)
    calc = _first_calc(evidence, "landing_exposure", side="before", player_id="player_a")
    assertFieldEquals(
        calc["intermediate_values"]["threat_property_id"],
        "property_park_place",
        field_path="landing_exposure.threat_property_id",
        scenario=scenario,
    )
    assertFieldEquals(calc["result"], 1700, field_path="landing_exposure.result", scenario=scenario)


def assert_field_largest_threat_landing_exposure(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_SURVIVAL)
    calc = _first_calc(evidence, "largest_threat", side="before", player_id="player_a")
    assertFieldEquals(
        calc["intermediate_values"]["landing_exposure"],
        1700,
        field_path="largest_threat.landing_exposure",
        scenario=scenario,
    )
    assertFieldEquals(calc["result"], 1700, field_path="largest_threat.result", scenario=scenario)


def assert_field_metadata(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    metadata = evidence["metadata"]
    assertFieldIsType(metadata, dict, field_path="metadata", scenario=scenario)
    assertFieldIsType(
        metadata["implementation_overrides"],
        list,
        field_path="metadata.implementation_overrides",
        scenario=scenario,
    )
    assertFieldIsType(
        metadata["specification_dependencies"],
        list,
        field_path="metadata.specification_dependencies",
        scenario=scenario,
    )


def assert_field_metadata_implementation_overrides(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    assertFieldIsType(
        evidence["metadata"]["implementation_overrides"],
        list,
        field_path="metadata.implementation_overrides",
        scenario=scenario,
    )


def assert_field_metadata_specification_dependencies(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    deps = evidence["metadata"]["specification_dependencies"]
    assertFieldIsType(deps, list, field_path="metadata.specification_dependencies", scenario=scenario)
    assert len(deps) >= 1


def assert_field_metadata_specification_dependencies_specification_id(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    dep = evidence["metadata"]["specification_dependencies"][0]
    assertNonEmptyString(
        dep["specification_id"],
        field_path="metadata.specification_dependencies.specification_id",
        scenario=scenario,
    )


def assert_field_metadata_specification_dependencies_specification_version(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    dep = evidence["metadata"]["specification_dependencies"][0]
    assertNonEmptyString(
        dep["specification_version"],
        field_path="metadata.specification_dependencies.specification_version",
        scenario=scenario,
    )


def assert_field_monopoly_value_completed_groups(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc = _first_calc(evidence, "monopoly_value", side="after", player_id="player_b")
    assertFieldIsType(
        calc["intermediate_values"]["completed_groups"],
        list,
        field_path="monopoly_value.completed_groups",
        scenario=scenario,
    )


def assert_field_monopoly_value_per_group_values(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc = _first_calc(evidence, "monopoly_value", side="after", player_id="player_b")
    assertFieldIsType(
        calc["intermediate_values"]["per_group_values"],
        list,
        field_path="monopoly_value.per_group_values",
        scenario=scenario,
    )


def assert_field_monopoly_value_total_monopoly_value(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc = _first_calc(evidence, "monopoly_value", side="after", player_id="player_b")
    assertFieldIsType(
        calc["intermediate_values"]["total_monopoly_value"],
        (int, float),
        field_path="monopoly_value.total_monopoly_value",
        scenario=scenario,
    )


def assert_field_mortgage_capacity_result(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc = _first_calc(evidence, "mortgage_capacity", side="before", player_id="player_a")
    assertFieldEquals(calc["result"], 390, field_path="mortgage_capacity.result", scenario=scenario)


def assert_field_purpose(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    assertNonEmptyString(evidence["purpose"], field_path="purpose", scenario=scenario)


def assert_field_railroad_value_context_multiplier(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_FOUR_RR)
    calc = _first_calc(evidence, "railroad_value", side="after", player_id="player_a")
    assertFieldEquals(
        calc["intermediate_values"]["context_multiplier"],
        1.3,
        field_path="railroad_value.context_multiplier",
        scenario=scenario,
    )
    assertFieldEquals(
        calc["intermediate_values"]["base_value"],
        1800,
        field_path="railroad_value.base_value",
        scenario=scenario,
    )
    assertFieldEquals(calc["result"], 2340, field_path="railroad_value.result", scenario=scenario)
    assert calc["result"] == 1800 * 1.3


def assert_field_railroad_value_railroad_count(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_FOUR_RR)
    calc = _first_calc(evidence, "railroad_value", side="after", player_id="player_a")
    assertFieldEquals(
        calc["intermediate_values"]["railroad_count"],
        4,
        field_path="railroad_value.railroad_count",
        scenario=scenario,
    )
    assertFieldEquals(calc["result"], 2340, field_path="railroad_value.result", scenario=scenario)


def assert_field_repair_exposure_repair_card_scenario(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_SURVIVAL)
    calc = _first_calc(evidence, "repair_exposure", side="before", player_id="player_a")
    assertFieldEquals(
        calc["intermediate_values"]["repair_card_scenario"],
        "Both Cards",
        field_path="repair_exposure.repair_card_scenario",
        scenario=scenario,
    )
    assertFieldEquals(calc["result"], 0, field_path="repair_exposure.result", scenario=scenario)


def assert_field_risk_margin_surplus_amount(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_SURVIVAL)
    calc = _first_calc(evidence, "risk_margin", side="before", player_id="player_a")
    assertFieldEquals(
        calc["intermediate_values"]["surplus_amount"],
        0,
        field_path="risk_margin.surplus_amount",
        scenario=scenario,
    )
    assertFieldEquals(
        calc["intermediate_values"]["deficit_amount"],
        1600,
        field_path="risk_margin.deficit_amount",
        scenario=scenario,
    )
    assertFieldEquals(calc["result"], -1600, field_path="risk_margin.result", scenario=scenario)


def assert_field_sources(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_CUSTOM_STREET)
    found_labels: set[str] = set()
    for calc in evidence["intermediate_calculations"]:
        found_labels.update((calc.get("sources") or {}).values())
    assert "BOARD_STATE_RENT_TABLE" in found_labels
    assert "NEUTRAL_CUSTOM_GROUP_DEFAULT" in found_labels
    for label in found_labels:
        assert label in SOURCE_LABELS or label == "UNAVAILABLE"


def assert_field_statistics(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    assertFieldIsType(evidence["statistics"], dict, field_path="statistics", scenario=scenario)


def assert_field_statistics_calculation_count(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    assertFieldEquals(
        evidence["statistics"]["calculation_count"],
        112,
        field_path="statistics.calculation_count",
        scenario=scenario,
    )


def assert_field_strategic_opportunity_score_criteria(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BLOCKING)
    calc = _first_calc(evidence, "strategic_opportunity_score", side="after", player_id="player_a")
    criteria = calc["intermediate_values"]["criteria"]
    assertFieldIsType(
        criteria,
        dict,
        field_path="strategic_opportunity_score.criteria",
        scenario=scenario,
    )
    assertFieldEquals(
        criteria["negotiation_leverage"],
        True,
        field_path="strategic_opportunity_score.criteria",
        scenario=scenario,
    )


def assert_field_strategic_value_base_asset_value(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc = _first_calc(evidence, "strategic_value", side="trade", player_id="player_a")
    value = calc["intermediate_values"]["base_asset_value"]
    assertFieldIsType(
        value,
        (int, float),
        field_path="strategic_value.base_asset_value",
        scenario=scenario,
    )


def assert_field_strategic_value_blocking_value(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc = _first_calc(evidence, "strategic_value", side="trade", player_id="player_a")
    value = calc["intermediate_values"]["blocking_value"]
    assertFieldIsType(
        value,
        (int, float),
        field_path="strategic_value.blocking_value",
        scenario=scenario,
    )


def assert_field_strategic_value_floor_applied(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc = _first_calc(evidence, "strategic_value", side="trade", player_id="player_a")
    value = calc["intermediate_values"]["floor_applied"]
    assertFieldIsType(value, bool, field_path="strategic_value.floor_applied", scenario=scenario)


def assert_field_strategic_value_house_control_bonus(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc = _first_calc(evidence, "strategic_value", side="trade", player_id="player_a")
    value = calc["intermediate_values"]["house_control_bonus"]
    assertFieldIsType(
        value,
        (int, float),
        field_path="strategic_value.house_control_bonus",
        scenario=scenario,
    )


def assert_field_strategic_value_house_denial_bonus(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc = _first_calc(evidence, "strategic_value", side="trade", player_id="player_a")
    value = calc["intermediate_values"]["house_denial_bonus"]
    assertFieldIsType(
        value,
        (int, float),
        field_path="strategic_value.house_denial_bonus",
        scenario=scenario,
    )


def assert_field_strategic_value_immediate_risk_change(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc = _first_calc(evidence, "strategic_value", side="trade", player_id="player_a")
    value = calc["intermediate_values"]["immediate_risk_change"]
    assertFieldIsType(
        value,
        (int, float),
        field_path="strategic_value.immediate_risk_change",
        scenario=scenario,
    )


def assert_field_strategic_value_monopoly_value(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc = _first_calc(evidence, "strategic_value", side="trade", player_id="player_a")
    value = calc["intermediate_values"]["monopoly_value"]
    assertFieldIsType(
        value,
        (int, float),
        field_path="strategic_value.monopoly_value",
        scenario=scenario,
    )


def assert_field_strategic_value_railroad_value(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc = _first_calc(evidence, "strategic_value", side="trade", player_id="player_a")
    value = calc["intermediate_values"]["railroad_value"]
    assertFieldIsType(
        value,
        (int, float),
        field_path="strategic_value.railroad_value",
        scenario=scenario,
    )


def assert_field_strategic_value_strategic_opportunity_value(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc = _first_calc(evidence, "strategic_value", side="trade", player_id="player_a")
    value = calc["intermediate_values"]["strategic_opportunity_value"]
    assertFieldIsType(
        value,
        (int, float),
        field_path="strategic_value.strategic_opportunity_value",
        scenario=scenario,
    )


def assert_field_subject_group_ids(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    for calc in evidence["intermediate_calculations"]:
        assertFieldIsType(
            calc["subject"]["group_ids"],
            list,
            field_path="subject.group_ids",
            scenario=scenario,
        )


def assert_field_subject_player_ids(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    for calc in evidence["intermediate_calculations"]:
        assertFieldIsType(
            calc["subject"]["player_ids"],
            list,
            field_path="subject.player_ids",
            scenario=scenario,
        )


def assert_field_subject_property_ids(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    for calc in evidence["intermediate_calculations"]:
        assertFieldIsType(
            calc["subject"]["property_ids"],
            list,
            field_path="subject.property_ids",
            scenario=scenario,
        )


def assert_field_subject_trade_id(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    trade_calcs = _calcs_with_side(evidence, "trade")
    trade_ids = [c["subject"]["trade_id"] for c in trade_calcs if c["subject"].get("trade_id")]
    assert trade_ids, f"Scenario {scenario}: expected at least one trade calculation with trade_id"
    for trade_id in trade_ids:
        assertNonEmptyString(trade_id, field_path="subject.trade_id", scenario=scenario)


def assert_field_subject_transfer_ids(evidence: dict[str, Any], input_data: dict[str, Any], scenario: str) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    for calc in evidence["intermediate_calculations"]:
        assertFieldIsType(
            calc["subject"]["transfer_ids"],
            list,
            field_path="subject.transfer_ids",
            scenario=scenario,
        )


def assert_field_trade_ratio_division_denominator(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc = _first_calc(evidence, "trade_ratio", side="trade")
    assertFieldEquals(
        calc["intermediate_values"]["division_denominator"],
        180,
        field_path="trade_ratio.division_denominator",
        scenario=scenario,
    )


def assert_field_trade_ratio_highest_strategic_value(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc = _first_calc(evidence, "trade_ratio", side="trade")
    assertFieldEquals(
        calc["intermediate_values"]["highest_strategic_value"],
        280,
        field_path="trade_ratio.highest_strategic_value",
        scenario=scenario,
    )


def assert_field_trade_ratio_lowest_strategic_value(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc = _first_calc(evidence, "trade_ratio", side="trade")
    assertFieldEquals(
        calc["intermediate_values"]["lowest_strategic_value"],
        180,
        field_path="trade_ratio.lowest_strategic_value",
        scenario=scenario,
    )


def assert_field_trade_ratio_maximum_trade_ratio(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_BALANCED)
    calc = _first_calc(evidence, "trade_ratio", side="trade")
    assertFieldEquals(
        calc["intermediate_values"]["maximum_trade_ratio"],
        5.0,
        field_path="trade_ratio.maximum_trade_ratio",
        scenario=scenario,
    )


def assert_field_trade_ratio_published_trade_ratio(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_RATIO5)
    calc = _first_calc(evidence, "trade_ratio", side="trade")
    assertFieldEquals(
        calc["intermediate_values"]["published_trade_ratio"],
        5.0,
        field_path="trade_ratio.published_trade_ratio",
        scenario=scenario,
    )


def assert_field_trade_ratio_raw_trade_ratio(
    evidence: dict[str, Any], input_data: dict[str, Any], scenario: str
) -> None:
    _require_scenario(scenario, SCENARIO_RATIO5)
    calc = _first_calc(evidence, "trade_ratio", side="trade")
    assertFieldEquals(
        calc["intermediate_values"]["raw_trade_ratio"],
        18.0,
        field_path="trade_ratio.raw_trade_ratio",
        scenario=scenario,
    )


FIELD_ASSERTION_HANDLERS: dict[str, Callable[[dict, dict, str], None]] = {
    "algorithm_id": assert_field_algorithm_id,
    "algorithm_name": assert_field_algorithm_name,
    "algorithm_version": assert_field_algorithm_version,
    "available_construction_budget.cash": assert_field_available_construction_budget_cash,
    "available_risk_resources.mortgage_capacity": assert_field_available_risk_resources_mortgage_capacity,
    "base_asset_value.building_value": assert_field_base_asset_value_building_value,
    "base_asset_value.card_value": assert_field_base_asset_value_card_value,
    "base_asset_value.cash_received": assert_field_base_asset_value_cash_received,
    "base_asset_value.line_item.building_value": assert_field_base_asset_value_line_item_building_value,
    "base_asset_value.line_item.printed_value": assert_field_base_asset_value_line_item_printed_value,
    "base_asset_value.line_item.property_id": assert_field_base_asset_value_line_item_property_id,
    "base_asset_value.line_item.transfer_id": assert_field_base_asset_value_line_item_transfer_id,
    "base_asset_value.line_item.type": assert_field_base_asset_value_line_item_type,
    "base_asset_value.line_items": assert_field_base_asset_value_line_items,
    "base_asset_value.property_value": assert_field_base_asset_value_property_value,
    "blocking_value.per_property": assert_field_blocking_value_per_property,
    "classification.apparent_overpayer": assert_field_classification_apparent_overpayer,
    "classification.automatic_rule.flag_generated": assert_field_classification_automatic_rule_flag_generated,
    "classification.automatic_rule.predicate_result": assert_field_classification_automatic_rule_predicate_result,
    "classification.automatic_rule.rule": assert_field_classification_automatic_rule_rule,
    "classification.automatic_rules": assert_field_classification_automatic_rules,
    "classification.final_classification": assert_field_classification_final_classification,
    "classification.flags_after_initiator_adjustment": assert_field_classification_flags_after_initiator_adjustment,
    "classification.flags_before_initiator_adjustment": assert_field_classification_flags_before_initiator_adjustment,
    "classification.initiating_player_id": assert_field_classification_initiating_player_id,
    "classification.initiator_adjustment_applied": assert_field_classification_initiator_adjustment_applied,
    "classification.initiator_rule_evaluated": assert_field_classification_initiator_rule_evaluated,
    "classification.strong_flag_count": assert_field_classification_strong_flag_count,
    "classification.strong_flags": assert_field_classification_strong_flags,
    "classification.trade_ratio": assert_field_classification_trade_ratio,
    "conclusions.classification": assert_field_conclusions_classification,
    "conclusions.classification_calculation_id": assert_field_conclusions_classification_calculation_id,
    "conclusions.flags": assert_field_conclusions_flags,
    "conclusions.flags.calculation_id": assert_field_conclusions_flags_calculation_id,
    "conclusions.flags.values": assert_field_conclusions_flags_values,
    "conclusions.risk_labels": assert_field_conclusions_risk_labels,
    "conclusions.risk_labels.player.after": assert_field_conclusions_risk_labels_player_after,
    "conclusions.risk_labels.player.after_calculation_id": assert_field_conclusions_risk_labels_player_after_calculation_id,
    "conclusions.risk_labels.player.before": assert_field_conclusions_risk_labels_player_before,
    "conclusions.risk_labels.player.before_calculation_id": assert_field_conclusions_risk_labels_player_before_calculation_id,
    "conclusions.risk_warnings": assert_field_conclusions_risk_warnings,
    "conclusions.risk_warnings.calculation_ids": assert_field_conclusions_risk_warnings_calculation_ids,
    "conclusions.risk_warnings.values": assert_field_conclusions_risk_warnings_values,
    "conclusions.strategic_value": assert_field_conclusions_strategic_value,
    "conclusions.strategic_value.player.calculation_id": assert_field_conclusions_strategic_value_player_calculation_id,
    "conclusions.strategic_value.player.value": assert_field_conclusions_strategic_value_player_value,
    "conclusions.trade_ratio": assert_field_conclusions_trade_ratio,
    "conclusions.trade_ratio.calculation_id": assert_field_conclusions_trade_ratio_calculation_id,
    "conclusions.trade_ratio.value": assert_field_conclusions_trade_ratio_value,
    "coverage_ratio.no_exposure": assert_field_coverage_ratio_no_exposure,
    "dangerous_monopoly_availability.dangerous_predicate": assert_field_dangerous_monopoly_availability_dangerous_predicate,
    "development_capability.predicate": assert_field_development_capability_predicate,
    "final_conclusions": assert_field_final_conclusions,
    "id": assert_field_id,
    "immediate_risk.available_risk_resources": assert_field_immediate_risk_available_risk_resources,
    "immediate_risk.bounded_risk_penalty": assert_field_immediate_risk_bounded_risk_penalty,
    "immediate_risk.coverage_ratio": assert_field_immediate_risk_coverage_ratio,
    "immediate_risk.coverage_ratio_component": assert_field_immediate_risk_coverage_ratio_component,
    "immediate_risk.coverage_ratio_tier": assert_field_immediate_risk_coverage_ratio_tier,
    "immediate_risk.largest_threat": assert_field_immediate_risk_largest_threat,
    "immediate_risk.maximum_risk_penalty": assert_field_immediate_risk_maximum_risk_penalty,
    "immediate_risk.minimum_risk_penalty": assert_field_immediate_risk_minimum_risk_penalty,
    "immediate_risk.risk_label": assert_field_immediate_risk_risk_label,
    "immediate_risk.risk_margin": assert_field_immediate_risk_risk_margin,
    "immediate_risk.surplus_or_deficit_amount": assert_field_immediate_risk_surplus_or_deficit_amount,
    "immediate_risk.surplus_or_deficit_component": assert_field_immediate_risk_surplus_or_deficit_component,
    "immediate_risk.surplus_or_deficit_tier": assert_field_immediate_risk_surplus_or_deficit_tier,
    "immediate_risk.uncapped_risk_penalty": assert_field_immediate_risk_uncapped_risk_penalty,
    "immediate_risk.warnings": assert_field_immediate_risk_warnings,
    "intermediate_calculations": assert_field_intermediate_calculations,
    "item.calculation_type": assert_field_item_calculation_type,
    "item.dependent_calculation_ids": assert_field_item_dependent_calculation_ids,
    "item.description": assert_field_item_description,
    "item.formula": assert_field_item_formula,
    "item.id": assert_field_item_id,
    "item.input_references": assert_field_item_input_references,
    "item.input_values": assert_field_item_input_values,
    "item.intermediate_values": assert_field_item_intermediate_values,
    "item.limitations": assert_field_item_limitations,
    "item.metadata": assert_field_item_metadata,
    "item.missing_inputs": assert_field_item_missing_inputs,
    "item.procedure": assert_field_item_procedure,
    "item.result": assert_field_item_result,
    "item.side": assert_field_item_side,
    "item.side.after": assert_field_item_side_after,
    "item.side.before": assert_field_item_side_before,
    "item.side.delta": assert_field_item_side_delta,
    "item.side.trade": assert_field_item_side_trade,
    "item.sources": assert_field_item_sources,
    "item.status": assert_field_item_status,
    "item.status.COMPLETE": assert_field_item_status_COMPLETE,
    "item.status.ERROR": assert_field_item_status_ERROR,
    "item.status.UNAVAILABLE": assert_field_item_status_UNAVAILABLE,
    "item.status.PARTIAL": assert_field_item_status_PARTIAL,
    "item.subject": assert_field_item_subject,
    "item.unit": assert_field_item_unit,
    "landing_exposure.threat_property_id": assert_field_landing_exposure_threat_property_id,
    "largest_threat.landing_exposure": assert_field_largest_threat_landing_exposure,
    "metadata": assert_field_metadata,
    "metadata.implementation_overrides": assert_field_metadata_implementation_overrides,
    "metadata.specification_dependencies": assert_field_metadata_specification_dependencies,
    "metadata.specification_dependencies.specification_id": assert_field_metadata_specification_dependencies_specification_id,
    "metadata.specification_dependencies.specification_version": assert_field_metadata_specification_dependencies_specification_version,
    "monopoly_value.completed_groups": assert_field_monopoly_value_completed_groups,
    "monopoly_value.per_group_values": assert_field_monopoly_value_per_group_values,
    "monopoly_value.total_monopoly_value": assert_field_monopoly_value_total_monopoly_value,
    "mortgage_capacity.result": assert_field_mortgage_capacity_result,
    "purpose": assert_field_purpose,
    "railroad_value.context_multiplier": assert_field_railroad_value_context_multiplier,
    "railroad_value.railroad_count": assert_field_railroad_value_railroad_count,
    "repair_exposure.repair_card_scenario": assert_field_repair_exposure_repair_card_scenario,
    "risk_margin.surplus_amount": assert_field_risk_margin_surplus_amount,
    "sources": assert_field_sources,
    "statistics": assert_field_statistics,
    "statistics.calculation_count": assert_field_statistics_calculation_count,
    "strategic_opportunity_score.criteria": assert_field_strategic_opportunity_score_criteria,
    "strategic_value.base_asset_value": assert_field_strategic_value_base_asset_value,
    "strategic_value.blocking_value": assert_field_strategic_value_blocking_value,
    "strategic_value.floor_applied": assert_field_strategic_value_floor_applied,
    "strategic_value.house_control_bonus": assert_field_strategic_value_house_control_bonus,
    "strategic_value.house_denial_bonus": assert_field_strategic_value_house_denial_bonus,
    "strategic_value.immediate_risk_change": assert_field_strategic_value_immediate_risk_change,
    "strategic_value.monopoly_value": assert_field_strategic_value_monopoly_value,
    "strategic_value.railroad_value": assert_field_strategic_value_railroad_value,
    "strategic_value.strategic_opportunity_value": assert_field_strategic_value_strategic_opportunity_value,
    "subject.group_ids": assert_field_subject_group_ids,
    "subject.player_ids": assert_field_subject_player_ids,
    "subject.property_ids": assert_field_subject_property_ids,
    "subject.trade_id": assert_field_subject_trade_id,
    "subject.transfer_ids": assert_field_subject_transfer_ids,
    "trade_ratio.division_denominator": assert_field_trade_ratio_division_denominator,
    "trade_ratio.highest_strategic_value": assert_field_trade_ratio_highest_strategic_value,
    "trade_ratio.lowest_strategic_value": assert_field_trade_ratio_lowest_strategic_value,
    "trade_ratio.maximum_trade_ratio": assert_field_trade_ratio_maximum_trade_ratio,
    "trade_ratio.published_trade_ratio": assert_field_trade_ratio_published_trade_ratio,
    "trade_ratio.raw_trade_ratio": assert_field_trade_ratio_raw_trade_ratio,
}
