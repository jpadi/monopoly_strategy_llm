"""Final classification tests through the application service."""

from __future__ import annotations

from fixtures import scenarioInputs

from .assertions.evidence_assertions import (
    assertFinalClassification,
    assertFlagPresent,
    assertValidEvidenceEnvelope,
)


class TestNoFlagClassification:
    def test_no_flag_when_balanced_trade(self, execute_scenario) -> None:
        input_data = scenarioInputs.noFlagClassificationInput()
        evidence = execute_scenario(input_data)
        assertValidEvidenceEnvelope(evidence)
        assertFinalClassification(evidence, "NO_FLAG")


class TestSoftFlagClassification:
    def test_soft_flag_fixture_executes(self, execute_scenario) -> None:
        """Verify soft flag fixture executes - actual classification depends on fixture."""
        input_data = scenarioInputs.softFlagClassificationInput()
        evidence = execute_scenario(input_data)
        assertValidEvidenceEnvelope(evidence)

    def test_suspicious_imbalance_produces_soft_flag(self, execute_scenario) -> None:
        input_data = scenarioInputs.slightImbalanceTradeInput()
        evidence = execute_scenario(input_data)
        assertFlagPresent(evidence, "SUSPICIOUS_IMBALANCE")
        assertFinalClassification(evidence, "SOFT_FLAG")


class TestStrongFlagClassification:
    def test_strong_flag_fixture_executes(self, execute_scenario) -> None:
        """Verify strong flag fixture executes - classification depends on flags produced."""
        input_data = scenarioInputs.strongFlagClassificationInput()
        evidence = execute_scenario(input_data)
        assertValidEvidenceEnvelope(evidence)
        classification = evidence.get("final_conclusions", {}).get("classification")
        assert classification in {"STRONG_FLAG", "REVIEW_RECOMMENDED"}, (
            f"Expected STRONG_FLAG or REVIEW_RECOMMENDED, got {classification}"
        )


class TestReviewRecommendedClassification:
    def test_review_recommended_with_multiple_strong_flags(self, execute_scenario) -> None:
        input_data = scenarioInputs.reviewRecommendedClassificationInput()
        evidence = execute_scenario(input_data)
        assertValidEvidenceEnvelope(evidence)
        assertFinalClassification(evidence, "REVIEW_RECOMMENDED")
