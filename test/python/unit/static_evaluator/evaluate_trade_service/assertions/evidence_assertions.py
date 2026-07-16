"""Shared assertion helpers for application-service tests.

These helpers validate structural invariants and locate calculations
without calculating expected business values using production logic.
"""

from __future__ import annotations

import json
from typing import Any


def assertValidEvidenceEnvelope(evidence: dict[str, Any]) -> None:
    """Assert the evidence envelope has all required top-level fields."""
    assert "id" in evidence, "Missing evidence 'id'"
    assert "algorithm_id" in evidence, "Missing 'algorithm_id'"
    assert evidence["algorithm_id"] == "monopoly_static_algorithm", f"Invalid algorithm_id: {evidence['algorithm_id']}"

    assert "algorithm_name" in evidence, "Missing 'algorithm_name'"
    assert "algorithm_version" in evidence, "Missing 'algorithm_version'"
    assert "purpose" in evidence, "Missing 'purpose'"
    assert "intermediate_calculations" in evidence, "Missing 'intermediate_calculations'"
    assert "final_conclusions" in evidence, "Missing 'final_conclusions'"
    assert "metadata" in evidence, "Missing 'metadata'"
    assert "statistics" in evidence, "Missing 'statistics'"

    metadata = evidence["metadata"]
    assert "implementation_overrides" in metadata, "Missing 'implementation_overrides'"
    assert "specification_dependencies" in metadata, "Missing 'specification_dependencies'"

    assert isinstance(evidence["intermediate_calculations"], list)
    assert len(evidence["intermediate_calculations"]) > 0


def assertCalculationExists(
    evidence: dict[str, Any],
    calculation_type: str,
    *,
    side: str | None = None,
    player_id: str | None = None,
) -> dict[str, Any]:
    """Assert a calculation exists and return it."""
    for calc in evidence["intermediate_calculations"]:
        if calc["calculation_type"] != calculation_type:
            continue
        if side is not None and calc.get("side") != side:
            continue
        if player_id is not None:
            subject_players = calc.get("subject", {}).get("player_ids", [])
            if player_id not in subject_players:
                continue
        return calc

    filters = f"type={calculation_type}"
    if side:
        filters += f", side={side}"
    if player_id:
        filters += f", player={player_id}"
    raise AssertionError(f"Calculation not found: {filters}")


def assertTradeRatio(
    evidence: dict[str, Any],
    *,
    expected_raw: float | None = None,
    expected_published: float | None = None,
    min_published: float | None = None,
    max_published: float | None = None,
) -> None:
    """Assert trade ratio values using canonical intermediate_values keys."""
    calc = assertCalculationExists(evidence, "trade_ratio", side="trade")
    intermediate = calc.get("intermediate_values", {})

    raw = intermediate.get("raw_trade_ratio")
    published = intermediate.get("published_trade_ratio")

    assert raw is not None, "trade_ratio missing intermediate_values.raw_trade_ratio"
    assert published is not None, "trade_ratio missing intermediate_values.published_trade_ratio"

    if expected_raw is not None:
        assert raw == expected_raw, f"Raw ratio: expected {expected_raw}, got {raw}"

    if expected_published is not None:
        assert published == expected_published, f"Published ratio: expected {expected_published}, got {published}"

    if min_published is not None:
        assert published >= min_published, f"Published ratio: expected >= {min_published}, got {published}"

    if max_published is not None:
        assert published <= max_published, f"Published ratio: expected <= {max_published}, got {published}"


def _getFlagsList(evidence: dict[str, Any]) -> list[str]:
    """Extract flags list from evidence, handling both dict and list formats."""
    conclusions = evidence.get("final_conclusions", {})
    flags = conclusions.get("flags", [])
    if isinstance(flags, dict):
        return flags.get("values", [])
    return flags


def assertFlagPresent(evidence: dict[str, Any], flag: str) -> None:
    """Assert a flag is present in final conclusions."""
    flags = _getFlagsList(evidence)
    assert flag in flags, f"Flag '{flag}' not found. Actual flags: {flags}"


