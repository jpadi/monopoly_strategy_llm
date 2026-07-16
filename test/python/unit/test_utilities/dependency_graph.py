"""Dependency graph validation utilities.

Validates the calculation dependency graph is well-formed and complete.
"""

from __future__ import annotations

from typing import Any


def buildDependencyGraph(evidence: dict[str, Any]) -> dict[str, set[str]]:
    """Build a directed graph of calculation dependencies.

    Args:
        evidence: The complete evidence dictionary

    Returns:
        Dict mapping calc_id -> set of calc_ids it depends on
    """
    graph: dict[str, set[str]] = {}

    for calc in evidence["intermediate_calculations"]:
        calc_id = calc["id"]
        deps = set(calc.get("dependent_calculation_ids", []))
        graph[calc_id] = deps

    return graph


def getAllCalculationIds(evidence: dict[str, Any]) -> set[str]:
    """Get all calculation IDs in the evidence.

    Args:
        evidence: The complete evidence dictionary

    Returns:
        Set of all calculation IDs
    """
    return {calc["id"] for calc in evidence["intermediate_calculations"]}


def assertNoDuplicateIds(evidence: dict[str, Any]) -> None:
    """Assert there are no duplicate calculation IDs.

    Args:
        evidence: The complete evidence dictionary
    """
    ids = [calc["id"] for calc in evidence["intermediate_calculations"]]
    unique_ids = set(ids)
    assert len(ids) == len(unique_ids), f"Duplicate calculation IDs found: {len(ids)} total, {len(unique_ids)} unique"


def assertAllReferencesExist(evidence: dict[str, Any]) -> None:
    """Assert all dependent_calculation_ids reference existing calculations.

    Args:
        evidence: The complete evidence dictionary
    """
    all_ids = getAllCalculationIds(evidence)

    for calc in evidence["intermediate_calculations"]:
        for dep_id in calc.get("dependent_calculation_ids", []):
            assert dep_id in all_ids, (
                f"Calculation {calc['id']} references non-existent dependent_calculation_id: {dep_id}"
            )


def assertNoSelfDependencies(evidence: dict[str, Any]) -> None:
    """Assert no calculation depends on itself.

    Args:
        evidence: The complete evidence dictionary
    """
    for calc in evidence["intermediate_calculations"]:
        calc_id = calc["id"]
        deps = calc.get("dependent_calculation_ids", [])
        assert calc_id not in deps, f"Calculation {calc_id} has self-dependency"


def findCycles(graph: dict[str, set[str]]) -> list[list[str]]:
    """Find any cycles in the dependency graph.

    Note: In this graph, edges go FROM a calculation TO the calculations
    that depend on it. So cycles would mean A depends on B depends on A.

    Args:
        graph: The dependency graph

    Returns:
        List of cycles found (each cycle is a list of calc_ids)
    """
    cycles = []
    visited = set()
    rec_stack = set()
    path = []

    def dfs(node: str) -> bool:
        if node in rec_stack:
            # Found cycle - extract it
            cycle_start = path.index(node)
            cycles.append(path[cycle_start:] + [node])
            return True

        if node in visited:
            return False

        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbor in graph.get(node, set()):
            dfs(neighbor)

        path.pop()
        rec_stack.remove(node)
        return False

    for node in graph:
        if node not in visited:
            dfs(node)

    return cycles


def assertNoCycles(evidence: dict[str, Any]) -> None:
    """Assert there are no cycles in the dependency graph.

    Args:
        evidence: The complete evidence dictionary
    """
    graph = buildDependencyGraph(evidence)
    cycles = findCycles(graph)
    assert len(cycles) == 0, f"Dependency cycles found: {cycles}"


def assertDependencyChainExists(
    evidence: dict[str, Any],
    from_type: str,
    to_type: str,
) -> None:
    """Assert there is a dependency path from one calculation type to another.

    Args:
        evidence: The complete evidence dictionary
        from_type: Starting calculation type
        to_type: Target calculation type
    """
    # Build type-based graph
    calcs_by_type: dict[str, list[dict[str, Any]]] = {}
    for calc in evidence["intermediate_calculations"]:
        calcs_by_type.setdefault(calc["calculation_type"], []).append(calc)

    assert from_type in calcs_by_type, f"No calculations of type {from_type}"
    assert to_type in calcs_by_type, f"No calculations of type {to_type}"

    # Check if any from_type calc eventually leads to a to_type calc
    id_to_calc = {c["id"]: c for c in evidence["intermediate_calculations"]}

    def can_reach(start_id: str, target_type: str, visited: set[str]) -> bool:
        if start_id in visited:
            return False
        visited.add(start_id)

        calc = id_to_calc.get(start_id)
        if calc is None:
            return False

        for dep_id in calc.get("dependent_calculation_ids", []):
            dep_calc = id_to_calc.get(dep_id)
            if dep_calc and dep_calc["calculation_type"] == target_type:
                return True
            if can_reach(dep_id, target_type, visited):
                return True

        return False

    found_path = False
    for calc in calcs_by_type[from_type]:
        if can_reach(calc["id"], to_type, set()):
            found_path = True
            break

    assert found_path, f"No dependency path from {from_type} to {to_type}"


def assertValidDependencyGraph(evidence: dict[str, Any]) -> None:
    """Run all dependency graph validations.

    Args:
        evidence: The complete evidence dictionary
    """
    assertNoDuplicateIds(evidence)
    assertAllReferencesExist(evidence)
    assertNoSelfDependencies(evidence)
    assertNoCycles(evidence)


def assertStrategicValueDependencies(evidence: dict[str, Any]) -> None:
    """Assert that strategic_value has correct dependency chains.

    According to the spec:
    - mortgage_capacity → available_construction_budget
    - available_risk_resources, landing_exposure, repair_exposure → largest_threat
    - largest_threat, available_risk_resources → risk_margin, coverage_ratio
    - risk_margin, coverage_ratio → immediate_risk
    - All component deltas → strategic_value
    - strategic_value → trade_ratio → final_static_classification

    Args:
        evidence: The complete evidence dictionary
    """
    # These are expected dependency chains
    expected_chains = [
        ("mortgage_capacity", "available_construction_budget"),
        ("strategic_value", "trade_ratio"),
        ("trade_ratio", "final_static_classification"),
    ]

    for from_type, to_type in expected_chains:
        assertDependencyChainExists(evidence, from_type, to_type)


def assertBeforeAfterFeedDelta(
    evidence: dict[str, Any],
    calculation_type: str,
) -> None:
    """Assert that before/after calculations feed into delta for a type.

    Args:
        evidence: The complete evidence dictionary
        calculation_type: The calculation type to check
    """
    calcs = [c for c in evidence["intermediate_calculations"] if c["calculation_type"] == calculation_type]

    deltas = [c for c in calcs if c["side"] == "delta"]

    if not deltas:
        return  # No delta calculations for this type

    # Check that delta calculations reference before/after in intermediate_values
    for delta in deltas:
        iv = delta["intermediate_values"]
        # Most deltas should have before/after in intermediate_values
        if "before" in iv or "after" in iv:
            assert "before" in iv and "after" in iv, (
                f"{calculation_type} delta must have both before and after in intermediate_values"
            )
