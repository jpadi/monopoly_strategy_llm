"""Unit test fixtures for EvaluateTradeWithJudgeService."""

from __future__ import annotations

import json
from typing import Any

import pytest
from llmFixtureLoader import loadProviderResponseWithFallbackEvidence
from test_utilities.fake_llm_client import FakeLlmClient
from test_utilities.judge_output_builder import buildCanonicalJudgeOutput
from test_utilities.repo_paths import FIXTURE_ROOT, REPO_ROOT

from Monopoly.LlmEvaluation.Application.Query.EvaluateTradeWithJudge.EvaluateTradeWithJudgeQuery import (
    EvaluateTradeWithJudgeQuery,
)
from Monopoly.LlmEvaluation.Application.Service.EvaluateTradeWithJudgeService import (
    EvaluateTradeWithJudgeService,
    createDefaultModeResolver,
)
from Monopoly.LlmEvaluation.Domain.Service.JudgeOutputValidator import JudgeOutputValidator
from Monopoly.LlmEvaluation.Domain.Service.JudgePromptBuilder import JudgePromptBuilder
from Monopoly.LlmEvaluation.Domain.Service.JudgeResponseParser import JudgeResponseParser
from Monopoly.LlmEvaluation.Domain.Service.SpecificationBundleBuilder import SpecificationBundleBuilder
from Monopoly.LlmEvaluation.Infrastructure.Artifact.DefaultJudgeArtifactRecorder import DefaultJudgeArtifactRecorder
from Monopoly.LlmEvaluation.Infrastructure.Json.JudgeOutputSerializer import JudgeOutputSerializer
from Monopoly.LlmEvaluation.Infrastructure.Json.JudgeRequestMapper import JudgeRequestMapper
from Monopoly.LlmEvaluation.Infrastructure.Specification.FileSystemSpecificationRepository import (
    FileSystemSpecificationRepository,
)


@pytest.fixture
def specification_repository() -> FileSystemSpecificationRepository:
    return FileSystemSpecificationRepository(docsRoot=REPO_ROOT)


@pytest.fixture
def fake_llm_client() -> FakeLlmClient:
    responses = {}
    response_dir = FIXTURE_ROOT / "provider_responses"
    for path in response_dir.glob("*.json"):
        scenario_id = path.stem
        responses[scenario_id] = loadProviderResponseWithFallbackEvidence(scenario_id)
    return FakeLlmClient(
        responsesByScenario=responses,
        defaultResponse=buildCanonicalJudgeOutput(),
    )


@pytest.fixture
def evaluate_trade_with_judge_service(
    fake_llm_client: FakeLlmClient,
    specification_repository: FileSystemSpecificationRepository,
) -> EvaluateTradeWithJudgeService:
    modeResolver = createDefaultModeResolver(specificationRepository=specification_repository)
    return EvaluateTradeWithJudgeService(
        llmClient=fake_llm_client,
        modeResolver=modeResolver,
        bundleBuilder=SpecificationBundleBuilder(specificationRepository=specification_repository),
        promptBuilder=JudgePromptBuilder(),
        responseParser=JudgeResponseParser(),
        outputValidator=JudgeOutputValidator(),
        artifactRecorder=DefaultJudgeArtifactRecorder(),
    )


@pytest.fixture
def execute_judge_scenario(evaluate_trade_with_judge_service, fake_llm_client):
    def _execute(fixture_name: str, scenario_id: str) -> dict[str, Any]:
        fake_llm_client.activeScenarioId = scenario_id
        payload = json.loads((FIXTURE_ROOT / "inputs" / fixture_name).read_text(encoding="utf-8"))
        request = JudgeRequestMapper.fromDict(payload)
        query = EvaluateTradeWithJudgeQuery(request=request)
        result = evaluate_trade_with_judge_service.execute(query.request)
        return JudgeOutputSerializer.resultToDict(result)

    return _execute
