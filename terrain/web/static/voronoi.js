// Bounded Voronoi cells of 2-D points, in input-point order (as terrain/features.py visits
// scipy.spatial.Voronoi regions via point_region). A cell is unbounded exactly when its point is a
// vertex of the convex hull; bounded cells are built by clipping a large square with the
// perpendicular bisectors to every other point (Sutherland-Hodgman).

function cross(o, a, b) { return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]); }

// Indices of the convex-hull vertices (Andrew's monotone chain; collinear points excluded).
export function hullIndices(points) {
  const idx = points.map((_, i) => i).sort((a, b) => points[a][0] - points[b][0] || points[a][1] - points[b][1]);
  const half = order => {
    const h = [];
    for (const i of order) {
      while (h.length >= 2 && cross(points[h[h.length - 2]], points[h[h.length - 1]], points[i]) <= 0) h.pop();
      h.push(i);
    }
    h.pop();
    return h;
  };
  return new Set([...half(idx), ...half(idx.slice().reverse())]);
}

function clip(poly, p, q) { // keep the half-plane closer to p than to q
  const nx = q[0] - p[0], ny = q[1] - p[1];
  const c = (q[0] * q[0] + q[1] * q[1] - p[0] * p[0] - p[1] * p[1]) / 2;
  const f = v => v[0] * nx + v[1] * ny - c; // <= 0 inside
  const out = [];
  for (let i = 0; i < poly.length; i++) {
    const a = poly[i], b = poly[(i + 1) % poly.length];
    const fa = f(a), fb = f(b);
    if (fa <= 0) out.push(a);
    if ((fa < 0 && fb > 0) || (fa > 0 && fb < 0)) {
      const t = fa / (fa - fb);
      out.push([a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])]);
    }
  }
  return out;
}

// For each point: null if its cell is unbounded, else the cell polygon [[x, y], ...].
export function voronoiCells(points) {
  const hull = hullIndices(points);
  const B = 1e9;
  return points.map((p, i) => {
    if (hull.has(i)) return null;
    let poly = [[-B, -B], [B, -B], [B, B], [-B, B]];
    for (let j = 0; j < points.length && poly.length; j++) if (j !== i) poly = clip(poly, p, points[j]);
    return poly;
  });
}
