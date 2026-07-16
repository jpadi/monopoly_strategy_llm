"""Map wrapped request JSON to JudgeEvaluationRequest."""

from __future__ import annotations

from typing import Any

from Monopoly.LlmEvaluation.Domain.Model.LlmExecution.LlmExecutionConfig import LlmExecutionConfig
from Monopoly.LlmEvaluation.Domain.Model.Request.JudgeEvaluationRequest import JudgeEvaluationRequest
from Monopoly.LlmEvaluation.Infrastructure.Json.JudgeInputMapper import JudgeInputMapper


class JudgeRequestMapper:
    @classmethod
    def fromDict(cls, data: dict[str, Any]) -> JudgeEvaluationRequest:
        evaluationInput = JudgeInputMapper.fromDict(data.get("evaluation_input", data))
        llmExecutionData = data.get("llm_execution", {})
        llmExecution = LlmExecutionConfig(
            provider=str(llmExecutionData.get("provider", "fake")),
            model=str(llmExecutionData.get("model", "")),
            timeoutSeconds=llmExecutionData.get("timeout_seconds"),
            temperature=llmExecutionData.get("temperature"),
        )
        return JudgeEvaluationRequest(
            evaluationInput=evaluationInput,
            llmExecution=llmExecution,
        )
