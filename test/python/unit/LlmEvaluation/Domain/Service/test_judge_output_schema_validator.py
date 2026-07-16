"""Judge output schema structural validation tests."""

from __future__ import annotations

import copy

import pytest
from test_utilities.judge_output_builder import buildCanonicalJudgeOutput

from Monopoly.LlmEvaluation.Domain.Exception.LlmEvaluationErrors import JudgeOutputSchemaViolationError
from Monopoly.LlmEvaluation.Domain.Model.JudgeEnums import REQUIRED_OUTPUT_SECTIONS
from Monopoly.LlmEvaluation.Domain.Model.Runtime.ResolvedRuntimePlan import ResolvedRuntimePlan
from Monopoly.LlmEvaluation.Domain.Service.JudgeOutputSchemaValidator import validateJudgeOutputStructure
from Monopoly.LlmEvaluation.Domain.Service.JudgeOutputValidator import JudgeOutputValidator


def _runtime_plan(**overrides) -> ResolvedRuntimePlan:
    defaults = dict(
        requestedMode="auto",
        executionMode="NO_STATIC_ANALYSIS",
        evidenceSource=None,
        algorithmId=None,
        algorithmVersion=None,
        dependencyVersions={},
        expectedExecutionStatus="UNAVAILABLE",
        fallbackAuthorized=False,
        fallbackRequired=False,
        fallbackAttempted=False,
        evidenceUsability=(),
        limitations=(),
        bundleRequired=False,
    )
    defaults.update(overrides)
    return ResolvedRuntimePlan(**defaults)


def test_valid_output_passes_structural_validation():
    output = buildCanonicalJudgeOutput()
    assert validateJudgeOutputStructure(output) == []


def test_missing_required_section_fails():
    output = buildCanonicalJudgeOutput()
    output.pop("final_summary")
    errors = validateJudgeOutputStructure(output)
    assert any("Missing output section: final_summary" in error for error in errors)


@pytest.mark.parametrize("section", REQUIRED_OUTPUT_SECTIONS)
def test_each_required_section_must_exist(section: str):
    output = buildCanonicalJudgeOutput()
    output.pop(section)
    errors = validateJudgeOutputStructure(output)
    assert any(section in error for error in errors)


def test_invalid_enum_values_fail():
    output = buildCanonicalJudgeOutput()
    output["competitive_classification"]["classification"] = "invalid"
    output["confidence_assessment"]["overall_confidence"] = "invalid"
    errors = validateJudgeOutputStructure(output)
    assert any("competitive_classification.classification" in error for error in errors)
    assert any("confidence_assessment.overall_confidence" in error for error in errors)


def test_extra_top_level_key_rejected():
    output = buildCanonicalJudgeOutput()
    output["unexpected_key"] = "value"
    errors = validateJudgeOutputStructure(output)
    assert any("Unexpected top-level key: unexpected_key" in error for error in errors)


def test_validator_rejects_invalid_structure_with_runtime_plan():
    output = buildCanonicalJudgeOutput()
    output["competitive_evaluation"]["summary"] = 123
    validator = JudgeOutputValidator()
    with pytest.raises(JudgeOutputSchemaViolationError):
        validator.validate(output, _runtime_plan())


def test_validator_rejects_extra_top_level_key_with_runtime_plan():
    output = buildCanonicalJudgeOutput()
    output["unexpected_key"] = "value"
    validator = JudgeOutputValidator()
    with pytest.raises(JudgeOutputSchemaViolationError):
        validator.validate(output, _runtime_plan())


def test_validator_accepts_canonical_output():
    output = buildCanonicalJudgeOutput(
        executionMode="STATIC_EVIDENCE_PROVIDED",
        evidenceSource="SUPPLIED_STATIC_SOFTWARE",
        executionStatus="COMPLETE",
    )
    validator = JudgeOutputValidator()
    result = validator.validate(
        output,
        _runtime_plan(
            executionMode="STATIC_EVIDENCE_PROVIDED",
            evidenceSource="SUPPLIED_STATIC_SOFTWARE",
            expectedExecutionStatus="COMPLETE",
        ),
    )
    assert result.toDict() == output


def test_nested_pattern_items_require_shape():
    output = buildCanonicalJudgeOutput()
    output["decision_pattern_analysis"]["matched_patterns"] = [{"pattern_id": 1, "summary": "x"}]
    errors = validateJudgeOutputStructure(output)
    assert any("pattern_id must be a string" in error for error in errors)


def test_optional_unmatched_patterns_may_be_omitted():
    output = buildCanonicalJudgeOutput()
    output["decision_pattern_analysis"].pop("unmatched_patterns")
    assert validateJudgeOutputStructure(output) == []


def test_deep_copy_valid_output_remains_valid():
    output = copy.deepcopy(buildCanonicalJudgeOutput())
    assert validateJudgeOutputStructure(output) == []
