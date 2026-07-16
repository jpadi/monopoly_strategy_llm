"""Scenario registry integrity tests."""

from __future__ import annotations

from judge_assertions.judge_scenario_registry import RUNTIME_MODES, SCENARIO_BY_ID
from judge_scenario_registry import JUDGE_RUNTIME_SCENARIOS


def test_unit_registry_matches_shared_source():
    assert RUNTIME_MODES is JUDGE_RUNTIME_SCENARIOS


def test_unit_runtime_mode_ids_are_unique():
    scenario_ids = [scenario.scenario_id for scenario in RUNTIME_MODES]
    assert len(scenario_ids) == len(set(scenario_ids))
    assert len(RUNTIME_MODES) == 9


def test_unit_registry_lookup_matches_list():
    assert len(SCENARIO_BY_ID) == len(RUNTIME_MODES)
