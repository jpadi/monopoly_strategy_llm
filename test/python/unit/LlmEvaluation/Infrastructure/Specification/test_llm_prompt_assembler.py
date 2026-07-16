"""Unit tests for LlmPromptAssembler."""

from __future__ import annotations

from test_utilities.repo_paths import INPUT_SPECIFICATION_PATH, REPO_ROOT

from Monopoly.LlmEvaluation.Domain.Model.Specification.SpecificationBundle import (
    BundleFile,
    SpecificationBundle,
    SpecificationStructureManifest,
)
from Monopoly.LlmEvaluation.Domain.Port.LlmClient import LlmRequest
from Monopoly.LlmEvaluation.Domain.Service.JudgePromptBuilder import (
    FILE_ATTACHMENT_STANDARD_PATH,
    INITIAL_PROMPT_PATH,
)
from Monopoly.LlmEvaluation.Infrastructure.Specification.FileSystemSpecificationRepository import (
    FileSystemSpecificationRepository,
)
from Monopoly.LlmEvaluation.Infrastructure.Specification.LlmPromptAssembler import (
    LlmPromptAssembler,
)


def test_assemble_loads_instruction_paths_and_formats_attachments():
    repository = FileSystemSpecificationRepository(docsRoot=REPO_ROOT)
    input_spec_bytes = repository.readFile(INPUT_SPECIFICATION_PATH)
    bundle = SpecificationBundle(
        files=(
            BundleFile(
                relativePath=INPUT_SPECIFICATION_PATH,
                content=input_spec_bytes,
            ),
        ),
        structureManifest=SpecificationStructureManifest(
            rootLabel="docs",
            treeText="docs/",
            readOrder=(INPUT_SPECIFICATION_PATH,),
            linkNotes=(),
            instructionFilePaths=(INITIAL_PROMPT_PATH, FILE_ATTACHMENT_STANDARD_PATH),
            attachmentFilePaths=(INPUT_SPECIFICATION_PATH,),
            deliveredFilePaths=(
                INITIAL_PROMPT_PATH,
                FILE_ATTACHMENT_STANDARD_PATH,
                INPUT_SPECIFICATION_PATH,
            ),
        ),
    )
    request = LlmRequest(
        model="fake-model",
        instructionFilePaths=(INITIAL_PROMPT_PATH, FILE_ATTACHMENT_STANDARD_PATH),
        attachmentFilePaths=(INPUT_SPECIFICATION_PATH,),
        taskPrompt="## Evaluation task\nexample",
        specificationBundle=bundle,
    )

    prompt = LlmPromptAssembler(specificationRepository=repository).assemble(request)

    assert "# LLM Judge Initial Prompt" in prompt
    assert "# File Attachment Standard" in prompt
    assert "## Evaluation task" in prompt
    assert f"--- BEGIN ATTACHED FILE: {INPUT_SPECIFICATION_PATH} ---" in prompt
