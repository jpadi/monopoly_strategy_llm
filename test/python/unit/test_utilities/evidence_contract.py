"""Evidence contract validation utilities.

Validates that every calculation item conforms to the Static Algorithm Evidence Specification.
These utilities validate semantic invariants, not just key existence.
"""

from __future__ import annotations

from typing import Any


VALID_STATUSES = frozenset({"COMPLETE", "PARTIAL", "UNAVAILABLE", "ERROR"})
VALID_SIDES = frozenset({"before", "after", "delta", "trade"})

VALID_SOURCE_LABELS = frozenset(
    {
        "SPECIFICATION_DEFAULT",
        "GAME_CONFIGURATION",
        "GAME_CONFIGURATION_OVERRIDE",
        "BOARD_STATE_RENT_TABLE",
        "CLASSIC_DEFAULT",
        "NEUTRAL_CUSTOM_GROUP_DEFAULT",
        "RISK_REFERENCE_DEFAULT",
        "IMPLEMENTATION_OVERRIDE",
    }
)

REGISTERED_CALCULATION_TYPES = frozenset(
    {
        "base_asset_value",
        "mortgage_capacity",
        "available_construction_budget",
        "development_capability",
        "monopoly_value",
        "house_control",
        "house_control_bonus",
        "house_denial",
        "house_denial_bonus",
        "railroad_value",
        "blocking_value",
        "strategic_opportunity_score",
        "dangerous_monopoly_availability",
        "available_risk_resources",
        "landing_exposure",
        "repair_exposure",
        "largest_threat",
        "risk_margin",
        "coverage_ratio",
        "immediate_risk",
        "strategic_value",
        "trade_ratio",
        "final_static_classification",
    }
)


def assertValidCalculationItem(item: dict[str, Any], context: str = "") -> None:
    """Assert a calculation item conforms to the evidence specification.

    Args:
        item: The calculation item dictionary to validate
        context: Optional context string for error messages
    """
    prefix = f"{context}: " if context else ""

    # Required fields
    assert "id" in item, f"{prefix}Missing 'id' field"
    assert isinstance(item["id"], str), f"{prefix}'id' must be string"
    assert item["id"], f"{prefix}'id' cannot be empty"

    assert "calculation_type" in item, f"{prefix}Missing 'calculation_type'"
    assert item["calculation_type"] in REGISTERED_CALCULATION_TYPES, (
        f"{prefix}Unknown calculation_type: {item['calculation_type']}"
    )

    assert "description" in item, f"{prefix}Missing 'description'"
    assert isinstance(item["description"], str), f"{prefix}'description' must be string"

    assert "status" in item, f"{prefix}Missing 'status'"
    assert item["status"] in VALID_STATUSES, f"{prefix}Invalid status: {item['status']}"

    assert "side" in item, f"{prefix}Missing 'side'"
    assert item["side"] in VALID_SIDES, f"{prefix}Invalid side: {item['side']}"

    # Subject validation
    assert "subject" in item, f"{prefix}Missing 'subject'"
    subject = item["subject"]
    assert isinstance(subject, dict), f"{prefix}'subject' must be dict"
    assert "player_ids" in subject, f"{prefix}Missing 'subject.player_ids'"
    assert "property_ids" in subject, f"{prefix}Missing 'subject.property_ids'"
    assert "group_ids" in subject, f"{prefix}Missing 'subject.group_ids'"
    assert "trade_id" in subject, f"{prefix}Missing 'subject.trade_id'"
    assert "transfer_ids" in subject, f"{prefix}Missing 'subject.transfer_ids'"

    # Input references and values
    assert "input_references" in item, f"{prefix}Missing 'input_references'"
    assert isinstance(item["input_references"], list), (
        f"{prefix}'input_references' must be list"
    )

    assert "input_values" in item, f"{prefix}Missing 'input_values'"
    assert isinstance(item["input_values"], dict), (
        f"{prefix}'input_values' must be dict"
    )

    assert "sources" in item, f"{prefix}Missing 'sources'"
    assert isinstance(item["sources"], dict), f"{prefix}'sources' must be dict"

    # Intermediate values and result
    assert "intermediate_values" in item, f"{prefix}Missing 'intermediate_values'"
    assert isinstance(item["intermediate_values"], dict), (
        f"{prefix}'intermediate_values' must be dict"
    )

    assert "result" in item, f"{prefix}Missing 'result'"

    # Limitations and missing inputs
    assert "limitations" in item, f"{prefix}Missing 'limitations'"
    assert isinstance(item["limitations"], list), f"{prefix}'limitations' must be list"

    assert "missing_inputs" in item, f"{prefix}Missing 'missing_inputs'"
    assert isinstance(item["missing_inputs"], list), (
        f"{prefix}'missing_inputs' must be list"
    )

    # Status-specific validation
    status = item["status"]
    if status == "COMPLETE":
        # Some calculations like bonuses may legitimately have null/zero results
        # when no bonus applies, so we don't require non-null result
        assert len(item["missing_inputs"]) == 0, (
            f"{prefix}COMPLETE calculation must have empty missing_inputs"
        )

    elif status in ("PARTIAL", "UNAVAILABLE"):
        assert len(item["missing_inputs"]) > 0 or len(item["limitations"]) > 0, (
            f"{prefix}{status} calculation must explain why in missing_inputs or limitations"
        )

    elif status == "ERROR":
        assert len(item["limitations"]) > 0, (
            f"{prefix}ERROR calculation must identify error in limitations"
        )


