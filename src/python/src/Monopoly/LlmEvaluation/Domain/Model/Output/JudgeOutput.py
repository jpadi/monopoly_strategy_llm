"""Canonical Judge output wrapper."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class JudgeOutput:
    """Seven-section canonical output as snake_case JSON."""

    sections: dict[str, Any]

    def toDict(self) -> dict[str, Any]:
        return dict(self.sections)

    def staticAnalysisResult(self) -> dict[str, Any]:
        result = self.sections.get("static_analysis_result", {})
        if isinstance(result, dict):
            return result
        return {}
