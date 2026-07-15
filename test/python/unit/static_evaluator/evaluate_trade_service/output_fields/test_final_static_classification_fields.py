"""Focused unit tests for Final Static Classification Fields output fields."""

from __future__ import annotations

from ._field_test_support import make_parametrize_decorator, run_field_assertion
from .output_field_coverage import OutputFieldCoverageEntry

_parametrize = make_parametrize_decorator("test_final_static_classification_fields")


@_parametrize
def test_output_field(
    coverage_entry: OutputFieldCoverageEntry,
    scenario_evidence_cache: dict,
) -> None:
    """Verify one canonical output field through EvaluateTradeService evidence."""
    run_field_assertion(coverage_entry, scenario_evidence_cache)
