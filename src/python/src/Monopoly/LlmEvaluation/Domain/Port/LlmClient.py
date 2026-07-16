"""Provider-neutral LLM port."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from Monopoly.LlmEvaluation.Domain.Model.Specification.SpecificationBundle import SpecificationBundle


@dataclass(frozen=True, slots=True)
class LlmRequest:
    model: str
    instructionFilePaths: tuple[str, ...]
    attachmentFilePaths: tuple[str, ...]
    taskPrompt: str
    specificationBundle: SpecificationBundle | None
    responseFormat: str = "json"
    timeoutSeconds: int | None = None


@dataclass(frozen=True, slots=True)
class LlmResponse:
    rawText: str
    modelUsed: str
    finishReason: str | None = None
    tokenUsage: dict[str, Any] | None = None
    providerMetadata: dict[str, Any] | None = None


class LlmClient(Protocol):
    def complete(self, request: LlmRequest) -> LlmResponse: ...
