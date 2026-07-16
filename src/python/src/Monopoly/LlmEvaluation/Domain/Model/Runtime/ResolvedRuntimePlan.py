"""Deterministic runtime plan resolved before any LLM call."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EvidenceUsabilityResult:
    evidenceId: str
    usability: str


@dataclass(frozen=True, slots=True)
class ResolvedRuntimePlan:
    requestedMode: str
    executionMode: str
    evidenceSource: str | None
    algorithmId: str | None
    algorithmVersion: str | None
    dependencyVersions: dict[str, str]
    expectedExecutionStatus: str
    fallbackAuthorized: bool
    fallbackRequired: bool
    fallbackAttempted: bool
    evidenceUsability: tuple[EvidenceUsabilityResult, ...]
    limitations: tuple[str, ...]
    bundleRequired: bool
