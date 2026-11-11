"""Tests for terrain/raster.py (the NumPy polygon fill and thick line that replaced cv2)."""
import unittest

import numpy as np
from scipy.spatial import Voronoi

from terrain.raster import draw_line, fill_polygon

try:
    import cv2
except ImportError:  # OpenCV is no longer a dependency; comparisons are optional
    cv2 = None


class TestFillPolygon(unittest.TestCase):
    def test_square(self):
        m = np.zeros((10, 10))
        fill_polygon(m, [(2, 2), (6, 2), (6, 5), (2, 5)])
        expected = np.zeros((10, 10))
        expected[2:5, 2:6] = 1  # half-open: rows 2..4, columns 2..5
        np.testing.assert_array_equal(m, expected)

    def test_clipped_to_image(self):
        m = np.zeros((8, 8))
        fill_polygon(m, [(-5, -5), (20, -5), (20, 20), (-5, 20)])
        self.assertEqual(m.sum(), 64)

    @unittest.skipIf(cv2 is None, "OpenCV not installed")
    def test_close_to_opencv_on_voronoi_cells(self):
        rng = np.random.default_rng(0)
        total = diff = 0
        for _ in range(10):
            vor = Voronoi(rng.random((20, 2)) * 128)
            for i in range(20):
                region = vor.regions[vor.point_region[i]]
                if -1 in region or not region:
                    continue
                a, b = np.zeros((128, 128)), np.zeros((128, 128))
                cv2.fillPoly(a, [vor.vertices[region].astype(np.int32)], 1)
                fill_polygon(b, vor.vertices[region])
                total += a.sum()
                diff += (a != b).sum()
        self.assertLess(diff / total, 0.08)


class TestDrawLine(unittest.TestCase):
    def test_horizontal_round_caps(self):
        m = np.zeros((9, 12))
        draw_line(m, (3, 4), (8, 4))
        self.assertEqual(m[3:6, 3:9].sum(), 18)  # three rows thick along the segment
        self.assertEqual(m[4, 2], 1)  # round cap
        self.assertEqual(m[3, 2], 0)

    def test_point_and_offscreen(self):
        m = np.zeros((5, 5))
        draw_line(m, (2, 2), (2, 2))
        self.assertEqual(m.sum(), 5)  # disc of radius 1: plus shape
        draw_line(m, (-20, -20), (-10, -15))
        self.assertEqual(m.sum(), 5)


if __name__ == "__main__":
    unittest.main()
