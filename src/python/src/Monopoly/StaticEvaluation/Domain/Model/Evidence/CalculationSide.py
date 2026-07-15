from Monopoly.Shared.Domain.StrEnumCompat import StrEnum


class CalculationSide(StrEnum):
    BEFORE = "before"
    AFTER = "after"
    DELTA = "delta"
    TRADE = "trade"
