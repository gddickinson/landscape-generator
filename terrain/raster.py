"""
Small pure-NumPy rasterisers for feature masks (polygon fill, thick line).

They replace cv2.fillPoly / cv2.line so the masks are defined by a few lines of plain
arithmetic that the browser port (terrain/web/static/terrain_raster.js) repeats
operation for operation, giving identical pixels. Pixel (x, y) is mask[y, x] and its
centre is at the integer point (x, y), as in OpenCV.
"""

import math
from typing import Sequence

import numpy as np


def fill_polygon(mask: np.ndarray, vertices: Sequence[Sequence[float]], value: float = 1.0) -> None:
    """Fill a simple polygon (vertices as (x, y) floats) in place, even-odd rule.

    A pixel is set when its centre lies inside: on each row y the edge crossings
    x = x0 + (y - y0) * (x1 - x0) / (y1 - y0) (half-open in y) are sorted and the
    pixels with xa <= x < xb are filled for each pair.
    """
    h, w = mask.shape
    pts = [(float(p[0]), float(p[1])) for p in vertices]
    n = len(pts)
    if n < 3:
        return
    ys = [p[1] for p in pts]
    y_lo = max(0, math.ceil(min(ys)))
    y_hi = min(h - 1, math.floor(max(ys)))
    for y in range(y_lo, y_hi + 1):
        xs = []
        for i in range(n):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            a = max(0, math.ceil(xs[k]))
            b = min(w - 1, math.ceil(xs[k + 1]) - 1)
            if b >= a:
                mask[y, a:b + 1] = value


def draw_line(mask: np.ndarray, p0: Sequence[int], p1: Sequence[int],
              value: float = 1.0, thickness: float = 2.0) -> None:
    """Draw a segment p0-p1 ((x, y) points) in place: every pixel whose centre is within
    thickness / 2 of the segment (round caps)."""
    h, w = mask.shape
    x0, y0 = float(p0[0]), float(p0[1])
    x1, y1 = float(p1[0]), float(p1[1])
    r = thickness / 2.0
    xa = max(0, math.floor(min(x0, x1) - r))
    xb = min(w - 1, math.ceil(max(x0, x1) + r))
    ya = max(0, math.floor(min(y0, y1) - r))
    yb = min(h - 1, math.ceil(max(y0, y1) + r))
    if xb < xa or yb < ya:
        return
    px = np.arange(xa, xb + 1, dtype=float)[None, :]
    py = np.arange(ya, yb + 1, dtype=float)[:, None]
    dx, dy = x1 - x0, y1 - y0
    length2 = dx * dx + dy * dy
    if length2 > 0:
        t = np.clip(((px - x0) * dx + (py - y0) * dy) / length2, 0.0, 1.0)
    else:
        t = np.zeros((1, 1))
    ex = px - (x0 + t * dx)
    ey = py - (y0 + t * dy)
    inside = ex * ex + ey * ey <= r * r
    mask[ya:yb + 1, xa:xb + 1][inside] = value
