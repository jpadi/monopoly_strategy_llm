"""Cursor integration tests — run when CURSOR_API_KEY is configured, skip otherwise."""

from __future__ import annotations

import pytest

from integration.LlmEvaluation.Infrastructure.Cursor.cursor_integration_helpers import (
    assertIntegrationScenarioOutput,
    runCursorJudgeScenario,
)
from integration.LlmEvaluation.integration_scenario_registry import INTEGRATION_SCENARIOS
from Monopoly.bootstrap import repoRoot
from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorLlmClient import CursorLlmClient
from Monopoly.LlmEvaluation.Infrastructure.Specification.FileSystemSpecificationRepository import (
    FileSystemSpecificationRepository,
)
from Monopoly.Shared.Infrastructure.EnvironmentLoader import cursorApiKeyConfigured

pytestmark = [
    pytest.mark.integration,
    pytest.mark.llm,
    pytest.mark.cursor,
    pytest.mark.skipif(
        not cursorApiKeyConfigured(),
        reason="CURSOR_API_KEY is not configured (set in repository root .env or process environment)",
    ),
]


class TestCursorSdkImport:
    def test_cursor_client_import(self, cursor_api_key: str, integration_artifact_dir):
        repository = FileSystemSpecificationRepository(docsRoot=repoRoot())
        client = CursorLlmClient(apiKey=cursor_api_key, specificationRepository=repository)
        assert client is not None
        assert integration_artifact_dir.is_dir()


class TestCursorJudgeRuntimeModes:
    """Live Cursor tests — one scenario per distinct runtime mode path."""

    @pytest.mark.parametrize(
        "scenario",
        INTEGRATION_SCENARIOS,
        ids=lambda scenario: scenario.scenario_id,
    )
    def test_runtime_mode(
        self,
        scenario,
        cursor_api_key: str,
        cursor_judge_model: str,
        integration_artifact_dir,
    ):
        serialized = runCursorJudgeScenario(
            scenario=scenario,
            cursor_api_key=cursor_api_key,
            cursor_judge_model=cursor_judge_model,
        )
        assertIntegrationScenarioOutput(serialized, scenario)
        assert integration_artifact_dir.is_dir()
