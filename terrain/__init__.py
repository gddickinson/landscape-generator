"""
Terrain generation package.

Modules:
    params       - TerrainParams, EnhancedTerrainParams, Season enum
    generator    - Noise generation and fractal terrain
    biomes       - Biome/terrain color mapping and seasonal colors
    features     - Feature masks, road networks, settlements (Voronoi-based)
    visualization - 3D surface plots and 2D analysis views
    raster       - NumPy polygon fill / thick line for feature masks
    pipeline     - generate_landscape(): the whole pipeline in one call
    web/         - FastAPI web app and the JS port (see INTERFACE.md)
"""

from .params import TerrainParams, EnhancedTerrainParams, Season, TerrainFeature
from .generator import TerrainGenerator
from .biomes import BiomeColorMapper
from .features import FeatureGenerator
from .visualization import TerrainVisualizer

__all__ = [
    "TerrainParams",
    "EnhancedTerrainParams",
    "Season",
    "TerrainFeature",
    "TerrainGenerator",
    "BiomeColorMapper",
    "FeatureGenerator",
    "TerrainVisualizer",
]
