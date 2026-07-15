"""Map JSON/dict input to EvaluationInput domain model."""

from __future__ import annotations

from typing import Any

from Monopoly.StaticEvaluation.Domain.Model.EvaluationInput import (
    BoardState,
    EvaluationInput,
    GameConfiguration,
    GameStateInfo,
    PlayerState,
    PropertyState,
    RentTable,
    TradableAssetState,
    Trade,
    Transfer,
)


class EvaluationInputMapper:
    @classmethod
    def fromDict(cls, data: dict[str, Any]) -> EvaluationInput:
        config = cls._mapGameConfiguration(data.get("game_configuration", {}))
        return EvaluationInput(
            gameConfiguration=config,
            boardStateBefore=cls._mapBoardState(data.get("board_state_before", {})),
            trade=cls._mapTrade(data.get("trade", {})),
            boardStateAfter=cls._mapBoardState(data.get("board_state_after", {})),
            evidenceId=data.get("evidence_id", "evidence_static_trade_imbalance_001"),
        )

    @classmethod
    def _mapGameConfiguration(cls, data: dict[str, Any]) -> GameConfiguration:
        return GameConfiguration(
            rulesetName=data.get("ruleset_name", "classic_monopoly"),
            rulesetVersion=data.get("ruleset_version", "1.0"),
            startingCash=int(data.get("starting_cash", 1500)),
            totalHouses=int(data.get("total_houses", 32)),
            totalHotels=int(data.get("total_hotels", 12)),
            mortgageInterestRate=float(data.get("mortgage_interest_rate", 0.10)),
            mustPayInterestOnMortgagedPropertyTransfer=bool(
                data.get("must_pay_interest_on_mortgaged_property_transfer", True)
            ),
            evenBuildingRequired=bool(data.get("even_building_required", True)),
            evenSellingRequired=bool(data.get("even_selling_required", True)),
            houseSellBackRatio=float(data.get("house_sell_back_ratio", 0.50)),
            hotelSellBackRatio=float(data.get("hotel_sell_back_ratio", 0.50)),
            hotelLiquidationBasis=data.get("hotel_liquidation_basis", "houses_plus_hotel"),
            buildingAllowedWithMortgagedGroupMember=bool(
                data.get("building_allowed_with_mortgaged_group_member", False)
            ),
            groupRentRequiresAllMembersUnmortgaged=bool(data.get("group_rent_requires_all_members_unmortgaged", False)),
            groupMultipliers={str(k): float(v) for k, v in data.get("group_multipliers", {}).items()},
        )

    @classmethod
    def _mapBoardState(cls, data: dict[str, Any]) -> BoardState:
        gs = data.get("game_state", {})
        return BoardState(
            players=tuple(cls._mapPlayer(p) for p in data.get("players", [])),
            properties=tuple(cls._mapProperty(p) for p in data.get("properties", [])),
            tradableAssets=tuple(cls._mapTradableAsset(a) for a in data.get("tradable_assets", [])),
            gameState=GameStateInfo(
                availableHouses=int(gs.get("available_houses", 32)),
                availableHotels=int(gs.get("available_hotels", 12)),
            ),
        )

    @classmethod
    def _mapPlayer(cls, data: dict[str, Any]) -> PlayerState:
        return PlayerState(
            id=data["id"],
            displayName=data.get("display_name", ""),
            cash=int(data.get("cash", 0)),
            getOutOfJailFreeCards=int(data.get("get_out_of_jail_free_cards", 0)),
            ownedProperties=tuple(data.get("owned_properties", [])),
            ownedTradableAssets=tuple(data.get("owned_tradable_assets", [])),
        )

    @classmethod
    def _mapProperty(cls, data: dict[str, Any]) -> PropertyState:
        unmortgage = data.get("unmortgage_cost")
        hotelLiq = data.get("hotel_liquidation_value")
        return PropertyState(
            id=data["id"],
            displayName=data.get("display_name", ""),
            category=data.get("category", "street"),
            groupId=data.get("group_id", ""),
            ownerPlayerId=data.get("owner_player_id"),
            purchasePrice=int(data.get("purchase_price", 0)),
            mortgageValue=int(data.get("mortgage_value", 0)),
            unmortgageCost=int(unmortgage) if unmortgage is not None else None,
            isMortgaged=bool(data.get("is_mortgaged", False)),
            isTradable=bool(data.get("is_tradable", True)),
            houses=int(data.get("houses", 0)),
            hasHotel=bool(data.get("has_hotel", False)),
            houseCost=int(data.get("house_cost", 0)),
            hotelCost=int(data.get("hotel_cost", 0)),
            hotelLiquidationValue=int(hotelLiq) if hotelLiq is not None else None,
            rentTable=RentTable.fromDict(data.get("rent_table")),
        )

    @classmethod
    def _mapTradableAsset(cls, data: dict[str, Any]) -> TradableAssetState:
        return TradableAssetState(
            id=data["id"],
            displayName=data.get("display_name", ""),
            assetType=data.get("asset_type", ""),
            ownerPlayerId=data.get("owner_player_id"),
            isTradable=bool(data.get("is_tradable", True)),
            quantity=int(data.get("quantity", 1)),
        )

    @classmethod
    def _mapTrade(cls, data: dict[str, Any]) -> Trade:
        return Trade(
            id=data.get("id", "trade_001"),
            initiatingPlayerId=data.get("initiating_player_id", ""),
            participants=tuple(data.get("participants", [])),
            transfers=tuple(cls._mapTransfer(t) for t in data.get("transfers", [])),
        )

    @classmethod
    def _mapTransfer(cls, data: dict[str, Any]) -> Transfer:
        rawAmount = data.get("amount")
        amount = int(rawAmount) if rawAmount is not None else None
        assetId = data.get("asset_id")
        return Transfer(
            id=data.get("id", ""),
            fromPlayerId=data.get("from_player_id", ""),
            toPlayerId=data.get("to_player_id", ""),
            assetType=data.get("asset_type", data.get("transfer_type", "")),
            assetId=assetId,
            amount=amount,
        )
