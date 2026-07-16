"""Build canonical Judge output dicts for deterministic tests."""

from __future__ import annotations

from typing import Any


def buildCanonicalJudgeOutput(
    *,
    requestedMode: str = "auto",
    executionMode: str = "NO_STATIC_ANALYSIS",
    evidenceSource: str | None = None,
    executionStatus: str = "NOT_REQUESTED",
    classification: str = "competitively_sound",
    overallConfidence: str = "high",
    fallbackAttempted: bool = False,
    generatedEvidence: list[dict[str, Any]] | None = None,
    limitations: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "competitive_classification": {
            "classification": classification,
            "score": None,
            "confidence": overallConfidence,
            "metadata": {},
        },
        "competitive_evaluation": {
            "summary": "Trade appears competitively balanced based on provided evidence.",
            "immediate_effects": [],
            "long_term_effects": [],
            "affected_players": [],
            "key_findings": [],
            "metadata": {},
        },
        "supporting_evidence": {
            "board_state_evidence": [],
            "trade_information_evidence": [],
            "game_configuration_evidence": [],
            "static_algorithm_evidence": [],
            "metadata": {},
        },
        "static_analysis_result": {
            "requested_mode": requestedMode,
            "execution_mode": executionMode,
            "evidence_source": evidenceSource,
            "algorithm_id": "monopoly_static_algorithm" if evidenceSource else None,
            "algorithm_version": "1.0" if evidenceSource else None,
            "dependency_versions": {"monopoly_risk_reference": "1.0"} if evidenceSource else {},
            "execution_status": executionStatus,
            "fallback_attempted": fallbackAttempted,
            "fallback_reason": "NO_USABLE_SUPPLIED_EVIDENCE" if fallbackAttempted else None,
            "competitive_evaluation_used_static_evidence": evidenceSource is not None,
            "generated_static_algorithm_evidence": generatedEvidence or [],
            "limitations": limitations or [],
            "errors": [],
            "metadata": {},
        },
        "decision_pattern_analysis": {
            "matched_patterns": [],
            "unmatched_patterns": [],
            "summary": "No decision patterns matched.",
            "metadata": {},
        },
        "confidence_assessment": {
            "overall_confidence": overallConfidence,
            "confidence_factors": ["Complete board state provided"],
            "limitations": limitations or [],
            "metadata": {},
        },
        "final_summary": {
            "summary": "Evaluation complete.",
            "highlights": [classification],
            "metadata": {},
        },
    }
