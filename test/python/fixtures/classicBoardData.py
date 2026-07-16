"""Canonical classic Monopoly property definitions for test fixtures."""

from __future__ import annotations

from typing import Any

CLASSIC_STREET_COUNT = 22
CLASSIC_RAILROAD_COUNT = 4
CLASSIC_UTILITY_COUNT = 2
CLASSIC_PURCHASABLE_COUNT = CLASSIC_STREET_COUNT + CLASSIC_RAILROAD_COUNT + CLASSIC_UTILITY_COUNT

CLASSIC_STREET_GROUP_SIZES: dict[str, int] = {
    "brown": 2,
    "light_blue": 3,
    "pink": 3,
    "orange": 3,
    "red": 3,
    "yellow": 3,
    "green": 3,
    "dark_blue": 2,
}

CLASSIC_PROPERTY_IDS: frozenset[str] = frozenset(
    {
        "property_mediterranean",
        "property_baltic",
        "property_oriental",
        "property_vermont",
        "property_connecticut",
        "property_st_charles",
        "property_states",
        "property_virginia",
        "property_st_james",
        "property_tennessee",
        "property_new_york",
        "property_kentucky",
        "property_indiana",
        "property_illinois",
        "property_atlantic",
        "property_ventnor",
        "property_marvin_gardens",
        "property_pacific",
        "property_north_carolina",
        "property_pennsylvania",
        "property_park_place",
        "property_boardwalk",
        "property_rr_1",
        "property_rr_2",
        "property_rr_3",
        "property_rr_4",
        "property_electric_company",
        "property_water_works",
    }
)


def _rent(
    base: int,
    one: int,
    two: int,
    three: int,
    four: int,
    hotel: int,
) -> dict[str, int]:
    return {
        "base": base,
        "one_house": one,
        "two_houses": two,
        "three_houses": three,
        "four_houses": four,
        "hotel": hotel,
    }


_RAILROAD_RENT = {
    "railroad_1_owned": 25,
    "railroad_2_owned": 50,
    "railroad_3_owned": 100,
    "railroad_4_owned": 200,
}

_UTILITY_RENT = {
    "utility_1_owned": 48,
    "utility_2_owned": 120,
}

