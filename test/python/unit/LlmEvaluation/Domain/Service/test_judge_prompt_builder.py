"""Unit tests for JudgePromptBuilder — passes file paths to LlmClient, not inlined bodies."""

from __future__ import annotations

import json

import pytest
from test_utilities.repo_paths import FIXTURE_ROOT, INPUT_SPECIFICATION_PATH, REPO_ROOT

from Monopoly.LlmEvaluation.Domain.Model.Input.JudgeInput import JudgeInput
from Monopoly.LlmEvaluation.Domain.Model.Runtime.ResolvedRuntimePlan import (
    ResolvedRuntimePlan,
)
from Monopoly.LlmEvaluation.Domain.Service.JudgePromptBuilder import (
    DEFAULT_INSTRUCTION_FILE_PATHS,
    FILE_ATTACHMENT_STANDARD_PATH,
    INITIAL_PROMPT_PATH,
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
        fallbackRequired=True,
        fallbackAttempted=True,
        evidenceUsability=(),
        limitations=(),
        bundleRequired=True,
    )


def test_request_includes_instruction_file_paths(
    fallback_runtime_plan: ResolvedRuntimePlan,
):
    judge_input = JudgeInput(
        metadata={},
        gameConfiguration={},
        boardStateBefore={},
        trade={},
        boardStateAfter={},
    )
    llm_request = JudgePromptBuilder().build(
        judgeInput=judge_input,
        runtimePlan=fallback_runtime_plan,
        specificationBundle=None,
        model="fake-model",
    )

    assert llm_request.instructionFilePaths == DEFAULT_INSTRUCTION_FILE_PATHS
    assert INITIAL_PROMPT_PATH in llm_request.instructionFilePaths
    assert FILE_ATTACHMENT_STANDARD_PATH in llm_request.instructionFilePaths
    assert llm_request.attachmentFilePaths == ()


def test_build_passes_attachment_paths_and_manifest_without_inlined_bodies(
    fallback_runtime_plan: ResolvedRuntimePlan,
):
    payload = json.loads((FIXTURE_ROOT / "inputs/fallback_authorized.json").read_text(encoding="utf-8"))
    request = JudgeRequestMapper.fromDict(payload)
    repository = FileSystemSpecificationRepository(docsRoot=REPO_ROOT)
    bundle = SpecificationBundleBuilder(specificationRepository=repository).build(fallback_runtime_plan)
    llm_request = JudgePromptBuilder().build(
        request.evaluationInput,
        fallback_runtime_plan,
        bundle,
        model="fake-model",
    )

    assert llm_request.instructionFilePaths == DEFAULT_INSTRUCTION_FILE_PATHS
    assert INITIAL_PROMPT_PATH not in llm_request.attachmentFilePaths
    assert FILE_ATTACHMENT_STANDARD_PATH not in llm_request.attachmentFilePaths
    assert "docs/llm_evaluator/01_judge.md" in llm_request.attachmentFilePaths
    assert INPUT_SPECIFICATION_PATH in llm_request.attachmentFilePaths
    assert "docs/llm_evaluator/03_input_schema.md" in llm_request.attachmentFilePaths
    assert "docs/llm_evaluator/04_static_algorithm_specification.md" in llm_request.attachmentFilePaths
    assert "docs/static_evaluator/static_algorithm_specification.md" in llm_request.attachmentFilePaths
    assert "## Specification delivery manifest" in llm_request.taskPrompt
    assert bundle is not None
    manifest = llm_request.specificationBundle.structureManifest
    assert manifest.deliveredFilePaths == llm_request.instructionFilePaths + llm_request.attachmentFilePaths
    assert FILE_ATTACHMENT_STANDARD_PATH in manifest.deliveredFilePaths

    judge_body = repository.readFile("docs/llm_evaluator/01_judge.md").decode("utf-8")
    assert judge_body[:80] not in llm_request.taskPrompt


def test_initial_prompt_file_exists_in_repo():
    path = REPO_ROOT / INITIAL_PROMPT_PATH
    assert path.is_file()
    content = path.read_text(encoding="utf-8")
    assert "01_judge.md" in content
    assert "06_output_schema.md" in content