def assertFlagAbsent(evidence: dict[str, Any], flag: str) -> None:
    """Assert a flag is NOT present in final conclusions."""
    flags = _getFlagsList(evidence)
    assert flag not in flags, f"Flag '{flag}' should not be present. Actual flags: {flags}"


def assertFinalClassification(evidence: dict[str, Any], expected: str) -> None:
    """Assert the final classification."""
    conclusions = evidence.get("final_conclusions", {})
    actual = conclusions.get("classification")
    assert actual == expected, f"Classification: expected {expected}, got {actual}"


def assertRiskLabel(
    evidence: dict[str, Any],
    player_id: str,
    expected_label: str,
    *,
    side: str = "after",
) -> None:
    """Assert a player's risk label."""
    calc = assertCalculationExists(evidence, "immediate_risk", side=side, player_id=player_id)
    result = calc.get("result", {})
    actual = result.get("risk_label") if isinstance(result, dict) else None

    if actual is None:
        actual = calc.get("intermediate_values", {}).get("risk_label")

    assert actual == expected_label, f"Risk label for {player_id}: expected {expected_label}, got {actual}"


def assertRiskWarningPresent(
    evidence: dict[str, Any],
    player_id: str,
    warning: str,
    *,
    side: str = "after",
) -> None:
    """Assert a risk warning is present for a player."""
    calc = assertCalculationExists(evidence, "immediate_risk", side=side, player_id=player_id)
    result = calc.get("result", {})
    warnings = result.get("warnings", []) if isinstance(result, dict) else []

    if not warnings:
        warnings = calc.get("intermediate_values", {}).get("warnings", [])

    assert warning in warnings, f"Warning '{warning}' not found for {player_id}. Actual: {warnings}"


def assertJsonSerializable(evidence: dict[str, Any]) -> None:
    """Assert the evidence can be serialized to JSON without Python-specific values."""
    try:
        serialized = json.dumps(evidence, indent=2)
        deserialized = json.loads(serialized)
        assert deserialized is not None
    except (TypeError, ValueError) as e:
        raise AssertionError(f"Evidence is not JSON-serializable: {e}")

    forbidden_patterns = [
        "Enum(",
        "<enum",
        "Decimal(",
        "UUID(",
        "datetime(",
        "set(",
        "<class",
        "object at 0x",
    ]
    for pattern in forbidden_patterns:
        assert pattern not in serialized, f"Python-specific pattern found in JSON: {pattern}"


def assertDeterministicIds(evidence: dict[str, Any]) -> None:
    """Assert calculation IDs follow deterministic pattern."""
    calc_ids = [c["id"] for c in evidence["intermediate_calculations"]]
    assert len(calc_ids) == len(set(calc_ids)), "Duplicate calculation IDs found"

    for calc_id in calc_ids:
        assert calc_id.startswith("calc_"), f"Calculation ID should start with 'calc_': {calc_id}"


def assertValidDependencyGraph(evidence: dict[str, Any]) -> None:
    """Assert the dependency graph is well-formed."""
    all_ids = {c["id"] for c in evidence["intermediate_calculations"]}

    for calc in evidence["intermediate_calculations"]:
        calc_id = calc["id"]
        deps = calc.get("dependent_calculation_ids", [])
        assert calc_id not in deps, f"Self-dependency in {calc_id}"
        for dep_id in deps:
            assert dep_id in all_ids, f"Calculation {calc_id} references non-existent: {dep_id}"


def assertStrategicValueComponentsExist(evidence: dict[str, Any]) -> None:
    """Assert all Strategic Value components exist."""
    components = [
        "base_asset_value",
        "monopoly_value",
        "railroad_value",
        "blocking_value",
        "strategic_opportunity_score",
        "immediate_risk",
        "strategic_value",
    ]

    for component in components:
        calcs = [c for c in evidence["intermediate_calculations"] if c["calculation_type"] == component]
        assert len(calcs) > 0, f"Missing calculation type: {component}"


def getCalculationsByType(evidence: dict[str, Any], calculation_type: str) -> list[dict[str, Any]]:
    """Get all calculations of a specific type."""
    return [c for c in evidence["intermediate_calculations"] if c["calculation_type"] == calculation_type]
