# Enhanced Landscape Generator -- Roadmap

## Current State
A procedural terrain generator with two script files: `landscape-generator.py` (219 lines, basic version) and `enhanced-landscape.py` (421 lines, advanced version with biomes, seasons, Voronoi features, roads, and settlements). Uses numpy, matplotlib, scipy, OpenCV, and shapely. Outputs 3D terrain visualization and analysis PNGs. The generated images are committed to the repo. Good use of dataclasses and enums, but everything lives in two standalone scripts with no package structure.

## Short-term Improvements
- [ ] Create a proper package: `terrain/` with `generator.py`, `features.py`, `biomes.py`, `visualization.py`, and `params.py`
- [ ] Remove or `.gitignore` the generated PNG files (4 images committed to repo)
- [ ] Remove or archive `landscape-generator.py` -- `enhanced-landscape.py` supersedes it
- [ ] Add a `requirements.txt` with numpy, matplotlib, scipy, opencv-python, shapely
- [ ] Add type hints to all methods in `EnhancedLandscapeGenerator` (partially present)
- [ ] Add unit tests for noise generation, biome assignment, and feature placement
- [ ] Add a CLI interface with argparse for seed, size, season, and output path

## Feature Enhancements
- [ ] Implement hydraulic erosion simulation for more realistic terrain
- [ ] Add river generation that follows terrain gradients to water bodies
- [ ] Implement climate zones based on latitude and altitude
- [ ] Add vegetation density maps influenced by moisture and terrain
- [ ] Support tiling -- generate seamlessly connecting terrain chunks
- [ ] Add real-time preview using matplotlib interactive mode before final render
- [ ] Implement heightmap export (16-bit PNG or raw) for use in game engines
- [ ] Add texture generation for each biome (grass, rock, sand, snow)

## Long-term Vision
- [ ] Integrate with a real-time 3D viewer (PyVista, Open3D, or Three.js export)
- [ ] Add tectonic plate simulation for continent-scale terrain generation
- [ ] Implement city/civilization placement with road networks between settlements
- [ ] Export to game engine formats (Unity terrain, Unreal heightmap)
- [ ] Add GPU-accelerated noise generation for large terrains (4096x4096+)
- [ ] Create an interactive GUI for painting terrain features and adjusting parameters in real time

## Technical Debt
- [ ] Two separate scripts doing similar things -- consolidate into one package
- [ ] `np.random.seed()` is used globally -- switch to `np.random.Generator` for reproducible, non-global RNG
- [ ] Voronoi-based feature placement depends on scipy.spatial but error handling for degenerate cases is missing
- [ ] The color mapping logic is interleaved with generation logic -- separate rendering from generation
- [ ] No `setup.py` or `pyproject.toml` for packaging
- [ ] Season color palettes are hard-coded in methods -- externalize to a configuration dict or file
