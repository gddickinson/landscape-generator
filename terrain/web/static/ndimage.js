// NumPy / SciPy helpers used by the terrain port, written to follow the same arithmetic as the Python
// (np.linspace, numpy's pairwise sum, scipy.ndimage.gaussian_filter with mode='reflect', truncate=4).
// Arrays are square size x size Float64Arrays in row-major (C) order, like the NumPy maps.

export function linspace(start, stop, num) {
  const out = new Float64Array(num);
  const step = (stop - start) / (num - 1);
  for (let i = 0; i < num; i++) out[i] = i * step + start;
  if (num > 1) out[num - 1] = stop;
  return out;
}

// numpy's pairwise summation for arrays of up to 128 elements (enough for the kernels here).
export function pairwiseSum(a) {
  const n = a.length;
  if (n < 8) { let s = 0; for (let i = 0; i < n; i++) s += a[i]; return s; }
  if (n > 128) throw new Error('pairwiseSum: n > 128 not needed');
  const r = Array.from(a.slice(0, 8));
  let i = 8;
  for (; i < n - (n % 8); i += 8) for (let j = 0; j < 8; j++) r[j] += a[i + j];
  let res = ((r[0] + r[1]) + (r[2] + r[3])) + ((r[4] + r[5]) + (r[6] + r[7]));
  for (; i < n; i++) res += a[i];
  return res;
}

// scipy.ndimage._filters._gaussian_kernel1d(sigma, 0, radius)
export function gaussianKernel(sigma, truncate = 4.0) {
  const radius = Math.trunc(truncate * sigma + 0.5);
  const sigma2 = sigma * sigma;
  const phi = new Float64Array(2 * radius + 1);
  for (let k = -radius; k <= radius; k++) phi[k + radius] = Math.exp(-0.5 / sigma2 * (k * k));
  const sum = pairwiseSum(phi);
  for (let k = 0; k < phi.length; k++) phi[k] = phi[k] / sum;
  return phi;
}

const reflect = (i, n) => {
  const p = 2 * n;
  i = ((i % p) + p) % p;
  return i < n ? i : p - 1 - i;
};

// One symmetric 1-D correlation pass along rows (axis 1) or columns (axis 0), as scipy's NI_Correlate1D.
function correlate1d(src, n, w, axis) {
  const r = (w.length - 1) / 2;
  const out = new Float64Array(n * n);
  const line = new Float64Array(n + 2 * r);
  for (let a = 0; a < n; a++) {
    for (let k = -r; k < n + r; k++) {
      const b = reflect(k, n);
      line[k + r] = axis === 1 ? src[a * n + b] : src[b * n + a];
    }
    for (let k = 0; k < n; k++) {
      const c = k + r;
      let v = line[c] * w[r];
      for (let j = -r; j < 0; j++) v += (line[c + j] + line[c - j]) * w[r + j];
      if (axis === 1) out[a * n + k] = v; else out[k * n + a] = v;
    }
  }
  return out;
}

export function gaussianFilter(src, n, sigma) {
  const w = gaussianKernel(sigma);
  return correlate1d(correlate1d(src, n, w, 0), n, w, 1);
}

export function minMax(a) {
  let lo = Infinity, hi = -Infinity;
  for (let i = 0; i < a.length; i++) { const v = a[i]; if (v < lo) lo = v; if (v > hi) hi = v; }
  return [lo, hi];
}

// (a - a.min()) / (a.max() - a.min()), in place
export function normalize(a) {
  const [lo, hi] = minMax(a);
  const d = hi - lo;
  for (let i = 0; i < a.length; i++) a[i] = (a[i] - lo) / d;
  return a;
}
