"""Fixture loader for LLM Judge tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

FIXTURE_ROOT = Path(__file__).parent


def loadJudgeFixture(relativePath: str) -> dict[str, Any]:
    path = FIXTURE_ROOT / relativePath
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def loadProviderResponse(scenarioId: str) -> dict[str, Any]:
    return loadJudgeFixture(f"provider_responses/{scenarioId}.json")


def loadCanonicalFallbackEvidence() -> dict[str, Any]:
    return loadJudgeFixture("static_evidence/minimal_valid_fallback_evidence.json")


def loadProviderResponseWithFallbackEvidence(scenarioId: str) -> dict[str, Any]:
    response = loadProviderResponse(scenarioId)
    if scenarioId in {"fallback_authorized", "allow_llm_fallback_mode"}:
        evidence = loadCanonicalFallbackEvidence()
        response = dict(response)
        static = dict(response["static_analysis_result"])
        static["generated_static_algorithm_evidence"] = [evidence]
        response["static_analysis_result"] = static
    return response