# Canonical classic Monopoly values aligned with ClassicRiskReference rent matrices.
_STREET_DEFINITIONS: tuple[dict[str, Any], ...] = (
    {
        "id": "property_mediterranean",
        "display_name": "Mediterranean Avenue",
        "group_id": "brown",
        "purchase_price": 60,
        "mortgage_value": 30,
        "house_cost": 50,
        "rent_table": _rent(2, 10, 30, 90, 160, 250),
    },
    {
        "id": "property_baltic",
        "display_name": "Baltic Avenue",
        "group_id": "brown",
        "purchase_price": 60,
        "mortgage_value": 30,
        "house_cost": 50,
        "rent_table": _rent(4, 20, 60, 180, 320, 450),
    },
    {
        "id": "property_oriental",
        "display_name": "Oriental Avenue",
        "group_id": "light_blue",
        "purchase_price": 100,
        "mortgage_value": 50,
        "house_cost": 50,
        "rent_table": _rent(6, 30, 90, 270, 400, 550),
    },
    {
        "id": "property_vermont",
        "display_name": "Vermont Avenue",
        "group_id": "light_blue",
        "purchase_price": 100,
        "mortgage_value": 50,
        "house_cost": 50,
        "rent_table": _rent(6, 30, 90, 270, 400, 550),
    },
    {
        "id": "property_connecticut",
        "display_name": "Connecticut Avenue",
        "group_id": "light_blue",
        "purchase_price": 120,
        "mortgage_value": 60,
        "house_cost": 50,
        "rent_table": _rent(8, 40, 100, 300, 450, 600),
    },
    {
        "id": "property_st_charles",
        "display_name": "St. Charles Place",
        "group_id": "pink",
        "purchase_price": 140,
        "mortgage_value": 70,
        "house_cost": 100,
        "rent_table": _rent(10, 50, 150, 450, 625, 750),
    },
    {
        "id": "property_states",
        "display_name": "States Avenue",
        "group_id": "pink",
        "purchase_price": 140,
        "mortgage_value": 70,
        "house_cost": 100,
        "rent_table": _rent(10, 50, 150, 450, 625, 750),
    },
    {
        "id": "property_virginia",
        "display_name": "Virginia Avenue",
        "group_id": "pink",
        "purchase_price": 160,
        "mortgage_value": 80,
        "house_cost": 100,
        "rent_table": _rent(12, 60, 180, 500, 700, 900),
    },
    {
        "id": "property_st_james",
        "display_name": "St. James Place",
        "group_id": "orange",
        "purchase_price": 180,
        "mortgage_value": 90,
        "house_cost": 100,
        "rent_table": _rent(14, 70, 200, 550, 750, 950),
    },
    {
        "id": "property_tennessee",
        "display_name": "Tennessee Avenue",
        "group_id": "orange",
        "purchase_price": 180,
        "mortgage_value": 90,
        "house_cost": 100,
        "rent_table": _rent(14, 70, 200, 550, 750, 950),
    },
    {
        "id": "property_new_york",
        "display_name": "New York Avenue",
        "group_id": "orange",
        "purchase_price": 200,
        "mortgage_value": 100,
        "house_cost": 100,
        "rent_table": _rent(16, 80, 220, 600, 800, 1000),
    },
    {
        "id": "property_kentucky",
        "display_name": "Kentucky Avenue",
        "group_id": "red",
        "purchase_price": 220,
        "mortgage_value": 110,
        "house_cost": 150,
        "rent_table": _rent(22, 110, 330, 800, 975, 1150),
    },
    {
        "id": "property_indiana",
        "display_name": "Indiana Avenue",
        "group_id": "red",
        "purchase_price": 220,
        "mortgage_value": 110,
        "house_cost": 150,
        "rent_table": _rent(22, 110, 330, 800, 975, 1150),
    },
    {
        "id": "property_illinois",
        "display_name": "Illinois Avenue",
        "group_id": "red",
        "purchase_price": 240,
        "mortgage_value": 120,
        "house_cost": 150,
        "rent_table": _rent(24, 120, 360, 850, 1025, 1200),
    },
    {
        "id": "property_atlantic",
        "display_name": "Atlantic Avenue",
        "group_id": "yellow",
        "purchase_price": 260,
        "mortgage_value": 130,
        "house_cost": 150,
        "rent_table": _rent(26, 130, 390, 900, 1100, 1275),
    },
    {
        "id": "property_ventnor",
        "display_name": "Ventnor Avenue",
        "group_id": "yellow",
        "purchase_price": 260,
        "mortgage_value": 130,
        "house_cost": 150,
        "rent_table": _rent(26, 130, 390, 900, 1100, 1275),
    },
    {
        "id": "property_marvin_gardens",
        "display_name": "Marvin Gardens",
        "group_id": "yellow",
        "purchase_price": 280,
        "mortgage_value": 140,
        "house_cost": 150,
        "rent_table": _rent(28, 150, 450, 1000, 1200, 1400),
    },
    {
        "id": "property_pacific",
        "display_name": "Pacific Avenue",
        "group_id": "green",
        "purchase_price": 300,
        "mortgage_value": 150,
        "house_cost": 200,
        "rent_table": _rent(26, 130, 390, 900, 1100, 1275),
    },
    {
        "id": "property_north_carolina",
        "display_name": "North Carolina Avenue",
        "group_id": "green",
        "purchase_price": 300,
        "mortgage_value": 150,
        "house_cost": 200,
        "rent_table": _rent(26, 130, 390, 900, 1100, 1275),
    },
    {
        "id": "property_pennsylvania",
        "display_name": "Pennsylvania Avenue",
        "group_id": "green",
        "purchase_price": 320,
        "mortgage_value": 160,
        "house_cost": 200,
        "rent_table": _rent(28, 150, 450, 1000, 1200, 1400),
    },
    {
        "id": "property_park_place",
        "display_name": "Park Place",
        "group_id": "dark_blue",
        "purchase_price": 350,
        "mortgage_value": 175,
        "house_cost": 200,
        "rent_table": _rent(35, 175, 500, 1100, 1300, 1500),
    },
    {
        "id": "property_boardwalk",
        "display_name": "Boardwalk",
        "group_id": "dark_blue",
        "purchase_price": 400,
        "mortgage_value": 200,
        "house_cost": 200,
        "rent_table": _rent(50, 200, 600, 1400, 1700, 2000),
    },
)

