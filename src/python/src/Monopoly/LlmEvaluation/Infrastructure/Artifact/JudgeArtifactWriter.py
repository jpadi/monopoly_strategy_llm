"""Write sanitized Judge run artifacts to the project artifact directory."""

from __future__ import annotations

import hashlib
from typing import Any

from Monopoly.LlmEvaluation.Domain.Model.Artifact.JudgeExecutionArtifactTrace import JudgeExecutionArtifactTrace
from Monopoly.LlmEvaluation.Domain.Model.Request.JudgeEvaluationRequest import JudgeEvaluationRequest
from Monopoly.LlmEvaluation.Domain.Model.Runtime.ResolvedRuntimePlan import ResolvedRuntimePlan
from Monopoly.LlmEvaluation.Domain.Port.LlmClient import LlmRequest, LlmResponse
from Monopoly.Shared.Infrastructure.ArtifactStore import (
    currentArtifactSubpath,
    timestampSlug,
    writeArtifact,
    writeArtifactJson,
)


class JudgeArtifactWriter:
    @staticmethod
    def writeExecutionArtifacts(
        *,
        request: JudgeEvaluationRequest,
        runtimePlan: ResolvedRuntimePlan,
        trace: JudgeExecutionArtifactTrace,
        finalOutputDict: dict[str, Any] | None = None,
    ) -> str:
        evaluationId = str(request.evaluationInput.metadata.get("evaluation_id", "unknown"))
        runId = f"{evaluationId}_{timestampSlug()}"
        subpath = currentArtifactSubpath()
        base = subpath if subpath else f"llm_judge/{runId}"

        activeRequest = trace.repairRequest if trace.repairAttempted and trace.repairRequest else trace.initialRequest
        activeResponse = (
            trace.repairResponse if trace.repairAttempted and trace.repairResponse else trace.initialResponse
        )

        JudgeArtifactWriter._writeRequestSummary(
            base=base,
            request=request,
            runtimePlan=runtimePlan,
            llmRequest=activeRequest,
            runId=runId,
            evaluationId=evaluationId,
            repairAttempted=trace.repairAttempted,
        )
        writeArtifact(f"{base}/initial_llm_response.txt", trace.initialResponse.rawText)
        JudgeArtifactWriter._writeProviderTransportDiagnostics(base=base, response=trace.initialResponse)
        if trace.initialOutputDict is not None:
            writeArtifactJson(f"{base}/initial_output.json", trace.initialOutputDict)
        if trace.initialParseError is not None:
            writeArtifactJson(f"{base}/initial_parse_error.json", {"message": trace.initialParseError})
        if trace.initialValidationErrors:
            writeArtifactJson(
                f"{base}/initial_validation_errors.json",
                {
                    "errors": list(trace.initialValidationErrors),
                    "structured_errors": [record.toDict() for record in trace.initialStructuredErrors],
                },
            )

        if trace.repairAttempted:
            JudgeArtifactWriter._writeRepairArtifacts(base=base, trace=trace)

        writeArtifact(f"{base}/llm_response.txt", activeResponse.rawText)
        JudgeArtifactWriter._writeProviderTransportDiagnostics(base=base, response=activeResponse)
        if finalOutputDict is not None:
            writeArtifactJson(f"{base}/output.json", finalOutputDict)

        return runId

    @staticmethod
    def _writeRepairArtifacts(*, base: str, trace: JudgeExecutionArtifactTrace) -> None:
        if trace.repairRequest is not None:
            writeArtifactJson(
                f"{base}/repair_request_summary.json",
                {
                    "instruction_file_paths": list(trace.repairRequest.instructionFilePaths),
                    "attachment_file_paths": list(trace.repairRequest.attachmentFilePaths),
                    "task_prompt_byte_count": len(trace.repairRequest.taskPrompt.encode("utf-8")),
                    "includes_invalid_previous_output": JudgeArtifactWriter.repairInvalidOutputIncluded(
                        trace.repairRequest
                    ),
                },
            )
        if trace.repairResponse is not None:
            writeArtifact(f"{base}/repair_response.txt", trace.repairResponse.rawText)
        if trace.repairParseError is not None:
            writeArtifactJson(f"{base}/repair_parse_error.json", {"message": trace.repairParseError})
        if trace.repairOutputDict is not None:
            writeArtifactJson(f"{base}/repair_output.json", trace.repairOutputDict)
        if trace.repairValidationErrors:
            writeArtifactJson(
                f"{base}/repair_validation_errors.json",
                {
                    "errors": list(trace.repairValidationErrors),
                    "structured_errors": [record.toDict() for record in trace.repairStructuredErrors],
                },
            )

    @staticmethod
    def repairInvalidOutputIncluded(repairRequest: LlmRequest) -> bool:
        return "### Invalid previous output (correct this object)" in repairRequest.taskPrompt

    @staticmethod
    def _writeRequestSummary(
        *,
        base: str,
        request: JudgeEvaluationRequest,
        runtimePlan: ResolvedRuntimePlan,
        llmRequest: LlmRequest,
        runId: str,
        evaluationId: str,
        repairAttempted: bool,
    ) -> None:
        manifest = (
            llmRequest.specificationBundle.structureManifest if llmRequest.specificationBundle is not None else None
        )
        writeArtifactJson(
            f"{base}/request_summary.json",
            {
                "evaluation_id": evaluationId,
                "run_id": runId,
                "provider": request.llmExecution.provider,
                "model": request.llmExecution.model,
                "requested_mode": runtimePlan.requestedMode,
                "execution_mode": runtimePlan.executionMode,
                "evidence_source": runtimePlan.evidenceSource,
                "expected_execution_status": runtimePlan.expectedExecutionStatus,
                "fallback_bundle_required": runtimePlan.bundleRequired,
                "repair_attempted": repairAttempted,
                "instruction_file_paths": list(llmRequest.instructionFilePaths),
                "attachment_file_paths": list(llmRequest.attachmentFilePaths),
                "manifest_paths": list(manifest.deliveredFilePaths) if manifest else [],
                "instruction_file_count": len(llmRequest.instructionFilePaths),
                "attachment_count": len(llmRequest.attachmentFilePaths),
                "instruction_files": JudgeArtifactWriter._instructionInventory(
                    llmRequest.instructionFilePaths,
                    llmRequest.specificationBundle,
                ),
                "attachment_files": JudgeArtifactWriter._fileInventory(
                    llmRequest.attachmentFilePaths,
                    llmRequest.specificationBundle,
                ),
            },
        )

    @staticmethod
    def _instructionInventory(
        instructionFilePaths: tuple[str, ...],
        specificationBundle: Any,
    ) -> list[dict[str, Any]]:
        bundleByPath = {}
        if specificationBundle is not None:
            bundleByPath = {item.relativePath: item.content for item in specificationBundle.files}
        return [JudgeArtifactWriter._entryForPath(path, bundleByPath.get(path)) for path in instructionFilePaths]

    @staticmethod
    def _fileInventory(
        attachmentFilePaths: tuple[str, ...],
        specificationBundle: Any,
    ) -> list[dict[str, Any]]:
        bundleByPath = {}
        if specificationBundle is not None:
            bundleByPath = {item.relativePath: item.content for item in specificationBundle.files}
        return [JudgeArtifactWriter._entryForPath(path, bundleByPath.get(path)) for path in attachmentFilePaths]

    @staticmethod
    def _writeProviderTransportDiagnostics(*, base: str, response: LlmResponse) -> None:
        metadata = response.providerMetadata
        if not metadata:
            return
        writeArtifactJson(f"{base}/provider_transport_diagnostics.json", metadata)
        originalRawText = metadata.get("original_raw_text")
        if isinstance(originalRawText, str) and originalRawText and originalRawText != response.rawText:
            writeArtifact(f"{base}/initial_provider_response.txt", originalRawText)

    @staticmethod
    def _entryForPath(path: str, content: bytes | None) -> dict[str, Any]:
        if content is None:
            return {"path": path, "byte_count": None, "sha256": None}
        return {
            "path": path,
            "byte_count": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
        }
