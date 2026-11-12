// Seasons page: one seed generated in all four seasons side by side (the season changes the palette,
// the moisture and height scaling and, in winter, the snow line).
import { route, api, app, esc, list, onLeave } from './core.js';
import { generate, cancel, randomSeed } from './terrain_client.js';
import { paint } from './terrain_render.js';

const EFFECTS = {
  spring: 'moisture x 1.2, height x 0.95', summer: 'moisture x 0.9, height x 1.05',
  fall: 'moisture x 0.85', winter: 'moisture x 0.7, snow line x 0.8',
};

route('seasons', async (args, query) => {
  const info = await api('/info');
  let seed = /^\d{1,15}$/.test(query.seed || '') ? +query.seed : 42, alive = true, view = 'relief';
  app().innerHTML = `
  <h1 class="glow">Four seasons</h1>
  <p class="lead">The same seed in each season. Height and feature placement come from the same random draws, so
  the differences are the season's effects: palette, moisture and height scaling, and the winter snow line.</p>
  <div class="row narrow"><div><label for="s-seed">Seed</label><input id="s-seed" type="number" min="0" value="${seed}"></div>
    <div><label for="s-view">View</label><select id="s-view"><option value="relief">Shaded relief</option>
      <option value="terrain">Coloured terrain</option><option value="moisture">Moisture map</option></select></div>
    <button id="s-rand" class="alt" type="button">Random seed</button></div>
  <div class="seasons">${list(info.seasons, s => `<figure class="panel season">
    <canvas id="c-${esc(s.key)}" role="img" aria-label="${esc(s.name)} landscape"></canvas>
    <figcaption><b>${esc(s.name)}</b> <span class="mute small">${esc(EFFECTS[s.key] || '')}</span>
    <span class="swatches">${list(Object.entries(s.colors), ([k, hx]) => `<span class="sw" title="${esc(k)} ${esc(hx)}" style="background:${esc(hx)}"></span>`)}</span>
    <a class="small" href="#/generate?seed=${seed}&size=128&season=${esc(s.key)}" data-open>Open in the generator</a></figcaption></figure>`)}</div>
  <p class="small mute">128 x 128 cells each, generated in your browser. Swatches: the season's grassland, forest,
  fields and trees colours from <code>terrain/biomes.py</code> (grassland and moist forest biomes, and the agricultural-field and forest features).</p>`;
  const results = {};
  const luts = await api('/colormaps');
  const drawAll = () => info.seasons.forEach(s => results[s.key] && paint(document.getElementById('c-' + s.key), results[s.key], view, luts));
  async function run() {
    for (const s of info.seasons) {
      try { results[s.key] = await generate({ size: 128, season: s.key }, seed); } catch (e) { if (e.cancelled) return; throw e; }
      if (!alive) return;
      paint(document.getElementById('c-' + s.key), results[s.key], view, luts);
    }
    document.querySelectorAll('[data-open]').forEach(a => { a.href = a.href.replace(/seed=\d+/, 'seed=' + seed); });
    history.replaceState(null, '', '#/seasons?seed=' + seed);
  }
  const inp = document.getElementById('s-seed');
  inp.addEventListener('change', () => { const v = Math.trunc(+inp.value); if (v >= 0 && Number.isSafeInteger(v)) { seed = v; run(); } });
  document.getElementById('s-rand').addEventListener('click', () => { seed = randomSeed(); inp.value = seed; run(); });
  document.getElementById('s-view').addEventListener('change', e => { view = e.target.value; drawAll(); });
  onLeave(() => { alive = false; cancel(); });
  run();
});
