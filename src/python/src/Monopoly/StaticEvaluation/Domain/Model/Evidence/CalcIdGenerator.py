class CalcIdGenerator:
    """Deterministic sequential calculation IDs: calc_001, calc_002, ..."""

    def __init__(self) -> None:
        self._counter = 0

    def next(self) -> str:
        self._counter += 1
        return f"calc_{self._counter:03d}"

    @property
    def count(self) -> int:
        return self._counter
