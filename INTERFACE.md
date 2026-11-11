# Landscape Generator — Interface Map

## Package: `terrain/`

| File | Purpose | Key classes / functions |
|------|---------|----------------------|
| `params.py` | Enums, dataclasses for all configuration | `Season`, `TerrainParams`, `EnhancedTerrainParams`, `TerrainFeature` |
| `generator.py` | Noise primitives and fractal terrain; owns the seeded RNG | `TerrainGenerator` (`.generate_noise()`, `.generate_fractal_noise()`, `.rng`) |
| `biomes.py` | Colour mapping, seasonal palettes | `BiomeColorMapper`, `SEASONAL_COLORS`, `hex_to_rgb()` |
| `features.py` | Voronoi feature masks, road networks, seasonal effects (all draws from the shared RNG) | `FeatureGenerator`, `DEFAULT_FEATURES` |
| `raster.py` | NumPy polygon fill and thick line for feature masks (replaced cv2; mirrored in JS) | `fill_polygon()`, `draw_line()` |
| `pipeline.py` | The whole generation pipeline in one call (used by the CLI and the web app) | `generate_landscape()`, `Landscape` |
| `visualization.py` | Matplotlib 3D/2D rendering | `TerrainVisualizer` (`.plot_3d()`, `.plot_analysis()`, `.generate_color_map()`) |
| `__init__.py` | Re-exports all public symbols | — |

## Web interface: `terrain/web/`

| File | Purpose |
|------|---------|
| `app.py` | FastAPI app: `/api/info`, `/api/colormaps`, `/api/reference[/{name}]`, `/api/limits`, `POST /api/generate`; `STATIC_ENDPOINTS` for the Pages export |
| `reference.py` | Python reference landscapes for the Verify page (`CASES`, `run()`, `make_params()`) |
| `static/index.html`, `style.css` (kit), `style_app.css`, `core.js` (kit), `main.js`, `static_api.js`, `icon.svg` | Front end shell, router, static-site data layer |
| `static/np_random.js` + `ziggurat_tables.js` | Bit-exact port of `numpy.random.default_rng` (SeedSequence, PCG64, random/uniform/normal) |
| `static/ndimage.js` | `linspace`, numpy pairwise sum, `scipy.ndimage.gaussian_filter` (reflect) |
| `static/terrain_noise.js`, `voronoi.js`, `terrain_raster.js`, `terrain_features.js`, `terrain_biomes.js` | Ports of `generator.py`, the Voronoi cells, `raster.py`, `features.py`, `biomes.py` |
| `static/terrain_engine.js` | Port of `pipeline.generate_landscape` (`generateLandscape`, `DEFAULTS`) |
| `static/terrain_worker.js`, `terrain_client.js` | Web Worker running the engine; `generate()` / `cancel()` |
| `static/terrain_render.js`, `legend.js` | Canvas views (terrain, relief, 3-D, height, moisture, features, analysis) and coverage legend |
| `static/home.js`, `generate.js` + `generate_panel.js`, `seasons.js`, `verify.js`, `about.js` | Pages |
| `static/np_random.test.mjs`, `terrain_engine.test.mjs` | Node tests of the port against `tests/fixtures/terrain_reference.json` |

## Entry Points

| File | Purpose |
|------|---------|
| `generate.py` | CLI (`argparse`) — seed, size, season, density, output dir |
| `run_web.py` | Web app on http://127.0.0.1:8162 |
| `enhanced-landscape.py` | Original monolithic script (kept for reference; still uses OpenCV) |

## Scripts

| File | Purpose |
|------|---------|
| `scripts/build_static.py` | Export the static GitHub Pages site to `site/` |
| `scripts/screenshots.py` | Playwright smoke test of routes + README screenshots (`docs/img/`) |
| `scripts/make_terrain_fixture.py` | Write the Python reference values for the JS node tests |
| `scripts/make_ziggurat_tables.py` | Write `ziggurat_tables.js` from NumPy's `ziggurat_constants.h` |

## Tests

| File | Coverage |
|------|----------|
| `tests/test_terrain.py` | Params, noise generation, biome mapping, feature masks |
| `tests/test_feature_fixes.py` | Regression tests: seeded features, whole-map placement, idempotent winter snow line |
| `tests/test_raster.py` | Polygon fill / thick line (and closeness to OpenCV when installed) |
| `tests/test_web.py` | API endpoints, static build, fixture is current, runs the node tests |

## Archive

| File | Reason |
|------|--------|
| `_archive/landscape-generator.py` | Superseded by `enhanced-landscape.py` / `terrain/` package |

## Data Flow

```
generate.py / terrain.web ──▶ pipeline.generate_landscape(params, seed)
    TerrainGenerator (rng)  ──▶  height_map, moisture_map
    FeatureGenerator        ──▶  seasonal effects, feature_masks (raster.py)
    TerrainVisualizer       ──▶  colour map, PNG outputs (CLI)
browser: terrain_engine.js mirrors the same steps (same seed → same maps)
```
