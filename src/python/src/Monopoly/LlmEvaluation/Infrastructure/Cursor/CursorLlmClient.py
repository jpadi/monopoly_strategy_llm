"""Cursor Agent SDK adapter."""

from __future__ import annotations

import os
from typing import Any

from Monopoly.LlmEvaluation.Domain.Exception.LlmEvaluationErrors import LlmProviderError
from Monopoly.LlmEvaluation.Domain.Port.LlmClient import LlmClient, LlmRequest, LlmResponse
from Monopoly.LlmEvaluation.Domain.Port.SpecificationRepository import SpecificationRepository
from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorExecutionWorkspace import CursorExecutionWorkspace
from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorResponseMapper import CursorResponseMapper
from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorTransportError import CursorTransportError
from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorTransportInstruction import CursorTransportInstruction
from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorTransportNormalizer import CursorTransportNormalizer
from Monopoly.LlmEvaluation.Infrastructure.Specification.LlmPromptAssembler import LlmPromptAssembler


class CursorLlmClient(LlmClient):
    def __init__(
        self,
        *,
        apiKey: str | None = None,
        specificationRepository: SpecificationRepository,
        promptAssembler: LlmPromptAssembler | None = None,
    ) -> None:
        self._apiKey = apiKey or os.environ.get("CURSOR_API_KEY", "")
        self._promptAssembler = promptAssembler or LlmPromptAssembler(
            specificationRepository=specificationRepository,
        )

    def complete(self, request: LlmRequest) -> LlmResponse:
        if not self._apiKey:
            raise LlmProviderError("CURSOR_API_KEY is not configured")

        try:
            from cursor_sdk import Agent, AgentOptions  # type: ignore[import-untyped]
        except ImportError as exc:
            raise LlmProviderError("cursor-sdk is not installed; install with: pip install cursor-sdk") from exc

        workspace = CursorExecutionWorkspace.create()
        prompt = CursorTransportInstruction.appendToPrompt(self._promptAssembler.assemble(request))

        try:
            agent = Agent.create(
                AgentOptions(
                    api_key=self._apiKey,
                    model={"id": request.model},
                    local={"cwd": os.fspath(workspace.root)},
                ),
            )
            try:
                result = agent.send(prompt).wait()
                rawProviderText = CursorLlmClient._extractProviderText(result)
                normalizedText, diagnostics = CursorTransportNormalizer.normalize(
                    rawProviderText=rawProviderText,
                    workspaceRoot=workspace.root,
                    agent=agent,
                )
                return CursorResponseMapper.toLlmResponse(
                    normalizedText=normalizedText,
                    modelUsed=request.model,
                    result=result,
                    diagnostics=diagnostics,
                )
            finally:
                agent.close()
        except CursorTransportError:
            raise
        except Exception as exc:
            raise LlmProviderError(f"Cursor agent call failed: {exc}") from exc
        finally:
            workspace.cleanup()

    @staticmethod
    def _extractProviderText(result: Any) -> str:
        rawText = getattr(result, "result", "") or ""
        if not rawText:
            textAccessor = getattr(result, "text", None)
            if callable(textAccessor):
                rawText = textAccessor()
        if not rawText:
            rawText = str(result)
        return rawText
