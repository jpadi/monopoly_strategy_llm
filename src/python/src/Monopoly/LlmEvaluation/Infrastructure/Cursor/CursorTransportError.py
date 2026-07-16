"""Cursor transport normalization errors."""

from __future__ import annotations

from Monopoly.LlmEvaluation.Domain.Exception.LlmEvaluationErrors import LlmProviderError


class CursorTransportError(LlmProviderError):
    """Cursor response transport envelope or file retrieval failed."""

    def __init__(self, message: str, *, stage: str, details: dict[str, object] | None = None) -> None:
        super().__init__(message)
        self.stage = stage
        self.details = details or {}
