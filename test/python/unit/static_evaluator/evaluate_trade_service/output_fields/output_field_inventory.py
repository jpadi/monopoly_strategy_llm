"""Canonical Output Field Inventory.

This module defines the complete field inventory from the Static Algorithm Evidence
specification. Every canonical output field must appear here.

Structure:
- FieldDefinition: Data class for each field's metadata
- FIELD_INVENTORY: Complete inventory of all output fields
- Utility functions for field enumeration

Normative Sources:
- docs/llm_evaluator/04_static_algorithm_specification.md (Evidence contract)
- docs/static_evaluator/static_algorithm_specification.md (Calculation-type registry)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class FieldCategory(str, Enum):
    """Field category classification."""

    ENVELOPE = "envelope"
    CALCULATION_ITEM = "calculation_item"
    SUBJECT = "subject"
    INPUT_VALUES = "input_values"
    SOURCES = "sources"
    INTERMEDIATE_VALUES = "intermediate_values"
    FINAL_CONCLUSIONS = "final_conclusions"
    METADATA = "metadata"
    STATISTICS = "statistics"


class FieldType(str, Enum):
    """Expected field type."""

    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    ENUM = "enum"
    NULL = "null"
    ANY = "any"


@dataclass(frozen=True)
class FieldDefinition:
    """Definition of a canonical output field."""

    path: str
    category: FieldCategory
    field_type: FieldType
    description: str
    required: bool = True
    calculation_types: frozenset[str] = frozenset()
    enum_values: frozenset[str] = frozenset()
    example_value: str | None = None


# ==============================================================================
# EVIDENCE ENVELOPE FIELDS
# ==============================================================================

ENVELOPE_FIELDS: dict[str, FieldDefinition] = {
    "id": FieldDefinition(
        path="id",
        category=FieldCategory.ENVELOPE,
        field_type=FieldType.STRING,
        description="Unique stable identifier for the evidence object",
        example_value="evidence_static_trade_imbalance_001",
    ),
    "algorithm_id": FieldDefinition(
        path="algorithm_id",
        category=FieldCategory.ENVELOPE,
        field_type=FieldType.STRING,
        description="Machine-readable algorithm identifier (must equal specification_id)",
        example_value="monopoly_static_algorithm",
    ),
    "algorithm_name": FieldDefinition(
        path="algorithm_name",
        category=FieldCategory.ENVELOPE,
        field_type=FieldType.STRING,
        description="Human-readable algorithm name",
        example_value="Static Trade Imbalance Evaluator",
    ),
    "algorithm_version": FieldDefinition(
        path="algorithm_version",
        category=FieldCategory.ENVELOPE,
        field_type=FieldType.STRING,
        description="Implemented specification_version",
        example_value="1.0",
    ),
    "purpose": FieldDefinition(
        path="purpose",
        category=FieldCategory.ENVELOPE,
        field_type=FieldType.STRING,
        description="Canonical purpose string",
        example_value="trade ratio calculation and competitive advantage calculation",
    ),
    "intermediate_calculations": FieldDefinition(
        path="intermediate_calculations",
        category=FieldCategory.ENVELOPE,
        field_type=FieldType.ARRAY,
        description="Array of Intermediate Calculation Items",
    ),
    "final_conclusions": FieldDefinition(
        path="final_conclusions",
        category=FieldCategory.ENVELOPE,
        field_type=FieldType.OBJECT,
        description="Final deterministic conclusions object",
    ),
    "metadata": FieldDefinition(
        path="metadata",
        category=FieldCategory.ENVELOPE,
        field_type=FieldType.OBJECT,
        description="Evidence-level metadata",
    ),
    "statistics": FieldDefinition(
        path="statistics",
        category=FieldCategory.ENVELOPE,
        field_type=FieldType.OBJECT,
        description="Calculation statistics",
    ),
}

# ==============================================================================
# INTERMEDIATE CALCULATION ITEM COMMON FIELDS
# ==============================================================================

CALCULATION_ITEM_FIELDS: dict[str, FieldDefinition] = {
    "item.id": FieldDefinition(
        path="intermediate_calculations[*].id",
        category=FieldCategory.CALCULATION_ITEM,
        field_type=FieldType.STRING,
        description="Unique stable calculation identifier",
        example_value="calc_001",
    ),
    "item.calculation_type": FieldDefinition(
        path="intermediate_calculations[*].calculation_type",
        category=FieldCategory.CALCULATION_ITEM,
        field_type=FieldType.ENUM,
        description="Canonical calculation type from the registry",
        enum_values=frozenset(
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
        ),
    ),
    "item.description": FieldDefinition(
        path="intermediate_calculations[*].description",
        category=FieldCategory.CALCULATION_ITEM,
        field_type=FieldType.STRING,
        description="Human-readable calculation description",
    ),
    "item.status": FieldDefinition(
        path="intermediate_calculations[*].status",
        category=FieldCategory.CALCULATION_ITEM,
        field_type=FieldType.ENUM,
        description="Calculation completion status",
        enum_values=frozenset({"COMPLETE", "PARTIAL", "UNAVAILABLE", "ERROR"}),
    ),
    "item.side": FieldDefinition(
        path="intermediate_calculations[*].side",
        category=FieldCategory.CALCULATION_ITEM,
        field_type=FieldType.ENUM,
        description="Board state side",
        enum_values=frozenset({"before", "after", "delta", "trade"}),
    ),
    "item.subject": FieldDefinition(
        path="intermediate_calculations[*].subject",
        category=FieldCategory.CALCULATION_ITEM,
        field_type=FieldType.OBJECT,
        description="Entity identifiers involved in calculation",
    ),
    "item.input_references": FieldDefinition(
        path="intermediate_calculations[*].input_references",
        category=FieldCategory.CALCULATION_ITEM,
        field_type=FieldType.ARRAY,
        description="Machine-readable input object references",
    ),
    "item.input_values": FieldDefinition(
        path="intermediate_calculations[*].input_values",
        category=FieldCategory.CALCULATION_ITEM,
        field_type=FieldType.OBJECT,
        description="Factual values read from input",
    ),
    "item.sources": FieldDefinition(
        path="intermediate_calculations[*].sources",
        category=FieldCategory.CALCULATION_ITEM,
        field_type=FieldType.OBJECT,
        description="Provenance of configurable/default values",
    ),
    "item.formula": FieldDefinition(
        path="intermediate_calculations[*].formula",
        category=FieldCategory.CALCULATION_ITEM,
        field_type=FieldType.STRING,
        description="Mathematical formula (when formula-based)",
        required=False,
    ),
    "item.procedure": FieldDefinition(
        path="intermediate_calculations[*].procedure",
        category=FieldCategory.CALCULATION_ITEM,
        field_type=FieldType.STRING,
        description="Deterministic procedure description",
        required=False,
    ),
    "item.intermediate_values": FieldDefinition(
        path="intermediate_calculations[*].intermediate_values",
        category=FieldCategory.CALCULATION_ITEM,
        field_type=FieldType.OBJECT,
        description="Intermediate values for result reproduction",
    ),
    "item.result": FieldDefinition(
        path="intermediate_calculations[*].result",
        category=FieldCategory.CALCULATION_ITEM,
        field_type=FieldType.ANY,
        description="Calculation result",
    ),
    "item.unit": FieldDefinition(
        path="intermediate_calculations[*].unit",
        category=FieldCategory.CALCULATION_ITEM,
        field_type=FieldType.ENUM,
        description="Result unit or semantic type",
        enum_values=frozenset(
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
        ),
        required=False,
    ),
    "item.limitations": FieldDefinition(
        path="intermediate_calculations[*].limitations",
        category=FieldCategory.CALCULATION_ITEM,
        field_type=FieldType.ARRAY,
        description="Known limitations affecting interpretation",
    ),
    "item.missing_inputs": FieldDefinition(
        path="intermediate_calculations[*].missing_inputs",
        category=FieldCategory.CALCULATION_ITEM,
        field_type=FieldType.ARRAY,
        description="Required inputs that were unavailable",
    ),
    "item.dependent_calculation_ids": FieldDefinition(
        path="intermediate_calculations[*].dependent_calculation_ids",
        category=FieldCategory.CALCULATION_ITEM,
        field_type=FieldType.ARRAY,
        description="IDs of calculations consuming this result",
    ),
    "item.metadata": FieldDefinition(
        path="intermediate_calculations[*].metadata",
        category=FieldCategory.CALCULATION_ITEM,
        field_type=FieldType.OBJECT,
        description="Optional implementation-specific metadata",
        required=False,
    ),
}

# ==============================================================================
# SUBJECT FIELDS
# ==============================================================================

SUBJECT_FIELDS: dict[str, FieldDefinition] = {
    "subject.player_ids": FieldDefinition(
        path="intermediate_calculations[*].subject.player_ids",
        category=FieldCategory.SUBJECT,
        field_type=FieldType.ARRAY,
        description="Player identifiers involved",
    ),
    "subject.property_ids": FieldDefinition(
        path="intermediate_calculations[*].subject.property_ids",
        category=FieldCategory.SUBJECT,
        field_type=FieldType.ARRAY,
        description="Property identifiers involved",
    ),
    "subject.group_ids": FieldDefinition(
        path="intermediate_calculations[*].subject.group_ids",
        category=FieldCategory.SUBJECT,
        field_type=FieldType.ARRAY,
        description="Group identifiers involved",
    ),
    "subject.trade_id": FieldDefinition(
        path="intermediate_calculations[*].subject.trade_id",
        category=FieldCategory.SUBJECT,
        field_type=FieldType.STRING,
        description="Trade identifier",
        required=False,
    ),
    "subject.transfer_ids": FieldDefinition(
        path="intermediate_calculations[*].subject.transfer_ids",
        category=FieldCategory.SUBJECT,
        field_type=FieldType.ARRAY,
        description="Transfer identifiers involved",
    ),
}

# ==============================================================================
# FINAL CONCLUSIONS FIELDS
# ==============================================================================

FINAL_CONCLUSIONS_FIELDS: dict[str, FieldDefinition] = {
    "conclusions.strategic_value": FieldDefinition(
        path="final_conclusions.strategic_value",
        category=FieldCategory.FINAL_CONCLUSIONS,
        field_type=FieldType.OBJECT,
        description="Strategic value per player",
    ),
    "conclusions.strategic_value.player.value": FieldDefinition(
        path="final_conclusions.strategic_value[player].value",
        category=FieldCategory.FINAL_CONCLUSIONS,
        field_type=FieldType.NUMBER,
        description="Player's strategic value",
    ),
    "conclusions.strategic_value.player.calculation_id": FieldDefinition(
        path="final_conclusions.strategic_value[player].calculation_id",
        category=FieldCategory.FINAL_CONCLUSIONS,
        field_type=FieldType.STRING,
        description="Supporting calculation ID",
    ),
    "conclusions.trade_ratio": FieldDefinition(
        path="final_conclusions.trade_ratio",
        category=FieldCategory.FINAL_CONCLUSIONS,
        field_type=FieldType.OBJECT,
        description="Trade ratio conclusion",
    ),
    "conclusions.trade_ratio.value": FieldDefinition(
        path="final_conclusions.trade_ratio.value",
        category=FieldCategory.FINAL_CONCLUSIONS,
        field_type=FieldType.NUMBER,
        description="Published trade ratio value",
    ),
    "conclusions.trade_ratio.calculation_id": FieldDefinition(
        path="final_conclusions.trade_ratio.calculation_id",
        category=FieldCategory.FINAL_CONCLUSIONS,
        field_type=FieldType.STRING,
        description="Supporting calculation ID",
    ),
    "conclusions.flags": FieldDefinition(
        path="final_conclusions.flags",
        category=FieldCategory.FINAL_CONCLUSIONS,
        field_type=FieldType.OBJECT,
        description="Generated flags",
    ),
    "conclusions.flags.values": FieldDefinition(
        path="final_conclusions.flags.values",
        category=FieldCategory.FINAL_CONCLUSIONS,
        field_type=FieldType.ARRAY,
        description="Flag values array",
        enum_values=frozenset(
            {
                "SUSPICIOUS_IMBALANCE",
                "HIGHLY_SUSPICIOUS_IMBALANCE",
                "BUILDABLE_MONOPOLY_GIVEN_AWAY",
                "DANGEROUS_MONOPOLY_ENABLED",
                "SYMBOLIC_VALUE_TRADE",
                "HOUSE_CONTROL_ENABLED",
                "HOUSE_SUPPLY_DENIAL",
                "STRATEGIC_RAILROAD_GIVEAWAY",
            }
        ),
    ),
    "conclusions.flags.calculation_id": FieldDefinition(
        path="final_conclusions.flags.calculation_id",
        category=FieldCategory.FINAL_CONCLUSIONS,
        field_type=FieldType.STRING,
        description="Supporting calculation ID",
    ),
    "conclusions.risk_labels": FieldDefinition(
        path="final_conclusions.risk_labels",
        category=FieldCategory.FINAL_CONCLUSIONS,
        field_type=FieldType.OBJECT,
        description="Risk labels per player",
    ),
    "conclusions.risk_labels.player.before": FieldDefinition(
        path="final_conclusions.risk_labels[player].before",
        category=FieldCategory.FINAL_CONCLUSIONS,
        field_type=FieldType.STRING,
        description="Before-trade risk label",
        enum_values=frozenset(
            {
                "SURVIVAL_RISK_VERY_LOW",
                "SURVIVAL_RISK_LOW",
                "SURVIVAL_RISK_MODERATE",
                "SURVIVAL_RISK_HIGH",
                "SURVIVAL_RISK_CRITICAL",
            }
        ),
    ),
    "conclusions.risk_labels.player.after": FieldDefinition(
        path="final_conclusions.risk_labels[player].after",
        category=FieldCategory.FINAL_CONCLUSIONS,
        field_type=FieldType.STRING,
        description="After-trade risk label",
    ),
    "conclusions.risk_labels.player.before_calculation_id": FieldDefinition(
        path="final_conclusions.risk_labels[player].before_calculation_id",
        category=FieldCategory.FINAL_CONCLUSIONS,
        field_type=FieldType.STRING,
        description="Supporting before calculation ID",
    ),
    "conclusions.risk_labels.player.after_calculation_id": FieldDefinition(
        path="final_conclusions.risk_labels[player].after_calculation_id",
        category=FieldCategory.FINAL_CONCLUSIONS,
        field_type=FieldType.STRING,
        description="Supporting after calculation ID",
    ),
    "conclusions.risk_warnings": FieldDefinition(
        path="final_conclusions.risk_warnings",
        category=FieldCategory.FINAL_CONCLUSIONS,
        field_type=FieldType.OBJECT,
        description="Risk warnings",
    ),
    "conclusions.risk_warnings.values": FieldDefinition(
        path="final_conclusions.risk_warnings.values",
        category=FieldCategory.FINAL_CONCLUSIONS,
        field_type=FieldType.ARRAY,
        description="Warning values array",
        enum_values=frozenset(
            {
                "PLAYER_CANNOT_SURVIVE_ONE_LANDING",
                "PLAYER_CANNOT_COVER_REPAIR_EXPOSURE",
            }
        ),
    ),
    "conclusions.risk_warnings.calculation_ids": FieldDefinition(
        path="final_conclusions.risk_warnings.calculation_ids",
        category=FieldCategory.FINAL_CONCLUSIONS,
        field_type=FieldType.ARRAY,
        description="Supporting calculation IDs",
    ),
    "conclusions.classification": FieldDefinition(
        path="final_conclusions.classification",
        category=FieldCategory.FINAL_CONCLUSIONS,
        field_type=FieldType.ENUM,
        description="Final static classification",
        enum_values=frozenset(
            {
                "NO_FLAG",
                "SOFT_FLAG",
                "STRONG_FLAG",
                "REVIEW_RECOMMENDED",
            }
        ),
    ),
    "conclusions.classification_calculation_id": FieldDefinition(
        path="final_conclusions.classification_calculation_id",
        category=FieldCategory.FINAL_CONCLUSIONS,
        field_type=FieldType.STRING,
        description="Supporting classification calculation ID",
    ),
}

# ==============================================================================
# METADATA FIELDS
# ==============================================================================

METADATA_FIELDS: dict[str, FieldDefinition] = {
    "metadata.implementation_overrides": FieldDefinition(
        path="metadata.implementation_overrides",
        category=FieldCategory.METADATA,
        field_type=FieldType.ARRAY,
        description="Implementation overrides to specification defaults",
    ),
    "metadata.specification_dependencies": FieldDefinition(
        path="metadata.specification_dependencies",
        category=FieldCategory.METADATA,
        field_type=FieldType.ARRAY,
        description="Specification dependencies (e.g., Risk Reference)",
    ),
    "metadata.specification_dependencies.specification_id": FieldDefinition(
        path="metadata.specification_dependencies[*].specification_id",
        category=FieldCategory.METADATA,
        field_type=FieldType.STRING,
        description="Dependency specification identifier",
        example_value="monopoly_risk_reference",
    ),
    "metadata.specification_dependencies.specification_version": FieldDefinition(
        path="metadata.specification_dependencies[*].specification_version",
        category=FieldCategory.METADATA,
        field_type=FieldType.STRING,
        description="Dependency specification version",
        example_value="1.0",
    ),
}

# ==============================================================================
# STATISTICS FIELDS
# ==============================================================================

STATISTICS_FIELDS: dict[str, FieldDefinition] = {
    "statistics.calculation_count": FieldDefinition(
        path="statistics.calculation_count",
        category=FieldCategory.STATISTICS,
        field_type=FieldType.NUMBER,
        description="Total number of calculations produced",
    ),
}

# ==============================================================================
# CALCULATION-TYPE SPECIFIC INTERMEDIATE VALUES
# ==============================================================================

BASE_ASSET_VALUE_INTERMEDIATE: dict[str, FieldDefinition] = {
    "base_asset_value.cash_received": FieldDefinition(
        path="intermediate_values.cash_received",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Cash received by player",
        calculation_types=frozenset({"base_asset_value"}),
    ),
    "base_asset_value.property_value": FieldDefinition(
        path="intermediate_values.property_value",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Total property value received",
        calculation_types=frozenset({"base_asset_value"}),
    ),
    "base_asset_value.building_value": FieldDefinition(
        path="intermediate_values.building_value",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Total building liquidation value",
        calculation_types=frozenset({"base_asset_value"}),
    ),
    "base_asset_value.card_value": FieldDefinition(
        path="intermediate_values.card_value",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Total card value",
        calculation_types=frozenset({"base_asset_value"}),
    ),
    "base_asset_value.line_items": FieldDefinition(
        path="intermediate_values.line_items",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.ARRAY,
        description="Per-transfer line items",
        calculation_types=frozenset({"base_asset_value"}),
    ),
    "base_asset_value.line_item.type": FieldDefinition(
        path="intermediate_values.line_items[*].type",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.ENUM,
        description="Line item type",
        enum_values=frozenset({"cash", "property", "card"}),
        calculation_types=frozenset({"base_asset_value"}),
    ),
    "base_asset_value.line_item.transfer_id": FieldDefinition(
        path="intermediate_values.line_items[*].transfer_id",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.STRING,
        description="Transfer identifier",
        calculation_types=frozenset({"base_asset_value"}),
    ),
    "base_asset_value.line_item.property_id": FieldDefinition(
        path="intermediate_values.line_items[*].property_id",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.STRING,
        description="Property identifier",
        calculation_types=frozenset({"base_asset_value"}),
        required=False,
    ),
    "base_asset_value.line_item.printed_value": FieldDefinition(
        path="intermediate_values.line_items[*].printed_value",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Property printed value",
        calculation_types=frozenset({"base_asset_value"}),
        required=False,
    ),
    "base_asset_value.line_item.building_value": FieldDefinition(
        path="intermediate_values.line_items[*].building_value",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Building liquidation value for property",
        calculation_types=frozenset({"base_asset_value"}),
        required=False,
    ),
}

MONOPOLY_VALUE_INTERMEDIATE: dict[str, FieldDefinition] = {
    "monopoly_value.completed_groups": FieldDefinition(
        path="intermediate_values.completed_groups",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.ARRAY,
        description="List of completed group IDs",
        calculation_types=frozenset({"monopoly_value"}),
    ),
    "monopoly_value.per_group_values": FieldDefinition(
        path="intermediate_values.per_group_values",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.ARRAY,
        description="Per-group monopoly value details",
        calculation_types=frozenset({"monopoly_value"}),
    ),
    "monopoly_value.total_monopoly_value": FieldDefinition(
        path="intermediate_values.total_monopoly_value",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Sum of all group monopoly values",
        calculation_types=frozenset({"monopoly_value"}),
    ),
}

TRADE_RATIO_INTERMEDIATE: dict[str, FieldDefinition] = {
    "trade_ratio.highest_strategic_value": FieldDefinition(
        path="intermediate_values.highest_strategic_value",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Higher of the two strategic values",
        calculation_types=frozenset({"trade_ratio"}),
    ),
    "trade_ratio.lowest_strategic_value": FieldDefinition(
        path="intermediate_values.lowest_strategic_value",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Lower of the two strategic values",
        calculation_types=frozenset({"trade_ratio"}),
    ),
    "trade_ratio.division_denominator": FieldDefinition(
        path="intermediate_values.division_denominator",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Denominator for ratio (max(1, lowest))",
        calculation_types=frozenset({"trade_ratio"}),
    ),
    "trade_ratio.raw_trade_ratio": FieldDefinition(
        path="intermediate_values.raw_trade_ratio",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Uncapped raw ratio",
        calculation_types=frozenset({"trade_ratio"}),
    ),
    "trade_ratio.maximum_trade_ratio": FieldDefinition(
        path="intermediate_values.maximum_trade_ratio",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Maximum allowed ratio (cap)",
        calculation_types=frozenset({"trade_ratio"}),
    ),
    "trade_ratio.published_trade_ratio": FieldDefinition(
        path="intermediate_values.published_trade_ratio",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Final capped ratio",
        calculation_types=frozenset({"trade_ratio"}),
    ),
}

IMMEDIATE_RISK_INTERMEDIATE: dict[str, FieldDefinition] = {
    "immediate_risk.available_risk_resources": FieldDefinition(
        path="intermediate_values.available_risk_resources",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Available risk resources",
        calculation_types=frozenset({"immediate_risk"}),
    ),
    "immediate_risk.largest_threat": FieldDefinition(
        path="intermediate_values.largest_threat",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Largest single-landing threat",
        calculation_types=frozenset({"immediate_risk"}),
    ),
    "immediate_risk.risk_margin": FieldDefinition(
        path="intermediate_values.risk_margin",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Resources minus threat",
        calculation_types=frozenset({"immediate_risk"}),
    ),
    "immediate_risk.coverage_ratio": FieldDefinition(
        path="intermediate_values.coverage_ratio",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Resources / Threat ratio",
        calculation_types=frozenset({"immediate_risk"}),
    ),
    "immediate_risk.coverage_ratio_tier": FieldDefinition(
        path="intermediate_values.coverage_ratio_tier",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.STRING,
        description="Coverage ratio tier",
        calculation_types=frozenset({"immediate_risk"}),
    ),
    "immediate_risk.coverage_ratio_component": FieldDefinition(
        path="intermediate_values.coverage_ratio_component",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Risk component from ratio",
        calculation_types=frozenset({"immediate_risk"}),
    ),
    "immediate_risk.surplus_or_deficit_amount": FieldDefinition(
        path="intermediate_values.surplus_or_deficit_amount",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Surplus or deficit amount",
        calculation_types=frozenset({"immediate_risk"}),
    ),
    "immediate_risk.surplus_or_deficit_tier": FieldDefinition(
        path="intermediate_values.surplus_or_deficit_tier",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.STRING,
        description="Surplus/deficit tier",
        calculation_types=frozenset({"immediate_risk"}),
    ),
    "immediate_risk.surplus_or_deficit_component": FieldDefinition(
        path="intermediate_values.surplus_or_deficit_component",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Risk component from surplus/deficit",
        calculation_types=frozenset({"immediate_risk"}),
    ),
    "immediate_risk.uncapped_risk_penalty": FieldDefinition(
        path="intermediate_values.uncapped_risk_penalty",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Uncapped risk penalty",
        calculation_types=frozenset({"immediate_risk"}),
    ),
    "immediate_risk.minimum_risk_penalty": FieldDefinition(
        path="intermediate_values.minimum_risk_penalty",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Minimum allowed penalty",
        calculation_types=frozenset({"immediate_risk"}),
    ),
    "immediate_risk.maximum_risk_penalty": FieldDefinition(
        path="intermediate_values.maximum_risk_penalty",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Maximum allowed penalty",
        calculation_types=frozenset({"immediate_risk"}),
    ),
    "immediate_risk.bounded_risk_penalty": FieldDefinition(
        path="intermediate_values.bounded_risk_penalty",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Final bounded penalty",
        calculation_types=frozenset({"immediate_risk"}),
    ),
    "immediate_risk.risk_label": FieldDefinition(
        path="intermediate_values.risk_label",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.ENUM,
        description="Risk severity label",
        enum_values=frozenset(
            {
                "SURVIVAL_RISK_VERY_LOW",
                "SURVIVAL_RISK_LOW",
                "SURVIVAL_RISK_MODERATE",
                "SURVIVAL_RISK_HIGH",
                "SURVIVAL_RISK_CRITICAL",
            }
        ),
        calculation_types=frozenset({"immediate_risk"}),
    ),
    "immediate_risk.warnings": FieldDefinition(
        path="intermediate_values.warnings",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.ARRAY,
        description="Risk warnings generated",
        enum_values=frozenset(
            {
                "PLAYER_CANNOT_SURVIVE_ONE_LANDING",
                "PLAYER_CANNOT_COVER_REPAIR_EXPOSURE",
            }
        ),
        calculation_types=frozenset({"immediate_risk"}),
    ),
}

FINAL_CLASSIFICATION_INTERMEDIATE: dict[str, FieldDefinition] = {
    "classification.automatic_rules": FieldDefinition(
        path="intermediate_values.automatic_rules",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.ARRAY,
        description="Automatic flag rule evaluations",
        calculation_types=frozenset({"final_static_classification"}),
    ),
    "classification.automatic_rule.rule": FieldDefinition(
        path="intermediate_values.automatic_rules[*].rule",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.STRING,
        description="Rule identifier",
        calculation_types=frozenset({"final_static_classification"}),
    ),
    "classification.automatic_rule.predicate_result": FieldDefinition(
        path="intermediate_values.automatic_rules[*].predicate_result",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.BOOLEAN,
        description="Whether rule predicate matched",
        calculation_types=frozenset({"final_static_classification"}),
    ),
    "classification.automatic_rule.flag_generated": FieldDefinition(
        path="intermediate_values.automatic_rules[*].flag_generated",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.STRING,
        description="Flag generated (if any)",
        required=False,
        calculation_types=frozenset({"final_static_classification"}),
    ),
    "classification.flags_before_initiator_adjustment": FieldDefinition(
        path="intermediate_values.flags_before_initiator_adjustment",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.ARRAY,
        description="Flags before initiator adjustment",
        calculation_types=frozenset({"final_static_classification"}),
    ),
    "classification.flags_after_initiator_adjustment": FieldDefinition(
        path="intermediate_values.flags_after_initiator_adjustment",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.ARRAY,
        description="Flags after initiator adjustment",
        calculation_types=frozenset({"final_static_classification"}),
    ),
    "classification.initiator_rule_evaluated": FieldDefinition(
        path="intermediate_values.initiator_rule_evaluated",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.BOOLEAN,
        description="Whether initiator adjustment was evaluated",
        calculation_types=frozenset({"final_static_classification"}),
    ),
    "classification.initiating_player_id": FieldDefinition(
        path="intermediate_values.initiating_player_id",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.STRING,
        description="Trade initiator player ID",
        calculation_types=frozenset({"final_static_classification"}),
    ),
    "classification.apparent_overpayer": FieldDefinition(
        path="intermediate_values.apparent_overpayer",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.STRING,
        description="Player with lower strategic value",
        calculation_types=frozenset({"final_static_classification"}),
    ),
    "classification.initiator_adjustment_applied": FieldDefinition(
        path="intermediate_values.initiator_adjustment_applied",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.BOOLEAN,
        description="Whether adjustment was applied",
        calculation_types=frozenset({"final_static_classification"}),
    ),
    "classification.strong_flags": FieldDefinition(
        path="intermediate_values.strong_flags",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.ARRAY,
        description="Strong flags present",
        calculation_types=frozenset({"final_static_classification"}),
    ),
    "classification.strong_flag_count": FieldDefinition(
        path="intermediate_values.strong_flag_count",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Count of strong flags",
        calculation_types=frozenset({"final_static_classification"}),
    ),
    "classification.trade_ratio": FieldDefinition(
        path="intermediate_values.trade_ratio",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Trade ratio used for classification",
        calculation_types=frozenset({"final_static_classification"}),
    ),
    "classification.final_classification": FieldDefinition(
        path="intermediate_values.final_classification",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.STRING,
        description="Final classification value",
        calculation_types=frozenset({"final_static_classification"}),
    ),
}

STRATEGIC_VALUE_INTERMEDIATE: dict[str, FieldDefinition] = {
    "strategic_value.base_asset_value": FieldDefinition(
        path="intermediate_values.base_asset_value",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Base asset value component",
        calculation_types=frozenset({"strategic_value"}),
    ),
    "strategic_value.monopoly_value": FieldDefinition(
        path="intermediate_values.monopoly_value",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Monopoly value component",
        calculation_types=frozenset({"strategic_value"}),
    ),
    "strategic_value.house_control_bonus": FieldDefinition(
        path="intermediate_values.house_control_bonus",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="House control bonus component",
        calculation_types=frozenset({"strategic_value"}),
    ),
    "strategic_value.house_denial_bonus": FieldDefinition(
        path="intermediate_values.house_denial_bonus",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="House denial bonus component",
        calculation_types=frozenset({"strategic_value"}),
    ),
    "strategic_value.railroad_value": FieldDefinition(
        path="intermediate_values.railroad_value",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Railroad value component",
        calculation_types=frozenset({"strategic_value"}),
    ),
    "strategic_value.blocking_value": FieldDefinition(
        path="intermediate_values.blocking_value",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Blocking value component",
        calculation_types=frozenset({"strategic_value"}),
    ),
    "strategic_value.strategic_opportunity_value": FieldDefinition(
        path="intermediate_values.strategic_opportunity_value",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Strategic opportunity value component",
        calculation_types=frozenset({"strategic_value"}),
    ),
    "strategic_value.immediate_risk_change": FieldDefinition(
        path="intermediate_values.immediate_risk_change",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Immediate risk change (subtracted)",
        calculation_types=frozenset({"strategic_value"}),
    ),
    "strategic_value.floor_applied": FieldDefinition(
        path="intermediate_values.floor_applied",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.BOOLEAN,
        description="Whether minimum floor was applied",
        calculation_types=frozenset({"strategic_value"}),
    ),
}

# ==============================================================================
# SOURCE LABELS
# ==============================================================================

SOURCE_LABELS: frozenset[str] = frozenset(
    {
        "SPECIFICATION_DEFAULT",
        "CLASSIC_DEFAULT",
        "RISK_REFERENCE_DEFAULT",
        "GAME_CONFIGURATION",
        "GAME_CONFIGURATION_OVERRIDE",
        "BOARD_STATE_RENT_TABLE",
        "NEUTRAL_CUSTOM_GROUP_DEFAULT",
        "IMPLEMENTATION_OVERRIDE",
    }
)

# ==============================================================================
# CANONICAL CALCULATION TYPES
# ==============================================================================

CALCULATION_TYPES: frozenset[str] = frozenset(
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

# ==============================================================================
# CANONICAL STATUS VALUES
# ==============================================================================

STATUS_VALUES: frozenset[str] = frozenset(
    {
        "COMPLETE",
        "PARTIAL",
        "UNAVAILABLE",
        "ERROR",
    }
)

# ==============================================================================
# CANONICAL SIDE VALUES
# ==============================================================================

SIDE_VALUES: frozenset[str] = frozenset(
    {
        "before",
        "after",
        "delta",
        "trade",
    }
)

# ==============================================================================
# ADDITIONAL FIELD INVENTORY (nested result keys and coverage variants)
# ==============================================================================

ADDITIONAL_FIELD_INVENTORY: dict[str, FieldDefinition] = {
    "mortgage_capacity.result": FieldDefinition(
        path="intermediate_calculations[*].result",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Mortgage capacity result value",
        calculation_types=frozenset({"mortgage_capacity"}),
    ),
    "available_construction_budget.cash": FieldDefinition(
        path="intermediate_values.cash",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Cash component of construction budget",
        calculation_types=frozenset({"available_construction_budget"}),
    ),
    "development_capability.predicate": FieldDefinition(
        path="intermediate_values.predicate",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.STRING,
        description="Development capability predicate name",
        calculation_types=frozenset({"development_capability"}),
    ),
    "railroad_value.railroad_count": FieldDefinition(
        path="intermediate_values.railroad_count",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Count of railroads owned",
        calculation_types=frozenset({"railroad_value"}),
    ),
    "railroad_value.context_multiplier": FieldDefinition(
        path="intermediate_values.context_multiplier",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Context multiplier applied to railroad value",
        calculation_types=frozenset({"railroad_value"}),
    ),
    "blocking_value.per_property": FieldDefinition(
        path="intermediate_values.per_property",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.ARRAY,
        description="Per-property blocking value breakdown",
        calculation_types=frozenset({"blocking_value"}),
    ),
    "dangerous_monopoly_availability.dangerous_predicate": FieldDefinition(
        path="intermediate_values.dangerous_predicate",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.BOOLEAN,
        description="Dangerous monopoly availability predicate result",
        calculation_types=frozenset({"dangerous_monopoly_availability"}),
    ),
    "strategic_opportunity_score.criteria": FieldDefinition(
        path="intermediate_values.criteria",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.OBJECT,
        description="Strategic opportunity score criteria flags",
        calculation_types=frozenset({"strategic_opportunity_score"}),
    ),
    "available_risk_resources.mortgage_capacity": FieldDefinition(
        path="intermediate_values.mortgage_capacity",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Mortgage capacity component of risk resources",
        calculation_types=frozenset({"available_risk_resources"}),
    ),
    "landing_exposure.threat_property_id": FieldDefinition(
        path="intermediate_values.threat_property_id",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.STRING,
        description="Property ID of the landing threat",
        calculation_types=frozenset({"landing_exposure"}),
    ),
    "repair_exposure.repair_card_scenario": FieldDefinition(
        path="intermediate_values.repair_card_scenario",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.STRING,
        description="Repair card scenario identifier",
        calculation_types=frozenset({"repair_exposure"}),
    ),
    "largest_threat.landing_exposure": FieldDefinition(
        path="intermediate_values.landing_exposure",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Landing exposure component of largest threat",
        calculation_types=frozenset({"largest_threat"}),
    ),
    "risk_margin.surplus_amount": FieldDefinition(
        path="intermediate_values.surplus_amount",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.NUMBER,
        description="Surplus amount in risk margin calculation",
        calculation_types=frozenset({"risk_margin"}),
    ),
    "coverage_ratio.no_exposure": FieldDefinition(
        path="intermediate_values.no_exposure",
        category=FieldCategory.INTERMEDIATE_VALUES,
        field_type=FieldType.BOOLEAN,
        description="Whether player has zero landing exposure",
        calculation_types=frozenset({"coverage_ratio"}),
    ),
    "item.status.ERROR": FieldDefinition(
        path="intermediate_calculations[*].status",
        category=FieldCategory.CALCULATION_ITEM,
        field_type=FieldType.ENUM,
        description="ERROR status coverage",
        enum_values=frozenset({"ERROR"}),
    ),
    "item.status.UNAVAILABLE": FieldDefinition(
        path="intermediate_calculations[*].status",
        category=FieldCategory.CALCULATION_ITEM,
        field_type=FieldType.ENUM,
        description="UNAVAILABLE status coverage",
        enum_values=frozenset({"UNAVAILABLE"}),
    ),
    "item.status.PARTIAL": FieldDefinition(
        path="intermediate_calculations[*].status",
        category=FieldCategory.CALCULATION_ITEM,
        field_type=FieldType.ENUM,
        description="PARTIAL status coverage",
        enum_values=frozenset({"PARTIAL"}),
    ),
    "item.status.COMPLETE": FieldDefinition(
        path="intermediate_calculations[*].status",
        category=FieldCategory.CALCULATION_ITEM,
        field_type=FieldType.ENUM,
        description="COMPLETE status coverage",
        enum_values=frozenset({"COMPLETE"}),
    ),
    "item.side.before": FieldDefinition(
        path="intermediate_calculations[*].side",
        category=FieldCategory.CALCULATION_ITEM,
        field_type=FieldType.ENUM,
        description="Before side coverage",
        enum_values=frozenset({"before"}),
    ),
    "item.side.after": FieldDefinition(
        path="intermediate_calculations[*].side",
        category=FieldCategory.CALCULATION_ITEM,
        field_type=FieldType.ENUM,
        description="After side coverage",
        enum_values=frozenset({"after"}),
    ),
    "item.side.delta": FieldDefinition(
        path="intermediate_calculations[*].side",
        category=FieldCategory.CALCULATION_ITEM,
        field_type=FieldType.ENUM,
        description="Delta side coverage",
        enum_values=frozenset({"delta"}),
    ),
    "item.side.trade": FieldDefinition(
        path="intermediate_calculations[*].side",
        category=FieldCategory.CALCULATION_ITEM,
        field_type=FieldType.ENUM,
        description="Trade side coverage",
        enum_values=frozenset({"trade"}),
    ),
    "sources": FieldDefinition(
        path="intermediate_calculations[*].sources",
        category=FieldCategory.SOURCES,
        field_type=FieldType.OBJECT,
        description="Source label coverage across calculations",
    ),
}

# ==============================================================================
# COMPLETE FIELD INVENTORY
# ==============================================================================


def get_all_fields() -> dict[str, FieldDefinition]:
    """Return the complete field inventory."""
    all_fields: dict[str, FieldDefinition] = {}
    all_fields.update(ENVELOPE_FIELDS)
    all_fields.update(CALCULATION_ITEM_FIELDS)
    all_fields.update(SUBJECT_FIELDS)
    all_fields.update(FINAL_CONCLUSIONS_FIELDS)
    all_fields.update(METADATA_FIELDS)
    all_fields.update(STATISTICS_FIELDS)
    all_fields.update(BASE_ASSET_VALUE_INTERMEDIATE)
    all_fields.update(MONOPOLY_VALUE_INTERMEDIATE)
    all_fields.update(TRADE_RATIO_INTERMEDIATE)
    all_fields.update(IMMEDIATE_RISK_INTERMEDIATE)
    all_fields.update(FINAL_CLASSIFICATION_INTERMEDIATE)
    all_fields.update(STRATEGIC_VALUE_INTERMEDIATE)
    all_fields.update(ADDITIONAL_FIELD_INVENTORY)
    return all_fields


def get_fields_by_category(category: FieldCategory) -> dict[str, FieldDefinition]:
    """Return fields for a specific category."""
    return {k: v for k, v in get_all_fields().items() if v.category == category}


def get_required_fields() -> dict[str, FieldDefinition]:
    """Return all required fields."""
    return {k: v for k, v in get_all_fields().items() if v.required}


def get_total_field_count() -> int:
    """Return total count of canonical fields."""
    return len(get_all_fields())
