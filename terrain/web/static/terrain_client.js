// Runs the JS generator in a Web Worker (one job at a time; a new request cancels the running one).
// Falls back to the main thread where module workers are unavailable.
let worker = null, seq = 0, current = null;

function makeWorker() {
  try { return new Worker(new URL('./terrain_worker.js', import.meta.url), { type: 'module' }); }
  catch (e) { console.warn('module worker unavailable, generating on the main thread', e); return null; }
}

export function generate(params, seed, onProgress = () => {}) {
  if (current) { current.reject(Object.assign(new Error('cancelled'), { cancelled: true })); worker?.terminate(); worker = null; current = null; }
  const id = ++seq;
  return new Promise((resolve, reject) => {
    if (!worker) worker = makeWorker();
    if (!worker) {
      import('./terrain_engine.js').then(m => setTimeout(() => {
        try { resolve(m.generateLandscape(params, seed, onProgress)); } catch (e) { reject(e); }
      }, 0), reject);
      return;
    }
    current = { id, reject };
    worker.onmessage = e => {
      const d = e.data;
      if (d.id !== id) return;
      if (d.progress !== undefined) { onProgress(d.progress, d.label); return; }
      current = null;
      if (d.error) reject(new Error(d.error)); else resolve(d.result);
    };
    worker.onerror = e => { current = null; worker = null; reject(new Error(e.message || 'worker error')); };
    worker.postMessage({ id, params, seed });
  });
}

// Stop any running job (e.g. when the page is left).
export function cancel() {
  if (current) { current.reject(Object.assign(new Error('cancelled'), { cancelled: true })); current = null; }
  if (worker) { worker.terminate(); worker = null; }
}

export const randomSeed = () => Math.floor(Math.random() * 1e6);
