// Canvas views of a generated landscape: the coloured terrain, the height and moisture maps (with the
// matplotlib colormaps of the Python analysis figure), the feature masks, a hill-shaded relief, an oblique
// 3-D view and the four-panel analysis layout of TerrainVisualizer.plot_analysis.
import { FEATURES } from './terrain_features.js';
import { hexToRgb } from './terrain_biomes.js';
import { minMax } from './ndimage.js';

export const VIEWS = [
  ['terrain', 'Coloured terrain'], ['relief', 'Shaded relief'], ['3d', '3-D view'], ['height', 'Height map'],
  ['moisture', 'Moisture map'], ['features', 'Feature map'], ['analysis', 'Analysis (2 x 2)'],
];

// Fixed, distinct colours for the feature-map view (the Python figure picks random colours each run).
export const FEATURE_VIEW_COLORS = {
  lake: '#3d8bff', mountain_range: '#b0b0b0', forest: '#2fbf4f', desert: '#ffc145',
  road_network: '#ff4f6d', settlement: '#c77dff', fields: '#9be15d',
};

function lutBytes(hexes) { return hexes.map(hexToRgb); }

// RGBA bytes for a scalar map through a 256-entry LUT, scaled to the map's own min-max (as imshow does).
function scalarRGBA(a, lut) {
  const [lo, hi] = minMax(a), d = hi - lo || 1, out = new Uint8ClampedArray(a.length * 4);
  for (let k = 0; k < a.length; k++) {
    const c = lut[Math.min(255, Math.max(0, Math.round((a[k] - lo) / d * 255)))];
    out[4 * k] = c[0]; out[4 * k + 1] = c[1]; out[4 * k + 2] = c[2]; out[4 * k + 3] = 255;
  }
  return out;
}

function featureRGBA(L) {
  const n2 = L.height.length, acc = new Float64Array(n2 * 3);
  for (const f of FEATURES) {
    const m = L.masks[f.key], c = hexToRgb(FEATURE_VIEW_COLORS[f.key]);
    for (let k = 0; k < n2; k++) if (m[k] > 0) for (let j = 0; j < 3; j++) acc[3 * k + j] += m[k] * c[j];
  }
  const out = new Uint8ClampedArray(n2 * 4);
  for (let k = 0; k < n2; k++) { for (let j = 0; j < 3; j++) out[4 * k + j] = acc[3 * k + j]; out[4 * k + 3] = 255; }
  return out;
}

// Lambert shading from the height gradient, light from the north-west; 1 = flat.
export function hillshade(h, n, z = 3) {
  const out = new Float64Array(n * n);
  const lx = -0.5, ly = -0.5, lz = 0.7071; // normalised (-1, -1, 1.414) / 2
  for (let r = 0; r < n; r++) {
    for (let c = 0; c < n; c++) {
      const xl = h[r * n + Math.max(0, c - 1)], xr = h[r * n + Math.min(n - 1, c + 1)];
      const yu = h[Math.max(0, r - 1) * n + c], yd = h[Math.min(n - 1, r + 1) * n + c];
      const dx = (xr - xl) * z * n / 128, dy = (yd - yu) * z * n / 128;
      const len = Math.hypot(dx, dy, 1);
      const s = (-dx * lx - dy * ly + lz) / len;
      out[r * n + c] = Math.max(0, s) / lz;
    }
  }
  return out;
}

function reliefRGBA(L) {
  const n = L.size, sh = hillshade(L.height, n), out = new Uint8ClampedArray(L.color);
  for (let k = 0; k < n * n; k++) {
    const f = 0.35 + 0.65 * Math.min(1.4, sh[k]);
    for (let j = 0; j < 3; j++) out[4 * k + j] = L.color[4 * k + j] * f;
  }
  return out;
}

function putRGBA(canvas, rgba, n) {
  canvas.width = n; canvas.height = n;
  canvas.getContext('2d').putImageData(new ImageData(rgba, n, n), 0, 0);
}

// Oblique 3-D view: each grid row drawn front to back with a per-column horizon buffer.
export function draw3d(canvas, L, exag = 0.2) {
  const n = L.size, k = Math.max(1, Math.round(640 / n)), W = n * k, depth = 0.5 * W, lift = exag * W;
  const H = Math.ceil(depth + lift + 8);
  canvas.width = W; canvas.height = H;
  const img = new ImageData(W, H), px = img.data, ybuf = new Float64Array(W).fill(H);
  const sh = hillshade(L.height, n);
  const top = lift + 4;
  for (let r = n - 1; r >= 0; r--) {
    const base = top + (r / n) * depth;
    for (let c = 0; c < n; c++) {
      const i = r * n + c, y = Math.round(base - L.height[i] * lift);
      const f = 0.35 + 0.65 * Math.min(1.4, sh[i]);
      const cr = L.color[4 * i] * f, cg = L.color[4 * i + 1] * f, cb = L.color[4 * i + 2] * f;
      for (let x = c * k; x < c * k + k; x++) {
        for (let yy = Math.max(0, y); yy < ybuf[x]; yy++) {
          const o = 4 * (yy * W + x), wall = yy > base + 1 ? 0.5 : 1; // darker below the ground line (front wall)
          px[o] = cr * wall; px[o + 1] = cg * wall; px[o + 2] = cb * wall; px[o + 3] = 255;
        }
        if (y < ybuf[x]) ybuf[x] = Math.max(0, y);
      }
    }
  }
  canvas.getContext('2d').putImageData(img, 0, 0);
}

// RGBA bytes of a 2-D view (everything except '3d' and 'analysis').
export function viewRGBA(L, view, luts) {
  switch (view) {
    case 'terrain': return new Uint8ClampedArray(L.color);
    case 'relief': return reliefRGBA(L);
    case 'height': return scalarRGBA(L.height, lutBytes(luts.terrain));
    case 'moisture': return scalarRGBA(L.moisture, lutBytes(luts.YlGnBu));
    case 'features': return featureRGBA(L);
    default: throw new Error('unknown view ' + view);
  }
}

function drawAnalysis(canvas, L, luts) {
  const n = L.size, s = Math.max(n, 256), gap = 30, W = 2 * s + gap, H = 2 * (s + gap);
  canvas.width = W; canvas.height = H;
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#0b0f1d'; ctx.fillRect(0, 0, W, H);
  const tmp = document.createElement('canvas');
  const panels = [['height', 'Height Map'], ['moisture', 'Moisture Map'], ['features', 'Feature Map'], ['terrain', 'Colored Terrain']];
  panels.forEach(([v, title], i) => {
    putRGBA(tmp, viewRGBA(L, v, luts), n);
    const x = (i % 2) * (s + gap), y = Math.floor(i / 2) * (s + gap) + gap;
    ctx.imageSmoothingEnabled = n < s ? false : true;
    ctx.drawImage(tmp, x, y, s, s);
    ctx.fillStyle = '#e8f1ff'; ctx.font = '600 15px -apple-system, Helvetica, sans-serif'; ctx.textAlign = 'center';
    ctx.fillText(title, x + s / 2, y - 9);
  });
}

// Draw any view into canvas. opts: { exag } for the 3-D view.
export function paint(canvas, L, view, luts, opts = {}) {
  if (view === '3d') return draw3d(canvas, L, opts.exag ?? 0.2);
  if (view === 'analysis') return drawAnalysis(canvas, L, luts);
  putRGBA(canvas, viewRGBA(L, view, luts), L.size);
}
