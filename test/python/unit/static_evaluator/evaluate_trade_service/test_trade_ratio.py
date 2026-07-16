"""Trade ratio boundary tests through the application service."""

from __future__ import annotations

from fixtures import scenarioInputs

from .assertions.evidence_assertions import (
    assertCalculationExists,
    assertFlagAbsent,
    assertTradeRatio,
    assertValidEvidenceEnvelope,
)


class TestTradeRatioBelowThresholds:
    """Tests for ratios below flag thresholds."""

    def test_perfectly_balanced_trade_produces_low_ratio(self, execute_scenario) -> None:
        input_data = scenarioInputs.perfectlyBalancedPrintedValueSwapInput()
        evidence = execute_scenario(input_data)
        assertValidEvidenceEnvelope(evidence)
        assertTradeRatio(evidence, max_published=2.0)
        assertFlagAbsent(evidence, "SUSPICIOUS_IMBALANCE")

    def test_ratio_just_below_two_has_no_suspicious_flag(self, execute_scenario) -> None:
        input_data = scenarioInputs.ratioJustBelowTwoInput()
        evidence = execute_scenario(input_data)
        assertTradeRatio(evidence, max_published=2.0)
        assertFlagAbsent(evidence, "SUSPICIOUS_IMBALANCE")


class TestTradeRatioAtThresholds:
    """Tests for ratios at flag thresholds."""

    def test_ratio_exactly_three_at_suspicious_threshold(self, execute_scenario) -> None:
        input_data = scenarioInputs.ratioExactlyThreeInput()
        evidence = execute_scenario(input_data)
        assertTradeRatio(evidence, min_published=3.0)

    def test_ratio_exactly_five_is_capped(self, execute_scenario) -> None:
        input_data = scenarioInputs.ratioExactlyFiveInput()
        evidence = execute_scenario(input_data)
        assertTradeRatio(evidence, expected_published=5.0)


class TestTradeRatioEdgeCases:
    """Tests for edge cases in trade ratio calculation."""

    def test_both_strategic_values_zero_produces_finite_ratio(self, execute_scenario) -> None:
        input_data = scenarioInputs.bothStrategicValuesZeroInput()
        evidence = execute_scenario(input_data)
        assertValidEvidenceEnvelope(evidence)

    def test_ratio_greater_than_five_is_capped(self, execute_scenario) -> None:
        input_data = scenarioInputs.ratioGreaterThanFiveInput()
        evidence = execute_scenario(input_data)
        assertTradeRatio(evidence, expected_published=5.0)
        calc = assertCalculationExists(evidence, "trade_ratio", side="trade")
        intermediate = calc.get("intermediate_values", {})
        raw_ratio = intermediate.get("raw_ratio")
        if raw_ratio is not None:
            assert raw_ratio > 5.0
