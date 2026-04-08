"""
Terrain generation parameters, enums, and dataclasses.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict


class Season(Enum):
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "fall"
    WINTER = "winter"


@dataclass
class TerrainFeature:
    """Describes a placeable terrain feature (lake, forest, settlement, etc.)."""
    name: str
    height_modifier: float
    moisture_modifier: float
    color_map: Dict[str, str]
    min_size: float
    max_size: float


@dataclass
class TerrainParams:
    """Basic terrain generation parameters."""
    size: int = 256
    octaves: int = 6
    persistence: float = 0.5
    lacunarity: float = 2.0
    base_frequency: float = 4.0
    sea_level: float = 0.4
    mountain_level: float = 0.7
    snow_level: float = 0.85


@dataclass
class EnhancedTerrainParams:
    """Enhanced terrain parameters with season and feature density."""
    size: int = 512
    octaves: int = 6
    persistence: float = 0.5
    lacunarity: float = 2.0
    base_frequency: float = 4.0
    sea_level: float = 0.35
    mountain_level: float = 0.7
    snow_level: float = 0.85
    season: Season = Season.SUMMER
    feature_density: float = 0.1
