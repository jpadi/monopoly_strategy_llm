"""Shared fixtures for output-field verification tests."""

from __future__ import annotations

from typing import Any

import pytest
from fixtures import scenarioInputs

from .output_field_coverage import get_required_scenarios

_EVIDENCE_CACHE: dict[str, dict[str, Any]] = {}


@pytest.fixture
def scenario_evidence_cache(execute_scenario) -> dict[str, dict[str, Any]]:
    """Execute each scenario referenced by output-field coverage once per session."""
    if not _EVIDENCE_CACHE:
        for scenario_name in sorted(get_required_scenarios()):
            loader = getattr(scenarioInputs, scenario_name)
            input_data = loader()
            _EVIDENCE_CACHE[scenario_name] = execute_scenario(input_data)
            _EVIDENCE_CACHE[f"{scenario_name}__input"] = input_data
    return _EVIDENCE_CACHE
