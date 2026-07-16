"""Validate canonical Judge input sections."""

from __future__ import annotations

from typing import Any

from Monopoly.LlmEvaluation.Domain.Exception.LlmEvaluationErrors import JudgeInputValidationError
from Monopoly.LlmEvaluation.Domain.Model.Input.JudgeInput import JudgeInput
from Monopoly.LlmEvaluation.Domain.Model.JudgeEnums import REQUIRED_INPUT_SECTIONS, StaticAnalysisControlMode

VALID_CONTROL_MODES = {m.value for m in StaticAnalysisControlMode}


def validateJudgeInput(judgeInput: JudgeInput) -> None:
    canonical = judgeInput.toCanonicalDict()
    missing = [section for section in REQUIRED_INPUT_SECTIONS if section not in canonical]
    if missing:
        raise JudgeInputValidationError(f"Missing required input sections: {', '.join(missing)}")

    mode = judgeInput.resolvedControlMode()
    if mode not in VALID_CONTROL_MODES:
        raise JudgeInputValidationError(f"Invalid static_analysis_control.mode: {mode}")

    if not judgeInput.trade.get("id"):
        raise JudgeInputValidationError("trade.id is required")

    _validateTransferMatrix(judgeInput.trade.get("transfers", []))


def _validateTransferMatrix(transfers: list[Any]) -> None:
    for transfer in transfers:
        assetType = transfer.get("asset_type")
        assetId = transfer.get("asset_id")
        amount = transfer.get("amount", 0)
        if assetType == "cash":
            if assetId is not None:
                raise JudgeInputValidationError("cash transfer asset_id must be null")
            if not isinstance(amount, (int, float)) or amount <= 0:
                raise JudgeInputValidationError("cash transfer amount must be greater than 0")
        elif assetType in ("property", "tradable_asset"):
            if not assetId:
                raise JudgeInputValidationError(f"{assetType} transfer requires asset_id")
        if transfer.get("from_player_id") is None or transfer.get("to_player_id") is None:
            raise JudgeInputValidationError("transfer requires from_player_id and to_player_id")
