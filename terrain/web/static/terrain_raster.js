// Port of terrain/raster.py: the polygon fill and thick line used for feature masks, with the same
// arithmetic in the same order, so the pixels match the Python exactly. mask[y * n + x], centre (x, y).

export function fillPolygon(mask, n, pts, value = 1) {
  const m = pts.length;
  if (m < 3) return;
  let ymin = Infinity, ymax = -Infinity;
  for (const p of pts) { ymin = Math.min(ymin, p[1]); ymax = Math.max(ymax, p[1]); }
  const yLo = Math.max(0, Math.ceil(ymin)), yHi = Math.min(n - 1, Math.floor(ymax));
  const xs = [];
  for (let y = yLo; y <= yHi; y++) {
    xs.length = 0;
    for (let i = 0; i < m; i++) {
      const [x0, y0] = pts[i], [x1, y1] = pts[(i + 1) % m];
      if ((y0 <= y && y < y1) || (y1 <= y && y < y0)) xs.push(x0 + (y - y0) * (x1 - x0) / (y1 - y0));
    }
    xs.sort((a, b) => a - b);
    for (let k = 0; k + 1 < xs.length; k += 2) {
      const a = Math.max(0, Math.ceil(xs[k])), b = Math.min(n - 1, Math.ceil(xs[k + 1]) - 1);
      for (let x = a; x <= b; x++) mask[y * n + x] = value;
    }
  }
}

export function drawLine(mask, n, p0, p1, value = 1, thickness = 2) {
  const [x0, y0] = p0, [x1, y1] = p1;
  const r = thickness / 2;
  const xa = Math.max(0, Math.floor(Math.min(x0, x1) - r)), xb = Math.min(n - 1, Math.ceil(Math.max(x0, x1) + r));
  const ya = Math.max(0, Math.floor(Math.min(y0, y1) - r)), yb = Math.min(n - 1, Math.ceil(Math.max(y0, y1) + r));
  if (xb < xa || yb < ya) return;
  const dx = x1 - x0, dy = y1 - y0, len2 = dx * dx + dy * dy;
  for (let py = ya; py <= yb; py++) {
    for (let px = xa; px <= xb; px++) {
      let t = 0;
      if (len2 > 0) t = Math.min(1, Math.max(0, ((px - x0) * dx + (py - y0) * dy) / len2));
      const ex = px - (x0 + t * dx), ey = py - (y0 + t * dy);
      if (ex * ex + ey * ey <= r * r) mask[py * n + px] = value;
    }
  }
}
