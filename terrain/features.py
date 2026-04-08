"""
Terrain feature generation: lakes, forests, settlements, roads, etc.

Uses Voronoi tessellation with organic noise masking for natural shapes,
and simple path generation for road networks.
"""

import random
from typing import Dict, Tuple

import cv2
import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.spatial import Voronoi

from .params import EnhancedTerrainParams, Season, TerrainFeature
from .generator import TerrainGenerator


# ── Default feature catalogue ───────────────────────────────────────────────

DEFAULT_FEATURES: Dict[str, TerrainFeature] = {
    "lake": TerrainFeature(
        name="Lake",
        height_modifier=-0.3,
        moisture_modifier=0.8,
        color_map={"water": "#005C99"},
        min_size=0.05,
        max_size=0.15,
    ),
    "mountain_range": TerrainFeature(
        name="Mountain Range",
        height_modifier=0.4,
        moisture_modifier=0.3,
        color_map={"rock": "#6F6F6F", "snow": "#FFFFFF"},
        min_size=0.1,
        max_size=0.3,
    ),
    "forest": TerrainFeature(
        name="Forest",
        height_modifier=0.1,
        moisture_modifier=0.6,
        color_map={"trees": "#1A3B1A"},
        min_size=0.08,
        max_size=0.2,
    ),
    "desert": TerrainFeature(
        name="Desert",
        height_modifier=0.1,
        moisture_modifier=-0.4,
        color_map={"sand": "#D9B382"},
        min_size=0.1,
        max_size=0.25,
    ),
    "road_network": TerrainFeature(
        name="Road Network",
        height_modifier=0.0,
        moisture_modifier=-0.1,
        color_map={"road": "#5C5C5C"},
        min_size=0.02,
        max_size=0.05,
    ),
    "settlement": TerrainFeature(
        name="Settlement",
        height_modifier=0.05,
        moisture_modifier=-0.2,
        color_map={"building": "#8C8C8C"},
        min_size=0.03,
        max_size=0.08,
    ),
    "fields": TerrainFeature(
        name="Agricultural Fields",
        height_modifier=0.0,
        moisture_modifier=0.2,
        color_map={"crops": "#7D944D"},
        min_size=0.05,
        max_size=0.15,
    ),
}


# ── Feature generator ───────────────────────────────────────────────────────

class FeatureGenerator:
    """Generates feature masks and road networks."""

    def __init__(
        self,
        params: EnhancedTerrainParams,
        noise_gen: TerrainGenerator,
    ) -> None:
        self.params = params
        self.noise_gen = noise_gen
        self.features = dict(DEFAULT_FEATURES)

    def generate_feature_mask(self, feature: TerrainFeature) -> np.ndarray:
        """Generate an organic feature mask using Voronoi + noise."""
        size = self.params.size
        mask = np.zeros((size, size))

        base_noise = self.noise_gen.generate_noise((size, size), 4.0)

        num_points = max(4, int(size * self.params.feature_density))
        points = np.random.rand(num_points, 2) * size

        try:
            vor = Voronoi(points)
        except Exception:
            # Degenerate point set — return empty mask
            return mask

        for region in vor.regions:
            if -1 in region or len(region) == 0:
                continue
            if random.random() < 0.3:
                polygon = [vor.vertices[i] for i in region]
                img_coords = np.array(polygon) * size / max(vor.vertices.max(), 1e-6)
                img_coords = img_coords.astype(np.int32)
                cv2.fillPoly(mask, [img_coords], 1)

        mask *= (base_noise > 0.3).astype(float)
        mask = gaussian_filter(mask, sigma=2.0)
        return mask

    def generate_road_network(self) -> np.ndarray:
        """Generate a road network connecting random settlements."""
        size = self.params.size
        mask = np.zeros((size, size))

        num_settlements = max(2, int(size * self.params.feature_density * 0.3))
        settlements = np.random.rand(num_settlements, 2) * size

        for i in range(len(settlements)):
            for j in range(i + 1, len(settlements)):
                if random.random() < 0.4:
                    pt1 = settlements[i].astype(int)
                    pt2 = settlements[j].astype(int)
                    num_points = 5
                    prev_point = None
                    for k in range(num_points):
                        t = k / (num_points - 1)
                        offset = np.random.normal(0, size * 0.05, 2)
                        mid_point = (pt1 * (1 - t) + pt2 * t + offset).astype(int)
                        if prev_point is not None:
                            cv2.line(
                                mask,
                                tuple(prev_point),
                                tuple(mid_point),
                                1,
                                thickness=2,
                            )
                        prev_point = mid_point

        mask = gaussian_filter(mask, sigma=1.0)
        return mask

    def apply_seasonal_effects(
        self,
        height_map: np.ndarray,
        moisture_map: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Modify maps according to the current season."""
        season = self.params.season

        if season == Season.WINTER:
            self.params.snow_level *= 0.8
            moisture_map = moisture_map * 0.7
        elif season == Season.SUMMER:
            moisture_map = moisture_map * 0.9
            height_map = height_map * 1.05
        elif season == Season.SPRING:
            moisture_map = moisture_map * 1.2
            height_map = height_map * 0.95
        elif season == Season.AUTUMN:
            moisture_map = moisture_map * 0.85

        return height_map, moisture_map
