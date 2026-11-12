"""
Biome colour mapping and seasonal palettes.

Separates rendering/colour logic from terrain generation.
Seasonal colour palettes are defined as data (not interleaved with methods).
"""

from typing import Dict, Tuple

from .params import EnhancedTerrainParams, Season


# ── Seasonal colour palettes ────────────────────────────────────────────────

SEASONAL_COLORS: Dict[Season, Dict[str, str]] = {
    Season.SPRING: {
        "grassland": "#4CA64C",
        "forest": "#2D5A27",
        "fields": "#90B44B",
        "trees": "#4F7942",
    },
    Season.SUMMER: {
        "grassland": "#2D5A27",
        "forest": "#1A3B1A",
        "fields": "#7D944D",
        "trees": "#1A3B1A",
    },
    Season.AUTUMN: {
        "grassland": "#8B6B43",
        "forest": "#8B4513",
        "fields": "#DAA520",
        "trees": "#D2691E",
    },
    Season.WINTER: {
        "grassland": "#E8E8E8",
        "forest": "#4F666A",
        "fields": "#F5F5F5",
        "trees": "#2F4F4F",
    },
}


# Feature colours (by their name in TerrainFeature.color_map) that take the season's
# palette entry instead of the fixed hex: crops -> "fields", trees -> "trees".
SEASONAL_FEATURE_COLORS: Dict[str, str] = {"crops": "fields", "trees": "trees"}


# ── Colour helper ───────────────────────────────────────────────────────────

def hex_to_rgb(hex_color: str) -> Tuple[float, float, float]:
    """Convert hex colour string to (r, g, b) floats in [0, 1]."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) / 255 for i in (0, 2, 4))


# ── Biome mapper ────────────────────────────────────────────────────────────

class BiomeColorMapper:
    """Maps (height, moisture, season) to terrain colours."""

    def __init__(self, params: EnhancedTerrainParams) -> None:
        self.params = params

    def get_terrain_color(
        self,
        height: float,
        moisture: float,
        seasonal_colors: Dict[str, str],
    ) -> Tuple[float, float, float]:
        """Return RGB tuple for a terrain cell."""
        p = self.params

        if height < p.sea_level:
            depth = height / p.sea_level
            return hex_to_rgb("#001933" if depth < 0.5 else "#003366")

        if height < p.sea_level + 0.05:
            return hex_to_rgb("#D9B382")  # Beach

        if height < p.mountain_level:
            if moisture > 0.6:
                return hex_to_rgb(seasonal_colors["forest"])
            return hex_to_rgb(seasonal_colors["grassland"])

        if height < p.snow_level:
            return hex_to_rgb("#6F6F6F")  # Mountain rock

        return hex_to_rgb("#FFFFFF")  # Snow

    def get_seasonal_palette(self) -> Dict[str, str]:
        """Return the colour palette for the current season."""
        return SEASONAL_COLORS[self.params.season]
