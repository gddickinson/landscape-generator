// node terrain_engine.test.mjs: the JS terrain port against the Python package
// (tests/fixtures/terrain_reference.json, written by scripts/make_terrain_fixture.py).
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { Generator } from './np_random.js';
import { gaussianKernel } from './ndimage.js';
import { generateNoise } from './terrain_noise.js';
import { FEATURES } from './terrain_features.js';
import { generateLandscape, DEFAULTS } from './terrain_engine.js';

const F = JSON.parse(readFileSync(new URL('../../../tests/fixtures/terrain_reference.json', import.meta.url)));
const RTOL = 1e-9, ATOL = 1e-10;
const close = (a, b, what) => {
  let worst = 0;
  for (let i = 0; i < b.length; i++) {
    const d = Math.abs(a[i] - b[i]);
    worst = Math.max(worst, d);
    assert.ok(d <= ATOL + RTOL * Math.abs(b[i]), `${what}[${i}]: ${a[i]} vs ${b[i]}`);
  }
  return worst;
};

assert.deepEqual(DEFAULTS, F.defaults, 'EnhancedTerrainParams defaults');
assert.deepEqual(FEATURES.map(({ key, name, height_modifier, moisture_modifier, color_map }) =>
  ({ key, name, height_modifier, moisture_modifier, color_map })), F.features, 'DEFAULT_FEATURES');
for (const [s, k] of Object.entries(F.kernels)) close(gaussianKernel(+s), k, `kernel sigma ${s}`);
let worst = close(generateNoise(new Generator(3), 32, 4.0), F.noise_32_f4_seed3, 'generate_noise');

for (const c of F.cases) {
  const L = generateLandscape(c.params, c.seed);
  const n2 = L.size * L.size;
  assert.ok(Math.abs(L.snowLevel - c.snow_level) < 1e-15, `${c.name} snow level`);
  for (const key of ['base_height', 'height', 'moisture']) {
    const js = { base_height: L.baseHeight, height: L.height, moisture: L.moisture }[key];
    if (Array.isArray(c[key])) worst = Math.max(worst, close(js, c[key], `${c.name} ${key}`));
    else {
      worst = Math.max(worst, close(c[key].index.map(i => js[i]), c[key].values, `${c.name} ${key} samples`));
      const sum = js.reduce((a, b) => a + b, 0);
      assert.ok(Math.abs(sum - c[key].sum) < 1e-8 * n2, `${c.name} ${key} sum ${sum} vs ${c[key].sum}`);
    }
  }
  for (const [k, s] of Object.entries(c.mask_sums)) {
    const sum = L.masks[k].reduce((a, b) => a + b, 0);
    assert.ok(Math.abs(sum - s) < 1e-8 * n2, `${c.name} mask ${k}: ${sum} vs ${s}`);
  }
  let bad = 0;
  for (let k = 0; k < n2; k++) {
    const hex = '#' + [0, 1, 2].map(j => L.color[4 * k + j].toString(16).padStart(2, '0')).join('').toUpperCase();
    if (c.palette[c.colors.charCodeAt(k) - 65] !== hex) bad++;
  }
  assert.equal(bad, 0, `${c.name}: ${bad} colour pixels differ`);
}
console.log(`terrain_engine: noise, kernels and ${F.cases.length} full landscapes match Python (max abs diff ${worst.toExponential(1)}, colours identical)`);
