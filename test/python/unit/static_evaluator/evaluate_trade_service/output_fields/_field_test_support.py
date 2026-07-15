"""Shared helpers for category-based output-field unit tests."""

from __future__ import annotations

from typing import Any

import pytest

from .output_field_assertion_handlers import FIELD_ASSERTION_HANDLERS
from .output_field_coverage import OutputFieldCoverageEntry, get_coverage_by_module


def build_field_test_params(test_module: str) -> list[OutputFieldCoverageEntry]:
    """Return non-waived coverage entries for a test module."""
    return [entry for entry in get_coverage_by_module(test_module) if not entry.waived]


def run_field_assertion(
    entry: OutputFieldCoverageEntry,
    scenario_evidence_cache: dict[str, Any],
) -> None:
    """Execute the focused assertion handler for one canonical output field."""
    handler = FIELD_ASSERTION_HANDLERS[entry.field_key]
    evidence = scenario_evidence_cache[entry.scenario_function]
    input_data = scenario_evidence_cache[f"{entry.scenario_function}__input"]
    handler(evidence, input_data, entry.scenario_function)


def make_parametrize_decorator(test_module: str):
    """Build a pytest parametrize decorator for a category test module."""
    entries = build_field_test_params(test_module)
    return pytest.mark.parametrize(
        "coverage_entry",
        entries,
        ids=[entry.field_key for entry in entries],
    )
