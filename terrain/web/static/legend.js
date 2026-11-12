// Legend for the coloured terrain: every biome and feature colour of the season, with the share of
// the map it covers in the current landscape.
import { esc, list } from './core.js';
import { SEASONAL_COLORS, BIOME_COLORS, SEASONAL_FEATURE_COLORS } from './terrain_biomes.js';
import { FEATURES } from './terrain_features.js';

// [name, hex] in painting order; later entries win when two share a colour.
export function legendEntries(season) {
  const pal = SEASONAL_COLORS[season];
  return [
    ['Deep water', BIOME_COLORS.deep], ['Shallow water', BIOME_COLORS.shallow], ['Beach', BIOME_COLORS.beach],
    ['Grassland', pal.grassland], ['Forest (moist)', pal.forest], ['Mountain rock', BIOME_COLORS.rock],
    ['Snow', BIOME_COLORS.snow],
    ...FEATURES.flatMap(f => Object.entries(f.color_map).map(([part, hx]) =>
      [`${f.name} (${part})`, SEASONAL_FEATURE_COLORS[part] ? pal[SEASONAL_FEATURE_COLORS[part]] : hx])),
  ];
}

export function coverage(L) {
  const counts = new Map(), c = L.color;
  for (let k = 0; k < c.length; k += 4) {
    const key = (c[k] << 16) | (c[k + 1] << 8) | c[k + 2];
    counts.set(key, (counts.get(key) || 0) + 1);
  }
  return hx => (counts.get(parseInt(hx.slice(1), 16)) || 0) / (c.length / 4);
}

export function legendHtml(L) {
  const share = coverage(L), seen = new Map();
  for (const [name, hx] of legendEntries(L.params.season)) {
    const k = hx.toUpperCase();
    seen.set(k, seen.has(k) ? seen.get(k) + ' / ' + name : name);
  }
  return `<ul class="legend">${list([...seen], ([hx, name]) => {
    const pct = share(hx) * 100;
    return `<li><span class="sw" style="background:${hx}"></span>${esc(name)} <b>${pct >= 0.05 ? pct.toFixed(1) + '%' : '-'}</b></li>`;
  })}</ul>`;
}
