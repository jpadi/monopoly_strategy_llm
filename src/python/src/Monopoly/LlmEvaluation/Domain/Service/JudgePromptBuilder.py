"""Build provider-neutral Judge LlmRequest with file paths for client-side delivery."""

from __future__ import annotations

import json
from typing import Any

from Monopoly.LlmEvaluation.Domain.Model.Input.JudgeInput import JudgeInput
from Monopoly.LlmEvaluation.Domain.Model.JudgeValidationError import JudgeValidationErrorRecord
from Monopoly.LlmEvaluation.Domain.Model.Runtime.ResolvedRuntimePlan import ResolvedRuntimePlan
from Monopoly.LlmEvaluation.Domain.Model.Specification.SpecificationBundle import (
    SpecificationBundle,
)
from Monopoly.LlmEvaluation.Domain.Port.LlmClient import LlmRequest
from Monopoly.LlmEvaluation.Domain.Service.SpecificationManifestBuilder import SpecificationManifestBuilder

INITIAL_PROMPT_PATH = "docs/llm_evaluator/00_initial_prompt.md"
FILE_ATTACHMENT_STANDARD_PATH = "docs/llm_platform/file_attachment_standard.md"
OUTPUT_SCHEMA_PATH = "docs/llm_evaluator/06_output_schema.md"
FALLBACK_EVIDENCE_SPEC_PATH = "docs/llm_evaluator/04_static_algorithm_specification.md"


DEFAULT_INSTRUCTION_FILE_PATHS = (
    INITIAL_PROMPT_PATH,
    FILE_ATTACHMENT_STANDARD_PATH,
)


class JudgePromptBuilder:
    def build(
        self,
        judgeInput: JudgeInput,
        runtimePlan: ResolvedRuntimePlan,
        specificationBundle: SpecificationBundle | None,
        *,
        model: str,
        timeoutSeconds: int | None = None,
        repairErrors: tuple[str, ...] | None = None,
        repairStructuredErrors: tuple[JudgeValidationErrorRecord, ...] | None = None,
        repairInvalidOutput: dict[str, Any] | None = None,
        repairInvalidRawText: str | None = None,
        instructionFilePaths: tuple[str, ...] = DEFAULT_INSTRUCTION_FILE_PATHS,
    ) -> LlmRequest:
        taskSections = [
            "## Evaluation task",
            "Follow the specification read order in the delivery manifest below.",
            f"Requested static analysis mode: {runtimePlan.requestedMode}",
            f"Resolved execution mode: {runtimePlan.executionMode}",
            f"Expected evidence source: {runtimePlan.evidenceSource}",
            f"Expected execution status: {runtimePlan.expectedExecutionStatus}",
            f"Static evaluator bundle required: {runtimePlan.bundleRequired}",
            "",
            "## Evaluation input JSON",
            json.dumps(judgeInput.toCanonicalDict(), indent=2),
        ]
        if runtimePlan.bundleRequired and not repairErrors:
            taskSections.extend(
                [
                    "",
                    "## Fallback execution checklist (required)",
                    f"Complete the Reference graph integrity self-check in {FALLBACK_EVIDENCE_SPEC_PATH}.",
                    f"Return output that satisfies the Mandatory Response Format in {OUTPUT_SCHEMA_PATH}.",
                ]
            )

        attachmentFilePaths: tuple[str, ...] = ()
        resolvedBundle = specificationBundle
        if specificationBundle is not None:
            instructionPaths = frozenset(instructionFilePaths)
            attachmentFilePaths = tuple(
                bundleFile.relativePath
                for bundleFile in specificationBundle.files
                if bundleFile.relativePath not in instructionPaths
            )
            bundlePaths = tuple(file.relativePath for file in specificationBundle.files)
            manifest = SpecificationManifestBuilder.build(
                instructionFilePaths=instructionFilePaths,
                attachmentFilePaths=attachmentFilePaths,
                specificationReadOrder=SpecificationManifestBuilder.specificationReadOrder(bundlePaths),
            )
            resolvedBundle = SpecificationBundle(
                files=specificationBundle.files,
                structureManifest=manifest,
            )
            taskSections.extend(["", manifest.formatForPrompt()])

        if repairErrors:
            taskSections.extend(
                self._repairSections(
                    repairErrors,
                    repairStructuredErrors,
                    repairInvalidOutput,
                    repairInvalidRawText,
                )
            )

        return LlmRequest(
            model=model,
            instructionFilePaths=instructionFilePaths,
            attachmentFilePaths=attachmentFilePaths,
            taskPrompt="\n".join(taskSections),
            specificationBundle=resolvedBundle,
            responseFormat="json",
            timeoutSeconds=timeoutSeconds,
        )

    def _repairSections(
        self,
        repairErrors: tuple[str, ...],
        repairStructuredErrors: tuple[JudgeValidationErrorRecord, ...] | None,
        repairInvalidOutput: dict[str, Any] | None,
        repairInvalidRawText: str | None,
    ) -> list[str]:
        structuredPayload = [record.toDict() for record in (repairStructuredErrors or ())]
        if not structuredPayload:
            structuredPayload = [
                {"path": "output", "code": "SCHEMA_VIOLATION", "message": error} for error in repairErrors
            ]

        sections = [
            "",
            "## Repair request",
            f"Follow the repair rules in {INITIAL_PROMPT_PATH} (section: What The Host Prompt Contains).",
            f"Return one complete Judge output that satisfies the Mandatory Response Format in {OUTPUT_SCHEMA_PATH}.",
            "",
            "### Structured validation errors",
            json.dumps(structuredPayload, indent=2),
        ]
        if repairInvalidOutput is not None:
            sections.extend(
                [
                    "",
                    "### Invalid previous output (correct this object)",
                    json.dumps(repairInvalidOutput, indent=2),
                ]
            )
        elif repairInvalidRawText:
            sections.extend(
                [
                    "",
                    "### Invalid previous response (non-JSON prose — replace with one JSON object)",
                    repairInvalidRawText,
                ]
            )
        return sections
