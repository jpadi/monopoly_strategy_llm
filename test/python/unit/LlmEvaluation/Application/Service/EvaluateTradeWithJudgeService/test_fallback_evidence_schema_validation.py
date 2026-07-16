"""Schema conformance tests for LLM fallback Static Algorithm Evidence."""

from __future__ import annotations

import copy
import json
from typing import Any

import pytest
from llmFixtureLoader import loadCanonicalFallbackEvidence
from test_utilities.judge_output_builder import buildCanonicalJudgeOutput
from test_utilities.repo_paths import FIXTURE_ROOT

from Monopoly.LlmEvaluation.Domain.Exception.LlmEvaluationErrors import (
    JudgeOutputSchemaViolationError,
)
from Monopoly.LlmEvaluation.Domain.Model.Runtime.ResolvedRuntimePlan import (
    ResolvedRuntimePlan,
)
from Monopoly.LlmEvaluation.Domain.Service.GeneratedStaticAlgorithmEvidenceValidator import (
    GeneratedStaticAlgorithmEvidenceValidator,
)
from Monopoly.LlmEvaluation.Domain.Service.JudgeOutputValidator import (
    JudgeOutputValidator,
)
from Monopoly.StaticEvaluation.Application.Query.EvaluateTrade.EvaluateTradeQuery import (
    EvaluateTradeQuery,
)
from Monopoly.StaticEvaluation.Application.Query.EvaluateTrade.EvaluateTradeService import (
    EvaluateTradeService,
)
from Monopoly.StaticEvaluation.Domain.Model.Algorithm.StaticTradeEvaluator import (
    StaticTradeEvaluator,
)
from Monopoly.StaticEvaluation.Infrastructure.Json.EvaluationInputMapper import (
    EvaluationInputMapper,
)
from Monopoly.StaticEvaluation.Infrastructure.Json.EvidenceSerializer import (
    EvidenceSerializer,
)


@pytest.fixture
def evidence_validator() -> GeneratedStaticAlgorithmEvidenceValidator:
    return GeneratedStaticAlgorithmEvidenceValidator()


@pytest.fixture
def judge_output_validator() -> JudgeOutputValidator:
    return JudgeOutputValidator()


@pytest.fixture
def valid_fallback_evidence() -> dict[str, Any]:
    return loadCanonicalFallbackEvidence()


@pytest.fixture
def fallback_runtime_plan() -> ResolvedRuntimePlan:
    return ResolvedRuntimePlan(
        requestedMode="auto",
        executionMode="LLM_STATIC_FALLBACK",
        evidenceSource="LLM_FALLBACK_GENERATED",
        algorithmId="monopoly_static_algorithm",
        algorithmVersion="1.0",
        dependencyVersions={"monopoly_risk_reference": "1.0"},
        expectedExecutionStatus="COMPLETE",
        fallbackAuthorized=True,
        fallbackRequired=False,
        fallbackAttempted=True,
        evidenceUsability=(),
        limitations=(),
        bundleRequired=True,
    )


def _buildFallbackJudgeOutput(evidence: dict[str, Any], *, execution_status: str = "COMPLETE") -> dict[str, Any]:
    return buildCanonicalJudgeOutput(
        requestedMode="auto",
        executionMode="LLM_STATIC_FALLBACK",
        evidenceSource="LLM_FALLBACK_GENERATED",
        executionStatus=execution_status,
        fallbackAttempted=True,
        generatedEvidence=[evidence],
    )


def test_valid_fallback_evidence_passes_validation(
    evidence_validator: GeneratedStaticAlgorithmEvidenceValidator,
    judge_output_validator: JudgeOutputValidator,
    valid_fallback_evidence: dict[str, Any],
    fallback_runtime_plan: ResolvedRuntimePlan,
) -> None:
    assert evidence_validator.validate(valid_fallback_evidence) == []
    output = _buildFallbackJudgeOutput(valid_fallback_evidence)
    judge_output_validator.validate(output, fallback_runtime_plan)


