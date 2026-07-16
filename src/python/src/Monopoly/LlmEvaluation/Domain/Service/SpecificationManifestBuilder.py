"""Build the delivered-file manifest for a Judge LLM request."""

from __future__ import annotations

from Monopoly.LlmEvaluation.Domain.Model.Specification.SpecificationBundle import SpecificationStructureManifest


class SpecificationManifestBuilder:
    @staticmethod
    def build(
        *,
        instructionFilePaths: tuple[str, ...],
        attachmentFilePaths: tuple[str, ...],
        specificationReadOrder: tuple[str, ...],
    ) -> SpecificationStructureManifest:
        deliveredFilePaths = instructionFilePaths + attachmentFilePaths
        treeText = SpecificationManifestBuilder._buildTreeText(deliveredFilePaths)
        linkNotes = (
            "This manifest lists every file delivered for this request.",
            "Instruction files appear in the instructions message before the task prompt.",
            "Attachment files appear after the task prompt using the platform attachment standard.",
            "All docs/llm_evaluator/ files are always delivered.",
            "docs/static_evaluator/ files are delivered only when execution_mode resolves to LLM_STATIC_FALLBACK.",
        )
        return SpecificationStructureManifest(
            rootLabel="delivered_files",
            treeText=treeText,
            readOrder=specificationReadOrder,
            linkNotes=linkNotes,
            instructionFilePaths=instructionFilePaths,
            attachmentFilePaths=attachmentFilePaths,
            deliveredFilePaths=deliveredFilePaths,
        )

    @staticmethod
    def specificationReadOrder(bundleFilePaths: tuple[str, ...]) -> tuple[str, ...]:
        """Reading order for specification bodies (excludes platform instruction-only files)."""
        llmEvaluator = tuple(path for path in bundleFilePaths if path.startswith("docs/llm_evaluator/"))
        staticEvaluator = tuple(path for path in bundleFilePaths if path.startswith("docs/static_evaluator/"))
        return llmEvaluator + staticEvaluator

    @staticmethod
    def _buildTreeText(paths: tuple[str, ...]) -> str:
        tree: dict[str, dict] = {}
        for path in paths:
            parts = path.split("/")
            node = tree
            for part in parts[:-1]:
                node = node.setdefault(part + "/", {})
            node[parts[-1]] = {}
        lines = ["delivered/"]
        SpecificationManifestBuilder._renderTree(tree, lines, prefix="")
        return "\n".join(lines)

    @staticmethod
    def _renderTree(node: dict, lines: list[str], prefix: str) -> None:
        items = sorted(node.items(), key=lambda kv: kv[0])
        for index, (name, child) in enumerate(items):
            connector = "└── " if index == len(items) - 1 else "├── "
            lines.append(f"{prefix}{connector}{name}")
            extension = "    " if index == len(items) - 1 else "│   "
            if child:
                SpecificationManifestBuilder._renderTree(child, lines, prefix + extension)
