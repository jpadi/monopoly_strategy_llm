"""Shared scenario expectation assertions for unit and functional tests."""

from __future__ import annotations

from typing import Any

from .scenario_registry import ScenarioEntry


def _get_flags(evidence: dict[str, Any]) -> list[str]:
    flags_data = evidence.get("final_conclusions", {}).get("flags", {})
    if isinstance(flags_data, dict):
        return flags_data.get("values", [])
    if isinstance(flags_data, list):
        return flags_data
    return []


def _get_classification(evidence: dict[str, Any]) -> str | None:
    return evidence.get("final_conclusions", {}).get("classification")


def _get_risk_labels(evidence: dict[str, Any], player_id: str) -> dict[str, str | None]:
    labels = evidence.get("final_conclusions", {}).get("risk_labels", {})
    player_labels = labels.get(player_id, {}) if isinstance(labels, dict) else {}
    if not isinstance(player_labels, dict):
        return {"before": None, "after": None}
    before = player_labels.get("before")
    after = player_labels.get("after")
    if isinstance(before, dict):
        before = before.get("label")
    if isinstance(after, dict):
        after = after.get("label")
    return {"before": before, "after": after}


def _get_warnings(evidence: dict[str, Any]) -> list[str]:
    warnings_data = evidence.get("final_conclusions", {}).get("risk_warnings", {})
    if isinstance(warnings_data, dict):
        return list(warnings_data.get("values", []))
    if isinstance(warnings_data, list):
        return warnings_data
    return []


def assert_scenario_expectations(
    evidence: dict[str, Any],
    scenario: ScenarioEntry,
) -> None:
    """Assert all declared expectations for a scenario."""
    expected = scenario.expected
    actual_classification = _get_classification(evidence)
    actual_flags = set(_get_flags(evidence))
    errors: list[str] = []

    if expected.classification is not None:
        if actual_classification != expected.classification:
            errors.append(f"Classification mismatch: expected {expected.classification}, got {actual_classification}")

    for flag in expected.flags:
        if flag not in actual_flags:
            errors.append(f"Expected flag {flag} not found. Actual flags: {actual_flags}")

    for flag in expected.flags_absent:
        if flag in actual_flags:
            errors.append(f"Unexpected flag {flag} found. Should be absent.")

    if expected.no_classification and actual_classification is not None:
        errors.append(f"Expected no classification for degraded result, but got {actual_classification}")

    if expected.risk_label_a is not None:
        labels = _get_risk_labels(evidence, "player_a")
        if labels.get("after") != expected.risk_label_a:
            errors.append(f"Expected player_a after risk label {expected.risk_label_a}, got {labels.get('after')}")

    if expected.risk_label_a_before is not None:
        labels = _get_risk_labels(evidence, "player_a")
        if labels.get("before") != expected.risk_label_a_before:
            errors.append(
                f"Expected player_a before risk label {expected.risk_label_a_before}, got {labels.get('before')}"
            )

    if expected.risk_label_a_after is not None:
        labels = _get_risk_labels(evidence, "player_a")
        if labels.get("after") != expected.risk_label_a_after:
            errors.append(
                f"Expected player_a after risk label {expected.risk_label_a_after}, got {labels.get('after')}"
            )

    if expected.risk_label_b is not None:
        labels = _get_risk_labels(evidence, "player_b")
        if labels.get("after") != expected.risk_label_b and labels.get("before") != expected.risk_label_b:
            errors.append(
                f"Expected player_b risk label {expected.risk_label_b}, "
                f"got before={labels.get('before')} after={labels.get('after')}"
            )

    for warning in expected.warnings_a:
        if warning not in _get_warnings(evidence):
            errors.append(f"Expected warning {warning} for player_a context not found")

    if expected.calculation_status is not None:
        found = False
        for calc in evidence.get("intermediate_calculations", []):
            if calc.get("calculation_type") != expected.calculation_status_type:
                continue
            if expected.calculation_status_side and calc.get("side") != expected.calculation_status_side:
                continue
            if calc.get("status") == expected.calculation_status:
                found = True
                break
        if not found:
            errors.append(
                f"Expected calculation {expected.calculation_status_type}"
                f" side={expected.calculation_status_side}"
                f" status={expected.calculation_status}"
            )

    if errors:
        raise AssertionError(
            f"\nScenario: {scenario.name}\n"
            f"Description: {scenario.description}\n" + "\n".join(f"  - {e}" for e in errors)
        )
