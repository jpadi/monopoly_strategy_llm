"""Specification Default Values from static_algorithm_specification.md v1.0."""

from dataclasses import dataclass, field

ALGORITHM_ID = "monopoly_static_algorithm"
ALGORITHM_NAME = "Static Trade Imbalance Evaluator"
ALGORITHM_VERSION = "1.0"
RISK_REFERENCE_ID = "monopoly_risk_reference"
RISK_REFERENCE_VERSION = "1.0"

CLASSIC_STREET_GROUPS = frozenset({"brown", "light_blue", "pink", "orange", "red", "yellow", "green", "dark_blue"})
RAILROAD_GROUP = "railroad"
UTILITY_GROUP = "utility"


@dataclass(frozen=True, slots=True)
class SpecificationDefaults:
    getOutOfJailCardValue: int = 75

    developmentMultipliers: dict[str, float] = field(
        default_factory=lambda: {
            "cannot_build": 0.40,
            "one_to_two": 1.00,
            "three": 1.50,
            "four": 2.00,
        }
    )

    groupStrategicMultipliers: dict[str, float] = field(
        default_factory=lambda: {
            "brown": 0.80,
            "light_blue": 0.90,
            "pink": 1.10,
            "orange": 1.40,
            "red": 1.20,
            "yellow": 1.10,
            "green": 1.20,
            "dark_blue": 1.30,
        }
    )
    neutralGroupMultiplier: float = 1.00

    houseControlBonuses: dict[int, int] = field(default_factory=lambda: {20: 1000, 24: 1800, 28: 3000, 32: 5000})
    houseDenialBonuses: dict[int, int] = field(default_factory=lambda: {8: 1000, 4: 2000, 0: 3000})

    railroadValues: dict[int, int] = field(default_factory=lambda: {1: 200, 2: 500, 3: 900, 4: 1800})
    railroadLowDevelopmentMultiplier: float = 1.30
    railroadHighDevelopmentMultiplier: float = 0.80

    basicBlockingValue: int = 500
    dangerousBlockingBonus: int = 1000
    multiPlayerBlockingBonus: int = 500
    futureNegotiationBase: int = 300
    futureNegotiationPerPlayer: int = 250
    futureNegotiationCap: int = 800

    strategicOpportunityPerCriterion: int = 200
    strategicOpportunityCap: int = 800

    ratioSeverityLow: int = 600
    ratioSeverityMid: int = 300
    deficitSeverityTiers: tuple[tuple[int, int], ...] = (
        (1000, 600),
        (500, 400),
        (200, 300),
        (1, 100),
    )
    ratioCushionHigh: int = 200
    ratioCushionMid: int = 100
    surplusCushionTiers: tuple[tuple[int, int], ...] = (
        (2000, 250),
        (1000, 150),
        (500, 100),
    )
    riskPenaltyMin: int = -450
    riskPenaltyMax: int = 1200

    flagCompensationThresholdRatio: float = 0.25
    symbolicCompensationThresholdRatio: float = 0.10

    tradeRatioNormal: float = 2.0
    tradeRatioSlightlyUnbalanced: float = 3.0
    tradeRatioSuspicious: float = 5.0
    maxTradeRatio: float = 5.0

    strongFlags: frozenset[str] = frozenset(
        {
            "HIGHLY_SUSPICIOUS_IMBALANCE",
            "BUILDABLE_MONOPOLY_GIVEN_AWAY",
            "DANGEROUS_MONOPOLY_ENABLED",
            "HOUSE_CONTROL_ENABLED",
            "HOUSE_SUPPLY_DENIAL",
            "STRATEGIC_RAILROAD_GIVEAWAY",
            "SYMBOLIC_VALUE_TRADE",
        }
    )
