"""Stub Gemini adapter — not implemented in v1.2.0."""

from Monopoly.LlmEvaluation.Domain.Exception.LlmEvaluationErrors import UnsupportedLlmProviderError
from Monopoly.LlmEvaluation.Domain.Port.LlmClient import LlmClient, LlmRequest, LlmResponse


class GeminiLlmClient(LlmClient):
    def complete(self, request: LlmRequest) -> LlmResponse:
        raise UnsupportedLlmProviderError(
            "Gemini provider is not implemented in v1.2.0; requires GEMINI_API_KEY and per-file upload"
        )
