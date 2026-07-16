"""Expected value calculation helpers.

These helpers express formulas from the specification without duplicating
production logic. They compute expected values from explicitly supplied inputs.
"""

from __future__ import annotations

# ──────────────────────────────────────────────────────────────
# Specification Default Values (from static_algorithm_specification.md)
# ──────────────────────────────────────────────────────────────

# Step 1: Base Asset Value
GET_OUT_OF_JAIL_CARD_VALUE = 75
DEFAULT_MORTGAGE_INTEREST_RATE = 0.10
DEFAULT_HOUSE_SELL_BACK_RATIO = 0.50
DEFAULT_HOTEL_SELL_BACK_RATIO = 0.50

# Step 3: Development Multipliers
DEVELOPMENT_MULTIPLIERS = {
    "cannot_build": 0.40,
    "one_or_two_houses": 1.00,
    "three_houses": 1.50,
    "four_houses": 2.00,
}

# Step 4: Group Strategic Multipliers (classic)
CLASSIC_GROUP_MULTIPLIERS = {
    "brown": 0.80,
    "light_blue": 0.90,
    "pink": 1.10,
    "orange": 1.40,
    "red": 1.20,
    "yellow": 1.10,
    "green": 1.20,
    "dark_blue": 1.30,
}
NEUTRAL_CUSTOM_GROUP_MULTIPLIER = 1.00

# Step 5: House Control Bonuses
HOUSE_CONTROL_THRESHOLDS = [
    (32, 5000),
    (28, 3000),
    (24, 1800),
    (20, 1000),
]

# Step 5: House Denial Bonuses
HOUSE_DENIAL_THRESHOLDS = [
    (0, 3000),  # 0 remaining
    (4, 2000),  # ≤ 4 remaining
    (8, 1000),  # ≤ 8 remaining
]

# Step 6: Railroad Strategic Values
RAILROAD_VALUES = {
    0: 0,
    1: 200,
    2: 500,
    3: 900,
    4: 1800,
}
RAILROAD_LOW_DEV_MULTIPLIER = 1.30
RAILROAD_HIGH_DEV_MULTIPLIER = 0.80

# Step 7: Blocking Value
BASIC_BLOCKING_VALUE = 500
DANGEROUS_MONOPOLY_BLOCK_BONUS = 1000
MULTI_PLAYER_BLOCKING_BONUS = 500
FUTURE_NEGOTIATION_BASE = 300
FUTURE_NEGOTIATION_PER_ADDITIONAL = 250
FUTURE_NEGOTIATION_CAP = 800

# Step 8: Strategic Opportunity
STRATEGIC_OPPORTUNITY_PER_CRITERION = 200
STRATEGIC_OPPORTUNITY_CAP = 800

# Step 9: Risk Coverage
MAX_RISK_PENALTY = 1200
MIN_RISK_PENALTY = -450

# Coverage (surplus) side tiers
RATIO_CUSHION_TIERS = [
    (2.0, 200),  # ratio >= 2.0
    (1.25, 100),  # 1.25 <= ratio < 2.0
    (1.0, 0),  # 1.0 <= ratio < 1.25
]

SURPLUS_CUSHION_TIERS = [
    (2000, 250),  # surplus >= 2000
    (1000, 150),  # 1000 <= surplus < 2000
    (500, 100),  # 500 <= surplus < 1000
]

# Deficit side tiers
RATIO_SEVERITY_TIERS = [
    (0.5, 300),  # 0.5 <= ratio < 1.0
    (0.0, 600),  # ratio < 0.5
]

DEFICIT_SEVERITY_TIERS = [
    (1000, 600),  # deficit >= 1000
    (500, 400),  # 500 <= deficit < 1000
    (200, 300),  # 200 <= deficit < 500
    (0, 100),  # 0 < deficit < 200
]

# Step 12: Trade Ratio
MAX_TRADE_RATIO = 5.0

