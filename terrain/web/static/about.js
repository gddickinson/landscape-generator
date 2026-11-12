// About page: how the generator works (from the README and the code), how to run the CLI and the web app, credits.
import { route, api, app, esc, list } from './core.js';

route('about', async () => {
  const info = await api('/info');
  const d = info.defaults;
  app().innerHTML = `
  <h1 class="glow">About</h1>
  <p class="lead">${esc(info.summary)}</p>
  <p>The Python package (<code>terrain/</code>, NumPy and SciPy) renders matplotlib figures from the command line.
  This web version runs a JavaScript port of the same pipeline in the browser, so the GitHub Pages site is a
  working generator, not a gallery.</p>

  <h2>How a landscape is made</h2>
  <ol>
    <li><b>Noise</b> (<code>generator.py</code>): each noise layer sums six sine-wave patterns, each rotated by a random
      angle and phase-shifted, at frequency multipliers 1, 2, 4 ... 32, plus Gaussian jitter (σ = 0.1, halved per
      pattern), then rescaled to 0-1.</li>
    <li><b>Fractal terrain</b>: ${d.octaves} octaves of that noise starting at frequency ${d.base_frequency}; each octave
      multiplies frequency by the lacunarity (${d.lacunarity}) and amplitude by the persistence (${d.persistence}).
      The sum is rescaled and smoothed with a Gaussian filter (σ = 1). A second fractal map gives the moisture.</li>
    <li><b>Season</b> (<code>features.py</code>): spring raises moisture (x 1.2) and lowers heights (x 0.95), summer
      dries (x 0.9) and raises (x 1.05), fall dries (x 0.85), winter dries (x 0.7) and lowers the snow line to 80%.</li>
    <li><b>Features</b>: for each of the ${info.features.length} features, random points are split into Voronoi cells;
      each bounded cell is kept with probability 0.3, masked by a noise layer (&gt; 0.3) and blurred (σ = 2). Roads join
      random settlement points (each pair with probability 0.4) through five jittered waypoints. Each mask raises or
      lowers height and moisture by the feature's modifiers:
      ${list(info.features, f => `${esc(f.name)} (${f.height_modifier}, ${f.moisture_modifier})`, ', ')}.</li>
    <li><b>Biomes</b> (<code>biomes.py</code>): after rescaling heights to 0-1, cells below the sea level
      (${d.sea_level}) are deep or shallow water, then beach (up to sea level + 0.05), grassland or forest (moisture
      &gt; 0.6) up to the mountain level (${d.mountain_level}), rock up to the snow level (${d.snow_level}), then
      snow. Grassland and forest take the season's colours; feature colours are painted where a mask exceeds 0.5
      (fields and forest features in the season's fields and trees colours, mountain-range snow only above the snow line).</li>
  </ol>

  <h2>Same seed, same landscape</h2>
  <p>Every random draw comes from one <code>numpy.random.default_rng(seed)</code>. The JavaScript port reimplements
  NumPy's SeedSequence, the PCG64 generator and its ziggurat normal sampler bit for bit, then repeats every step in
  the same order, so a seed reproduces the Python maps (to rounding in the last digits) and identical colours.
  See <a href="#/verify">Verify</a>; node tests check it against values written by the Python package.
  At 512 x 512 (the Python default) a landscape takes about 5 s in the browser, 256 x 256 about 1 s; generation runs
  in a Web Worker so the page stays responsive.</p>

  <h2>Run the command line</h2>
  <pre>pip install -r requirements.txt
python generate.py                              # seed 42, 512 x 512, summer
python generate.py --seed 7 --season winter     # spring, summer, fall, winter
python generate.py --size 256 --density 0.15 --output ./out</pre>
  <p>It writes <code>enhanced_landscape_3d.png</code> (3-D surface) and <code>enhanced_landscape_analysis.png</code>
  (height, moisture, features, coloured terrain).</p>

  <h2>Run the web app</h2>
  <pre>pip install -r requirements-web.txt
python run_web.py                                   # http://127.0.0.1:8162</pre>
  <p>The local server serves this front end and a small JSON API read from the Python package: defaults, seasons
  and features (<code>/api/info</code>), the matplotlib colormaps (<code>/api/colormaps</code>), Python reference
  landscapes (<code>/api/reference</code>) and, locally only, a Python run for any parameters
  (<code>POST /api/generate</code>). The GitHub Pages site is the same front end with the GET answers exported to JSON
  by <code>scripts/build_static.py</code>.</p>

  <h2>Credits</h2>
  <p>By George Dickinson, MIT licence. Built with NumPy, SciPy and matplotlib, and with AI assistance from
  <a href="https://claude.com/" rel="noopener">Claude (Anthropic)</a>. The ziggurat tables in the JS port are
  NumPy's (BSD licence). Source: <a href="https://github.com/gddickinson/landscape-generator">github.com/gddickinson/landscape-generator</a>.</p>`;
});
