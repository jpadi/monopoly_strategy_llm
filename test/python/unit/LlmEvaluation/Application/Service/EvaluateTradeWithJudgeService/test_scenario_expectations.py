"""Scenario expectation tests for LLM Judge service."""

from __future__ import annotations

import json

import pytest
from judge_assertions.judge_scenario_registry import RUNTIME_MODES
from test_utilities.repo_paths import FIXTURE_ROOT, INPUT_SPECIFICATION_PATH

from Monopoly.LlmEvaluation.Domain.Exception.LlmEvaluationErrors import (
    JudgeInputValidationError,
)
from Monopoly.LlmEvaluation.Infrastructure.Json.JudgeRequestMapper import (
    JudgeRequestMapper,
)


@pytest.mark.parametrize("scenario", RUNTIME_MODES, ids=lambda scenario: scenario.scenario_id)
def test_scenario_expectations(scenario, execute_judge_scenario, fake_llm_client):
    if scenario.expects_validation_error:
        pytest.skip("Validation-error scenario tested separately")

    result = execute_judge_scenario(scenario.input_fixture, scenario.provider_response)
    output = result["output"]
    static = output["static_analysis_result"]

    assert static["execution_mode"] == scenario.expected_execution_mode
    assert static["evidence_source"] == scenario.expected_evidence_source
    assert static["execution_status"] == scenario.expected_execution_status

    if scenario.expects_llm_call:
        assert fake_llm_client.lastCall is not None
        assert fake_llm_client.lastCall.model == "fake-model"
        assert fake_llm_client.requestIncludesInitialPromptPath()
        assert fake_llm_client.requestIncludesAttachmentStandardPath()
        assert fake_llm_client.requestIncludesJudgeAttachmentPath()
        assert fake_llm_client.requestIncludesInputSpecificationPath()
        assert fake_llm_client.taskPromptOmitsSpecBodies()
        assert fake_llm_client.manifestMatchesDeliveredPaths()
        assert fake_llm_client.lastCall.specificationBundle is not None
        assert fake_llm_client.bundleIncludesInitialPrompt()
        manifest = fake_llm_client.lastCall.specificationBundle.structureManifest
        assert manifest.treeText
        assert manifest.readOrder
        assert INPUT_SPECIFICATION_PATH in manifest.deliveredFilePaths
        if scenario.expects_bundle:
            assert len(fake_llm_client.lastCall.specificationBundle.files) == 10
        else:
            assert len(fake_llm_client.lastCall.specificationBundle.files) == 8


def test_validation_error_prevents_llm_call(evaluate_trade_with_judge_service, fake_llm_client):
    payload = json.loads((FIXTURE_ROOT / "inputs/competitive_only.json").read_text(encoding="utf-8"))
    payload["evaluation_input"]["trade"].pop("id")
    request = JudgeRequestMapper.fromDict(payload)
    with pytest.raises(JudgeInputValidationError):
        evaluate_trade_with_judge_service.execute(request)
    assert fake_llm_client.calls == []


def test_blank_model_rejected():
    payload = json.loads((FIXTURE_ROOT / "inputs/competitive_only.json").read_text(encoding="utf-8"))
    payload["llm_execution"]["model"] = ""
    request = JudgeRequestMapper.fromDict(payload)
    with pytest.raises(ValueError, match="model"):
        request.llmExecution.validate()
