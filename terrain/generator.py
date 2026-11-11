"""
Noise generation and fractal terrain building.

Uses multiple rotated sine waves to approximate Perlin-like noise,
then combines octaves for fractal detail.
"""

from typing import Optional, Tuple

import numpy as np
from scipy.ndimage import gaussian_filter

from .params import EnhancedTerrainParams


class TerrainGenerator:
    """Generates height maps and moisture maps via fractal noise."""

    def __init__(
        self,
        params: Optional[EnhancedTerrainParams] = None,
        seed: Optional[int] = None,
    ) -> None:
        self.params = params or EnhancedTerrainParams()
        self._rng = np.random.default_rng(seed)

    @property
    def rng(self) -> np.random.Generator:
        """The seeded generator shared by the noise and the feature placement."""
        return self._rng

    # ── noise primitives ─────────────────────────────────────────────────

    def generate_noise(
        self, shape: Tuple[int, int], frequency: float
    ) -> np.ndarray:
        """Generate improved Perlin-like noise with multiple frequencies."""
        noise = np.zeros(shape)
        x = np.linspace(0, frequency, shape[0])
        y = np.linspace(0, frequency, shape[1])
        X, Y = np.meshgrid(x, y)

        for i in range(6):
            angle = self._rng.uniform(0, 2 * np.pi)
            phase = self._rng.uniform(0, 2 * np.pi)
            freq_mul = 2 ** i

            X_rot = X * np.cos(angle) - Y * np.sin(angle)
            Y_rot = X * np.sin(angle) + Y * np.cos(angle)

            noise += np.sin(X_rot * freq_mul + phase) * np.cos(
                Y_rot * freq_mul + phase
            )
            noise += self._rng.normal(0, 0.1, shape) * (0.5**i)

        return (noise - noise.min()) / (noise.max() - noise.min())

    def generate_fractal_noise(self) -> np.ndarray:
        """Generate fractal noise using multiple octaves."""
        size = self.params.size
        noise = np.zeros((size, size))
        frequency = self.params.base_frequency
        amplitude = 1.0

        for _ in range(self.params.octaves):
            noise += amplitude * self.generate_noise((size, size), frequency)
            frequency *= self.params.lacunarity
            amplitude *= self.params.persistence

        noise = (noise - noise.min()) / (noise.max() - noise.min())
        noise = gaussian_filter(noise, sigma=1.0)
        return noise
