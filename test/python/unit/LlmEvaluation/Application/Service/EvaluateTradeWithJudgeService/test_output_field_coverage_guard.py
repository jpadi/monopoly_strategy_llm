"""Output field coverage guard for LLM Judge output schema."""

from __future__ import annotations

from judge_output_field_inventory import (
    CANONICAL_OUTPUT_FIELDS,
    REQUIRED_OUTPUT_SECTIONS,
)


def test_output_field_inventory():
    assert len(REQUIRED_OUTPUT_SECTIONS) == 7
    assert len(CANONICAL_OUTPUT_FIELDS) == 40


def test_output_sections_and_fields_present(execute_judge_scenario):
    result = execute_judge_scenario("competitive_only.json", "competitive_only")
    output = result["output"]
    for section in REQUIRED_OUTPUT_SECTIONS:
        assert section in output
    for fieldPath in CANONICAL_OUTPUT_FIELDS:
        section, _, key = fieldPath.partition(".")
        assert key in output[section]
