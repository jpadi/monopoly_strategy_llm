"""Legacy experimental compatibility for unstructured Cursor prose responses."""

from __future__ import annotations

import json
import re
from pathlib import Path

from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorFileRetriever import CursorArtifactAgent, CursorFileRetriever
from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorTransportEnvelopeParser import CursorTransportEnvelopeParser
from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorWorkspacePathResolver import CursorWorkspacePathResolver

_LEGACY_FILENAME_PATTERN = re.compile(
    r"([A-Za-z0-9_./-]+\.json)",
    re.IGNORECASE,
)
_LEGACY_KNOWN_RELATIVE_PATHS = (
    "output/judge_output.json",
    "judge_output.json",
    ".judge_output_response.json",
    "judge_final.json",
)


class CursorLegacyProseRecovery:
    @staticmethod
    def recover(
        *,
        rawText: str,
        workspaceRoot: Path,
        agent: CursorArtifactAgent | None,
    ) -> tuple[str, str] | None:
        text = rawText.strip()
        if not text or text.startswith("{"):
            return None

        listedPaths = CursorFileRetriever._listArtifactPaths(agent)
        candidatePaths = CursorLegacyProseRecovery._candidatePaths(text, listedPaths)

        for relativePath in candidatePaths:
            try:
                CursorWorkspacePathResolver.resolve(workspaceRoot=workspaceRoot, relativePath=relativePath)
                recoveredText, retrievalMethod, _, _ = CursorFileRetriever.retrieveJsonText(
                    workspaceRoot=workspaceRoot,
                    relativePath=relativePath,
                    agent=agent,
                )
                normalized = CursorLegacyProseRecovery._validateSingleJsonObject(recoveredText)
                return normalized, f"legacy_prose_{retrievalMethod}:{relativePath}"
            except Exception:
                continue

        for relativePath in _LEGACY_KNOWN_RELATIVE_PATHS:
            resolved = workspaceRoot / relativePath
            if not resolved.is_file():
                continue
            try:
                CursorWorkspacePathResolver.resolve(workspaceRoot=workspaceRoot, relativePath=relativePath)
                normalized = CursorLegacyProseRecovery._validateSingleJsonObject(resolved.read_text(encoding="utf-8"))
                return normalized, f"legacy_known_path:{relativePath}"
            except Exception:
                continue

        return None

    @staticmethod
    def _candidatePaths(rawText: str, listedPaths: tuple[str, ...]) -> tuple[str, ...]:
        ordered: list[str] = []
        seen: set[str] = set()

        def add(path: str) -> None:
            normalized = path.strip().lstrip("./")
            if not normalized or normalized in seen:
                return
            if "\x00" in normalized:
                return
            if CursorWorkspacePathResolver._isForeignAbsolutePath(normalized.replace("\\", "/")):
                return
            if ".." in Path(normalized).parts:
                return
            seen.add(normalized)
            ordered.append(normalized)

        for path in listedPaths:
            add(path)
        for match in _LEGACY_FILENAME_PATTERN.finditer(rawText):
            add(match.group(1))
        for path in _LEGACY_KNOWN_RELATIVE_PATHS:
            add(path)
        return tuple(ordered)

    @staticmethod
    def _validateSingleJsonObject(text: str) -> str:
        payload = json.loads(text.strip())
        if not isinstance(payload, dict):
            raise ValueError("Recovered JSON must be an object")
        if CursorTransportEnvelopeParser.looksLikeTransportEnvelope(payload):
            raise ValueError("Legacy recovery must not return a transport envelope")
        return json.dumps(payload)
