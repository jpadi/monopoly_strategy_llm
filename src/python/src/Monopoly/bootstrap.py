"""Manual dependency injection wiring for Monopoly modules."""

from __future__ import annotations

from pathlib import Path

from Monopoly.LlmEvaluation.Application.Query.EvaluateTradeWithJudge.EvaluateTradeWithJudgeQuery import (
    EvaluateTradeWithJudgeQuery,
)
from Monopoly.LlmEvaluation.Application.Query.EvaluateTradeWithJudge.EvaluateTradeWithJudgeQueryHandler import (
    EvaluateTradeWithJudgeQueryHandler,
)
from Monopoly.LlmEvaluation.Application.Service.EvaluateTradeWithJudgeService import (
    EvaluateTradeWithJudgeService,
    createDefaultModeResolver,
)
from Monopoly.LlmEvaluation.Domain.Exception.LlmEvaluationErrors import UnsupportedLlmProviderError
from Monopoly.LlmEvaluation.Domain.Port.LlmClient import LlmClient
from Monopoly.LlmEvaluation.Domain.Service.JudgeOutputValidator import JudgeOutputValidator
from Monopoly.LlmEvaluation.Domain.Service.JudgePromptBuilder import JudgePromptBuilder
from Monopoly.LlmEvaluation.Domain.Service.JudgeResponseParser import JudgeResponseParser
from Monopoly.LlmEvaluation.Domain.Service.SpecificationBundleBuilder import SpecificationBundleBuilder
from Monopoly.LlmEvaluation.Infrastructure.Anthropic.ClaudeLlmClient import ClaudeLlmClient
from Monopoly.LlmEvaluation.Infrastructure.Artifact.DefaultJudgeArtifactRecorder import DefaultJudgeArtifactRecorder
from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorLlmClient import CursorLlmClient
from Monopoly.LlmEvaluation.Infrastructure.Google.GeminiLlmClient import GeminiLlmClient
from Monopoly.LlmEvaluation.Infrastructure.OpenAi.OpenAiLlmClient import OpenAiLlmClient
from Monopoly.LlmEvaluation.Infrastructure.Specification.FileSystemSpecificationRepository import (
    FileSystemSpecificationRepository,
)
from Monopoly.LlmEvaluation.Infrastructure.Xai.GrokLlmClient import GrokLlmClient
from Monopoly.Shared.Domain.Bus.QueryBus import QueryBus
from Monopoly.Shared.Infrastructure.EnvironmentLoader import loadRepositoryEnvironment
from Monopoly.StaticEvaluation.Application.Query.EvaluateTrade.EvaluateTradeQuery import (
    EvaluateTradeQuery,
)
from Monopoly.StaticEvaluation.Application.Query.EvaluateTrade.EvaluateTradeQueryHandler import (
    EvaluateTradeQueryHandler,
)
from Monopoly.StaticEvaluation.Application.Query.EvaluateTrade.EvaluateTradeService import (
    EvaluateTradeService,
)
from Monopoly.StaticEvaluation.Domain.Model.Algorithm.StaticTradeEvaluator import (
    StaticTradeEvaluator,
)

loadRepositoryEnvironment()


def repoRoot() -> Path:
    return Path(__file__).resolve().parents[4]


def _repoRoot() -> Path:
    return repoRoot()


def createLlmClient(*, provider: str, docsRoot: Path | None = None) -> LlmClient:
    normalized = provider.strip().lower()
    root = docsRoot or _repoRoot()
    specificationRepository = FileSystemSpecificationRepository(docsRoot=root)
    if normalized == "cursor":
        return CursorLlmClient(specificationRepository=specificationRepository)
    if normalized == "claude" or normalized == "anthropic":
        return ClaudeLlmClient()
    if normalized == "gemini" or normalized == "google":
        return GeminiLlmClient()
    if normalized == "grok" or normalized == "xai":
        return GrokLlmClient()
    if normalized == "openai":
        return OpenAiLlmClient()
    raise UnsupportedLlmProviderError(f"Unsupported LLM provider: {provider}")


def createEvaluateTradeWithJudgeHandler(
    *,
    llmClient: LlmClient | None = None,
    docsRoot: Path | None = None,
) -> EvaluateTradeWithJudgeQueryHandler:
    root = docsRoot or _repoRoot()
    specificationRepository = FileSystemSpecificationRepository(docsRoot=root)
    client = llmClient or CursorLlmClient(specificationRepository=specificationRepository)
    modeResolver = createDefaultModeResolver(specificationRepository=specificationRepository)
    service = EvaluateTradeWithJudgeService(
        llmClient=client,
        modeResolver=modeResolver,
        bundleBuilder=SpecificationBundleBuilder(specificationRepository=specificationRepository),
        promptBuilder=JudgePromptBuilder(),
        responseParser=JudgeResponseParser(),
        outputValidator=JudgeOutputValidator(),
        artifactRecorder=DefaultJudgeArtifactRecorder(),
    )
    return EvaluateTradeWithJudgeQueryHandler(evaluateTradeWithJudgeService=service)


def createEvaluateTradeHandler() -> EvaluateTradeQueryHandler:
    evaluator = StaticTradeEvaluator()
    service = EvaluateTradeService(evaluator=evaluator)
    return EvaluateTradeQueryHandler(evaluateTradeService=service)


def createQueryBus(*, llmClient: LlmClient | None = None) -> QueryBus:
    bus = QueryBus()
    bus.subscribe(EvaluateTradeQuery, createEvaluateTradeHandler().handle)
    bus.subscribe(
        EvaluateTradeWithJudgeQuery,
        createEvaluateTradeWithJudgeHandler(llmClient=llmClient).handle,
    )
    return bus
