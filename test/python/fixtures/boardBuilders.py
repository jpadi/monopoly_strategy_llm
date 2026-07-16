"""Classic Monopoly board builders for fixture generation and builder-specific tests.

This module provides low-level utilities for:
- Creating complete classic Monopoly boards
- Creating custom board configurations
- Constructing canonical transfer objects
- Validating classic board structure

IMPORTANT: This module is NOT the source of truth for committed test scenarios.
Named scenarios are defined as canonical JSON fixtures loaded via scenarioInputs.py.
These builders are retained for:
- Developer fixture generation/authoring
- Builder-specific tests
- Custom programmatic test construction
"""

from __future__ import annotations

from typing import Any

from fixtures.classicBoardData import (
    CLASSIC_PROPERTY_IDS,
    CLASSIC_PURCHASABLE_COUNT,
    CLASSIC_RAILROAD_COUNT,
    CLASSIC_STREET_COUNT,
    CLASSIC_STREET_GROUP_SIZES,
    CLASSIC_UTILITY_COUNT,
    classicAllProperties,
)

# ──────────────────────────────────────────────────────────────
# Internal Property Constructors
# ──────────────────────────────────────────────────────────────


def _street(
    *,
    id: str,
    display_name: str,
    group_id: str,
    owner_player_id: str | None,
    purchase_price: int,
    mortgage_value: int,
    house_cost: int,
    rent_table: dict[str, int],
    houses: int = 0,
    has_hotel: bool = False,
    is_mortgaged: bool = False,
    is_tradable: bool = True,
) -> dict[str, Any]:
    return {
        "id": id,
        "display_name": display_name,
        "category": "street",
        "group_id": group_id,
        "owner_player_id": owner_player_id,
        "purchase_price": purchase_price,
        "mortgage_value": mortgage_value,
        "house_cost": house_cost,
        "hotel_cost": house_cost,
        "houses": houses,
        "has_hotel": has_hotel,
        "is_mortgaged": is_mortgaged,
        "is_tradable": is_tradable,
        "rent_table": rent_table,
    }


def _railroad(*, id: str, owner_player_id: str | None, is_tradable: bool = True) -> dict[str, Any]:
    return {
        "id": id,
        "display_name": id,
        "category": "railroad",
        "group_id": "railroad",
        "owner_player_id": owner_player_id,
        "purchase_price": 200,
        "mortgage_value": 100,
        "houses": 0,
        "has_hotel": False,
        "is_mortgaged": False,
        "is_tradable": is_tradable,
    }


# ──────────────────────────────────────────────────────────────
# Ownership Synchronization
# ──────────────────────────────────────────────────────────────


def _syncOwnedProperties(board: dict[str, Any]) -> None:
    """Synchronize player.owned_properties with property.owner_player_id."""
    ownership: dict[str, list[str]] = {p["id"]: [] for p in board["players"]}
    for prop in board["properties"]:
        owner = prop.get("owner_player_id")
        if owner:
            ownership.setdefault(owner, []).append(prop["id"])
    for player in board["players"]:
        player["owned_properties"] = ownership.get(player["id"], [])


def _validateOwnershipConsistency(board: dict[str, Any]) -> None:
    """Validate that player.owned_properties matches property.owner_player_id."""
    propsById = {p["id"]: p for p in board["properties"]}
    for player in board["players"]:
        for pid in player["owned_properties"]:
            assert propsById[pid]["owner_player_id"] == player["id"]
    for prop in board["properties"]:
        owner = prop.get("owner_player_id")
        if owner:
            player = next(p for p in board["players"] if p["id"] == owner)
            assert prop["id"] in player["owned_properties"]


# ──────────────────────────────────────────────────────────────
# Public Board Builders
# ──────────────────────────────────────────────────────────────


def assignPropertyOwners(
    board: dict[str, Any],
    owners: dict[str, str | None],
) -> None:
    """Assign property owners and synchronize ownership lists."""
    for prop in board["properties"]:
        if prop["id"] in owners:
            prop["owner_player_id"] = owners[prop["id"]]
    _syncOwnedProperties(board)


