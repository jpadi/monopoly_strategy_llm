"""Semantic assessor using LLM for integration tests."""

from __future__ import annotations

from Monopoly.LlmEvaluation.Domain.Port.LlmClient import LlmClient, LlmRequest
from Monopoly.LlmEvaluation.Domain.Port.SemanticResponseAssessor import (
    SemanticAssessmentRequest,
    SemanticAssessmentResult,
    SemanticResponseAssessor,
)


class LlmSemanticResponseAssessor(SemanticResponseAssessor):
    def __init__(self, *, llmClient: LlmClient, model: str) -> None:
        self._llmClient = llmClient
        self._model = model

    def assess(self, request: SemanticAssessmentRequest) -> SemanticAssessmentResult:
        prompt = (
            "Assess whether the Judge output is correct for the scenario. "
            'Return JSON: {"is_correct": bool, "summary": str, "issues": [], '
            '"manual_review_notes": []}\n'
            f"Scenario: {request.scenarioId}\n"
            f"Output: {request.judgeOutput}"
        )
        response = self._llmClient.complete(
            LlmRequest(
                model=self._model,
                instructionFilePaths=(),
                attachmentFilePaths=(),
                taskPrompt=prompt,
                specificationBundle=None,
            )
        )
        import json

        try:
            parsed = json.loads(response.rawText)
        except json.JSONDecodeError:
            return SemanticAssessmentResult(
                isCorrect=False,
                summary="Assessor returned non-JSON",
                issues=("Non-JSON assessor response",),
                manualReviewNotes=(),
            )
        return SemanticAssessmentResult(
            isCorrect=bool(parsed.get("is_correct", False)),
            summary=str(parsed.get("summary", "")),
            issues=tuple(str(i) for i in parsed.get("issues", [])),
            manualReviewNotes=tuple(str(n) for n in parsed.get("manual_review_notes", [])),
        )
