"""
Terrain visualization: 3D surface plots and 2D analysis grids.

Separated from generation logic so rendering can be swapped
or extended independently.
"""

import os
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np

from .biomes import BiomeColorMapper, hex_to_rgb
from .params import EnhancedTerrainParams, TerrainFeature


class TerrainVisualizer:
    """Creates matplotlib visualisations from terrain data."""

    def __init__(
        self,
        params: EnhancedTerrainParams,
        biome_mapper: BiomeColorMapper,
        output_dir: str = ".",
    ) -> None:
        self.params = params
        self.biome_mapper = biome_mapper
        self.output_dir = output_dir

    def _out(self, filename: str) -> str:
        return os.path.join(self.output_dir, filename)

    # ── colour map ───────────────────────────────────────────────────────

    def generate_color_map(
        self,
        height_map: np.ndarray,
        moisture_map: np.ndarray,
        feature_masks: Dict[str, np.ndarray],
        features: Dict[str, TerrainFeature],
    ) -> np.ndarray:
        """Build an RGB colour map from height, moisture, and features."""
        color_map = np.zeros((*height_map.shape, 3))
        seasonal_colors = self.biome_mapper.get_seasonal_palette()

        for i in range(height_map.shape[0]):
            for j in range(height_map.shape[1]):
                color_map[i, j] = self.biome_mapper.get_terrain_color(
                    height_map[i, j], moisture_map[i, j], seasonal_colors
                )

        # Feature colours are painted where a mask exceeds 0.5, in catalogue order. A "snow"
        # colour (mountain ranges) only applies at or above the season's snow line, so the
        # range shows rock below it and snow above, like the biome colours.
        above_snow_line = height_map >= self.params.snow_level
        for feature_name, mask in feature_masks.items():
            feature = features[feature_name]
            covered = mask > 0.5
            for color_name, color_hex in feature.color_map.items():
                where = covered & above_snow_line if color_name == "snow" else covered
                rgb_color = hex_to_rgb(color_hex)
                color_map = np.where(where[:, :, np.newaxis], rgb_color, color_map)

        return color_map

    # ── plotting ─────────────────────────────────────────────────────────

    def plot_3d(
        self,
        height_map: np.ndarray,
        color_map: np.ndarray,
        filename: str = "enhanced_landscape_3d.png",
    ) -> None:
        """Render a 3D surface plot."""
        fig = plt.figure(figsize=(15, 10))
        ax = fig.add_subplot(111, projection="3d")

        x = np.linspace(0, 1, self.params.size)
        y = np.linspace(0, 1, self.params.size)
        X, Y = np.meshgrid(x, y)

        ax.plot_surface(X, Y, height_map, facecolors=color_map, shade=False)
        ax.set_title(f"Procedural Landscape ({self.params.season.value})")

        plt.savefig(self._out(filename), dpi=300, bbox_inches="tight")
        plt.close()

    def plot_analysis(
        self,
        height_map: np.ndarray,
        moisture_map: np.ndarray,
        color_map: np.ndarray,
        feature_masks: Dict[str, np.ndarray],
        filename: str = "enhanced_landscape_analysis.png",
    ) -> None:
        """Render 2D analysis grid (height, moisture, features, colour)."""
        fig, axes = plt.subplots(2, 2, figsize=(15, 15))

        axes[0, 0].imshow(height_map, cmap="terrain")
        axes[0, 0].set_title("Height Map")

        axes[0, 1].imshow(moisture_map, cmap="YlGnBu")
        axes[0, 1].set_title("Moisture Map")

        feature_vis = np.zeros((*height_map.shape, 3))
        for _name, mask in feature_masks.items():
            color = np.random.rand(3)
            feature_vis += mask[:, :, np.newaxis] * color
        axes[1, 0].imshow(feature_vis)
        axes[1, 0].set_title("Feature Map")

        axes[1, 1].imshow(color_map)
        axes[1, 1].set_title("Colored Terrain")

        plt.tight_layout()
        plt.savefig(self._out(filename), dpi=300, bbox_inches="tight")
        plt.close()
