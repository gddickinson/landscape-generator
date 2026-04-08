"""
Smoke tests for the terrain generation package.
"""

import unittest
import numpy as np

from terrain.params import EnhancedTerrainParams, Season, TerrainFeature
from terrain.generator import TerrainGenerator
from terrain.biomes import BiomeColorMapper, hex_to_rgb, SEASONAL_COLORS
from terrain.features import FeatureGenerator, DEFAULT_FEATURES


class TestTerrainParams(unittest.TestCase):
    """Sanity checks for parameter dataclasses."""

    def test_default_params(self):
        p = EnhancedTerrainParams()
        self.assertEqual(p.size, 512)
        self.assertEqual(p.season, Season.SUMMER)

    def test_season_values(self):
        self.assertEqual(Season.WINTER.value, "winter")
        self.assertEqual(Season.AUTUMN.value, "fall")


class TestNoiseGeneration(unittest.TestCase):
    """Tests for noise and fractal generation."""

    def setUp(self):
        self.params = EnhancedTerrainParams(size=64)
        self.gen = TerrainGenerator(self.params, seed=42)

    def test_noise_shape(self):
        noise = self.gen.generate_noise((64, 64), 4.0)
        self.assertEqual(noise.shape, (64, 64))

    def test_noise_range(self):
        noise = self.gen.generate_noise((64, 64), 4.0)
        self.assertAlmostEqual(noise.min(), 0.0, places=5)
        self.assertAlmostEqual(noise.max(), 1.0, places=5)

    def test_fractal_noise_shape(self):
        noise = self.gen.generate_fractal_noise()
        self.assertEqual(noise.shape, (64, 64))

    def test_fractal_noise_range(self):
        noise = self.gen.generate_fractal_noise()
        self.assertGreaterEqual(noise.min(), 0.0)
        self.assertLessEqual(noise.max(), 1.0)

    def test_deterministic_with_seed(self):
        g1 = TerrainGenerator(self.params, seed=123)
        g2 = TerrainGenerator(self.params, seed=123)
        n1 = g1.generate_fractal_noise()
        n2 = g2.generate_fractal_noise()
        np.testing.assert_array_equal(n1, n2)


class TestBiomeMapper(unittest.TestCase):
    """Tests for biome colour assignment."""

    def setUp(self):
        self.params = EnhancedTerrainParams()
        self.mapper = BiomeColorMapper(self.params)

    def test_hex_to_rgb(self):
        r, g, b = hex_to_rgb("#FF0000")
        self.assertAlmostEqual(r, 1.0)
        self.assertAlmostEqual(g, 0.0)
        self.assertAlmostEqual(b, 0.0)

    def test_deep_water(self):
        color = self.mapper.get_terrain_color(0.1, 0.5, SEASONAL_COLORS[Season.SUMMER])
        # Should return a dark blue (deep or shallow water)
        self.assertIsInstance(color, tuple)
        self.assertEqual(len(color), 3)

    def test_snow(self):
        color = self.mapper.get_terrain_color(0.95, 0.5, SEASONAL_COLORS[Season.SUMMER])
        self.assertEqual(color, (1.0, 1.0, 1.0))

    def test_all_seasons_have_palettes(self):
        for season in Season:
            self.assertIn(season, SEASONAL_COLORS)
            palette = SEASONAL_COLORS[season]
            self.assertIn("grassland", palette)
            self.assertIn("forest", palette)


class TestFeatureGenerator(unittest.TestCase):
    """Tests for feature mask generation."""

    def setUp(self):
        self.params = EnhancedTerrainParams(size=64, feature_density=0.1)
        self.gen = TerrainGenerator(self.params, seed=42)
        self.feat = FeatureGenerator(self.params, self.gen)

    def test_feature_mask_shape(self):
        feature = DEFAULT_FEATURES["forest"]
        mask = self.feat.generate_feature_mask(feature)
        self.assertEqual(mask.shape, (64, 64))

    def test_road_network_shape(self):
        roads = self.feat.generate_road_network()
        self.assertEqual(roads.shape, (64, 64))

    def test_seasonal_effects(self):
        h = np.ones((64, 64)) * 0.5
        m = np.ones((64, 64)) * 0.5
        self.params.season = Season.WINTER
        h2, m2 = self.feat.apply_seasonal_effects(h.copy(), m.copy())
        # Winter reduces moisture
        self.assertLess(m2.mean(), m.mean())


if __name__ == "__main__":
    unittest.main()
