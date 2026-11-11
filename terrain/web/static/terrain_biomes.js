// Port of terrain/biomes.py (SEASONAL_COLORS, BiomeColorMapper.get_terrain_color) and
// TerrainVisualizer.generate_color_map: biome colour by height and moisture, then feature colours
// painted over where a feature mask is above 0.5 (in catalogue order).
export const SEASONAL_COLORS = {
  spring: { grassland: '#4CA64C', forest: '#2D5A27', fields: '#90B44B', trees: '#4F7942' },
  summer: { grassland: '#2D5A27', forest: '#1A3B1A', fields: '#7D944D', trees: '#1A3B1A' },
  fall: { grassland: '#8B6B43', forest: '#8B4513', fields: '#DAA520', trees: '#D2691E' },
  winter: { grassland: '#E8E8E8', forest: '#4F666A', fields: '#F5F5F5', trees: '#2F4F4F' },
};
export const BIOME_COLORS = { deep: '#001933', shallow: '#003366', beach: '#D9B382', rock: '#6F6F6F', snow: '#FFFFFF' };

export const hexToRgb = h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16));

export function terrainColor(h, m, p, snowLevel, pal) {
  if (h < p.sea_level) return h / p.sea_level < 0.5 ? BIOME_COLORS.deep : BIOME_COLORS.shallow;
  if (h < p.sea_level + 0.05) return BIOME_COLORS.beach;
  if (h < p.mountain_level) return m > 0.6 ? pal.forest : pal.grassland;
  if (h < snowLevel) return BIOME_COLORS.rock;
  return BIOME_COLORS.snow;
}

// RGBA bytes (n * n * 4) of the coloured terrain.
export function colorMap(height, moisture, masks, features, p, snowLevel) {
  const n2 = height.length, out = new Uint8ClampedArray(n2 * 4);
  const pal = SEASONAL_COLORS[p.season], cache = {};
  const rgb = hx => cache[hx] || (cache[hx] = hexToRgb(hx));
  for (let k = 0; k < n2; k++) {
    const c = rgb(terrainColor(height[k], moisture[k], p, snowLevel, pal));
    out[4 * k] = c[0]; out[4 * k + 1] = c[1]; out[4 * k + 2] = c[2]; out[4 * k + 3] = 255;
  }
  for (const f of features) {
    const mask = masks[f.key];
    for (const hx of Object.values(f.color_map)) {
      const c = rgb(hx);
      for (let k = 0; k < n2; k++) if (mask[k] > 0.5) { out[4 * k] = c[0]; out[4 * k + 1] = c[1]; out[4 * k + 2] = c[2]; }
    }
  }
  return out;
}
