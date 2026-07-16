"""Build specification file bundles with structure manifest."""

from __future__ import annotations

from Monopoly.LlmEvaluation.Domain.Model.Runtime.ResolvedRuntimePlan import ResolvedRuntimePlan
from Monopoly.LlmEvaluation.Domain.Model.Specification.SpecificationBundle import (
    BundleFile,
    SpecificationBundle,
    SpecificationStructureManifest,
)
from Monopoly.LlmEvaluation.Domain.Port.SpecificationRepository import SpecificationRepository
from Monopoly.LlmEvaluation.Domain.Service.SpecificationManifestBuilder import SpecificationManifestBuilder


class SpecificationBundleBuilder:
    def __init__(self, *, specificationRepository: SpecificationRepository) -> None:
        self._repository = specificationRepository

    def build(self, runtimePlan: ResolvedRuntimePlan) -> SpecificationBundle | None:
        if runtimePlan.bundleRequired:
            paths = self._repository.fallbackBundlePaths()
        else:
            paths = self._repository.minimalBundlePaths()
        if not paths:
            return None
        files = tuple(BundleFile(relativePath=path, content=self._repository.readFile(path)) for path in paths)
        placeholderManifest = SpecificationStructureManifest(
            rootLabel="specifications",
            treeText="",
            readOrder=SpecificationManifestBuilder.specificationReadOrder(paths),
            linkNotes=(),
        )
        return SpecificationBundle(files=files, structureManifest=placeholderManifest)
