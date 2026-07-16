"""Canonical enum strings for the LLM Judge module."""

from Monopoly.Shared.Domain.StrEnumCompat import StrEnum


class StaticAnalysisControlMode(StrEnum):
    AUTO = "auto"
    REQUIRE_PROVIDED_EVIDENCE = "require_provided_evidence"
    ALLOW_LLM_FALLBACK = "allow_llm_fallback"
    DISABLE_STATIC_ANALYSIS = "disable_static_analysis"


class RuntimeExecutionMode(StrEnum):
    STATIC_EVIDENCE_PROVIDED = "STATIC_EVIDENCE_PROVIDED"
    LLM_STATIC_FALLBACK = "LLM_STATIC_FALLBACK"
    NO_STATIC_ANALYSIS = "NO_STATIC_ANALYSIS"


class EvidenceUsability(StrEnum):
    USABLE = "USABLE"
    PARTIALLY_USABLE = "PARTIALLY_USABLE"
    UNUSABLE = "UNUSABLE"


class EvidenceSource(StrEnum):
    SUPPLIED_STATIC_SOFTWARE = "SUPPLIED_STATIC_SOFTWARE"
    LLM_FALLBACK_GENERATED = "LLM_FALLBACK_GENERATED"


class ExecutionStatus(StrEnum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"
    NOT_REQUESTED = "NOT_REQUESTED"


class CompetitiveClassification(StrEnum):
    COMPETITIVELY_SOUND = "competitively_sound"
    SLIGHTLY_UNBALANCED = "slightly_unbalanced"
    SIGNIFICANTLY_UNBALANCED = "significantly_unbalanced"
    SEVERELY_UNBALANCED = "severely_unbalanced"


class ConfidenceLevel(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


CANONICAL_ALGORITHM_ID = "monopoly_static_algorithm"
CANONICAL_ALGORITHM_VERSION = "1.0"
CANONICAL_RISK_REFERENCE_ID = "monopoly_risk_reference"
CANONICAL_RISK_REFERENCE_VERSION = "1.0"

REQUIRED_INPUT_SECTIONS = (
    "metadata",
    "game_configuration",
    "board_state_before",
    "trade",
    "board_state_after",
)

REQUIRED_OUTPUT_SECTIONS = (
    "competitive_classification",
    "competitive_evaluation",
    "supporting_evidence",
    "static_analysis_result",
    "decision_pattern_analysis",
    "confidence_assessment",
    "final_summary",
)
