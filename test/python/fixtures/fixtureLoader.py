"""Canonical JSON fixture loader for Static Evaluator tests.

This module provides a validated fixture loader that:
- Loads complete scenario inputs from canonical JSON files
- Validates fixture structure and consistency
- Supports both valid and intentionally invalid fixtures
- Produces clear error messages when fixtures are malformed

JSON fixtures are the authoritative source of scenario data.
Python scenario functions document and load fixtures but do not construct them.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


FIXTURE_ROOT = Path(__file__).parent / "inputs"


class FixtureLoadError(Exception):
    """Raised when a fixture cannot be loaded or validated."""

    pass


class FixtureValidationError(Exception):
    """Raised when a fixture fails semantic validation."""

    pass


def loadScenarioInput(
    relative_path: str,
    *,
    validate: bool = True,
) -> dict[str, Any]:
    """Load a scenario input from a canonical JSON fixture.

    Args:
        relative_path: Path relative to the fixture root (e.g., "trade_ratio/ratio_exactly_three.json")
        validate: If True, validate fixture structure and consistency.
                  Set to False only for intentionally invalid fixtures.

    Returns:
        The complete canonical evaluation input dictionary.

    Raises:
        FixtureLoadError: If file cannot be found or parsed
        FixtureValidationError: If fixture fails validation (when validate=True)
    """
    fixture_path = FIXTURE_ROOT / relative_path

    if not fixture_path.exists():
        raise FixtureLoadError(f"Scenario fixture not found: {relative_path}")

    # Verify path is within fixture root (prevent path traversal)
    try:
        fixture_path.resolve().relative_to(FIXTURE_ROOT.resolve())
    except ValueError:
        raise FixtureLoadError(
            f"Invalid fixture path (outside fixture root): {relative_path}"
        )

    try:
        with open(fixture_path, "r", encoding="utf-8") as f:
            content = f.read()
    except IOError as e:
        raise FixtureLoadError(f"Cannot read fixture {relative_path}: {e}")

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise FixtureLoadError(
            f"Invalid JSON in {relative_path} at line {e.lineno}, column {e.colno}: {e.msg}"
        )

    if not isinstance(data, dict):
        raise FixtureLoadError(f"Scenario root must be a JSON object: {relative_path}")

    if validate:
        _validateFixture(data, relative_path)

    return data


def loadRawScenarioInput(relative_path: str) -> dict[str, Any]:
    """Load a scenario input without validation.

    Use this only for intentionally invalid fixtures that test error handling.
    The fixture must still be valid JSON, but may violate semantic rules.

    Args:
        relative_path: Path relative to the fixture root

    Returns:
        The raw fixture dictionary without validation
    """
    return loadScenarioInput(relative_path, validate=False)


def _validateFixture(data: dict[str, Any], path: str) -> None:
    """Validate fixture structure and consistency.

    Args:
        data: The loaded fixture dictionary
        path: Fixture path for error messages

    Raises:
        FixtureValidationError: If validation fails
    """
    # Check required top-level sections
    required_sections = [
        "metadata",
        "game_configuration",
        "board_state_before",
        "board_state_after",
        "trade",
    ]
    for section in required_sections:
        if section not in data:
            raise FixtureValidationError(
                f"Missing required section '{section}' in {path}"
            )

    # Validate metadata completeness
    metadata = data["metadata"]
    required_metadata = [
        "evaluation_id",
        "game_id",
        "platform",
        "game_version",
        "evaluation_timestamp",
        "schema_version",
        "language",
    ]
    for field in required_metadata:
        if field not in metadata:
            raise FixtureValidationError(f"Missing metadata field '{field}' in {path}")

    # Validate trade structure
    trade = data["trade"]
    required_trade = [
        "id",
        "status",
        "initiating_player_id",
        "participants",
        "transfers",
    ]
    for field in required_trade:
        if field not in trade:
            raise FixtureValidationError(f"Missing trade field '{field}' in {path}")

    # Validate transfer semantics
    for i, transfer in enumerate(trade["transfers"]):
        _validateTransfer(transfer, i, path)

    # Validate board states
    before = data["board_state_before"]
    after = data["board_state_after"]

    _validateBoardState(before, "board_state_before", path)
    _validateBoardState(after, "board_state_after", path)

    # Validate ownership consistency in both states
    _validateOwnershipConsistency(before, "board_state_before", path)
    _validateOwnershipConsistency(after, "board_state_after", path)

    # Validate classic board completeness if applicable
    config = data["game_configuration"]
    if config.get("ruleset_name") == "classic_monopoly":
        _validateClassicBoard(before, "board_state_before", path)
        _validateClassicBoard(after, "board_state_after", path)
        _validatePropertySetConsistency(before, after, path)


def _validateTransfer(transfer: dict[str, Any], index: int, path: str) -> None:
    """Validate a single transfer follows canonical semantics."""
    required = [
        "id",
        "from_player_id",
        "to_player_id",
        "asset_type",
        "asset_id",
        "amount",
    ]
    for field in required:
        if field not in transfer:
            raise FixtureValidationError(
                f"Transfer {index} missing field '{field}' in {path}"
            )

    asset_type = transfer["asset_type"]
    asset_id = transfer["asset_id"]
    amount = transfer["amount"]

    if asset_type == "cash":
        if asset_id is not None:
            raise FixtureValidationError(
                f"Transfer {index}: cash transfer requires asset_id=null in {path}"
            )
        if amount <= 0:
            raise FixtureValidationError(
                f"Transfer {index}: cash transfer requires amount > 0 in {path}"
            )
    elif asset_type == "property":
        if asset_id is None:
            raise FixtureValidationError(
                f"Transfer {index}: property transfer requires asset_id in {path}"
            )
        if amount != 0:
            raise FixtureValidationError(
                f"Transfer {index}: property transfer requires amount=0 in {path}"
            )


def _validateBoardState(board: dict[str, Any], name: str, path: str) -> None:
    """Validate board state structure."""
    if "players" not in board:
        raise FixtureValidationError(f"Missing 'players' in {name} in {path}")
    if "properties" not in board:
        raise FixtureValidationError(f"Missing 'properties' in {name} in {path}")


def _validateOwnershipConsistency(board: dict[str, Any], name: str, path: str) -> None:
    """Validate that player.owned_properties matches property.owner_player_id.

    This is a deliberate improvement over silent synchronization.
    The JSON must already be consistent.
    """
    properties_by_id = {p["id"]: p for p in board["properties"]}
    player_ids = {p["id"] for p in board["players"]}

    # Check each player's owned_properties list
    for player in board["players"]:
        player_id = player["id"]
        owned = player.get("owned_properties", [])

        for prop_id in owned:
            if prop_id not in properties_by_id:
                raise FixtureValidationError(
                    f"Player {player_id} owns non-existent property {prop_id} in {name} in {path}"
                )
            prop = properties_by_id[prop_id]
            if prop.get("owner_player_id") != player_id:
                raise FixtureValidationError(
                    f"Ownership mismatch: {player_id}.owned_properties includes {prop_id} "
                    f"but property.owner_player_id is {prop.get('owner_player_id')} "
                    f"in {name} in {path}"
                )

    # Check each property's owner is in their owned_properties list
    for prop in board["properties"]:
        owner = prop.get("owner_player_id")
        if owner is not None:
            if owner not in player_ids:
                raise FixtureValidationError(
                    f"Property {prop['id']} owned by non-existent player {owner} "
                    f"in {name} in {path}"
                )
            player = next(p for p in board["players"] if p["id"] == owner)
            owned = player.get("owned_properties", [])
            if prop["id"] not in owned:
                raise FixtureValidationError(
                    f"Ownership mismatch: property {prop['id']} has owner_player_id={owner} "
                    f"but {owner}.owned_properties does not include it "
                    f"in {name} in {path}"
                )


def _validateClassicBoard(board: dict[str, Any], name: str, path: str) -> None:
    """Validate classic Monopoly board completeness.

    Classic board must have:
    - 28 total purchasable properties
    - 22 streets
    - 4 railroads
    - 2 utilities
    """
    props = board["properties"]

    if len(props) != 28:
        raise FixtureValidationError(
            f"Classic board requires 28 properties, found {len(props)} in {name} in {path}"
        )

    streets = [p for p in props if p.get("category") == "street"]
    railroads = [p for p in props if p.get("category") == "railroad"]
    utilities = [p for p in props if p.get("category") == "utility"]

    if len(streets) != 22:
        raise FixtureValidationError(
            f"Classic board requires 22 streets, found {len(streets)} in {name} in {path}"
        )
    if len(railroads) != 4:
        raise FixtureValidationError(
            f"Classic board requires 4 railroads, found {len(railroads)} in {name} in {path}"
        )
    if len(utilities) != 2:
        raise FixtureValidationError(
            f"Classic board requires 2 utilities, found {len(utilities)} in {name} in {path}"
        )


def _validatePropertySetConsistency(
    before: dict[str, Any], after: dict[str, Any], path: str
) -> None:
    """Validate before and after have the same property IDs."""
    before_ids = {p["id"] for p in before["properties"]}
    after_ids = {p["id"] for p in after["properties"]}

    if before_ids != after_ids:
        missing_after = before_ids - after_ids
        missing_before = after_ids - before_ids
        msg = f"Property set mismatch in {path}."
        if missing_after:
            msg += f" Missing in after: {missing_after}."
        if missing_before:
            msg += f" Missing in before: {missing_before}."
        raise FixtureValidationError(msg)