_RAILROAD_DEFINITIONS: tuple[dict[str, Any], ...] = (
    {
        "id": "property_rr_1",
        "display_name": "Reading Railroad",
        "purchase_price": 200,
        "mortgage_value": 100,
    },
    {
        "id": "property_rr_2",
        "display_name": "Pennsylvania Railroad",
        "purchase_price": 200,
        "mortgage_value": 100,
    },
    {
        "id": "property_rr_3",
        "display_name": "B. & O. Railroad",
        "purchase_price": 200,
        "mortgage_value": 100,
    },
    {
        "id": "property_rr_4",
        "display_name": "Short Line",
        "purchase_price": 200,
        "mortgage_value": 100,
    },
)

_UTILITY_DEFINITIONS: tuple[dict[str, Any], ...] = (
    {
        "id": "property_electric_company",
        "display_name": "Electric Company",
        "purchase_price": 150,
        "mortgage_value": 75,
    },
    {
        "id": "property_water_works",
        "display_name": "Water Works",
        "purchase_price": 150,
        "mortgage_value": 75,
    },
)


def classicStreetTemplate(
    definition: dict[str, Any],
    *,
    owner_player_id: str | None = None,
    houses: int = 0,
    has_hotel: bool = False,
    is_mortgaged: bool = False,
    is_tradable: bool = True,
) -> dict[str, Any]:
    house_cost = definition["house_cost"]
    return {
        "id": definition["id"],
        "display_name": definition["display_name"],
        "category": "street",
        "group_id": definition["group_id"],
        "owner_player_id": owner_player_id,
        "purchase_price": definition["purchase_price"],
        "mortgage_value": definition["mortgage_value"],
        "house_cost": house_cost,
        "hotel_cost": house_cost,
        "houses": houses,
        "has_hotel": has_hotel,
        "is_mortgaged": is_mortgaged,
        "is_tradable": is_tradable,
        "rent_table": dict(definition["rent_table"]),
    }


def classicRailroadTemplate(
    definition: dict[str, Any],
    *,
    owner_player_id: str | None = None,
    is_mortgaged: bool = False,
    is_tradable: bool = True,
) -> dict[str, Any]:
    return {
        "id": definition["id"],
        "display_name": definition["display_name"],
        "category": "railroad",
        "group_id": "railroad",
        "owner_player_id": owner_player_id,
        "purchase_price": definition["purchase_price"],
        "mortgage_value": definition["mortgage_value"],
        "houses": 0,
        "has_hotel": False,
        "is_mortgaged": is_mortgaged,
        "is_tradable": is_tradable,
        "rent_table": dict(_RAILROAD_RENT),
    }


def classicUtilityTemplate(
    definition: dict[str, Any],
    *,
    owner_player_id: str | None = None,
    is_mortgaged: bool = False,
    is_tradable: bool = True,
) -> dict[str, Any]:
    return {
        "id": definition["id"],
        "display_name": definition["display_name"],
        "category": "utility",
        "group_id": "utility",
        "owner_player_id": owner_player_id,
        "purchase_price": definition["purchase_price"],
        "mortgage_value": definition["mortgage_value"],
        "houses": 0,
        "has_hotel": False,
        "is_mortgaged": is_mortgaged,
        "is_tradable": is_tradable,
        "rent_table": dict(_UTILITY_RENT),
    }


def classicAllProperties(
    *,
    owners: dict[str, str | None] | None = None,
) -> list[dict[str, Any]]:
    """Return all 28 classic purchasable properties; unowned by default."""
    owners = owners or {}
    props: list[dict[str, Any]] = []
    for definition in _STREET_DEFINITIONS:
        props.append(
            classicStreetTemplate(
                definition,
                owner_player_id=owners.get(definition["id"]),
            )
        )
    for definition in _RAILROAD_DEFINITIONS:
        props.append(
            classicRailroadTemplate(
                definition,
                owner_player_id=owners.get(definition["id"]),
            )
        )
    for definition in _UTILITY_DEFINITIONS:
        props.append(
            classicUtilityTemplate(
                definition,
                owner_player_id=owners.get(definition["id"]),
            )
        )
    return props
