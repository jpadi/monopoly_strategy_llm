"""Map JSON to JudgeInput domain model."""

from __future__ import annotations

from typing import Any

from Monopoly.LlmEvaluation.Domain.Model.Input.JudgeInput import JudgeInput


class JudgeInputMapper:
    @classmethod
    def fromDict(cls, data: dict[str, Any]) -> JudgeInput:
        staticControl = data.get("static_analysis_control")
        evidence = data.get("static_algorithm_evidence", [])
        profiles = data.get("player_profiles", [])
        patterns = data.get("decision_pattern_profiles", [])
        return JudgeInput(
            metadata=dict(data.get("metadata", {})),
            gameConfiguration=dict(data.get("game_configuration", {})),
            boardStateBefore=dict(data.get("board_state_before", {})),
            trade=dict(data.get("trade", {})),
            boardStateAfter=dict(data.get("board_state_after", {})),
            staticAnalysisControl=dict(staticControl) if staticControl is not None else None,
            staticAlgorithmEvidence=tuple(dict(item) for item in evidence),
            playerProfiles=tuple(dict(item) for item in profiles),
            decisionPatternProfiles=tuple(dict(item) for item in patterns),
        )