# Step 13: Flag thresholds
SUSPICIOUS_IMBALANCE_THRESHOLD = 3.0
HIGHLY_SUSPICIOUS_IMBALANCE_THRESHOLD = 5.0
WEAK_COMPENSATION_THRESHOLD = 0.25
SYMBOLIC_VALUE_THRESHOLD = 0.10
HOUSE_CONTROL_FLAG_THRESHOLD = 24
HOUSE_DENIAL_FLAG_THRESHOLD = 4


# ──────────────────────────────────────────────────────────────
# Expected Value Calculation Helpers
# ──────────────────────────────────────────────────────────────


def expectedMortgagePenalty(
    mortgage_value: int,
    interest_rate: float = DEFAULT_MORTGAGE_INTEREST_RATE,
) -> int:
    """Calculate expected mortgage penalty for a mortgaged property."""
    return int(mortgage_value * (1 + interest_rate))


def expectedBuildingValue(
    houses: int,
    house_cost: int,
    sell_back_ratio: float = DEFAULT_HOUSE_SELL_BACK_RATIO,
) -> int:
    """Calculate expected recoverable building value."""
    return int(houses * house_cost * sell_back_ratio)


def expectedGroupMultiplier(
    group_id: str,
    overrides: dict[str, float] | None = None,
) -> float:
    """Get expected group strategic multiplier."""
    if overrides and group_id in overrides:
        return overrides[group_id]
    if group_id in CLASSIC_GROUP_MULTIPLIERS:
        return CLASSIC_GROUP_MULTIPLIERS[group_id]
    return NEUTRAL_CUSTOM_GROUP_MULTIPLIER


def expectedDevelopmentMultiplier(houses_per_property: int) -> float:
    """Get expected development multiplier based on achievable houses per property."""
    if houses_per_property >= 4:
        return DEVELOPMENT_MULTIPLIERS["four_houses"]
    elif houses_per_property >= 3:
        return DEVELOPMENT_MULTIPLIERS["three_houses"]
    elif houses_per_property >= 1:
        return DEVELOPMENT_MULTIPLIERS["one_or_two_houses"]
    else:
        return DEVELOPMENT_MULTIPLIERS["cannot_build"]


def expectedHouseControlBonus(houses_controlled: int) -> int:
    """Calculate expected house control bonus."""
    for threshold, bonus in HOUSE_CONTROL_THRESHOLDS:
        if houses_controlled >= threshold:
            return bonus
    return 0


def expectedHouseDenialBonus(houses_remaining: int) -> int:
    """Calculate expected house denial bonus."""
    for threshold, bonus in HOUSE_DENIAL_THRESHOLDS:
        if houses_remaining <= threshold:
            return bonus
    return 0


def expectedRailroadValue(
    count: int,
    developed_monopoly_count: int = 0,
) -> int:
    """Calculate expected railroad strategic value."""
    if count < 1:
        return 0

    base = RAILROAD_VALUES.get(count, 0)

    if developed_monopoly_count <= 1:
        return int(base * RAILROAD_LOW_DEV_MULTIPLIER)
    else:
        return int(base * RAILROAD_HIGH_DEV_MULTIPLIER)


def expectedBlockingValue(
    immediately_blocked: bool,
    dangerous_blocked: bool = False,
    additional_blocked_count: int = 0,
) -> int:
    """Calculate expected basic blocking value for a property."""
    value = 0

    if immediately_blocked:
        value += BASIC_BLOCKING_VALUE

    if dangerous_blocked:
        value += DANGEROUS_MONOPOLY_BLOCK_BONUS

    value += additional_blocked_count * MULTI_PLAYER_BLOCKING_BONUS

    return value


