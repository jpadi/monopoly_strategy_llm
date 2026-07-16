"""Canonical Static Algorithm Evidence schema constants for Judge fallback validation."""

from __future__ import annotations

from typing import Any

# Evidence envelope (closed schema)
EVIDENCE_ENVELOPE_KEYS = frozenset(
    {
        "id",
        "algorithm_id",
        "algorithm_name",
        "algorithm_version",
        "purpose",
        "intermediate_calculations",
        "final_conclusions",
        "metadata",
        "statistics",
    }
)

CALCULATION_ITEM_REQUIRED_KEYS = frozenset(
    {
        "id",
        "calculation_type",
        "description",
        "status",
        "side",
        "subject",
        "input_references",
        "input_values",
        "sources",
        "intermediate_values",
        "result",
        "limitations",
        "missing_inputs",
    }
)

CALCULATION_ITEM_OPTIONAL_KEYS = frozenset(
    {
        "formula",
        "procedure",
        "unit",
        "dependent_calculation_ids",
        "metadata",
    }
)

CALCULATION_ITEM_ALLOWED_KEYS = CALCULATION_ITEM_REQUIRED_KEYS | CALCULATION_ITEM_OPTIONAL_KEYS

SUBJECT_KEYS = frozenset(
    {
        "player_ids",
        "property_ids",
        "group_ids",
        "trade_id",
        "transfer_ids",
    }
)

METADATA_KEYS = frozenset({"implementation_overrides", "specification_dependencies"})

SPECIFICATION_DEPENDENCY_KEYS = frozenset({"specification_id", "specification_version"})

STATISTICS_KEYS = frozenset({"calculation_count"})

FINAL_CONCLUSIONS_KEYS = frozenset(
    {
        "strategic_value",
        "trade_ratio",
        "flags",
        "risk_labels",
        "risk_warnings",
        "classification",
        "classification_calculation_id",
        "limitations",
    }
)

VALID_STATUSES = frozenset({"COMPLETE", "PARTIAL", "UNAVAILABLE", "ERROR"})
VALID_SIDES = frozenset({"before", "after", "delta", "trade"})
VALID_UNITS = frozenset(
    {
        "currency",
        "ratio",
        "percentage",
        "houses",
        "hotels",
        "development_level",
        "boolean",
        "classification",
    }
)

REGISTERED_CALCULATION_TYPES = frozenset(
    {
        "base_asset_value",
        "mortgage_capacity",
        "available_construction_budget",
        "monopoly_value",
        "house_control_bonus",
        "house_denial_bonus",
        "railroad_value",
        "blocking_value",
        "strategic_opportunity_score",
        "available_risk_resources",
        "landing_exposure",
        "repair_exposure",
        "largest_threat",
        "risk_margin",
        "coverage_ratio",
        "immediate_risk",
        "development_capability",
        "dangerous_monopoly_availability",
        "strategic_value",
        "trade_ratio",
        "final_static_classification",
    }
)

VALID_RISK_LABELS = frozenset(
    {
        "SURVIVAL_RISK_CRITICAL",
        "SURVIVAL_RISK_HIGH",
        "SURVIVAL_RISK_MODERATE",
        "SURVIVAL_RISK_LOW",
        "SURVIVAL_RISK_VERY_LOW",
    }
)

VALID_RISK_WARNINGS = frozenset(
    {
        "PLAYER_CANNOT_SURVIVE_ONE_LANDING",
        "PLAYER_CANNOT_COVER_REPAIR_EXPOSURE",
    }
)

VALID_AUTOMATIC_FLAGS = frozenset(
    {
        "BUILDABLE_MONOPOLY_GIVEN_AWAY",
        "DANGEROUS_MONOPOLY_ENABLED",
        "SYMBOLIC_VALUE_TRADE",
        "HOUSE_CONTROL_ENABLED",
        "HOUSE_SUPPLY_DENIAL",
        "STRATEGIC_RAILROAD_GIVEAWAY",
        "SUSPICIOUS_IMBALANCE",
        "HIGHLY_SUSPICIOUS_IMBALANCE",
    }
)

VALID_FINAL_CLASSIFICATIONS = frozenset(
    {
        "NO_FLAG",
        "SOFT_FLAG",
        "STRONG_FLAG",
        "REVIEW_RECOMMENDED",
    }
)

CANONICAL_ALGORITHM_NAME = "Static Trade Imbalance Evaluator"
CANONICAL_PURPOSE = "trade ratio calculation and competitive advantage calculation"


def isJsonPrimitive(value: Any) -> bool:
    return value is None or isinstance(value, (bool, int, float, str))
