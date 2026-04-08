import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.ndimage import gaussian_filter
import colorsys
from dataclasses import dataclass
from typing import Tuple, List, Optional
import random

@dataclass
class TerrainParams:
    size: int = 256
    octaves: int = 6
    persistence: float = 0.5
    lacunarity: float = 2.0
    base_frequency: float = 4.0
    sea_level: float = 0.4
    mountain_level: float = 0.7
    snow_level: float = 0.85

class LandscapeGenerator:
    def __init__(self, params: TerrainParams = None, seed: Optional[int] = None):
        self.params = params or TerrainParams()
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)
        
        # Initialize color mappings
        self.biome_colors = {
            'deep_water': '#001933',
            'water': '#003366',
            'beach': '#D9B382',
            'grassland': '#2D5A27',
            'forest': '#1A3B1A',
            'mountain': '#6F6F6F',
            'snow': '#FFFFFF'
        }
    
    def generate_noise(self, shape: Tuple[int, int], frequency: float) -> np.ndarray:
        """Generate Perlin-like noise"""
        noise = np.zeros(shape)
        x = np.linspace(0, frequency, shape[0])
        y = np.linspace(0, frequency, shape[1])
        X, Y = np.meshgrid(x, y)
        
        # Generate multiple waves of different frequencies
        for i in range(4):
            phase_x = random.uniform(0, 2 * np.pi)
            phase_y = random.uniform(0, 2 * np.pi)
            freq_mul = 2 ** i
            
            noise += np.sin(X * freq_mul + phase_x) * np.cos(Y * freq_mul + phase_y)
        
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
    
    def get_biome_color(self, height: float, moisture: float) -> Tuple[float, float, float]:
        """Determine terrain color based on height and moisture"""
        if height < self.params.sea_level:
            depth = height / self.params.sea_level
            return self._hex_to_rgb(self.biome_colors['deep_water' if depth < 0.5 else 'water'])
        
        elif height < self.params.sea_level + 0.05:
            return self._hex_to_rgb(self.biome_colors['beach'])
        
        elif height < self.params.mountain_level:
            if moisture > 0.6:
                return self._hex_to_rgb(self.biome_colors['forest'])
            else:
                return self._hex_to_rgb(self.biome_colors['grassland'])
        
        elif height < self.params.snow_level:
            return self._hex_to_rgb(self.biome_colors['mountain'])
        
        else:
            return self._hex_to_rgb(self.biome_colors['snow'])
    
    @staticmethod
    def _hex_to_rgb(hex_color: str) -> Tuple[float, float, float]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4))
    
    def apply_lighting(self, terrain: np.ndarray, 
                      sun_angle: float = 45.0) -> np.ndarray:
        """Apply simple directional lighting to the terrain"""
        gradient_y, gradient_x = np.gradient(terrain)
        
        # Convert sun angle to radians
        angle_rad = np.radians(sun_angle)
        
        # Calculate lighting based on surface normal and sun direction
        sun_dir = np.array([np.cos(angle_rad), np.sin(angle_rad), 1])
        sun_dir = sun_dir / np.linalg.norm(sun_dir)
        
        # Calculate surface normals
        normals = np.dstack((-gradient_x, -gradient_y, np.ones_like(terrain)))
        norm = np.linalg.norm(normals, axis=2)
        normals /= norm[:, :, np.newaxis]
        
        # Calculate lighting
        lighting = np.dot(normals, sun_dir)
        lighting = np.clip(lighting, 0.2, 1.0)  # Ambient light
        
        return lighting
    
    def generate_landscape(self, render_3d: bool = True) -> None:
        """Generate and visualize a complete landscape"""
        # Generate height map
        print("Generating terrain height map...")
        height_map = self.generate_fractal_noise()
        
        # Generate moisture map
        print("Generating moisture map...")
        moisture_map = self.generate_fractal_noise()
        moisture_map = gaussian_filter(moisture_map, sigma=2.0)
        
        # Apply lighting
        print("Calculating lighting...")
        lighting = self.apply_lighting(height_map)
        
        # Create color map
        print("Generating color map...")
        color_map = np.zeros((self.params.size, self.params.size, 3))
        for i in range(self.params.size):
            for j in range(self.params.size):
                base_color = self.get_biome_color(height_map[i, j], moisture_map[i, j])
                color_map[i, j] = np.array(base_color) * lighting[i, j]
        
        # Create visualizations
        print("Creating visualizations...")
        
        if render_3d:
            # 3D Surface plot
            fig = plt.figure(figsize=(15, 10))
            ax = fig.add_subplot(111, projection='3d')
            
            x = np.linspace(0, 1, self.params.size)
            y = np.linspace(0, 1, self.params.size)
            X, Y = np.meshgrid(x, y)
            
            surf = ax.plot_surface(
                X, Y, height_map,
                facecolors=color_map,
                shade=False
            )
            
            ax.set_title('Procedural Landscape')
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Height')
            
            plt.savefig('landscape_3d.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # 2D visualization with multiple aspects
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 15))
        
        # Height map
        im1 = ax1.imshow(height_map, cmap='terrain')
        ax1.set_title('Height Map')
        plt.colorbar(im1, ax=ax1)
        
        # Moisture map
        im2 = ax2.imshow(moisture_map, cmap='YlGnBu')
        ax2.set_title('Moisture Map')
        plt.colorbar(im2, ax=ax2)
        
        # Lighting map
        im3 = ax3.imshow(lighting, cmap='gray')
        ax3.set_title('Lighting Map')
        plt.colorbar(im3, ax=ax3)
        
        # Final colored terrain
        ax4.imshow(color_map)
        ax4.set_title('Colored Terrain')
        
        plt.tight_layout()
        plt.savefig('landscape_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Landscape generation complete!")
        print("Check 'landscape_3d.png' and 'landscape_analysis.png' for results.")

if __name__ == "__main__":
    # Create generator with custom parameters
    params = TerrainParams(
        size=256,
        octaves=6,
        persistence=0.5,
        lacunarity=2.0,
        base_frequency=4.0,
        sea_level=0.4,
        mountain_level=0.7,
        snow_level=0.85
    )
    
    generator = LandscapeGenerator(params, seed=42)
    generator.generate_landscape()