import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.ndimage import gaussian_filter
import colorsys
from dataclasses import dataclass
from typing import Tuple, List, Optional, Dict
import random
from enum import Enum
from scipy.spatial import Voronoi
from shapely.geometry import Point, LineString, Polygon
import cv2

class Season(Enum):
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "fall"
    WINTER = "winter"

@dataclass
class TerrainFeature:
    name: str
    height_modifier: float
    moisture_modifier: float
    color_map: Dict[str, str]
    min_size: float
    max_size: float

@dataclass
class EnhancedTerrainParams:
    size: int = 512  # Increased size for more detail
    octaves: int = 6
    persistence: float = 0.5
    lacunarity: float = 2.0
    base_frequency: float = 4.0
    sea_level: float = 0.35
    mountain_level: float = 0.7
    snow_level: float = 0.85
    season: Season = Season.SUMMER
    feature_density: float = 0.1

class EnhancedLandscapeGenerator:
    def __init__(self, params: EnhancedTerrainParams = None, seed: Optional[int] = None):
        self.params = params or EnhancedTerrainParams()
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)

        self.features = self._initialize_features()
        self.seasonal_colors = self._initialize_seasonal_colors()

    def generate_noise(self, shape: Tuple[int, int], frequency: float) -> np.ndarray:
        """Generate improved Perlin-like noise with multiple frequencies"""
        noise = np.zeros(shape)
        x = np.linspace(0, frequency, shape[0])
        y = np.linspace(0, frequency, shape[1])
        X, Y = np.meshgrid(x, y)

        # Generate multiple waves with random orientations
        for i in range(6):  # Increased number of waves
            angle = random.uniform(0, 2 * np.pi)
            phase = random.uniform(0, 2 * np.pi)
            freq_mul = 2 ** i

            # Rotate coordinates
            X_rot = X * np.cos(angle) - Y * np.sin(angle)
            Y_rot = X * np.sin(angle) + Y * np.cos(angle)

            noise += np.sin(X_rot * freq_mul + phase) * np.cos(Y_rot * freq_mul + phase)
            # Add some random perturbation
            noise += np.random.normal(0, 0.1, shape) * (0.5 ** i)

        return (noise - noise.min()) / (noise.max() - noise.min())

    def generate_fractal_noise(self) -> np.ndarray:
        """Generate fractal noise using multiple octaves"""
        noise = np.zeros((self.params.size, self.params.size))
        frequency = self.params.base_frequency
        amplitude = 1.0

        for _ in range(self.params.octaves):
            noise += amplitude * self.generate_noise(
                (self.params.size, self.params.size),
                frequency
            )
            frequency *= self.params.lacunarity
            amplitude *= self.params.persistence

        # Normalize to [0, 1]
        noise = (noise - noise.min()) / (noise.max() - noise.min())

        # Apply Gaussian smoothing
        noise = gaussian_filter(noise, sigma=1.0)

        return noise

    def get_terrain_color(self, height: float, moisture: float,
                         seasonal_colors: Dict[str, str]) -> Tuple[float, float, float]:
        """Determine terrain color based on height, moisture, and season"""
        if height < self.params.sea_level:
            depth = height / self.params.sea_level
            return self._hex_to_rgb('#001933' if depth < 0.5 else '#003366')

        elif height < self.params.sea_level + 0.05:
            return self._hex_to_rgb('#D9B382')  # Beach

        elif height < self.params.mountain_level:
            if moisture > 0.6:
                return self._hex_to_rgb(seasonal_colors['forest'])
            else:
                return self._hex_to_rgb(seasonal_colors['grassland'])

        elif height < self.params.snow_level:
            return self._hex_to_rgb('#6F6F6F')  # Mountain

        else:
            return self._hex_to_rgb('#FFFFFF')  # Snow

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> Tuple[float, float, float]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4))


    def _initialize_features(self) -> Dict[str, TerrainFeature]:
        """Initialize different terrain features"""
        return {
            'lake': TerrainFeature(
                name="Lake",
                height_modifier=-0.3,
                moisture_modifier=0.8,
                color_map={'water': '#005C99'},
                min_size=0.05,
                max_size=0.15
            ),
            'mountain_range': TerrainFeature(
                name="Mountain Range",
                height_modifier=0.4,
                moisture_modifier=0.3,
                color_map={'rock': '#6F6F6F', 'snow': '#FFFFFF'},
                min_size=0.1,
                max_size=0.3
            ),
            'forest': TerrainFeature(
                name="Forest",
                height_modifier=0.1,
                moisture_modifier=0.6,
                color_map={'trees': '#1A3B1A'},
                min_size=0.08,
                max_size=0.2
            ),
            'desert': TerrainFeature(
                name="Desert",
                height_modifier=0.1,
                moisture_modifier=-0.4,
                color_map={'sand': '#D9B382'},
                min_size=0.1,
                max_size=0.25
            ),
            'road_network': TerrainFeature(
                name="Road Network",
                height_modifier=0.0,
                moisture_modifier=-0.1,
                color_map={'road': '#5C5C5C'},
                min_size=0.02,
                max_size=0.05
            ),
            'settlement': TerrainFeature(
                name="Settlement",
                height_modifier=0.05,
                moisture_modifier=-0.2,
                color_map={'building': '#8C8C8C'},
                min_size=0.03,
                max_size=0.08
            ),
            'fields': TerrainFeature(
                name="Agricultural Fields",
                height_modifier=0.0,
                moisture_modifier=0.2,
                color_map={'crops': '#7D944D'},
                min_size=0.05,
                max_size=0.15
            )
        }

    def _initialize_seasonal_colors(self) -> Dict[Season, Dict[str, str]]:
        """Initialize color schemes for different seasons"""
        return {
            Season.SPRING: {
                'grassland': '#4CA64C',
                'forest': '#2D5A27',
                'fields': '#90B44B',
                'trees': '#4F7942'
            },
            Season.SUMMER: {
                'grassland': '#2D5A27',
                'forest': '#1A3B1A',
                'fields': '#7D944D',
                'trees': '#1A3B1A'
            },
            Season.AUTUMN: {
                'grassland': '#8B6B43',
                'forest': '#8B4513',
                'fields': '#DAA520',
                'trees': '#D2691E'
            },
            Season.WINTER: {
                'grassland': '#E8E8E8',
                'forest': '#4F666A',
                'fields': '#F5F5F5',
                'trees': '#2F4F4F'
            }
        }

    def generate_feature_mask(self, feature: TerrainFeature) -> np.ndarray:
        """Generate more natural-looking feature masks"""
        size = self.params.size
        mask = np.zeros((size, size))

        # Generate base noise for organic shapes
        base_noise = self.generate_noise((size, size), 4.0)

        # Generate feature regions using Voronoi with organic perturbation
        num_points = int(size * self.params.feature_density)
        points = np.random.rand(num_points, 2) * size
        vor = Voronoi(points)

        for region in vor.regions:
            if not -1 in region and len(region) > 0:
                if random.random() < 0.3:
                    polygon = [vor.vertices[i] for i in region]
                    img_coords = np.array(polygon) * size / vor.vertices.max()
                    img_coords = img_coords.astype(np.int32)

                    # Create organic mask
                    cv2.fillPoly(mask, [img_coords], 1)

        # Apply noise-based organic shaping
        mask *= (base_noise > 0.3).astype(float)

        # Smooth edges
        mask = gaussian_filter(mask, sigma=2.0)

        return mask


    def generate_road_network(self) -> np.ndarray:
        """Generate a more realistic road network"""
        size = self.params.size
        mask = np.zeros((size, size))

        # Generate major settlement locations
        num_settlements = int(size * self.params.feature_density * 0.3)  # Reduced number
        settlements = np.random.rand(num_settlements, 2) * size

        # Generate main roads connecting major settlements
        for i in range(len(settlements)):
            for j in range(i + 1, len(settlements)):
                if random.random() < 0.4:  # Reduced connectivity
                    pt1 = settlements[i].astype(int)
                    pt2 = settlements[j].astype(int)
                    # Add some curvature to roads
                    num_points = 5
                    for k in range(num_points):
                        t = k / (num_points - 1)
                        # Add random offset to make roads curved
                        offset = np.random.normal(0, size * 0.05, 2)
                        mid_point = (pt1 * (1-t) + pt2 * t + offset).astype(int)
                        if k > 0:
                            cv2.line(mask, tuple(prev_point), tuple(mid_point), 1, thickness=2)
                        prev_point = mid_point

        # Add noise to road edges and smooth
        mask = gaussian_filter(mask, sigma=1.0)
        return mask

    def apply_seasonal_effects(self, height_map: np.ndarray,
                             moisture_map: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Apply seasonal modifications to the landscape"""
        season = self.params.season

        if season == Season.WINTER:
            # Increase snow coverage
            self.params.snow_level *= 0.8
            moisture_map *= 0.7

        elif season == Season.SUMMER:
            # Decrease moisture in some areas
            moisture_map *= 0.9
            height_map *= 1.05

        elif season == Season.SPRING:
            # Increase moisture
            moisture_map *= 1.2
            height_map *= 0.95

        elif season == Season.AUTUMN:
            # Moderate conditions
            moisture_map *= 0.85
            height_map *= 1.0

        return height_map, moisture_map

    def generate_enhanced_landscape(self) -> None:
        """Generate landscape with multiple features and seasonal effects"""
        size = self.params.size

        # Generate base terrain
        height_map = self.generate_fractal_noise()
        moisture_map = self.generate_fractal_noise()

        # Apply seasonal effects
        height_map, moisture_map = self.apply_seasonal_effects(height_map, moisture_map)

        # Generate and apply feature masks
        feature_masks = {}
        for feature_name, feature in self.features.items():
            if feature_name == 'road_network':
                feature_masks[feature_name] = self.generate_road_network()
            else:
                feature_masks[feature_name] = self.generate_feature_mask(feature)

            # Apply feature effects to height and moisture maps
            height_map += feature_masks[feature_name] * feature.height_modifier
            moisture_map += feature_masks[feature_name] * feature.moisture_modifier

        # Normalize maps
        height_map = (height_map - height_map.min()) / (height_map.max() - height_map.min())
        moisture_map = np.clip(moisture_map, 0, 1)

        # Generate colored visualization
        color_map = self.generate_color_map(height_map, moisture_map, feature_masks)

        # Create visualizations
        self.create_visualizations(height_map, moisture_map, color_map, feature_masks)

    def generate_color_map(self, height_map: np.ndarray,
                          moisture_map: np.ndarray,
                          feature_masks: Dict[str, np.ndarray]) -> np.ndarray:
        """Generate colored visualization with features and seasonal effects"""
        color_map = np.zeros((*height_map.shape, 3))
        seasonal_colors = self.seasonal_colors[self.params.season]

        # Apply base terrain colors
        for i in range(height_map.shape[0]):
            for j in range(height_map.shape[1]):
                height = height_map[i, j]
                moisture = moisture_map[i, j]

                # Apply seasonal and feature-specific coloring
                base_color = self.get_terrain_color(height, moisture, seasonal_colors)
                color_map[i, j] = base_color

        # Apply feature colors
        for feature_name, mask in feature_masks.items():
            feature = self.features[feature_name]
            for color_name, color_hex in feature.color_map.items():
                rgb_color = self._hex_to_rgb(color_hex)
                color_map = np.where(mask[:, :, np.newaxis] > 0.5,
                                   rgb_color,
                                   color_map)

        return color_map

    def create_visualizations(self, height_map: np.ndarray,
                            moisture_map: np.ndarray,
                            color_map: np.ndarray,
                            feature_masks: Dict[str, np.ndarray]) -> None:
        """Create multiple visualization views of the landscape"""
        # 3D Surface plot
        fig = plt.figure(figsize=(15, 10))
        ax = fig.add_subplot(111, projection='3d')

        x = np.linspace(0, 1, self.params.size)
        y = np.linspace(0, 1, self.params.size)
        X, Y = np.meshgrid(x, y)

        surf = ax.plot_surface(X, Y, height_map, facecolors=color_map, shade=False)
        ax.set_title(f'Procedural Landscape ({self.params.season.value})')

        plt.savefig('enhanced_landscape_3d.png', dpi=300, bbox_inches='tight')
        plt.close()

        # 2D analysis views
        fig, axes = plt.subplots(2, 2, figsize=(15, 15))

        # Height map
        axes[0, 0].imshow(height_map, cmap='terrain')
        axes[0, 0].set_title('Height Map')

        # Moisture map
        axes[0, 1].imshow(moisture_map, cmap='YlGnBu')
        axes[0, 1].set_title('Moisture Map')

        # Feature visualization
        feature_vis = np.zeros((*height_map.shape, 3))
        for feature_name, mask in feature_masks.items():
            color = np.random.rand(3)
            feature_vis += mask[:, :, np.newaxis] * color
        axes[1, 0].imshow(feature_vis)
        axes[1, 0].set_title('Feature Map')

        # Final colored terrain
        axes[1, 1].imshow(color_map)
        axes[1, 1].set_title('Colored Terrain')

        plt.tight_layout()
        plt.savefig('enhanced_landscape_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()

if __name__ == "__main__":
    # Create generator with enhanced parameters
    params = EnhancedTerrainParams(
        size=512,
        season=Season.AUTUMN,  # Try different seasons
        feature_density=0.1
    )

    generator = EnhancedLandscapeGenerator(params, seed=42)
    generator.generate_enhanced_landscape()
