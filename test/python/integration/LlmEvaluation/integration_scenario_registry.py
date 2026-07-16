"""Integration scenario registry — re-exports shared Judge runtime scenarios."""

from __future__ import annotations

from judge_scenario_registry import (
    INTEGRATION_SCENARIOS,
    JUDGE_RUNTIME_SCENARIOS,
    IntegrationJudgeScenario,
)

__all__ = (
    "INTEGRATION_SCENARIOS",
    "IntegrationJudgeScenario",
    "JUDGE_RUNTIME_SCENARIOS",
)
