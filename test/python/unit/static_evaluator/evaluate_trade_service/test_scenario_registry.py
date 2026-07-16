"""Scenario registry integrity tests.

These tests verify the registry itself is complete and correct:
- Every scenario input function is registered
- No orphan JSON fixtures
- Every valid scenario has at least one behavioral assertion
- No duplicate paths
"""

from __future__ import annotations

import inspect
from pathlib import Path

from fixtures import scenarioInputs

from .assertions.scenario_registry import (
    SCENARIO_REGISTRY,
    getScenariosWithoutExpectations,
)


class TestRegistryCompleteness:
    """Tests that the registry covers all scenarios."""

    def test_every_scenario_function_is_registered(self) -> None:
        """Every public scenario input function has a registry entry."""
        public_functions = [
            name
            for name, obj in inspect.getmembers(scenarioInputs)
            if inspect.isfunction(obj)
            and not name.startswith("_")
            and name.endswith("Input")
            and not name.startswith("load")
        ]

        registry_names = set(SCENARIO_REGISTRY.keys())
        function_names = set(public_functions)

        missing_from_registry = function_names - registry_names
        assert not missing_from_registry, f"Functions not in registry: {missing_from_registry}"

        extra_in_registry = registry_names - function_names
        assert not extra_in_registry, f"Registry entries without functions: {extra_in_registry}"

    def test_no_orphan_json_fixtures(self) -> None:
        """Every JSON fixture has a registry entry."""
        fixtures_dir = Path(__file__).parents[3] / "fixtures" / "inputs"

        if not fixtures_dir.exists():
            return  # No fixtures to check

        json_files = set()
        for json_file in fixtures_dir.rglob("*.json"):
            relative_path = json_file.relative_to(fixtures_dir)
            json_files.add(str(relative_path))

        registered_paths = {entry.json_path for entry in SCENARIO_REGISTRY.values()}

        orphan_fixtures = json_files - registered_paths
        if orphan_fixtures:
            # Only fail if there are actual orphans (not index files, etc.)
            real_orphans = {f for f in orphan_fixtures if not f.startswith("_")}
            assert not real_orphans, f"Orphan JSON fixtures without registry entries: {real_orphans}"

    def test_no_duplicate_json_paths(self) -> None:
        """Every JSON path appears in exactly one registry entry."""
        paths = [entry.json_path for entry in SCENARIO_REGISTRY.values()]
        duplicates = [p for p in paths if paths.count(p) > 1]
        assert not duplicates, f"Duplicate JSON paths in registry: {set(duplicates)}"


class TestRegistryExpectations:
    """Tests that every scenario has proper expectations."""

    def test_every_valid_scenario_has_behavioral_assertion(self) -> None:
        """Every valid business scenario has at least one expected assertion.

        This is the critical test - no valid scenario may have empty ExpectedOutput.
        """
        missing = getScenariosWithoutExpectations()
        if missing:
            names = [s.name for s in missing]
            raise AssertionError(
                f"Valid scenarios without behavioral assertions: {names}\n"
                "Every valid scenario MUST have at least one expected value "
                "(classification, flags, risk_label, etc.)"
            )

    def test_valid_scenarios_are_marked_valid(self) -> None:
        """Valid scenarios have is_valid=True."""
        for entry in SCENARIO_REGISTRY.values():
            if entry.is_valid:
                assert not entry.expected.validation_error, (
                    f"Scenario {entry.name} is marked valid but expects validation error"
                )

    def test_invalid_scenarios_have_expected_failure(self) -> None:
        """Invalid scenarios have expected failure mode documented."""
        for entry in SCENARIO_REGISTRY.values():
            if not entry.is_valid:
                has_failure_expectation = (
                    entry.expected.validation_error
                    or entry.expected.no_classification
                    or entry.expected.error_expected
                    or entry.expected.has_behavioral_assertion()
                )
                assert has_failure_expectation, f"Invalid scenario {entry.name} has no expected failure mode"
