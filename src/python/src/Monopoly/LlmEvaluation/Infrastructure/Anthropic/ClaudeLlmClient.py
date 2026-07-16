"""Stub Claude adapter — not implemented in v1.2.0."""

from Monopoly.LlmEvaluation.Domain.Exception.LlmEvaluationErrors import UnsupportedLlmProviderError
from Monopoly.LlmEvaluation.Domain.Port.LlmClient import LlmClient, LlmRequest, LlmResponse


class ClaudeLlmClient(LlmClient):
    def complete(self, request: LlmRequest) -> LlmResponse:
        raise UnsupportedLlmProviderError(
            "Claude provider is not implemented in v1.2.0; requires ANTHROPIC_API_KEY and Files API upload"
        )
