// Port of terrain/features.py: the feature catalogue, Voronoi + noise feature masks, the road network
// and the seasonal effects. Same random draws in the same order as the Python (one shared Generator).
import { generateNoise } from './terrain_noise.js';
import { gaussianFilter } from './ndimage.js';
import { voronoiCells } from './voronoi.js';
import { fillPolygon, drawLine } from './terrain_raster.js';

// DEFAULT_FEATURES (insertion order matters: masks are applied and coloured in this order).
export const FEATURES = [
  { key: 'lake', name: 'Lake', height_modifier: -0.3, moisture_modifier: 0.8, color_map: { water: '#005C99' } },
  { key: 'mountain_range', name: 'Mountain Range', height_modifier: 0.4, moisture_modifier: 0.3, color_map: { rock: '#6F6F6F', snow: '#FFFFFF' } },
  { key: 'forest', name: 'Forest', height_modifier: 0.1, moisture_modifier: 0.6, color_map: { trees: '#1A3B1A' } },
  { key: 'desert', name: 'Desert', height_modifier: 0.1, moisture_modifier: -0.4, color_map: { sand: '#D9B382' } },
  { key: 'road_network', name: 'Road Network', height_modifier: 0.0, moisture_modifier: -0.1, color_map: { road: '#5C5C5C' } },
  { key: 'settlement', name: 'Settlement', height_modifier: 0.05, moisture_modifier: -0.2, color_map: { building: '#8C8C8C' } },
  { key: 'fields', name: 'Agricultural Fields', height_modifier: 0.0, moisture_modifier: 0.2, color_map: { crops: '#7D944D' } },
];

export function featureMask(rng, p) {
  const n = p.size;
  let mask = new Float64Array(n * n);
  const base = generateNoise(rng, n, 4.0);
  const numPoints = Math.max(4, Math.trunc(n * p.feature_density));
  const pts = [];
  for (let i = 0; i < numPoints; i++) { const x = rng.random() * n, y = rng.random() * n; pts.push([x, y]); }
  const cells = voronoiCells(pts);
  for (const cell of cells) {
    if (!cell || !cell.length) continue;
    if (rng.random() < 0.3) fillPolygon(mask, n, cell, 1);
  }
  for (let k = 0; k < n * n; k++) mask[k] *= base[k] > 0.3 ? 1 : 0;
  return gaussianFilter(mask, n, 2.0);
}

export function roadNetwork(rng, p) {
  const n = p.size;
  const mask = new Float64Array(n * n);
  const num = Math.max(2, Math.trunc(n * p.feature_density * 0.3));
  const s = [];
  for (let i = 0; i < num; i++) { const x = rng.random() * n, y = rng.random() * n; s.push([x, y]); }
  for (let i = 0; i < num; i++) {
    for (let j = i + 1; j < num; j++) {
      if (!(rng.random() < 0.4)) continue;
      const a = s[i].map(Math.trunc), b = s[j].map(Math.trunc);
      let prev = null;
      for (let k = 0; k < 5; k++) {
        const t = k / 4;
        const ox = rng.normal(0, n * 0.05), oy = rng.normal(0, n * 0.05);
        const mid = [Math.trunc(a[0] * (1 - t) + b[0] * t + ox), Math.trunc(a[1] * (1 - t) + b[1] * t + oy)];
        if (prev) drawLine(mask, n, prev, mid, 1, 2);
        prev = mid;
      }
    }
  }
  return gaussianFilter(mask, n, 1.0);
}

// Returns [height, moisture, snow_level] for the season (FeatureGenerator.apply_seasonal_effects).
export function seasonalEffects(height, moisture, p) {
  const scale = (a, f) => a.map(v => v * f);
  switch (p.season) {
    case 'winter': return [height, scale(moisture, 0.7), p.snow_level * 0.8];
    case 'summer': return [scale(height, 1.05), scale(moisture, 0.9), p.snow_level];
    case 'spring': return [scale(height, 0.95), scale(moisture, 1.2), p.snow_level];
    case 'fall': return [height, scale(moisture, 0.85), p.snow_level];
    default: throw new Error('unknown season ' + p.season);
  }
}
