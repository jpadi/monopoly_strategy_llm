"""Validate Judge output schema and mode consistency."""

from __future__ import annotations

from typing import Any

from Monopoly.LlmEvaluation.Domain.Exception.LlmEvaluationErrors import JudgeOutputSchemaViolationError
from Monopoly.LlmEvaluation.Domain.Model.JudgeEnums import (
    EvidenceSource,
    ExecutionStatus,
    RuntimeExecutionMode,
)
from Monopoly.LlmEvaluation.Domain.Model.JudgeValidationError import JudgeValidationErrorRecord
from Monopoly.LlmEvaluation.Domain.Model.Output.JudgeOutput import JudgeOutput
from Monopoly.LlmEvaluation.Domain.Model.Runtime.ResolvedRuntimePlan import ResolvedRuntimePlan
from Monopoly.LlmEvaluation.Domain.Service.GeneratedStaticAlgorithmEvidenceValidator import (
    GeneratedStaticAlgorithmEvidenceValidator,
)
from Monopoly.LlmEvaluation.Domain.Service.JudgeOutputSchemaValidator import validateJudgeOutputStructure
from Monopoly.LlmEvaluation.Domain.Service.JudgeValidationErrorFactory import (
    genericSchemaViolation,
    invalidFallbackEvidenceComplete,
)


class JudgeOutputValidator:
    def __init__(self, *, evidenceValidator: GeneratedStaticAlgorithmEvidenceValidator | None = None) -> None:
        self._evidenceValidator = evidenceValidator or GeneratedStaticAlgorithmEvidenceValidator()

    def validate(self, outputDict: dict[str, Any], runtimePlan: ResolvedRuntimePlan) -> JudgeOutput:
        errors: list[str] = []
        structuredErrors: list[JudgeValidationErrorRecord] = []

        for message in validateJudgeOutputStructure(outputDict):
            errors.append(message)
            structuredErrors.append(
                genericSchemaViolation(path="output", message=message, code="OUTPUT_SCHEMA_VIOLATION")
            )

        staticResult = outputDict.get("static_analysis_result", {})
        if isinstance(staticResult, dict):
            staticMessages, staticRecords = self._validateStaticAnalysisResult(staticResult, runtimePlan)
            errors.extend(staticMessages)
            structuredErrors.extend(staticRecords)

        if errors:
            raise JudgeOutputSchemaViolationError(
                "Judge output validation failed",
                errors=tuple(errors),
                structuredErrors=tuple(structuredErrors),
            )
        return JudgeOutput(sections=outputDict)

    def _validateStaticAnalysisResult(
        self,
        staticResult: dict[str, Any],
        runtimePlan: ResolvedRuntimePlan,
    ) -> tuple[list[str], list[JudgeValidationErrorRecord]]:
        errors: list[str] = []
        structuredErrors: list[JudgeValidationErrorRecord] = []

        if staticResult.get("execution_mode") != runtimePlan.executionMode:
            message = (
                f"execution_mode mismatch: expected {runtimePlan.executionMode}, "
                f"got {staticResult.get('execution_mode')}"
            )
            errors.append(message)
            structuredErrors.append(
                genericSchemaViolation(
                    path="static_analysis_result.execution_mode",
                    message=message,
                    code="EXECUTION_MODE_MISMATCH",
                )
            )

        expectedSource = runtimePlan.evidenceSource
        actualSource = staticResult.get("evidence_source")
        if runtimePlan.executionMode == RuntimeExecutionMode.NO_STATIC_ANALYSIS:
            if actualSource is not None:
                message = "evidence_source must be null for NO_STATIC_ANALYSIS"
                errors.append(message)
                structuredErrors.append(
                    genericSchemaViolation(
                        path="static_analysis_result.evidence_source",
                        message=message,
                        code="EVIDENCE_SOURCE_INVALID",
                    )
                )
        elif actualSource != expectedSource:
            message = f"evidence_source mismatch: expected {expectedSource}, got {actualSource}"
            errors.append(message)
            structuredErrors.append(
                genericSchemaViolation(
                    path="static_analysis_result.evidence_source",
                    message=message,
                    code="EVIDENCE_SOURCE_MISMATCH",
                )
            )

        if runtimePlan.executionMode == RuntimeExecutionMode.LLM_STATIC_FALLBACK:
            evidenceMessages, evidenceRecords = self._validateGeneratedFallbackEvidence(staticResult)
            errors.extend(evidenceMessages)
            structuredErrors.extend(evidenceRecords)

        if runtimePlan.executionMode == RuntimeExecutionMode.STATIC_EVIDENCE_PROVIDED:
            if staticResult.get("evidence_source") != EvidenceSource.SUPPLIED_STATIC_SOFTWARE:
                message = "evidence_source must be SUPPLIED_STATIC_SOFTWARE"
                errors.append(message)
                structuredErrors.append(
                    genericSchemaViolation(
                        path="static_analysis_result.evidence_source",
                        message=message,
                        code="EVIDENCE_SOURCE_MISMATCH",
                    )
                )

        return errors, structuredErrors

    def _validateGeneratedFallbackEvidence(
        self,
        staticResult: dict[str, Any],
    ) -> tuple[list[str], list[JudgeValidationErrorRecord]]:
        errors: list[str] = []
        structuredErrors: list[JudgeValidationErrorRecord] = []
        generated = staticResult.get("generated_static_algorithm_evidence")
        if not generated:
            message = "generated_static_algorithm_evidence required for LLM_STATIC_FALLBACK"
            errors.append(message)
            structuredErrors.append(
                genericSchemaViolation(
                    path="static_analysis_result.generated_static_algorithm_evidence",
                    message=message,
                    code="MISSING_FALLBACK_EVIDENCE",
                )
            )
            return errors, structuredErrors
        if not isinstance(generated, list):
            message = "generated_static_algorithm_evidence must be an array"
            errors.append(message)
            structuredErrors.append(
                genericSchemaViolation(
                    path="static_analysis_result.generated_static_algorithm_evidence",
                    message=message,
                    code="INVALID_FALLBACK_EVIDENCE",
                )
            )
            return errors, structuredErrors

        evidenceErrors: list[str] = []
        evidenceRecords: list[JudgeValidationErrorRecord] = []
        for index, evidence in enumerate(generated):
            path = f"static_analysis_result.generated_static_algorithm_evidence[{index}]"
            if not isinstance(evidence, dict):
                message = f"{path} must be an object"
                evidenceErrors.append(message)
                evidenceRecords.append(genericSchemaViolation(path=path, message=message))
                continue
            evidenceErrors.extend(self._evidenceValidator.validate(evidence, path=path))
            evidenceRecords.extend(self._evidenceValidator.lastStructuredErrors)

        errors.extend(evidenceErrors)
        structuredErrors.extend(evidenceRecords)

        executionStatus = staticResult.get("execution_status")
        if executionStatus == ExecutionStatus.COMPLETE.value:
            if evidenceErrors:
                record = invalidFallbackEvidenceComplete(path="static_analysis_result.execution_status")
                structuredErrors.append(record)
                errors.append(record.message)
            for index, evidence in enumerate(generated):
                if isinstance(evidence, dict):
                    path = f"static_analysis_result.generated_static_algorithm_evidence[{index}]"
                    errors.extend(self._evidenceValidator.validateForCompleteExecution(evidence, path=path))
        return errors, structuredErrors
