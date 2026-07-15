from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GroupId:
    value: str

    def __str__(self) -> str:
        return self.value
