from __future__ import annotations

from dataclasses import dataclass

from Monopoly.StaticEvaluation.Domain.Model.EvaluationInput import (
    BoardState,
    GameConfiguration,
    PropertyState,
)
from Monopoly.StaticEvaluation.Domain.Model.SpecificationDefaults import (
    RAILROAD_GROUP,
    UTILITY_GROUP,
)


@dataclass(frozen=True, slots=True)
class GroupInfo:
    groupId: str
    propertyIds: tuple[str, ...]
    size: int


class BoardContext:
    """Helper for board analysis derived from a BoardState."""

    def __init__(self, board: BoardState, config: GameConfiguration) -> None:
        self._board = board
        self._config = config
        self._properties: dict[str, PropertyState] = {p.id: p for p in board.properties}
        self._players: dict[str, int] = {p.id: p.cash for p in board.players}
        self._groups = self._buildGroups()

    @property
    def board(self) -> BoardState:
        return self._board

    @property
    def config(self) -> GameConfiguration:
        return self._config

    @property
    def properties(self) -> dict[str, PropertyState]:
        return self._properties

    def playerCash(self, playerId: str) -> int:
        for player in self._board.players:
            if player.id == playerId:
                return player.cash
        return 0

    def player(self, playerId: str):
        for player in self._board.players:
            if player.id == playerId:
                return player
        return None

    def property(self, propertyId: str) -> PropertyState | None:
        return self._properties.get(propertyId)

    def groups(self) -> dict[str, GroupInfo]:
        return self._groups

    def streetGroups(self) -> dict[str, GroupInfo]:
        return {gid: info for gid, info in self._groups.items() if gid not in (RAILROAD_GROUP, UTILITY_GROUP)}

    def groupProperties(self, groupId: str) -> tuple[PropertyState, ...]:
        info = self._groups.get(groupId)
        if info is None:
            return ()
        return tuple(self._properties[pid] for pid in info.propertyIds if pid in self._properties)

    def ownsGroup(self, playerId: str, groupId: str) -> bool:
        props = self.groupProperties(groupId)
        if not props:
            return False
        return all(p.ownerPlayerId == playerId for p in props)

    def completedMonopolies(self, playerId: str) -> list[str]:
        return [gid for gid, _ in self.streetGroups().items() if self.ownsGroup(playerId, gid)]

    def railroadCount(self, playerId: str) -> int:
        return sum(1 for p in self._properties.values() if p.groupId == RAILROAD_GROUP and p.ownerPlayerId == playerId)

    def utilityCount(self, playerId: str) -> int:
        return sum(1 for p in self._properties.values() if p.groupId == UTILITY_GROUP and p.ownerPlayerId == playerId)

    def housesOnBoard(self) -> int:
        return sum(p.houses for p in self._properties.values() if p.category == "street")

    def hotelsOnBoard(self) -> int:
        return sum(1 for p in self._properties.values() if p.hasHotel)

    def availableHousesInBank(self) -> int:
        return self._board.gameState.availableHouses

    def availableHotelsInBank(self) -> int:
        return self._board.gameState.availableHotels

    def developedMonopolyCount(self) -> int:
        return len(self.developedMonopolyGroupIds())

    def developedMonopolyGroupIds(self) -> list[str]:
        """Street groups owned by one player with at least one house or hotel."""
        result: list[str] = []
        for gid in self.streetGroups():
            props = self.groupProperties(gid)
            if not props:
                continue
            owner = props[0].ownerPlayerId
            if owner is None or not all(p.ownerPlayerId == owner for p in props):
                continue
            if any(p.houses >= 1 or p.hasHotel for p in props):
                result.append(gid)
        return result

    def playerProperties(self, playerId: str) -> tuple[PropertyState, ...]:
        return tuple(p for p in self._properties.values() if p.ownerPlayerId == playerId)

    def blockedPlayers(self, propertyId: str) -> list[str]:
        prop = self._properties.get(propertyId)
        if prop is None or not prop.groupId or prop.groupId in (RAILROAD_GROUP, UTILITY_GROUP):
            return []
        group = self._groups.get(prop.groupId)
        if group is None:
            return []
        blocked: list[str] = []
        for player in self._board.players:
            if player.id == prop.ownerPlayerId:
                continue
            owned = sum(1 for pid in group.propertyIds if self._properties[pid].ownerPlayerId == player.id)
            if 0 < owned < group.size:
                blocked.append(player.id)
        return blocked

    def immediatelyBlockedPlayers(self, propertyId: str) -> list[str]:
        prop = self._properties.get(propertyId)
        if prop is None or not prop.groupId:
            return []
        group = self._groups.get(prop.groupId)
        if group is None:
            return []
        result: list[str] = []
        for player in self._board.players:
            if player.id == prop.ownerPlayerId:
                continue
            owned = sum(1 for pid in group.propertyIds if self._properties[pid].ownerPlayerId == player.id)
            if owned == group.size - 1:
                result.append(player.id)
        return result

    def playersNeedingProperty(self, propertyId: str) -> list[str]:
        prop = self._properties.get(propertyId)
        if prop is None or not prop.groupId:
            return []
        group = self._groups.get(prop.groupId)
        if group is None:
            return []
        needing: list[str] = []
        for player in self._board.players:
            if player.id == prop.ownerPlayerId:
                continue
            owned = sum(1 for pid in group.propertyIds if self._properties[pid].ownerPlayerId == player.id)
            if 0 < owned < group.size:
                needing.append(player.id)
        return needing

    def oneFromMonopoly(self, playerId: str) -> list[str]:
        """Groups where player is within one property of completing."""
        result: list[str] = []
        for gid, info in self.streetGroups().items():
            owned = sum(1 for pid in info.propertyIds if self._properties[pid].ownerPlayerId == playerId)
            if owned == info.size - 1:
                result.append(gid)
        return result

    def mostlyBlockedBoard(self) -> bool:
        """No street group can be completed by any single player without a trade."""
        for _gid, info in self.streetGroups().items():
            for player in self._board.players:
                owned = sum(1 for pid in info.propertyIds if self._properties[pid].ownerPlayerId == player.id)
                unowned = sum(1 for pid in info.propertyIds if self._properties[pid].ownerPlayerId is None)
                if owned + unowned >= info.size:
                    return False
        return True

    def opponentIds(self, playerId: str) -> list[str]:
        return [p.id for p in self._board.players if p.id != playerId]

    def _buildGroups(self) -> dict[str, GroupInfo]:
        groups: dict[str, list[str]] = {}
        for prop in self._board.properties:
            if prop.groupId:
                groups.setdefault(prop.groupId, []).append(prop.id)
        return {
            gid: GroupInfo(groupId=gid, propertyIds=tuple(sorted(pids)), size=len(pids)) for gid, pids in groups.items()
        }

    @classmethod
    def withHypotheticalOwnership(
        cls,
        board: BoardState,
        config: GameConfiguration,
        overrides: dict[str, str | None],
    ) -> BoardContext:
        """Return a context with property ownership overridden (for predicates)."""
        newProps = []
        for prop in board.properties:
            if prop.id in overrides:
                newProps.append(
                    PropertyState(
                        id=prop.id,
                        displayName=prop.displayName,
                        category=prop.category,
                        groupId=prop.groupId,
                        ownerPlayerId=overrides[prop.id],
                        purchasePrice=prop.purchasePrice,
                        mortgageValue=prop.mortgageValue,
                        unmortgageCost=prop.unmortgageCost,
                        isMortgaged=prop.isMortgaged,
                        isTradable=prop.isTradable,
                        houses=prop.houses,
                        hasHotel=prop.hasHotel,
                        houseCost=prop.houseCost,
                        hotelCost=prop.hotelCost,
                        hotelLiquidationValue=prop.hotelLiquidationValue,
                        rentTable=prop.rentTable,
                    )
                )
            else:
                newProps.append(prop)
        from Monopoly.StaticEvaluation.Domain.Model.EvaluationInput import BoardState as BS

        return cls(
            BS(
                players=board.players,
                properties=tuple(newProps),
                tradableAssets=board.tradableAssets,
                gameState=board.gameState,
            ),
            config,
        )
