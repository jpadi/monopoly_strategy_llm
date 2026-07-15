from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlayerId:
    value: str

    def __str__(self) -> str:
        return self.value
