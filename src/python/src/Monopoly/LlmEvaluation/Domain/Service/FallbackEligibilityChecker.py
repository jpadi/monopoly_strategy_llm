"""Verify fallback specification dependencies."""

from __future__ import annotations

from Monopoly.LlmEvaluation.Domain.Exception.LlmEvaluationErrors import FallbackEligibilityError
from Monopoly.LlmEvaluation.Domain.Port.SpecificationRepository import SpecificationRepository


class FallbackEligibilityChecker:
    def __init__(self, *, specificationRepository: SpecificationRepository) -> None:
        self._repository = specificationRepository

    def verify(
        self,
        algorithmId: str,
        algorithmVersion: str,
        dependencies: tuple[tuple[str, str], ...],
    ) -> None:
        if not self._repository.verifySpecificationIdentity(algorithmId, algorithmVersion):
            raise FallbackEligibilityError(
                f"Static algorithm specification not verified: {algorithmId} v{algorithmVersion}"
            )
        for depId, depVersion in dependencies:
            if not self._repository.verifySpecificationIdentity(depId, depVersion):
                raise FallbackEligibilityError(f"Dependency specification not verified: {depId} v{depVersion}")

    def canVerify(
        self,
        algorithmId: str,
        algorithmVersion: str,
        dependencies: tuple[tuple[str, str], ...],
    ) -> bool:
        try:
            self.verify(algorithmId, algorithmVersion, dependencies)
            return True
        except FallbackEligibilityError:
            return False
