"""Regression tests for feature colouring (2026-11-11).

1. Mountain ranges were painted rock and then snow over the same mask, so they always showed
   solid white. Snow must appear only above the (season-adjusted) snow line; rock below it.
"""
import unittest

import numpy as np

from terrain.biomes import BiomeColorMapper, hex_to_rgb
from terrain.features import DEFAULT_FEATURES
from terrain.params import EnhancedTerrainParams, Season
from terrain.visualization import TerrainVisualizer


def _colors(season, feature, height):
    p = EnhancedTerrainParams(size=4, season=season)
    viz = TerrainVisualizer(p, BiomeColorMapper(p))
    h = np.full((4, 4), height)
    m = np.full((4, 4), 0.5)
    masks = {k: np.zeros((4, 4)) for k in DEFAULT_FEATURES}
    masks[feature][:2] = 1.0  # top half covered by the feature
    return viz.generate_color_map(h, m, masks, DEFAULT_FEATURES)


class TestMountainRangeColours(unittest.TestCase):
    def test_rock_below_snow_line(self):
        c = _colors(Season.SUMMER, "mountain_range", 0.5)
        np.testing.assert_allclose(c[0, 0], hex_to_rgb("#6F6F6F"))

    def test_snow_above_snow_line(self):
        c = _colors(Season.SUMMER, "mountain_range", 0.9)
        np.testing.assert_allclose(c[0, 0], hex_to_rgb("#FFFFFF"))

    def test_winter_lowers_mountain_snow_line(self):
        p = EnhancedTerrainParams(size=4, season=Season.WINTER)
        p.snow_level = 0.68  # as set by apply_seasonal_effects in winter
        viz = TerrainVisualizer(p, BiomeColorMapper(p))
        masks = {k: np.zeros((4, 4)) for k in DEFAULT_FEATURES}
        masks["mountain_range"][:] = 1.0
        c = viz.generate_color_map(np.full((4, 4), 0.75), np.full((4, 4), 0.5), masks, DEFAULT_FEATURES)
        np.testing.assert_allclose(c[0, 0], hex_to_rgb("#FFFFFF"))


if __name__ == "__main__":
    unittest.main()
