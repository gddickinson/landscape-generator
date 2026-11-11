# Enhanced Landscape Generator

A sophisticated Python-based procedural landscape generator that creates realistic terrains with multiple biomes, seasonal variations, and various geographic features. The generator uses advanced noise algorithms and feature placement techniques to create natural-looking landscapes.

## Features

### Terrain Generation
- Procedural height map generation using multi-octave noise
- Realistic moisture distribution
- Natural-looking terrain features
- Smooth transitions between different biomes

### Geographic Features
- Mountains and hills
- Lakes and water bodies
- Forests and vegetation
- Desert regions
- Road networks
- Settlements/buildings
- Agricultural fields

### Seasonal Variations
- Spring: Lush vegetation, high moisture
- Summer: Deep greens, moderate moisture
- Autumn: Warm colors, transitional moisture
- Winter: Snow coverage, low moisture

### Visualization
- 3D terrain visualization
- Height map analysis
- Moisture distribution maps
- Feature placement visualization
- Colored terrain rendering

## Installation

1. Clone this repository:
```bash
git clone https://github.com/gddickinson/landscape-generator.git
cd landscape-generator
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command line

```bash
python generate.py                              # seed 42, 512 x 512, summer
python generate.py --seed 7 --season winter     # seasons: spring, summer, fall, winter
python generate.py --size 256 --density 0.15 --output ./out
```

### Basic Usage

Generate a landscape with default settings from Python:

```python
from terrain.params import EnhancedTerrainParams, Season
from terrain.pipeline import generate_landscape

params = EnhancedTerrainParams(size=512, season=Season.SUMMER, feature_density=0.08)
land = generate_landscape(params, seed=42)   # same seed -> same landscape
land.height_map, land.moisture_map, land.feature_masks, land.color_map
```

### Customizing Parameters

```python
# Create custom parameters
params = EnhancedTerrainParams(
    size=512,              # Size of the generated landscape
    octaves=6,            # Number of noise octaves
    persistence=0.5,      # How quickly amplitudes diminish
    lacunarity=2.0,       # How quickly frequency increases
    base_frequency=4.0,   # Initial frequency
    sea_level=0.35,       # Water level threshold
    mountain_level=0.7,   # Mountain threshold
    snow_level=0.85,      # Snow line threshold
    season=Season.AUTUMN,  # Current season
    feature_density=0.08   # Density of geographic features
)
```

## Output Files

The generator produces two main output files:

1. `enhanced_landscape_3d.png`
   - 3D visualization of the landscape
   - Shows terrain elevation with seasonal coloring
   - Includes all generated features

2. `enhanced_landscape_analysis.png`
   - Four-panel analysis view:
     - Height map
     - Moisture map
     - Feature distribution
     - Final colored terrain

## Terrain Features

### Height Map
- Uses multi-octave noise for natural terrain variation
- Implements realistic mountain and valley formation
- Smooth transitions between elevation levels

### Moisture System
- Dynamic moisture distribution
- Affects vegetation and biome placement
- Seasonal variations in moisture levels

### Feature Generation
- Natural feature placement using Voronoi diagrams
- Organic shape generation for lakes and forests
- Road network generation with jittered, curved paths between random settlement points
- Settlement areas placed as Voronoi regions (like the other features)

### Biome System
- Dynamic biome assignment based on height and moisture
- Seasonal color variations
- Natural transitions between different biomes

## Customization Options

### Terrain Modification
```python
# Adjust terrain parameters
params.mountain_level = 0.8  # More mountainous terrain
params.sea_level = 0.3      # Less water coverage
```

### Feature Density
```python
# Modify feature placement
params.feature_density = 0.05  # Sparse features
# or
params.feature_density = 0.15  # Dense features
```

### Seasonal Changes
```python
# Change seasons
params.season = Season.WINTER  # Winter landscape
# or
params.season = Season.SPRING  # Spring landscape
```

## Contributing

Areas for potential enhancement:

- Additional terrain features
- More complex biome systems
- Enhanced road network algorithms
- River system generation
- Erosion simulation
- Climate system implementation
- Additional visualization options

## Technical Details

### Noise Generation
- Multi-octave Perlin-like noise built from randomly rotated, phase-shifted sine waves plus Gaussian jitter
- Gaussian smoothing for natural transitions
- One seeded NumPy generator (`np.random.default_rng(seed)`) drives every random draw, so a seed reproduces the landscape

### Feature Placement
- Voronoi diagram-based region generation
- Organic shape generation using noise masks
- Road segments through randomly offset waypoints between settlement points

### Visualization
- Matplotlib for 2D and 3D plotting
- Custom colormaps for different seasons
- Multiple analysis views for debugging

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built using numpy and matplotlib
- OpenCV for feature mask generation
- Scipy for various mathematical operations
- Shapely (used only by the legacy `enhanced-landscape.py` script)


---
*Built with AI assistance from [Claude (Anthropic)](https://claude.com/).*
