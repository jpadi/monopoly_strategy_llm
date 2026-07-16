"""Execution trace for Judge artifact recording."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from Monopoly.LlmEvaluation.Domain.Model.JudgeValidationError import JudgeValidationErrorRecord
from Monopoly.LlmEvaluation.Domain.Port.LlmClient import LlmRequest, LlmResponse


@dataclass(frozen=True, slots=True)
class JudgeExecutionArtifactTrace:
    initialRequest: LlmRequest
    initialResponse: LlmResponse
    initialOutputDict: dict[str, Any] | None = None
    initialParseError: str | None = None
    initialValidationErrors: tuple[str, ...] = ()
    initialStructuredErrors: tuple[JudgeValidationErrorRecord, ...] = ()
    repairAttempted: bool = False
    repairRequest: LlmRequest | None = None
    repairResponse: LlmResponse | None = None
    repairOutputDict: dict[str, Any] | None = None
    repairParseError: str | None = None
    repairValidationErrors: tuple[str, ...] = ()
    repairStructuredErrors: tuple[JudgeValidationErrorRecord, ...] = ()
