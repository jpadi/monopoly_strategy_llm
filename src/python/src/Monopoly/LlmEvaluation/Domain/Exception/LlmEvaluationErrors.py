"""Domain exceptions for the LLM Judge module."""

from typing import Any


class LlmEvaluationError(Exception):
    """Base exception for LLM Evaluation module."""


class JudgeInputValidationError(LlmEvaluationError):
    """Canonical input failed validation."""


class JudgeOutputParseError(LlmEvaluationError):
    """LLM response could not be parsed as JSON."""


class JudgeOutputSchemaViolationError(LlmEvaluationError):
    """Parsed output failed schema or mode-consistency validation."""

    def __init__(
        self,
        message: str,
        errors: tuple[str, ...] = (),
        structuredErrors: tuple[Any, ...] = (),
    ) -> None:
        super().__init__(message)
        self.errors = errors
        self.structuredErrors = structuredErrors


class JudgeRepairFailureError(LlmEvaluationError):
    """Initial validation failed and the single repair attempt did not produce valid output."""

    def __init__(
        self,
        message: str,
        *,
        initialValidationErrors: tuple[str, ...] = (),
        initialStructuredErrors: tuple[Any, ...] = (),
        repairParseError: str | None = None,
        repairValidationErrors: tuple[str, ...] = (),
        repairStructuredErrors: tuple[Any, ...] = (),
        artifactTrace: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.initialValidationErrors = initialValidationErrors
        self.initialStructuredErrors = initialStructuredErrors
        self.repairParseError = repairParseError
        self.repairValidationErrors = repairValidationErrors
        self.repairStructuredErrors = repairStructuredErrors
        self.artifactTrace = artifactTrace


class FallbackEligibilityError(LlmEvaluationError):
    """Fallback prerequisites could not be verified."""


class LlmProviderError(LlmEvaluationError):
    """Provider call failed."""


class UnsupportedLlmProviderError(LlmProviderError):
    """Requested provider is not implemented."""