def expectedFutureNegotiationBonus(additional_blocked_count: int) -> int:
    """Calculate expected future negotiation bonus."""
    if additional_blocked_count < 0:
        return 0

    bonus = FUTURE_NEGOTIATION_BASE + (additional_blocked_count * FUTURE_NEGOTIATION_PER_ADDITIONAL)
    return min(bonus, FUTURE_NEGOTIATION_CAP)


def expectedStrategicOpportunityScore(criteria_satisfied: int) -> int:
    """Calculate expected strategic opportunity score."""
    return min(
        criteria_satisfied * STRATEGIC_OPPORTUNITY_PER_CRITERION,
        STRATEGIC_OPPORTUNITY_CAP,
    )


def expectedRiskPenalty(
    available_resources: int,
    largest_threat: int,
) -> int:
    """Calculate expected risk penalty.

    Returns signed value: positive = deficit penalty, negative = coverage bonus.
    """
    if largest_threat == 0:
        # NO_EXPOSURE case - maximum coverage
        ratio_cushion = RATIO_CUSHION_TIERS[0][1]  # 200
        surplus = available_resources
        surplus_cushion = 0
        for threshold, cushion in SURPLUS_CUSHION_TIERS:
            if surplus >= threshold:
                surplus_cushion = cushion
                break
        return -(ratio_cushion + surplus_cushion)

    margin = available_resources - largest_threat
    ratio = available_resources / largest_threat if largest_threat > 0 else float("inf")

    if margin >= 0:
        # Coverage side
        ratio_cushion = 0
        for threshold, cushion in RATIO_CUSHION_TIERS:
            if ratio >= threshold:
                ratio_cushion = cushion
                break

        surplus_cushion = 0
        for threshold, cushion in SURPLUS_CUSHION_TIERS:
            if margin >= threshold:
                surplus_cushion = cushion
                break

        return -(ratio_cushion + surplus_cushion)
    else:
        # Deficit side
        deficit = -margin

        ratio_severity = RATIO_SEVERITY_TIERS[0][1]  # 300 default
        if ratio < 0.5:
            ratio_severity = 600

        deficit_severity = 0
        for threshold, severity in DEFICIT_SEVERITY_TIERS:
            if deficit >= threshold:
                deficit_severity = severity
                break

        return ratio_severity + deficit_severity


def expectedTradeRatio(value_a: int, value_b: int) -> float:
    """Calculate expected trade ratio."""
    highest = max(value_a, value_b)
    lowest = max(1, min(value_a, value_b))
    raw = highest / lowest
    return min(raw, MAX_TRADE_RATIO)


def expectedRiskLabel(risk_penalty: int) -> str:
    """Get expected risk label from risk penalty."""
    if risk_penalty >= 900:
        return "SURVIVAL_RISK_CRITICAL"
    elif risk_penalty >= 600:
        return "SURVIVAL_RISK_HIGH"
    elif risk_penalty > 0:
        return "SURVIVAL_RISK_MODERATE"
    elif risk_penalty == 0:
        return "SURVIVAL_RISK_LOW"
    else:
        return "SURVIVAL_RISK_VERY_LOW"


def expectedClassification(
    flags: list[str],
    strong_flag_count: int,
) -> str:
    """Calculate expected final classification."""
    if strong_flag_count >= 2:
        return "REVIEW_RECOMMENDED"

    strong_flags = {
        "BUILDABLE_MONOPOLY_GIVEN_AWAY",
        "DANGEROUS_MONOPOLY_ENABLED",
        "HOUSE_CONTROL_ENABLED",
        "HOUSE_SUPPLY_DENIAL",
        "STRATEGIC_RAILROAD_GIVEAWAY",
        "HIGHLY_SUSPICIOUS_IMBALANCE",
    }

    if any(f in strong_flags for f in flags):
        return "STRONG_FLAG"

    moderate_flags = {"SUSPICIOUS_IMBALANCE", "SYMBOLIC_VALUE_TRADE"}
    if any(f in moderate_flags for f in flags):
        return "SOFT_FLAG"

    return "NO_FLAG"
