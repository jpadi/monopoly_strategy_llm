"""Field-level assertion helpers for output-field verification tests."""

from __future__ import annotations

import json
from typing import Any

from ..assertions.evidence_assertions import assertCalculationExists


def getCalculation(
    evidence: dict[str, Any],
    calculation_type: str,
    *,
    side: str | None = None,
    player_id: str | None = None,
) -> dict[str, Any]:
    """Return a calculation item or raise."""
    return assertCalculationExists(evidence, calculation_type, side=side, player_id=player_id)


def assertFieldEquals(
    actual: Any,
    expected: Any,
    *,
    field_path: str,
    scenario: str,
) -> None:
    """Assert an output field equals the expected value."""
    assert actual == expected, f"Scenario {scenario}: {field_path}\n  expected: {expected!r}\n  actual:   {actual!r}"


def assertFieldIn(
    actual: Any,
    allowed: set[Any],
    *,
    field_path: str,
    scenario: str,
) -> None:
    """Assert an output field is one of the allowed values."""
    assert actual in allowed, (
        f"Scenario {scenario}: {field_path}\n  expected one of: {sorted(allowed)!r}\n  actual: {actual!r}"
    )


def assertFieldIsType(
    value: Any,
    expected_type: type,
    *,
    field_path: str,
    scenario: str,
) -> None:
    """Assert a field has the expected Python type."""
    assert isinstance(value, expected_type), (
        f"Scenario {scenario}: {field_path}\n"
        f"  expected type: {expected_type.__name__}\n"
        f"  actual type:   {type(value).__name__}"
    )


def assertNonEmptyString(
    value: Any,
    *,
    field_path: str,
    scenario: str,
) -> None:
    """Assert a field is a non-empty string."""
    assertFieldIsType(value, str, field_path=field_path, scenario=scenario)
    assert value, f"Scenario {scenario}: {field_path} must be non-empty"


def assertInputReferenceResolves(
    input_data: dict[str, Any],
    reference: str,
    *,
    scenario: str,
) -> None:
    """Assert an input_references path resolves against the evaluation input."""
    if reference.startswith("trade.transfers["):
        transfer_id = reference.split("[", 1)[1].rstrip("]")
        transfers = input_data["trade"]["transfers"]
        assert any(t["id"] == transfer_id for t in transfers), (
            f"Scenario {scenario}: transfer reference {reference!r} not found"
        )
        return

    if reference.startswith("board_state_before.properties[") or reference.startswith("board_state_after.properties["):
        board_key = "board_state_before" if reference.startswith("board_state_before") else "board_state_after"
        property_id = reference.split("[", 1)[1].rstrip("]")
        properties = input_data[board_key]["properties"]
        assert any(p["id"] == property_id for p in properties), (
            f"Scenario {scenario}: property reference {reference!r} not found"
        )
        return

    if reference.startswith("game_configuration."):
        path = reference.removeprefix("game_configuration.")
        config = input_data["game_configuration"]
        if path.startswith("group_multipliers["):
            group_id = path.split("[", 1)[1].rstrip("]")
            assert group_id in config.get("group_multipliers", {}), (
                f"Scenario {scenario}: group multiplier reference {reference!r} not found"
            )
            return
        assert path in config, f"Scenario {scenario}: config reference {reference!r} not found"
        return

    if reference.startswith("board_state_before.players[") or reference.startswith("board_state_after.players["):
        board_key = "board_state_before" if reference.startswith("board_state_before") else "board_state_after"
        player_id = reference.split("[", 1)[1].rstrip("]")
        players = input_data[board_key]["players"]
        assert any(p["id"] == player_id for p in players), (
            f"Scenario {scenario}: player reference {reference!r} not found"
        )
        return

    raise AssertionError(f"Scenario {scenario}: unsupported input reference pattern {reference!r}")


def assertConclusionReferencesCalculation(
    evidence: dict[str, Any],
    calculation_id: str,
) -> None:
    """Assert a final-conclusion calculation_id references an existing calc."""
    calc_ids = {c["id"] for c in evidence["intermediate_calculations"]}
    assert calculation_id in calc_ids, f"Conclusion references missing calculation: {calculation_id}"


def countCalculationsByStatus(evidence: dict[str, Any]) -> dict[str, int]:
    """Count calculations grouped by status."""
    counts: dict[str, int] = {}
    for calc in evidence["intermediate_calculations"]:
        status = calc["status"]
        counts[status] = counts.get(status, 0) + 1
    return counts


def assertJsonRoundTrip(evidence: dict[str, Any]) -> None:
    """Assert evidence survives JSON serialization."""
    serialized = json.dumps(evidence)
    assert json.loads(serialized) is not None
