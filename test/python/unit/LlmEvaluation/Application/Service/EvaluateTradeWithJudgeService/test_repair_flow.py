"""Unit tests for Judge repair flow."""

from __future__ import annotations

import copy
import json

import pytest
from llmFixtureLoader import loadCanonicalFallbackEvidence, loadProviderResponseWithFallbackEvidence
from test_utilities.judge_output_builder import buildCanonicalJudgeOutput
from test_utilities.repo_paths import FIXTURE_ROOT, REPO_ROOT

from Monopoly.LlmEvaluation.Domain.Exception.LlmEvaluationErrors import (
    JudgeOutputSchemaViolationError,
    JudgeRepairFailureError,
)
from Monopoly.LlmEvaluation.Domain.Model.Runtime.ResolvedRuntimePlan import ResolvedRuntimePlan
from Monopoly.LlmEvaluation.Domain.Service.JudgeOutputValidator import JudgeOutputValidator
from Monopoly.LlmEvaluation.Domain.Service.JudgePromptBuilder import JudgePromptBuilder
from Monopoly.LlmEvaluation.Domain.Service.JudgeResponseParser import JudgeResponseParser
from Monopoly.LlmEvaluation.Domain.Service.SpecificationBundleBuilder import SpecificationBundleBuilder
from Monopoly.LlmEvaluation.Infrastructure.Json.JudgeRequestMapper import JudgeRequestMapper
from Monopoly.LlmEvaluation.Infrastructure.Specification.FileSystemSpecificationRepository import (
    FileSystemSpecificationRepository,
)

FALLBACK_PLAN = ResolvedRuntimePlan(
    requestedMode="auto",
    executionMode="LLM_STATIC_FALLBACK",
    evidenceSource="LLM_FALLBACK_GENERATED",
    algorithmId="monopoly_static_algorithm",
    algorithmVersion="1.0",
    dependencyVersions={"monopoly_risk_reference": "1.0"},
    expectedExecutionStatus="COMPLETE",
    fallbackAuthorized=True,
    fallbackRequired=True,
    fallbackAttempted=True,
    evidenceUsability=(),
    limitations=(),
    bundleRequired=True,
)


def _broken_fallback_output() -> dict:
    output = buildCanonicalJudgeOutput(
        executionMode="LLM_STATIC_FALLBACK",
        evidenceSource="LLM_FALLBACK_GENERATED",
        executionStatus="COMPLETE",
        fallbackAttempted=True,
        generatedEvidence=[
            {
                "id": "evidence_static_trade_imbalance_001",
                "algorithm_id": "monopoly_static_algorithm",
                "algorithm_name": "Static Trade Imbalance Evaluator",
                "algorithm_version": "1.0",
                "purpose": "trade ratio calculation and competitive advantage calculation",
                "intermediate_calculations": [
                    {
                        "id": "calc_001",
                        "calculation_type": "base_asset_value",
                        "description": "broken dependency",
                        "status": "COMPLETE",
                        "side": "trade",
                        "subject": {
                            "player_ids": ["player_a"],
                            "property_ids": [],
                            "group_ids": [],
                            "trade_id": "trade_balanced",
                            "transfer_ids": [],
                        },
                        "input_references": [],
                        "input_values": {},
                        "sources": {},
                        "formula": "x",
                        "procedure": None,
                        "intermediate_values": {},
                        "result": 1,
                        "unit": "currency",
                        "limitations": [],
                        "missing_inputs": [],
                        "dependent_calculation_ids": ["calc_missing"],
                        "metadata": {},
                    }
                ],
                "final_conclusions": {
                    "trade_ratio": {"value": 1.0, "calculation_id": "calc_missing"},
                    "classification": "NO_FLAG",
                    "classification_calculation_id": "calc_missing",
                    "flags": {"values": [], "calculation_id": "calc_missing"},
                    "risk_labels": {},
                    "risk_warnings": {"values": [], "calculation_ids": []},
                    "strategic_value": {},
                    "limitations": [],
                },
                "metadata": {
                    "implementation_overrides": [],
                    "specification_dependencies": [
                        {
                            "specification_id": "monopoly_risk_reference",
                            "specification_version": "1.0",
                        }
                    ],
                },
                "statistics": {"calculation_count": 1},
            }
        ],
    )
    return output


def _valid_fallback_output() -> dict:
    return loadProviderResponseWithFallbackEvidence("fallback_authorized")


def test_initial_broken_fallback_fails_validation():
    output = _broken_fallback_output()
    with pytest.raises(JudgeOutputSchemaViolationError) as exc_info:
        JudgeOutputValidator().validate(output, FALLBACK_PLAN)
    assert any("calc_missing" in error for error in exc_info.value.errors)
    assert any(record.code == "UNKNOWN_DEPENDENT_CALCULATION_ID" for record in exc_info.value.structuredErrors)


