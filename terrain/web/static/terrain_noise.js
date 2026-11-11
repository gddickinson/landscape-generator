// Port of terrain/generator.py (TerrainGenerator.generate_noise / generate_fractal_noise): rotated,
// phase-shifted sine waves plus Gaussian jitter, summed over octaves and smoothed. Draws from the
// shared numpy-compatible Generator in the same order as the Python, so a seed gives the same maps.
import { linspace, gaussianFilter, normalize } from './ndimage.js';

const TWO_PI = 2 * Math.PI;

export function generateNoise(rng, n, frequency) {
  const noise = new Float64Array(n * n);
  const x = linspace(0, frequency, n), y = x; // shape is square: np.linspace(0, f, n) for both axes
  for (let i = 0; i < 6; i++) {
    const angle = rng.uniform(0, TWO_PI);
    const phase = rng.uniform(0, TWO_PI);
    const fm = 2 ** i;
    const ca = Math.cos(angle), sa = Math.sin(angle);
    for (let r = 0; r < n; r++) {
      const Y = y[r], row = r * n;
      for (let c = 0; c < n; c++) {
        const X = x[c];
        const xr = X * ca - Y * sa, yr = X * sa + Y * ca;
        noise[row + c] += Math.sin(xr * fm + phase) * Math.cos(yr * fm + phase);
      }
    }
    const w = 0.5 ** i;
    for (let k = 0; k < n * n; k++) noise[k] += (0 + 0.1 * rng.standardNormal()) * w;
  }
  return normalize(noise);
}

export function generateFractalNoise(rng, p) {
  const n = p.size;
  const noise = new Float64Array(n * n);
  let frequency = p.base_frequency, amplitude = 1.0;
  for (let o = 0; o < p.octaves; o++) {
    const layer = generateNoise(rng, n, frequency);
    for (let k = 0; k < n * n; k++) noise[k] += amplitude * layer[k];
    frequency *= p.lacunarity;
    amplitude *= p.persistence;
  }
  normalize(noise);
  return gaussianFilter(noise, n, 1.0);
}
