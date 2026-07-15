from __future__ import annotations

from dataclasses import dataclass

from Monopoly.Shared.Domain.StrEnumCompat import StrEnum
from Monopoly.StaticEvaluation.Domain.Model.BoardContext import BoardContext
from Monopoly.StaticEvaluation.Domain.Model.EvaluationInput import PropertyState, RentTable
from Monopoly.StaticEvaluation.Domain.Model.RiskReference.ClassicRiskReference import (
    ClassicRiskReference,
)
from Monopoly.StaticEvaluation.Domain.Model.SpecificationDefaults import CLASSIC_STREET_GROUPS
from Monopoly.StaticEvaluation.Domain.Model.ValueSource import ValueSourceLabel


class RentResolution(StrEnum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True, slots=True)
class ResolvedRent:
    value: int | None
    source: ValueSourceLabel
    developmentLevel: str | None = None
    multiLanding: tuple[int, ...] | None = None
    status: RentResolution = RentResolution.AVAILABLE


class RentResolver:
    """Resolve rent using the specification value-source priority chain."""

    def __init__(self, ctx: BoardContext) -> None:
        self._ctx = ctx
        self._config = ctx.config

    def groupMultiplier(self, groupId: str) -> tuple[float, ValueSourceLabel]:
        if groupId in self._config.groupMultipliers:
            return self._config.groupMultipliers[groupId], ValueSourceLabel.GAME_CONFIGURATION_OVERRIDE
        from Monopoly.StaticEvaluation.Domain.Model.SpecificationDefaults import SpecificationDefaults

        defaults = SpecificationDefaults()
        if groupId in defaults.groupStrategicMultipliers:
            return defaults.groupStrategicMultipliers[groupId], ValueSourceLabel.CLASSIC_DEFAULT
        if groupId in CLASSIC_STREET_GROUPS:
            return defaults.groupStrategicMultipliers[groupId], ValueSourceLabel.CLASSIC_DEFAULT
        return defaults.neutralGroupMultiplier, ValueSourceLabel.NEUTRAL_CUSTOM_GROUP_DEFAULT

    def streetRent(
        self,
        prop: PropertyState,
        housesPerProperty: tuple[int, ...] | None = None,
        useMaxInGroup: bool = False,
    ) -> ResolvedRent:
        groupProps = self._ctx.groupProperties(prop.groupId)
        if not groupProps:
            return ResolvedRent(None, ValueSourceLabel.UNAVAILABLE, status=RentResolution.UNAVAILABLE)

        if housesPerProperty is None:
            if useMaxInGroup:
                housesPerProperty = tuple(p.houses for p in groupProps)
            else:
                housesPerProperty = (prop.houses,)

        hasHotel = any(p.hasHotel for p in groupProps) if useMaxInGroup else prop.hasHotel
        devKey = ClassicRiskReference.normalizeDevelopment(housesPerProperty, hasHotel)

        # Priority 1: board state rent_table on max-rent property
        maxProp = max(groupProps, key=lambda p: p.purchasePrice)
        rentFromTable = self._rentFromTable(maxProp.rentTable, devKey, len(groupProps))
        if rentFromTable is not None:
            multi = self._multiLandingFromRisk(maxProp.groupId, devKey)
            return ResolvedRent(
                rentFromTable,
                ValueSourceLabel.BOARD_STATE_RENT_TABLE,
                devKey,
                multi,
            )

        # Priority 2: risk reference
        risk = ClassicRiskReference.streetLandingExposure(maxProp.groupId, devKey)
        if risk is not None:
            return ResolvedRent(risk[0], ValueSourceLabel.RISK_REFERENCE_DEFAULT, devKey, risk[1])

        return ResolvedRent(None, ValueSourceLabel.UNAVAILABLE, devKey, status=RentResolution.UNAVAILABLE)

    def railroadRent(self, ownerId: str, landedProp: PropertyState) -> ResolvedRent:
        if landedProp.isMortgaged:
            return ResolvedRent(0, ValueSourceLabel.BOARD_STATE, "mortgaged")
        count = self._ctx.railroadCount(ownerId)
        tableRent = landedProp.rentTable.railroadCount.get(count)
        if tableRent is not None:
            return ResolvedRent(tableRent, ValueSourceLabel.BOARD_STATE_RENT_TABLE)
        risk = ClassicRiskReference.railroadLandingExposure(count)
        if risk:
            return ResolvedRent(risk[0], ValueSourceLabel.RISK_REFERENCE_DEFAULT, multiLanding=risk[1])
        return ResolvedRent(None, ValueSourceLabel.UNAVAILABLE, status=RentResolution.UNAVAILABLE)

    def utilityRent(self, ownerId: str, landedProp: PropertyState) -> ResolvedRent:
        if landedProp.isMortgaged:
            return ResolvedRent(0, ValueSourceLabel.BOARD_STATE, "mortgaged")
        count = self._ctx.utilityCount(ownerId)
        tableRent = landedProp.rentTable.utilityCount.get(count)
        if tableRent is not None:
            return ResolvedRent(tableRent, ValueSourceLabel.BOARD_STATE_RENT_TABLE)
        risk = ClassicRiskReference.utilityLandingExposure(count)
        if risk:
            return ResolvedRent(risk[0], ValueSourceLabel.RISK_REFERENCE_DEFAULT, multiLanding=risk[1])
        return ResolvedRent(None, ValueSourceLabel.UNAVAILABLE, status=RentResolution.UNAVAILABLE)

    def maxAffordableRent(
        self,
        groupId: str,
        housesAchievable: int,
        groupSize: int,
    ) -> ResolvedRent:
        devKey = "-".join(str(housesAchievable) for _ in range(groupSize))
        if housesAchievable >= 5:
            devKey = "hotels"
        props = self._ctx.groupProperties(groupId)
        if not props:
            return ResolvedRent(None, ValueSourceLabel.UNAVAILABLE, status=RentResolution.UNAVAILABLE)
        maxProp = max(props, key=lambda p: p.purchasePrice)
        rent = self._rentFromTable(maxProp.rentTable, devKey, groupSize)
        if rent is not None:
            multi = self._multiLandingFromRisk(groupId, devKey)
            return ResolvedRent(rent, ValueSourceLabel.BOARD_STATE_RENT_TABLE, devKey, multi)
        risk = ClassicRiskReference.streetLandingExposure(groupId, devKey)
        if risk:
            return ResolvedRent(risk[0], ValueSourceLabel.RISK_REFERENCE_DEFAULT, devKey, risk[1])
        return ResolvedRent(None, ValueSourceLabel.UNAVAILABLE, devKey, status=RentResolution.UNAVAILABLE)

    def _rentFromTable(self, table: RentTable, devKey: str, groupSize: int) -> int | None:
        mapping = {
            "0": table.base,
            "0-0": table.base,
            "0-0-0": table.base,
        }
        if devKey in mapping and mapping[devKey] is not None:
            return mapping[devKey]
        levelMap = {
            "1-1": table.oneHouse,
            "1-1-1": table.oneHouse,
            "2-2": table.twoHouses,
            "2-2-2": table.twoHouses,
            "3-3": table.threeHouses,
            "3-3-3": table.threeHouses,
            "4-4": table.fourHouses,
            "4-4-4": table.fourHouses,
            "hotels": table.hotel,
        }
        val = levelMap.get(devKey)
        if val is not None:
            return val
        # Try parsing uniform level
        parts = devKey.split("-")
        if parts and all(p == parts[0] for p in parts):
            level = int(parts[0])
            if level == 0:
                return table.base
            if level == 1:
                return table.oneHouse
            if level == 2:
                return table.twoHouses
            if level == 3:
                return table.threeHouses
            if level == 4:
                return table.fourHouses
        return None

    def _multiLandingFromRisk(self, groupId: str, devKey: str) -> tuple[int, ...] | None:
        risk = ClassicRiskReference.streetLandingExposure(groupId, devKey)
        return risk[1] if risk else None
