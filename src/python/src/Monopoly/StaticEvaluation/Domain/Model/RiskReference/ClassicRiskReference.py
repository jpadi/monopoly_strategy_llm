"""Classic Monopoly risk reference tables from risk_reference.md v1.0."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LandingExposureRow:
    developmentKey: str
    maximumRent: int
    landings: tuple[int, ...]  # 1-6 landings


# Repair tables: Both Cards column
REPAIR_HOUSES_BOTH: dict[int, int] = {
    0: 0,
    4: 260,
    8: 520,
    12: 780,
    16: 1040,
    20: 1300,
    24: 1560,
    28: 1820,
    29: 1885,
    30: 1950,
    31: 2015,
    32: 2080,
}

REPAIR_HOTELS_BOTH: dict[int, int] = {
    0: 0,
    1: 215,
    2: 430,
    3: 645,
    4: 860,
    5: 1075,
    6: 1290,
    7: 1505,
    8: 1720,
    9: 1935,
    10: 2150,
    11: 2365,
    12: 2580,
}

# Street group risk matrices keyed by group_id
STREET_RISK_MATRICES: dict[str, tuple[LandingExposureRow, ...]] = {
    "brown": (
        LandingExposureRow("0-0", 8, (8, 16, 24, 32, 40, 48)),
        LandingExposureRow("1-1", 20, (20, 40, 60, 80, 100, 120)),
        LandingExposureRow("2-2", 60, (60, 120, 180, 240, 300, 360)),
        LandingExposureRow("3-3", 180, (180, 360, 540, 720, 900, 1080)),
        LandingExposureRow("4-4", 320, (320, 640, 960, 1280, 1600, 1920)),
        LandingExposureRow("hotels", 450, (450, 900, 1350, 1800, 2250, 2700)),
    ),
    "light_blue": (
        LandingExposureRow("0-0-0", 12, (12, 24, 36, 48, 60, 72)),
        LandingExposureRow("1-1-1", 60, (60, 120, 180, 240, 300, 360)),
        LandingExposureRow("2-2-2", 180, (180, 360, 540, 720, 900, 1080)),
        LandingExposureRow("3-3-3", 500, (500, 1000, 1500, 2000, 2500, 3000)),
        LandingExposureRow("4-4-4", 700, (700, 1400, 2100, 2800, 3500, 4200)),
        LandingExposureRow("hotels", 900, (900, 1800, 2700, 3600, 4500, 5400)),
    ),
    "pink": (
        LandingExposureRow("0-0-0", 28, (28, 56, 84, 112, 140, 168)),
        LandingExposureRow("1-1-1", 140, (140, 280, 420, 560, 700, 840)),
        LandingExposureRow("2-2-2", 400, (400, 800, 1200, 1600, 2000, 2400)),
        LandingExposureRow("3-3-3", 850, (850, 1700, 2550, 3400, 4250, 5100)),
        LandingExposureRow("4-4-4", 1025, (1025, 2050, 3075, 4100, 5125, 6150)),
        LandingExposureRow("hotels", 1200, (1200, 2400, 3600, 4800, 6000, 7200)),
    ),
    "orange": (
        LandingExposureRow("0-0-0", 32, (32, 64, 96, 128, 160, 192)),
        LandingExposureRow("1-1-1", 80, (80, 160, 240, 320, 400, 480)),
        LandingExposureRow("2-2-2", 220, (220, 440, 660, 880, 1100, 1320)),
        LandingExposureRow("3-3-3", 600, (600, 1200, 1800, 2400, 3000, 3600)),
        LandingExposureRow("4-4-4", 800, (800, 1600, 2400, 3200, 4000, 4800)),
        LandingExposureRow("hotels", 1000, (1000, 2000, 3000, 4000, 5000, 6000)),
    ),
    "red": (
        LandingExposureRow("0-0-0", 40, (40, 80, 120, 160, 200, 240)),
        LandingExposureRow("1-1-1", 100, (100, 200, 300, 400, 500, 600)),
        LandingExposureRow("2-2-2", 300, (300, 600, 900, 1200, 1500, 1800)),
        LandingExposureRow("3-3-3", 750, (750, 1500, 2250, 3000, 3750, 4500)),
        LandingExposureRow("4-4-4", 925, (925, 1850, 2775, 3700, 4625, 5550)),
        LandingExposureRow("hotels", 1100, (1100, 2200, 3300, 4400, 5500, 6600)),
    ),
    "yellow": (
        LandingExposureRow("0-0-0", 48, (48, 96, 144, 192, 240, 288)),
        LandingExposureRow("1-1-1", 120, (120, 240, 360, 480, 600, 720)),
        LandingExposureRow("2-2-2", 360, (360, 720, 1080, 1440, 1800, 2160)),
        LandingExposureRow("3-3-3", 850, (850, 1700, 2550, 3400, 4250, 5100)),
        LandingExposureRow("4-4-4", 1025, (1025, 2050, 3075, 4100, 5125, 6150)),
        LandingExposureRow("hotels", 1200, (1200, 2400, 3600, 4800, 6000, 7200)),
    ),
    "green": (
        LandingExposureRow("0-0-0", 56, (56, 112, 168, 224, 280, 336)),
        LandingExposureRow("1-1-1", 150, (150, 300, 450, 600, 750, 900)),
        LandingExposureRow("2-2-2", 450, (450, 900, 1350, 1800, 2250, 2700)),
        LandingExposureRow("3-3-3", 1000, (1000, 2000, 3000, 4000, 5000, 6000)),
        LandingExposureRow("4-4-4", 1200, (1200, 2400, 3600, 4800, 6000, 7200)),
        LandingExposureRow("hotels", 1400, (1400, 2800, 4200, 5600, 7000, 8400)),
    ),
    "dark_blue": (
        LandingExposureRow("0-0", 100, (100, 200, 300, 400, 500, 600)),
        LandingExposureRow("1-1", 200, (200, 400, 600, 800, 1000, 1200)),
        LandingExposureRow("2-2", 600, (600, 1200, 1800, 2400, 3000, 3600)),
        LandingExposureRow("3-3", 1400, (1400, 2800, 4200, 5600, 7000, 8400)),
        LandingExposureRow("4-4", 1700, (1700, 3400, 5100, 6800, 8500, 10200)),
        LandingExposureRow("hotels", 2000, (2000, 4000, 6000, 8000, 10000, 12000)),
    ),
}

RAILROAD_RISK: dict[int, tuple[int, ...]] = {
    1: (25, 50, 75, 100, 125, 150),
    2: (50, 100, 150, 200, 250, 300),
    3: (100, 200, 300, 400, 500, 600),
    4: (200, 400, 600, 800, 1000, 1200),
}

UTILITY_RISK: dict[int, tuple[int, ...]] = {
    1: (48, 96, 144, 192, 240, 288),
    2: (120, 240, 360, 480, 600, 720),
}


class ClassicRiskReference:
    """Rent matrices, repair tables, and development classification from risk_reference.md."""

    @staticmethod
    def normalizeDevelopment(housesPerProperty: tuple[int, ...], hasHotel: bool) -> str:
        if hasHotel or any(h >= 5 for h in housesPerProperty):
            return "hotels"
        if any(h >= 4 for h in housesPerProperty):
            sep = "-" * (len(housesPerProperty) - 1) if len(housesPerProperty) > 1 else ""
            return "4" + sep + "4" if len(housesPerProperty) == 2 else "4-4-4"
        maxH = max(housesPerProperty) if housesPerProperty else 0
        return "-".join(str(maxH) for _ in housesPerProperty)

    @staticmethod
    def repairExposureBothCards(totalHouses: int, totalHotels: int) -> int:
        houseCost = ClassicRiskReference._lookupRepair(REPAIR_HOUSES_BOTH, totalHouses)
        hotelCost = ClassicRiskReference._lookupRepair(REPAIR_HOTELS_BOTH, totalHotels)
        return houseCost + hotelCost

    @staticmethod
    def _lookupRepair(table: dict[int, int], count: int) -> int:
        if count <= 0:
            return 0
        keys = sorted(table.keys())
        result = 0
        for key in keys:
            if key <= count:
                result = table[key]
            else:
                break
        return result

    @staticmethod
    def streetLandingExposure(groupId: str, developmentKey: str) -> tuple[int, tuple[int, ...]] | None:
        matrix = STREET_RISK_MATRICES.get(groupId)
        if matrix is None:
            return None
        for row in matrix:
            if row.developmentKey == developmentKey:
                return row.maximumRent, row.landings
        return None

    @staticmethod
    def railroadLandingExposure(count: int) -> tuple[int, tuple[int, ...]] | None:
        landings = RAILROAD_RISK.get(count)
        if landings is None:
            return None
        return landings[0], landings

    @staticmethod
    def utilityLandingExposure(count: int) -> tuple[int, tuple[int, ...]] | None:
        landings = UTILITY_RISK.get(count)
        if landings is None:
            return None
        return landings[0], landings
