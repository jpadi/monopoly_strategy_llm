"""Shared Judge runtime scenario registry for unit, functional, and integration tests."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class JudgeRuntimeScenario:
    scenario_id: str
    input_fixture: str
    expected_execution_mode: str
    expected_evidence_source: str | None
    expected_execution_status: str
    provider_response: str
    expects_spec_bundle: bool = False
    expects_llm_call: bool = True
    expects_validation_error: bool = False

    @property
    def expects_bundle(self) -> bool:
        return self.expects_spec_bundle


IntegrationJudgeScenario = JudgeRuntimeScenario
JudgeScenarioExpectation = JudgeRuntimeScenario

JUDGE_RUNTIME_SCENARIOS: tuple[JudgeRuntimeScenario, ...] = (
    JudgeRuntimeScenario(
        "competitive_only",
        "competitive_only.json",
        "NO_STATIC_ANALYSIS",
        None,
        "UNAVAILABLE",
        "competitive_only",
    ),
    JudgeRuntimeScenario(
        "disable_static_analysis",
        "disable_static_analysis.json",
        "NO_STATIC_ANALYSIS",
        None,
        "NOT_REQUESTED",
        "disable_static_analysis",
    ),
    JudgeRuntimeScenario(
        "require_evidence_missing",
        "require_evidence_missing.json",
        "NO_STATIC_ANALYSIS",
        None,
        "UNAVAILABLE",
        "require_evidence_missing",
    ),
    JudgeRuntimeScenario(
        "fallback_not_authorized",
        "fallback_not_authorized.json",
        "NO_STATIC_ANALYSIS",
        None,
        "UNAVAILABLE",
        "fallback_not_authorized",
    ),
    JudgeRuntimeScenario(
        "supplied_evidence_unusable",
        "supplied_evidence_unusable.json",
        "NO_STATIC_ANALYSIS",
        None,
        "UNAVAILABLE",
        "supplied_evidence_unusable",
    ),
    JudgeRuntimeScenario(
        "supplied_evidence_usable",
        "supplied_evidence_usable.json",
        "STATIC_EVIDENCE_PROVIDED",
        "SUPPLIED_STATIC_SOFTWARE",
        "COMPLETE",
        "supplied_evidence_usable",
    ),
    JudgeRuntimeScenario(
        "supplied_evidence_partial",
        "supplied_evidence_partial.json",
        "STATIC_EVIDENCE_PROVIDED",
        "SUPPLIED_STATIC_SOFTWARE",
        "PARTIAL",
        "supplied_evidence_partial",
    ),
    JudgeRuntimeScenario(
        "fallback_authorized",
        "fallback_authorized.json",
        "LLM_STATIC_FALLBACK",
        "LLM_FALLBACK_GENERATED",
        "COMPLETE",
        "fallback_authorized",
        expects_spec_bundle=True,
    ),
    JudgeRuntimeScenario(
        "allow_llm_fallback_mode",
        "allow_llm_fallback_mode.json",
        "LLM_STATIC_FALLBACK",
        "LLM_FALLBACK_GENERATED",
        "COMPLETE",
        "allow_llm_fallback_mode",
        expects_spec_bundle=True,
    ),
)

INTEGRATION_SCENARIOS = JUDGE_RUNTIME_SCENARIOS
RUNTIME_MODES = JUDGE_RUNTIME_SCENARIOS
SCENARIOS = JUDGE_RUNTIME_SCENARIOS
SCENARIO_BY_ID = {scenario.scenario_id: scenario for scenario in JUDGE_RUNTIME_SCENARIOS}
