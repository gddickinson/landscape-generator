"""
The full landscape pipeline (height, moisture, season, features, colours) in one call.

Shared by the CLI (generate.py) and the web app (terrain/web/), so both run exactly
the same steps in the same order (the order matters: every step draws from one
seeded random generator).
"""

from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np

from .biomes import BiomeColorMapper
from .features import FeatureGenerator
from .generator import TerrainGenerator
from .params import EnhancedTerrainParams, TerrainFeature
from .visualization import TerrainVisualizer


@dataclass
class Landscape:
    """Result of generate_landscape: maps are (size, size); color_map is RGB in [0, 1]."""
    params: EnhancedTerrainParams
    base_height: np.ndarray
    height_map: np.ndarray
    moisture_map: np.ndarray
    feature_masks: Dict[str, np.ndarray]
    features: Dict[str, TerrainFeature]
    color_map: np.ndarray


def generate_landscape(
    params: EnhancedTerrainParams, seed: Optional[int] = None
) -> Landscape:
    """Generate a landscape: fractal height and moisture, seasonal effects, feature
    masks (roads separately), normalisation, then the biome/feature colour map.

    Note: params.snow_level is set for the season (lowered in winter) as a side effect.
    """
    gen = TerrainGenerator(params, seed=seed)
    feat_gen = FeatureGenerator(params, gen)
    viz = TerrainVisualizer(params, BiomeColorMapper(params))

    height_map = gen.generate_fractal_noise()
    base_height = height_map.copy()
    moisture_map = gen.generate_fractal_noise()

    height_map, moisture_map = feat_gen.apply_seasonal_effects(height_map, moisture_map)

    feature_masks = {}
    for name, feature in feat_gen.features.items():
        if name == "road_network":
            feature_masks[name] = feat_gen.generate_road_network()
        else:
            feature_masks[name] = feat_gen.generate_feature_mask(feature)

        height_map += feature_masks[name] * feature.height_modifier
        moisture_map += feature_masks[name] * feature.moisture_modifier

    height_map = (height_map - height_map.min()) / (height_map.max() - height_map.min())
    moisture_map = moisture_map.clip(0, 1)

    color_map = viz.generate_color_map(
        height_map, moisture_map, feature_masks, feat_gen.features
    )
    return Landscape(params, base_height, height_map, moisture_map,
                     feature_masks, feat_gen.features, color_map)
