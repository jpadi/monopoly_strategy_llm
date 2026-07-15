from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class GameConfiguration:
    rulesetName: str = "classic_monopoly"
    rulesetVersion: str = "1.0"
    startingCash: int = 1500
    totalHouses: int = 32
    totalHotels: int = 12
    mortgageInterestRate: float = 0.10
    mustPayInterestOnMortgagedPropertyTransfer: bool = True
    evenBuildingRequired: bool = True
    evenSellingRequired: bool = True
    houseSellBackRatio: float = 0.50
    hotelSellBackRatio: float = 0.50
    hotelLiquidationBasis: str = "houses_plus_hotel"
    buildingAllowedWithMortgagedGroupMember: bool = False
    groupRentRequiresAllMembersUnmortgaged: bool = False
    groupMultipliers: dict[str, float] = field(default_factory=dict)
    implementationOverrides: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class RentTable:
    base: int | None = None
    oneHouse: int | None = None
    twoHouses: int | None = None
    threeHouses: int | None = None
    fourHouses: int | None = None
    hotel: int | None = None
    railroadCount: dict[int, int] = field(default_factory=dict)
    utilityCount: dict[int, int] = field(default_factory=dict)

    @classmethod
    def fromDict(cls, data: dict[str, Any] | None) -> "RentTable":
        if not data:
            return cls()
        railroadCount: dict[int, int] = {}
        utilityCount: dict[int, int] = {}
        for key, value in data.items():
            if key.startswith("railroad_") and key.endswith("_owned"):
                count = int(key.split("_")[1])
                railroadCount[count] = int(value)
            elif key.startswith("utility_") and key.endswith("_owned"):
                count = int(key.split("_")[1])
                utilityCount[count] = int(value)
        return cls(
            base=data.get("base"),
            oneHouse=data.get("one_house"),
            twoHouses=data.get("two_houses"),
            threeHouses=data.get("three_houses"),
            fourHouses=data.get("four_houses"),
            hotel=data.get("hotel"),
            railroadCount=railroadCount,
            utilityCount=utilityCount,
        )


@dataclass(frozen=True, slots=True)
class PropertyState:
    id: str
    displayName: str = ""
    category: str = "street"
    groupId: str = ""
    ownerPlayerId: str | None = None
    purchasePrice: int = 0
    mortgageValue: int = 0
    unmortgageCost: int | None = None
    isMortgaged: bool = False
    isTradable: bool = True
    houses: int = 0
    hasHotel: bool = False
    houseCost: int = 0
    hotelCost: int = 0
    hotelLiquidationValue: int | None = None
    rentTable: RentTable = field(default_factory=RentTable)


@dataclass(frozen=True, slots=True)
class TradableAssetState:
    id: str
    displayName: str = ""
    assetType: str = ""
    ownerPlayerId: str | None = None
    isTradable: bool = True
    quantity: int = 1


@dataclass(frozen=True, slots=True)
class PlayerState:
    id: str
    displayName: str = ""
    cash: int = 0
    getOutOfJailFreeCards: int = 0
    ownedProperties: tuple[str, ...] = ()
    ownedTradableAssets: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class GameStateInfo:
    availableHouses: int = 32
    availableHotels: int = 12


@dataclass(frozen=True, slots=True)
class BoardState:
    players: tuple[PlayerState, ...] = ()
    properties: tuple[PropertyState, ...] = ()
    tradableAssets: tuple[TradableAssetState, ...] = ()
    gameState: GameStateInfo = field(default_factory=GameStateInfo)


@dataclass(frozen=True, slots=True)
class Transfer:
    id: str
    fromPlayerId: str
    toPlayerId: str
    assetType: str
    assetId: str | None = None
    amount: int | None = None


@dataclass(frozen=True, slots=True)
class Trade:
    id: str
    initiatingPlayerId: str
    participants: tuple[str, ...]
    transfers: tuple[Transfer, ...] = ()


@dataclass(frozen=True, slots=True)
class EvaluationInput:
    gameConfiguration: GameConfiguration
    boardStateBefore: BoardState
    trade: Trade
    boardStateAfter: BoardState
    evidenceId: str = "evidence_static_trade_imbalance_001"
