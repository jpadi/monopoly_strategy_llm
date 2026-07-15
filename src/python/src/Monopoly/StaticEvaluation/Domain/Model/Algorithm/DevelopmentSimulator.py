from __future__ import annotations

from dataclasses import dataclass

from Monopoly.StaticEvaluation.Domain.Model.BoardContext import BoardContext
from Monopoly.StaticEvaluation.Domain.Model.EvaluationInput import PropertyState
from Monopoly.StaticEvaluation.Domain.Model.SpecificationDefaults import SpecificationDefaults


@dataclass(frozen=True, slots=True)
class GroupBuildResult:
    groupId: str
    housesPerProperty: int
    housesPurchased: int
    unmortgageCost: int
    budgetUsed: int
    buildable: bool
    dangerous: bool


@dataclass(frozen=True, slots=True)
class ConstructionSimulation:
    totalHousesControlled: int
    housesPurchased: int
    remainingHousesInBank: int
    groupResults: tuple[GroupBuildResult, ...]
    houseControlBonus: int
    houseDenialBonus: int


@dataclass(frozen=True, slots=True)
class DevelopmentCapability:
    groupId: str
    predicate: str
    housesPerProperty: int
    availableBudget: int
    unmortgageCost: int
    result: bool


class DevelopmentSimulator:
    """Step 3 capability procedure and Step 5 house control simulation."""

    def __init__(self, ctx: BoardContext, defaults: SpecificationDefaults | None = None) -> None:
        self._ctx = ctx
        self._defaults = defaults or SpecificationDefaults()
        self._config = ctx.config

    def mortgageCapacity(self, playerId: str, excludeGroupId: str | None = None) -> int:
        total = 0
        for prop in self._ctx.playerProperties(playerId):
            if excludeGroupId and prop.groupId == excludeGroupId:
                continue
            if prop.isMortgaged:
                continue
            if prop.houses > 0 or prop.hasHotel:
                continue
            total += prop.mortgageValue
        return total

    def unmortgageCostForGroup(self, playerId: str, groupId: str) -> int:
        if self._config.buildingAllowedWithMortgagedGroupMember:
            return 0
        total = 0
        for prop in self._ctx.groupProperties(groupId):
            if prop.ownerPlayerId == playerId and prop.isMortgaged:
                cost = prop.unmortgageCost
                if cost is None:
                    cost = int(prop.mortgageValue * (1 + self._config.mortgageInterestRate))
                total += cost
        return total

    def availableConstructionBudget(self, playerId: str, excludeGroupId: str | None = None) -> int:
        return self._ctx.playerCash(playerId) + self.mortgageCapacity(playerId, excludeGroupId)

    def simulateGroupBuild(
        self,
        playerId: str,
        groupId: str,
        budget: int,
        housesInBank: int,
    ) -> GroupBuildResult:
        unmortgage = self.unmortgageCostForGroup(playerId, groupId)
        remaining = budget - unmortgage
        props = self._ctx.groupProperties(groupId)
        if not props:
            return GroupBuildResult(groupId, 0, 0, unmortgage, 0, False, False)
        houseCost = props[0].houseCost
        if houseCost <= 0:
            return GroupBuildResult(groupId, 0, 0, unmortgage, 0, False, False)

        groupSize = len(props)
        maxNeeded = 4 * groupSize
        maxByBudget = remaining // houseCost if houseCost else 0
        maxByBank = housesInBank
        totalBuildable = min(maxByBudget, maxByBank, maxNeeded)

        if self._config.evenBuildingRequired:
            housesPerProp = 0
            spent = 0
            bankLeft = housesInBank
            for level in range(1, 5):
                costThisRound = houseCost * groupSize
                if spent + costThisRound > remaining or bankLeft < groupSize:
                    break
                housesPerProp = level
                spent += costThisRound
                bankLeft -= groupSize
        else:
            housesPerProp = min(4, totalBuildable // groupSize) if groupSize else 0
            spent = housesPerProp * groupSize * houseCost

        purchased = housesPerProp * groupSize
        buildable = housesPerProp >= 1
        dangerous = housesPerProp >= 3
        return GroupBuildResult(groupId, housesPerProp, purchased, unmortgage, spent + unmortgage, buildable, dangerous)

    def evaluateCapability(
        self,
        playerId: str,
        groupId: str,
        predicate: str,
    ) -> DevelopmentCapability:
        budget = self.availableConstructionBudget(playerId, excludeGroupId=groupId)
        unmortgage = self.unmortgageCostForGroup(playerId, groupId)
        housesInBank = self._ctx.availableHousesInBank()
        result = self.simulateGroupBuild(playerId, groupId, budget, housesInBank)
        if predicate == "buildable":
            ok = result.buildable
        else:
            ok = result.dangerous
        return DevelopmentCapability(
            groupId=groupId,
            predicate=predicate,
            housesPerProperty=result.housesPerProperty,
            availableBudget=budget,
            unmortgageCost=unmortgage,
            result=ok,
        )

    def developmentMultiplier(self, housesPerProperty: int) -> float:
        if housesPerProperty <= 0:
            return self._defaults.developmentMultipliers["cannot_build"]
        if housesPerProperty <= 2:
            return self._defaults.developmentMultipliers["one_to_two"]
        if housesPerProperty == 3:
            return self._defaults.developmentMultipliers["three"]
        return self._defaults.developmentMultipliers["four"]

    def simulateAllMonopolies(self, playerId: str) -> ConstructionSimulation:
        monopolies = self._ctx.completedMonopolies(playerId)
        budget = self.availableConstructionBudget(playerId)
        housesInBank = self._ctx.availableHousesInBank()
        currentHouses = sum(p.houses for p in self._ctx.playerProperties(playerId) if p.category == "street")

        # Allocate budget to groups in descending monopoly value order (simplified: by house cost desc)
        ordered = sorted(
            monopolies,
            key=lambda gid: self._ctx.groupProperties(gid)[0].houseCost if self._ctx.groupProperties(gid) else 0,
            reverse=True,
        )

        remainingBudget = budget
        remainingBank = housesInBank
        groupResults: list[GroupBuildResult] = []
        totalPurchased = 0

        for gid in ordered:
            grpBudget = remainingBudget
            res = self.simulateGroupBuild(playerId, gid, grpBudget, remainingBank)
            groupResults.append(res)
            remainingBudget -= res.budgetUsed
            remainingBank -= res.housesPurchased
            totalPurchased += res.housesPurchased

        totalControlled = currentHouses + totalPurchased
        totalHouses = self._config.totalHouses
        remainingInBank = totalHouses - totalControlled

        houseControlBonus = self._tierBonus(totalControlled, self._defaults.houseControlBonuses)
        houseDenialBonus = self._denialBonus(remainingInBank, self._defaults.houseDenialBonuses)

        return ConstructionSimulation(
            totalHousesControlled=totalControlled,
            housesPurchased=totalPurchased,
            remainingHousesInBank=remainingInBank,
            groupResults=tuple(groupResults),
            houseControlBonus=houseControlBonus,
            houseDenialBonus=houseDenialBonus,
        )

    def _tierBonus(self, value: int, tiers: dict[int, int]) -> int:
        bonus = 0
        for threshold in sorted(tiers.keys()):
            if value >= threshold:
                bonus = tiers[threshold]
        return bonus

    def _denialBonus(self, remaining: int, tiers: dict[int, int]) -> int:
        bonus = 0
        for threshold in sorted(tiers.keys(), reverse=True):
            if remaining <= threshold:
                bonus = tiers[threshold]
        return bonus

    def buildingLiquidationValue(self, playerId: str) -> int:
        total = 0
        for prop in self._ctx.playerProperties(playerId):
            total += self.propertyBuildingLiquidation(prop)
        return total

    def propertyBuildingLiquidation(self, prop: PropertyState) -> int:
        if prop.category != "street":
            return 0
        ratio = self._config.houseSellBackRatio
        houseVal = int(prop.houses * prop.houseCost * ratio)
        if prop.hasHotel:
            if prop.hotelLiquidationValue is not None:
                hotelVal = prop.hotelLiquidationValue
            elif self._config.hotelLiquidationBasis == "houses_plus_hotel":
                hotelVal = int((4 * prop.houseCost + prop.hotelCost) * self._config.hotelSellBackRatio)
            else:
                hotelVal = int(prop.hotelCost * self._config.hotelSellBackRatio)
            return houseVal + hotelVal
        return houseVal
