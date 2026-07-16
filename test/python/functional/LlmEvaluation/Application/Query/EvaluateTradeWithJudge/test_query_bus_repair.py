"""Functional tests for fallback repair through the Query Bus."""

from __future__ import annotations

import json

import pytest
from llmFixtureLoader import loadProviderResponseWithFallbackEvidence
from test_utilities.fake_llm_client import FakeLlmClient
from test_utilities.judge_output_builder import buildCanonicalJudgeOutput
from test_utilities.repo_paths import FIXTURE_ROOT

from Monopoly.bootstrap import createQueryBus
from Monopoly.LlmEvaluation.Application.Query.EvaluateTradeWithJudge.EvaluateTradeWithJudgeQuery import (
    EvaluateTradeWithJudgeQuery,
)
from Monopoly.LlmEvaluation.Domain.Exception.LlmEvaluationErrors import (
    JudgeRepairFailureError,
)
from Monopoly.LlmEvaluation.Infrastructure.Json.JudgeOutputSerializer import (
    JudgeOutputSerializer,
)
from Monopoly.LlmEvaluation.Infrastructure.Json.JudgeRequestMapper import (
    JudgeRequestMapper,
)


def _broken_fallback_output() -> dict:
    return buildCanonicalJudgeOutput(
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


@pytest.fixture
def fallback_repair_client() -> FakeLlmClient:
    return FakeLlmClient(
        responsesByScenario={"fallback_authorized": _broken_fallback_output()},
        repairResponseText=json.dumps(loadProviderResponseWithFallbackEvidence("fallback_authorized")),
    )


def test_query_bus_fallback_repair_success(fallback_repair_client: FakeLlmClient):
    fallback_repair_client.activeScenarioId = "fallback_authorized"
    query_bus = createQueryBus(llmClient=fallback_repair_client)
    payload = json.loads((FIXTURE_ROOT / "inputs/fallback_authorized.json").read_text(encoding="utf-8"))
    request = JudgeRequestMapper.fromDict(payload)
    result = query_bus.ask(EvaluateTradeWithJudgeQuery(request=request))
    serialized = JudgeOutputSerializer.resultToDict(result)

    assert serialized["metadata"]["repair_attempted"] is True
    assert serialized["metadata"]["repair_count"] == 1
    assert len(fallback_repair_client.calls) == 2
    assert "## Repair request" in fallback_repair_client.calls[1].taskPrompt
    assert "Structured validation errors" in fallback_repair_client.calls[1].taskPrompt
    assert fallback_repair_client.manifestMatchesDeliveredPaths()


def test_query_bus_fallback_repair_prose_failure(fallback_repair_client: FakeLlmClient):
    fallback_repair_client.activeScenarioId = "fallback_authorized"
    fallback_repair_client.repairResponseText = "Please read the output file from disk."
    query_bus = createQueryBus(llmClient=fallback_repair_client)

    payload = json.loads((FIXTURE_ROOT / "inputs/fallback_authorized.json").read_text(encoding="utf-8"))
    request = JudgeRequestMapper.fromDict(payload)

    with pytest.raises(JudgeRepairFailureError) as exc_info:
        query_bus.ask(EvaluateTradeWithJudgeQuery(request=request))

    assert exc_info.value.repairParseError is not None
    assert exc_info.value.initialValidationErrors
    assert len(fallback_repair_client.calls) == 2
