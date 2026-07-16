"""Application-level LLM execution configuration (not part of canonical Judge input)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LlmExecutionConfig:
    provider: str
    model: str
    timeoutSeconds: int | None = None
    temperature: float | None = None

    def validate(self) -> None:
        if not self.provider or not self.provider.strip():
            raise ValueError("llm_execution.provider is required")
        if not self.model or not self.model.strip():
            raise ValueError("llm_execution.model is required")
