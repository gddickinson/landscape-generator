// Generate page: the full generator in the browser (JS port of the Python pipeline, in a Web Worker),
// every view of the Python analysis figure plus relief and 3-D, a coverage legend and PNG export.
import { route, api, app, esc, list, onLeave, download } from './core.js';
import { generate, cancel, randomSeed } from './terrain_client.js';
import { paint, VIEWS } from './terrain_render.js';
import { legendHtml } from './legend.js';
import { buildPanel, stateFromQuery, stateToQuery } from './generate_panel.js';

route('generate', async (args, query) => {
  const [info, luts] = await Promise.all([api('/info'), api('/colormaps')]);
  const state = stateFromQuery(info.defaults, info.seasons, query);
  let view = VIEWS.some(v => v[0] === query.view) ? query.view : 'terrain';
  let exag = 0.2, L = null, timer = 0, alive = true;

  app().innerHTML = `
  <h1 class="glow">Generate a landscape</h1>
  <p class="lead">The Python generator, ported to JavaScript and running in your browser: the same seed gives the
  same height map, features and colours as <code>python generate.py</code>. Change any control and the landscape is
  regenerated.</p>
  <div class="gen">
    <aside class="panel" id="ctl" aria-label="Generator settings"></aside>
    <section class="gen-main">
      <div class="row viewrow">
        <div><label for="view">View</label><select id="view">${list(VIEWS, ([k, t]) =>
          `<option value="${k}" ${k === view ? 'selected' : ''}>${esc(t)}</option>`)}</select></div>
        <div id="exag-wrap" class="ctl" hidden><label for="exag">Height exaggeration <b id="exag-v">0.20</b></label>
          <input id="exag" type="range" min="0.05" max="0.8" step="0.05" value="0.2"></div>
      </div>
      <div class="stage land"><canvas id="cv" role="img" aria-label="Generated landscape"></canvas>
        <div id="busy" class="busy" hidden><progress id="prog" max="1" value="0"></progress><span id="busy-t">Generating...</span></div></div>
      <p id="status" class="small mute" aria-live="polite"></p>
      <button id="png" type="button">Save PNG</button><button id="link" type="button" class="alt">Copy link</button>
      <h3>Legend: coverage of this map</h3><div id="legend"></div>
      <p class="small mute">Feature map colours are fixed here; the Python analysis figure picks random ones each run.</p>
    </section>
  </div>`;

  const cv = document.getElementById('cv');
  const draw = () => {
    if (!L) return;
    paint(cv, L, view, luts, { exag });
    cv.setAttribute('aria-label', `${VIEWS.find(v => v[0] === view)[1]} of the landscape, seed ${L.seed}, ${L.params.season}`);
    cv.classList.toggle('pixels', L.size < 256 && view !== '3d' && view !== 'analysis');
  };
  const syncUrl = () => history.replaceState(null, '', '#/generate?' + stateToQuery(state, info.defaults) + (view !== 'terrain' ? '&view=' + view : ''));

  async function run() {
    syncUrl();
    const busy = document.getElementById('busy'), prog = document.getElementById('prog');
    busy.hidden = false; prog.value = 0;
    const t0 = performance.now();
    const { seed, ...params } = state;
    try {
      const res = await generate(params, seed, (f, label) => {
        prog.value = f; document.getElementById('busy-t').textContent = `Generating... ${label}`;
      });
      if (!alive) return;
      L = res;
      draw();
      busy.hidden = true;
      document.getElementById('status').textContent = `Seed ${L.seed} · ${L.size} x ${L.size} · ${L.params.season} · `
        + `generated in ${((performance.now() - t0) / 1000).toFixed(1)} s in your browser`
        + (L.params.season === 'winter' ? ` · winter snow line ${L.snowLevel.toFixed(3)}` : '');
      document.getElementById('legend').innerHTML = legendHtml(L);
    } catch (e) {
      if (e.cancelled) return;
      busy.hidden = true;
      document.getElementById('status').innerHTML = `<span class="err">${esc(e.message)}</span>`;
    }
  }
  const schedule = () => { clearTimeout(timer); timer = setTimeout(run, 250); };

  buildPanel(document.getElementById('ctl'), state, info.seasons, schedule, randomSeed);
  const exagWrap = document.getElementById('exag-wrap');
  exagWrap.hidden = view !== '3d';
  document.getElementById('view').addEventListener('change', e => {
    view = e.target.value; exagWrap.hidden = view !== '3d'; syncUrl(); draw();
  });
  document.getElementById('exag').addEventListener('input', e => {
    exag = +e.target.value; document.getElementById('exag-v').textContent = exag.toFixed(2); draw();
  });
  document.getElementById('png').addEventListener('click', () => {
    if (!L) return;
    cv.toBlob(b => download(`landscape_seed${L.seed}_${L.params.season}_${L.size}_${view}.png`, b), 'image/png');
  });
  document.getElementById('link').addEventListener('click', async e => {
    try { await navigator.clipboard.writeText(location.href); e.target.textContent = 'Copied'; }
    catch { e.target.textContent = 'Copy failed'; }
    setTimeout(() => { e.target.textContent = 'Copy link'; }, 1500);
  });
  onLeave(() => { alive = false; clearTimeout(timer); cancel(); });
  run();
});
