# Session log

## 2026-11-11 — Web interface and static GitHub Pages site (branch `web-interface`)

- **Bugs fixed** (separate commits, regression tests in `tests/test_feature_fixes.py`):
  - Feature masks and roads used the global unseeded `np.random` / `random`, so `--seed` did not reproduce
    the landscape; they now use the TerrainGenerator's seeded generator (Voronoi cells visited in point order).
  - Voronoi polygons were rescaled by `size / max(all Voronoi vertices)` (~0.3), squashing features into the
    top-left corner; vertices are now used as the pixel coordinates they are.
  - `apply_seasonal_effects` lowered `params.snow_level` again on every call; now idempotent.
  - README usage imported a non-existent `landscape_generator` module; rewritten for `generate.py` and
    `terrain.pipeline`, and road/settlement descriptions corrected.
- **Refactor**: `terrain/pipeline.py` (`generate_landscape`) shared by the CLI and the web app.
- **Rasteriser**: `terrain/raster.py` replaces `cv2.fillPoly` / `cv2.line` in the package so the browser can
  reproduce the masks exactly (polygon pixels within a few % of OpenCV; diagonal roads ~1 px thinner).
- **Web**: `terrain/web/` (FastAPI + ES modules), `run_web.py` (port 8162), static export, Pages workflow.
  The JS port reproduces NumPy's RNG bit for bit and the whole pipeline; node tests against
  `tests/fixtures/terrain_reference.json` show max height difference 5e-13 (fixture rounding) and identical colours.
- **Needs George's decision**: the mountain-range feature paints rock then snow over the same mask, so mountain
  ranges always show as snow; the seasonal `fields` / `trees` colours are defined but never used.
- Tests: `python -m pytest -q tests` (40 passed, includes the node tests).
