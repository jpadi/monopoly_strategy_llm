"""Canonical Judge evaluation input (module-owned, JSON field names preserved)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class JudgeInput:
    """Full canonical evaluation input as snake_case JSON sections."""

    metadata: dict[str, Any]
    gameConfiguration: dict[str, Any]
    boardStateBefore: dict[str, Any]
    trade: dict[str, Any]
    boardStateAfter: dict[str, Any]
    staticAnalysisControl: dict[str, Any] | None = None
    staticAlgorithmEvidence: tuple[dict[str, Any], ...] = ()
    playerProfiles: tuple[dict[str, Any], ...] = ()
    decisionPatternProfiles: tuple[dict[str, Any], ...] = ()

    def toCanonicalDict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "metadata": self.metadata,
            "game_configuration": self.gameConfiguration,
            "board_state_before": self.boardStateBefore,
            "trade": self.trade,
            "board_state_after": self.boardStateAfter,
        }
        if self.staticAnalysisControl is not None:
            result["static_analysis_control"] = self.staticAnalysisControl
        if self.staticAlgorithmEvidence:
            result["static_algorithm_evidence"] = list(self.staticAlgorithmEvidence)
        if self.playerProfiles:
            result["player_profiles"] = list(self.playerProfiles)
        if self.decisionPatternProfiles:
            result["decision_pattern_profiles"] = list(self.decisionPatternProfiles)
        return result

    def resolvedControlMode(self) -> str:
        if self.staticAnalysisControl is None:
            return "auto"
        return str(self.staticAnalysisControl.get("mode", "auto"))

    def resolvedFallbackAllowed(self) -> bool:
        if self.staticAnalysisControl is None:
            return False
        mode = self.resolvedControlMode()
        if mode == "allow_llm_fallback":
            return True
        return bool(self.staticAnalysisControl.get("fallback_allowed", False))

    def requiredAlgorithm(self) -> tuple[str, str]:
        control = self.staticAnalysisControl or {}
        required = control.get("required_algorithm") or {}
        algoId = str(required.get("id", "monopoly_static_algorithm"))
        algoVersion = str(required.get("version", "1.0"))
        return algoId, algoVersion

    def requiredDependencies(self) -> tuple[tuple[str, str], ...]:
        control = self.staticAnalysisControl or {}
        deps = control.get("required_dependencies")
        if deps is None:
            return (("monopoly_risk_reference", "1.0"),)
        return tuple((str(d["id"]), str(d["version"])) for d in deps)

    def collectReferencedPlayerIds(self) -> set[str]:
        ids: set[str] = set()
        for board in (self.boardStateBefore, self.boardStateAfter):
            for player in board.get("players", []):
                if player.get("id"):
                    ids.add(str(player["id"]))
        for participant in self.trade.get("participants", []):
            ids.add(str(participant))
        initiating = self.trade.get("initiating_player_id")
        if initiating:
            ids.add(str(initiating))
        for transfer in self.trade.get("transfers", []):
            if transfer.get("from_player_id"):
                ids.add(str(transfer["from_player_id"]))
            if transfer.get("to_player_id"):
                ids.add(str(transfer["to_player_id"]))
        return ids
