"""Integration scenario registry integrity tests."""

from __future__ import annotations

from judge_scenario_registry import JUDGE_RUNTIME_SCENARIOS

from integration.LlmEvaluation.integration_scenario_registry import INTEGRATION_SCENARIOS


def test_integration_registry_matches_shared_source():
    assert INTEGRATION_SCENARIOS is JUDGE_RUNTIME_SCENARIOS


def test_integration_runtime_mode_ids_are_unique():
    scenario_ids = [scenario.scenario_id for scenario in INTEGRATION_SCENARIOS]
    assert len(scenario_ids) == len(set(scenario_ids))
    assert len(INTEGRATION_SCENARIOS) == 9