def validateClassicFixtureBoard(board: dict[str, Any]) -> None:
    """Validate classic Monopoly board structure.

    Verifies:
    - 28 total properties
    - 22 streets, 4 railroads, 2 utilities
    - Correct group sizes
    - Ownership consistency
    """
    props = board["properties"]
    assert len(props) == CLASSIC_PURCHASABLE_COUNT
    assert {p["id"] for p in props} == set(CLASSIC_PROPERTY_IDS)
    streets = [p for p in props if p["category"] == "street"]
    railroads = [p for p in props if p["category"] == "railroad"]
    utilities = [p for p in props if p["category"] == "utility"]
    assert len(streets) == CLASSIC_STREET_COUNT
    assert len(railroads) == CLASSIC_RAILROAD_COUNT
    assert len(utilities) == CLASSIC_UTILITY_COUNT
    for groupId, size in CLASSIC_STREET_GROUP_SIZES.items():
        assert sum(1 for p in streets if p["group_id"] == groupId) == size
    _validateOwnershipConsistency(board)


def classicTwoPlayerBoard(
    *,
    playerACash: int = 2000,
    playerBCash: int = 1500,
    owners: dict[str, str | None] | None = None,
    availableHouses: int = 32,
    availableHotels: int = 12,
) -> dict[str, Any]:
    """Create a complete classic Monopoly board for two players.

    Args:
        playerACash: Starting cash for player A
        playerBCash: Starting cash for player B
        owners: Optional property ownership mapping
        availableHouses: Available houses in bank
        availableHotels: Available hotels in bank

    Returns:
        Complete board state dictionary
    """
    board = {
        "players": [
            {"id": "player_a", "cash": playerACash, "owned_properties": []},
            {"id": "player_b", "cash": playerBCash, "owned_properties": []},
        ],
        "properties": classicAllProperties(owners=owners or {}),
        "tradable_assets": [],
        "game_state": {
            "available_houses": availableHouses,
            "available_hotels": availableHotels,
        },
    }
    _syncOwnedProperties(board)
    validateClassicFixtureBoard(board)
    return board


def customTwoPlayerBoard(
    *,
    properties: list[dict[str, Any]],
    playerACash: int = 2000,
    playerBCash: int = 1500,
    availableHouses: int = 32,
    availableHotels: int = 12,
) -> dict[str, Any]:
    """Create a custom board for two players.

    Args:
        properties: Custom property list
        playerACash: Starting cash for player A
        playerBCash: Starting cash for player B
        availableHouses: Available houses in bank
        availableHotels: Available hotels in bank

    Returns:
        Complete board state dictionary
    """
    board = {
        "players": [
            {"id": "player_a", "cash": playerACash, "owned_properties": []},
            {"id": "player_b", "cash": playerBCash, "owned_properties": []},
        ],
        "properties": properties,
        "tradable_assets": [],
        "game_state": {
            "available_houses": availableHouses,
            "available_hotels": availableHotels,
        },
    }
    _syncOwnedProperties(board)
    _validateOwnershipConsistency(board)
    return board


# ──────────────────────────────────────────────────────────────
# Game Configuration
# ──────────────────────────────────────────────────────────────


def gameConfiguration(**overrides: Any) -> dict[str, Any]:
    """Create a classic Monopoly game configuration."""
    base: dict[str, Any] = {
        "ruleset_name": "classic_monopoly",
        "total_houses": 32,
        "total_hotels": 12,
        "mortgage_interest_rate": 0.10,
        "even_building_required": True,
        "house_sell_back_ratio": 0.50,
        "hotel_sell_back_ratio": 0.50,
        "hotel_liquidation_basis": "houses_plus_hotel",
        "building_allowed_with_mortgaged_group_member": False,
    }
    base.update(overrides)
    return base


def customGameConfiguration(**overrides: Any) -> dict[str, Any]:
    """Create a custom game configuration (non-classic ruleset)."""
    return gameConfiguration(ruleset_name="custom_purple_board", **overrides)


# ──────────────────────────────────────────────────────────────
# Transfer Constructors
# ──────────────────────────────────────────────────────────────


def transferCash(
    *,
    id: str,
    from_player_id: str,
    to_player_id: str,
    amount: int,
) -> dict[str, Any]:
    """Create a canonical cash transfer object.

    Cash transfers:
    - asset_type = "cash"
    - asset_id = null
    - amount > 0
    """
    return {
        "id": id,
        "from_player_id": from_player_id,
        "to_player_id": to_player_id,
        "asset_type": "cash",
        "asset_id": None,
        "amount": amount,
    }


def transferProperty(
    *,
    id: str,
    from_player_id: str,
    to_player_id: str,
    asset_id: str,
) -> dict[str, Any]:
    """Create a canonical property transfer object.

    Property transfers:
    - asset_type = "property"
    - asset_id = property ID
    - amount = 0 (not applicable for property)
    """
    return {
        "id": id,
        "from_player_id": from_player_id,
        "to_player_id": to_player_id,
        "asset_type": "property",
        "asset_id": asset_id,
        "amount": 0,
    }
