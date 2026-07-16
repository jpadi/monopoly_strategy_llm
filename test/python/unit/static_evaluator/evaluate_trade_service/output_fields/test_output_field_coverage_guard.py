"""Guard tests for canonical output-field coverage completeness."""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from .output_field_assertion_handlers import FIELD_ASSERTION_HANDLERS
from .output_field_coverage import OUTPUT_FIELD_COVERAGE, get_coverage_by_field
from .output_field_inventory import get_all_fields


def test_every_inventory_field_has_coverage_entry() -> None:
    """Every canonical inventory field must appear in the coverage registry."""
    inventory_keys = set(get_all_fields().keys())
    coverage_keys = {entry.field_key for entry in OUTPUT_FIELD_COVERAGE}
    missing = sorted(inventory_keys - coverage_keys)
    assert not missing, f"Inventory fields missing coverage entries: {missing}"


def test_every_coverage_entry_has_inventory_field() -> None:
    """Coverage registry must not reference stale or unknown field keys."""
    inventory_keys = set(get_all_fields().keys())
    coverage_keys = {entry.field_key for entry in OUTPUT_FIELD_COVERAGE}
    stale = sorted(coverage_keys - inventory_keys)
    assert not stale, f"Stale coverage entries not in inventory: {stale}"


def test_every_coverage_entry_has_assertion_handler() -> None:
    """Every mapped field must have a registered assertion handler."""
    handler_keys = set(FIELD_ASSERTION_HANDLERS.keys())
    for entry in OUTPUT_FIELD_COVERAGE:
        if entry.waived:
            continue
        assert entry.field_key in handler_keys, f"Missing handler for {entry.field_key}"


def test_every_handler_has_coverage_entry() -> None:
    """Every assertion handler must be referenced by the coverage registry."""
    coverage = get_coverage_by_field()
    for field_key in FIELD_ASSERTION_HANDLERS:
        assert field_key in coverage, f"Handler {field_key} lacks coverage entry"


@pytest.mark.parametrize(
    "entry",
    OUTPUT_FIELD_COVERAGE,
    ids=[entry.field_key for entry in OUTPUT_FIELD_COVERAGE],
)
def test_coverage_scenario_loader_exists(entry) -> None:
    """Every mapped scenario function must exist in fixtures.scenarioInputs."""
    from fixtures import scenarioInputs

    assert hasattr(scenarioInputs, entry.scenario_function), f"Missing scenario loader: {entry.scenario_function}"


@pytest.mark.parametrize(
    "entry",
    OUTPUT_FIELD_COVERAGE,
    ids=[entry.field_key for entry in OUTPUT_FIELD_COVERAGE],
)
def test_coverage_test_module_exists(entry) -> None:
    """Every mapped test module file must exist."""
    module_path = Path(__file__).parent / f"{entry.test_module}.py"
    assert module_path.is_file(), f"Missing test module: {entry.test_module}.py"


def test_partial_status_reachable() -> None:
    """PARTIAL is emitted when a calculation has usable partial results."""
    from .output_field_inventory import STATUS_VALUES

    assert "PARTIAL" in STATUS_VALUES
    partial_entries = [entry for entry in OUTPUT_FIELD_COVERAGE if entry.field_key == "item.status.PARTIAL"]
    assert len(partial_entries) == 1
    assert partial_entries[0].scenario_function == "partialMonopolyRentInput"


CRITICAL_SEMANTIC_FIELD_KEYS = frozenset(
    {
        "item.input_values",
        "item.sources",
        "item.formula",
        "item.procedure",
        "item.intermediate_values",
        "item.dependent_calculation_ids",
        "item.status.PARTIAL",
        "item.status.UNAVAILABLE",
        "conclusions.classification_calculation_id",
        "conclusions.flags.calculation_id",
        "conclusions.risk_labels.player.after_calculation_id",
        "conclusions.risk_labels.player.before_calculation_id",
        "conclusions.risk_warnings.calculation_ids",
        "conclusions.strategic_value.player.calculation_id",
        "conclusions.trade_ratio.calculation_id",
        "conclusions.trade_ratio.value",
        "immediate_risk.coverage_ratio_tier",
        "immediate_risk.surplus_or_deficit_tier",
        "immediate_risk.risk_label",
        "immediate_risk.uncapped_risk_penalty",
        "immediate_risk.bounded_risk_penalty",
        "immediate_risk.warnings",
        "railroad_value.context_multiplier",
        "railroad_value.railroad_count",
        "dangerous_monopoly_availability.dangerous_predicate",
        "classification.automatic_rule.predicate_result",
        "classification.automatic_rule.rule",
        "classification.automatic_rule.flag_generated",
        "classification.final_classification",
        "mortgage_capacity.result",
        "monopoly_value.total_monopoly_value",
        "blocking_value.per_property",
        "trade_ratio.raw_trade_ratio",
        "trade_ratio.published_trade_ratio",
        "coverage_ratio.no_exposure",
    }
)


def test_critical_fields_classified_as_semantic() -> None:
    """High-trust fields must be classified as semantic in the coverage registry."""
    by_key = {entry.field_key: entry for entry in OUTPUT_FIELD_COVERAGE}
    missing = sorted(key for key in CRITICAL_SEMANTIC_FIELD_KEYS if by_key[key].assertion_tier != "SEMANTIC")
    assert not missing, f"Critical fields not marked SEMANTIC: {missing}"


def test_every_category_module_exposes_parametrized_field_test() -> None:
    """Each category module must expose the shared parametrized field test."""
    modules = {entry.test_module for entry in OUTPUT_FIELD_COVERAGE}
    for module_name in sorted(modules):
        module = importlib.import_module(f"unit.static_evaluator.evaluate_trade_service.output_fields.{module_name}")
        assert hasattr(module, "test_output_field"), f"{module_name}.test_output_field not found"
