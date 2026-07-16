"""Application wrapper separating canonical input from LLM execution config."""

from __future__ import annotations

from dataclasses import dataclass

from Monopoly.LlmEvaluation.Domain.Model.Input.JudgeInput import JudgeInput
from Monopoly.LlmEvaluation.Domain.Model.LlmExecution.LlmExecutionConfig import LlmExecutionConfig


@dataclass(frozen=True, slots=True)
class JudgeEvaluationRequest:
    evaluationInput: JudgeInput
    llmExecution: LlmExecutionConfig