def test_deterministic_evaluator_evidence_passes_fallback_schema(
    evidence_validator: GeneratedStaticAlgorithmEvidenceValidator,
) -> None:
    eval_input = json.loads((FIXTURE_ROOT / "inputs/fallback_authorized.json").read_text())["evaluation_input"]
    evaluation_input = EvaluationInputMapper.fromDict(eval_input)
    service = EvaluateTradeService(evaluator=StaticTradeEvaluator())
    evidence = EvidenceSerializer.toDict(service.execute(EvaluateTradeQuery(evaluationInput=evaluation_input)))
    assert evidence_validator.validate(evidence) == []


@pytest.mark.parametrize(
    ("mutator", "expected_fragment"),
    [
        (
            lambda e: e["metadata"].update({"dependency_versions": {"monopoly_risk_reference": "1.0"}}),
            "unknown fields",
        ),
        (
            lambda e: e["statistics"].pop("calculation_count") or e["statistics"].update({"calculations_performed": 3}),
            "calculation_count",
        ),
        (
            lambda e: (
                e["final_conclusions"]
                .setdefault("risk_labels", {})
                .update(
                    {
                        "player_a": {
                            "before": "STRONG_COVERAGE",
                            "after": "STRONG_COVERAGE",
                        }
                    }
                )
            ),
            "invalid risk label",
        ),
        (
            lambda e: e["intermediate_calculations"][0].__setitem__("calculation_type", "mortgage_cap"),
            "calculation_type invalid",
        ),
        (
            lambda e: e["intermediate_calculations"][0].__setitem__("side", "BEFORE"),
            "side invalid",
        ),
        (
            lambda e: e["intermediate_calculations"][0].__setitem__("status", "DONE"),
            "status invalid",
        ),
        (
            lambda e: e["intermediate_calculations"][0].__setitem__("unit", "money"),
            "unit invalid",
        ),
        (
            lambda e: e["intermediate_calculations"][0]["subject"].pop("player_ids"),
            "missing required field 'player_ids'",
        ),
        (
            lambda e: e["intermediate_calculations"][0].__setitem__("dependent_calculation_ids", ["missing_calc_id"]),
            "references unknown id",
        ),
        (
            lambda e: e["intermediate_calculations"][0].__setitem__(
                "dependent_calculation_ids", [e["intermediate_calculations"][0]["id"]]
            ),
            "self-dependency",
        ),
        (
            lambda e: e["final_conclusions"].__setitem__("classification", "SAFE"),
            "classification invalid",
        ),
        (
            lambda e: e["final_conclusions"]["flags"]["values"].append("LEGACY_FLAG"),
            "contains invalid flag",
        ),
        (
            lambda e: e.pop("algorithm_name"),
            "missing required field 'algorithm_name'",
        ),
        (
            lambda e: e.__setitem__("narrative_summary", "not allowed"),
            "unknown envelope fields",
        ),
    ],
)
def test_malformed_fallback_evidence_rejected(
    evidence_validator: GeneratedStaticAlgorithmEvidenceValidator,
    judge_output_validator: JudgeOutputValidator,
    valid_fallback_evidence: dict[str, Any],
    fallback_runtime_plan: ResolvedRuntimePlan,
    mutator,
    expected_fragment: str,
) -> None:
    evidence = copy.deepcopy(valid_fallback_evidence)
    mutator(evidence)
    errors = evidence_validator.validate(evidence)
    assert errors
    assert any(expected_fragment in error for error in errors)

    output = _buildFallbackJudgeOutput(evidence)
    with pytest.raises(JudgeOutputSchemaViolationError) as exc_info:
        judge_output_validator.validate(output, fallback_runtime_plan)
    assert any(expected_fragment in error for error in exc_info.value.errors)


def test_complete_execution_status_rejected_for_invalid_evidence(
    judge_output_validator: JudgeOutputValidator,
    valid_fallback_evidence: dict[str, Any],
    fallback_runtime_plan: ResolvedRuntimePlan,
) -> None:
    evidence = copy.deepcopy(valid_fallback_evidence)
    evidence.pop("statistics")
    output = _buildFallbackJudgeOutput(evidence, execution_status="COMPLETE")
    with pytest.raises(JudgeOutputSchemaViolationError) as exc_info:
        judge_output_validator.validate(output, fallback_runtime_plan)
    assert any("COMPLETE not permitted" in error for error in exc_info.value.errors)