def test_repair_prompt_includes_invalid_output_and_structured_errors():
    invalid = _broken_fallback_output()
    with pytest.raises(JudgeOutputSchemaViolationError) as exc_info:
        JudgeOutputValidator().validate(invalid, FALLBACK_PLAN)

    payload = json.loads((FIXTURE_ROOT / "inputs/fallback_authorized.json").read_text(encoding="utf-8"))
    request = JudgeRequestMapper.fromDict(payload)
    repair_request = JudgePromptBuilder().build(
        request.evaluationInput,
        FALLBACK_PLAN,
        None,
        model="fake-model",
        repairErrors=exc_info.value.errors,
        repairStructuredErrors=exc_info.value.structuredErrors,
        repairInvalidOutput=invalid,
    )

    assert "### Invalid previous output (correct this object)" in repair_request.taskPrompt
    assert "calc_missing" in repair_request.taskPrompt
    assert "Structured validation errors" in repair_request.taskPrompt
    assert "docs/llm_evaluator/00_initial_prompt.md" in repair_request.taskPrompt
    assert "docs/llm_evaluator/06_output_schema.md" in repair_request.taskPrompt


def test_initial_non_json_triggers_repair(evaluate_trade_with_judge_service, fake_llm_client):
    payload = json.loads((FIXTURE_ROOT / "inputs/fallback_authorized.json").read_text(encoding="utf-8"))
    request = JudgeRequestMapper.fromDict(payload)
    fixed = _valid_fallback_output()
    fake_llm_client.activeScenarioId = "fallback_authorized"
    fake_llm_client.initialResponseText = "Output written to disk; read judge_output_response.json"
    fake_llm_client.repairResponseText = json.dumps(fixed)

    result = evaluate_trade_with_judge_service.execute(request)
    assert result.metadata.repairAttempted is True
    assert len(fake_llm_client.calls) == 2
    assert "Invalid previous response (non-JSON prose" in fake_llm_client.calls[1].taskPrompt


def test_parse_repair_writes_initial_validation_errors_artifact(
    evaluate_trade_with_judge_service,
    fake_llm_client,
    llm_evaluation_artifact_subpath,
):
    payload = json.loads((FIXTURE_ROOT / "inputs/fallback_authorized.json").read_text(encoding="utf-8"))
    request = JudgeRequestMapper.fromDict(payload)
    fixed = _valid_fallback_output()
    fake_llm_client.activeScenarioId = "fallback_authorized"
    fake_llm_client.initialResponseText = "Output written to disk; read judge_output_response.json"
    fake_llm_client.repairResponseText = json.dumps(fixed)

    evaluate_trade_with_judge_service.execute(request)

    errorsPath = llm_evaluation_artifact_subpath / "initial_validation_errors.json"
    assert errorsPath.is_file()
    payload = json.loads(errorsPath.read_text(encoding="utf-8"))
    assert payload["errors"]
    assert payload["structured_errors"]


def test_repair_prose_fails_with_domain_error(evaluate_trade_with_judge_service, fake_llm_client):
    payload = json.loads((FIXTURE_ROOT / "inputs/fallback_authorized.json").read_text(encoding="utf-8"))
    request = JudgeRequestMapper.fromDict(payload)
    broken = _broken_fallback_output()
    fake_llm_client.responsesByScenario["fallback_authorized"] = broken
    fake_llm_client.activeScenarioId = "fallback_authorized"
    fake_llm_client.repairResponseText = "Please read the file from disk and continue."

    with pytest.raises(JudgeRepairFailureError) as exc_info:
        evaluate_trade_with_judge_service.execute(request)
    assert exc_info.value.repairParseError is not None
    assert len(fake_llm_client.calls) == 2


def test_repair_valid_json_succeeds(evaluate_trade_with_judge_service, fake_llm_client):
    payload = json.loads((FIXTURE_ROOT / "inputs/fallback_authorized.json").read_text(encoding="utf-8"))
    request = JudgeRequestMapper.fromDict(payload)
    broken = _broken_fallback_output()
    fixed = _valid_fallback_output()
    fake_llm_client.responsesByScenario["fallback_authorized"] = broken
    fake_llm_client.activeScenarioId = "fallback_authorized"
    fake_llm_client.repairResponseText = json.dumps(fixed)

    result = evaluate_trade_with_judge_service.execute(request)
    assert result.metadata.repairAttempted is True
    assert result.metadata.repairCount == 1
    assert len(fake_llm_client.calls) == 2


def _fallback_output_with_evidence(evidence: dict) -> dict:
    return buildCanonicalJudgeOutput(
        executionMode="LLM_STATIC_FALLBACK",
        evidenceSource="LLM_FALLBACK_GENERATED",
        executionStatus="COMPLETE",
        fallbackAttempted=True,
        generatedEvidence=[evidence],
    )


