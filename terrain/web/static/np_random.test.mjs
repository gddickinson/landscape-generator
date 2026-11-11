// node np_random.test.mjs: the JS numpy.random port against values drawn by NumPy
// (tests/fixtures/terrain_reference.json, written by scripts/make_terrain_fixture.py).
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { seedSequenceState, PCG64, Generator } from './np_random.js';

const F = JSON.parse(readFileSync(new URL('../../../tests/fixtures/terrain_reference.json', import.meta.url)));

for (const r of F.rng) {
  assert.deepEqual(Array.from(seedSequenceState(r.seed, 8)), r.seedseq, `SeedSequence(${r.seed})`);
  const bg = new PCG64(r.seed);
  assert.deepEqual(r.raw.map(() => bg.rawString()), r.raw, `PCG64(${r.seed}) raw`);
  const g = new Generator(r.seed);
  assert.deepEqual(r.random.map(() => g.random()), r.random, `random() seed ${r.seed}`);
  assert.deepEqual(r.normal.map(() => g.normal(0, 0.1)), r.normal, `normal() seed ${r.seed}`);
  let sum = 0, last = 0, absmax = 0;
  for (let i = 0; i < 200000; i++) { last = g.standardNormal(); sum += last; absmax = Math.max(absmax, Math.abs(last)); }
  // Bit-identical draws (including the ziggurat tail and wedge rejections) give the same last value.
  assert.equal(last, r.big_last, `200000th normal, seed ${r.seed}`);
  assert.equal(absmax, r.big_absmax, `max |normal|, seed ${r.seed}`);
  assert.ok(Math.abs(sum - r.big_sum) < 1e-9 * 200000, `sum of normals, seed ${r.seed}`);
}
console.log(`np_random: ${F.rng.length} seeds, SeedSequence, PCG64 raw, random, normal and 200000 normals each match NumPy ${F.numpy}`);
