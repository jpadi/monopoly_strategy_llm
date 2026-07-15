"""Domain validation for canonical Transfer semantics."""

from __future__ import annotations

from Monopoly.StaticEvaluation.Domain.Model.EvaluationInput import Transfer

QUANTITATIVE_ASSET_TYPES = frozenset({"cash"})
NON_QUANTITATIVE_ASSET_TYPES = frozenset({"property", "tradable_asset"})


class TransferValidationError(ValueError):
    """Raised when a Transfer violates canonical input semantics."""


def validateTransfer(transfer: Transfer) -> None:
    assetType = transfer.assetType
    if assetType == "cash":
        if transfer.assetId is not None:
            raise TransferValidationError(f"Transfer {transfer.id}: cash transfer requires asset_id=null")
        if transfer.amount is None or transfer.amount <= 0:
            raise TransferValidationError(f"Transfer {transfer.id}: cash transfer requires amount > 0")
        return

    if assetType in NON_QUANTITATIVE_ASSET_TYPES:
        if not transfer.assetId:
            raise TransferValidationError(f"Transfer {transfer.id}: {assetType} transfer requires asset_id")
        if transfer.amount != 0:
            raise TransferValidationError(f"Transfer {transfer.id}: {assetType} transfer requires amount=0")
        return

    if transfer.assetId:
        if transfer.amount != 0:
            raise TransferValidationError(f"Transfer {transfer.id}: non-quantitative asset requires amount=0")
    elif transfer.amount is None or transfer.amount <= 0:
        raise TransferValidationError(f"Transfer {transfer.id}: quantitative asset requires amount > 0")
