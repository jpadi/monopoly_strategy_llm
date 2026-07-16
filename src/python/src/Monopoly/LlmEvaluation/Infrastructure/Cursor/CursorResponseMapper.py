"""Map Cursor SDK RunResult to provider-neutral LlmResponse fields."""

from __future__ import annotations

from typing import Any

from Monopoly.LlmEvaluation.Domain.Port.LlmClient import LlmResponse
from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorTransportDiagnostics import CursorTransportDiagnostics


class CursorResponseMapper:
    @staticmethod
    def toLlmResponse(
        *,
        normalizedText: str,
        modelUsed: str,
        result: Any,
        diagnostics: CursorTransportDiagnostics,
    ) -> LlmResponse:
        usage = getattr(result, "usage", None)
        tokenUsage = None
        if usage is not None:
            tokenUsage = {
                "input_tokens": getattr(usage, "input_tokens", None),
                "output_tokens": getattr(usage, "output_tokens", None),
                "total_tokens": getattr(usage, "total_tokens", None),
            }

        metadata = diagnostics.toProviderMetadata()
        metadata["run_id"] = getattr(result, "id", None)
        metadata["duration_ms"] = getattr(result, "duration_ms", None)

        return LlmResponse(
            rawText=normalizedText,
            modelUsed=modelUsed,
            finishReason=str(getattr(result, "status", "stop")),
            tokenUsage=tokenUsage,
            providerMetadata=metadata,
        )