def test_duplicate_calculation_ids_fail_validation():
    evidence = copy.deepcopy(loadCanonicalFallbackEvidence())
    duplicate = copy.deepcopy(evidence["intermediate_calculations"][0])
    evidence["intermediate_calculations"].append(duplicate)
    output = _fallback_output_with_evidence(evidence)
    with pytest.raises(JudgeOutputSchemaViolationError) as exc_info:
        JudgeOutputValidator().validate(output, FALLBACK_PLAN)
    assert any(record.code == "DUPLICATE_CALCULATION_ID" for record in exc_info.value.structuredErrors)


def test_self_dependency_fails_validation():
    evidence = copy.deepcopy(loadCanonicalFallbackEvidence())
    evidence["intermediate_calculations"][0]["dependent_calculation_ids"] = ["calc_001"]
    output = _fallback_output_with_evidence(evidence)
    with pytest.raises(JudgeOutputSchemaViolationError) as exc_info:
        JudgeOutputValidator().validate(output, FALLBACK_PLAN)
    assert any(record.code == "SELF_DEPENDENCY" for record in exc_info.value.structuredErrors)


def test_broken_final_conclusion_reference_fails_validation():
    evidence = copy.deepcopy(loadCanonicalFallbackEvidence())
    evidence["final_conclusions"]["trade_ratio"]["calculation_id"] = "calc_missing"
    output = _fallback_output_with_evidence(evidence)
    with pytest.raises(JudgeOutputSchemaViolationError) as exc_info:
        JudgeOutputValidator().validate(output, FALLBACK_PLAN)
    assert any(record.code == "UNKNOWN_FINAL_CONCLUSION_REFERENCE" for record in exc_info.value.structuredErrors)


def test_valid_reference_graph_passes_validation():
    evidence = loadCanonicalFallbackEvidence()
    output = _fallback_output_with_evidence(evidence)
    JudgeOutputValidator().validate(output, FALLBACK_PLAN)


def test_repair_still_broken_no_third_provider_call(evaluate_trade_with_judge_service, fake_llm_client):
    payload = json.loads((FIXTURE_ROOT / "inputs/fallback_authorized.json").read_text(encoding="utf-8"))
    request = JudgeRequestMapper.fromDict(payload)
    broken = _broken_fallback_output()
    fake_llm_client.responsesByScenario["fallback_authorized"] = broken
    fake_llm_client.activeScenarioId = "fallback_authorized"
    fake_llm_client.repairResponseText = json.dumps(broken)

    with pytest.raises(JudgeRepairFailureError) as exc_info:
        evaluate_trade_with_judge_service.execute(request)
    assert exc_info.value.repairValidationErrors
    assert len(fake_llm_client.calls) == 2


def test_repair_fenced_json_succeeds(evaluate_trade_with_judge_service, fake_llm_client):
    payload = json.loads((FIXTURE_ROOT / "inputs/fallback_authorized.json").read_text(encoding="utf-8"))
    request = JudgeRequestMapper.fromDict(payload)
    broken = _broken_fallback_output()
    fixed = _valid_fallback_output()
    fake_llm_client.responsesByScenario["fallback_authorized"] = broken
    fake_llm_client.activeScenarioId = "fallback_authorized"
    fake_llm_client.repairResponseText = f"```json\n{json.dumps(fixed)}\n```"

    result = evaluate_trade_with_judge_service.execute(request)
    assert result.metadata.repairAttempted is True
    assert len(fake_llm_client.calls) == 2


def test_repair_preserves_fallback_bundle():
    repository = FileSystemSpecificationRepository(docsRoot=REPO_ROOT)
    runtime_plan = FALLBACK_PLAN
    payload = json.loads((FIXTURE_ROOT / "inputs/fallback_authorized.json").read_text(encoding="utf-8"))
    request = JudgeRequestMapper.fromDict(payload)
    bundle = SpecificationBundleBuilder(specificationRepository=repository).build(runtime_plan)
    original = JudgePromptBuilder().build(request.evaluationInput, runtime_plan, bundle, model="fake-model")
    invalid = _broken_fallback_output()
    with pytest.raises(JudgeOutputSchemaViolationError) as exc_info:
        JudgeOutputValidator().validate(invalid, runtime_plan)
    repair = JudgePromptBuilder().build(
        request.evaluationInput,
        runtime_plan,
        bundle,
        model="fake-model",
        repairErrors=exc_info.value.errors,
        repairStructuredErrors=exc_info.value.structuredErrors,
        repairInvalidOutput=invalid,
    )
    assert original.instructionFilePaths == repair.instructionFilePaths
    assert original.attachmentFilePaths == repair.attachmentFilePaths
    assert "docs/static_evaluator/static_algorithm_specification.md" in repair.attachmentFilePaths
    assert "### Invalid previous output (correct this object)" in repair.taskPrompt


def test_parser_accepts_single_fenced_json_object():
    payload = {"competitive_classification": {"classification": "competitively_sound"}}
    parsed = JudgeResponseParser().parse(f"```json\n{json.dumps(payload)}\n```")
    assert parsed["competitive_classification"]["classification"] == "competitively_sound"