def assertValidEvidenceObject(evidence: dict[str, Any]) -> None:
    """Assert the complete evidence object is valid.

    Args:
        evidence: The complete static algorithm evidence dictionary
    """
    # Top-level required fields
    assert "id" in evidence, "Missing evidence 'id'"
    assert "algorithm_id" in evidence, "Missing 'algorithm_id'"
    assert evidence["algorithm_id"] == "monopoly_static_algorithm", (
        f"Invalid algorithm_id: {evidence['algorithm_id']}"
    )

    assert "algorithm_name" in evidence, "Missing 'algorithm_name'"
    assert "algorithm_version" in evidence, "Missing 'algorithm_version'"

    assert "purpose" in evidence, "Missing 'purpose'"
    assert "intermediate_calculations" in evidence, (
        "Missing 'intermediate_calculations'"
    )
    assert "final_conclusions" in evidence, "Missing 'final_conclusions'"
    assert "metadata" in evidence, "Missing 'metadata'"
    assert "statistics" in evidence, "Missing 'statistics'"

    # Validate metadata
    metadata = evidence["metadata"]
    assert "implementation_overrides" in metadata, "Missing 'implementation_overrides'"
    assert "specification_dependencies" in metadata, (
        "Missing 'specification_dependencies'"
    )

    # Validate all calculation items
    calcs = evidence["intermediate_calculations"]
    assert isinstance(calcs, list), "'intermediate_calculations' must be list"
    assert len(calcs) > 0, "Must have at least one calculation"

    for i, calc in enumerate(calcs):
        assertValidCalculationItem(calc, context=f"calc[{i}]")


def assertCalculationExists(
    evidence: dict[str, Any],
    calculation_type: str,
    side: str | None = None,
    player_id: str | None = None,
) -> dict[str, Any]:
    """Assert a calculation exists and return it.

    Args:
        evidence: The complete evidence dictionary
        calculation_type: The type of calculation to find
        side: Optional side filter
        player_id: Optional player filter

    Returns:
        The matching calculation item

    Raises:
        AssertionError if not found
    """
    for calc in evidence["intermediate_calculations"]:
        if calc["calculation_type"] != calculation_type:
            continue
        if side is not None and calc["side"] != side:
            continue
        if player_id is not None and player_id not in calc["subject"]["player_ids"]:
            continue
        return calc

    filters = f"type={calculation_type}"
    if side:
        filters += f", side={side}"
    if player_id:
        filters += f", player={player_id}"
    raise AssertionError(f"Calculation not found: {filters}")


def assertAllCalculationsComplete(
    evidence: dict[str, Any],
    exclude_types: set[str] | None = None,
) -> None:
    """Assert all calculations have COMPLETE status.

    Args:
        evidence: The complete evidence dictionary
        exclude_types: Optional set of calculation types to exclude from check
    """
    exclude = exclude_types or set()
    for calc in evidence["intermediate_calculations"]:
        if calc["calculation_type"] in exclude:
            continue
        assert calc["status"] == "COMPLETE", (
            f"Calculation {calc['id']} ({calc['calculation_type']}) "
            f"has status {calc['status']}, expected COMPLETE"
        )


def getCalculationsByType(
    evidence: dict[str, Any],
    calculation_type: str,
) -> list[dict[str, Any]]:
    """Get all calculations of a specific type.

    Args:
        evidence: The complete evidence dictionary
        calculation_type: The type to filter by

    Returns:
        List of matching calculations
    """
    return [
        c
        for c in evidence["intermediate_calculations"]
        if c["calculation_type"] == calculation_type
    ]


def getCalculationById(
    evidence: dict[str, Any],
    calc_id: str,
) -> dict[str, Any] | None:
    """Get a calculation by its ID.

    Args:
        evidence: The complete evidence dictionary
        calc_id: The calculation ID

    Returns:
        The calculation or None if not found
    """
    for calc in evidence["intermediate_calculations"]:
        if calc["id"] == calc_id:
            return calc
    return None
