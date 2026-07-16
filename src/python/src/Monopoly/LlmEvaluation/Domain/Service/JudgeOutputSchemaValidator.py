"""Structural validation for Judge output JSON per 06_output_schema.md."""

from __future__ import annotations

from typing import Any

from Monopoly.LlmEvaluation.Domain.Model.JudgeEnums import (
    REQUIRED_OUTPUT_SECTIONS,
    CompetitiveClassification,
    ConfidenceLevel,
    EvidenceSource,
    ExecutionStatus,
    RuntimeExecutionMode,
    StaticAnalysisControlMode,
)


def validateJudgeOutputStructure(outputDict: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if not isinstance(outputDict, dict):
        return ["Output must be a JSON object"]

    missingSections = [section for section in REQUIRED_OUTPUT_SECTIONS if section not in outputDict]
    errors.extend(f"Missing output section: {section}" for section in missingSections)

    extraTopLevelKeys = sorted(set(outputDict.keys()) - set(REQUIRED_OUTPUT_SECTIONS))
    errors.extend(f"Unexpected top-level key: {key}" for key in extraTopLevelKeys)

    errors.extend(_validateCompetitiveClassification(outputDict.get("competitive_classification")))
    errors.extend(_validateCompetitiveEvaluation(outputDict.get("competitive_evaluation")))
    errors.extend(_validateSupportingEvidence(outputDict.get("supporting_evidence")))
    errors.extend(_validateStaticAnalysisResultStructure(outputDict.get("static_analysis_result")))
    errors.extend(_validateDecisionPatternAnalysis(outputDict.get("decision_pattern_analysis")))
    errors.extend(_validateConfidenceAssessment(outputDict.get("confidence_assessment")))
    errors.extend(_validateFinalSummary(outputDict.get("final_summary")))

    return errors


def _validateCompetitiveClassification(value: Any) -> list[str]:
    path = "competitive_classification"
    errors: list[str] = []
    if not isinstance(value, dict):
        return [f"{path} must be an object"]
    classification = value.get("classification")
    if classification not in {item.value for item in CompetitiveClassification}:
        errors.append(f"{path}.classification is invalid")
    if "score" in value and value["score"] is not None and not isinstance(value["score"], (int, float)):
        errors.append(f"{path}.score must be a number or null")
    if "confidence" in value and value["confidence"] is not None:
        if value["confidence"] not in {item.value for item in ConfidenceLevel}:
            errors.append(f"{path}.confidence is invalid")
    if "metadata" in value and value["metadata"] is not None and not isinstance(value["metadata"], dict):
        errors.append(f"{path}.metadata must be an object")
    return errors


def _validateCompetitiveEvaluation(value: Any) -> list[str]:
    path = "competitive_evaluation"
    errors: list[str] = []
    if not isinstance(value, dict):
        return [f"{path} must be an object"]
    if not isinstance(value.get("summary"), str):
        errors.append(f"{path}.summary must be a string")
    for field in ("immediate_effects", "long_term_effects", "affected_players", "key_findings"):
        if not isinstance(value.get(field), list):
            errors.append(f"{path}.{field} must be an array")
    if "metadata" in value and value["metadata"] is not None and not isinstance(value["metadata"], dict):
        errors.append(f"{path}.metadata must be an object")
    return errors


def _validateSupportingEvidence(value: Any) -> list[str]:
    path = "supporting_evidence"
    errors: list[str] = []
    if not isinstance(value, dict):
        return [f"{path} must be an object"]
    for field in (
        "board_state_evidence",
        "trade_information_evidence",
        "game_configuration_evidence",
        "static_algorithm_evidence",
    ):
        if not isinstance(value.get(field), list):
            errors.append(f"{path}.{field} must be an array")
    if "metadata" in value and value["metadata"] is not None and not isinstance(value["metadata"], dict):
        errors.append(f"{path}.metadata must be an object")
    return errors


def _validateStaticAnalysisResultStructure(value: Any) -> list[str]:
    path = "static_analysis_result"
    errors: list[str] = []
    if not isinstance(value, dict):
        return [f"{path} must be an object"]

    if value.get("requested_mode") not in {item.value for item in StaticAnalysisControlMode}:
        errors.append(f"{path}.requested_mode is invalid")
    if value.get("execution_mode") not in {item.value for item in RuntimeExecutionMode}:
        errors.append(f"{path}.execution_mode is invalid")
    if value.get("execution_status") not in {item.value for item in ExecutionStatus}:
        errors.append(f"{path}.execution_status is invalid")

    evidenceSource = value.get("evidence_source")
    if evidenceSource is not None and evidenceSource not in {item.value for item in EvidenceSource}:
        errors.append(f"{path}.evidence_source is invalid")

    for field in ("fallback_attempted", "competitive_evaluation_used_static_evidence"):
        if not isinstance(value.get(field), bool):
            errors.append(f"{path}.{field} must be a boolean")

    if not isinstance(value.get("dependency_versions"), dict):
        errors.append(f"{path}.dependency_versions must be an object")
    if not isinstance(value.get("limitations"), list):
        errors.append(f"{path}.limitations must be an array")
    if not isinstance(value.get("errors"), list):
        errors.append(f"{path}.errors must be an array")
    generated = value.get("generated_static_algorithm_evidence")
    if not isinstance(generated, list):
        errors.append(f"{path}.generated_static_algorithm_evidence must be an array")

    if value.get("execution_mode") == RuntimeExecutionMode.NO_STATIC_ANALYSIS.value:
        if evidenceSource is not None:
            errors.append(f"{path}.evidence_source must be null for NO_STATIC_ANALYSIS")
        if value.get("algorithm_id") is not None:
            errors.append(f"{path}.algorithm_id must be null for NO_STATIC_ANALYSIS")
        if value.get("algorithm_version") is not None:
            errors.append(f"{path}.algorithm_version must be null for NO_STATIC_ANALYSIS")

    if "metadata" in value and value["metadata"] is not None and not isinstance(value["metadata"], dict):
        errors.append(f"{path}.metadata must be an object")
    return errors


def _validateDecisionPatternAnalysis(value: Any) -> list[str]:
    path = "decision_pattern_analysis"
    errors: list[str] = []
    if not isinstance(value, dict):
        return [f"{path} must be an object"]
    if not isinstance(value.get("summary"), str):
        errors.append(f"{path}.summary must be a string")
    for field in ("matched_patterns", "unmatched_patterns"):
        if field in value and value[field] is not None:
            errors.extend(_validatePatternItems(value[field], f"{path}.{field}"))
        elif field == "matched_patterns" and not isinstance(value.get(field), list):
            errors.append(f"{path}.matched_patterns must be an array")
    if "metadata" in value and value["metadata"] is not None and not isinstance(value["metadata"], dict):
        errors.append(f"{path}.metadata must be an object")
    return errors


def _validatePatternItems(items: Any, path: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(items, list):
        return [f"{path} must be an array"]
    for index, item in enumerate(items):
        itemPath = f"{path}[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{itemPath} must be an object")
            continue
        if not isinstance(item.get("pattern_id"), str):
            errors.append(f"{itemPath}.pattern_id must be a string")
        if not isinstance(item.get("summary"), str):
            errors.append(f"{itemPath}.summary must be a string")
    return errors


def _validateConfidenceAssessment(value: Any) -> list[str]:
    path = "confidence_assessment"
    errors: list[str] = []
    if not isinstance(value, dict):
        return [f"{path} must be an object"]
    if value.get("overall_confidence") not in {item.value for item in ConfidenceLevel}:
        errors.append(f"{path}.overall_confidence is invalid")
    for field in ("confidence_factors", "limitations"):
        if not isinstance(value.get(field), list):
            errors.append(f"{path}.{field} must be an array")
    if "metadata" in value and value["metadata"] is not None and not isinstance(value["metadata"], dict):
        errors.append(f"{path}.metadata must be an object")
    return errors


def _validateFinalSummary(value: Any) -> list[str]:
    path = "final_summary"
    errors: list[str] = []
    if not isinstance(value, dict):
        return [f"{path} must be an object"]
    if not isinstance(value.get("summary"), str):
        errors.append(f"{path}.summary must be a string")
    if not isinstance(value.get("highlights"), list):
        errors.append(f"{path}.highlights must be an array")
    if "metadata" in value and value["metadata"] is not None and not isinstance(value["metadata"], dict):
        errors.append(f"{path}.metadata must be an object")
    return errors
