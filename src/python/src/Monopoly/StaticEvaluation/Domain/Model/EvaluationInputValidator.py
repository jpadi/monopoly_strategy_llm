"""Validate EvaluationInput against canonical boundary rules."""

from __future__ import annotations

from Monopoly.StaticEvaluation.Domain.Model.EvaluationInput import EvaluationInput
from Monopoly.StaticEvaluation.Domain.Model.TransferValidation import validateTransfer


class EvaluationInputValidationError(ValueError):
    """Raised when evaluation input violates canonical boundary rules."""


def validateEvaluationInput(evaluationInput: EvaluationInput) -> None:
    for transfer in evaluationInput.trade.transfers:
        validateTransfer(transfer)
    _validateBoardConsistency(evaluationInput.boardStateBefore, "board_state_before")
    _validateBoardConsistency(evaluationInput.boardStateAfter, "board_state_after")
    _validateBoardPropertySetsMatch(
        evaluationInput.boardStateBefore,
        evaluationInput.boardStateAfter,
    )


def _validateBoardConsistency(board, label: str) -> None:
    propsById = {p.id: p for p in board.properties}
    for player in board.players:
        for pid in player.ownedProperties:
            prop = propsById.get(pid)
            if prop is None:
                raise EvaluationInputValidationError(f"{label}: player {player.id} lists unknown property {pid}")
            if prop.ownerPlayerId != player.id:
                raise EvaluationInputValidationError(
                    f"{label}: player {player.id} lists {pid} but owner is {prop.ownerPlayerId!r}"
                )
    for prop in board.properties:
        if prop.ownerPlayerId is None:
            continue
        owner = next((p for p in board.players if p.id == prop.ownerPlayerId), None)
        if owner is None:
            raise EvaluationInputValidationError(
                f"{label}: property {prop.id} owned by unknown player {prop.ownerPlayerId!r}"
            )
        if prop.id not in owner.ownedProperties:
            raise EvaluationInputValidationError(
                f"{label}: property {prop.id} owned by {prop.ownerPlayerId} but missing from owned_properties"
            )


def _validateBoardPropertySetsMatch(before, after) -> None:
    beforeIds = {p.id for p in before.properties}
    afterIds = {p.id for p in after.properties}
    if beforeIds != afterIds:
        raise EvaluationInputValidationError(
            "board_state_before and board_state_after must contain the same property IDs"
        )
    beforeById = {p.id: p for p in before.properties}
    afterById = {p.id: p for p in after.properties}
    staticFields = (
        "displayName",
        "category",
        "groupId",
        "purchasePrice",
        "mortgageValue",
        "houseCost",
        "hotelCost",
    )
    for pid in beforeIds:
        b = beforeById[pid]
        a = afterById[pid]
        for field in staticFields:
            if getattr(b, field) != getattr(a, field):
                raise EvaluationInputValidationError(
                    f"Property {pid} static field {field} changed between before and after"
                )
