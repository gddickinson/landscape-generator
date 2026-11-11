// Controls of the Generate page: the CLI options of generate.py (seed, size, season, feature density)
// and the other EnhancedTerrainParams fields, with defaults read from the Python package (/api/info).
import { esc, list, slider } from './core.js';

export const SIZES = [64, 128, 256, 512];
export const DEFAULT_SIZE = 256; // the Python default is 512 (about 5 s in the browser): pick it from the list
export const SLIDERS = [
  { id: 'feature_density', label: 'Feature density', min: 0.02, max: 0.3, step: 0.01 },
];
export const ADVANCED = [
  { id: 'octaves', label: 'Octaves', min: 1, max: 8, step: 1 },
  { id: 'persistence', label: 'Persistence', min: 0.2, max: 0.9, step: 0.05 },
  { id: 'lacunarity', label: 'Lacunarity', min: 1.5, max: 3, step: 0.1 },
  { id: 'base_frequency', label: 'Base frequency', min: 1, max: 10, step: 0.5 },
  { id: 'sea_level', label: 'Sea level', min: 0.1, max: 0.6, step: 0.01 },
  { id: 'mountain_level', label: 'Mountain level', min: 0.4, max: 0.95, step: 0.01 },
  { id: 'snow_level', label: 'Snow level', min: 0.5, max: 1, step: 0.01 },
];
const NUM_KEYS = [...SLIDERS, ...ADVANCED].map(s => s.id);

// State from the defaults overridden by the page query (?seed=..&size=..&season=..&octaves=..).
export function stateFromQuery(defaults, seasons, q) {
  const s = { ...defaults, size: DEFAULT_SIZE, seed: 42 };
  if (q.seed !== undefined && /^\d{1,15}$/.test(q.seed)) s.seed = +q.seed;
  if (SIZES.includes(+q.size)) s.size = +q.size;
  if (seasons.some(x => x.key === q.season)) s.season = q.season;
  for (const k of NUM_KEYS) if (q[k] !== undefined && Number.isFinite(+q[k])) s[k] = +q[k];
  return s;
}

export function stateToQuery(s, defaults) {
  const q = new URLSearchParams({ seed: s.seed, size: s.size, season: s.season });
  for (const k of NUM_KEYS) if (s[k] !== defaults[k]) q.set(k, s[k]);
  return q.toString();
}

const decimals = step => (String(step).split('.')[1] || '').length;

// Build the panel into host; onChange(state) fires on every change.
export function buildPanel(host, state, seasons, onChange, onRandom) {
  host.innerHTML = `
    <div class="row seedrow"><div><label for="seed">Seed</label>
      <input id="seed" type="number" min="0" step="1" value="${state.seed}"></div>
      <button id="rand" class="alt" type="button" title="Random seed">Random</button></div>
    <label for="size">Size (grid cells per side)</label>
    <select id="size">${list(SIZES, n => `<option value="${n}" ${n === state.size ? 'selected' : ''}>${n} x ${n}${n === 512 ? ' (Python default, slower)' : ''}</option>`)}</select>
    <label id="season-l">Season</label>
    <div class="seg" role="group" aria-labelledby="season-l">${list(seasons, s =>
      `<button type="button" data-season="${esc(s.key)}" class="${s.key === state.season ? 'on' : ''}" aria-pressed="${s.key === state.season}">${esc(s.name)}</button>`)}</div>
    <div id="sl-main"></div>
    <details class="grp"><summary>Noise and levels</summary><div id="sl-adv"></div></details>`;
  const fire = () => onChange(state);
  const seed = host.querySelector('#seed');
  seed.addEventListener('change', () => {
    const v = Math.trunc(+seed.value);
    if (Number.isSafeInteger(v) && v >= 0) { state.seed = v; fire(); } else seed.value = state.seed;
  });
  host.querySelector('#rand').addEventListener('click', () => { state.seed = onRandom(); seed.value = state.seed; fire(); });
  host.querySelector('#size').addEventListener('change', e => { state.size = +e.target.value; fire(); });
  host.querySelectorAll('[data-season]').forEach(b => b.addEventListener('click', () => {
    state.season = b.dataset.season;
    host.querySelectorAll('[data-season]').forEach(x => { x.classList.toggle('on', x === b); x.setAttribute('aria-pressed', x === b); });
    fire();
  }));
  const add = (where, spec) => slider(host.querySelector(where),
    { ...spec, value: state[spec.id], fmt: v => (+v).toFixed(decimals(spec.step)) }, v => { state[spec.id] = v; fire(); });
  SLIDERS.forEach(s => add('#sl-main', s));
  ADVANCED.forEach(s => add('#sl-adv', s));
}
