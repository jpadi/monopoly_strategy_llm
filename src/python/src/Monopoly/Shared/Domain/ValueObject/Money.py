from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Money:
    """Integer currency amount; no floating-point money arithmetic."""

    amount: int

    def __post_init__(self) -> None:
        if not isinstance(self.amount, int):
            raise TypeError("Money.amount must be int")

    @classmethod
    def zero(cls) -> "Money":
        return cls(0)

    def __add__(self, other: "Money") -> "Money":
        return Money(self.amount + other.amount)

    def __sub__(self, other: "Money") -> "Money":
        return Money(self.amount - other.amount)

    def __neg__(self) -> "Money":
        return Money(-self.amount)

    def __lt__(self, other: "Money") -> bool:
        return self.amount < other.amount

    def __le__(self, other: "Money") -> bool:
        return self.amount <= other.amount

    def __gt__(self, other: "Money") -> bool:
        return self.amount > other.amount

    def __ge__(self, other: "Money") -> bool:
        return self.amount >= other.amount

    def max(self, other: "Money") -> "Money":
        return self if self.amount >= other.amount else other

    def min(self, other: "Money") -> "Money":
        return self if self.amount <= other.amount else other

    def is_negative(self) -> bool:
        return self.amount < 0

    def is_nonnegative(self) -> bool:
        return self.amount >= 0

    def __int__(self) -> int:
        return self.amount
