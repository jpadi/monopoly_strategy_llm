from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CalculationSubject:
    playerIds: tuple[str, ...] = ()
    propertyIds: tuple[str, ...] = ()
    groupIds: tuple[str, ...] = ()
    tradeId: str | None = None
    transferIds: tuple[str, ...] = ()
