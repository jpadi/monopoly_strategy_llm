"""Functional tests for EvaluateTradeWithJudgeQuery via QueryBus."""

from __future__ import annotations

import json

import pytest
from integration.LlmEvaluation.integration_scenario_registry import (
    INTEGRATION_SCENARIOS,
)
from llmFixtureLoader import loadProviderResponseWithFallbackEvidence
from test_utilities.fake_llm_client import FakeLlmClient
from test_utilities.repo_paths import FIXTURE_ROOT, INPUT_SPECIFICATION_PATH

from Monopoly.bootstrap import createQueryBus
from Monopoly.LlmEvaluation.Application.Query.EvaluateTradeWithJudge.EvaluateTradeWithJudgeQuery import (
    EvaluateTradeWithJudgeQuery,
)
from Monopoly.LlmEvaluation.Infrastructure.Json.JudgeOutputSerializer import (
    JudgeOutputSerializer,
)
from Monopoly.LlmEvaluation.Infrastructure.Json.JudgeRequestMapper import (
    JudgeRequestMapper,
)


@pytest.fixture
def fake_llm_client() -> FakeLlmClient:
    responses = {
        scenario.scenario_id: loadProviderResponseWithFallbackEvidence(scenario.scenario_id)
        for scenario in INTEGRATION_SCENARIOS
    }
    return FakeLlmClient(responsesByScenario=responses)


@pytest.fixture
def query_bus(fake_llm_client: FakeLlmClient):
    return createQueryBus(llmClient=fake_llm_client)


@pytest.mark.parametrize("scenario", INTEGRATION_SCENARIOS, ids=lambda scenario: scenario.scenario_id)
def test_query_bus_runtime_mode(scenario, query_bus, fake_llm_client):
    fake_llm_client.activeScenarioId = scenario.scenario_id
    payload = json.loads((FIXTURE_ROOT / "inputs" / scenario.input_fixture).read_text(encoding="utf-8"))
    request = JudgeRequestMapper.fromDict(payload)
    result = query_bus.ask(EvaluateTradeWithJudgeQuery(request=request))
    serialized = JudgeOutputSerializer.resultToDict(result)
    static = serialized["output"]["static_analysis_result"]

    assert static["execution_mode"] == scenario.expected_execution_mode
    assert static["evidence_source"] == scenario.expected_evidence_source
    assert static["execution_status"] == scenario.expected_execution_status

    assert fake_llm_client.lastCall is not None
    assert fake_llm_client.requestIncludesInitialPromptPath()
    assert fake_llm_client.requestIncludesAttachmentStandardPath()
    assert fake_llm_client.requestIncludesJudgeAttachmentPath()
    assert fake_llm_client.requestIncludesInputSpecificationPath()
    assert fake_llm_client.taskPromptOmitsSpecBodies()
    assert fake_llm_client.manifestMatchesDeliveredPaths()
    if scenario.expects_spec_bundle:
        assert fake_llm_client.bundleIncludesInitialPrompt()
        assert "docs/static_evaluator/static_algorithm_specification.md" in fake_llm_client.lastCall.attachmentFilePaths
    else:
        assert INPUT_SPECIFICATION_PATH in fake_llm_client.lastCall.attachmentFilePaths
        assert not any(
            path.startswith("docs/static_evaluator/") for path in fake_llm_client.lastCall.attachmentFilePaths
        )
