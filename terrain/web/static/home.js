// Home page: hero with a landscape generated live in the browser, counts from the Python package and entry cards.
import { route, api, app, list, esc, onLeave } from './core.js';
import { generate, cancel } from './terrain_client.js';
import { paint } from './terrain_render.js';

const DOORS = [
  ['#/generate', 'Generate', 'The full generator: seed, size, season, feature density, noise octaves and levels; seven views including relief and 3-D; PNG export.', 'a'],
  ['#/seasons', 'Four seasons', 'One seed in spring, summer, fall and winter side by side.', 'b'],
  ['#/verify', 'Python vs JavaScript', 'Seeded landscapes from the Python package next to the browser port, with the differences measured.', 'c'],
  ['#/about', 'About', 'How the noise, features, seasons and biomes work, and how to run the command line and web apps.', 'a'],
];

route('home', async () => {
  const info = await api('/info');
  const c = info.counts;
  app().innerHTML = `
  <section class="hero home-hero">
    <div>
      <p class="kicker">Fractal noise · Voronoi features · Seasons</p>
      <h1 class="glow">Landscape Generator</h1>
      <p class="lead">${esc(info.summary)}</p>
      <p>This site runs the generator itself: a JavaScript port of the Python package that gives the same landscape
      for the same seed.</p>
      <a class="btn" href="#/generate">Generate a landscape</a><a class="btn alt" href="#/about">How it works</a>
    </div>
    <figure class="hero-map"><canvas id="hero" role="img" aria-label="Landscape generated in the browser, seed 42, summer"></canvas>
      <figcaption class="small mute">Seed 42, summer, 160 x 160: generated in your browser just now.</figcaption></figure>
  </section>
  <div class="tiles">
    <div class="tile"><b>${c.features}</b><span>geographic features</span></div>
    <div class="tile"><b>${c.seasons}</b><span>seasons</span></div>
    <div class="tile"><b>${c.params}</b><span>terrain parameters</span></div>
    <div class="tile"><b>7</b><span>map views</span></div>
  </div>
  <div class="grid wide">${list(DOORS, ([href, t, d, cl]) => `<a class="card door ${cl}" href="${href}"><b>${t}</b><span>${d}</span></a>`)}</div>
  <h2>Features</h2>
  <div class="grid">${list(info.features, f => `<div class="card"><b>${esc(f.name)}</b>
    <span>${list(Object.values(f.color_map), hx => `<span class="sw" style="background:${esc(hx)}"></span>`)}
    height ${f.height_modifier >= 0 ? '+' : ''}${f.height_modifier}, moisture ${f.moisture_modifier >= 0 ? '+' : ''}${f.moisture_modifier}</span></div>`)}</div>`;
  let alive = true;
  onLeave(() => { alive = false; cancel(); });
  const [L, luts] = await Promise.all([generate({ size: 160 }, 42), api('/colormaps')]).catch(e => { if (e.cancelled) return []; throw e; });
  if (alive && L) paint(document.getElementById('hero'), L, 'relief', luts);
});
