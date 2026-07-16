"""Unit tests for Cursor repair transport contract."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from Monopoly.LlmEvaluation.Application.Service.EvaluateTradeWithJudgeService import (
    EvaluateTradeWithJudgeService,
    createDefaultModeResolver,
)
from Monopoly.LlmEvaluation.Domain.Exception.LlmEvaluationErrors import JudgeRepairFailureError
from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorTransportError import CursorTransportError
from Monopoly.LlmEvaluation.Domain.Port.LlmClient import LlmClient, LlmRequest, LlmResponse
from Monopoly.LlmEvaluation.Domain.Service.JudgeOutputValidator import JudgeOutputValidator
from Monopoly.LlmEvaluation.Domain.Service.JudgePromptBuilder import JudgePromptBuilder
from Monopoly.LlmEvaluation.Domain.Service.JudgeResponseParser import JudgeResponseParser
from Monopoly.LlmEvaluation.Domain.Service.SpecificationBundleBuilder import SpecificationBundleBuilder
from Monopoly.LlmEvaluation.Infrastructure.Artifact.DefaultJudgeArtifactRecorder import DefaultJudgeArtifactRecorder
from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorExecutionWorkspace import CursorExecutionWorkspace
from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorTransportNormalizer import CursorTransportNormalizer
from Monopoly.LlmEvaluation.Infrastructure.Json.JudgeRequestMapper import JudgeRequestMapper
from Monopoly.LlmEvaluation.Infrastructure.Specification.FileSystemSpecificationRepository import (
    FileSystemSpecificationRepository,
)
from test_utilities.judge_output_builder import buildCanonicalJudgeOutput
from test_utilities.repo_paths import FIXTURE_ROOT, REPO_ROOT


def _inlineEnvelope(content: dict) -> str:
    return json.dumps(
        {
            "transport_version": "1.0",
            "response_type": "inline_json",
            "content": content,
        }
    )


def _fileEnvelope(path: str) -> str:
    return json.dumps(
        {
            "transport_version": "1.0",
            "response_type": "file_reference",
            "file_reference": {
                "path": path,
                "format": "json",
                "encoding": "utf-8",
                "content_type": "application/json",
            },
        }
    )


class TransportScenarioLlmClient(LlmClient):
    """Cursor-like client that applies transport normalization per call with its own workspace."""

    def __init__(self, *, scenarios: list[dict[str, Any]]) -> None:
        self._scenarios = scenarios
        self.calls: list[LlmRequest] = []
        self.workspaces: list[Path] = []
        self.diagnostics: list[dict[str, Any]] = []

    def complete(self, request: LlmRequest) -> LlmResponse:
        self.calls.append(request)
        index = len(self.calls) - 1
        if index >= len(self._scenarios):
            raise RuntimeError("Unexpected extra provider call")

        scenario = self._scenarios[index]
        workspace = CursorExecutionWorkspace.create()
        self.workspaces.append(workspace.root)
        try:
            rawProviderText = scenario["raw_provider_text"]
            if "workspace_file" in scenario:
                relativePath, payload = scenario["workspace_file"]
                target = workspace.root / relativePath
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(
                    json.dumps(payload) if isinstance(payload, dict) else payload,
                    encoding="utf-8",
                )
            normalizedText, diagnostics = CursorTransportNormalizer.normalize(
                rawProviderText=rawProviderText,
                workspaceRoot=workspace.root,
                agent=scenario.get("agent"),
            )
            metadata = diagnostics.toProviderMetadata()
            self.diagnostics.append(metadata)
            return LlmResponse(
                rawText=normalizedText,
                modelUsed=request.model,
                providerMetadata=metadata,
            )
        finally:
            workspace.cleanup()


@pytest.fixture
def specification_repository() -> FileSystemSpecificationRepository:
    return FileSystemSpecificationRepository(docsRoot=REPO_ROOT)


@pytest.fixture
def fallback_request():
    payload = json.loads((FIXTURE_ROOT / "inputs/fallback_authorized.json").read_text(encoding="utf-8"))
    return JudgeRequestMapper.fromDict(payload)


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


def _service(client: LlmClient, specification_repository: FileSystemSpecificationRepository):
    modeResolver = createDefaultModeResolver(specificationRepository=specification_repository)
    return EvaluateTradeWithJudgeService(
        llmClient=client,
        modeResolver=modeResolver,
        bundleBuilder=SpecificationBundleBuilder(specificationRepository=specification_repository),
        promptBuilder=JudgePromptBuilder(),
        responseParser=JudgeResponseParser(),
        outputValidator=JudgeOutputValidator(),
        artifactRecorder=DefaultJudgeArtifactRecorder(),
    )


def test_repair_returns_inline_json(fallback_request, specification_repository):
    from llmFixtureLoader import loadProviderResponseWithFallbackEvidence

    fixed = loadProviderResponseWithFallbackEvidence("fallback_authorized")
    client = TransportScenarioLlmClient(
        scenarios=[
            {"raw_provider_text": _inlineEnvelope(_broken_fallback_output())},
            {"raw_provider_text": _inlineEnvelope(fixed)},
        ]
    )
    result = _service(client, specification_repository).execute(fallback_request)
    assert result.metadata.repairAttempted is True
    assert len(client.calls) == 2
    assert client.diagnostics[1]["normalization_method"] == "transport_inline_json"


def test_repair_returns_file_reference(fallback_request, specification_repository):
    from llmFixtureLoader import loadProviderResponseWithFallbackEvidence

    fixed = loadProviderResponseWithFallbackEvidence("fallback_authorized")
    client = TransportScenarioLlmClient(
        scenarios=[
            {"raw_provider_text": _inlineEnvelope(_broken_fallback_output())},
            {
                "raw_provider_text": _fileEnvelope("output/judge_output.json"),
                "workspace_file": ("output/judge_output.json", fixed),
            },
        ]
    )
    result = _service(client, specification_repository).execute(fallback_request)
    assert result.metadata.repairAttempted is True
    assert client.diagnostics[1]["response_type"] == "file_reference"
    assert client.diagnostics[1]["retrieval_method"] == "local_workspace_read"


def test_repair_file_exists_in_repair_workspace_only(fallback_request, specification_repository):
    from llmFixtureLoader import loadProviderResponseWithFallbackEvidence

    fixed = loadProviderResponseWithFallbackEvidence("fallback_authorized")
    client = TransportScenarioLlmClient(
        scenarios=[
            {
                "raw_provider_text": _fileEnvelope("output/judge_output.json"),
                "workspace_file": ("output/judge_output.json", _broken_fallback_output()),
            },
            {
                "raw_provider_text": _fileEnvelope("output/judge_output.json"),
                "workspace_file": ("output/judge_output.json", fixed),
            },
        ]
    )
    result = _service(client, specification_repository).execute(fallback_request)
    assert result.metadata.repairAttempted is True
    assert client.workspaces[0] != client.workspaces[1]


def test_repair_file_missing(fallback_request, specification_repository):
    client = TransportScenarioLlmClient(
        scenarios=[
            {"raw_provider_text": _inlineEnvelope(_broken_fallback_output())},
            {"raw_provider_text": _fileEnvelope("missing/output.json")},
        ]
    )
    with pytest.raises(CursorTransportError) as exc_info:
        _service(client, specification_repository).execute(fallback_request)
    assert exc_info.value.stage == "file_reference_missing_file"
    assert len(client.calls) == 2


def test_repair_transport_envelope_invalid(fallback_request, specification_repository):
    client = TransportScenarioLlmClient(
        scenarios=[
            {"raw_provider_text": _inlineEnvelope(_broken_fallback_output())},
            {"raw_provider_text": "please read the file manually"},
        ]
    )
    with pytest.raises(CursorTransportError) as exc_info:
        _service(client, specification_repository).execute(fallback_request)
    assert exc_info.value.stage == "unstructured_prose"
    assert len(client.calls) == 2


def test_repair_output_canonical_json_invalid(fallback_request, specification_repository):
    client = TransportScenarioLlmClient(
        scenarios=[
            {"raw_provider_text": _inlineEnvelope(_broken_fallback_output())},
            {"raw_provider_text": _inlineEnvelope(_broken_fallback_output())},
        ]
    )
    with pytest.raises(JudgeRepairFailureError) as exc_info:
        _service(client, specification_repository).execute(fallback_request)
    assert exc_info.value.repairValidationErrors
    assert len(client.calls) == 2


def test_repair_transport_diagnostics_preserved_separately(fallback_request, specification_repository):
    from llmFixtureLoader import loadProviderResponseWithFallbackEvidence

    fixed = loadProviderResponseWithFallbackEvidence("fallback_authorized")
    client = TransportScenarioLlmClient(
        scenarios=[
            {"raw_provider_text": _inlineEnvelope(_broken_fallback_output())},
            {"raw_provider_text": _inlineEnvelope(fixed)},
        ]
    )
    _service(client, specification_repository).execute(fallback_request)
    assert client.diagnostics[0]["normalization_method"] == "transport_inline_json"
    assert client.diagnostics[1]["normalization_method"] == "transport_inline_json"
    assert client.diagnostics[0] is not client.diagnostics[1]


def test_repair_file_reference_cannot_read_initial_workspace(fallback_request, specification_repository):
    from llmFixtureLoader import loadProviderResponseWithFallbackEvidence

    fixed = loadProviderResponseWithFallbackEvidence("fallback_authorized")
    client = TransportScenarioLlmClient(
        scenarios=[
            {
                "raw_provider_text": _inlineEnvelope(_broken_fallback_output()),
                "workspace_file": ("output/judge_output.json", fixed),
            },
            {"raw_provider_text": _fileEnvelope("output/judge_output.json")},
        ]
    )
    with pytest.raises(CursorTransportError) as exc_info:
        _service(client, specification_repository).execute(fallback_request)
    assert exc_info.value.stage == "file_reference_missing_file"
    assert client.workspaces[0] != client.workspaces[1]
    assert len(client.calls) == 2


def test_only_one_repair_attempt_occurs(fallback_request, specification_repository):
    client = TransportScenarioLlmClient(
        scenarios=[
            {"raw_provider_text": _inlineEnvelope(_broken_fallback_output())},
            {"raw_provider_text": _inlineEnvelope(_broken_fallback_output())},
        ]
    )
    with pytest.raises(JudgeRepairFailureError):
        _service(client, specification_repository).execute(fallback_request)
    assert len(client.calls) == 2
