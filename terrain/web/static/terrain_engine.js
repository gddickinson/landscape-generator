// Port of terrain/pipeline.py generate_landscape(params, seed): fractal height and moisture, season,
// feature masks, normalisation and the colour map. Pure functions: runs in node, a Web Worker or the page.
import { Generator } from './np_random.js';
import { generateFractalNoise } from './terrain_noise.js';
import { FEATURES, featureMask, roadNetwork, seasonalEffects } from './terrain_features.js';
import { colorMap } from './terrain_biomes.js';
import { normalize } from './ndimage.js';

// EnhancedTerrainParams defaults (checked against the Python by the node test).
export const DEFAULTS = {
  size: 512, octaves: 6, persistence: 0.5, lacunarity: 2.0, base_frequency: 4.0,
  sea_level: 0.35, mountain_level: 0.7, snow_level: 0.85, season: 'summer', feature_density: 0.1,
};

export function generateLandscape(params, seed, onProgress = () => {}) {
  const p = { ...DEFAULTS, ...params };
  const n = p.size;
  const rng = new Generator(seed);
  const steps = 2 + FEATURES.length + 1;
  let done = 0;
  const tick = label => onProgress(++done / steps, label);

  let height = generateFractalNoise(rng, p); tick('height');
  const baseHeight = height.slice();
  let moisture = generateFractalNoise(rng, p); tick('moisture');
  let snowLevel;
  [height, moisture, snowLevel] = seasonalEffects(height, moisture, p);
  height = Float64Array.from(height); moisture = Float64Array.from(moisture);

  const masks = {};
  for (const f of FEATURES) {
    const m = f.key === 'road_network' ? roadNetwork(rng, p) : featureMask(rng, p);
    masks[f.key] = m;
    for (let k = 0; k < n * n; k++) {
      height[k] = height[k] + m[k] * f.height_modifier;
      moisture[k] = moisture[k] + m[k] * f.moisture_modifier;
    }
    tick(f.key);
  }
  normalize(height);
  for (let k = 0; k < n * n; k++) moisture[k] = Math.min(1, Math.max(0, moisture[k]));
  const color = colorMap(height, moisture, masks, FEATURES, p, snowLevel); tick('colour');
  return { params: p, seed, size: n, snowLevel, baseHeight, height, moisture, masks, color };
}
