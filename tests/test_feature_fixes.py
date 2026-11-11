"""Regression tests for bugs fixed in terrain/features.py (2026-11-11).

1. Feature placement used the global, unseeded np.random / random modules, so --seed did not make
   the landscape reproducible (lakes, forests, roads moved on every run).
2. Voronoi polygons were rescaled by size / max(all Voronoi vertices); the far-away vertices of the
   hull cells made that factor far below 1, squashing every feature into the top-left corner.
3. apply_seasonal_effects multiplied params.snow_level by 0.8 on every call, so a second call
   (e.g. generating twice with one params object) lowered the snow line again.
"""
import unittest

import numpy as np

from terrain.features import DEFAULT_FEATURES, FeatureGenerator
from terrain.generator import TerrainGenerator
from terrain.params import EnhancedTerrainParams, Season


def _masks(seed, size=96, density=0.15):
    p = EnhancedTerrainParams(size=size, feature_density=density)
    f = FeatureGenerator(p, TerrainGenerator(p, seed=seed))
    out = {k: f.generate_feature_mask(v) for k, v in DEFAULT_FEATURES.items() if k != "road_network"}
    out["road_network"] = f.generate_road_network()
    return out


class TestFeatureSeeding(unittest.TestCase):
    def test_same_seed_same_features(self):
        a, b = _masks(5), _masks(5)
        for k in a:
            np.testing.assert_array_equal(a[k], b[k], err_msg=k)

    def test_different_seed_different_features(self):
        a, b = _masks(5), _masks(6)
        self.assertTrue(any(not np.array_equal(a[k], b[k]) for k in a))


class TestFeatureCoverage(unittest.TestCase):
    def test_features_spread_over_whole_map(self):
        """Filled feature pixels, pooled over seeds, must be spread over the four quadrants
        (each ~25 %), not concentrated near the origin (the old scaling gave ~50 % top-left)."""
        size, h = 96, 48
        counts = np.zeros(4)
        for seed in range(1, 9):
            for k, m in _masks(seed, size).items():
                if k != "road_network":
                    b = m > 0.5
                    counts += [b[:h, :h].sum(), b[:h, h:].sum(), b[h:, :h].sum(), b[h:, h:].sum()]
        share = counts / counts.sum()
        for q in share:
            self.assertGreater(q, 0.12, share)
            self.assertLess(q, 0.38, share)


class TestSeasonalIdempotent(unittest.TestCase):
    def test_winter_snow_level_not_compounded(self):
        p = EnhancedTerrainParams(size=8, season=Season.WINTER)
        f = FeatureGenerator(p, TerrainGenerator(p, seed=1))
        h, m = np.full((8, 8), 0.5), np.full((8, 8), 0.5)
        f.apply_seasonal_effects(h, m)
        f.apply_seasonal_effects(h, m)
        self.assertAlmostEqual(p.snow_level, 0.85 * 0.8)

    def test_snow_level_restored_for_other_seasons(self):
        p = EnhancedTerrainParams(size=8, season=Season.WINTER)
        f = FeatureGenerator(p, TerrainGenerator(p, seed=1))
        h, m = np.full((8, 8), 0.5), np.full((8, 8), 0.5)
        f.apply_seasonal_effects(h, m)
        p.season = Season.SUMMER
        f.apply_seasonal_effects(h, m)
        self.assertAlmostEqual(p.snow_level, 0.85)


if __name__ == "__main__":
    unittest.main()
