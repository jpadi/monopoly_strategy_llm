"""Helpers for live Cursor Judge integration tests."""

from __future__ import annotations

import json
from typing import Any

from Monopoly.LlmEvaluation.Application.Query.EvaluateTradeWithJudge.EvaluateTradeWithJudgeQuery import (
    EvaluateTradeWithJudgeQuery,
)
from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorLlmClient import CursorLlmClient
from Monopoly.LlmEvaluation.Infrastructure.Json.JudgeOutputSerializer import JudgeOutputSerializer
from Monopoly.LlmEvaluation.Infrastructure.Json.JudgeRequestMapper import JudgeRequestMapper
from Monopoly.LlmEvaluation.Infrastructure.Specification.FileSystemSpecificationRepository import (
    FileSystemSpecificationRepository,
)
from Monopoly.Shared.Infrastructure.ArtifactStore import currentArtifactSubpath, writeArtifactJson
from Monopoly.bootstrap import createEvaluateTradeWithJudgeHandler, repoRoot
from integration.LlmEvaluation.integration_scenario_registry import IntegrationJudgeScenario
from test_utilities.repo_paths import FIXTURE_ROOT, INPUT_SPECIFICATION_PATH, REPO_ROOT


def runCursorJudgeScenario(
    *,
    scenario: IntegrationJudgeScenario,
    cursor_api_key: str,
    cursor_judge_model: str,
) -> dict[str, Any]:
    payload = json.loads((FIXTURE_ROOT / "inputs" / scenario.input_fixture).read_text(encoding="utf-8"))
    payload["llm_execution"] = {"provider": "cursor", "model": cursor_judge_model}

    subpath = currentArtifactSubpath()
    if subpath:
        writeArtifactJson(f"{subpath}/input_fixture.json", payload)
        writeArtifactJson(
            f"{subpath}/expected.json",
            {
                "scenario_id": scenario.scenario_id,
                "expected_execution_mode": scenario.expected_execution_mode,
                "expected_evidence_source": scenario.expected_evidence_source,
                "expected_execution_status": scenario.expected_execution_status,
                "expects_spec_bundle": scenario.expects_spec_bundle,
            },
        )

    request = JudgeRequestMapper.fromDict(payload)
    specificationRepository = FileSystemSpecificationRepository(docsRoot=repoRoot())
    handler = createEvaluateTradeWithJudgeHandler(
        llmClient=CursorLlmClient(
            apiKey=cursor_api_key,
            specificationRepository=specificationRepository,
        ),
    )
    result = handler.handle(EvaluateTradeWithJudgeQuery(request=request))
    serialized = JudgeOutputSerializer.resultToDict(result)

    if subpath:
        writeArtifactJson(f"{subpath}/result.json", serialized)
        _writeIntegrationDiagnostics(subpath, scenario, serialized)
        requestSummaryPath = REPO_ROOT / "artifact" / subpath / "request_summary.json"
        if requestSummaryPath.is_file():
            requestSummary = json.loads(requestSummaryPath.read_text(encoding="utf-8"))
            assertDeliveryEvidenceInArtifacts(request_summary=requestSummary, scenario=scenario)

    return serialized


def _writeIntegrationDiagnostics(
    subpath: str,
    scenario: IntegrationJudgeScenario,
    serialized: dict[str, Any],
) -> None:
    artifactRoot = REPO_ROOT / "artifact" / subpath
    requestSummaryPath = artifactRoot / "request_summary.json"
    if requestSummaryPath.is_file():
        requestSummary = json.loads(requestSummaryPath.read_text(encoding="utf-8"))
        writeArtifactJson(f"{subpath}/delivery_verification.json", requestSummary)

    metadata = serialized.get("metadata", {})
    transportDiagnosticsPath = artifactRoot / "provider_transport_diagnostics.json"
    transportDiagnostics = {}
    if transportDiagnosticsPath.is_file():
        transportDiagnostics = json.loads(transportDiagnosticsPath.read_text(encoding="utf-8"))

    diagnostics = {
        "scenario_id": scenario.scenario_id,
        "repair_attempted": metadata.get("repair_attempted", False),
        "repair_count": metadata.get("repair_count", 0),
        "initial_validation_error_count": len(metadata.get("original_validation_errors", [])),
        "artifact_files": sorted(path.name for path in artifactRoot.iterdir() if path.is_file()),
        "transport_envelope_detected": transportDiagnostics.get("transport_envelope_detected"),
        "response_type": transportDiagnostics.get("response_type"),
        "workspace_relative_path": transportDiagnostics.get("workspace_relative_path"),
        "retrieval_method": transportDiagnostics.get("retrieval_method"),
        "bytes_recovered": transportDiagnostics.get("bytes_recovered"),
        "legacy_recovery_used": transportDiagnostics.get("legacy_recovery_used"),
        "normalization_method": transportDiagnostics.get("normalization_method"),
        "failure_stage": transportDiagnostics.get("failure_stage"),
    }
    writeArtifactJson(f"{subpath}/integration_diagnostics.json", diagnostics)


def assertIntegrationScenarioOutput(
    serialized: dict[str, Any],
    scenario: IntegrationJudgeScenario,
) -> None:
    output = serialized["output"]
    static = output["static_analysis_result"]

    assert static["execution_mode"] == scenario.expected_execution_mode, (
        f"{scenario.scenario_id}: execution_mode mismatch"
    )
    assert static["evidence_source"] == scenario.expected_evidence_source, (
        f"{scenario.scenario_id}: evidence_source mismatch"
    )

    actual_status = static["execution_status"]
    if scenario.expected_execution_mode == "LLM_STATIC_FALLBACK":
        assert actual_status in {"COMPLETE", "PARTIAL"}, (
            f"{scenario.scenario_id}: fallback execution_status expected COMPLETE or PARTIAL, got {actual_status}"
        )
    else:
        assert actual_status == scenario.expected_execution_status, (
            f"{scenario.scenario_id}: execution_status mismatch"
        )

    classification = output["competitive_classification"]["classification"]
    assert classification in {
        "competitively_sound",
        "slightly_unbalanced",
        "significantly_unbalanced",
        "severely_unbalanced",
    }

    if scenario.expected_execution_mode == "LLM_STATIC_FALLBACK":
        generated = static.get("generated_static_algorithm_evidence", [])
        assert generated, f"{scenario.scenario_id}: fallback must generate static evidence"


def assertDeliveryEvidenceInArtifacts(
    *,
    request_summary: dict[str, Any],
    scenario: IntegrationJudgeScenario,
) -> None:
    assert INPUT_SPECIFICATION_PATH in request_summary["attachment_file_paths"] or any(
        item["path"] == INPUT_SPECIFICATION_PATH for item in request_summary["attachment_files"]
    )
    if scenario.expects_spec_bundle:
        static_paths = {
            "docs/static_evaluator/static_algorithm_specification.md",
            "docs/static_evaluator/risk_reference.md",
        }
        delivered = set(request_summary["attachment_file_paths"])
        assert static_paths <= delivered
