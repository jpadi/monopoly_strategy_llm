"""Complete prompt delivery tests for non-fallback and fallback requests."""

from __future__ import annotations

import json

import pytest
from test_utilities.repo_paths import FIXTURE_ROOT, INPUT_SPECIFICATION_PATH, REPO_ROOT

from Monopoly.LlmEvaluation.Domain.Model.Runtime.ResolvedRuntimePlan import (
    ResolvedRuntimePlan,
)
from Monopoly.LlmEvaluation.Domain.Service.JudgePromptBuilder import (
    DEFAULT_INSTRUCTION_FILE_PATHS,
    JudgePromptBuilder,
)
from Monopoly.LlmEvaluation.Domain.Service.SpecificationBundleBuilder import (
    SpecificationBundleBuilder,
)
from Monopoly.LlmEvaluation.Infrastructure.Json.JudgeRequestMapper import (
    JudgeRequestMapper,
)
from Monopoly.LlmEvaluation.Infrastructure.Specification.FileSystemSpecificationRepository import (
    FileSystemSpecificationRepository,
)
from Monopoly.LlmEvaluation.Infrastructure.Specification.LlmPromptAssembler import (
    LlmPromptAssembler,
)


@pytest.fixture
def repository() -> FileSystemSpecificationRepository:
    return FileSystemSpecificationRepository(docsRoot=REPO_ROOT)


def _build_request(
    fixture_name: str,
    runtime_plan: ResolvedRuntimePlan,
    repository: FileSystemSpecificationRepository,
):
    payload = json.loads((FIXTURE_ROOT / "inputs" / fixture_name).read_text(encoding="utf-8"))
    request = JudgeRequestMapper.fromDict(payload)
    bundle = SpecificationBundleBuilder(specificationRepository=repository).build(runtime_plan)
    llm_request = JudgePromptBuilder().build(
        request.evaluationInput,
        runtime_plan,
        bundle,
        model="fake-model",
    )
    prompt = LlmPromptAssembler(specificationRepository=repository).assemble(llm_request)
    return llm_request, prompt


def test_non_fallback_delivers_complete_llm_evaluator_set(
    repository: FileSystemSpecificationRepository,
):
    runtime_plan = ResolvedRuntimePlan(
        requestedMode="auto",
        executionMode="NO_STATIC_ANALYSIS",
        evidenceSource=None,
        algorithmId=None,
        algorithmVersion=None,
        dependencyVersions={},
        expectedExecutionStatus="UNAVAILABLE",
        fallbackAuthorized=False,
        fallbackRequired=False,
        fallbackAttempted=False,
        evidenceUsability=(),
        limitations=(),
        bundleRequired=False,
    )
    llm_request, prompt = _build_request("competitive_only.json", runtime_plan, repository)

    expected_llm = set(repository.llmEvaluatorBundlePaths())
    attachment_set = set(llm_request.attachmentFilePaths)
    instruction_set = set(llm_request.instructionFilePaths)
    assert expected_llm - {DEFAULT_INSTRUCTION_FILE_PATHS[0]} <= attachment_set
    assert INPUT_SPECIFICATION_PATH in attachment_set
    assert not any(path.startswith("docs/static_evaluator/") for path in attachment_set)
    assert llm_request.specificationBundle is not None
    manifest = llm_request.specificationBundle.structureManifest
    assert set(manifest.deliveredFilePaths) == instruction_set | attachment_set
    assert f"--- BEGIN ATTACHED FILE: {INPUT_SPECIFICATION_PATH} ---" in prompt
    assert f"--- END ATTACHED FILE: {INPUT_SPECIFICATION_PATH} ---" in prompt


def test_fallback_delivers_static_evaluator_set(
    repository: FileSystemSpecificationRepository,
):
    runtime_plan = ResolvedRuntimePlan(
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
    llm_request, prompt = _build_request("fallback_authorized.json", runtime_plan, repository)

    expected_static = set(repository.staticEvaluatorBundlePaths())
    attachment_set = set(llm_request.attachmentFilePaths)
    assert expected_static <= attachment_set
    manifest = llm_request.specificationBundle.structureManifest
    assert set(manifest.deliveredFilePaths) == set(llm_request.instructionFilePaths) | attachment_set
    for static_path in expected_static:
        assert f"--- BEGIN ATTACHED FILE: {static_path} ---" in prompt


def test_repair_request_preserves_delivery_sets(
    repository: FileSystemSpecificationRepository,
):
    runtime_plan = ResolvedRuntimePlan(
        requestedMode="auto",
        executionMode="NO_STATIC_ANALYSIS",
        evidenceSource=None,
        algorithmId=None,
        algorithmVersion=None,
        dependencyVersions={},
        expectedExecutionStatus="UNAVAILABLE",
        fallbackAuthorized=False,
        fallbackRequired=False,
        fallbackAttempted=False,
        evidenceUsability=(),
        limitations=(),
        bundleRequired=False,
    )
    payload = json.loads((FIXTURE_ROOT / "inputs/competitive_only.json").read_text(encoding="utf-8"))
    request = JudgeRequestMapper.fromDict(payload)
    bundle = SpecificationBundleBuilder(specificationRepository=repository).build(runtime_plan)
    original = JudgePromptBuilder().build(request.evaluationInput, runtime_plan, bundle, model="fake-model")
    repair = JudgePromptBuilder().build(
        request.evaluationInput,
        runtime_plan,
        bundle,
        model="fake-model",
        repairErrors=("example validation error",),
    )
    assert original.instructionFilePaths == repair.instructionFilePaths
    assert original.attachmentFilePaths == repair.attachmentFilePaths
