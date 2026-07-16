"""Semantic validation port for integration tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class SemanticAssessmentRequest:
    scenarioId: str
    evaluationInput: dict[str, Any]
    judgeOutput: dict[str, Any]
    model: str


@dataclass(frozen=True, slots=True)
class SemanticAssessmentResult:
    isCorrect: bool
    summary: str
    issues: tuple[str, ...]
    manualReviewNotes: tuple[str, ...]


class SemanticResponseAssessor(Protocol):
    def assess(self, request: SemanticAssessmentRequest) -> SemanticAssessmentResult: ...
