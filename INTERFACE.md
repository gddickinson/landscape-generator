# Landscape Generator — Interface Map

## Package: `terrain/`

| File | Purpose | Key classes / functions |
|------|---------|----------------------|
| `params.py` | Enums, dataclasses for all configuration | `Season`, `TerrainParams`, `EnhancedTerrainParams`, `TerrainFeature` |
| `generator.py` | Noise primitives and fractal terrain | `TerrainGenerator` (`.generate_noise()`, `.generate_fractal_noise()`) |
| `biomes.py` | Colour mapping, seasonal palettes | `BiomeColorMapper`, `SEASONAL_COLORS`, `hex_to_rgb()` |
| `features.py` | Voronoi feature masks, road networks, seasonal effects | `FeatureGenerator`, `DEFAULT_FEATURES` |
| `visualization.py` | Matplotlib 3D/2D rendering | `TerrainVisualizer` (`.plot_3d()`, `.plot_analysis()`, `.generate_color_map()`) |
| `__init__.py` | Re-exports all public symbols | — |

## Entry Points

| File | Purpose |
|------|---------|
| `generate.py` | CLI (`argparse`) — seed, size, season, output dir |
| `enhanced-landscape.py` | Original monolithic script (kept for reference) |

## Tests

| File | Coverage |
|------|----------|
| `tests/test_terrain.py` | Params, noise generation, biome mapping, feature masks |

## Archive

| File | Reason |
|------|--------|
| `_archive/landscape-generator.py` | Superseded by `enhanced-landscape.py` / `terrain/` package |

## Data Flow

```
generate.py  ──▶  TerrainGenerator  ──▶  height_map, moisture_map
                  FeatureGenerator   ──▶  feature_masks
                  BiomeColorMapper   ──▶  seasonal colours
                  TerrainVisualizer  ──▶  PNG outputs
```
