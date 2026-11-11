// Web Worker: runs generateLandscape off the main thread and posts progress and the result back
// (typed arrays transferred, not copied).
import { generateLandscape } from './terrain_engine.js';

self.onmessage = e => {
  const { id, params, seed } = e.data;
  try {
    const L = generateLandscape(params, seed, (f, label) => self.postMessage({ id, progress: f, label }));
    const bufs = [L.height.buffer, L.moisture.buffer, L.baseHeight.buffer, L.color.buffer,
      ...Object.values(L.masks).map(m => m.buffer)];
    self.postMessage({ id, result: L }, bufs);
  } catch (err) {
    self.postMessage({ id, error: String(err && err.message || err) });
  }
};
