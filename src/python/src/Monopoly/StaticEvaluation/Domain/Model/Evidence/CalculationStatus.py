from Monopoly.Shared.Domain.StrEnumCompat import StrEnum


class CalculationStatus(StrEnum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"
