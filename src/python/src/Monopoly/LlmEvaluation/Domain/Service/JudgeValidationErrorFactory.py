"""Helpers for building structured validation error records."""

from __future__ import annotations

from Monopoly.LlmEvaluation.Domain.Model.JudgeValidationError import JudgeValidationErrorRecord


def unknownDependentCalculationId(*, path: str, calculationId: str) -> JudgeValidationErrorRecord:
    return JudgeValidationErrorRecord(
        path=path,
        code="UNKNOWN_DEPENDENT_CALCULATION_ID",
        message=f"Calculation ID {calculationId!r} does not exist in this evidence object.",
    )


def selfDependency(*, path: str, calculationId: str) -> JudgeValidationErrorRecord:
    return JudgeValidationErrorRecord(
        path=path,
        code="SELF_DEPENDENCY",
        message=f"Calculation {calculationId!r} must not reference itself.",
    )


def duplicateCalculationId(*, path: str, calculationId: str) -> JudgeValidationErrorRecord:
    return JudgeValidationErrorRecord(
        path=path,
        code="DUPLICATE_CALCULATION_ID",
        message=f"Duplicate calculation id {calculationId!r}.",
    )


def unknownFinalConclusionReference(*, path: str, calculationId: str) -> JudgeValidationErrorRecord:
    return JudgeValidationErrorRecord(
        path=path,
        code="UNKNOWN_FINAL_CONCLUSION_REFERENCE",
        message=f"Final conclusion references unknown calculation id {calculationId!r}.",
    )


def invalidFallbackEvidenceComplete(*, path: str) -> JudgeValidationErrorRecord:
    return JudgeValidationErrorRecord(
        path=path,
        code="INVALID_FALLBACK_EVIDENCE",
        message="execution_status COMPLETE not permitted when generated_static_algorithm_evidence is schema-invalid.",
    )


def outputParseError(*, message: str) -> JudgeValidationErrorRecord:
    return JudgeValidationErrorRecord(
        path="output",
        code="OUTPUT_PARSE_ERROR",
        message=message,
    )


def genericSchemaViolation(*, path: str, message: str, code: str = "SCHEMA_VIOLATION") -> JudgeValidationErrorRecord:
    return JudgeValidationErrorRecord(path=path, code=code, message=message)
