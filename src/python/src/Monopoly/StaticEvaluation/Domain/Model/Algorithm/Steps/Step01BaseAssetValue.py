"""Step 1 — Base Asset Value (trade-scoped)."""

from __future__ import annotations

from typing import Any

from Monopoly.StaticEvaluation.Domain.Model.EvaluationInput import (
    EvaluationInput,
    GameConfiguration,
    PropertyState,
    TradableAssetState,
)
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationSide import CalculationSide
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationStatus import CalculationStatus
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationSubject import CalculationSubject
from Monopoly.StaticEvaluation.Domain.Model.Evidence.EvidenceCollector import EvidenceCollector
from Monopoly.StaticEvaluation.Domain.Model.SpecificationDefaults import SpecificationDefaults
from Monopoly.StaticEvaluation.Domain.Model.ValueSource import ValueSourceLabel


def calculateBaseAssetValue(
    evaluationInput: EvaluationInput,
    playerId: str,
    collector: EvidenceCollector,
    defaults: SpecificationDefaults,
) -> int:
    trade = evaluationInput.trade
    config = evaluationInput.gameConfiguration
    props = {p.id: p for p in evaluationInput.boardStateBefore.properties}
    assets = {a.id: a for a in evaluationInput.boardStateBefore.tradableAssets}

    cashReceived = 0
    propertyValue = 0
    buildingValue = 0
    cardValue = 0
    transferIds: list[str] = []
    propertyIds: list[str] = []
    lineItems: list[dict[str, int | str]] = []

    for transfer in trade.transfers:
        if transfer.toPlayerId != playerId:
            continue
        transferIds.append(transfer.id)
        if transfer.assetType == "cash":
            amount = transfer.amount or 0
            cashReceived += amount
            lineItems.append({"type": "cash", "transfer_id": transfer.id, "value": amount})
        elif transfer.assetType == "property" and transfer.assetId:
            prop = props.get(transfer.assetId)
            if prop:
                propertyIds.append(prop.id)
                val = _propertyReceivedValue(prop, config)
                propertyValue += val
                bld = _buildingReceivedValue(prop, config)
                buildingValue += bld
                lineItems.append(
                    {
                        "type": "property",
                        "transfer_id": transfer.id,
                        "property_id": prop.id,
                        "amount": 0,
                        "printed_value": val - bld,
                        "building_value": bld,
                    }
                )
        elif transfer.assetType == "tradable_asset" and transfer.assetId:
            asset = assets.get(transfer.assetId)
            if asset:
                val = _tradableAssetValue(asset, defaults)
                cardValue += val
                lineItems.append({"type": "tradable_asset", "asset_id": asset.id, "value": val})

    total = cashReceived + propertyValue + buildingValue + cardValue

    refs = [f"trade.transfers[{tid}]" for tid in transferIds]
    for pid in propertyIds:
        refs.append(f"board_state_before.properties[{pid}]")
    ivs: dict[str, Any] = {}
    for item in lineItems:
        if item["type"] == "cash":
            ivs[f"transfer_{item['transfer_id']}_amount"] = item["value"]
        elif item["type"] == "property":
            pid = str(item["property_id"])
            p = props[pid]
            ivs[f"property_{pid}_purchase_price"] = p.purchasePrice
            ivs[f"property_{pid}_mortgage_value"] = p.mortgageValue
            ivs[f"property_{pid}_is_mortgaged"] = p.isMortgaged
    ivs["house_sell_back_ratio"] = config.houseSellBackRatio
    ivs["hotel_sell_back_ratio"] = config.hotelSellBackRatio

    collector.add(
        f"base_asset_{playerId}",
        "base_asset_value",
        f"Nominal recoverable value received by {playerId}",
        CalculationStatus.COMPLETE,
        CalculationSide.TRADE,
        CalculationSubject(
            playerIds=(playerId,),
            propertyIds=tuple(propertyIds),
            tradeId=trade.id,
            transferIds=tuple(transferIds),
        ),
        result=total,
        inputReferences=tuple(refs),
        inputValues=ivs,
        formula="Cash + Printed Property + Building Liquidation + Cards",
        intermediateValues={
            "cash_received": cashReceived,
            "property_value": propertyValue,
            "building_value": buildingValue,
            "card_value": cardValue,
            "line_items": lineItems,
        },
        sources={
            "get_out_of_jail_card_value": ValueSourceLabel.SPECIFICATION_DEFAULT,
            "house_sell_back_ratio": ValueSourceLabel.GAME_CONFIGURATION,
        },
        unit="currency",
    )
    return total


def _propertyReceivedValue(prop: PropertyState, config: GameConfiguration) -> int:
    base = prop.purchasePrice
    if prop.isMortgaged:
        penalty = prop.unmortgageCost
        if penalty is None:
            penalty = int(prop.mortgageValue * (1 + config.mortgageInterestRate))
        base -= penalty
    return base + _buildingReceivedValue(prop, config)


def _buildingReceivedValue(prop: PropertyState, config: GameConfiguration) -> int:
    if prop.category != "street":
        return 0
    houseVal = int(prop.houses * prop.houseCost * config.houseSellBackRatio)
    if prop.hasHotel:
        if prop.hotelLiquidationValue is not None:
            return houseVal + prop.hotelLiquidationValue
        if config.hotelLiquidationBasis == "houses_plus_hotel":
            hotelVal = int((4 * prop.houseCost + prop.hotelCost) * config.hotelSellBackRatio)
        else:
            hotelVal = int(prop.hotelCost * config.hotelSellBackRatio)
        return houseVal + hotelVal
    return houseVal


def _tradableAssetValue(asset: TradableAssetState, defaults: SpecificationDefaults) -> int:
    if asset.assetType in ("get_out_of_jail_free", "get_out_of_jail"):
        return defaults.getOutOfJailCardValue * asset.quantity
    return 0
