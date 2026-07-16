"""Unit tests for SuppliedEvidenceValidator."""

from __future__ import annotations

import copy
import json
from dataclasses import replace

import pytest
from test_utilities.repo_paths import FIXTURE_ROOT

from Monopoly.LlmEvaluation.Domain.Model.JudgeEnums import EvidenceUsability
from Monopoly.LlmEvaluation.Domain.Service.SuppliedEvidenceValidator import (
    SuppliedEvidenceValidator,
)
from Monopoly.LlmEvaluation.Infrastructure.Json.JudgeInputMapper import JudgeInputMapper


def _load_judge_input(fixture_name: str):
    payload = json.loads((FIXTURE_ROOT / "inputs" / fixture_name).read_text(encoding="utf-8"))
    return JudgeInputMapper.fromDict(payload["evaluation_input"])


@pytest.fixture
def validator() -> SuppliedEvidenceValidator:
    return SuppliedEvidenceValidator()


def test_balanced_supplied_evidence_is_usable(validator: SuppliedEvidenceValidator):
    judge_input = _load_judge_input("supplied_evidence_usable.json")
    results = validator.classifyAll(
        judge_input,
        "monopoly_static_algorithm",
        "1.0",
    )
    assert len(results) == 1
    assert results[0].usability == EvidenceUsability.USABLE


def test_partial_supplied_evidence_is_partially_usable(
    validator: SuppliedEvidenceValidator,
):
    judge_input = _load_judge_input("supplied_evidence_partial.json")
    results = validator.classifyAll(
        judge_input,
        "monopoly_static_algorithm",
        "1.0",
    )
    assert results[0].usability == EvidenceUsability.PARTIALLY_USABLE


def test_wrong_version_is_unusable(validator: SuppliedEvidenceValidator):
    judge_input = _load_judge_input("supplied_evidence_unusable.json")
    results = validator.classifyAll(
        judge_input,
        "monopoly_static_algorithm",
        "1.0",
    )
    assert results[0].usability == EvidenceUsability.UNUSABLE


def test_missing_envelope_field_is_unusable(validator: SuppliedEvidenceValidator):
    judge_input = _load_judge_input("supplied_evidence_usable.json")
    evidence = copy.deepcopy(judge_input.staticAlgorithmEvidence[0])
    evidence.pop("metadata")
    judge_input = replace(judge_input, staticAlgorithmEvidence=(evidence,))
    results = validator.classifyAll(
        judge_input,
        "monopoly_static_algorithm",
        "1.0",
    )
    assert results[0].usability == EvidenceUsability.UNUSABLE
